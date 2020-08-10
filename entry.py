import base64
import requests
import json

import api
import info

header = {
    'accessToken': '',
}

if __name__ == '__main__':
    req = requests.post(url=api.login, params={
        'username': info.studentID,
        'password': base64.b64encode(info.password.encode('UTF-8'))
    }).json()

    header['accessToken'] = req['data']['accessToken']
    userId = req['data']['userInfo']['userId']
    userType = req['data']['userInfo']['userType']

    req = requests.get(url=api.current).json()

    semester = req['data']['currentSemester']

    req = requests.get(url=api.weeklist).json()

    weekAll = int(req['data'][-1]['code'])

    week_list = list(range(1, weekAll + 1))

    semesterData = []

    for week in week_list:
        req = requests.post(url=api.course, headers=header, json={
            'academicYearSemester': semester,
            'userId': userId,
            'userType': userType,
            'weeks': [week]
        }).json()
        courseData = req['data']['course']
        semesterData.append(courseData)

    pointer_week = 0
    pointer_course = 0


    while(True):
        if semesterData[pointer_week][pointer_course]['courseName']=='':
            if pointer_course!=76:
                pointer_course +=1
                continue
            else:
                pointer_course=0
                if pointer_week!=weekAll-1:
                    pointer_week+=1
                    continue
                else:
                    break
        else:









