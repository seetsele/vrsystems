from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Any
import asyncio
import re


@dataclass
class VerificationResult:
    """Standardized verification result used by orchestrator and adapters."""
    provider: str
    verdict: str  # TRUE, FALSE, MISLEADING, UNVERIFIABLE
    confidence: float = 0.0  # 0-100
    reasoning: str = ""
    cost: float = 0.0
    response_time: float = 0.0
    raw_response: Optional[str] = None
    sources: Optional[List[str]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseAIProvider(ABC):
    """Base class all async provider adapters should inherit from."""

    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key

        self.request_count = 0
        self.total_cost = 0.0
        self.total_time = 0.0

    @abstractmethod
    async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
        """Verify a claim and return standardized result"""
        raise NotImplementedError()

    async def verify_claim_with_retry(
        self,
        claim: str,
        max_retries: int = 3,
        **kwargs,
    ) -> VerificationResult:
        """Verify with automatic retry logic; returns an ERROR result on repeated failures."""
        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                result = await self.verify_claim(claim, **kwargs)
                self.request_count += 1
                self.total_cost += getattr(result, "cost", 0.0)
                self.total_time += getattr(result, "response_time", 0.0)
                return result
            except Exception as e:
                last_exc = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    return VerificationResult(
                        provider=self.name,
                        verdict="ERROR",
                        confidence=0.0,
                        reasoning=f"Error: {str(e)}",
                        cost=0.0,
                        response_time=0.0,
                    )

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse free-form LLM text responses for `VERDICT`, `CONFIDENCE`, and `REASONING`."""
        if not text:
            return {"verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": ""}

        # Extract verdict
        verdict_match = re.search(r"VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)", text, re.IGNORECASE)
        verdict = verdict_match.group(1).upper() if verdict_match else "UNVERIFIABLE"

        # Extract confidence
        conf_match = re.search(r"CONFIDENCE:\s*(\d{1,3})", text)
        try:
            confidence = int(conf_match.group(1)) if conf_match else 50
        except Exception:
            confidence = 50

        # Extract reasoning
        reasoning_match = re.search(r"REASONING:\s*(.+?)(?=SOURCES:|$)", text, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else text.strip()[:1000]

        return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}

    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "name": self.name,
            "requests": self.request_count,
            "total_cost": self.total_cost,
            "avg_cost": self.total_cost / self.request_count if self.request_count > 0 else 0,
            "avg_time": self.total_time / self.request_count if self.request_count > 0 else 0,
        }
