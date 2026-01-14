import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'python-tools'))
from fastapi.testclient import TestClient
import api_server_v9 as server

client = TestClient(server.app)


def test_simulate_provider_fail_recover():
    # Ensure simulation key is not required for this test
    server.Config.SIMULATE_KEY = None
    server.Config.DEBUG = True
    # Clear rate limit state to ensure tests aren't impacted by prior requests
    server.rate_limiter.requests.clear()
    server.simulate_key_limiter.requests.clear()

    resp = client.post('/tools/simulate', json={'content': {'action': 'provider_fail', 'provider': 'groq', 'count': 3}})
    assert resp.status_code == 200
    data = resp.json()
    assert 'Simulated' in data['message']

    # Check providers health shows groq in cooldown
    ph = client.get('/providers/health').json()
    assert 'groq' in ph['health']['in_cooldown'] or server.provider_health.failures.get('groq',0) >= 3

    # Recover
    resp2 = client.post('/tools/simulate', json={'content': {'action': 'provider_recover', 'provider': 'groq'}})
    assert resp2.status_code == 200
    # slight delay to ensure state propagation
    import time
    time.sleep(0.05)
    ph2_resp = client.get('/providers/health')
    assert ph2_resp.status_code == 200
    ph2 = ph2_resp.json()
    assert 'health' in ph2 and 'in_cooldown' in ph2['health']
    assert 'groq' not in ph2['health']['in_cooldown']


def test_simulate_requires_sim_key_when_set():
    # When the SIMULATE_KEY is configured, requests without the header are forbidden
    server.Config.SIMULATE_KEY = 'the-secret'
    resp = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}})
    assert resp.status_code == 403

    # With header should succeed
    resp2 = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}}, headers={'X-SIM-KEY': 'the-secret'})
    assert resp2.status_code == 200
    assert resp2.json()['limit'] == 2

    # cleanup
    server.Config.SIMULATE_KEY = None


def test_simulate_rate_limit():
    server.Config.DEBUG = True
    resp = client.post('/tools/simulate', json={'content': {'action': 'set_rate_limit', 'limit': 2}})
    assert resp.status_code == 200
    assert resp.json()['limit'] == 2

    # trigger rate limit
    tr = client.post('/tools/simulate', json={'content': {'action': 'trigger_rate_limit', 'identifier': 'test-rl', 'count': 5}})
    assert tr.status_code == 200
    assert tr.json()['allowed'] is False
