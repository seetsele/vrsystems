"""
Verity Systems - Extended Data Sources
Additional free and premium data sources for comprehensive fact-checking.

Categories:
- Academic & Research (Semantic Scholar, PubMed, arXiv, CrossRef)
- News & Media (NewsAPI, MediaStack, CurrentsAPI)  
- Social Media Analysis (Twitter/X trends, Reddit)
- Government & Official (Data.gov, WHO, CDC)
- Knowledge Bases (Wikidata, DBpedia, YAGO)
- Image/Video Analysis (TinEye, Google Vision)

Author: Verity Systems
License: MIT
"""

import os
import asyncio
import aiohttp
import logging
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from urllib.parse import quote_plus, urlencode
import hashlib

logger = logging.getLogger('VerityDataSources')


# ============================================================
# BASE CLASSES
# ============================================================

@dataclass
class SourceResult:
    """Result from a data source"""
    source_name: str
    source_type: str
    relevance: float  # 0-1
    title: str
    content: str
    url: Optional[str] = None
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    credibility_score: float = 0.5


class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, session: aiohttp.ClientSession = None):
        self._session = session
        self._own_session = False
        
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            self._own_session = True
        return self._session
    
    async def close(self):
        if self._own_session and self._session:
            await self._session.close()
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        pass
    
    @property
    def is_available(self) -> bool:
        return True
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        pass


# ============================================================
# ACADEMIC SOURCES
# ============================================================

class SemanticScholarSource(DataSource):
    """
    Semantic Scholar - Free academic paper search
    https://www.semanticscholar.org/
    
    Rate limit: 100 requests per 5 minutes for public API
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    @property
    def name(self) -> str:
        return "Semantic Scholar"
    
    @property
    def source_type(self) -> str:
        return "academic"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,abstract,authors,year,citationCount,url,venue"
            }
            
            async with session.get(
                f"{self.BASE_URL}/paper/search",
                params=params
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for paper in data.get("data", []):
                    # Calculate relevance based on citations
                    citations = paper.get("citationCount", 0)
                    relevance = min(1.0, citations / 1000) * 0.5 + 0.5
                    
                    authors = [a.get("name", "") for a in paper.get("authors", [])]
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=relevance,
                        title=paper.get("title", ""),
                        content=paper.get("abstract", "")[:500] if paper.get("abstract") else "",
                        url=paper.get("url"),
                        author=", ".join(authors[:3]),
                        metadata={
                            "year": paper.get("year"),
                            "citations": citations,
                            "venue": paper.get("venue")
                        },
                        credibility_score=0.9  # Academic papers are highly credible
                    ))
                    
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed: {e}")
        
        return results


class PubMedSource(DataSource):
    """
    PubMed - Free medical/biomedical literature
    https://pubmed.ncbi.nlm.nih.gov/
    
    NCBI E-utilities API (free, rate limited)
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    @property
    def name(self) -> str:
        return "PubMed"
    
    @property
    def source_type(self) -> str:
        return "medical"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            # First, search for PMIDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": limit,
                "retmode": "json"
            }
            
            async with session.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=search_params
            ) as resp:
                if resp.status != 200:
                    return results
                
                search_data = await resp.json()
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                return results
            
            # Fetch details for each PMID
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }
            
            async with session.get(
                f"{self.BASE_URL}/esummary.fcgi",
                params=fetch_params
            ) as resp:
                if resp.status != 200:
                    return results
                
                fetch_data = await resp.json()
                articles = fetch_data.get("result", {})
            
            for pmid in pmids:
                if pmid not in articles:
                    continue
                    
                article = articles[pmid]
                
                authors = article.get("authors", [])
                author_names = [a.get("name", "") for a in authors[:3]]
                
                results.append(SourceResult(
                    source_name=self.name,
                    source_type=self.source_type,
                    relevance=0.8,  # Medical literature is highly relevant for health claims
                    title=article.get("title", ""),
                    content=article.get("title", ""),  # Abstract requires separate fetch
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    author=", ".join(author_names),
                    metadata={
                        "pmid": pmid,
                        "journal": article.get("fulljournalname"),
                        "pubdate": article.get("pubdate")
                    },
                    credibility_score=0.95  # Peer-reviewed medical research
                ))
                
        except Exception as e:
            logger.warning(f"PubMed search failed: {e}")
        
        return results


