from uuid import uuid1

from func import *



if __name__ == '__main__':
    mainSession, userID, semesterName, semesterStartTime = login()

    reqData = {
        "pageNo": 1,
        "pageSize": 20,
        "total": 0,
        "param": {"semesterId": semesterName}
    }

    reqHeader = {
        'permission': 'studentServer:examArrange'
    }

    mainSession.get('https://jw.jgsu.edu.cn:19995/')

    resp = mainSession.post(api.exam, json=reqData, headers=reqHeader).json()

    data = resp['data']['rows']

    info = []

    for one in data:
        day = datetime.strptime(one['positiveExamPaperDate'], '%Y-%m-%d').date()
        startTime = datetime.strptime(one['positiveExamTime'].split('~')[0], '%H:%M').time()
        endTime = datetime.strptime(one['positiveExamTime'].split('~')[1], '%H:%M').time()
        one['examStart'] = datetime.combine(day, startTime, TIMEZONE)
        one['examEnd'] = datetime.combine(day, endTime, TIMEZONE)
        print(one)

    calt = getIcal(f'{semesterName} 考试')

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

    with open('exam.ics', 'wb') as f:
        f.write(calt.to_ical())
