Recommendations & next steps
===========================

Short-term (local/dev):
- Use the provided `docker-compose.yml` + `python-tools/start_compose.*` scripts to run the stack (static UI, runner, Prometheus, Grafana).
- Keep SQLite for local dev, but migrate FastAPI runner to use Postgres for production parity.
- Add a small Compose/Make target to run migrations and create DB backups.

Medium-term (hardening & infra):
- Replace provider secret storage with a KMS/Vault-backed encryption (AWS KMS, GCP KMS, or HashiCorp Vault).
- Move persistence to Postgres and add Alembic migrations (`python-tools` DB schema).
- Run background workers for webhooks using Celery/RQ and persist queue state in Postgres.
- Add TLS and optional OIDC/RBAC for the FastAPI runner; support JWT bearer tokens for UI-authenticated runs.

Testing & CI:
- Add Playwright E2E tests covering the browser runner pages and APIs (`public/tests/*`).
- Add CI job to run `local_smoke_tests.py` and `python-tools` unit tests; publish test artifacts and JUnit results.

Observability & Ops:
- Configure Prometheus scrape (already added) and import the Grafana dashboard (`python-tools/grafana/test_runner_dashboard.json`).
- Add alerting rules for webhook queue backlog and repeated failed deliveries.
- Add retention/compaction job for `runs` table and DB backups.

Security & compliance:
- Rate-limit /run-tests and require API keys or JWT to avoid abuse.
- Add redaction policy tests to ensure no PII escapes via logs/webhooks.

Deployment:
- Provide a production deployment recipe (Dockerfile improvements, Compose/Helm chart) and runbook for backups and restore.
