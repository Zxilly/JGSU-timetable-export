from datetime import datetime
from uuid import uuid1

import icalendar
from dateutil.relativedelta import relativedelta

import info
import re


def rmzero(input):
    return int(str(input))


def getcalender(course):
    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'
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

    for one_course in course:
        event = icalendar.Event()
        event.add('summary', one_course['kcmc'])
        event.add('uid', str(uuid1()) + '@JGSU')
        event.add('dtstamp', datetime.now())
        event.add('location', one_course['jsmc'])
        event.add('description', one_course['jsxm'])

        week_start = int(one_course['kkzc'].split('-')[0])
        week_end = int(one_course['kkzc'].split('-')[1])
        course_weekday = int(re.match(r'\d',one_course['kcsj'])[0])

        #course_time_regrx = re.search(r'(?<=\d)(\d)*','10102').group(0)
        #course_time_list = re.split(r'(\d\d)',course_time_regrx)


        #print(one_course['kcsj'])
        exit(0)

        #print(one_course)

        dtstart_day = info.semester_start + relativedelta(weeks=(week_start-1))+relativedelta(days=(course_weekday-1))
        #dtstart_day = dtstart_day+
