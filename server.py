import uvicorn
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import PlainTextResponse
import os
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

from curriculum import curriculum
from exam import exam

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class refreshMethod(Enum):
    CURRICULUM = 0,
    EXAM = 1


@app.get('/{studentID}/exam.ics', response_class=PlainTextResponse)
async def getExam(studentID: str):
    if os.path.exists(f'{studentID}.exam.ics'):
        with open(f'{studentID}.exam.ics') as f:
            return str(f.read())
    raise HTTPException(404)


@app.get('/{studentID}/curriculum.ics', response_class=PlainTextResponse)
async def getCurriculum(studentID: str):
    if os.path.exists(f'{studentID}.curriculum.ics'):
        with open(f'{studentID}.curriculum.ics') as f:
            return str(f.read())
    raise HTTPException(404)


@app.post('/refresh')
async def refresh(method: refreshMethod = refreshMethod.CURRICULUM, cookies=Body(..., embed=False)):

    if method == refreshMethod.CURRICULUM:
        return curriculum(cookies)
    elif method == refreshMethod.EXAM:
        return exam(cookies)


if __name__ == '__main__':
    os.environ['SERVER'] = 'true'
    uvicorn.run('server:app', host='0.0.0.0', port=24654)
