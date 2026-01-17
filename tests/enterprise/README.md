Enterprise Test Runner
======================

Overview
--------
This folder contains the enterprise-grade test runner `run_enterprise.py`.
It is designed to run live against a Verity deployment and:

- Execute a broad matrix of API and feature checks
- Log detailed JSON reports to `test-vault/`
- Maintain a history file used to adapt future runs
- Produce concise suggestions for failures

Usage
-----
Run against a local server (default `http://localhost:8000`):

```powershell
python .\tests\enterprise\run_enterprise.py
```

To point at another environment set `TEST_URL`:

```powershell
$env:TEST_URL = 'https://staging.verity.ai'
python .\tests\enterprise\run_enterprise.py
```

If your deployment requires an API key, set `TEST_API_KEY` or `VERITY_TEST_KEY`.

Outputs
-------
- Per-run: `test-vault/enterprise-<unix_ts>.json` (detailed test results)
- History: `test-vault/enterprise-history.json` (last 100 runs summary)

Notes
-----
- The runner intentionally runs live tests by default. Ensure your environment
  variables for external providers are configured before running.
- The adaptive behavior is simple: repeated failures add variant inputs for
  the next run to exercise edge-cases.
