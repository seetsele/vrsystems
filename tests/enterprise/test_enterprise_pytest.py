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


TEST_SPECS = [
    ("GET", "/health"),
    ("GET", "/health/deep"),
    ("GET", "/providers"),
    ("GET", "/providers/health"),
    ("POST", "/verify", {"claim": "The sky is blue.", "source": "pytest"}),
    ("POST", "/v3/batch-verify", {"claims": ["Water is wet.", "The moon is made of cheese."]}),
    ("POST", "/tools/image-forensics", {"image_url": "https://example.com/sample.jpg"}),
    ("POST", "/tools/realtime-stream", {"text": "This is a viral test message", "metadata": {"platform": "pytest"}}),
    ("POST", "/tools/research-assistant", {"query": "recent research on misinformation detection"}),
    ("POST", "/tools/social-media", {"url": "https://twitter.com/example/status/1"}),
    ("POST", "/tools/source-credibility", {"url": "https://example.com/article"}),
    ("POST", "/tools/statistics-validator", {"text": "10% of people do X"}),
]


def save_result(results: list):
    fname = VAULT / f"pytest-enterprise-{int(time.time())}.json"
    import json

    fname.write_text(json.dumps({"time": int(time.time()), "results": results}, indent=2))


@pytest.mark.parametrize("method,path,payload", [(m, p, payload if len(t) == 3 else None) for t in TEST_SPECS for (m, p, *payload) in [t]])
def test_enterprise_live(method, path, payload):
    url = TEST_URL + path
    start = time.time()
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=30)
        else:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    except Exception as e:
        pytest.fail(f"Request to {url} raised exception: {e}")

    duration = time.time() - start
    # Save minimal record for debugging
    rec = {"path": path, "method": method, "status_code": getattr(r, "status_code", None), "duration_ms": int(duration * 1000)}
    save_result([rec])

    assert r.status_code == 200, f"{method} {path} returned {r.status_code} - body: {r.text}"
