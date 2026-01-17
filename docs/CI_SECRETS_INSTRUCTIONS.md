CI Secrets & GitHub Actions
--------------------------------

Add these secrets to the repository Settings → Secrets for full CI and release workflows:

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service_role key (for admin operations in tests)
- `SENDGRID_API_KEY` or `LOCAL_SMTP_HOST`/`LOCAL_SMTP_PORT` for email tests
- `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` for payment flows
- `SENTRY_DSN` for Sentry error reporting
- `VERCEL_TOKEN` / `VERCEL_PROJECT_ID` for Vercel deployments
- `GITHUB_TOKEN` - already provided by Actions, but use `PERSONAL_ACCESS_TOKEN` for some releases
- `APPLE_NOTARIZATION_KEY` / `APPLE_TEAM_ID` for macOS notarization (store secrets securely)

Notes:
- Never commit service keys to source. Use Actions secrets and environment variables.
- For local development, use a `.env` file kept out of version control and populated from a secure vault.
# CI Secrets and Environment Setup

Required repository secrets for CI and beta runs:

- `SUPABASE_SERVICE_KEY` (service_role key) — used by tests to create confirmed test users.
- `SUPABASE_URL` — project URL.
- `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` — for payment integration testing.
- `VERCEL_TOKEN` — to trigger Vercel deployments (if used by release workflow).
- `GITHUB_TOKEN` — already available in Actions, but a personal token may be needed for release scripts.

How to add (GitHub): Repository → Settings → Secrets → Actions → New repository secret

Security notes
- Never store production service_role keys in public repos. Use environment-specific keys.
- Rotate keys after onboarding CI and store them in a secrets manager when possible.
