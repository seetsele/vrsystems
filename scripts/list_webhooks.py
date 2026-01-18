#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'python-tools' / 'test_results.db'
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute('SELECT id, url FROM webhooks')
rows = cur.fetchall()
if not rows:
    print('No webhooks found in', DB)
else:
    for r in rows:
        print(r[0], r[1])
conn.close()
