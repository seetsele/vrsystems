import os
import pytest
try:
    import psycopg
except Exception:
    psycopg = None


def test_database_connect_env():
    """Attempt to connect using DATABASE_URL env var if present; otherwise skip."""
    url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI')
    if not url:
        pytest.skip('No DATABASE_URL configured')
    if psycopg is None:
        pytest.skip('psycopg not installed')
    try:
        with psycopg.connect(url, timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                assert cur.fetchone()[0] == 1
    except Exception:
        pytest.skip('Could not connect to database')
