import requests
import os

class PerplexityProvider:
    def __init__(self):
        self.enabled = os.getenv('ENABLE_PERPLEXITY', '1') not in ('0', 'false', 'False')
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        sources = kwargs.get("sources") or []
        user_content = f"Fact-check with sources: {claim}"
        if sources:
            user_content += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{
                "role": "user",
                "content": user_content
            }]
        }
        if not self.enabled or not self.api_key:
            return {
                "provider": "perplexity_sonar",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "Perplexity disabled or API key missing"
            }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
        except Exception as e:
            return {
                "provider": "perplexity_sonar",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": str(e)
            }
        return {
            "provider": "perplexity_sonar",
            "verdict": self._extract_verdict(result),
            "confidence": self._extract_confidence(result),
            "reasoning": result,
            "raw_response": str(result),
            "cost": 0.0
        }
    
    def _extract_verdict(self, text: str) -> str:
        import re
        m = re.search(r'VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)', text, re.IGNORECASE)
        return m.group(1).upper() if m else 'UNVERIFIABLE'

    def _extract_confidence(self, text: str) -> int:
        import re
        m = re.search(r'CONFIDENCE:\s*(\d+)', text)
        return int(m.group(1)) if m else 50
