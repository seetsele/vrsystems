"""Minimal Python SDK stub for Verity API (usable in tests and examples)."""
from typing import Optional
import requests


class VerityClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _headers(self):
        h = {'Accept': 'application/json'}
        if self.api_key:
            h['Authorization'] = f'Bearer {self.api_key}'
        return h

    def moderate(self, content: str):
        return requests.post(f"{self.base_url}/api/moderate", json={'content': content}, headers=self._headers()).json()
"""Minimal Verity Python SDK (local package)."""
from .client import VerityClient, AsyncVerityClient

__all__ = ["VerityClient", "AsyncVerityClient"]
