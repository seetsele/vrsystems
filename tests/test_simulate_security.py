import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_simulate_allowlist_blocks():
    server.Config.DEBUG = True
    server.Config.SIMULATE_ALLOWED_IPS = ['127.0.0.2']  # not matching localhost
    resp = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}})
    assert resp.status_code == 403
    server.Config.SIMULATE_ALLOWED_IPS = []


def test_simulate_key_rate_limit():
    server.Config.DEBUG = True
    server.Config.SIMULATE_KEY = 'rk123'
    headers = {'X-SIM-KEY': 'rk123'}
    # quickly consume allowed requests
    server.simulate_key_limiter.max_requests = 2
    # make 2 allowed requests
    for i in range(2):
        r = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}}, headers=headers)
        assert r.status_code == 200
    # third should be 429
    r2 = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}}, headers=headers)
    assert r2.status_code == 429
    # cleanup
    server.Config.SIMULATE_KEY = None
    server.simulate_key_limiter.requests.clear()
    server.simulate_key_limiter.max_requests = 60
