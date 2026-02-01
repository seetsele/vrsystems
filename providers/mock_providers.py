"""Lightweight mock providers for unit tests and CI.

These return deterministic responses to keep tests fast and reliable.
"""
from typing import Any, Dict


class MockProvider:
    def __init__(self, name: str):
        self.name = name

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> Dict[str, Any]:
        # Deterministic mock response used by tests and CI when enabled
        return {
            "provider": self.name,
            "status": "success",
            "verdict": "SUPPORTED",
            "confidence": 0.95,
            "reason": "mocked provider response",
        }

    # sync wrapper for code that may call a sync verify
    def verify_claim(self, claim: str, **kwargs) -> Dict[str, Any]:
        import asyncio

        return asyncio.get_event_loop().run_until_complete(self.verify_claim_with_retry(claim, **kwargs))
