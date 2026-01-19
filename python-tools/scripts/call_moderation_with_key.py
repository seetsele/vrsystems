#!/usr/bin/env python3
"""Simple helper to call /api/moderate with a scoped API key for local testing."""
import os
import sys
import json
from urllib.request import Request, urlopen

API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
API_KEY = os.getenv('API_KEY', 'PiLl66YdclgQCwEQFwp7rB5Diw3xDpvJi2cR709TNkA')

def call_moderate(text='test'):
    url = API_URL.rstrip('/') + '/api/moderate'
    payload = json.dumps({'text': text}).encode('utf-8')
    req = Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }, method='POST')
    try:
        with urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')
            print('Status:', r.status)
            print('Body:', body)
    except Exception as e:
        print('Request failed:', e)
        sys.exit(2)

if __name__ == '__main__':
    txt = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'test'
    call_moderate(txt)
