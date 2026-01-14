import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_run_internal_tests_requires_sim_key():
    # Ensure SIMULATE_KEY is set
    server.Config.SIMULATE_KEY = 'secret-sim'
    headers = {}  # no key
    resp = client.post('/tools/run-internal-tests', json={'suite': 'smoke'}, headers=headers)
    assert resp.status_code == 403

    # With correct key
    headers = {'X-SIM-KEY': 'secret-sim'}
    resp2 = client.post('/tools/run-internal-tests', json={'suite': 'smoke'}, headers=headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert 'exit_code' in data
    assert 'output' in data
