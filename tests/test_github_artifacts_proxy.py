import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_github_artifacts_proxy_requires_auth(monkeypatch):
    server.Config.DEBUG = True
    # mock requests.get
    class FakeResp:
        def __init__(self):
            self.status_code = 200
        def json(self):
            return {'artifacts': []}
    monkeypatch.setattr('requests.get', lambda *a, **k: FakeResp())

    # No auth header required in DEBUG
    resp = client.post('/tools/github-artifacts', json={'owner': 'octocat', 'repo': 'Hello-World'})
    assert resp.status_code == 200
    assert 'artifacts' in resp.json()

    # When SIMULATE_KEY is configured, require X-SIM-KEY
    server.Config.SIMULATE_KEY = 'sek'
    resp2 = client.post('/tools/github-artifacts', json={'owner': 'octocat', 'repo': 'Hello-World'})
    assert resp2.status_code == 403
    # With header works
    resp3 = client.post('/tools/github-artifacts', headers={'X-SIM-KEY': 'sek'}, json={'owner': 'octocat', 'repo': 'Hello-World'})
    assert resp3.status_code == 200
    server.Config.SIMULATE_KEY = None
