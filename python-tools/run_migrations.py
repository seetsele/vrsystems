"""Run SQL migrations against a Postgres database.

Usage:
  Set `DATABASE_URL` env var (Postgres connection string) or `SUPABASE_DB_URL`.
  Then run: python run_migrations.py
"""
import os
import glob
import psycopg2
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent.parent / 'database' / 'migrations'

def get_database_url():
    return os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL') or os.getenv('SUPABASE_DB_CONN')

def apply_migration(conn, sql_text, filename):
    with conn.cursor() as cur:
        cur.execute(sql_text)
    conn.commit()
    print(f"Applied: {filename}")

def main():
    db_url = get_database_url()
    if not db_url:
        print('DATABASE_URL or SUPABASE_DB_URL not set. Aborting.')
        return 1

    files = sorted(glob.glob(str(MIGRATIONS_DIR / '*.sql')))
    if not files:
        print('No migration files found in', MIGRATIONS_DIR)
        return 0

    conn = psycopg2.connect(db_url)
    try:
        for f in files:
            sql_text = Path(f).read_text(encoding='utf-8')
            apply_migration(conn, sql_text, Path(f).name)
    finally:
        conn.close()

if __name__ == '__main__':
    raise SystemExit(main())
