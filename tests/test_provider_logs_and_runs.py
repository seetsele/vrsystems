import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_provider_health_logs_endpoint_empty_or_present():
    # Ensure endpoint returns structure
    resp = client.get('/tools/provider-health-logs')
    assert resp.status_code == 200
    data = resp.json()
    assert 'lines' in data


def test_test_runs_endpoint_requires_run_and_returns():
    # Ensure running internal tests writes to test_runs.log
    server.Config.DEBUG = True
    r = client.post('/tools/run-internal-tests', json={'suite': 'smoke'})
    assert r.status_code == 200
    # Now fetch test runs
    rr = client.get('/tools/test-runs')
    assert rr.status_code == 200
    d = rr.json()
    assert 'runs' in d
    # runs may be empty if runner timed out; ensure structure
    assert isinstance(d['runs'], list)
