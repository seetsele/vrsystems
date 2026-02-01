"""
Anthropic Provider for Verity Systems
Provides Claude-based fact verification via Anthropic API
"""

import os
from typing import Dict, Any, List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

__all__ = ['AnthropicProvider']


class AnthropicProvider:
    """Anthropic Claude-based verification provider."""
    
    def __init__(self) -> None:
        if anthropic is None:
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def verify_claim(self, claim: str, model: str = "claude-opus-4-20250514", **kwargs) -> Dict[str, Any]:
        """
        Verify claim using Claude.
        
        Args:
            claim: The claim to verify
            model: Claude model to use
            **kwargs: Additional options including 'sources' list
            
        Returns:
            Dict containing verdict, confidence, reasoning, and metadata
        """
        if self.client is None:
            return {
                "provider": "anthropic",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "Anthropic client not available"
            }
        try:
            sources: List[str] = kwargs.get("sources") or []
            user_content = f"Verify this claim. Respond with VERDICT, CONFIDENCE (0-100), and REASONING:\n\n{claim}"
            if sources:
                user_content += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)

            message = self.client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": user_content
                }]
            )
            result = getattr(message, 'content', '')
            if isinstance(result, list):
                result = result[0].text if result else ''
        except Exception as exc:
            return {
                "provider": "anthropic",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": str(exc)
            }
        return {
            "provider": f"anthropic_{model}",
            "verdict": self._extract_verdict(result),
            "confidence": self._extract_confidence(result),
            "reasoning": result[:300] if result else "",
            "raw_response": str(result),
            "cost": 0.0
        }
    
    def _extract_verdict(self, text: str) -> str:
        """Extract verdict from model response."""
        import re
        m = re.search(r'VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)', text, re.IGNORECASE)
        return m.group(1).upper() if m else 'UNVERIFIABLE'
    
    def _extract_confidence(self, text: str) -> int:
        """Extract confidence score from model response."""
        import re
        m = re.search(r'CONFIDENCE:\s*(\d+)', text)
        return int(m.group(1)) if m else 50
