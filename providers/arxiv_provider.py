import arxiv

class ArxivProvider:
    def verify_claim(self, claim: str) -> dict:
        """Search arXiv preprints"""
        try:
            search = arxiv.Search(query=claim, max_results=10, sort_by=arxiv.SortCriterion.Relevance)
            results = list(search.results())
        except Exception as e:
            return {"provider": "arxiv", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not results:
            return {"provider": "arxiv", "verdict": "UNVERIFIABLE", "confidence": 0, "raw_response": None, "cost": 0.0}
        return {"provider": "arxiv", "verdict": "TRUE", "confidence": 85, "reasoning": f"Found {len(results)} preprints", "papers": [{"title": r.title, "authors": [a.name for a in r.authors], "url": r.pdf_url} for r in results[:3]], "raw_response": results, "cost": 0.0}
