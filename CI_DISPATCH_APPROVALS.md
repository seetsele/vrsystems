# CI: Running the Migrations Workflow and Approval Flow

Purpose
- Explain how to safely dispatch the `.github/workflows/migrations.yml` workflow, review artifacts, and require approvals for production runs.

Run in staging (recommended)
1. In GitHub, go to `Actions` → `migrations` workflow → `Run workflow`.
2. Select the `ci/add-migrations-workflow` branch (or your branch) and set inputs if requested.
3. Choose the `staging` environment when asked for environment.
4. Click `Run workflow`.

What to review after run
- Confirm artifact `pre_migration_dump` exists and download it; verify size and timestamp.
- Check workflow logs for `python-tools/run_migrations.py` output and ensure there are no SQL errors.
- Inspect smoke test logs (`test_stripe_webhook_integration.py`) and uploaded test artifacts.

Promote to production (manual approval required)
- Configure the `production` environment under repository Settings → Environments and require at least one reviewer.
- Once staging pass is validated, re-run the workflow and select the `production` environment; a reviewer must approve the run before it proceeds.

Manual dispatch via API (optional)
- If you prefer to trigger via the GitHub API, create a short-lived PAT with `repo` and `workflow` scopes and run:

```
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  https://api.github.com/repos/<owner>/<repo>/actions/workflows/migrations.yml/dispatches \
  -d '{"ref":"ci/add-migrations-workflow","inputs":{}}'
```

Rollback & emergency stops
- If a migration fails, the workflow will stop. Use the backup artifact to restore with `pg_restore`.
- For long-running or blocking migrations, abort the workflow run from the Actions UI and restore from backup if needed.

Notes
- Never run this workflow against production without an explicit backup and an assigned reviewer.
- Use test keys for Stripe and SendGrid in non-production runs.

End.
