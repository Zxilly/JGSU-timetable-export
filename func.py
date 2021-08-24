import base64
import hashlib
import json
import os
from datetime import datetime

import icalendar
from static import *
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import api

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
    dict_cookies = {}

    if os.getenv('CI'):
        cookies = os.getenv('cookies').replace('\\', '')
    else:
        import info
        cookies = info.cookies

    for line in cookies.split(';'):
        if line.isspace():
            continue
        name, value = line.strip().split('=', 1)
        dict_cookies[name] = value

    mainSession = requests.session()
    mainSession.params = {"_t": int(datetime.now().timestamp())}
    mainSession.headers = header
    mainSession.verify = False

    mainSession.cookies.update(dict_cookies)

    # loginDict = {
    #     "userName": studentID,
    #     "token": base64.b64encode(password.encode('UTF-8')).decode(),
    #     "target": "",
    #     "pattern": "teacher-login",
    #     "timestamp": int(datetime.now().timestamp() * 1000),
    #     "username": studentID,
    #     'password': hashlib.md5(("admin" + password).encode("UTF-8")).hexdigest(),
    # }

    # req = mainSession.post(url=api.login, params=loginDict, data={})

    # if req.json()['code'] in [51000003, 50000012]:
    #     print(req.json())
    #     exit(1)

    userData = json.loads(dict_cookies['user'])

    # print(userData)

    userID = userData['userName']

    try:
        if os.getenv('CI'):
            import importlib.util
            import sys
            spec = importlib.util.spec_from_file_location('infoexample', 'info.example.py')
            info_example = importlib.util.module_from_spec(spec)
            sys.modules['infoexample'] = info_example
            spec.loader.exec_module(info_example)
            from infoexample import semester
        else:
            from info import semester
        semesterName = semester['name']
        semesterStartTime = semester['start']
    except ImportError:
        if os.getenv('CI'):
            raise Exception("Failed CI")
        semesterName = userData['semester']
        req = mainSession.get(url=api.semester).json()
        print(req)
        semesterStartTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE)

    # semesterEndTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 2

    print(semesterName)
    print(semesterStartTime)

    assert semesterStartTime.weekday() == 0

    return mainSession, userID, semesterName, semesterStartTime


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
