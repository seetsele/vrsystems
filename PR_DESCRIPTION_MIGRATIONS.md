Title: chore(ci): add dispatchable migrations workflow + runbook

Summary
- Adds a dispatchable GitHub Actions workflow to create DB backups, run SQL migrations, and execute focused smoke tests.
- Adds migration SQL files, a `run_migrations.py` runner, a `RUNBOOK_MIGRATIONS.md` runbook, and deployment notes.

What changed
- `.github/workflows/migrations.yml` — dispatchable workflow to backup DB, run migrations, and run smoke tests.
- `python-tools/run_migrations.py` — migration runner used by the workflow.
- `database/migrations/` — SQL migrations (new schema objects: `subscriptions`, `email_logs`, `stripe_events`).
- `python-tools/api_server_v10.py` — harden Stripe webhook verification and safer event persistence.
- `RUNBOOK_MIGRATIONS.md` & `DEPLOYMENT_NOTES_MIGRATIONS.md` — runbook and secrets guidance.

Why
- Provide a safe, auditable process to apply schema changes with backups and automated smoke tests to catch regressions early.

Deployment notes
- Before running in production, add the required repository secrets (see `DEPLOYMENT_NOTES_MIGRATIONS.md`).
- Run first against a staging environment and validate artifacts and smoke tests.

Testing
- Local `python-tools` tests passed: `3 passed, 1 warning`.
- Recommended: run the workflow in `staging` environment and validate backups and smoke tests.

Risk & mitigation
- Risk: schema changes may introduce downtime or require data migrations. Mitigation: backup first, run in staging, and add manual approvals for production.

How to open the PR
1. Create a PR from branch `ci/add-migrations-workflow` into `main`.
2. Use this file's contents as the PR body (copy/paste from `PR_DESCRIPTION_MIGRATIONS.md`).

End.
