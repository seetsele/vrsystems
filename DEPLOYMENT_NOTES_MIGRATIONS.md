# Migration workflow and deployment notes

This PR adds a GitHub Actions workflow that:

- Creates a Postgres DB backup artifact using `pg_dump`.
- Runs `python-tools/run_migrations.py` against the `DATABASE_URL` provided as a repo secret.
- Runs a focused smoke/integration test (`test_stripe_webhook_integration.py`) and uploads logs.

Required repository secrets (add these in Settings → Secrets → Actions):

- `DATABASE_URL` — Postgres connection string used for migrations and backups.
- `SUPABASE_URL` — Supabase project URL (for tests).
- `SUPABASE_SERVICE_KEY` — Service role key for server-side upserts and idempotency.
- `STRIPE_SECRET_KEY` — Stripe secret key (for integration checks).
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret (for webhook verification).
- `SENDGRID_API_KEY` — SendGrid API key (if running email-related tests).
- `FROM_EMAIL` — From address for transactional emails used in tests.
- `ADMIN_EMAIL` — Admin contact for notifications.
- `ADMIN_SLACK_WEBHOOK` — Slack webhook URL for admin alerts (optional).

Extra guidance for secrets configuration:

- `DATABASE_URL`: Use the managed read/write connection string for the target environment. For RDS/Aurora ensure TLS is enabled and the user has schema modification rights.
- `SUPABASE_SERVICE_KEY`: This is a privileged key; restrict access to the `production` environment and rotate after use if possible.
- `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`: Use test keys for `staging` runs. Ensure `STRIPE_WEBHOOK_SECRET` is set so the webhook verification passes.
- `SENDGRID_API_KEY` / `FROM_EMAIL`: If you don't want to send real emails during CI, create a staging SendGrid API key with suppressed delivery or use a sandbox account.

Checklist before running:

- Confirm `database/migrations/` contains only intentional schema changes.
- Ensure `python-tools/run_migrations.py --dry-run` succeeds against a staging DB.
- Have a rollback plan and confirm backup artifact presence after the workflow runs.

Recommended process:

1. Create a `staging` environment in the GitHub repository and add the corresponding staging secrets.
2. Trigger this workflow via **Actions → Run workflow** selecting `staging` and validate the artifacts and smoke tests.
3. If staging passes, run again targeting `production`. Configure the `production` environment to require at least one reviewer/approval.

Safety notes:

- Always ensure you have a valid DB backup (the workflow uploads the dump as an artifact).
- Review the migration SQL files under `database/migrations/` before approving production runs.
- This workflow intentionally does not automatically promote to production without a manual dispatch/approval.

If you'd like, I can open the PR with these files and a short description. After you add secrets, trigger the workflow manually and share any failures to debug.
