import wikipedia

class WikipediaProvider:
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search Wikipedia"""
        try:
            search_results = wikipedia.search(claim, results=3)
            if not search_results:
                return {"provider": "wikipedia", "verdict": "UNVERIFIABLE", "confidence": 0}
            page = wikipedia.page(search_results[0])
            summary_lower = page.summary.lower()
            claim_lower = claim.lower()
            claim_keywords = set(claim_lower.split())
            summary_keywords = set(summary_lower.split())
            overlap = len(claim_keywords & summary_keywords) / len(claim_keywords) if claim_keywords else 0
            if overlap > 0.5:
                verdict = "TRUE"
                confidence = int(overlap * 100)
            else:
                verdict = "UNVERIFIABLE"
                confidence = 30
                return {"provider": "wikipedia", "verdict": verdict, "confidence": min(confidence, 90), "reasoning": f"Wikipedia article: {page.title}", "url": page.url, "raw_response": page.url, "cost": 0.0}
        except wikipedia.exceptions.DisambiguationError:
            return {"provider": "wikipedia", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "Multiple Wikipedia articles found - ambiguous", "raw_response": None, "cost": 0.0}
        except wikipedia.exceptions.PageError:
            return {"provider": "wikipedia", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "No Wikipedia page found", "raw_response": None, "cost": 0.0}
        except Exception as e:
            return {"provider": "wikipedia", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