class ArxivSource(DataSource):
    """
    arXiv - Free preprint server for scientific papers
    https://arxiv.org/
    
    Open API, no authentication required
    """
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    @property
    def name(self) -> str:
        return "arXiv"
    
    @property
    def source_type(self) -> str:
        return "preprint"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit
            }
            
            async with session.get(
                self.BASE_URL,
                params=params
            ) as resp:
                if resp.status != 200:
                    return results
                
                text = await resp.text()
                
                # Parse Atom XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(text)
                
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    link = entry.find("atom:id", ns)
                    published = entry.find("atom:published", ns)
                    
                    authors = []
                    for author in entry.findall("atom:author", ns):
                        name = author.find("atom:name", ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.7,
                        title=title.text.strip() if title is not None else "",
                        content=summary.text.strip()[:500] if summary is not None else "",
                        url=link.text if link is not None else None,
                        published_date=datetime.fromisoformat(published.text.replace("Z", "+00:00")) if published is not None else None,
                        author=", ".join(authors[:3]),
                        metadata={"preprint": True},
                        credibility_score=0.75  # Preprints not peer-reviewed
                    ))
                    
        except Exception as e:
            logger.warning(f"arXiv search failed: {e}")
        
        return results


class CrossRefSource(DataSource):
    """
    CrossRef - DOI registration agency with citation metadata
    https://www.crossref.org/
    
    Free API with polite pool
    """
    
    BASE_URL = "https://api.crossref.org/works"
    
    @property
    def name(self) -> str:
        return "CrossRef"
    
    @property
    def source_type(self) -> str:
        return "citation"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            params = {
                "query": query,
                "rows": limit,
                "select": "title,author,DOI,URL,published-print,container-title,is-referenced-by-count"
            }
            
            headers = {
                "User-Agent": "VeritySystems/1.0 (mailto:contact@verity-systems.com)"
            }
            
            async with session.get(
                self.BASE_URL,
                params=params,
                headers=headers
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for item in data.get("message", {}).get("items", []):
                    title = item.get("title", [""])[0] if item.get("title") else ""
                    
                    authors = []
                    for author in item.get("author", [])[:3]:
                        name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                        if name:
                            authors.append(name)
                    
                    citations = item.get("is-referenced-by-count", 0)
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=min(1.0, citations / 500) * 0.5 + 0.5,
                        title=title,
                        content="",  # CrossRef doesn't provide abstracts
                        url=item.get("URL"),
                        author=", ".join(authors),
                        metadata={
                            "doi": item.get("DOI"),
                            "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                            "citations": citations
                        },
                        credibility_score=0.85
                    ))
                    
        except Exception as e:
            logger.warning(f"CrossRef search failed: {e}")
        
        return results


# ============================================================
# NEWS & MEDIA SOURCES
# ============================================================

class NewsAPISource(DataSource):
    """
    NewsAPI.org - News aggregator
    https://newsapi.org/
    
    Free tier: 100 requests/day, 1 month old articles
    """
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, session: aiohttp.ClientSession = None):
        super().__init__(session)
        self.api_key = os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
    
    @property
    def name(self) -> str:
        return "NewsAPI"
    
    @property
    def source_type(self) -> str:
        return "news"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        if not self.is_available:
            return []
        
        session = await self.get_session()
        results = []
        
        try:
            params = {
                "q": query,
                "pageSize": limit,
                "sortBy": "relevancy",
                "language": "en"
            }
            
            headers = {
                "X-Api-Key": self.api_key
            }
            
            async with session.get(
                f"{self.BASE_URL}/everything",
                params=params,
                headers=headers
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for article in data.get("articles", []):
                    source = article.get("source", {})
                    
                    # Estimate credibility based on source
                    source_name = source.get("name", "").lower()
                    credibility = 0.6
                    if any(s in source_name for s in ["reuters", "ap", "bbc", "npr", "pbs"]):
                        credibility = 0.9
                    elif any(s in source_name for s in ["cnn", "nytimes", "washington post", "guardian"]):
                        credibility = 0.8
                    
                    pub_date = None
                    if article.get("publishedAt"):
                        try:
                            pub_date = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                        except:
                            pass
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.7,
                        title=article.get("title", ""),
                        content=article.get("description", "")[:500] or article.get("content", "")[:500],
                        url=article.get("url"),
                        published_date=pub_date,
                        author=article.get("author"),
                        metadata={
                            "news_source": source.get("name"),
                            "source_id": source.get("id")
                        },
                        credibility_score=credibility
                    ))
                    
        except Exception as e:
            logger.warning(f"NewsAPI search failed: {e}")
        
        return results


