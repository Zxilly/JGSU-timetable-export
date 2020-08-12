import base64
import hashlib
import json
import re
from datetime import datetime

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import api
import info

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
    # 'csrfToken':'610453b7b20b8a4402042a201b3665b1',
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

    startTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d")
    endTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d")

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
    parsedCourseData = {}

    for course in tmpData:
        time = course['time']['timeCode']
        week = course['week']['weekCode']
        key = int(week) * 100 + int(time)
        courseData[key]={}
        for course in course['courseList']:
            courseData[key][course['courseCode']] = course

    parsedCourseDataPointer = 0
    for weekPointer in range(1, 8):
        for coursePointer in range(1, 12):
            print(weekPointer * 100 + coursePointer)
            if courseData[weekPointer * 100 + coursePointer]:






    for weekPointer in range(1, 8):
        parsedCourseDataPointer = 0
        for coursePointer in range(1, 12):
            print(weekPointer * 100 + coursePointer)
            if courseData[weekPointer * 100 + coursePointer]:
                data = courseData[weekPointer * 100 + coursePointer]
                if parsedCourseData:
                    if parsedCourseData[parsedCourseDataPointer]:
                        if data['courseName'] == parsedCourseData[parsedCourseDataPointer]['courseName']:
                            parsedCourseData[parsedCourseDataPointer]['endTime'] = coursePointer
                            continue
                        else:
                            parsedCourseDataPointer += 1
                reObject = re.compile(r'(\d*)-(\d*)( 单)?')
                print(data['weeks'])
                parsedWeek = re.match(reObject, data['weeks']).groups()
                startWeek = parsedWeek[0]
                endWeek = parsedWeek[1]
                interval = 2 if parsedWeek[2] else 1
                parsedCourseData[parsedCourseDataPointer] = {
                    "courseName": data['courseName'],
                    'teacherName': data['teacherName'],
                    'className': data['className'],
                    'classroomName': data['classroomName'],
                    'numberOfStudent': data['numberOfStudent'],
                    'startTime': coursePointer,
                    'endTime': coursePointer,
                    'startWeek': startWeek,
                    'endWeek': endTime,
                    'interval': interval,
                }
        if parsedCourseData:
            if not parsedCourseData[parsedCourseDataPointer]:
                parsedCourseDataPointer += 1

    print(parsedCourseData)