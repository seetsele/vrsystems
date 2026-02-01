import requests

class OpenAlexProvider:
    def __init__(self, email="your@email.com"):
        self.base_url = "https://api.openalex.org"
        self.email = email
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search OpenAlex"""
        try:
            response = requests.get(
                f"{self.base_url}/works",
                params={"filter": f"title.search:{claim}", "per-page": 10, "mailto": self.email},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {"provider": "openalex", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        results = data.get('results', [])
        if not results:
            return {"provider": "openalex", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        total_cited = sum(r.get('cited_by_count', 0) for r in results)
        return {"provider": "openalex", "verdict": "TRUE", "confidence": min(75 + (total_cited // 50), 94), "reasoning": f"Found {len(results)} works, {total_cited} citations", "works": results[:3], "raw_response": results, "cost": 0.0}
