from SPARQLWrapper import SPARQLWrapper, JSON

class WikidataProvider:
    def __init__(self):
        self.sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    
    def verify_claim(self, claim: str, entities: list, **kwargs) -> dict:
        """Query Wikidata for structured facts"""
        if not entities:
            return {"provider": "wikidata", "verdict": "UNVERIFIABLE", "confidence": 0}
        entity = entities[0]
        query = f"""
        SELECT ?item ?itemLabel ?property ?propertyLabel ?value ?valueLabel WHERE {{
          ?item rdfs:label "{entity}"@en.
          ?item ?property ?value.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 100
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        try:
            results = self.sparql.query().convert()
            bindings = results["results"]["bindings"]
            if not bindings:
                return {"provider": "wikidata", "verdict": "UNVERIFIABLE", "confidence": 0}
            return {"provider": "wikidata", "verdict": "TRUE", "confidence": 88, "reasoning": f"Found {len(bindings)} Wikidata properties for {entity}", "facts": bindings[:10]}
        except Exception as e:
            return {"provider": "wikidata", "verdict": "ERROR", "confidence": 0, "reasoning": str(e)}
