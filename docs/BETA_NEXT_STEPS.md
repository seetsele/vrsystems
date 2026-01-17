Beta Launch - Next Steps
-------------------------

High priority checklist to prepare for beta:

- Configure SMTP: set `SENDGRID_API_KEY` or run MailHog and set `LOCAL_SMTP_HOST=localhost`.
- Add CI secrets per `docs/CI_SECRETS_INSTRUCTIONS.md`.
- Configure Sentry by setting `SENTRY_DSN` in secrets and enable sampling as needed.
- Add code-signing credentials to CI for builds (`APPLE_NOTARIZATION_KEY`, `WINDOWS_SIGNING_CERT`).
- Run comprehensive and robustness test suites locally and capture JSON results in `python-tools/`.
- Review `python-tools/regression_results.json` and apply prompt/provider tuning for failing claims.
- Run `scripts/security_audit.sh` and address critical findings.
- Configure database backups in CI using `scripts/db_backup.sh` template.
- Run `k6` with `scripts/k6_load_test.js` to validate load targets.

If you want, I can attempt to run local smoke tests and the comprehensive suite now; tell me and I'll start them (they require the API server and PWA running locally).
