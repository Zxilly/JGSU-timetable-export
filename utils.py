import hashlib
import json
import os
import re
from datetime import datetime

import icalendar
import requests
import urllib3

import static
from static import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def str_hash(hash_string: str):
    return hashlib.md5(hash_string.encode()).hexdigest()


def dict_hash(hash_dict: dict):
    return hashlib.md5(str(hash_dict).encode()).hexdigest()


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

    user_id = user_data['userName']

    req = main_session.get(static.student_number_url.format(user_id)).json()
    student_num = req['data']['xh']

    semester_name = user_data['semester']
    req = main_session.get(url=static.semester_url).json()
    semester_start_time = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 1

    assert semester_start_time.weekday() == 0

    return main_session, user_id, student_num, semester_name, semester_start_time


def get_ical(name: str, url: str):
    cal = icalendar.Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//Zxilly//JGSUCalender//CN'
    cal['X-WR-TIMEZONE'] = 'Asia/Shanghai'
    cal['X-WR-CALNAME'] = name
    cal['URL'] = url
    cal['REFRESH-INTERVAL'] = icalendar.vDuration(timedelta(hours=4))
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


def raw_week_parse(rawWeek: str):
    pos = []
    weeks = rawWeek.split(';')
    for week in weeks:
        week = week.strip()
        th_spec = re.compile(r'[单双]')
        tw_spec = re.compile(r'\d{1,2}-\d{1,2}')
        on_spec = re.compile(r'\d')
        if th_spec.search(week):
            pattern = week[-1]
            week = week[:-2]
            nums = week.split('-')
            for num in range(int(nums[0]), int(nums[1]) + 1):
                if pattern == '单':
                    if num % 2 == 1:
                        pos.append(num)
                elif pattern == '双':
                    if num % 2 == 0:
                        pos.append(num)
        elif tw_spec.match(week):
            nums = week.split('-')
            for num in range(int(nums[0]), int(nums[1]) + 1):
                pos.append(num)
        elif on_spec.match(week):
            pos.append(int(week))
        else:
            raise ValueError('无法识别的周数')
        pos.sort()
    return pos


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, timedelta):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
