import json
import icalendar
import datetime
import qzsdk
import re

from info import *

course = []
course_true = []

ai = qzsdk.SW(account, password)
print(ai.getCurrentTime())
#one_week_couse = json.loads(ai.getKbcxAzc(1))
#for x in one_week_couse:
#    print(x)

# 获取完整课表
print("开始爬取")
for x in range(1, 18, 1):
    one_week_couse = json.loads(ai.getKbcxAzc(x))
    course += one_week_couse
    print('week {} finished'.format(x))
print("爬取完成")

# 生成去重课表list:course_true
for x in course:
    if x not in course_true:
        course_true.append(x)

#print(one_course)
for x in course_true:
    print(x)
    if(x['sjbz']==0):
        weekday = re.match(r'\d',x['kcsj']).group(1)
        date_time = semester_start+datetime.timedelta()

