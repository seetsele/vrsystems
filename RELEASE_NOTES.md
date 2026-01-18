# Release Notes — Candidate for launch

2026-01-18 — Local endpoints, CI, and hardening

- Implemented feature-complete local endpoints for testing and launch readiness:
  - `POST /api/moderate` — deterministic local moderation with input validation
  - `GET /api/analyze-image/health` — image-analysis health and Pillow check
  - `GET /auth/login` — local OAuth redirect simulation for integration tests
  - `GET /api/stats` — SQLite-backed stats summary
  - `GET/POST /api/waitlist` — SQLite-backed waitlist with input validation

- Added security and stability improvements:
  - API key enforcement via `X-API-Key` or `Authorization: Bearer <key>` (configurable)
  - Simple sliding-window rate limiter for critical endpoints
  - Input validation using Pydantic models

- CI & Dev Ops:
  - GitHub Actions workflow `ci-postgres.yml` to run tests against Postgres
  - `docker-compose.postgres.yml` for local Postgres integration
  - SQL migration `python-tools/migrations/001_create_waitlist_and_stats.sql`

Notes:
- The local features are suitable for initial launch and CI; for production we recommend replacing SQLite with a managed Postgres instance and enabling full provider integrations.
