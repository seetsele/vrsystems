import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure api_server_v10 can be imported when running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api_server_v10 import app


@pytest.mark.integration
def test_sdk_like_root_ping():
    client = TestClient(app)
    r = client.get('/')
    assert r.status_code < 500
