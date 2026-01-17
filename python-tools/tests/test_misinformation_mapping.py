import os
import pytest
try:
    import requests
except Exception:
    requests = None


@pytest.mark.integration
def test_misinformation_map_available():
    """Check that misinformation mapping asset or API exists."""
    # local static file
    static = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'misinformation-map.html')
    if os.path.exists(static):
        assert True
        return
    if requests is None:
        pytest.skip('requests not installed and static asset missing')
    try:
        r = requests.get('http://127.0.0.1:8000/api/mapping')
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
    except requests.exceptions.ConnectionError:
        pytest.skip('Mapping API not reachable')
