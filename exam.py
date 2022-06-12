from uuid import uuid1

from utils import *


def exam(cookies: str = None):
    main_session, user_id, student_num, semester_name, semester_start_time = login(cookies)

    req_data = {
        "pageNo": 1,
        "pageSize": 20,
        "total": 0,
        "param": {"semesterId": semester_name}
    }

    req_header = {
        'permission': 'studentServer:examArrange'
    }

    main_session.get('https://jw.jgsu.edu.cn:19995/')

    resp = main_session.post(static.exam_url, json=req_data, headers=req_header).json()

    data = resp['data']['rows']

    for one in data:
        day = datetime.strptime(one['positiveExamPaperDate'], '%Y-%m-%d').date()
        start_time = datetime.strptime(one['positiveExamTime'].split('~')[0], '%H:%M').time()
        end_time = datetime.strptime(one['positiveExamTime'].split('~')[1], '%H:%M').time()
        one['examStart'] = datetime.combine(day, start_time, TIMEZONE)
        one['examEnd'] = datetime.combine(day, end_time, TIMEZONE)

    url = f'https://ical.learningman.top/{student_num}/{semester_name}/exam.ics'
    calt = get_ical(f'{semester_name} 考试', url)

    for oneEvent in data:
        event = icalendar.Event()
        event.add('summary', "考试： " + oneEvent['courseName'])  # 标题
        event.add('uid', str(uuid1()) + '@JGSU')  # UUID
        event.add('dtstamp', datetime.now())  # 创建时间
        event.add('location', oneEvent['classroomName'])  # 地点
        event.add('dtstart', oneEvent['examStart'])
        event.add('dtend', oneEvent['examEnd'])
        event.add('description', "学期： {}\r\n座位号： {}\r\n学院： {}\r\n轮次：{}\r\n时间： {}".format(
            oneEvent['semester'],
            oneEvent['studentSetNumber'],
            oneEvent['departmentName'],
            oneEvent['roundName'],
            oneEvent['positiveExamPaperDate'] + ' ' + oneEvent['positiveExamTime']
        ))
        calt.add_component(event)

    with open(f'data/{student_num}.{semester_name}.exam.ics', 'wb') as f:
        f.write(calt.to_ical())

    return url


if __name__ == '__main__':
    exam()
