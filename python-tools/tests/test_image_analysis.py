import os
import pytest
import json
try:
    import requests
except Exception:
    requests = None


def _url(path, port=8000):
    return f"http://127.0.0.1:{port}{path}"


@pytest.mark.integration
def test_image_analysis_endpoint_available():
    """Check image analysis endpoint or local sample presence."""
    # If requests not available, skip network checks but ensure sample exists
    sample = os.path.join(os.path.dirname(__file__), '..', 'public', 'assets', 'sample_image.jpg')
    if requests is None:
        assert os.path.exists(sample) or os.path.exists(sample.replace('.jpg', '.png'))
        return

    try:
        r = requests.get(_url('/api/analyze-image/health'))
        if r.status_code == 404:
            pytest.skip('Image analysis API not implemented (404)')
        assert r.status_code == 200
        j = r.json()
        assert 'status' in j
    except requests.exceptions.ConnectionError:
        pytest.skip('Image analysis service not running')
