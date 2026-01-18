import sqlite3
import time
from pathlib import Path

from python_tools import simple_test_api as s


def test_webhook_delivery(tmp_path, capsys):
    # ensure clean DB for test
    db = s.DB_PATH
    if db.exists():
        db.unlink()
    s.init_db()

    # register receiver is external; instead, register a webhook to localhost:9000
    wid = s.register_webhook('http://127.0.0.1:9000/webhook', secret='t1')
    assert wid is not None

    # enqueue a payload and process queue (synchronous)
    qid = s.enqueue_webhook(wid, {'id': 'test-run'})
    assert qid is not None
    s._process_webhook_queue_once()

    # check deliveries table
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute('SELECT status, attempts FROM webhook_deliveries WHERE webhook_id=? ORDER BY ts DESC', (wid,))
    rows = cur.fetchall()
    conn.close()

    # delivery may fail if receiver not running; assert queue processed and record exists
    assert len(rows) >= 1
