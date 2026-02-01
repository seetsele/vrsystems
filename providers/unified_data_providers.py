"""
Unified Data Providers Integration
===================================
Integrates ALL standalone provider files into a unified data source system.
These providers handle fact-checking, academic research, web search, and knowledge bases.

This module bridges the gap between:
1. Standalone provider files (wikipedia_provider.py, pubmed_provider.py, etc.)
2. The DataSourceAggregator in data_sources/all_sources.py
3. The main verification orchestration system

Categories:
- FACT_CHECKERS: Snopes, PolitiFact, FactCheck.org, Full Fact, Africa Check, Google Fact Check
- ACADEMIC_SOURCES: PubMed, arXiv, Semantic Scholar, CrossRef, OpenAlex
- KNOWLEDGE_BASES: Wikipedia, Wikidata
- SEARCH_ENGINES: DuckDuckGo, Brave Search
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================
# UNIFIED RESULT STRUCTURE
# ============================================================

@dataclass
class DataSourceResult:
    """Unified result from any data source provider"""
    provider: str
    verdict: str  # TRUE, FALSE, MISLEADING, UNVERIFIABLE
    confidence: int  # 0-100
    reasoning: str
    source_url: Optional[str] = None
    source_type: str = "general"  # fact_checker, academic, search, knowledge_base
    raw_data: Optional[Any] = None
    cost: float = 0.0
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# FACT-CHECKER PROVIDERS
# ============================================================

class UnifiedFactCheckers:
    """Aggregates all fact-checking providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all fact-checker providers safely"""
        
        # Snopes
        try:
            from providers.snopes_provider import SnopesProvider
            self.providers['snopes'] = SnopesProvider()
        except Exception as e:
            logger.warning(f"Snopes provider not available: {e}")
        
        # PolitiFact
        try:
            from providers.politifact_provider import PolitiFactProvider
            self.providers['politifact'] = PolitiFactProvider()
        except Exception as e:
            logger.warning(f"PolitiFact provider not available: {e}")
        
        # FactCheck.org
        try:
            from providers.factcheck_provider import FactCheckOrgProvider
            self.providers['factcheck_org'] = FactCheckOrgProvider()
        except Exception as e:
            logger.warning(f"FactCheck.org provider not available: {e}")
        
        # Full Fact (UK)
        try:
            from providers.full_fact_provider import FullFactProvider
            self.providers['full_fact'] = FullFactProvider()
        except Exception as e:
            logger.warning(f"Full Fact provider not available: {e}")
        
        # Africa Check
        try:
            from providers.africa_check_provider import AfricaCheckProvider
            self.providers['africa_check'] = AfricaCheckProvider()
        except Exception as e:
            logger.warning(f"Africa Check provider not available: {e}")
        
        # Google Fact Check API
        try:
            from providers.google_factcheck_provider import GoogleFactCheckProvider
            self.providers['google_factcheck'] = GoogleFactCheckProvider()
        except Exception as e:
            logger.warning(f"Google Fact Check provider not available: {e}")
    
    async def check_claim(self, claim: str, use_all: bool = True) -> List[DataSourceResult]:
        """Check a claim against all fact-checking sources"""
        results = []
        
        async def _check_one(name: str, provider):
            try:
                result = provider.verify_claim(claim)
                return DataSourceResult(
                    provider=name,
                    verdict=result.get('verdict', 'UNVERIFIABLE'),
                    confidence=result.get('confidence', 0),
                    reasoning=result.get('reasoning', ''),
                    source_url=result.get('source_url'),
                    source_type='fact_checker',
                    raw_data=result.get('raw_response'),
                    metadata={'rating': result.get('rating')}
                )
            except Exception as e:
                logger.error(f"Error from {name}: {e}")
                return None
        
        tasks = [_check_one(name, prov) for name, prov in self.providers.items()]
        checked = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in checked:
            if res and not isinstance(res, Exception):
                results.append(res)
        
        return results
    
    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())


# ============================================================
# ACADEMIC SOURCE PROVIDERS
# ============================================================

class UnifiedAcademicSources:
    """Aggregates all academic research providers"""
    
    def __init__(self, email: str = "verity@example.com"):
        self.email = email
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all academic providers safely"""
        
        # PubMed (Biomedical)
        try:
            from providers.pubmed_provider import PubMedProvider
            self.providers['pubmed'] = PubMedProvider(email=self.email)
        except Exception as e:
            logger.warning(f"PubMed provider not available: {e}")
        
        # arXiv (Preprints)
        try:
            from providers.arxiv_provider import ArxivProvider
            self.providers['arxiv'] = ArxivProvider()
        except Exception as e:
            logger.warning(f"arXiv provider not available: {e}")
        
        # Semantic Scholar (All fields)
        try:
            from providers.semantic_scholar_provider import SemanticScholarProvider
            self.providers['semantic_scholar'] = SemanticScholarProvider()
        except Exception as e:
            logger.warning(f"Semantic Scholar provider not available: {e}")
        
        # CrossRef (DOI metadata)
        try:
            from providers.crossref_provider import CrossRefProvider
            self.providers['crossref'] = CrossRefProvider()
        except Exception as e:
            logger.warning(f"CrossRef provider not available: {e}")
        
        # OpenAlex (Open academic data)
        try:
            from providers.openalex_provider import OpenAlexProvider
            self.providers['openalex'] = OpenAlexProvider(email=self.email)
        except Exception as e:
            logger.warning(f"OpenAlex provider not available: {e}")
    
    async def search_academic(self, query: str, max_per_source: int = 5) -> List[DataSourceResult]:
        """Search academic sources for evidence"""
        results = []
        
        async def _search_one(name: str, provider):
            try:
                result = provider.verify_claim(query)
                return DataSourceResult(
                    provider=name,
                    verdict=result.get('verdict', 'UNVERIFIABLE'),
                    confidence=result.get('confidence', 0),
                    reasoning=result.get('reasoning', ''),
                    source_type='academic',
                    raw_data=result.get('papers') or result.get('dois') or result.get('works') or result.get('ids'),
                    metadata={
                        'paper_count': len(result.get('papers', result.get('ids', []))),
                        'citations': result.get('citations', 0)
                    }
                )
            except Exception as e:
                logger.error(f"Error from {name}: {e}")
                return None
        
        tasks = [_search_one(name, prov) for name, prov in self.providers.items()]
        checked = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in checked:
            if res and not isinstance(res, Exception):
                results.append(res)
        
        return results
    
    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())


