import base64
import copy
import hashlib
import json
import re
from datetime import datetime, timedelta
from uuid import uuid1

import icalendar
import pytz
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import api
import info
from func import dictHash, fixDay

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
}

COURSE_TIME = timedelta(minutes=45)
WEEK_TIME = timedelta(days=7)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(weeks=1)

TIMEZONE = pytz.timezone("Asia/Shanghai")

courseTimeDict = {
    1: timedelta(hours=8, minutes=20),
    2: timedelta(hours=9, minutes=10),
    3: timedelta(hours=10, minutes=15),
    4: timedelta(hours=11, minutes=5),
    5: timedelta(hours=14, minutes=00),
    6: timedelta(hours=14, minutes=50),
    7: timedelta(hours=15, minutes=55),
    8: timedelta(hours=16, minutes=45),
    9: timedelta(hours=18, minutes=30),
    10: timedelta(hours=19, minutes=20),
    11: timedelta(hours=20, minutes=10)
}

if __name__ == '__main__':
    mainSession = requests.session()
    mainSession.params = {"_t": int(datetime.now().timestamp())}
    mainSession.headers = header
    mainSession.verify = False

    loginDict = {
        "userName": info.studentID,
        "token": base64.b64encode(info.password.encode('UTF-8')).decode(),
        "target": "",
        "pattern": "manager-login",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "username": info.studentID,
        'password': hashlib.md5(("admin" + info.password).encode("UTF-8")).hexdigest(),
    }

    req = mainSession.post(url=api.login, params=loginDict, data={})

    # print(req.json())

    userData = json.loads(req.cookies.get_dict()['user'])

    userID = userData['userName']
    semesterName = userData['semester']

    req = mainSession.get(url=api.semester).json()

    semesterStartTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 2
    semesterEndTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 2

    req = mainSession.post(url=api.course, json={
        "oddOrDouble": 0,
        "semester": semesterName,
        "startWeek": "1",
        "stopWeek": "22",
        "studentId": userID,
        "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    }).json()

    tmpData = req['data']
    reObject = re.compile(r'(\d*)-(\d*)( 单双)?')
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
    print(purgeAllCourseData)

    for timeSign in purgeAllCourseData.keys():
        day = timeSign[0]
        time = timeSign[1]
        if purgeAllCourseData[timeSign]:
            currentOptCourse = purgeAllCourseData[timeSign].popitem()

            # print(currentOptCourse)
            courseHash = currentOptCourse[0]
            courseData = currentOptCourse[1]

            courseName = courseData['courseName']
            teacher = courseData['teacher']
            studentNum = courseData['studentNum']
            className = courseData['className']
            classroomName = courseData['classroomName']

            rawWeeks = courseData['weeks']
            print(rawWeeks)
            parsedWeeks = re.match(reObject, rawWeeks).groups()
            interval = 2 if parsedWeeks[2] else 1
            startWeek = parsedWeeks[0]
            endWeek = parsedWeeks[1]

            startTime = copy.copy(time)
            endTimePointer = copy.copy(time)
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
                # 'startTime': courseTimeDict[startTime],
                # 'endTime': courseTimeDict[endTime] + COURSE_TIME,
                'startWeek': startWeek,
                'endWeek': endWeek,
                'interval': interval,
                'studentNumber': studentNum
            }

            parsedCourseData.append(copy.deepcopy(parsedOneCourse))
            parsedOneCourse.clear()

    print(json.dumps(parsedCourseData,ensure_ascii=False))
    exit(0)

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

    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'
    calt['X-WR-TIMEZONE'] = 'Asia/Shanghai'
    calt['X-WR-CALNAME'] = '课表'
    tz = icalendar.Timezone()
    tz['tzid'] = 'Asia/Shanghai'
    tzStandard = icalendar.TimezoneStandard()
    tzStandard.add('X-LIC-LOCATION', 'Asia/Shanghai')
    tzStandard.add('TZOFFSETFROM', timedelta(hours=8))
    tzStandard.add('TZOFFSETTO', timedelta(hours=8))
    tzStandard.add('TZNAME', 'CST')
    tz.add_component(tzStandard)
    calt.add_component(tz)

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
