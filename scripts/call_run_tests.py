import urllib.request, json, sys
try:
    req=urllib.request.Request('http://127.0.0.1:8010/run-tests', data=json.dumps({'target':'python-tools/tests'}).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        print('STATUS', r.status)
        data = r.read().decode()
        print(data)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
