import requests
from bs4 import BeautifulSoup

class SnopesProvider:
    def __init__(self):
        self.base_url = "https://www.snopes.com"
        self.search_url = "https://www.snopes.com/search"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search Snopes for claim"""
        try:
            response = requests.get(
                self.search_url,
                params={"q": claim},
                headers={"User-Agent": "VerityBot/1.0"},
                timeout=10
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            first_result = soup.find('article', class_='search-result')
        except Exception as e:
                return {"provider": "snopes", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not first_result:
                return {"provider": "snopes", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "No Snopes article found", "raw_response": None, "cost": 0.0}
        rating_elem = first_result.find('span', class_='rating')
        rating = rating_elem.text.strip() if rating_elem else "Unknown"
        verdict_map = {
            "True": "TRUE",
            "Mostly True": "TRUE",
            "False": "FALSE",
            "Mostly False": "FALSE",
            "Mixture": "MISLEADING",
            "Unproven": "UNVERIFIABLE",
            "Outdated": "MISLEADING"
        }
        verdict = verdict_map.get(rating, "UNVERIFIABLE")
        link = first_result.find('a')['href'] if first_result.find('a') else None
        return {
            "provider": "snopes",
            "verdict": verdict,
            "confidence": 99 if verdict in ["TRUE", "FALSE"] else 85,
            "reasoning": f"Snopes rating: {rating}",
                "raw_response": link,
                "cost": 0.0,
            "source_url": link
        }
