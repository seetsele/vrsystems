import requests
from bs4 import BeautifulSoup

class AfricaCheckProvider:
    def __init__(self):
        self.search_url = "https://africacheck.org/?s="
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        try:
            response = requests.get(self.search_url + requests.utils.quote(claim), headers={"User-Agent": "VerityBot/1.0"}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            first = soup.find('article')
        except Exception as e:
            return {"provider": "africa_check", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e)}
        if not first:
            return {"provider": "africa_check", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "No Africa Check article found"}
        title = first.find(['h1','h2'])
        link = first.find('a')['href'] if first.find('a') else None
        return {"provider": "africa_check", "verdict": "UNVERIFIABLE", "confidence": 80, "reasoning": f"Found article: {title.text.strip() if title else 'unknown'}", "source_url": link}
