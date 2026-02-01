try:
    from Bio import Entrez
except Exception:
    Entrez = None

class PubMedProvider:
    def __init__(self, email="your@email.com"):
        if Entrez is not None:
            Entrez.email = email
    
    def verify_claim(self, claim: str, **kwargs) -> dict:
        if Entrez is None:
            return {"provider": "pubmed", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "Biopython Entrez not available", "raw_response": None, "cost": 0.0}
        try:
            handle = Entrez.esearch(db="pubmed", term=claim, retmax=10)
            record = Entrez.read(handle)
            ids = record.get("IdList", [])
        except Exception as e:
            return {"provider": "pubmed", "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e), "raw_response": None, "cost": 0.0}
        if not ids:
            return {"provider": "pubmed", "verdict": "UNVERIFIABLE", "confidence": 0}
        return {"provider": "pubmed", "verdict": "TRUE", "confidence": 92, "reasoning": f"Found {len(ids)} PubMed articles", "ids": ids, "raw_response": ids, "cost": 0.0}
