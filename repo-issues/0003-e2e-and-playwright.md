Title: Playwright E2E for browser test runner UI

Description:
Add Playwright tests to validate the UI flows in `public/tests/*`: run tests from browser UI, stream logs, register webhooks, and provider secret retrieval.

Checklist:
- [ ] Add Playwright test project and config
- [ ] Write tests for `runner.html` run flow and `history.html` results display
- [ ] Mock external providers where possible to keep tests deterministic
- [ ] Add CI job to run Playwright against the locally started servers (use `docker-compose` to provide services)

Priority: Medium
