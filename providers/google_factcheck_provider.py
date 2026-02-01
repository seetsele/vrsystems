import requests
import os

class GoogleFactCheckProvider:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        """Search Google Fact Check API"""
        try:
            response = requests.get(
                self.endpoint,
                params={"query": claim, "key": self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return {"provider": "google_fact_check", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e)}
        if 'claims' not in data or not data['claims']:
            return {"provider": "google_fact_check", "verdict": "UNVERIFIABLE", "confidence": 0}
        first_claim = data['claims'][0]
        reviews = first_claim.get('claimReview', [])
        if not reviews:
            return {"provider": "google_fact_check", "verdict": "UNVERIFIABLE", "confidence": 0}
        first_review = reviews[0]
        rating = (first_review.get('textualRating') or '').lower()
        if 'true' in rating or 'correct' in rating:
            verdict = "TRUE"
        elif 'false' in rating or 'incorrect' in rating:
            verdict = "FALSE"
        elif 'misleading' in rating or 'mixture' in rating:
            verdict = "MISLEADING"
        else:
            verdict = "UNVERIFIABLE"
        return {
            "provider": "google_fact_check",
            "verdict": verdict,
            "confidence": 90,
            "reasoning": rating,
            "publisher": first_review.get('publisher', {}).get('name', 'Unknown')
        }
