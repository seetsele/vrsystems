#!/usr/bin/env python3
"""Start lightweight local mock services used by the test suite.

Services started (localhost):
- Moderation API: 127.0.0.1:5010  (/moderate)
- Image analysis: 127.0.0.1:5020 (/analyze)
- Live stream websocket: 127.0.0.1:5030 (/stream) (websocket echo)
- Auth server: 127.0.0.1:5040 (/auth/health)
- Stats API: 127.0.0.1:5050 (/stats)
- Verification service: 127.0.0.1:5060 (/verify)
- Waitlist API: 127.0.0.1:5070 (/waitlist)

Run: python python-tools/mocks/start_mocks.py
"""
import asyncio
from aiohttp import web


async def moderation(request):
    data = {"result": "ok", "flags": []}
    return web.json_response(data)


async def image_analyze(request):
    return web.json_response({"labels": [], "safe": True})


async def auth_health(request):
    return web.json_response({"status": "ok"})


async def stats(request):
    return web.json_response({"uptime": 123, "requests": 0})


async def verify(request):
    return web.json_response({"verified": True})


async def waitlist(request):
    return web.json_response({"position": None, "joined": False})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"echo:{msg.data}")
        elif msg.type == web.WSMsgType.BINARY:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.CLOSE:
            break
    return ws


async def start_service(app, host, port):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"Started {app['name']} on http://{host}:{port}")


async def main():

    host = '127.0.0.1'
    services = []

    # Allow shifting base port via MOCK_BASE env var to avoid conflicts
    base = int(__import__('os').environ.get('MOCK_BASE', '5000'))

    # Moderation
    app1 = web.Application()
    app1['name'] = 'moderation'
    app1.router.add_post('/moderate', moderation)
    app1.router.add_get('/moderation/health', moderation)
    services.append((app1, host, base + 10))

    # Image analysis
    app2 = web.Application()
    app2['name'] = 'image_analysis'
    app2.router.add_post('/analyze', image_analyze)
    app2.router.add_get('/image/health', image_analyze)
    services.append((app2, host, base + 20))

    # Live stream websocket
    app3 = web.Application()
    app3['name'] = 'live_stream'
    app3.router.add_get('/stream', websocket_handler)
    services.append((app3, host, base + 30))

    # Auth server
    app4 = web.Application()
    app4['name'] = 'auth'
    app4.router.add_get('/auth/health', auth_health)
    services.append((app4, host, base + 40))

    # Stats API
    app5 = web.Application()
    app5['name'] = 'stats'
    app5.router.add_get('/stats', stats)
    services.append((app5, host, base + 50))

    # Verification service
    app6 = web.Application()
    app6['name'] = 'verify'
    app6.router.add_post('/verify', verify)
    app6.router.add_get('/verify/health', verify)
    services.append((app6, host, base + 60))

    # Waitlist API
    app7 = web.Application()
    app7['name'] = 'waitlist'
    app7.router.add_get('/waitlist', waitlist)
    services.append((app7, host, base + 70))

    # start all
    for app, h, p in services:
        await start_service(app, h, p)

    print('All mock services started. Press Ctrl+C to stop.')
    # run forever
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Shutting down mocks')
