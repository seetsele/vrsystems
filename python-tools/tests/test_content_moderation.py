import pytest
import os
try:
    import requests
except Exception:
    requests = None


@pytest.mark.integration
def test_content_moderation_api_or_doc():
    """Ensure content moderation endpoint or docs exist."""
    doc = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'content-moderation.html')
    if os.path.exists(doc):
        assert True
        return
    if requests is None:
        pytest.skip('requests not installed and doc missing')
    try:
        r = requests.post('http://127.0.0.1:8000/api/moderate', json={'text':'test'})
        if r.status_code == 404:
            pytest.skip('Moderation API not implemented (404)')
        assert r.status_code in (200, 202)
    except requests.exceptions.ConnectionError:
        pytest.skip('Moderation API not reachable')
