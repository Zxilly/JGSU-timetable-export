# hashcode：对应修复值dict
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

fix_dict = {
    'd90aa58689d965aa16e4c7063c8f5382': {
        "endTimeID": 7,
        "endTime": courseTimeDict[7] + COURSE_TIME
    }
}
