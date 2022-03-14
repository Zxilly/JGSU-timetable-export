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
    CURRICULUM = 'curriculum'
    EXAM = 'exam'


@app.get('/{studentID}/{semesterName}/{type}.ics', response_class=PlainTextResponse)
async def getIcal(studentID: str, semesterName: str, type: str):
    if os.path.exists(f'data/{studentID}.{semesterName}.{type}.ics'):
        with open(f'data/{studentID}.{semesterName}.{type}.ics') as f:
            return str(f.read())
    raise HTTPException(404, "Please cache before get file.")


@app.post('/refresh')
async def refresh(cookies: str, method: refreshMethod = refreshMethod.CURRICULUM):
    if method == refreshMethod.CURRICULUM:
        return curriculum(cookies)
    elif method == refreshMethod.EXAM:
        return exam(cookies)
    raise HTTPException(500, "Method not found")


if __name__ == '__main__':
    os.environ['SERVER'] = 'true'
    uvicorn.run('server:app', host='0.0.0.0', port=24654)