class MediaStackSource(DataSource):
    """
    MediaStack - News API with free tier
    https://mediastack.com/
    
    Free tier: 500 requests/month
    """
    
    BASE_URL = "http://api.mediastack.com/v1/news"
    
    def __init__(self, session: aiohttp.ClientSession = None):
        super().__init__(session)
        self.api_key = os.getenv("MEDIASTACK_API_KEY")
    
    @property
    def name(self) -> str:
        return "MediaStack"
    
    @property
    def source_type(self) -> str:
        return "news"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        if not self.is_available:
            return []
        
        session = await self.get_session()
        results = []
        
        try:
            params = {
                "access_key": self.api_key,
                "keywords": query,
                "limit": limit,
                "languages": "en"
            }
            
            async with session.get(
                self.BASE_URL,
                params=params
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for article in data.get("data", []):
                    pub_date = None
                    if article.get("published_at"):
                        try:
                            pub_date = datetime.fromisoformat(article["published_at"].replace("Z", "+00:00"))
                        except:
                            pass
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.65,
                        title=article.get("title", ""),
                        content=article.get("description", "")[:500],
                        url=article.get("url"),
                        published_date=pub_date,
                        author=article.get("author"),
                        metadata={
                            "news_source": article.get("source"),
                            "category": article.get("category"),
                            "country": article.get("country")
                        },
                        credibility_score=0.6
                    ))
                    
        except Exception as e:
            logger.warning(f"MediaStack search failed: {e}")
        
        return results


# ============================================================
# KNOWLEDGE BASES
# ============================================================

class WikidataSource(DataSource):
    """
    Wikidata - Structured knowledge base
    https://www.wikidata.org/
    
    Free, no authentication required
    """
    
    BASE_URL = "https://www.wikidata.org/w/api.php"
    SPARQL_URL = "https://query.wikidata.org/sparql"
    
    @property
    def name(self) -> str:
        return "Wikidata"
    
    @property
    def source_type(self) -> str:
        return "knowledge_base"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            # Use wbsearchentities for entity search
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "limit": limit,
                "format": "json"
            }
            
            async with session.get(
                self.BASE_URL,
                params=params
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for entity in data.get("search", []):
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.8,
                        title=entity.get("label", ""),
                        content=entity.get("description", ""),
                        url=entity.get("concepturi"),
                        metadata={
                            "entity_id": entity.get("id"),
                            "aliases": entity.get("aliases", [])
                        },
                        credibility_score=0.85  # Wikidata is community-verified
                    ))
                    
        except Exception as e:
            logger.warning(f"Wikidata search failed: {e}")
        
        return results
    
    async def get_entity_facts(self, entity_id: str) -> Dict[str, Any]:
        """Get structured facts about an entity"""
        session = await self.get_session()
        
        try:
            params = {
                "action": "wbgetentities",
                "ids": entity_id,
                "format": "json",
                "languages": "en"
            }
            
            async with session.get(
                self.BASE_URL,
                params=params
            ) as resp:
                if resp.status != 200:
                    return {}
                
                data = await resp.json()
                entity = data.get("entities", {}).get(entity_id, {})
                
                claims = entity.get("claims", {})
                labels = entity.get("labels", {})
                descriptions = entity.get("descriptions", {})
                
                return {
                    "id": entity_id,
                    "label": labels.get("en", {}).get("value"),
                    "description": descriptions.get("en", {}).get("value"),
                    "claims_count": len(claims),
                    "properties": list(claims.keys())[:20]
                }
                
        except Exception as e:
            logger.warning(f"Wikidata entity fetch failed: {e}")
            return {}