# ============================================================
# KNOWLEDGE BASE PROVIDERS
# ============================================================

class UnifiedKnowledgeBases:
    """Aggregates Wikipedia, Wikidata, and similar sources"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize knowledge base providers"""
        
        # Wikipedia
        try:
            from providers.wikipedia_provider import WikipediaProvider
            self.providers['wikipedia'] = WikipediaProvider()
        except Exception as e:
            logger.warning(f"Wikipedia provider not available: {e}")
        
        # Wikidata (Structured data)
        try:
            from providers.wikidata_provider import WikidataProvider
            self.providers['wikidata'] = WikidataProvider()
        except Exception as e:
            logger.warning(f"Wikidata provider not available: {e}")
    
    async def query_knowledge(self, query: str, entities: List[str] = None) -> List[DataSourceResult]:
        """Query knowledge bases"""
        results = []
        
        # Wikipedia
        if 'wikipedia' in self.providers:
            try:
                result = self.providers['wikipedia'].verify_claim(query)
                results.append(DataSourceResult(
                    provider='wikipedia',
                    verdict=result.get('verdict', 'UNVERIFIABLE'),
                    confidence=result.get('confidence', 0),
                    reasoning=result.get('reasoning', ''),
                    source_url=result.get('url'),
                    source_type='knowledge_base',
                    raw_data=result.get('raw_response')
                ))
            except Exception as e:
                logger.error(f"Wikipedia error: {e}")
        
        # Wikidata (needs entities)
        if 'wikidata' in self.providers and entities:
            try:
                result = self.providers['wikidata'].verify_claim(query, entities=entities)
                results.append(DataSourceResult(
                    provider='wikidata',
                    verdict=result.get('verdict', 'UNVERIFIABLE'),
                    confidence=result.get('confidence', 0),
                    reasoning=result.get('reasoning', ''),
                    source_type='knowledge_base',
                    raw_data=result.get('facts'),
                    metadata={'entity_count': len(entities)}
                ))
            except Exception as e:
                logger.error(f"Wikidata error: {e}")
        
        return results
    
    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())


