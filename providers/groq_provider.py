"""
Groq Provider - Ultra-Fast LLM Inference
=========================================
Production-grade Groq integration for lightning-fast verification.

Features:
- Groq API integration (fastest LLM inference)
- Multiple model support (Llama 3.3, Mixtral, etc.)
- Structured output parsing
- Cost tracking
- Rate limiting awareness
"""
from __future__ import annotations

import os
import re
import time
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqProvider:
    """
    Ultra-fast verification provider using Groq's inference infrastructure.
    
    Groq provides the fastest LLM inference available, making it ideal
    for real-time fact verification use cases.
    """
    
    SUPPORTED_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "llama-3.3-70b-versatile",
    ):
        self.enabled = os.getenv("ENABLE_GROQ", "1").lower() not in ("0", "false")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.default_model = default_model
        self.client = None
        
        # Statistics
        self.request_count = 0
        self.total_tokens = 0
        self.total_latency = 0.0
        
        if self.enabled and self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq provider initialized")
            except Exception as e:
                logger.error("Failed to initialize Groq client: %s", e)
                self.client = None

    def verify_claim(
        self,
        claim: str,
        model: Optional[str] = None,
        sources: Optional[List[str]] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Verify a claim using Groq's ultra-fast inference.
        
        Args:
            claim: The claim to verify
            model: Model to use (defaults to llama-3.3-70b-versatile)
            sources: Optional list of source URLs/references
            temperature: LLM temperature (0 = deterministic)
            max_tokens: Maximum response tokens
            
        Returns:
            Standardized verification result
        """
        model = model or self.default_model
        provider_name = f"groq_{model.replace('-', '_').replace('.', '_')}"
        
        if not self.enabled or not self.client:
            return {
                "provider": provider_name,
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "Groq provider not available",
                "cost": 0.0,
            }
        
        # Build prompt with sources
        user_content = claim
        if sources:
            user_content += "\n\nRelevant sources:\n" + "\n".join(f"- {s}" for s in sources)
        
        system_prompt = """You are Verity, an expert fact-checking AI. Analyze claims with precision.

Output format (required):
VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE]
CONFIDENCE: [0-100]
REASONING: [Concise evidence-based explanation]

Guidelines:
- TRUE: Claim is factually accurate with strong evidence
- FALSE: Claim is factually incorrect
- MISLEADING: Partially true but missing context or exaggerated
- UNVERIFIABLE: Insufficient evidence to determine truth"""

        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            elapsed = time.time() - start_time
            result_text = response.choices[0].message.content or ""
            
            # Update stats
            self.request_count += 1
            self.total_latency += elapsed
            if hasattr(response, "usage") and response.usage:
                self.total_tokens += response.usage.total_tokens or 0
            
            # Parse response
            verdict = self._extract_verdict(result_text)
            confidence = self._extract_confidence(result_text)
            reasoning = self._extract_reasoning(result_text)
            
            return {
                "provider": provider_name,
                "model": model,
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
                "raw_response": result_text,
                "cost": 0.0,  # Groq is currently free
                "latency": round(elapsed, 3),
                "tokens": response.usage.total_tokens if hasattr(response, "usage") and response.usage else 0,
            }
            
        except Exception as e:
            logger.error("Groq verification failed: %s", e)
            return {
                "provider": provider_name,
                "model": model,
                "verdict": "ERROR",
                "confidence": 0,
                "reasoning": f"Error: {str(e)}",
                "cost": 0.0,
                "latency": time.time() - start_time,
            }

    def _extract_verdict(self, text: str) -> str:
        """Extract verdict from response."""
        match = re.search(
            r"VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)",
            text,
            re.IGNORECASE,
        )
        return match.group(1).upper() if match else "UNVERIFIABLE"

    def _extract_confidence(self, text: str) -> int:
        """Extract confidence score from response."""
        match = re.search(r"CONFIDENCE:\s*(\d{1,3})", text)
        if match:
            try:
                return min(100, max(0, int(match.group(1))))
            except ValueError:
                pass
        return 50

    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning from response."""
        match = re.search(
            r"REASONING:\s*(.+?)(?=\n\n|$)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()[:500]
        # Fallback: return truncated response
        return text[:300].strip()

    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "provider": "groq",
            "enabled": self.enabled,
            "available": self.client is not None,
            "requests": self.request_count,
            "total_tokens": self.total_tokens,
            "avg_latency": (
                round(self.total_latency / self.request_count, 3)
                if self.request_count > 0
                else 0
            ),
        }

    def health_check(self) -> bool:
        """Check if provider is healthy."""
        return self.enabled and self.client is not None
