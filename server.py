import hashlib
import os
import traceback
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, RedirectResponse

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


@app.get('/{md5}',
         response_class=IcalResponse)
async def get_ical_with_hash(md5: str):
    # return file in data with md5
    files = os.listdir('data')
    for file in files:
        with open('data/' + file, 'r') as f:
            fc = f.read()
            h = hashlib.md5(fc.encode('utf-8')).hexdigest()
            print(h, file)
            if md5 == h:
                return fc
    raise HTTPException(status_code=404, detail='File not found')


@app.get('/{studentID}/{semesterName}/{ics_type}.ics',
         response_class=IcalResponse,
         description="Endpoint for getting ical file, should not be called manually.")
async def get_ical(studentID: str, semesterName: str, ics_type: str):
    if os.path.exists(f'data/{studentID}.{semesterName}.{ics_type}.ics'):
        with open(f'data/{studentID}.{semesterName}.{ics_type}.ics') as f:
            return str(f.read())
    raise HTTPException(404, "Please make cache before get file.")


@app.post('/refresh', description=refreshDescription)
async def refresh(cookies: str, method: refreshMethod = refreshMethod.CURRICULUM):
    try:
        if method == refreshMethod.CURRICULUM:
            return curriculum(cookies)
        elif method == refreshMethod.EXAM:
            return exam(cookies)
        else:
            raise Exception("Unknown refresh method.")
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(500, err)


if __name__ == '__main__':
    os.environ['SERVER'] = 'true'
    uvicorn.run('server:app', host='0.0.0.0', port=24654)
