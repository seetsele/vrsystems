from duckduckgo_search import DDGS

class DuckDuckGoProvider:
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search DuckDuckGo"""
        try:
            ddgs = DDGS()
            results = list(ddgs.text(claim, max_results=10))
        except Exception as e:
            return {"provider": "duckduckgo", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not results:
            return {"provider": "duckduckgo", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        return {"provider": "duckduckgo", "verdict": "TRUE", "confidence": 70, "reasoning": f"Found {len(results)} web results", "results": results[:5], "raw_response": results, "cost": 0.0}