# ============================================================
# SEARCH ENGINE PROVIDERS
# ============================================================

class UnifiedSearchEngines:
    """Aggregates web search providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize search engine providers"""
        
        # DuckDuckGo (Privacy-focused, no API key needed)
        try:
            from providers.duckduckgo_provider import DuckDuckGoProvider
            self.providers['duckduckgo'] = DuckDuckGoProvider()
        except Exception as e:
            logger.warning(f"DuckDuckGo provider not available: {e}")
        
        # Brave Search (Privacy-focused, API key optional)
        try:
            from providers.brave_search_provider import BraveSearchProvider
            if os.getenv('BRAVE_API_KEY'):
                self.providers['brave'] = BraveSearchProvider()
        except Exception as e:
            logger.warning(f"Brave Search provider not available: {e}")
    
    async def web_search(self, query: str, max_results: int = 10) -> List[DataSourceResult]:
        """Search the web"""
        results = []
        
        for name, provider in self.providers.items():
            try:
                result = provider.verify_claim(query)
                results.append(DataSourceResult(
                    provider=name,
                    verdict=result.get('verdict', 'UNVERIFIABLE'),
                    confidence=result.get('confidence', 0),
                    reasoning=result.get('reasoning', ''),
                    source_type='search',
                    raw_data=result.get('results'),
                    metadata={'result_count': len(result.get('results', []))}
                ))
            except Exception as e:
                logger.error(f"{name} error: {e}")
        
        return results
    
    def get_available_providers(self) -> List[str]:
        return list(self.providers.keys())


# ============================================================
# MASTER DATA PROVIDER AGGREGATOR
# ============================================================

