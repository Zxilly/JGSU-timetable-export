import re
from datetime import datetime, time
from uuid import uuid1

import icalendar
import pytz
from dateutil.relativedelta import relativedelta

import info


def rmzero(input):
    return int(str(input))


def getcalender(course,server_status=0):
    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'

    """
    dict_week = {
        '01': relativedelta(hours=8, minutes=0),
        '02': relativedelta(hours=8, minutes=55),
        '03': relativedelta(hours=10, minutes=0),
        '04': relativedelta(hours=10, minutes=55),
        '05': relativedelta(hours=14, minutes=30),
        '06': relativedelta(hours=15, minutes=25),
        '07': relativedelta(hours=16, minutes=20),
        '08': relativedelta(hours=18, minutes=30),
        '09': relativedelta(hours=19, minutes=25),
        '10': relativedelta(hours=20, minutes=20),
    }
    """

    dirt_week = {
        1: time(8, 0),
        2: time(8, 55),
        3: time(10, 0),
        4: time(10, 55),
        5: time(14, 30),
        6: time(15, 25),
        7: time(16, 20),
        8: time(18, 30),
        9: time(19, 25),
        10: time(20, 20),
    }

    for one_course in course:
        print(one_course)

        week_start = int(one_course['kkzc'].split('-')[0])  # 周次开始
        try:
            week_end = int(one_course['kkzc'].split('-')[1])  # 周次结束
        except IndexError:
            week_end=week_start #catch单周课程
        course_weekday = int(re.match(r'\d', one_course['kcsj'])[0])

        course_period_regrx = re.compile(r'(\d\d)')  # 编译正则
        course_period_list = course_period_regrx.findall(one_course['kcsj'], 1)  # 得到一个课时的list
        course_period_num = len(course_period_list)  # 一共几节课
        course_period_start = int(course_period_list[0])  # 第一节课的课时号
        course_period_end = int(course_period_list[course_period_num - 1])  # 最后一节课的课时号

        # print(course_period_list)
        # course_time_regrx = re.search(r'(?<=\d)(\d)*','10102').group(0)
        # course_time_list = re.split(r'(\d\d)',course_time_regrx)

        lesson_time = relativedelta(minutes=45)

        # print(one_course['kcsj'])

        # print(one_course)

        dt_date = info.semester_start + relativedelta(weeks=(week_start - 1)) + relativedelta(
            days=(course_weekday - 1))  # 课程日期
        # dtstart_day = dtstart_day+

        dtstart_time = dirt_week[course_period_start]  # 上课时间
        dtend_time = dirt_week[course_period_end]  # 最后一节小课下课时间

        dtstart_datetime = datetime.combine(dt_date, dtstart_time, tzinfo=pytz.timezone("Asia/Shanghai"))  # 上课日期时间

        dtend_datetime = datetime.combine(dt_date, dtend_time, tzinfo=pytz.timezone("Asia/Shanghai"))  # 下课日期时间
        dtend_datetime += lesson_time

        # dtend_datetime = dtstart_datetime + lesson_time

        interval = 1 if one_course['sjbz'] == '0' else 2  # 单双周判定

        count = (week_end - week_start + 1) if one_course['sjbz'] == '0' else (((week_end - week_start) / 2) + 1)

        event = icalendar.Event()
        event.add('summary', one_course['kcmc'])  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        event.add('location', one_course['jsxm'] + '@' + one_course['jsmc'])  # 地点
        event.add('description',
                  '第{}-{}节\r\n教师： {}\r\n教室: {}'.format(course_period_start, course_period_end, one_course['jsxm'],
                                                       one_course['jsmc']))  # 教师名称
        event.add('dtstart', dtstart_datetime)
        event.add('dtend', dtend_datetime)
        event.add('rrule', {'freq': 'weekly', 'interval': interval, 'count': count})

        calt.add_component(event)

        # print_cal(calt)

    if server_status==0:
        with open('output.ics', 'w+', encoding='utf-8', newline='') as file:
            # file.write(calt.to_ical().decode('utf-8'))
            file.write(calt.to_ical().decode('utf-8'.replace('\r\n', '\n')).strip())
    else:
        return calt.to_ical().decode('utf-8'.replace('\r\n','\n').strip())
