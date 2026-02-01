import requests
import os

class BraveSearchProvider:
    def __init__(self):
        self.api_key = os.getenv('BRAVE_API_KEY')
        self.endpoint = "https://api.search.brave.com/res/v1/web/search"
    
    def verify_claim(self, claim: str) -> dict:
        headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": self.api_key}
        try:
            response = requests.get(self.endpoint, headers=headers, params={"q": claim}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {"provider": "brave_search", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        results = data.get('web', {}).get('results', [])
        if not results:
            return {"provider": "brave_search", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        return {"provider": "brave_search", "verdict": "TRUE", "confidence": 75, "reasoning": f"Found {len(results)} results", "results": results[:5], "raw_response": results, "cost": 0.0}
