#!/usr/bin/env python3
"""
Enterprise test runner - live-first, adaptive, logged

Run this script to execute the full Verity enterprise test suite against a
live deployment. The runner always attempts live calls (use `TEST_URL` to
point to the target) and records results under `test-vault/`.

Behavior:
- Runs many endpoint checks (health, providers, image-forensics, realtime,
  verify, research-assistant, social-media, and more).
- Writes a detailed JSON run log: `test-vault/enterprise-<timestamp>.json`.
- Maintains a history file `test-vault/enterprise-history.json` used to
  adjust future runs (add variants for repeatedly-failing tests).
- Produces basic suggestions per failure to help prioritize fixes.

Designed to run on developer machines or CI where environment variables
for external providers are configured. If an endpoint returns 4xx/5xx the
failure will be logged and used to adapt the next run.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests


ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "test-vault"
VAULT.mkdir(exist_ok=True)

TEST_URL = os.getenv("TEST_URL", "http://localhost:8000")
API_KEY = os.getenv("TEST_API_KEY") or os.getenv("VERITY_TEST_KEY")
HEADERS = {"Content-Type": "application/json"}
if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"

HISTORY_FILE = VAULT / "enterprise-history.json"


def timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def load_history() -> Dict[str, Any]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return {"runs": []}
    return {"runs": []}


def save_history(history: Dict[str, Any]):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def log_run(result: Dict[str, Any]):
    fname = VAULT / f"enterprise-{int(time.time())}.json"
    fname.write_text(json.dumps(result, indent=2))
    # Append to history
    history = load_history()
    history.setdefault("runs", []).append({
        "time": result["started_at"],
        "summary": {"passed": result["summary"]["passed"], "failed": result["summary"]["failed"]},
        "details_path": str(fname.name),
    })
    # Keep only last 100 runs
    history["runs"] = history["runs"][-100:]
    save_history(history)


def suggest_for_failure(test_name: str, details: Dict[str, Any]) -> str:
    code = details.get("status_code")
    body = details.get("body")
    if code and 500 <= int(code) < 600:
        return "Server error: investigate provider integrations and retry logic; add exponential backoff and circuit-breaker tuning."
    if code == 429:
        return "Rate limited: increase capacity, add per-provider rate limits, or stagger calls in tests."
    if code and 400 <= int(code) < 500:
        return "Client error: validate payload and auth; ensure API keys and headers are correct."
    if isinstance(body, dict) and not body.get("success", True):
        return body.get("message") or "API returned unsuccessful response; inspect provider responses and input data."
    return "No specific suggestion available; inspect logs and repeat the test with verbose provider tracing."


def run_check(method: str, path: str, payload: Any = None, timeout: int = 30) -> Dict[str, Any]:
    url = TEST_URL.rstrip("/") + path
    start = time.time()
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, timeout=timeout)
        else:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
        elapsed = time.time() - start
        body = None
        try:
            body = r.json()
        except Exception:
            body = r.text
        success = r.status_code == 200 and (not isinstance(body, dict) or body.get("success", True) is not False)
        return {
            "name": path,
            "method": method,
            "url": url,
            "status_code": r.status_code,
            "duration_ms": int(elapsed * 1000),
            "body": body,
            "success": bool(success),
        }
    except Exception as e:
        return {"name": path, "method": method, "url": url, "status_code": None, "duration_ms": None, "body": str(e), "success": False}


def main():
    started = timestamp()
    history = load_history()

    # Base test matrix
    tests: List[Dict[str, Any]] = [
        {"name": "health", "method": "GET", "path": "/health"},
        {"name": "health_deep", "method": "GET", "path": "/health/deep"},
        {"name": "providers", "method": "GET", "path": "/providers"},
        {"name": "providers_health", "method": "GET", "path": "/providers/health"},
        {"name": "verify", "method": "POST", "path": "/verify", "payload": {"claim": "The sky is blue.", "source": "unit-test"}},
        {"name": "v3_batch_verify", "method": "POST", "path": "/v3/batch-verify", "payload": {"claims": ["Water is wet.", "The moon is made of cheese."]}},
        {"name": "image_forensics", "method": "POST", "path": "/tools/image-forensics", "payload": {"image_url": "https://example.com/sample.jpg"}},
        {"name": "realtime_stream", "method": "POST", "path": "/tools/realtime-stream", "payload": {"text": "This is a viral test message", "metadata": {"platform": "test"}}},
        {"name": "research_assistant", "method": "POST", "path": "/tools/research-assistant", "payload": {"query": "recent research on misinformation detection"}},
        {"name": "social_media", "method": "POST", "path": "/tools/social-media", "payload": {"url": "https://twitter.com/example/status/1"}},
        {"name": "source_credibility", "method": "POST", "path": "/tools/source-credibility", "payload": {"url": "https://example.com/article"}},
        {"name": "statistics_validator", "method": "POST", "path": "/tools/statistics-validator", "payload": {"text": "10% of people do X"}},
    ]

    # Adaptive: if recent runs show repeated failures, add additional variants for those tests
    recent = history.get("runs", [])[-5:]
    failed_names = set()
    for r in recent:
        # read details file if exists
        details_path = VAULT / r.get("details_path", "")
        if details_path.exists():
            try:
                content = json.loads(details_path.read_text())
                for t in content.get("tests", []):
                    if not t.get("success"):
                        failed_names.add(t.get("name") or t.get("url"))
            except Exception:
                continue

    # For each repeatedly failing test, add a variant payload to exercise edge cases
    for name in list(failed_names):
        if "image-forensics" in name or "image_forensics" in name:
            tests.append({"name": "image_forensics_variant", "method": "POST", "path": "/tools/image-forensics", "payload": {"image_url": "https://example.com/deepfake.png", "sensitivity": "high"}})
        if "realtime" in name:
            tests.append({"name": "realtime_high_viral", "method": "POST", "path": "/tools/realtime-stream", "payload": {"text": "Breaking: major event causing massive spread", "metadata": {"platform": "twitter", "shares": 100000}}})

    results: List[Dict[str, Any]] = []

    for t in tests:
        print(f"Running {t['name']} -> {t['path']}")
        try:
            res = run_check(t.get("method", "POST"), t["path"], payload=t.get("payload"))
            # normalize name
            res["name"] = t["name"]
            results.append(res)
            if not res.get("success"):
                print(f"  FAIL {t['name']} status={res.get('status_code')} url={res.get('url')}")
        except Exception:
            tb = traceback.format_exc()
            results.append({"name": t["name"], "success": False, "error": tb})

    passed = sum(1 for r in results if r.get("success"))
    failed = len(results) - passed

    summary = {"total": len(results), "passed": passed, "failed": failed}

    suggestions = []
    for r in results:
        if not r.get("success"):
            suggestions.append({"test": r.get("name"), "suggestion": suggest_for_failure(r.get("name"), r)})

    run_result = {
        "started_at": started,
        "finished_at": timestamp(),
        "test_url": TEST_URL,
        "summary": summary,
        "tests": results,
        "suggestions": suggestions,
    }

    log_run(run_result)

    # Print concise summary
    print(json.dumps({"summary": summary, "suggestions_count": len(suggestions)}, indent=2))

    # Exit code non-zero if any test failed
    if failed > 0:
        print("One or more enterprise tests failed; see test-vault for details.")
        sys.exit(2)


if __name__ == "__main__":
    main()
