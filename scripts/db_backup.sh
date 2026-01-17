#!/usr/bin/env bash
# Minimal DB backup helper (Postgres via PGPASSWORD env)
set -euo pipefail

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_KEY:-}" ]; then
  echo "Set SUPABASE_URL and SUPABASE_SERVICE_KEY or DATABASE_URL before running." >&2
  exit 1
fi

OUT_DIR="backups"
mkdir -p "$OUT_DIR"
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$OUT_DIR/verity-db-backup-$TS.sql"

echo "Backing up database to $OUT (placeholder). Use pg_dump with DATABASE_URL in CI." 
echo "If you have DATABASE_URL, run: pg_dump $DATABASE_URL > $OUT"
#!/usr/bin/env bash
set -euo pipefail

echo "DB backup template for Supabase Postgres (requires `pg_dump` and env vars)."

if [ -z "${SUPABASE_DB_URL:-}" ]; then
  echo "Please export SUPABASE_DB_URL (postgres:// user:pass@host:port/db)"
  exit 1
fi

OUTDIR="backups"
mkdir -p "$OUTDIR"
FNAME="$OUTDIR/pg_backup_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "Running pg_dump to $FNAME (this will include data)."
# pg_dump "$SUPABASE_DB_URL" | gzip > "$FNAME"
echo "Template created; uncomment pg_dump and ensure credentials are correct before running."
