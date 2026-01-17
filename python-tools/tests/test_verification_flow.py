import os
import pytest
try:
    import requests
except Exception:
    requests = None


@pytest.mark.integration
def test_verification_endpoint():
    """POST to verification endpoint or skip if not running."""
    if requests is None:
        pytest.skip('requests not installed')
    url = 'http://127.0.0.1:8000/verify'
    try:
        r = requests.post(url, json={'claim': 'smoke-test'})
        assert r.status_code in (200, 202)
    except requests.exceptions.ConnectionError:
        pytest.skip('Verification service not running')
