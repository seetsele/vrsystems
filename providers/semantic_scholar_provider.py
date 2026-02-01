import requests

class SemanticScholarProvider:
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search academic papers"""
        try:
            response = requests.get(
                f"{self.base_url}/paper/search",
                params={"query": claim, "limit": 10, "fields": "title,abstract,authors,year,citationCount,url"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {"provider": "semantic_scholar", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if 'data' not in data or not data['data']:
            return {"provider": "semantic_scholar", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "No academic papers found", "raw_response": None, "cost": 0.0}
        papers = data['data']
        total_citations = sum(p.get('citationCount', 0) for p in papers)
        confidence = min(70 + (total_citations // 100), 95)
        return {"provider": "semantic_scholar", "verdict": "TRUE", "confidence": confidence, "reasoning": f"Found {len(papers)} papers, {total_citations} total citations", "papers": papers[:3], "raw_response": papers, "cost": 0.0}
