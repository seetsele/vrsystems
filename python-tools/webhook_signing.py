"""Utilities for signing and verifying webhook payloads (HMAC-SHA256)."""
import hmac
import hashlib
import base64
from typing import Optional


def sign_payload(secret: str, payload: bytes) -> str:
    mac = hmac.new(secret.encode(), payload, hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


def verify_signature(secret: str, payload: bytes, signature_b64: str) -> bool:
    try:
        expected = base64.b64decode(signature_b64)
    except Exception:
        return False
    mac = hmac.new(secret.encode(), payload, hashlib.sha256)
    return hmac.compare_digest(mac.digest(), expected)
