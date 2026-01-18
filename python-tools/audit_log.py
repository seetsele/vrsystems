"""
Tamper-evident audit log: simple hash-chain recorder for verification events.
Stores JSON lines with prev_hash and sha256(payload + prev_hash).
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / "audit_chain.log"


def _compute_hash(payload_str: str, prev_hash: str) -> str:
    h = hashlib.sha256()
    h.update(prev_hash.encode('utf-8'))
    h.update(payload_str.encode('utf-8'))
    return h.hexdigest()


def _get_last_hash() -> str:
    if not AUDIT_FILE.exists():
        return ""  # genesis
    try:
        with AUDIT_FILE.open('rb') as f:
            lines = f.read().splitlines()
            if not lines:
                return ""
            last = lines[-1].decode('utf-8')
            entry = json.loads(last)
            return entry.get('hash', '')
    except Exception:
        return ""


def record_event(event_type: str, data: dict) -> dict:
    """Record an audit event and append to the chain. Returns the entry."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    payload = {
        'type': event_type,
        'timestamp': timestamp,
        'data': data
    }
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    prev = _get_last_hash()
    entry_hash = _compute_hash(payload_str, prev)
    entry = {
        'payload': payload,
        'prev': prev,
        'hash': entry_hash
    }
    try:
        with AUDIT_FILE.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry, separators=(',', ':')) + "\n")
    except Exception:
        pass
    return entry


def get_chain(limit: int = 100) -> list:
    """Return last `limit` audit entries (most recent last)."""
    if not AUDIT_FILE.exists():
        return []
    out = []
    try:
        with AUDIT_FILE.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out[-limit:]
