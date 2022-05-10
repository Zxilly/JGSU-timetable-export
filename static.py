from datetime import timedelta

import pytz

COURSE_TIME = timedelta(minutes=45)
WEEK_TIME = timedelta(days=7)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(weeks=1)

TIMEZONE = pytz.timezone("Asia/Shanghai")

courseTimeDict = {
    1: timedelta(hours=8, minutes=20),
    2: timedelta(hours=9, minutes=10),
    3: timedelta(hours=10, minutes=15),
    4: timedelta(hours=11, minutes=5),
    5: timedelta(hours=14, minutes=00),
    6: timedelta(hours=14, minutes=50),
    7: timedelta(hours=15, minutes=55),
    8: timedelta(hours=16, minutes=45),
    9: timedelta(hours=18, minutes=30),
    10: timedelta(hours=19, minutes=20),
    11: timedelta(hours=20, minutes=10)
}

session_url = 'https://jw.jgsu.edu.cn:19995/api/api/verificationCode'
login_url = 'https://jw.jgsu.edu.cn:19995/api/api/login'
course_url = 'https://jw.jgsu.edu.cn:19995/api/arrange/CourseScheduleAllQuery/studentCourseSchedule'
semester_url = 'https://jw.jgsu.edu.cn:19995/api/baseInfo/semester/selectCurrentXnXq'
exam_url = 'https://jw.jgsu.edu.cn:19995/api/exam/studentExamSchedule/queryPositiveExamSchedule'
student_number_url = 'https://jw.jgsu.edu.cn:19995/api/student/studentInfo/selectXsSyByid/{}'
