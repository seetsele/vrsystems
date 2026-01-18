"""Lightweight psycopg shim for test environments.
Provides a minimal `connect` function with context manager that supports cursor(), execute(), fetchone().
This allows tests that import `psycopg` to run without a real Postgres server.
"""
from contextlib import contextmanager

class DummyCursor:
    def execute(self, query, *args, **kwargs):
        return None
    def fetchone(self):
        return (1,)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

class DummyConnection:
    def cursor(self):
        return DummyCursor()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

@contextmanager
def connect(dsn=None, timeout=None):
    yield DummyConnection()
