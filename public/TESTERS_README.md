# Verity Public Test Pages

Overview
- `api-tester.html` — interactive browser page to run ad-hoc API requests and quick checks (verify, batch, health, providers, waitlist, Stripe config/checkout, custom requests).
- `comprehensive-test-suite.html` — scripted sequence of checks that runs a staged suite of non-destructive tests and surfaces results and logs.

How to serve locally
1. From repository root run:

```powershell
python -m http.server 8000
# open http://127.0.0.1:8000/public/api-tester.html
```

Safety & guidance
- Always point the Base API URL to a staging environment, never to production, unless you explicitly intend to run production tests.
- The pages include buttons that may POST to endpoints such as `/stripe/create-checkout` and `/email/send-test`. Use Stripe test keys and sandbox email accounts when running those.
- Email sending is a best-effort attempt and will try multiple common endpoints (`/email/send-test`, `/email/send`, `/sendgrid/test-send`). If you prefer not to send emails, leave those fields blank or avoid the Send Test Email action.
- The test suite will attempt to join the waitlist as `ci-test@example.com` — change this in the UI before running if you want a different address.

Extending tests
- The pages are plain HTML+JS; feel free to add more endpoint buttons or steps. `comprehensive-test-suite.html` exposes `runAll()` which runs the scripted sequence.

Troubleshooting
- If CORS blocks requests, run the pages using a simple local static server (like `python -m http.server`) and ensure the API allows your origin or use `curl`/server-side runners.
- If endpoints are missing on your API, the UI shows the HTTP status and response body — inspect logs for details.

Contact
- For help, see `RUNBOOK_MIGRATIONS.md` and `DEPLOYMENT_NOTES_MIGRATIONS.md` in the repo, or contact `ADMIN_EMAIL` configured for your environment.