class MasterDataProviderAggregator:
    """
    Central hub for ALL data source providers.
    Coordinates fact-checkers, academic sources, knowledge bases, and search engines.
    """
    
    def __init__(self, email: str = "verity@example.com"):
        self.fact_checkers = UnifiedFactCheckers()
        self.academic_sources = UnifiedAcademicSources(email=email)
        self.knowledge_bases = UnifiedKnowledgeBases()
        self.search_engines = UnifiedSearchEngines()
        
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def get_all_available_providers(self) -> Dict[str, List[str]]:
        """Get all available providers by category"""
        return {
            'fact_checkers': self.fact_checkers.get_available_providers(),
            'academic': self.academic_sources.get_available_providers(),
            'knowledge_bases': self.knowledge_bases.get_available_providers(),
            'search_engines': self.search_engines.get_available_providers()
        }
    
    def get_provider_count(self) -> int:
        """Get total number of available providers"""
        avail = self.get_all_available_providers()
        return sum(len(v) for v in avail.values())
    
    async def comprehensive_check(
        self,
        claim: str,
        entities: List[str] = None,
        include_fact_checkers: bool = True,
        include_academic: bool = True,
        include_knowledge: bool = True,
        include_search: bool = True,
        max_sources_per_category: int = 5
    ) -> Dict[str, List[DataSourceResult]]:
        """
        Perform comprehensive verification across all data source categories.
        
        Args:
            claim: The claim to verify
            entities: Named entities extracted from claim (for Wikidata)
            include_*: Flags to enable/disable categories
            max_sources_per_category: Limit results per category
            
        Returns:
            Dictionary with results from each category
        """
        results = {}
        tasks = []
        
        if include_fact_checkers:
            tasks.append(('fact_checkers', self.fact_checkers.check_claim(claim)))
        
        if include_academic:
            tasks.append(('academic', self.academic_sources.search_academic(claim, max_sources_per_category)))
        
        if include_knowledge:
            tasks.append(('knowledge_bases', self.knowledge_bases.query_knowledge(claim, entities)))
        
        if include_search:
            tasks.append(('search', self.search_engines.web_search(claim)))
        
        # Run all in parallel
        task_results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        for (category, _), result in zip(tasks, task_results):
            if isinstance(result, Exception):
                logger.error(f"Category {category} failed: {result}")
                results[category] = []
            else:
                results[category] = result[:max_sources_per_category]
        
        return results
    
    async def quick_fact_check(self, claim: str) -> Dict[str, Any]:
        """
        Quick fact-check using only the fastest/most reliable sources.
        Prioritizes: fact-checkers > Wikipedia > DuckDuckGo
        """
        # Check fact-checkers first
        fact_results = await self.fact_checkers.check_claim(claim)
        
        # If fact-checkers found something definitive, return early
        definitive = [r for r in fact_results if r.verdict in ('TRUE', 'FALSE') and r.confidence > 85]
        if definitive:
            return {
                'verdict': definitive[0].verdict,
                'confidence': definitive[0].confidence,
                'source': definitive[0].provider,
                'reasoning': definitive[0].reasoning,
                'source_url': definitive[0].source_url,
                'all_results': fact_results
            }
        
        # Fall back to Wikipedia
        wiki_results = await self.knowledge_bases.query_knowledge(claim)
        
        # Combine and return best result
        all_results = fact_results + wiki_results
        if all_results:
            best = max(all_results, key=lambda x: x.confidence)
            return {
                'verdict': best.verdict,
                'confidence': best.confidence,
                'source': best.provider,
                'reasoning': best.reasoning,
                'source_url': best.source_url,
                'all_results': all_results
            }
        
        return {
            'verdict': 'UNVERIFIABLE',
            'confidence': 0,
            'source': None,
            'reasoning': 'No data sources could verify this claim',
            'all_results': []
        }
    
    def aggregate_verdicts(self, results: Dict[str, List[DataSourceResult]]) -> Dict[str, Any]:
        """
        Aggregate verdicts from multiple sources into a consensus.
        Uses weighted voting based on source type credibility.
        """
        # Credibility weights by source type
        weights = {
            'fact_checker': 1.0,      # Highest credibility
            'academic': 0.9,          # Very high
            'knowledge_base': 0.7,    # High
            'search': 0.4             # Lower (general web results)
        }
        
        all_results = []
        for category_results in results.values():
            all_results.extend(category_results)
        
        if not all_results:
            return {
                'final_verdict': 'UNVERIFIABLE',
                'confidence': 0,
                'agreement': 0.0,
                'source_count': 0
            }
        
        # Weighted voting
        verdict_scores = {'TRUE': 0, 'FALSE': 0, 'MISLEADING': 0, 'UNVERIFIABLE': 0}
        total_weight = 0
        
        for result in all_results:
            weight = weights.get(result.source_type, 0.5) * (result.confidence / 100)
            verdict_scores[result.verdict] = verdict_scores.get(result.verdict, 0) + weight
            total_weight += weight
        
        if total_weight == 0:
            return {
                'final_verdict': 'UNVERIFIABLE',
                'confidence': 0,
                'agreement': 0.0,
                'source_count': len(all_results)
            }
        
        # Determine winner
        final_verdict = max(verdict_scores, key=verdict_scores.get)
        final_score = verdict_scores[final_verdict]
        agreement = final_score / total_weight if total_weight > 0 else 0
        
        # Confidence is based on agreement and number of sources
        confidence = min(95, agreement * 100 * min(1.0, len(all_results) / 3))
        
        return {
            'final_verdict': final_verdict,
            'confidence': int(confidence),
            'agreement': round(agreement, 3),
            'source_count': len(all_results),
            'verdict_breakdown': verdict_scores
        }


# ============================================================
# FASTAPI ROUTER FOR DATA PROVIDERS
# ============================================================

