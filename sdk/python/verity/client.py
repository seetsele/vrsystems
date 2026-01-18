import requests
import asyncio
import httpx


class VerityClient:
    """Synchronous Verity SDK client (minimal)."""
    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:8000"):
        self.api_key = api_key
        self.base = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def verify(self, claim: str, tier: str = "free") -> dict:
        resp = requests.post(f"{self.base}/verify", json={"claim": claim, "tier": tier}, headers=self.headers, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def verify_stream(self, claim: str, tier: str = "free"):
        # Minimal streaming: yield single full response for compatibility
        result = self.verify(claim, tier=tier)
        yield result


class AsyncVerityClient:
    """Async Verity SDK client (minimal)."""
    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:8000"):
        self.api_key = api_key
        self.base = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def verify(self, claim: str, tier: str = "free") -> dict:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{self.base}/verify", json={"claim": claim, "tier": tier}, headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def verify_stream(self, claim: str, tier: str = "free"):
        # Minimal: return single response as async iterator
        res = await self.verify(claim, tier=tier)
        yield res
