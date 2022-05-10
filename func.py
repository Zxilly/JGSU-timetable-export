import hashlib
import json
import os
from datetime import datetime

import icalendar
import requests

import api
from static import *


def str_hash(hash_string: str):
    return hashlib.md5(hash_string.encode()).hexdigest()


def dict_hash(hash_dict: dict):
    return hashlib.md5(str(hash_dict).encode()).hexdigest()


def show_data(data):
    print(json.dumps(data, ensure_ascii=False))
    exit(0)


def fix_day(day: int):
    if day == 1:
        return 7
    else:
        return day - 1


header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest(),
    'Authorization': 'Bearer undefined',
    'Referer': 'https://jw.jgsu.edu.cn:19995/'
}


def login(cookies):
    dict_cookies = {}

    if not cookies:
        if os.getenv('CI'):
            cookies = os.getenv('cookies').replace('\\', '')
        else:
            import info
            cookies = info.cookies

    for line in cookies.split(';'):
        if line.isspace() or len(line) == 0:
            continue
        name, value = line.strip().split('=', 1)
        dict_cookies[name] = value

    main_session = requests.session()
    main_session.params = {"_t": int(datetime.now().timestamp())}
    main_session.headers = header
    main_session.verify = False

    main_session.cookies.update(dict_cookies)

    user_data = json.loads(dict_cookies['user'])

    # print(userData)

    user_id = user_data['userName']

    req = main_session.get(api.student_number.format(user_id)).json()
    student_num = req['data']['xh']

    semester_name = user_data['semester']
    req = main_session.get(url=api.semester).json()
    print(req)
    semester_start_time = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 1

    print(semester_name)
    print(semester_start_time)

    assert semester_start_time.weekday() == 0

    return main_session, user_id, student_num, semester_name, semester_start_time


def get_ical(name: str):
    cal = icalendar.Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//Zxilly//JGSUCalender//CN'
    cal['X-WR-TIMEZONE'] = 'Asia/Shanghai'
    cal['X-WR-CALNAME'] = name
    tz = icalendar.Timezone()
    tz['tzid'] = 'Asia/Shanghai'
    tz_standard = icalendar.TimezoneStandard()
    tz_standard.add('X-LIC-LOCATION', 'Asia/Shanghai')
    tz_standard.add('TZOFFSETFROM', timedelta(hours=8))
    tz_standard.add('TZOFFSETTO', timedelta(hours=8))
    tz_standard.add('TZNAME', 'CST')
    tz.add_component(tz_standard)
    cal.add_component(tz)
    return cal


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, timedelta):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
