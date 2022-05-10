import copy
import hashlib
import re
import sys
from datetime import datetime
from uuid import uuid1

import icalendar

import api
from fix import fix_dict
from func import dict_hash, fix_day, login, get_ical
from static import *

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
}


def curriculum(cookies: str = None):
    print(cookies)
    main_session, user_id, student_num, semester_name, semester_start_time = login(cookies)

    req = main_session.post(url=api.course, json={
        "oddOrDouble": 0,
        "semester": semester_name,
        "startWeek": "1",
        "stopWeek": "22",
        "studentId": user_id,
        "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    }).json()

    print(main_session.cookies.items())
    print(req)
    tmp_data = req['data']
    all_course_data = []

    for timeSection in tmp_data:
        for timeSectionCourse in timeSection['courseList']:
            all_course_data.append(timeSectionCourse)

    purge_all_course_data = {}

    for day in range(1, 8):
        for time in range(1, 12):
            time_sign = (day, time)
            purge_all_course_data[time_sign] = {}

    for course_data in all_course_data:
        day = fix_day(int(course_data['dayOfWeek']))
        time = int(course_data['time'])
        time_sign = (day, time)
        purge_course_dict = {
            'courseName': course_data['courseName'],
            'weeks': course_data['weeks'],
            'teacher': course_data.get('teacherName', ''),
            'studentNum': course_data['numberOfStudent'],
            'classroomName': course_data.get('classroomName', ''),
            'className': course_data.get('teachingClassName', '')
        }
        purge_all_course_data.setdefault(time_sign, {})
        purge_all_course_data[time_sign][dict_hash(purge_course_dict)] = purge_course_dict

    parsed_course_data = []

    for time_sign in purge_all_course_data.keys():
        day = time_sign[0]
        time = time_sign[1]
        while True:
            if purge_all_course_data[time_sign]:
                current_opt_course = purge_all_course_data[time_sign].popitem()

                course_hash = current_opt_course[0]
                course_data = current_opt_course[1]

                course_name = course_data['courseName']

                teacher = course_data['teacher']
                student_num = course_data['studentNum']
                class_name = course_data['className']
                classroom_name = course_data['classroomName']

                raw_weeks = course_data['weeks']
                try:
                    parsed_weeks = re.match(re_object, raw_weeks).groups()
                    interval = 2 if parsed_weeks[2] else 1
                    start_week = parsed_weeks[0]
                    end_week = parsed_weeks[1]
                except AttributeError:
                    parsed_weeks = int(raw_weeks)
                    interval = 1
                    start_week = parsed_weeks
                    end_week = parsed_weeks

                start_time_pointer = copy.copy(time)
                end_time_pointer = copy.copy(time)

                # print(courseName, str(parsedWeeks), rawWeeks)
                while True:
                    if end_time_pointer != 4 and end_time_pointer != 11:
                        if course_hash in purge_all_course_data[(day, end_time_pointer + 1)].keys():
                            purge_all_course_data[(day, end_time_pointer + 1)].pop(course_hash)
                            end_time_pointer += 1
                        else:
                            break
                    else:
                        break

                parsed_one_course = {
                    'day': day,
                    'courseName': course_name,
                    'className': class_name,
                    'classroomName': classroom_name,
                    'startTimeID': start_time_pointer,
                    'endTimeID': end_time_pointer,
                    'teacherName': teacher,
                    'startWeek': start_week,
                    'endWeek': end_week,
                    'interval': interval,
                    'studentNumber': student_num
                }

                one_course_hash = dict_hash(parsed_one_course)
                print(one_course_hash, parsed_one_course)
                if one_course_hash in fix_dict.keys():
                    fix_object = fix_dict[one_course_hash]
                    for key, value in fix_object.items():
                        parsed_one_course[key] = value
                    print("fixed:", parsed_one_course, file=sys.stderr)

                parsed_one_course['startTime'] = courseTimeDict[parsed_one_course['startTimeID']]
                parsed_one_course['endTime'] = courseTimeDict[parsed_one_course['endTimeID']] + COURSE_TIME

                parsed_course_data.append(copy.deepcopy(parsed_one_course))
                parsed_one_course.clear()
            else:
                break

    calt = get_ical(f'{semester_name} 课表')

    for oneEvent in parsed_course_data:
        count = int((int(oneEvent['endWeek']) - int(oneEvent['startWeek'])) / int(oneEvent['interval']) + 1)
        dtstart_datetime = semester_start_time + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 1) * ONE_DAY + oneEvent['startTime']
        dtend_datetime = semester_start_time + (int(oneEvent['startWeek']) - 1) * ONE_WEEK + (
                int(oneEvent['day']) - 1) * ONE_DAY + oneEvent['endTime']

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

    with open(f'data/{student_num}.{semester_name}.curriculum.ics', 'wb') as f:
        f.write(calt.to_ical())

    return f'https://ical.learningman.top/{student_num}/{semester_name}/curriculum.ics'


if __name__ == '__main__':
    curriculum()
