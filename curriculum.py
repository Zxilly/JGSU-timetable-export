import copy
import hashlib
from datetime import datetime
from typing import Dict
from uuid import uuid1

import icalendar
import pangu

import static
from entity.event import CourseEvent
from static import *
from utils import dict_hash, fix_day, get_ical, raw_week_parse, login

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
}


def curriculum(cookies: str = None, payload: Dict = None):
    if payload is None:
        main_session, user_id, student_num, semester_name, semester_start_time = login(cookies)
        req = main_session.post(url=static.course_url, json={
            "oddOrDouble": 0,
            "semester": semester_name,
            "startWeek": "1",
            "stopWeek": "22",
            "studentId": user_id,
            "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
        }, timeout=5).json()
        tmp_data = req['data']
    else:
        tmp_data = payload['data']
        student_num = payload['student_num']
        semester_name = payload['semester_name']
        semester_start_time = datetime.strptime(payload['semester_start_time'], "%Y-%m-%d").replace(tzinfo=TIMEZONE) + ONE_DAY * 1
        assert semester_start_time.weekday() == 0

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
                course_name = course_name.replace(' ', '')
                course_name = pangu.spacing_text(course_name)

                teacher = course_data['teacher']
                student_count = course_data['studentNum']
                class_name = course_data['className']
                classroom_name = course_data['classroomName']

                raw_weeks = course_data['weeks']

                start_time_pointer = copy.copy(time)
                end_time_pointer = copy.copy(time)

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
                    'rawWeeks': raw_weeks,
                    'studentNumber': student_count
                }

                parsed_one_course['startTime'] = courseTimeDict[parsed_one_course['startTimeID']]
                parsed_one_course['endTime'] = courseTimeDict[parsed_one_course['endTimeID']] + COURSE_TIME

                parsed_course_data.append(copy.deepcopy(parsed_one_course))
                parsed_one_course.clear()
            else:
                break
    url = f'https://ical.learningman.top/{student_num}/{semester_name}/curriculum.ics'
    calt = get_ical(f'{semester_name} 课表', url)

    courses: Dict[str, CourseEvent] = {}
    for course in parsed_course_data:
        ev = CourseEvent(
            day=int(course['day']),
            courseName=course['courseName'],
            className=course['className'],
            classroomName=course['classroomName'],
            startTimeID=course['startTimeID'],
            endTimeID=course['endTimeID'],
            startTime=course['startTime'],
            endTime=course['endTime'],
            teacherName=course['teacherName'],
            weeks=raw_week_parse(course['rawWeeks']),
            studentCount=course['studentNumber'],
            semester_start_time=semester_start_time
        )
        if ev.identify in courses:
            courses[ev.identify].merge(ev)
        else:
            courses[ev.identify] = ev

    for oneEvent in courses.values():
        dt_start_datetime = oneEvent.start_date + oneEvent.startTime
        dt_end_datetime = oneEvent.start_date + oneEvent.endTime

        event = icalendar.Event()
        event.add('summary', oneEvent.courseName)  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        if oneEvent.classroomName:
            event.add('location', oneEvent.classroomName)  # 地点
        event.add('description',
                  '{}'
                  '教师： {}\r\n'
                  '{}'
                  '时间： {} - {} \r\n'
                  '周期： {}\r\n'
                  '班级： {}\r\n'
                  '学生数： {}'.format(
                      oneEvent.period_str,
                      oneEvent.teacherName,
                      oneEvent.classroom_str,
                      str(oneEvent.startTime),
                      str(oneEvent.endTime),
                      oneEvent.cycle_str,
                      oneEvent.className,
                      oneEvent.studentCount
                  )
                  )
        event.add('dtstart', dt_start_datetime)
        event.add('dtend', dt_end_datetime)

        rrule = oneEvent.rrule
        if rrule:
            event.add('rrule', rrule)

        calt.add_component(event)

    with open(f'data/{student_num}.{semester_name}.curriculum.ics', 'wb') as f:
        f.write(calt.to_ical())

    return url


if __name__ == '__main__':
    curriculum()
