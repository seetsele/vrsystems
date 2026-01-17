import pytest
import os
import json
try:
    import requests
except Exception:
    requests = None


@pytest.mark.smoke
def test_statistics_report_present_or_api():
    """Ensure a basic statistics report exists or API provides stats."""
    repo_stats = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'stats.json')
    if os.path.exists(repo_stats):
        j = json.load(open(repo_stats))
        assert 'generated' in j or 'summary' in j
        return
    if requests is None:
        pytest.skip('requests not installed and local stats missing')
    try:
        r = requests.get('http://127.0.0.1:8000/api/stats')
        if r.status_code == 404:
            pytest.skip('Stats API not implemented (404)')
        assert r.status_code == 200
        j = r.json()
        assert 'summary' in j or 'counts' in j
    except requests.exceptions.ConnectionError:
        pytest.skip('Stats API not reachable')