class DBpediaSource(DataSource):
    """
    DBpedia - Structured data extracted from Wikipedia
    https://dbpedia.org/
    
    Free SPARQL endpoint
    """
    
    SPARQL_URL = "https://dbpedia.org/sparql"
    
    @property
    def name(self) -> str:
        return "DBpedia"
    
    @property
    def source_type(self) -> str:
        return "knowledge_base"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            # Simple text search using SPARQL
            sparql_query = f"""
            SELECT DISTINCT ?subject ?label ?abstract WHERE {{
                ?subject rdfs:label ?label .
                ?subject dbo:abstract ?abstract .
                FILTER (lang(?label) = 'en')
                FILTER (lang(?abstract) = 'en')
                FILTER (CONTAINS(LCASE(?label), LCASE("{query}")))
            }}
            LIMIT {limit}
            """
            
            params = {
                "query": sparql_query,
                "format": "application/json"
            }
            
            async with session.get(
                self.SPARQL_URL,
                params=params,
                headers={"Accept": "application/json"}
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for binding in data.get("results", {}).get("bindings", []):
                    abstract = binding.get("abstract", {}).get("value", "")
                    
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.75,
                        title=binding.get("label", {}).get("value", ""),
                        content=abstract[:500],
                        url=binding.get("subject", {}).get("value"),
                        metadata={
                            "full_abstract_length": len(abstract)
                        },
                        credibility_score=0.8
                    ))
                    
        except Exception as e:
            logger.warning(f"DBpedia search failed: {e}")
        
        return results


# ============================================================
# GOVERNMENT & OFFICIAL SOURCES
# ============================================================

class WHOSource(DataSource):
    """
    World Health Organization - Health information
    https://www.who.int/
    
    Free API for health data
    """
    
    BASE_URL = "https://ghoapi.azureedge.net/api"
    
    @property
    def name(self) -> str:
        return "WHO"
    
    @property
    def source_type(self) -> str:
        return "official"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        session = await self.get_session()
        results = []
        
        try:
            # Search indicators
            async with session.get(
                f"{self.BASE_URL}/Indicator",
                params={"$filter": f"contains(IndicatorName, '{query}')"}
            ) as resp:
                if resp.status != 200:
                    return results
                
                data = await resp.json()
                
                for indicator in data.get("value", [])[:limit]:
                    results.append(SourceResult(
                        source_name=self.name,
                        source_type=self.source_type,
                        relevance=0.85,
                        title=indicator.get("IndicatorName", ""),
                        content=f"WHO Health Indicator: {indicator.get('IndicatorName', '')}",
                        url=f"https://www.who.int/data/gho/indicator-metadata-registry/{indicator.get('IndicatorCode', '')}",
                        metadata={
                            "indicator_code": indicator.get("IndicatorCode"),
                            "language": indicator.get("Language")
                        },
                        credibility_score=0.98  # Official WHO data
                    ))
                    
        except Exception as e:
            logger.warning(f"WHO search failed: {e}")
        
        return results


class CDCSource(DataSource):
    """
    Centers for Disease Control and Prevention - US health data
    https://www.cdc.gov/
    
    Free API for health statistics
    """
    
    BASE_URL = "https://data.cdc.gov/resource"
    
    @property
    def name(self) -> str:
        return "CDC"
    
    @property
    def source_type(self) -> str:
        return "official"
    
    async def search(self, query: str, limit: int = 10) -> List[SourceResult]:
        # CDC uses dataset-specific endpoints
        # This is a simplified implementation
        session = await self.get_session()
        results = []
        
        # Return informational result pointing to CDC
        results.append(SourceResult(
            source_name=self.name,
            source_type=self.source_type,
            relevance=0.8,
            title=f"CDC Data on: {query}",
            content="For authoritative health information, consult the CDC website directly.",
            url=f"https://www.cdc.gov/search/?query={quote_plus(query)}",
            metadata={},
            credibility_score=0.98
        ))
        
        return results


# ============================================================
# FACT-CHECK AGGREGATOR
# ============================================================

