Title: FastAPI runner hardening and Postgres migration

Description:
This task covers moving the `test_runner` persistence from SQLite to Postgres, adding migrations, and hardening the FastAPI runner for production.

Checklist:
- [ ] Add Psycopg/SQLAlchemy DB layer and move `init_db()` logic to migrations
- [ ] Add Alembic and create initial migration for `runs`, `webhooks`, `providers`, `webhook_queue`, `webhook_deliveries`
- [ ] Replace SQLite connections with a connection pool and environment-driven DATABASE_URL
- [ ] Implement background workers (Celery/RQ) for webhook delivery and long-running jobs
- [ ] Add TLS guidance and optional OIDC/JWT authentication middleware
- [ ] Add integration tests for DB migrations and runner endpoints

Priority: High
