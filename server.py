import asyncio
import json

from aiohttp import web

import qzsdk
from function import getcalender

routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
    await asyncio.sleep(0.1)
    return web.Response(body=b'Redirected',
                        status=302,
                        headers={'content-type': 'text/html', 'location': 'https://learningman.top/archives/246'})


@routes.get('/api/{account}/{password}')
async def entry(request):
    await asyncio.sleep(0.1)
    course = []
    course_true = []
    # function.getcalender()
    # print(request.match_info['account'])
    # print(request.match_info['password'])
    # print(ai.getCurrentTime())
    # return web.Response(body='{}'.format(ai.getCurrentTime()))
    account = request.match_info['account']
    password = request.match_info['password']
    ai = qzsdk.SW(account, password)
    print("开始爬取")
    for x in range(1, 18, 1):
        one_week_couse = json.loads(ai.getKbcxAzc(x))
        course += one_week_couse
        print('week {} finished'.format(x))
    print("爬取完成")
    for x in course:
        if x not in course_true:
            course_true.append(x)
    print("去重完成")
    return web.Response(body='{}'.format(getcalender(course_true, 1)),
                        headers={'content-type': 'text/calendar',
                                 'content-disposition': "attachment; filename=\"{}.ics\"".format(account)
                                 }
                        )


app = web.Application()
app.add_routes(routes)
web.run_app(app)

"""
@routes.get('/json')
async def json1(request):
    await asyncio.sleep(0.1)
    return web.json_response({
        'name': 'anonymous'})


@routes.get('/json/{name}')
async def json2(request):
    await asyncio.sleep(0.1)
    return web.json_response({
        'name': request.match_info['name'] or 'index'})


@routes.get('/hello/')
async def hello1(request):
    await asyncio.sleep(0.1)
    return web.Response(body="<h1>hello user</h1>", headers={'content-type': 'text/html'})


@routes.get('/hello/{name}')
async def hello2(request):
    await asyncio.sleep(0.1)
    return web.Response(body="<h1>hello %s</h1>" % request.match_info['name'], headers={'content-type': 'text/html'})

""" \
"""
async def index(request):
    await asyncio.sleep(0.5)
    return web.Response(status='',body=b'<h1></h1>')

async def hello(request):
    await asyncio.sleep(0.5)
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'))

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
"""
