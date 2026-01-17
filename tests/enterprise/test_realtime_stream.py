import os
import time
from pathlib import Path

import pytest
import requests


ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "test-vault"
VAULT.mkdir(exist_ok=True)

TEST_URL = os.getenv("TEST_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("TEST_API_KEY") or os.getenv("VERITY_TEST_KEY")
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"


def save(results):
    import json

    fname = VAULT / f"realtime-{int(time.time())}.json"
    fname.write_text(json.dumps({"time": int(time.time()), "results": results}, indent=2))


@pytest.mark.parametrize("payload", [
    {"text": "Small test message", "metadata": {"platform": "pytest", "shares": 1}},
    {"text": "This should simulate a high-viral message for stream processing", "metadata": {"platform": "twitter", "shares": 100000}},
    {"text": "Edge-case: empty metadata", "metadata": {}},
])
def test_realtime_stream_live(payload):
    url = TEST_URL + "/tools/realtime-stream"
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=60)
    except Exception as e:
        pytest.fail(f"Request failed: {e}")

    rec = {"status_code": r.status_code, "ok": r.ok, "body": r.text[:200]}
    save([rec])

    assert r.status_code in (200, 202), f"unexpected status {r.status_code}: {r.text}"
