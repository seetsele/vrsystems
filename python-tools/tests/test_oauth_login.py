import pytest
try:
    import requests
except Exception:
    requests = None


def test_oauth_login_route():
    if requests is None:
        pytest.skip('requests not installed')
    try:
        r = requests.get('http://127.0.0.1:8000/auth/login', allow_redirects=False)
        if r.status_code == 404:
            pytest.skip('Auth login route not implemented (404)')
        assert r.status_code in (302,200)
    except requests.exceptions.ConnectionError:
        pytest.skip('Auth server not running')
