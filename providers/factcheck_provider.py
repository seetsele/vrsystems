import requests
from bs4 import BeautifulSoup

class FactCheckOrgProvider:
    def __init__(self):
        self.base_url = "https://www.factcheck.org"
        self.search_url = "https://www.factcheck.org/?s="
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        try:
            response = requests.get(self.search_url + requests.utils.quote(claim), headers={"User-Agent": "VerityBot/1.0"}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            first = soup.find('div', class_='post')
        except Exception as e:
            return {"provider": "factcheck_org", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not first:
            return {"provider": "factcheck_org", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "No FactCheck.org article found", "raw_response": None, "cost": 0.0}
        title = first.find('h2')
        link = first.find('a')['href'] if first.find('a') else None
        return {"provider": "factcheck_org", "verdict": "UNVERIFIABLE", "confidence": 80, "reasoning": f"Found article: {title.text.strip() if title else 'unknown'}", "source_url": link, "raw_response": link, "cost": 0.0}
