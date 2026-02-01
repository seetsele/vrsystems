import requests
from bs4 import BeautifulSoup

class PolitiFactProvider:
    def __init__(self):
        self.search_url = "https://www.politifact.com/search"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search PolitiFact"""
        try:
            response = requests.get(
                self.search_url,
                params={"q": claim},
                headers={"User-Agent": "VerityBot/1.0"},
                timeout=10
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            first_result = soup.find('div', class_='m-statement')
        except Exception as e:
            return {"provider": "politifact", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not first_result:
            return {"provider": "politifact", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        rating_elem = first_result.find('img', class_='c-image__original')
        rating = rating_elem['alt'] if rating_elem else "Unknown"
        verdict_map = {
            "true": "TRUE",
            "mostly-true": "TRUE",
            "half-true": "MISLEADING",
            "mostly-false": "FALSE",
            "false": "FALSE",
            "pants-fire": "FALSE"
        }
        verdict = verdict_map.get(rating.lower(), "UNVERIFIABLE") if isinstance(rating, str) else "UNVERIFIABLE"
        return {"provider": "politifact", "verdict": verdict, "confidence": 98, "reasoning": f"PolitiFact: {rating}", "raw_response": rating, "cost": 0.0}
