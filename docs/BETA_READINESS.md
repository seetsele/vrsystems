**Beta Readiness Checklist**

Current snapshot (2026-01-15): servers running locally; smoke/comprehensive/robust suites executed.

- **High priority (must before beta launch)**
  - Configure SMTP/email delivery for Supabase (remove admin-create fallback) — in progress
  - Add required CI secrets (`SUPABASE_SERVICE_KEY`, `STRIPE_*`, `VERCEL_TOKEN`, `GITHUB_TOKEN`) — in progress
  - Triage & fix failing tests (see `docs/BETA_TRIAGE.md`) — in progress

- **Medium priority**
  - Code-signing and notarization for desktop builds — in progress (instructions added)
  - End-to-end payment verification in staging — in progress
  - Observability (Sentry/metrics) — in progress

- **Lower priority / Release hygiene**
  - Release artifacts generation scripts — present
  - Security audit and dependency fixes — in progress (scripts added)
  - Backups & migrations — template scripts present
  - Data policy & legal updates — needs review

How we will measure beta readiness
- SMTP confirmed and user signup flows work without admin fallbacks
- CI passes on branch with full authenticated tests
- Desktop builds signed and installable on Windows/Mac
- Payment flows work end-to-end in staging
- Test accuracy >= 85% on comprehensive suite or product owner accepts risk

Next actions (pick one to start)
1. I implement SMTP via the `supabase` CLI template and test signups in staging (requires credentials).
2. I open PRs to fix the top 5 failed tests (I can start with `NH-003`, `NE-001`, `ENV-001`).
3. I add Sentry + metrics scaffolding to backend and desktop apps for beta telemetry.
