import base64
import hashlib
import json
from datetime import datetime

import icalendar
from static import *
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import api
import info

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def strHash(hash_string: str):
    return hashlib.md5(hash_string.encode()).hexdigest()


def dictHash(hash_dict: dict):
    return hashlib.md5(str(hash_dict).encode()).hexdigest()


def showData(data):
    print(json.dumps(data, ensure_ascii=False))
    exit(0)


def fixDay(day: int):
    if day == 1:
        return 7
    else:
        return day - 1


header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest(),
    'Authorization': 'Bearer undefined',
    'Referer': 'https://jw.jgsu.edu.cn:19995/'
}


def login():
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

    userData = json.loads(req.cookies.get_dict()['user'])

    # print(userData)

    userID = userData['userName']
    semesterName = userData['semester']

    print(semesterName)

    req = mainSession.get(url=api.semester).json()

    semesterStartTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 7
    semesterEndTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 7

    print(semesterStartTime)
    print(semesterEndTime)

    return mainSession, userID, semesterName, semesterStartTime, semesterEndTime


def getIcal(name: str):
    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'
    calt['X-WR-TIMEZONE'] = 'Asia/Shanghai'
    calt['X-WR-CALNAME'] = name
    tz = icalendar.Timezone()
    tz['tzid'] = 'Asia/Shanghai'
    tzStandard = icalendar.TimezoneStandard()
    tzStandard.add('X-LIC-LOCATION', 'Asia/Shanghai')
    tzStandard.add('TZOFFSETFROM', timedelta(hours=8))
    tzStandard.add('TZOFFSETTO', timedelta(hours=8))
    tzStandard.add('TZNAME', 'CST')
    tz.add_component(tzStandard)
    calt.add_component(tz)
    return calt


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, timedelta):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
