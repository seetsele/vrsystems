import time
from typing import List, Optional, Sequence
import jwt

# Minimal token service used for issuing and verifying scoped JWTs.
# Uses HS256 and a shared secret from environment in production.

class TokenService:
    def __init__(self, secret: Optional[str] = None, issuer: str = 'verity', secrets: Optional[Sequence[str]] = None):
        # `secret` kept for backward-compat; prefer `secrets` which can hold multiple active keys.
        self.issuer = issuer
        if secrets:
            self.secrets = list(secrets)
        elif secret:
            self.secrets = [secret]
        else:
            self.secrets = []

    def create_token(self, subject: str, scopes: List[str], expires_in: int = 3600) -> str:
        if not self.secrets:
            raise RuntimeError('no signing secret configured')
        now = int(time.time())
        payload = {
            'iss': self.issuer,
            'sub': subject,
            'iat': now,
            'exp': now + expires_in,
            'scopes': scopes,
        }
        # Sign with the first (primary) secret
        return jwt.encode(payload, self.secrets[0], algorithm='HS256')

    def verify_token(self, token: str, required_scope: Optional[str] = None) -> dict:
        # Try verification against all known secrets (supports rotation overlap).
        last_err = None
        for s in self.secrets:
            try:
                data = jwt.decode(token, s, algorithms=['HS256'])
                if required_scope and required_scope not in data.get('scopes', []):
                    raise ValueError('missing required scope')
                return data
            except Exception as exc:
                last_err = exc
                continue
        # If none succeeded, raise the last error for debugging
        raise last_err if last_err is not None else RuntimeError('no secrets configured')
