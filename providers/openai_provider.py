import os

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class OpenAIProvider:
    def __init__(self):
        # Only instantiate client when an API key is configured
        api_key = os.getenv('OPENAI_API_KEY')
        if OpenAI is None or not api_key:
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception:
                self.client = None
    
    def verify_claim(self, claim: str, model: str = "gpt-4o", **kwargs) -> dict:
        """Verify claim using OpenAI model"""
        if self.client is None:
            return {
                "provider": f"openai_{model.replace('-', '_')}",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "OpenAI client not available"
            }
        # Include optional sources in the prompt for search-augmented verification
        sources = kwargs.get("sources") or []
        user_content = f"Verify: {claim}"
        if sources:
            user_content += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)

        response = self.client.chat.completions.create(
            model=model,
            messages=[{
                "role": "system",
                "content": "You are a fact-checking expert. Respond in format: VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE], CONFIDENCE: [0-100], REASONING: [explanation]"
            }, {
                "role": "user",
                "content": user_content
            }],
            temperature=0
        )
        result = response.choices[0].message.content
        return {
            "provider": f"openai_{model.replace('-', '_')}",
            "verdict": self._extract_verdict(result),
            "confidence": self._extract_confidence(result),
            "reasoning": self._extract_reasoning(result),
            "raw_response": str(result),
            "cost": float(self._calculate_cost(getattr(response, 'usage', None), model) or 0.0)
        }
    
    def _extract_verdict(self, text: str) -> str:
        import re
        m = re.search(r'VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)', text, re.IGNORECASE)
        return m.group(1).upper() if m else 'UNVERIFIABLE'
    
    def _extract_confidence(self, text: str) -> int:
        import re
        m = re.search(r'CONFIDENCE:\s*(\d+)', text)
        return int(m.group(1)) if m else 50
    
    def _extract_reasoning(self, text: str) -> str:
        import re
        m = re.search(r'REASONING:\s*(.+)', text, re.DOTALL)
        return m.group(1).strip() if m else text[:300]
    
    def _calculate_cost(self, usage, model: str) -> float:
        costs = {
            "gpt-4o": {"input": 0.000015, "output": 0.00006},
            "gpt-4o-mini": {"input": 0.00000015, "output": 0.0000006},
            "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015}
        }
        model_costs = costs.get(model, costs["gpt-4o"])
        try:
            return (usage.prompt_tokens * model_costs["input"] + usage.completion_tokens * model_costs["output"])
        except Exception:
            return 0.0
