"""
Apply SQL migrations from `database/api-pricing-schema.sql` using DATABASE_URL (Postgres) if available.
Falls back to printing instructions for Supabase SQL editor.
"""
import os
import sys

SQL_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'api-pricing-schema.sql')
SQL_PATH = os.path.abspath(SQL_PATH)

DATABASE_URL = os.getenv('DATABASE_URL')


def apply_sql_via_psycopg2(sql_path: str, database_url: str):
    try:
        import psycopg2
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.close()
        print('Migrations applied via DATABASE_URL')
    except Exception as e:
        print('Failed to apply via psycopg2:', e)
        print('You can run the SQL manually in Supabase SQL editor at https://app.supabase.com/project/<your-id>/sql')


if __name__ == '__main__':
    if not os.path.exists(SQL_PATH):
        print('Cannot find SQL file at', SQL_PATH)
        sys.exit(1)

    if DATABASE_URL:
        apply_sql_via_psycopg2(SQL_PATH, DATABASE_URL)
    else:
        print('DATABASE_URL not set. To apply migrations, either set DATABASE_URL or paste the SQL into Supabase SQL editor:')
        with open(SQL_PATH, 'r', encoding='utf-8') as f:
            print(f.read())
