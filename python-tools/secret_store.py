"""
Secret store abstraction. Supports a Vault/KMS placeholder and a local Fernet-backed file store for development.

Usage:
  from secret_store import SecretStore
  store = SecretStore()
  store.set_secret('provider_x', 's3cr3t')
  store.get_secret('provider_x')

For production, set environment variable `USE_VAULT=1` and implement the `_vault_*` methods.
"""
import os
import json
from typing import Optional

from cryptography.fernet import Fernet

STORE_FILE = os.path.join(os.path.dirname(__file__), ".local_secrets.json")


class SecretStore:
    def __init__(self):
        self.use_vault = os.getenv("USE_VAULT", "0") == "1"
        key = os.environ.get("LOCAL_SECRET_KEY")
        if key is None:
            # generate a key and persist to env for dev convenience (in-memory only)
            key = Fernet.generate_key().decode()
            os.environ.setdefault("LOCAL_SECRET_KEY", key)
        self.fernet = Fernet(key.encode())

    def _read_store(self):
        if not os.path.exists(STORE_FILE):
            return {}
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_store(self, data):
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def set_secret(self, name: str, value: str):
        if self.use_vault:
            return self._vault_set_secret(name, value)
        store = self._read_store()
        token = self.fernet.encrypt(value.encode()).decode()
        store[name] = token
        self._write_store(store)

    def rotate_secret(self, name: str, new_value: str):
        """Rotate an existing secret atomically (local dev fallback).

        In production (`USE_VAULT=1`) this should call the KMS/Vault rotate API.
        """
        if self.use_vault:
            return self._vault_rotate_secret(name, new_value)
        store = self._read_store()
        token = self.fernet.encrypt(new_value.encode()).decode()
        store[name] = token
        self._write_store(store)

    def get_secret(self, name: str) -> Optional[str]:
        if self.use_vault:
            return self._vault_get_secret(name)
        store = self._read_store()
        token = store.get(name)
        if not token:
            return None
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return None

    # Placeholder methods for Vault/KMS integration
    def _vault_set_secret(self, name: str, value: str):
        raise NotImplementedError("Vault integration not implemented. Set USE_VAULT=0 for local dev.")

    def _vault_get_secret(self, name: str) -> Optional[str]:
        raise NotImplementedError("Vault integration not implemented. Set USE_VAULT=0 for local dev.")

    def _vault_rotate_secret(self, name: str, new_value: str):
        raise NotImplementedError("Vault rotate not implemented. Implement integration for production.")
