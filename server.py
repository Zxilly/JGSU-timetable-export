import traceback

import uvicorn
from fastapi import FastAPI, Body, HTTPException
import os
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, RedirectResponse

from curriculum import curriculum
from exam import exam_url

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


refreshDescription = """
Refresh data from server.
Can use script

```js
fetch(`https://ical.learningman.top/refresh?cookies=${encodeURIComponent(document.cookie)}&method=curriculum`, {
    method: 'POST',
    cache: 'no-cache',
    credentials: 'same-origin',
    mode: 'cors',
    redirect: 'follow',
    referrer: 'no-referrer',
}).then((resp) => {
    return resp.text()
}).then(uri => {
    console.log(uri)
})
```

on [`https://vpn2.jgsu.edu.cn/enlink/sso/login/`](https://vpn2.jgsu.edu.cn/enlink/sso/login/)
"""


@app.post('/refresh', description=refreshDescription)
async def refresh(cookies: str, method: refreshMethod = refreshMethod.CURRICULUM):
    try:
        if method == refreshMethod.CURRICULUM:
            return curriculum(cookies)
        elif method == refreshMethod.EXAM:
            return exam_url(cookies)
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(500, err)
    raise HTTPException(500, "Method not found")


if __name__ == '__main__':
    os.environ['SERVER'] = 'true'
    uvicorn.run('server:app', host='0.0.0.0', port=24654)
