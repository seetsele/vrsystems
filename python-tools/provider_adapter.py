"""ProviderAdapter: wrap multiple model providers with retry, backoff and failover.

Usage: create ProviderAdapter with provider callables and call `verify_claim(text)`.
This is a minimal, easily-extended example for local/deployment use.
"""
import time
import random
from typing import Callable, List, Dict, Any


class ProviderError(Exception):
    pass


class Provider:
    def __init__(self, name: str, call_fn: Callable[[str], Dict[str, Any]], weight: int = 1):
        self.name = name
        self.call_fn = call_fn
        self.weight = weight
        self.failures = 0


class ProviderAdapter:
    def __init__(self, providers: List[Provider], max_retries: int = 2, backoff_base: float = 0.5):
        self.providers = providers
        self.max_retries = max_retries
        self.backoff_base = backoff_base

    def _choose_providers(self) -> List[Provider]:
        # Prefer providers with fewer recent failures. Simple weighted shuffle.
        ordered = sorted(self.providers, key=lambda p: p.failures)
        return ordered

    def verify_claim(self, text: str) -> Dict[str, Any]:
        last_exc = None
        for provider in self._choose_providers():
            for attempt in range(self.max_retries + 1):
                try:
                    result = provider.call_fn(text)
                    # Reset failures on success
                    provider.failures = max(0, provider.failures - 1)
                    return {"provider": provider.name, "result": result}
                except Exception as e:
                    provider.failures += 1
                    last_exc = e
                    backoff = self.backoff_base * (2 ** attempt) + random.random() * 0.1
                    time.sleep(backoff)
                    continue

        raise ProviderError(f"All providers failed. Last error: {last_exc}")


if __name__ == "__main__":
    # Demo providers
    def p1(text):
        if "fail1" in text:
            raise RuntimeError("provider1 down")
        return {"verdict": "true", "confidence": 90}

    def p2(text):
        return {"verdict": "mixed", "confidence": 60}

    adapter = ProviderAdapter([Provider('p1', p1), Provider('p2', p2)])
    print(adapter.verify_claim('some test'))
