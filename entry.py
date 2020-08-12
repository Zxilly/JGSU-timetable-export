import base64
import hashlib
import json
import re
import copy
import icalendar
import pytz

from uuid import uuid1
from datetime import datetime, timedelta

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import api
import info

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
}

COURSE_TIME = timedelta(minutes=45)
WEEK_TIME = timedelta(days=7)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(weeks=1)

TIMEZONE = pytz.timezone("Asia/Shanghai")

courseTimeDict = {
    1: timedelta(hours=8, minutes=0),
    2: timedelta(hours=8, minutes=55),
    3: timedelta(hours=10, minutes=0),
    4: timedelta(hours=10, minutes=55),
    5: timedelta(hours=14, minutes=30),
    6: timedelta(hours=15, minutes=25),
    7: timedelta(hours=16, minutes=20),
    8: timedelta(hours=18, minutes=30),
    9: timedelta(hours=19, minutes=25),
    10: timedelta(hours=20, minutes=20),
    11: timedelta(hours=21, minutes=15)
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

    print(req.json())

    userData = json.loads(req.cookies.get_dict()['user'])

    userID = userData['userName']
    semesterName = userData['semester']

    req = mainSession.get(url=api.semester).json()

    semesterStartTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE)
    semesterEndTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE)

    req = mainSession.post(url=api.course, json={
        "oddOrDouble": 0,
        "semester": semesterName,
        "startWeek": "1",
        "stopWeek": "22",
        "studentId": userID,
        "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    }).json()

    tmpData = req['data']

    courseData = {}
    parsedCourseData = []

    for courseOnedayList in tmpData:
        time = courseOnedayList['time']['timeCode']
        week = courseOnedayList['week']['weekCode']
        timeSign = int(week) * 100 + int(time)
        for course in courseOnedayList['courseList']:
            if course['courseCode'] not in courseData.keys():
                reObject = re.compile(r'(\d*)-(\d*)( 单双)?')
                parsedWeek = re.match(reObject, course['weeks']).groups()
                interval = 2 if parsedWeek[2] else 1
                startWeek = parsedWeek[0]
                endWeek = parsedWeek[1]
                try:
                    classroomName = course['classroomName']
                except:
                    classroomName = ''
                courseData[course['courseCode']] = {
                    'data': {
                        'courseName': course['courseName'],
                        'teacherName': course['teacherName'],
                        'classroomName': classroomName,
                        'studentNumber': course['numberOfStudent'],
                        'interval': interval,
                        'startWeek': startWeek,
                        'endWeek': endWeek,
                    },
                    'timeSign': [timeSign],
                }
            else:
                courseData[course['courseCode']]['timeSign'].append(timeSign)

    # print(json.dumps(courseData,ensure_ascii=False))
    for course in courseData.keys():
        data = courseData[course]
        data['timeSign'].sort()
        timeSignList = data['timeSign']
        timeSignDivision = []
        tmpList = []
        for i in range(0, len(timeSignList)):
            if i == len(timeSignList) - 1:
                if (timeSignList[i] - timeSignList[i - 1] == 1):
                    tmpList.append(timeSignList[i])
                    timeSignDivision.append(tmpList)
                    tmpList = []
                else:
                    timeSignDivision.append([timeSignList[i]])
            elif timeSignList[i + 1] - timeSignList[i] == 1 and timeSignList[i] % 100 != 4:
                tmpList.append(timeSignList[i])
            else:
                tmpList.append(timeSignList[i])
                timeSignDivision.append(tmpList)
                tmpList = []
        courseData[course]['timeSign'] = timeSignDivision

    for course in courseData.keys():
        for oneTime in courseData[course]['timeSign']:
            day = int(int(oneTime[0]) / 100)
            startTimeID = int(oneTime[0] % 100)
            #print(startTimeID)
            endTimeID = int(oneTime[-1] % 100)
            #print(endTimeID)
            startTime = courseTimeDict[startTimeID]
            #print(startTime)
            endTime = courseTimeDict[endTimeID] + COURSE_TIME
            #print(endTime)
            parsedOneCourse = courseData[course]['data']
            parsedOneCourse['startTimeID'] = startTimeID
            parsedOneCourse['endTimeID'] = endTimeID
            parsedOneCourse['startTime'] = startTime
            parsedOneCourse['endTime'] = endTime
            parsedOneCourse['day'] = day
            parsedCourseData.append(copy.deepcopy(parsedOneCourse))

    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'
    tz = icalendar.Timezone()
    tz['tzid'] = 'Asia/Shanghai'
    calt.add_component(tz)

    for oneEvent in parsedCourseData:
        count = (int(oneEvent['endWeek'])-int(oneEvent['startWeek']))/int(oneEvent['interval'])+1
        dtstart_datetime = semesterStartTime+ (int(oneEvent['startWeek'])-1)*ONE_WEEK+(int(oneEvent['day'])-2)*ONE_DAY+oneEvent['startTime']
        dtend_datetime = semesterStartTime+ (int(oneEvent['startWeek'])-1)*ONE_WEEK+(int(oneEvent['day'])-2)*ONE_DAY+oneEvent['endTime']
        #dtstart_datetime.tzinfo = TIMEZONE
        #dtend_datetime.tzinfo = TIMEZONE

        event = icalendar.Event()
        event.add('summary', oneEvent['courseName'])  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        event.add('location', oneEvent['classroomName'])  # 地点
        event.add('description',
                  '第 {} - {} 节\r\n教师： {}\r\n教室: {}\r\n时间: {} - {} \r\n周期: {} - {}\r\n学生数: {}'.format(oneEvent['startTimeID'],oneEvent['endTimeID'],oneEvent['teacherName'],oneEvent['classroomName'],str(oneEvent['startTime']),str(oneEvent['endTime']),oneEvent['startWeek'],oneEvent['endWeek'],oneEvent['studentNumber']))
        event.add('dtstart', dtstart_datetime)
        event.add('dtend', dtend_datetime)
        event.add('rrule', {'freq': 'weekly', 'interval': oneEvent['interval'], 'count': count})
        calt.add_component(event)

    with open('output.ics','wb') as f:
        f.write(calt.to_ical())


