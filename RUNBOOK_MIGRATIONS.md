# RUNBOOK: Applying Database Migrations

Purpose
- Provide step-by-step safe procedure to apply SQL migrations to production/staging.

Pre-flight checks (required)
- Ensure a recent DB backup exists (pg_dump or managed backup). Create one if not.
- Verify `DATABASE_URL` points to the intended environment (staging vs production).
- Ensure repository branch with migrations is merged into main or target release branch.
- Ensure required secrets are present in CI: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SENDGRID_API_KEY`, `FROM_EMAIL`, `ADMIN_EMAIL`, `ADMIN_SLACK_WEBHOOK`.
- Confirm at least one reviewer (owner/admin) is available to approve if running in a protected environment.

Backup
- Use `pg_dump` for Postgres:
  - `pg_dump $DATABASE_URL -Fc -f backups/pre_migration_$(date +%Y%m%d_%H%M).dump`
- Upload or store backup in a secure location before proceeding.

Dry-run & validation (local or CI)
- Run migrations against a staging DB: `python-tools/run_migrations.py --database $STAGING_DATABASE_URL --dry-run`
- Run smoke tests: `cd python-tools && python local_smoke_tests.py`
- Run unit/integration tests: `cd python-tools && python -m pytest -q`

Apply migrations (CI recommended)
- Use the dispatchable GitHub Actions workflow `.github/workflows/migrations.yml`.
- From GitHub UI: open the workflow, choose the branch, set input variables, and run.
- The workflow will create a DB backup artifact, run migrations, and execute smoke tests. Review artifacts and logs.

Manual apply (only if CI not available)
- On a maintenance window, from a trusted machine with network access to DB:
  - `python-tools\run_migrations.py --database "$DATABASE_URL" --migrations-dir database/migrations`
  - Monitor output and errors closely.

Verification
- Confirm migration tables/columns exist: `psql $DATABASE_URL -c "\dt"` and `\d+ your_table`
- Run smoke tests and tests in `python-tools`.
- Check application logs for any errors for 30-60 minutes.

Rollback
- If migration fails and cannot be repaired, restore from backup:
  - `pg_restore -d $DATABASE_URL backups/pre_migration_YYYYMMDD_HHMM.dump`
- If migration added reversible DDL that has a safe downscript, use it only after careful analysis.

Post-migration
- Inform stakeholders and update release notes.
- Monitor metrics and error rates for at least one business cycle.

Troubleshooting
- If migrations fail due to locks, identify blocking PID in Postgres and assess risk before terminating.
- If schema drift is detected, run a differential check against a fresh replica and create a corrective migration.

Contact & approvals
- Primary owner: `ADMIN_EMAIL` (env var)
- Fallback: repo admins and on-call Slack webhook (`ADMIN_SLACK_WEBHOOK`)

References
- `python-tools/run_migrations.py`
- `.github/workflows/migrations.yml`

End of runbook.
