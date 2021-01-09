import copy
import hashlib
import re
from datetime import datetime
from uuid import uuid1

import icalendar

import api
from func import dictHash, fixDay, login, getIcal
from static import *

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
}

if __name__ == '__main__':
    mainSession, userID, semesterName, semesterStartTime, semesterEndTime = login()

    req = mainSession.post(url=api.course, json={
        "oddOrDouble": 0,
        "semester": semesterName,
        "startWeek": "1",
        "stopWeek": "22",
        "studentId": userID,
        "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    }).json()

    tmpData = req['data']
    reObject = re.compile(r'(\d*)-(\d*)( [单双])?')
    allCourseData = []

    for timeSection in tmpData:
        for timeSectionCourse in timeSection['courseList']:
            allCourseData.append(timeSectionCourse)

    # print(json.dumps(allCourseData,ensure_ascii=False))
    # exit(0)

    purgeAllCourseData = {}

    for day in range(1, 8):
        for time in range(1, 12):
            timeSign = (day, time)
            purgeAllCourseData[timeSign] = {}

    for courseData in allCourseData:
        # print(courseData)
        day = fixDay(int(courseData['dayOfWeek']))
        time = int(courseData['time'])
        timeSign = (day, time)
        purgeCourseDict = {
            'courseName': courseData['courseName'],
            'weeks': courseData['weeks'],
            'teacher': courseData['teacherName'],
            'studentNum': courseData['numberOfStudent'],
            'classroomName': courseData.get('classroomName', ''),
            'className': courseData.get('teachingClassName', '')
        }
        purgeAllCourseData.setdefault(timeSign, [])
        purgeAllCourseData[timeSign][dictHash(purgeCourseDict)] = purgeCourseDict

    parsedCourseData = []
    # print(purgeAllCourseData)

    for timeSign in purgeAllCourseData.keys():
        day = timeSign[0]
        time = timeSign[1]
        while True:
            if purgeAllCourseData[timeSign]:
                # print(f"time is {day} {time}")
                currentOptCourse = purgeAllCourseData[timeSign].popitem()

                # print(currentOptCourse)
                courseHash = currentOptCourse[0]
                courseData = currentOptCourse[1]

                courseName = courseData['courseName']

                # if courseName == "数字逻辑":
                #     print("数字逻辑" + str(day) + " " + str(time))

                teacher = courseData['teacher']
                studentNum = courseData['studentNum']
                className = courseData['className']
                classroomName = courseData['classroomName']

                rawWeeks = courseData['weeks']
                # print(rawWeeks)
                parsedWeeks = re.match(reObject, rawWeeks).groups()
                # interval = 2 if parsedWeeks[2] else 1
                # try:
                #     if parsedWeeks[2]:
                #         interval = 2
                # except IndexError:
                #     interval = 1
                interval = 2 if parsedWeeks[2] else 1
                startWeek = parsedWeeks[0]
                endWeek = parsedWeeks[1]

                startTime = copy.copy(time)
                endTimePointer = copy.copy(time)

                print(courseName + ":" + str(parsedWeeks) + ":" + rawWeeks)
                while True:
                    if endTimePointer != 4 and endTimePointer != 11:
                        if courseHash in purgeAllCourseData[(day, endTimePointer + 1)].keys():
                            purgeAllCourseData[(day, endTimePointer + 1)].pop(courseHash)
                            endTimePointer += 1
                        else:
                            break
                    else:
                        break
                endTime = endTimePointer

                parsedOneCourse = {
                    'day': day,
                    'courseName': courseName,
                    'className': className,
                    'classroomName': classroomName,
                    'startTimeID': startTime,
                    'endTimeID': endTime,
                    'teacherName': teacher,
                    'startTime': courseTimeDict[startTime],
                    'endTime': courseTimeDict[endTime] + COURSE_TIME,
                    'startWeek': startWeek,
                    'endWeek': endWeek,
                    'interval': interval,
                    'studentNumber': studentNum
                }

                parsedCourseData.append(copy.deepcopy(parsedOneCourse))
                parsedOneCourse.clear()
            else:
                break

    # print(json.dumps(parsedCourseData,ensure_ascii=False))
    # exit(0)

    #
    # for course in courseData.keys():
    #     for oneTime in courseData[course]['timeSign']:
    #         day = int(int(oneTime[0]) % 10000 / 100)
    #         startTimeID = int(oneTime[0] % 100)
    #         endTimeID = int(oneTime[-1] % 100)
    #         startTime = courseTimeDict[startTimeID]
    #         endTime = courseTimeDict[endTimeID] + COURSE_TIME
    #         parsedOneCourse = courseData[course]['data']
    #         parsedOneCourse['startTimeID'] = startTimeID
    #         parsedOneCourse['endTimeID'] = endTimeID
    #         parsedOneCourse['startTime'] = startTime
    #         parsedOneCourse['endTime'] = endTime
    #         parsedOneCourse['day'] = day
    #         parsedCourseData.append(copy.deepcopy(parsedOneCourse))

    # print(json.dumps(parsedCourseData, ensure_ascii=False, cls=DateEncoder))

    calt = getIcal('课表')

    for oneEvent in parsedCourseData:
        count = int((int(oneEvent['endWeek']) - int(oneEvent['startWeek'])) / int(oneEvent['interval']) + 1)
        # print(count)
        # print((int(oneEvent['startWeek']) - 1))
        # print((int(oneEvent['day']) - 2))
        dtstart_datetime = semesterStartTime + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 2) * ONE_DAY + oneEvent['startTime']
        dtend_datetime = semesterStartTime + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 2) * ONE_DAY + oneEvent['endTime']
        # print(dtstart_datetime)
        # print(dtend_datetime)
        # dtstart_datetime.tzinfo = TIMEZONE
        # dtend_datetime.tzinfo = TIMEZONE

        event = icalendar.Event()
        event.add('summary', oneEvent['courseName'])  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        event.add('location', oneEvent['classroomName'])  # 地点
        event.add('description',
                  '第 {} - {} 节\r\n教师： {}\r\n教室： {}\r\n时间： {} - {} \r\n周期： {} - {}\r\n班级： {}\r\n学生数： {}'.format(
                      oneEvent['startTimeID'],
                      oneEvent['endTimeID'],
                      oneEvent['teacherName'],
                      oneEvent['classroomName'],
                      str(oneEvent['startTime']),
                      str(oneEvent['endTime']),
                      oneEvent['startWeek'],
                      oneEvent['endWeek'],
                      oneEvent['className'],
                      oneEvent['studentNumber']
                  )
                  )
        event.add('dtstart', dtstart_datetime)
        event.add('dtend', dtend_datetime)
        event.add('rrule', {'freq': 'weekly', 'interval': oneEvent['interval'], 'count': count})
        calt.add_component(event)

    with open('output.ics', 'wb') as f:
        f.write(calt.to_ical())
