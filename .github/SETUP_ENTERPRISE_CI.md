# Setup Enterprise CI

To enable the enterprise test workflow, set the following repository secret in GitHub:

- `TEST_URL` — the base URL for the Verity deployment to test (e.g. `https://staging.example.com`).

Steps:
1. Go to your repository on GitHub > Settings > Secrets & variables > Actions > New repository secret.
2. Add `TEST_URL` with the value of the environment to test.
3. Optional: For scheduled runs ensure the repository is allowed to run scheduled workflows.

Triggering strict runs:
- Use the workflow_dispatch input `strict=true` to run the gated strict job which will set `STRICT_TESTS=1` and cause failures on any failing endpoint.

Artifacts:
- The workflow uploads `test-vault/`, the Playwright report directory, and a combined `artifacts-*.zip` containing those outputs.

Security note:
- Do not store sensitive credentials in `TEST_URL`. If additional secrets are needed (API keys), add them as repository secrets and reference them in the workflow.
