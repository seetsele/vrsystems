#!/usr/bin/env python3
import json
import tempfile
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path
import xml.etree.ElementTree as ET
import time
import threading
import re
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
import base64
import math

# Simple persistent store for test run results
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'python-tools' / 'test_results.db'
SSE_CLIENTS = []
SSE_LOCK = threading.Lock()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        ts TEXT,
        cmd TEXT,
        exit_code INTEGER,
        parsed_json TEXT,
        stdout TEXT,
        stderr TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS webhooks (
        id TEXT PRIMARY KEY,
        url TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS webhook_queue (
        id TEXT PRIMARY KEY,
        webhook_id TEXT,
        payload TEXT,
        attempts INTEGER,
        next_attempt_ts TEXT,
        status TEXT,
        last_error TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS webhook_deliveries (
        id TEXT PRIMARY KEY,
        webhook_id TEXT,
        run_id TEXT,
        status TEXT,
        attempts INTEGER,
        last_error TEXT,
        ts TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS providers (
        id TEXT PRIMARY KEY,
        name TEXT,
        secret TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        ts TEXT,
        actor TEXT,
        action TEXT,
        details TEXT
    )''')
    conn.commit()
    conn.close()


def save_run(cmd, exit_code, parsed, stdout, stderr):
    rid = str(uuid.uuid4())
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('INSERT INTO runs (id, ts, cmd, exit_code, parsed_json, stdout, stderr) VALUES (?,?,?,?,?,?,?)', (
        rid, datetime.utcnow().isoformat(), json.dumps(cmd), int(exit_code), json.dumps(parsed or {}), stdout or '', stderr or ''
    ))
    conn.commit()
    conn.close()
    # notify SSE clients
    payload = {'id': rid, 'ts': datetime.utcnow().isoformat(), 'exit_code': exit_code, 'parsed': parsed}
    notify_sse_clients('run', payload)
    # dispatch webhooks (fire-and-forget)
    threading.Thread(target=dispatch_webhooks, args=(payload,)).start()
    return rid


def list_runs(limit=50):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT id, ts, cmd, exit_code, parsed_json FROM runs ORDER BY ts DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({'id': r[0], 'ts': r[1], 'cmd': json.loads(r[2]) if r[2] else None, 'exit_code': r[3], 'parsed': json.loads(r[4]) if r[4] else {}})
    return out


def get_run(rid):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT id, ts, cmd, exit_code, parsed_json, stdout, stderr FROM runs WHERE id=?', (rid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {'id': row[0], 'ts': row[1], 'cmd': json.loads(row[2]) if row[2] else None, 'exit_code': row[3], 'parsed': json.loads(row[4]) if row[4] else {}, 'stdout': row[5], 'stderr': row[6]}


def register_webhook(url, secret=None):
    # optional secret support: add column if not present
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        try:
            cur.execute('ALTER TABLE webhooks ADD COLUMN secret TEXT')
        except Exception:
            pass
        wid = str(uuid.uuid4())
        try:
            if secret is not None:
                cur.execute('INSERT INTO webhooks (id, url, secret, created_at) VALUES (?,?,?,?)', (wid, url, secret, datetime.utcnow().isoformat()))
            else:
                cur.execute('INSERT INTO webhooks (id, url, created_at) VALUES (?,?,?)', (wid, url, datetime.utcnow().isoformat()))
        except Exception:
            # fallback to insert without secret
            cur.execute('INSERT INTO webhooks (id, url, created_at) VALUES (?,?,?)', (wid, url, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        try:
            audit_event('system', 'register_webhook', json.dumps({'id': wid, 'url': url}))
        except Exception:
            pass
        return wid
    except Exception:
        return None


### Provider secure storage helpers
KMS_KEY_PATH = DB_PATH.parent / 'runner_kms.key'

def _load_kms_key():
    # Prefer env var, else persisted key file, else generate and persist
    key = os.environ.get('TEST_RUNNER_KMS_KEY')
    if key:
        return key.encode('utf-8') if isinstance(key, str) else key
    try:
        if KMS_KEY_PATH.exists():
            return KMS_KEY_PATH.read_bytes()
    except Exception:
        pass
    # try to use cryptography Fernet key
    try:
        from cryptography.fernet import Fernet
        k = Fernet.generate_key()
        try:
            KMS_KEY_PATH.write_bytes(k)
        except Exception:
            pass
        return k
    except Exception:
        # fallback to a simple random key (not cryptographically strong)
        k = uuid.uuid4().hex.encode('utf-8')
        try:
            KMS_KEY_PATH.write_bytes(k)
        except Exception:
            pass
        return k


def encrypt_secret(plaintext: str):
    if plaintext is None:
        return ''
    try:
        from cryptography.fernet import Fernet
        k = _load_kms_key()
        f = Fernet(k)
        return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')
    except Exception:
        # simple XOR-ish fallback using key bytes
        k = _load_kms_key()
        kb = k if isinstance(k, (bytes, bytearray)) else str(k).encode('utf-8')
        pb = plaintext.encode('utf-8')
        out = bytearray()
        for i, b in enumerate(pb):
            out.append(b ^ kb[i % len(kb)])
        return out.hex()


def decrypt_secret(ciphertext: str):
    if not ciphertext:
        return ''
    try:
        from cryptography.fernet import Fernet
        k = _load_kms_key()
        f = Fernet(k)
        return f.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
    except Exception:
        try:
            k = _load_kms_key()
            kb = k if isinstance(k, (bytes, bytearray)) else str(k).encode('utf-8')
            data = bytes.fromhex(ciphertext)
            out = bytearray()
            for i, b in enumerate(data):
                out.append(b ^ kb[i % len(kb)])
            return out.decode('utf-8')
        except Exception:
            return ''


def create_provider(name, secret):
    pid = str(uuid.uuid4())
    enc = encrypt_secret(secret)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('INSERT INTO providers (id, name, secret, created_at) VALUES (?,?,?,?)', (pid, name, enc, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    try:
        audit_event('system', 'create_provider', json.dumps({'id': pid, 'name': name}))
    except Exception:
        pass
    return pid


def list_providers():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT id, name, created_at FROM providers ORDER BY created_at DESC')
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'created_at': r[2]} for r in rows]


def get_provider_secret(pid):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT secret FROM providers WHERE id=?', (pid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        secret = decrypt_secret(row[0])
        audit_event('system', 'get_provider_secret', json.dumps({'id': pid}))
        return secret
    except Exception:
        return decrypt_secret(row[0])


def list_webhooks():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT id, url, secret, created_at FROM webhooks ORDER BY created_at DESC')
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({'id': r[0], 'url': r[1], 'has_secret': bool(r[2]), 'created_at': r[3]})
    return out


def get_analytics(limit_days=30):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('SELECT parsed_json, ts FROM runs ORDER BY ts DESC')
    rows = cur.fetchall()
    conn.close()

    total_runs = len(rows)
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_time = 0.0
    time_count = 0
    runs_per_day = {}

    for parsed_json, ts in rows:
        try:
            pj = json.loads(parsed_json) if parsed_json else {}
        except Exception:
            pj = {}
        summary = pj.get('summary', {}) if isinstance(pj, dict) else {}
        try:
            total_passed += int(summary.get('passed', 0) or 0)
            total_failed += int(summary.get('failed', 0) or 0)
            total_skipped += int(summary.get('skipped', 0) or 0)
        except Exception:
            pass
        try:
            t = float(summary.get('time', 0.0) or 0.0)
            if t:
                total_time += t
                time_count += 1
        except Exception:
            pass
        try:
            day = ts.split('T', 1)[0]
            runs_per_day[day] = runs_per_day.get(day, 0) + 1
        except Exception:
            pass

    avg_time = (total_time / time_count) if time_count else 0.0

    # Reduce runs_per_day to last `limit_days` keys if possible
    try:
        days = sorted(runs_per_day.keys(), reverse=True)[:limit_days]
        runs_by_day = {d: runs_per_day.get(d, 0) for d in sorted(days)}
    except Exception:
        runs_by_day = runs_per_day

    return {
        'total_runs': total_runs,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'total_skipped': total_skipped,
        'avg_time_seconds': avg_time,
        'runs_by_day': runs_by_day,
    }


def audit_event(actor, action, details=''):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        aid = str(uuid.uuid4())
        cur.execute('INSERT INTO audit_log (id, ts, actor, action, details) VALUES (?,?,?,?,?)', (aid, datetime.utcnow().isoformat(), actor, action, details))
        conn.commit()
        conn.close()
    except Exception:
        pass


def list_audit(limit=200):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute('SELECT id, ts, actor, action, details FROM audit_log ORDER BY ts DESC LIMIT ?', (limit,))
        rows = cur.fetchall()
        conn.close()
        return [{'id': r[0], 'ts': r[1], 'actor': r[2], 'action': r[3], 'details': r[4]} for r in rows]
    except Exception:
        return []


def dispatch_webhooks(payload):
    # enqueue payloads for reliable delivery
    try:
        hooks = list_webhooks()
        for h in hooks:
            try:
                enqueue_webhook(h['id'], payload)
            except Exception:
                pass
    except Exception:
        pass


def enqueue_webhook(webhook_id, payload):
    # insert into webhook_queue with initial attempt 0
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        qid = str(uuid.uuid4())
        cur.execute('INSERT INTO webhook_queue (id, webhook_id, payload, attempts, next_attempt_ts, status, last_error, created_at) VALUES (?,?,?,?,?,?,?,?)', (
            qid, webhook_id, json.dumps(payload), 0, datetime.utcnow().isoformat(), 'queued', '', datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        # enqueue background Celery delivery task (best-effort; local worker required)
        try:
            from tasks import deliver_webhook
            deliver_webhook.delay(webhook_id, payload)
        except Exception:
            pass
        return qid
    except Exception:
        return None


def _deliver_webhook_record(rec):
    # rec: (id, webhook_id, payload, attempts, next_attempt_ts, status, last_error, created_at)
    try:
        wid = rec[1]
        payload = json.loads(rec[2]) if rec[2] else {}
    except Exception:
        payload = {}
        wid = rec[1]
    # get webhook url
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute('SELECT url FROM webhooks WHERE id=?', (wid,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return False, 'no webhook url'
        url = row[0]
    except Exception as e:
        return False, str(e)

    try:
        import requests
        # attempt to fetch secret column if present
        secret = None
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cur = conn.cursor()
            cur.execute('PRAGMA table_info(webhooks)')
            cols = [r[1] for r in cur.fetchall()]
            conn.close()
            if 'secret' in cols:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute('SELECT secret FROM webhooks WHERE id=?', (wid,))
                row = cur.fetchone()
                conn.close()
                if row:
                    secret = row[0]
        except Exception:
            secret = None

        headers = {'Content-Type': 'application/json'}
        body = json.dumps(payload).encode('utf-8')
        if secret:
            try:
                from webhook_signing import sign_payload
                headers['X-Webhook-Signature'] = sign_payload(secret, body)
            except Exception:
                pass

        r = requests.post(url, data=body, headers=headers, timeout=5)
        if 200 <= r.status_code < 300:
            return True, ''
        return False, f'status:{r.status_code}'
    except Exception as e:
        return False, str(e)


def _process_webhook_queue_once():
    # pick next queued item whose next_attempt_ts <= now
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute("SELECT id, webhook_id, payload, attempts, next_attempt_ts, status, last_error, created_at FROM webhook_queue WHERE status IN ('queued','retry') ORDER BY created_at ASC LIMIT 5")
        rows = cur.fetchall()
        for row in rows:
            qid = row[0]
            attempts = int(row[3] or 0)
            ok, err = _deliver_webhook_record(row)
            attempts += 1
            if ok:
                # mark delivery record
                try:
                    payload_obj = json.loads(row[2]) if row[2] else {}
                except Exception:
                    payload_obj = {}
                run_id = payload_obj.get('id') if isinstance(payload_obj, dict) else None
                did = str(uuid.uuid4())
                cur.execute('INSERT INTO webhook_deliveries (id, webhook_id, run_id, status, attempts, last_error, ts) VALUES (?,?,?,?,?,?,?)', (did, row[1], run_id, 'delivered', attempts, err, datetime.utcnow().isoformat()))
                cur.execute('DELETE FROM webhook_queue WHERE id=?', (qid,))
            else:
                # schedule retry with exponential backoff
                if attempts >= 5:
                    cur.execute('UPDATE webhook_queue SET status=?, attempts=?, last_error=? WHERE id=?', ('failed', attempts, str(err), qid))
                    try:
                        payload_obj = json.loads(row[2]) if row[2] else {}
                    except Exception:
                        payload_obj = {}
                    run_id = payload_obj.get('id') if isinstance(payload_obj, dict) else None
                    did = str(uuid.uuid4())
                    cur.execute('INSERT INTO webhook_deliveries (id, webhook_id, run_id, status, attempts, last_error, ts) VALUES (?,?,?,?,?,?,?)', (did, row[1], run_id, 'failed', attempts, str(err), datetime.utcnow().isoformat()))
                else:
                    # backoff seconds = 2 ** attempts
                    backoff = 2 ** attempts
                    next_ts = (datetime.utcnow() + timedelta(seconds=backoff)).isoformat()
                    cur.execute('UPDATE webhook_queue SET status=?, attempts=?, next_attempt_ts=?, last_error=? WHERE id=?', ('retry', attempts, next_ts, str(err), qid))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _webhook_worker_loop():
    while True:
        try:
            _process_webhook_queue_once()
        except Exception:
            pass
        time.sleep(2)


def notify_sse_clients(event, payload):
    data = json.dumps({'event': event, 'payload': payload})
    with SSE_LOCK:
        clients = list(SSE_CLIENTS)
    for w in clients:
        try:
            w.write(f"event: {event}\n")
            w.write(f"data: {json.dumps(payload)}\n\n")
            try:
                w.flush()
            except Exception:
                pass
        except Exception:
            with SSE_LOCK:
                try:
                    SSE_CLIENTS.remove(w)
                except Exception:
                    pass

ROOT = Path(__file__).resolve().parents[1]


def parse_junit(xml_path: Path):
    if not xml_path.exists():
        return {}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    summary = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'time': float(root.attrib.get('time', 0.0))}
    tests = []
    for tc in root.iter('testcase'):
        summary['total'] += 1
        name = tc.attrib.get('name')
        classname = tc.attrib.get('classname')
        time = float(tc.attrib.get('time', 0.0))
        outcome = 'passed'
        message = ''
        for child in tc:
            if child.tag in ('failure', 'error'):
                outcome = 'failed'
                message = child.text or ''
            elif child.tag == 'skipped':
                outcome = 'skipped'
                message = child.attrib.get('message', '') or (child.text or '')
        if outcome == 'passed':
            summary['passed'] += 1
        elif outcome == 'failed':
            summary['failed'] += 1
        elif outcome == 'skipped':
            summary['skipped'] += 1
        tests.append({'name': name, 'classname': classname, 'time': time, 'outcome': outcome, 'message': message})
    return {'summary': summary, 'tests': tests}


# Redaction helpers
def load_redaction_patterns():
    pfile = ROOT / 'python-tools' / 'redaction_patterns.json'
    default = {
        'patterns': [
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",
            r"(?i)token=\w+",
            r"[A-Fa-f0-9]{32,}",
            r"[A-Za-z0-9_-]{40,}",
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        ]
    }
    try:
        if pfile.exists():
            pj = json.loads(pfile.read_text(encoding='utf-8'))
            return pj.get('patterns', default['patterns'])
    except Exception:
        pass
    return default['patterns']


def is_base64(s: str):
    # quick check for base64-looking strings
    try:
        if len(s) < 20:
            return False
        b = s.encode('utf-8')
        return base64.b64encode(base64.b64decode(b)).decode('utf-8') == s
    except Exception:
        return False


def entropy(s: str):
    if not s:
        return 0.0
    # Shannon entropy
    probs = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log(p, 2) for p in probs)


def mask_value(val: str):
    if val is None:
        return val
    if isinstance(val, (int, float)):
        return val
    s = str(val)
    # short values: mask fully
    if len(s) <= 6:
        return '[REDACTED]'
    # long tokens or high entropy
    if len(s) > 20 and (entropy(s) > 3.5 or is_base64(s)):
        return '[REDACTED_TOKEN]'
    # emails
    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", s):
        return re.sub(r"([a-zA-Z0-9._%+-]+)@", r"\1@REDACTED.", s)
    # fallback partial mask
    return s[:4] + '…' + s[-4:]


def redact_json_object(obj, key_patterns=None):
    # mask known secret keys
    secret_keys = ['password', 'secret', 'api_key', 'apikey', 'token', 'access_token', 'refresh_token', 'authorization', 'auth']
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = k.lower()
            if any(sk in lk for sk in secret_keys) or (key_patterns and any(re.search(p, k, flags=re.I) for p in key_patterns)):
                out[k] = mask_value(v if isinstance(v, str) else json.dumps(v))
            else:
                out[k] = redact_json_object(v, key_patterns)
        return out
    elif isinstance(obj, list):
        return [redact_json_object(i, key_patterns) for i in obj]
    else:
        return obj


def redact_text_advanced(s, patterns=None):
    if not s:
        return s
    patterns = patterns or []
    # try to parse as JSON and redact keys
    try:
        j = json.loads(s)
        try:
            rj = redact_json_object(j, key_patterns=patterns)
            return json.dumps(rj)
        except Exception:
            pass
    except Exception:
        pass
    txt = s
    # apply regex patterns
    try:
        for pat in patterns:
            try:
                txt = re.sub(pat, '[REDACTED]', txt, flags=re.I)
            except Exception:
                try:
                    txt = re.sub(pat, '[REDACTED]', txt)
                except Exception:
                    pass
    except Exception:
        pass

    # mask long hex/base64 tokens and uuids
    txt = re.sub(r"[A-Fa-f0-9]{32,}", '[REDACTED_TOKEN]', txt)
    txt = re.sub(r"[A-Za-z0-9_-]{40,}", '[REDACTED_TOKEN]', txt)
    txt = re.sub(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", '[REDACTED_UUID]', txt)
    # emails
    txt = re.sub(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1@REDACTED.\2", txt)
    return txt


class Handler(BaseHTTPRequestHandler):
    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-KEY')
        self.end_headers()

    def _check_api_key(self):
        """Return True if request is authorized or no API key is configured."""
        required = None
        try:
            required = (os.environ.get('TEST_RUNNER_API_KEY') or '').strip()
        except Exception:
            required = ''
        if not required:
            return True
        # check header first
        key = self.headers.get('X-API-KEY')
        if key and key == required:
            return True
        # allow query param for SSE clients
        qs = ''
        if '?' in self.path:
            try:
                qs = self.path.split('?',1)[1]
            except Exception:
                qs = ''
        if qs:
            for part in qs.split('&'):
                if part.startswith('key=') and part.split('=',1)[1] == required:
                    return True
        return False

    def do_POST(self):
        # support multiple POST endpoints: /run-tests and /purge-logs
        if not self.path.startswith('/run-tests') and not self.path.startswith('/purge-logs'):
            self._set_json(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode())
            return

        # require API key if configured
        if not self._check_api_key():
            self._set_json(401)
            self.wfile.write(json.dumps({'error': 'unauthorized'}).encode())
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        try:
            req = json.loads(body)
        except Exception:
            req = {}

        # if purge request, delete log file
        if self.path.startswith('/purge-logs'):
            logs_dir = ROOT / 'python-tools' / 'logs'
            log_file = logs_dir / 'test_runner.log'
            try:
                if log_file.exists():
                    log_file.unlink()
                self._set_json(200)
                self.wfile.write(json.dumps({'status': 'purged'}).encode())
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return

        # register webhook
        if self.path.startswith('/register-webhook'):
            url = req.get('url') if isinstance(req, dict) else None
            secret = req.get('secret') if isinstance(req, dict) else None
            if not url:
                self._set_json(400)
                self.wfile.write(json.dumps({'error': 'missing url'}).encode())
                return
            wid = register_webhook(url, secret)
            self._set_json(200)
            self.wfile.write(json.dumps({'id': wid}).encode())
            return

        # create provider
        if self.path.startswith('/providers'):
            name = req.get('name') if isinstance(req, dict) else None
            secret = req.get('secret') if isinstance(req, dict) else None
            if not name:
                self._set_json(400)
                self.wfile.write(json.dumps({'error': 'missing name'}).encode())
                return
            pid = create_provider(name, secret or '')
            self._set_json(200)
            self.wfile.write(json.dumps({'id': pid}).encode())
            return
        # update redaction patterns
        if self.path.startswith('/redaction-patterns'):
            # accept JSON body { patterns: [...] }
            pats = req.get('patterns') if isinstance(req, dict) else None
            if not isinstance(pats, list):
                self._set_json(400)
                self.wfile.write(json.dumps({'error': 'missing patterns list'}).encode())
                return
            try:
                pfile = ROOT / 'python-tools' / 'redaction_patterns.json'
                pfile.parent.mkdir(parents=True, exist_ok=True)
                pfile.write_text(json.dumps({'patterns': pats}, indent=2), encoding='utf-8')
                self._set_json(200)
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return

        target = req.get('target', 'tests')
        items = req.get('items') or ( [req.get('item')] if req.get('item') else None )
        marker = req.get('marker')
        redact = bool(req.get('redact', True))

        extra_flags = []
        args = []
        if items:
            args = items
        elif marker:
            extra_flags = ['-m', marker]
            args = ['.'] if target == 'all' else [target]
        else:
            args = ['.'] if target == 'all' else ([ 'python-tools/tests' ] if target=='python-tools' else [target])

        # run pytest and capture outputs, also write logs to python-tools/logs/test_runner.log
        logs_dir = ROOT / 'python-tools' / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / 'test_runner.log'
        with tempfile.TemporaryDirectory() as td:
            junit = Path(td) / 'results.xml'
            cmd = ['python', '-m', 'pytest', '-q', '--junitxml', str(junit)] + extra_flags + args
            try:
                proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
            except subprocess.TimeoutExpired:
                self._set_json(504)
                self.wfile.write(json.dumps({'error': 'timeout'}).encode())
                return

            # advanced redaction using patterns plus JSON/key-aware masking
            REDACT_PATTERNS = load_redaction_patterns()

            out_stdout = proc.stdout or ''
            out_stderr = proc.stderr or ''
            if redact:
                out_stdout = redact_text_advanced(out_stdout, REDACT_PATTERNS)
                out_stderr = redact_text_advanced(out_stderr, REDACT_PATTERNS)

            # append to log file
            try:
                with log_file.open('a', encoding='utf-8') as lf:
                    lf.write('\n--- RUN START ---\n')
                    lf.write('cmd: ' + ' '.join(cmd) + '\n')
                    lf.write(out_stdout)
                    lf.write('\nSTDERR:\n')
                    lf.write(out_stderr)
                    lf.write('\n--- RUN END ---\n')
            except Exception:
                pass

            parsed = parse_junit(junit)
            if redact and parsed and isinstance(parsed.get('tests'), list):
                for t in parsed['tests']:
                    if 'message' in t and t['message']:
                        t['message'] = redact_text_advanced(t['message'], REDACT_PATTERNS)

            # persist run to DB and notify SSE clients
            try:
                init_db()
            except Exception:
                pass
            rid = save_run(cmd, proc.returncode, parsed, out_stdout, out_stderr)

            resp = {'id': rid, 'exit_code': proc.returncode, 'stdout': out_stdout, 'stderr': out_stderr, 'parsed': parsed, 'cmd': cmd}
            self._set_json(200)
            self.wfile.write(json.dumps(resp).encode())

    def do_GET(self):
        # expose a simple logs endpoint for the browser runner to poll
        if self.path.startswith('/logs'):
            logs_dir = ROOT / 'python-tools' / 'logs'
            log_file = logs_dir / 'test_runner.log'
            if not log_file.exists():
                self._set_json(200)
                self.wfile.write(json.dumps({'log': ''}).encode())
                return
            try:
                txt = log_file.read_text(encoding='utf-8')
            except Exception:
                txt = ''
            self._set_json(200)
            self.wfile.write(json.dumps({'log': txt}).encode())
            return
        # streaming logs via Server-Sent Events
        if self.path.startswith('/stream-logs'):
            # register this connection as SSE client for structured events
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with SSE_LOCK:
                SSE_CLIENTS.append(self.wfile)
            try:
                while True:
                    time.sleep(0.5)
                    # keep connection alive
                    try:
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
                    except Exception:
                        break
            finally:
                with SSE_LOCK:
                    try:
                        SSE_CLIENTS.remove(self.wfile)
                    except Exception:
                        pass
            return
        # analytics summary
        if self.path.startswith('/analytics'):
            try:
                data = get_analytics()
                self._set_json(200)
                self.wfile.write(json.dumps(data).encode())
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return
        # return redaction patterns
        if self.path.startswith('/redaction-patterns'):
            try:
                pats = load_redaction_patterns()
                self._set_json(200)
                self.wfile.write(json.dumps({'patterns': pats}).encode())
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return
        # provider secret retrieval (requires API key)
        if self.path.startswith('/provider-secret'):
            # require API key for secret retrieval
            if not self._check_api_key():
                self._set_json(401)
                self.wfile.write(json.dumps({'error': 'unauthorized'}).encode())
                return
            qs = ''
            if '?' in self.path:
                qs = self.path.split('?',1)[1]
            params = {}
            for p in qs.split('&') if qs else []:
                if '=' in p:
                    k,v = p.split('=',1); params[k]=v
            pid = params.get('id')
            if not pid:
                self._set_json(400)
                self.wfile.write(json.dumps({'error':'missing id'}).encode())
                return
            sec = get_provider_secret(pid)
            if sec is None:
                self._set_json(404)
                self.wfile.write(json.dumps({'error':'not found'}).encode())
                return
            self._set_json(200)
            self.wfile.write(json.dumps({'secret': sec}).encode())
            return
        # audit log listing (requires API key)
        if self.path.startswith('/audit'):
            if not self._check_api_key():
                self._set_json(401)
                self.wfile.write(json.dumps({'error': 'unauthorized'}).encode())
                return
            lst = list_audit()
            self._set_json(200)
            self.wfile.write(json.dumps({'audit': lst}).encode())
            return
        # rotate provider secret (requires API key)
        if self.path.startswith('/providers/rotate'):
            if not self._check_api_key():
                self._set_json(401)
                self.wfile.write(json.dumps({'error': 'unauthorized'}).encode())
                return
            secret_id = req.get('id') if isinstance(req, dict) else None
            new_secret = req.get('secret') if isinstance(req, dict) else None
            if not secret_id or new_secret is None:
                self._set_json(400)
                self.wfile.write(json.dumps({'error': 'missing id or secret'}).encode())
                return
            try:
                # update DB encrypted secret
                enc = encrypt_secret(new_secret)
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute('UPDATE providers SET secret=? WHERE id=?', (enc, secret_id))
                conn.commit()
                conn.close()
                audit_event('system', 'rotate_provider_secret', json.dumps({'id': secret_id}))
                self._set_json(200)
                self.wfile.write(json.dumps({'status': 'rotated'}).encode())
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        # verify webhook signature (debug/test endpoint)
        if self.path.startswith('/verify-signature'):
            # body should contain { url, payload, signature }
            url = req.get('url') if isinstance(req, dict) else None
            payload = req.get('payload') if isinstance(req, dict) else None
            signature = req.get('signature') if isinstance(req, dict) else None
            if not url or payload is None or not signature:
                self._set_json(400)
                self.wfile.write(json.dumps({'error': 'missing url/payload/signature'}).encode())
                return
            # find webhook by url
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute('SELECT id, secret FROM webhooks WHERE url=?', (url,))
                row = cur.fetchone()
                conn.close()
                if not row:
                    self._set_json(404)
                    self.wfile.write(json.dumps({'error': 'webhook not found'}).encode())
                    return
                secret = row[1]
                from webhook_signing import verify_signature
                ok = False
                try:
                    ok = verify_signature(secret or '', json.dumps(payload).encode('utf-8'), signature)
                except Exception:
                    ok = False
                self._set_json(200)
                self.wfile.write(json.dumps({'ok': bool(ok)}).encode())
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        # results listing
        if self.path.startswith('/results'):
            # optionally allow /results?id=<id>
            qs = ''
            if '?' in self.path:
                qs = self.path.split('?',1)[1]
            params = {}
            for p in qs.split('&') if qs else []:
                if '=' in p:
                    k,v = p.split('=',1); params[k]=v
            if 'id' in params:
                r = get_run(params['id'])
                if not r:
                    self._set_json(404)
                    self.wfile.write(json.dumps({'error':'not found'}).encode())
                    return
                self._set_json(200)
                self.wfile.write(json.dumps(r).encode())
                return
            lst = list_runs(limit=200)
            self._set_json(200)
            self.wfile.write(json.dumps({'runs': lst}).encode())
            return
        # list webhooks
        if self.path.startswith('/webhooks'):
            hooks = list_webhooks()
            self._set_json(200)
            self.wfile.write(json.dumps({'webhooks': hooks}).encode())
            return
        # metrics
        if self.path.startswith('/metrics'):
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute('SELECT COUNT(1) FROM runs')
                total_runs = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM runs WHERE exit_code!=0')
                failed_runs = cur.fetchone()[0]
                cur.execute("SELECT COUNT(1) FROM webhook_queue WHERE status IN ('queued', 'retry')")
                queued = cur.fetchone()[0]
                conn.close()
                self._set_json(200)
                self.wfile.write(json.dumps({'total_runs': total_runs, 'failed_runs': failed_runs, 'webhook_queue': queued}).encode())
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return
        # Prometheus exposition endpoint
        if self.path.startswith('/prometheus'):
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute('SELECT COUNT(1) FROM runs')
                total_runs = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM runs WHERE exit_code!=0')
                failed_runs = cur.fetchone()[0]
                cur.execute("SELECT COUNT(1) FROM webhook_queue WHERE status IN ('queued','retry')")
                queued = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM webhook_deliveries WHERE status=\'failed\'')
                failed_deliveries = cur.fetchone()[0]
                cur.execute('SELECT COUNT(1) FROM providers')
                providers = cur.fetchone()[0]
                conn.close()
                lines = []
                lines.append('# TYPE verity_total_runs counter')
                lines.append(f'verity_total_runs {int(total_runs)}')
                lines.append('# TYPE verity_failed_runs counter')
                lines.append(f'verity_failed_runs {int(failed_runs)}')
                lines.append('# TYPE verity_webhook_queue gauge')
                lines.append(f'verity_webhook_queue {int(queued)}')
                lines.append('# TYPE verity_webhook_failed_deliveries counter')
                lines.append(f'verity_webhook_failed_deliveries {int(failed_deliveries)}')
                lines.append('# TYPE verity_providers_total gauge')
                lines.append(f'verity_providers_total {int(providers)}')
                # active SSE client count
                with SSE_LOCK:
                    sse_count = len(SSE_CLIENTS)
                lines.append('# TYPE verity_sse_clients gauge')
                lines.append(f'verity_sse_clients {int(sse_count)}')
                body = '\n'.join(lines) + '\n'
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; version=0.0.4')
                self.end_headers()
                self.wfile.write(body.encode('utf-8'))
                return
            except Exception as e:
                self._set_json(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return
        # list providers or provider detail
        if self.path.startswith('/providers'):
            qs = ''
            if '?' in self.path:
                qs = self.path.split('?',1)[1]
            params = {}
            for p in qs.split('&') if qs else []:
                if '=' in p:
                    k,v = p.split('=',1); params[k]=v
            if 'id' in params:
                r = None
                try:
                    pid = params['id']
                    # return metadata only
                    conn = sqlite3.connect(str(DB_PATH))
                    cur = conn.cursor()
                    cur.execute('SELECT id, name, created_at FROM providers WHERE id=?', (pid,))
                    row = cur.fetchone()
                    conn.close()
                    if row:
                        r = {'id': row[0], 'name': row[1], 'created_at': row[2]}
                except Exception:
                    r = None
                if not r:
                    self._set_json(404)
                    self.wfile.write(json.dumps({'error':'not found'}).encode())
                    return
                self._set_json(200)
                self.wfile.write(json.dumps(r).encode())
                return
            lst = list_providers()
            self._set_json(200)
            self.wfile.write(json.dumps({'providers': lst}).encode())
            return
        self._set_json(404)
        self.wfile.write(json.dumps({'error': 'not found'}).encode())


def run():
    # allow overriding the bind port via env for local dev (avoids conflicts)
    port = int(os.environ.get('SIMPLE_TEST_API_PORT', os.environ.get('PORT', '8010')))
    addr = ('127.0.0.1', port)
    init_db()
    # start webhook worker
    try:
        t = threading.Thread(target=_webhook_worker_loop, daemon=True)
        t.start()
    except Exception:
        pass
    # Sentry init (best-effort)
    try:
        SENTRY_DSN = os.environ.get('SENTRY_DSN')
        if SENTRY_DSN:
            import sentry_sdk
            sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')))
            print('Sentry initialized')
    except Exception:
        pass
    httpd = ThreadingHTTPServer(addr, Handler)
    print('Simple test API running on http://%s:%d' % addr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == '__main__':
    run()
