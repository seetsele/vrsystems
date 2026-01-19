#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'python-tools' / 'test_results.db'
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name="webhooks"')
if cur.fetchone()[0] == 0:
    print('webhooks table not present')
else:
    cur.execute('SELECT COUNT(*) FROM webhooks')
    print('webhook_count:', cur.fetchone()[0])
conn.close()
