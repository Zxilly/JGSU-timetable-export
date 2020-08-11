import base64
import hashlib
import json
from datetime import datetime

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import api
import info

header = {
    'csrfToken': hashlib.md5((str(int(datetime.now().timestamp())) + "lyedu").encode('UTF-8')).hexdigest()
    # 'csrfToken':'610453b7b20b8a4402042a201b3665b1',
}
if __name__ == '__main__':
    mainSession = requests.session()
    mainSession.params = {"_t": int(datetime.now().timestamp())}
    mainSession.headers = header
    mainSession.verify = False

    loginDict = {
        "userName": info.studentID,
        "token": base64.b64encode(info.password.encode('UTF-8')).decode(),
        "target": "",
        "pattern": "manager-login",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "username": info.studentID,
        'password': hashlib.md5(("admin" + info.password).encode("UTF-8")).hexdigest(),
    }

    req = mainSession.post(url=api.login, params=loginDict, data={})

    userData = json.loads(req.cookies.get_dict()['user'])

    userID = userData['userName']
    semesterName = userData['semester']

    req = mainSession.get(url=api.semester).json()

    startTime = datetime.strptime(req['data']['ksrq'], "%Y-%m-%d")
    endTime = datetime.strptime(req['data']['jsrq'], "%Y-%m-%d")

    req = mainSession.post(url=api.course, json={
        "oddOrDouble": 0,
        "semester": semesterName,
        "startWeek": "1",
        "stopWeek": "22",
        "studentId": userID,
        "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    }).json()

    courseData = req['data']

    for course in courseData:


