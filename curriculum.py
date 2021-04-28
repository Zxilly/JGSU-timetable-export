import copy
import hashlib
import re
import sys
from datetime import datetime
from uuid import uuid1

import icalendar

import api
from func import dictHash, fixDay, login, getIcal
from static import *
from fix import fix_dict

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

    purgeAllCourseData = {}

    for day in range(1, 8):
        for time in range(1, 12):
            timeSign = (day, time)
            purgeAllCourseData[timeSign] = {}

    for courseData in allCourseData:
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
        purgeAllCourseData.setdefault(timeSign, {})
        purgeAllCourseData[timeSign][dictHash(purgeCourseDict)] = purgeCourseDict

    parsedCourseData = []

    for timeSign in purgeAllCourseData.keys():
        day = timeSign[0]
        time = timeSign[1]
        while True:
            if purgeAllCourseData[timeSign]:
                currentOptCourse = purgeAllCourseData[timeSign].popitem()

                courseHash = currentOptCourse[0]
                courseData = currentOptCourse[1]

                courseName = courseData['courseName']

                teacher = courseData['teacher']
                studentNum = courseData['studentNum']
                className = courseData['className']
                classroomName = courseData['classroomName']

                rawWeeks = courseData['weeks']
                try:
                    parsedWeeks = re.match(reObject, rawWeeks).groups()
                    interval = 2 if parsedWeeks[2] else 1
                    startWeek = parsedWeeks[0]
                    endWeek = parsedWeeks[1]
                except AttributeError:
                    parsedWeeks = int(rawWeeks)
                    interval = 1
                    startWeek = parsedWeeks
                    endWeek = parsedWeeks

                startTimePointer = copy.copy(time)
                endTimePointer = copy.copy(time)

                # print(courseName, str(parsedWeeks), rawWeeks)
                while True:
                    if endTimePointer != 4 and endTimePointer != 11:
                        if courseHash in purgeAllCourseData[(day, endTimePointer + 1)].keys():
                            purgeAllCourseData[(day, endTimePointer + 1)].pop(courseHash)
                            endTimePointer += 1
                        else:
                            break
                    else:
                        break

                parsedOneCourse = {
                    'day': day,
                    'courseName': courseName,
                    'className': className,
                    'classroomName': classroomName,
                    'startTimeID': startTimePointer,
                    'endTimeID': endTimePointer,
                    'teacherName': teacher,
                    'startWeek': startWeek,
                    'endWeek': endWeek,
                    'interval': interval,
                    'studentNumber': studentNum
                }

                oneCourseHash = dictHash(parsedOneCourse)
                print(oneCourseHash, parsedOneCourse)
                if oneCourseHash in fix_dict.keys():
                    fix_object = fix_dict[oneCourseHash]
                    for key, value in fix_object.items():
                        parsedOneCourse[key] = value
                    print("fixed:", parsedOneCourse, file=sys.stderr)

                parsedOneCourse['startTime'] = courseTimeDict[parsedOneCourse['startTimeID']]
                parsedOneCourse['endTime'] = courseTimeDict[parsedOneCourse['endTimeID']]

                parsedCourseData.append(copy.deepcopy(parsedOneCourse))
                parsedOneCourse.clear()
            else:
                break

    calt = getIcal(f'{semesterName} 课表')

    for oneEvent in parsedCourseData:
        count = int((int(oneEvent['endWeek']) - int(oneEvent['startWeek'])) / int(oneEvent['interval']) + 1)
        dtstart_datetime = semesterStartTime + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 2) * ONE_DAY + oneEvent['startTime']
        dtend_datetime = semesterStartTime + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 2) * ONE_DAY + oneEvent['endTime']

        event = icalendar.Event()
        event.add('summary', oneEvent['courseName'])  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        if oneEvent['classroomName']:
            event.add('location', oneEvent['classroomName'])  # 地点
        event.add('description',
                  '{}教师： {}\r\n'
                  '{}时间： {} - {} \r\n'
                  '周期： {}\r\n'
                  '班级： {}\r\n'
                  '学生数： {}'.format(
                      f"第 {oneEvent['startTimeID']} - {oneEvent['endTimeID']} 节\r\n"
                      if oneEvent['startTimeID'] != oneEvent['endTimeID']
                      else f"第 {oneEvent['startTimeID']} 节\r\n",
                      oneEvent['teacherName'],
                      f'教室： {oneEvent["classroomName"]}\r\n'
                      if oneEvent["classroomName"] else '',
                      str(oneEvent['startTime']),
                      str(oneEvent['endTime']),
                      f'{oneEvent["startWeek"]} - {oneEvent["endWeek"]}'
                      if oneEvent["startWeek"] != oneEvent["endWeek"]
                      else f'{oneEvent["startWeek"]}',
                      oneEvent['className'],
                      oneEvent['studentNumber']
                  )
                  )
        event.add('dtstart', dtstart_datetime)
        event.add('dtend', dtend_datetime)
        if count != 1:
            event.add('rrule', {'freq': 'weekly', 'interval': oneEvent['interval'], 'count': count})
        calt.add_component(event)

    with open('curriculum.ics', 'wb') as f:
        f.write(calt.to_ical())
