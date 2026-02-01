import requests

class CrossRefProvider:
    def __init__(self):
        self.base_url = "https://api.crossref.org/works"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search CrossRef for DOI metadata"""
        try:
            response = requests.get(self.base_url, params={"query": claim, "rows": 10}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {"provider": "crossref", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        items = data.get('message', {}).get('items', [])
        if not items:
            return {"provider": "crossref", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        return {"provider": "crossref", "verdict": "TRUE", "confidence": 90, "reasoning": f"Found {len(items)} works with DOIs", "dois": [item.get('DOI') for item in items[:5]], "raw_response": items, "cost": 0.0}
