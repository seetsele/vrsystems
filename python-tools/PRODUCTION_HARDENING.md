# Production Hardening Checklist

This document lists the recommended steps to prepare the Verity test-runner stack for production.

1. Secrets & KMS
   - Provision a managed KMS or Vault for provider/webhook secrets.
   - Remove any local Fernet key files; use environment-based KMS access with rotation.
   - Store `DATABASE_URL` and `SENTRY_DSN` in CI/CD secrets.

2. Database
   - Run Alembic migrations against a managed Postgres instance.
   - Enable automated backups and a migration test in CI that runs migrations on a temporary DB.

3. Background Workers
   - Run Celery workers behind process supervisor (systemd, k8s deployments).
   - Use Redis or RSMQ managed service; ensure persistence and failover.

4. Networking & TLS
   - Terminate TLS at a fronting load balancer (NGINX/ALB) or use Kubernetes Ingress with cert-manager.
   - Enforce `https` and HSTS; redirect HTTP to HTTPS.

5. Authentication & Rate-limiting
   - Protect management endpoints with API keys and IP allowlists.
   - Add rate-limiting for public endpoints to prevent abuse.

6. Webhook Security
   - Sign outgoing webhooks; include `X-Webhook-Signature` header.
   - Provide a webhook verification guide to integrators and rotate signing keys periodically.

7. Observability & SRE
   - Enable Sentry for error tracking; forward traces to APM.
   - Export Prometheus metrics and provision Grafana dashboards automatically.

8. CI/CD
   - Run tests, static analysis (CodeQL), and dependency updates (Dependabot) on PRs.
   - Run `alembic upgrade head` in a migration job with a dry-run migration test.

9. Compliance & Security
   - Add SAST and secrets scanning in CI (CodeQL, TruffleHog/GitHub secret scanning).
   - Regularly run dependency vulnerability scans and update pinned libs.

10. Disaster Recovery
    - Define RTO/RPO, backups for DB, and scripts to restore state.

Use this checklist as the basis for a staged rollout from internal beta → private customers → public launch.