def create_data_providers_router():
    """Create FastAPI router for data provider endpoints"""
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        return None
    
    router = APIRouter(prefix="/data-sources", tags=["Data Sources"])
    aggregator = MasterDataProviderAggregator()
    
    class ClaimRequest(BaseModel):
        claim: str
        entities: List[str] = []
        include_fact_checkers: bool = True
        include_academic: bool = True
        include_knowledge: bool = True
        include_search: bool = True
    
    @router.get("/providers")
    async def get_available_providers():
        """Get all available data source providers"""
        return {
            "providers": aggregator.get_all_available_providers(),
            "total_count": aggregator.get_provider_count()
        }
    
    @router.post("/comprehensive-check")
    async def comprehensive_check(request: ClaimRequest):
        """Comprehensive check across all data sources"""
        results = await aggregator.comprehensive_check(
            claim=request.claim,
            entities=request.entities,
            include_fact_checkers=request.include_fact_checkers,
            include_academic=request.include_academic,
            include_knowledge=request.include_knowledge,
            include_search=request.include_search
        )
        
        consensus = aggregator.aggregate_verdicts(results)
        
        # Convert results to JSON-serializable format
        serialized_results = {}
        for category, cat_results in results.items():
            serialized_results[category] = [
                {
                    'provider': r.provider,
                    'verdict': r.verdict,
                    'confidence': r.confidence,
                    'reasoning': r.reasoning,
                    'source_url': r.source_url,
                    'source_type': r.source_type
                }
                for r in cat_results
            ]
        
        return {
            "claim": request.claim,
            "consensus": consensus,
            "results_by_category": serialized_results
        }
    
    @router.post("/quick-check")
    async def quick_fact_check(request: ClaimRequest):
        """Quick fact-check using fastest sources"""
        result = await aggregator.quick_fact_check(request.claim)
        
        return {
            "claim": request.claim,
            "verdict": result['verdict'],
            "confidence": result['confidence'],
            "source": result['source'],
            "reasoning": result['reasoning'],
            "source_url": result.get('source_url')
        }
    
    @router.get("/fact-checkers")
    async def get_fact_checker_status():
        """Get status of fact-checker integrations"""
        providers = aggregator.fact_checkers.get_available_providers()
        return {
            "available": providers,
            "count": len(providers),
            "supported": ["snopes", "politifact", "factcheck_org", "full_fact", "africa_check", "google_factcheck"]
        }
    
    @router.get("/academic-sources")
    async def get_academic_status():
        """Get status of academic source integrations"""
        providers = aggregator.academic_sources.get_available_providers()
        return {
            "available": providers,
            "count": len(providers),
            "supported": ["pubmed", "arxiv", "semantic_scholar", "crossref", "openalex"]
        }
    
    return router


# ============================================================
# STANDALONE TEST
# ============================================================

async def test_providers():
    """Test all provider integrations"""
    print("=" * 60)
    print("TESTING UNIFIED DATA PROVIDERS")
    print("=" * 60)
    
    aggregator = MasterDataProviderAggregator()
    
    print("\n📊 Available Providers:")
    for category, providers in aggregator.get_all_available_providers().items():
        print(f"  {category}: {', '.join(providers) or 'none'}")
    
    print(f"\n  Total: {aggregator.get_provider_count()} providers")
    
    test_claim = "The Earth is approximately 4.5 billion years old"
    print(f"\n🔍 Testing claim: '{test_claim}'")
    
    # Quick check
    print("\n⚡ Quick fact-check...")
    quick_result = await aggregator.quick_fact_check(test_claim)
    print(f"  Verdict: {quick_result['verdict']}")
    print(f"  Confidence: {quick_result['confidence']}%")
    print(f"  Source: {quick_result['source']}")
    
    # Comprehensive check
    print("\n🔬 Comprehensive check...")
    full_results = await aggregator.comprehensive_check(test_claim, entities=["Earth"])
    consensus = aggregator.aggregate_verdicts(full_results)
    
    print(f"  Final Verdict: {consensus['final_verdict']}")
    print(f"  Confidence: {consensus['confidence']}%")
    print(f"  Agreement: {consensus['agreement'] * 100:.1f}%")
    print(f"  Sources consulted: {consensus['source_count']}")
    
    print("\n✅ Provider integration test complete!")


if __name__ == "__main__":
    asyncio.run(test_providers())
