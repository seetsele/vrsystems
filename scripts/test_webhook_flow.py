#!/usr/bin/env python3
import importlib.util
import sqlite3
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / 'python-tools' / 'simple_test_api.py'

spec = importlib.util.spec_from_file_location('simple_test_api_mod', str(MOD_PATH))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.init_db()
DB = mod.DB_PATH

print('Registering webhook to http://127.0.0.1:9000/webhook with secret=secret1')
wid = mod.register_webhook('http://127.0.0.1:9000/webhook', secret='secret1')
print('webhook id', wid)

print('Enqueueing delivery (initial)')
qid = mod.enqueue_webhook(wid, {'id': 'initial-run'})
print('queue id', qid)

print('Processing queue')
mod._process_webhook_queue_once()
time.sleep(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute('SELECT id, webhook_id, status, attempts, last_error FROM webhook_deliveries ORDER BY ts DESC')
rows = cur.fetchall()
print('deliveries after first run:', rows[:5])

print('Rotating secret to secret2')
cur.execute('UPDATE webhooks SET secret=? WHERE id=?', ('secret2', wid))
conn.commit()

print('Enqueueing delivery (after rotation)')
qid2 = mod.enqueue_webhook(wid, {'id': 'rotated-run'})
print('queue id', qid2)
mod._process_webhook_queue_once()
time.sleep(1)
cur.execute('SELECT id, webhook_id, status, attempts, last_error FROM webhook_deliveries ORDER BY ts DESC')
rows2 = cur.fetchall()
print('deliveries after rotation:', rows2[:5])
conn.close()

print('Done')