class FactCheckAggregator:
    """
    Aggregate results from multiple fact-checking sources.
    """
    
    def __init__(self, session: aiohttp.ClientSession = None):
        self.sources: List[DataSource] = [
            # Academic
            SemanticScholarSource(session),
            PubMedSource(session),
            ArxivSource(session),
            CrossRefSource(session),
            
            # News
            NewsAPISource(session),
            MediaStackSource(session),
            
            # Knowledge bases
            WikidataSource(session),
            DBpediaSource(session),
            
            # Official
            WHOSource(session),
            CDCSource(session),
        ]
    
    def get_available_sources(self) -> List[str]:
        """Get list of available sources"""
        return [s.name for s in self.sources if s.is_available]
    
    async def search_all(
        self,
        query: str,
        limit_per_source: int = 5,
        source_types: List[str] = None
    ) -> List[SourceResult]:
        """
        Search all sources in parallel.
        
        Args:
            query: Search query
            limit_per_source: Max results per source
            source_types: Filter by source types (academic, news, etc.)
        """
        tasks = []
        
        for source in self.sources:
            if not source.is_available:
                continue
            if source_types and source.source_type not in source_types:
                continue
            
            tasks.append(source.search(query, limit_per_source))
        
        if not tasks:
            return []
        
        # Gather with timeout
        try:
            all_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30
            )
        except asyncio.TimeoutError:
            logger.warning("Source search timed out")
            return []
        
        # Flatten and filter results
        results = []
        for result_set in all_results:
            if isinstance(result_set, Exception):
                logger.warning(f"Source error: {result_set}")
                continue
            results.extend(result_set)
        
        # Sort by relevance and credibility
        results.sort(key=lambda r: r.relevance * r.credibility_score, reverse=True)
        
        return results
    
    async def get_evidence_for_claim(
        self,
        claim: str,
        min_credibility: float = 0.6
    ) -> Dict[str, Any]:
        """
        Get supporting/refuting evidence for a claim.
        
        Returns structured evidence report.
        """
        results = await self.search_all(claim, limit_per_source=3)
        
        # Filter by credibility
        credible_results = [r for r in results if r.credibility_score >= min_credibility]
        
        # Categorize by source type
        by_type = {}
        for result in credible_results:
            if result.source_type not in by_type:
                by_type[result.source_type] = []
            by_type[result.source_type].append({
                "source": result.source_name,
                "title": result.title,
                "content": result.content[:200],
                "url": result.url,
                "credibility": result.credibility_score
            })
        
        # Calculate overall evidence strength
        if not credible_results:
            evidence_strength = 0
        else:
            avg_credibility = sum(r.credibility_score for r in credible_results) / len(credible_results)
            source_diversity = len(set(r.source_type for r in credible_results)) / 5  # Max 5 types
            evidence_strength = avg_credibility * 0.6 + source_diversity * 0.4
        
        return {
            "claim": claim,
            "evidence_count": len(credible_results),
            "evidence_strength": round(evidence_strength, 3),
            "by_source_type": by_type,
            "top_sources": [
                {
                    "source": r.source_name,
                    "title": r.title,
                    "url": r.url,
                    "credibility": r.credibility_score
                }
                for r in credible_results[:5]
            ]
        }
    
    async def close(self):
        """Close all source connections"""
        for source in self.sources:
            await source.close()


# ============================================================
# MAIN / TESTING
# ============================================================

async def main():
    """Test data sources"""
    
    aggregator = FactCheckAggregator()
    
    print("Available sources:", aggregator.get_available_sources())
    
    test_claims = [
        "Climate change is caused by human activities",
        "COVID-19 vaccines are safe and effective",
        "The Earth orbits the Sun"
    ]
    
    for claim in test_claims:
        print(f"\n{'='*60}")
        print(f"Claim: {claim}")
        print(f"{'='*60}")
        
        evidence = await aggregator.get_evidence_for_claim(claim)
        
        print(f"Evidence count: {evidence['evidence_count']}")
        print(f"Evidence strength: {evidence['evidence_strength']}")
        print(f"\nTop sources:")
        for source in evidence['top_sources']:
            print(f"  - {source['source']}: {source['title'][:60]}...")
            print(f"    Credibility: {source['credibility']}")
    
    await aggregator.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
