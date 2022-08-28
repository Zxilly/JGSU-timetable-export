import json
import os
import traceback
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, RedirectResponse
from uvicorn.config import LOGGING_CONFIG

from curriculum import curriculum
from exam import exam
from static import refreshDescription

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class refreshMethod(Enum):
    CURRICULUM = 'curriculum'
    EXAM = 'exam'


class IcalResponse(Response):
    media_type = "text/calendar"


@app.get('/')
async def redirect():
    return RedirectResponse(url='https://github.com/Zxilly/JGSU-timetable-export')


@app.get('/{studentID}/{semesterName}/{ics_type}.ics',
         response_class=IcalResponse,
         description="Endpoint for getting ical file, should not be called manually.")
async def get_ical(studentID: str, semesterName: str, ics_type: str):
    if os.path.exists(f'data/{studentID}.{semesterName}.{ics_type}.ics'):
        with open(f'data/{studentID}.{semesterName}.{ics_type}.ics') as f:
            return str(f.read())
    raise HTTPException(404, "Please make cache before get file.")


@app.get('/refreshWithCookie', description=refreshDescription)
async def refreshWithCookie(cookies: str, method: refreshMethod = refreshMethod.CURRICULUM):
    try:
        if method == refreshMethod.CURRICULUM:
            return curriculum(cookies=cookies)
        elif method == refreshMethod.EXAM:
            return exam(cookies=cookies)
        else:
            raise Exception("Unknown refresh method.")
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(500, err)


@app.post('/refreshWithPayload')
async def refreshWithPayload(request: Request, payload=Body(...), method: refreshMethod = refreshMethod.CURRICULUM):
    try:
        pd = await request.json()
        if method == refreshMethod.CURRICULUM:
            return curriculum(payload=pd)
        elif method == refreshMethod.EXAM:
            return exam(payload=pd)
        else:
            raise Exception("Unknown refresh method.")
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(500, err)


@app.get('/script')
async def script(type: refreshMethod = refreshMethod.CURRICULUM):
    s = ""
    if type == refreshMethod.CURRICULUM:
        with open('sendCurPayload.js') as f:
            s = f.read()
    elif type == refreshMethod.EXAM:
        with open('sendExamPayload.js') as f:
            s = f.read()
    return s


if __name__ == '__main__':
    os.environ['SERVER'] = 'true'
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    uvicorn.run('server:app', host='0.0.0.0', port=24654)
