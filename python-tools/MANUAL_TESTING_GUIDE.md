# Manual Testing Guide for Verity Test Suite

## How to Run Manual Tests

1. **Via Python Script**
   - Open a terminal in your workspace root.
   - Run: `python python-tools/test_comprehensive.py`
   - To test a specific claim, modify the `test_categories` dictionary in `test_comprehensive.py` and add your claim and expected verdict.

2. **Targeted Nuance Testing**
   - Run: `python python-tools/test_specific_claims.py`
   - Add your nuanced claims to the `tests` list in `test_specific_claims.py`.

3. **API Direct Testing**
   - Use a tool like Postman or curl to POST to `http://localhost:8000/verify` with `{ "claim": "your claim here" }`.
   - Review the JSON response for verdict, confidence, and provider details.

4. **Web UI Manual Testing** 🔧
   - Open `public/test-suite.html` in a browser (when your server is running on `http://localhost:8000`).
   - Use the **Run Manual** input to submit any claim and see the verdict, confidence, and top sources.
   - Use **Run Rate Limit Test** to simulate rapid requests and observe if a 429 is returned by the server (use responsibly).
   - Use **Check Providers** to fetch `/providers/health` and see which providers are in cooldown.

5. **Simulation & Internal Test Runner** 🔬
   - For extra safety, you can require a simulation key via the `SIMULATE_KEY` environment variable. Set it like:
     - `export SIMULATE_KEY=your-secret` (or set in your .env)
   - Optionally, limit client IPs allowed to use simulation endpoints with `SIMULATE_ALLOWED_IPS` (comma-separated list of IPs).
   - When `SIMULATE_KEY` is configured, include header `X-SIM-KEY: your-secret` on simulation requests (recommended even in DEBUG).
   - The simulate endpoints also support a per-key rate limit (env: `SIMULATE_KEY_RATE_LIMIT`, default 60 req/min).
   - Simulation endpoint: `POST /tools/simulate` with body `{ "content": { "action": "provider_fail", "provider": "groq", "count": 3 } }` or similar.
   - Run internal small test runner: `POST /tools/run-internal-tests` with body `{ "suite": "smoke" }` and header `X-SIM-KEY` when required.
   - Simulation endpoints will reject unauthorized IPs and throttle keys that exceed the per-key rate limit.

6. **Metrics & Dashboard** 📊
   - Run Prometheus + Grafana via `docker/prometheus/docker-compose.yml` to scrape `/metrics` exposed by the API.
   - Import `public/grafana_provider_dashboard.json` into Grafana for a starter dashboard (panels for provider failures and cooldowns).

7. **CI Artifacts Viewer**
   - Use `public/ci-artifacts.html` to query GitHub Actions artifacts for a given `owner/repo` (requires a Personal Access Token for private repos).

6. **Provider Monitoring**
   - Run the provider monitor script to poll provider health periodically:
     - `python python-tools/monitor_providers.py`
   - Logs are written to `python-tools/provider_health.log` and the script prints warnings when providers are in cooldown.
   - Or add the Windows scheduled task with `scripts/create_windows_task.ps1` to run every 5 minutes.

## What to Look For
- Correct verdict (true, false, mixed, unverifiable, error)
- Reasonable confidence score
- Nuance analysis fields (is_nuanced, nuance_score, override_applied)
- Provider and source details
- Response time and error handling

## Troubleshooting
- If a provider fails, check API keys and health endpoints.
- For rate limits, try again after a short wait.
- For edge cases, review the explanation and sources in the response.

## Next Steps
- Submit new claims and edge cases.
- Document any failures or unexpected results.
- Use results to further improve the verification system.

---

*For advanced users: You can add new test scripts in the `python-tools/` or `tests/` folder to automate custom scenarios.*
