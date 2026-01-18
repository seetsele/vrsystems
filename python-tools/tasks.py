from celery_app import app
import httpx
import os
import sqlite3
import json
from typing import Dict
from webhook_signing import sign_payload
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_results.db')


@app.task(bind=True, max_retries=5)
def deliver_webhook(self, webhook_id: str, run_payload: Dict):
    # Fetch webhook details from DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT url, secret FROM webhooks WHERE id=?', (webhook_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            raise ValueError('webhook not found')
        url, secret = row[0], (row[1] if len(row) > 1 else None)
    except Exception as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

    headers = {'Content-Type': 'application/json'}
    body = json.dumps(run_payload).encode('utf-8')
    # sign if secret present
    if secret:
        try:
            sig = sign_payload(secret, body)
            headers['X-Webhook-Signature'] = sig
        except Exception:
            pass

    try:
        r = httpx.post(url, content=body, headers=headers, timeout=10.0)
        r.raise_for_status()
        status_code = r.status_code
        text = r.text
        # write delivery record and remove from queue
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            did = os.urandom(8).hex()
            run_id = run_payload.get('id') if isinstance(run_payload, dict) else None
            cur.execute('INSERT INTO webhook_deliveries (id, webhook_id, run_id, status, attempts, last_error, ts) VALUES (?,?,?,?,?,?,?)', (did, webhook_id, run_id, 'delivered', 1, '', datetime.utcnow().isoformat()))
            cur.execute('DELETE FROM webhook_queue WHERE webhook_id=? AND payload=?', (webhook_id, json.dumps(run_payload)))
            conn.commit()
            conn.close()
        except Exception:
            pass
        return {'status_code': status_code, 'text': text}
    except Exception as exc:
        # On failure, update attempts and schedule retry
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            # find queue id
            cur.execute('SELECT id, attempts FROM webhook_queue WHERE webhook_id=? AND payload=?', (webhook_id, json.dumps(run_payload)))
            row = cur.fetchone()
            if row:
                qid, attempts = row[0], int(row[1] or 0)
                attempts += 1
                if attempts >= 5:
                    did = os.urandom(8).hex()
                    run_id = run_payload.get('id') if isinstance(run_payload, dict) else None
                    cur.execute('INSERT INTO webhook_deliveries (id, webhook_id, run_id, status, attempts, last_error, ts) VALUES (?,?,?,?,?,?,?)', (did, webhook_id, run_id, 'failed', attempts, str(exc), datetime.utcnow().isoformat()))
                    cur.execute('UPDATE webhook_queue SET status=?, attempts=?, last_error=? WHERE id=?', ('failed', attempts, str(exc), qid))
                else:
                    backoff = 2 ** attempts
                    next_ts = (datetime.utcnow() + timedelta(seconds=backoff)).isoformat()
                    cur.execute('UPDATE webhook_queue SET status=?, attempts=?, next_attempt_ts=?, last_error=? WHERE id=?', ('retry', attempts, next_ts, str(exc), qid))
                conn.commit()
            conn.close()
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
