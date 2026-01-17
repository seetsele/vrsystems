import sys
from pathlib import Path
import pytest

# ensure python-tools is importable when pytest runs from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api_server_v10 import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.integration
def test_root_returns_ok():
    r = client.get('/')
    assert r.status_code < 500


@pytest.mark.smoke
def test_verify_endpoint_accepts_json():
    # quick smoke: verify that OpenAPI is exposed and the route metadata exists
    r = client.get('/openapi.json')
    assert r.status_code == 200
    data = r.json()
    assert 'paths' in data and isinstance(data['paths'], dict)
