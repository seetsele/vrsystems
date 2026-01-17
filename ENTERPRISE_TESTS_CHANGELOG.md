# Enterprise Tests & Tooling — Changelog

Summary of test scaffolding, probes, scanners and UI artifacts added for enterprise live/visual testing.

Files added or modified (high level):

- `tests/enterprise/run_api_full.py` — artifact-first API runner that records per-endpoint JSON artifacts to `test-vault/` and updates `enterprise-summary.json`.
- `tests/enterprise/test_api_full.py` — pytest consumer that parametrizes tests from artifacts; supports non-strict (skip) and strict (JSON Schema) modes.
- `tests/enterprise/check_fireworks.py` — multi-probe Fireworks API checker that records latency, response snippets and quota parsing artifacts.
- `tests/enterprise/quota_monitor.py` — monitor that reads provider summaries and alerts on low quota (configurable threshold).
- `tests/enterprise/check_zyte_usage.py` — scanner for `ZYTE_API_KEY` presence and code imports referencing Zyte/Scrapy.
- `tests/visual/ui-flows.spec.ts`, `tests/visual/test-visual.spec.ts` — Playwright E2E + visual snapshot specs with screenshot capture on failures.
- `public/enterprise-test-suite.html`, `public/enterprise-runner.js` — browser-runner for interactive test execution in a browser.
- `tools/find_unused_defs.py` and `tools/find_unused_defs_app.py` — conservative and focused scanners for likely-unused functions/classes; output CSVs in `tools/`.
- `tests/enterprise/schemas/*.json` — minimal JSON Schemas used by strict validation mode in the pytest runner.
- `playwright.config.ts` — Playwright config for headless Chromium runs against `public/`.
- CSS/fonts: `desktop-app/renderer/styles.css` and `public/assets/css/verity-theme.css` — webfont imports (Inter + JetBrains Mono) and test-stabilizing styles (disable animations during snapshots).
- CI: `.github/workflows/enterprise-tests.yml` and `.github/SETUP_ENTERPRISE_CI.md` — workflow to run runner, Playwright, provider probes and package artifacts.

Where outputs are saved when runs succeed:

- Artifacts and per-run JSON: `test-vault/` (runner and provider probe outputs).
- Unused defs CSV: `tools/unused_app.csv` (focused scan). Expanded scan: `tools/unused_app_expanded.csv` (if present).
- Playwright HTML report (when run locally): `playwright-report/` (open with `npx playwright show-report`).

How to run locally (recommended):

1. Install Node and Python dependencies:

```bash
npm ci
npx playwright install
python -m pip install -r python-tools/requirements.txt
```

2. Run the API runner (writes `test-vault/`):

```bash
python tests/enterprise/run_api_full.py --target http://localhost:8000
```

3. Run pytest consumer (non-strict):

```bash
python -m pytest tests/enterprise/test_api_full.py -q
```

4. Run Playwright (Chromium) and open the visual report:

```bash
npx playwright test --project=chromium --reporter=html
npx playwright show-report
```

Notes & next steps:
- I ran the unused-defs scanner; the focused CSV is at `tools/unused_app.csv` (top entries include many `python-tools/*` definitions such as `AIProviders`, `AnalyticsEvent`, `CircuitBreaker`, etc.). Review and triage by priority — I can produce a filtered CSV excluding test-only files or generate a PR removing or deprecating candidates.
- I tried to run Playwright from this environment but Node/PowerShell execution did not complete here — please run the Playwright commands locally (above) and paste `playwright-report/` path or upload the HTML; I will analyze diffs and update baselines if needed.
- If you want, I can create a Git branch and open a PR with the changelog and scanners included.

If you want me to proceed with any of the next steps (filter CSV, open PR, or analyze Playwright report), tell me which one and I'll proceed.
