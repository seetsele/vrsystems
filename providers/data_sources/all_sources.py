"""
PART 6: ALL DATA SOURCES - COMPLETE IMPLEMENTATION
Fact-checkers, Academic APIs, Search Engines, News APIs - NOTHING SKIPPED
"""

import os
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class SourceResult:
    """Result from a data source"""
    source_name: str
    title: str
    url: str
    snippet: str
    relevance_score: float
    pub_date: Optional[str] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseDataSource(ABC):
    """Base class for all data sources"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.session = None
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search for information"""
        pass


# ============================================================
# FACT-CHECKING SOURCES
# ============================================================

class ClaimBusterAPI(BaseDataSource):
    """ClaimBuster - AI-powered claim detection"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ClaimBuster", api_key or os.getenv('CLAIMBUSTER_API_KEY'))
        self.base_url = "https://idir.uta.edu/claimbuster/api/v2"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Check if text contains checkworthy claims"""
        await self.initialize()
        
        url = f"{self.base_url}/score/text"
        
        async with self.session.post(
            url,
            json={"input_text": query},
            headers={"x-api-key": self.api_key}
        ) as response:
            data = await response.json()
        
        results = []
        for result in data.get('results', [])[:max_results]:
            results.append(SourceResult(
                source_name="ClaimBuster",
                title=f"Claim Score: {result['score']:.2f}",
                url=self.base_url,
                snippet=result['text'],
                relevance_score=result['score'],
                metadata={'checkworthy': result['score'] > 0.5}
            ))
        
        return results


class FactCheckOrgScraper(BaseDataSource):
    """FactCheck.org - Nonpartisan fact-checking"""
    
    def __init__(self):
        super().__init__("FactCheck.org")
        self.base_url = "https://www.factcheck.org"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search FactCheck.org articles"""
        await self.initialize()
        
        search_url = f"{self.base_url}/?s={query}"
        
        async with self.session.get(search_url) as response:
            html = await response.text()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        articles = soup.find_all('article', class_='item-list', limit=max_results)
        
        for article in articles:
            title_elem = article.find('h3', class_='entry-title')
            if not title_elem:
                continue
            
            link = title_elem.find('a')
            snippet_elem = article.find('div', class_='entry-content')
            
            results.append(SourceResult(
                source_name="FactCheck.org",
                title=title_elem.get_text(strip=True),
                url=link['href'] if link else '',
                snippet=snippet_elem.get_text(strip=True)[:300] if snippet_elem else '',
                relevance_score=0.9,  # High credibility
                metadata={'credibility': 'high'}
            ))
        
        return results


class PolitiFactScraper(BaseDataSource):
    """PolitiFact - Pulitzer Prize-winning fact-checking"""
    
    def __init__(self):
        super().__init__("PolitiFact")
        self.base_url = "https://www.politifact.com"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search PolitiFact fact-checks"""
        await self.initialize()
        
        search_url = f"{self.base_url}/search/?q={query}"
        
        async with self.session.get(search_url) as response:
            html = await response.text()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        statements = soup.find_all('div', class_='m-statement', limit=max_results)
        
        for statement in statements:
            title_elem = statement.find('div', class_='m-statement__quote')
            link_elem = statement.find('a')
            meter_elem = statement.find('div', class_='m-statement__meter')
            
            if not title_elem:
                continue
            
            results.append(SourceResult(
                source_name="PolitiFact",
                title=title_elem.get_text(strip=True),
                url=f"{self.base_url}{link_elem['href']}" if link_elem else '',
                snippet=title_elem.get_text(strip=True),
                relevance_score=0.95,
                metadata={
                    'credibility': 'very high',
                    'rating': meter_elem.get_text(strip=True) if meter_elem else None
                }
            ))
        
        return results


class SnopesScraper(BaseDataSource):
    """Snopes - Oldest and largest fact-checking site"""
    
    def __init__(self):
        super().__init__("Snopes")
        self.base_url = "https://www.snopes.com"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search Snopes fact-checks"""
        await self.initialize()
        
        search_url = f"{self.base_url}/?s={query}"
        
        async with self.session.get(search_url) as response:
            html = await response.text()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        articles = soup.find_all('article', limit=max_results)
        
        for article in articles:
            title_elem = article.find('h2')
            link_elem = article.find('a')
            snippet_elem = article.find('p')
            rating_elem = article.find('span', class_='rating')
            
            if not title_elem:
                continue
            
            results.append(SourceResult(
                source_name="Snopes",
                title=title_elem.get_text(strip=True),
                url=link_elem['href'] if link_elem else '',
                snippet=snippet_elem.get_text(strip=True) if snippet_elem else '',
                relevance_score=0.92,
                metadata={
                    'credibility': 'high',
                    'rating': rating_elem.get_text(strip=True) if rating_elem else None
                }
            ))
        
        return results


# ============================================================
# ACADEMIC & RESEARCH SOURCES
# ============================================================

class ArXivAPI(BaseDataSource):
    """arXiv - Preprint repository for scientific papers"""
    
    def __init__(self):
        super().__init__("arXiv")
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search arXiv papers"""
        await self.initialize()
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance'
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            xml = await response.text()
        
        from xml.etree import ElementTree as ET
        root = ET.fromstring(xml)
        
        results = []
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            link = entry.find('atom:id', ns)
            authors = entry.findall('atom:author/atom:name', ns)
            
            results.append(SourceResult(
                source_name="arXiv",
                title=title.text.strip() if title is not None else '',
                url=link.text if link is not None else '',
                snippet=summary.text.strip()[:300] if summary is not None else '',
                relevance_score=0.85,
                pub_date=published.text if published is not None else None,
                author=', '.join(a.text for a in authors) if authors else None,
                metadata={'source_type': 'academic'}
            ))
        
        return results


class PubMedAPI(BaseDataSource):
    """PubMed - Biomedical literature database"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("PubMed", api_key or os.getenv('NCBI_API_KEY'))
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search PubMed articles"""
        await self.initialize()
        
        # Search for article IDs
        search_url = f"{self.base_url}/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'api_key': self.api_key
        }
        
        async with self.session.get(search_url, params=search_params) as response:
            search_data = await response.json()
        
        id_list = search_data.get('esearchresult', {}).get('idlist', [])
        
        if not id_list:
            return []
        
        # Fetch article details
        fetch_url = f"{self.base_url}/esummary.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'json',
            'api_key': self.api_key
        }
        
        async with self.session.get(fetch_url, params=fetch_params) as response:
            fetch_data = await response.json()
        
        results = []
        for pmid in id_list:
            article = fetch_data.get('result', {}).get(pmid, {})
            
            if not article:
                continue
            
            results.append(SourceResult(
                source_name="PubMed",
                title=article.get('title', ''),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                snippet=article.get('title', '')[:300],
                relevance_score=0.9,
                pub_date=article.get('pubdate'),
                author=', '.join(a['name'] for a in article.get('authors', [])[:3]),
                metadata={'pmid': pmid, 'source_type': 'academic'}
            ))
        
        return results


class SemanticScholarAPI(BaseDataSource):
    """Semantic Scholar - AI-powered research tool"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Semantic Scholar", api_key or os.getenv('S2_API_KEY'))
        self.base_url = "https://api.semanticscholar.org/graph/v1"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search academic papers"""
        await self.initialize()
        
        url = f"{self.base_url}/paper/search"
        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,abstract,url,year,authors,citationCount'
        }
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        async with self.session.get(url, params=params, headers=headers) as response:
            data = await response.json()
        
        results = []
        for paper in data.get('data', []):
            authors = ', '.join(a['name'] for a in paper.get('authors', [])[:3])
            
            # Calculate relevance score based on citations
            citations = paper.get('citationCount', 0)
            relevance = min(0.95, 0.5 + (citations / 1000))
            
            results.append(SourceResult(
                source_name="Semantic Scholar",
                title=paper.get('title', ''),
                url=paper.get('url', ''),
                snippet=paper.get('abstract', '')[:300],
                relevance_score=relevance,
                pub_date=str(paper.get('year')),
                author=authors,
                metadata={
                    'citations': citations,
                    'source_type': 'academic'
                }
            ))
        
        return results


class GoogleScholarScraper(BaseDataSource):
    """Google Scholar - Academic search engine"""
    
    def __init__(self):
        super().__init__("Google Scholar")
        self.base_url = "https://scholar.google.com/scholar"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search Google Scholar (requires scraping)"""
        await self.initialize()
        
        params = {'q': query, 'hl': 'en'}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with self.session.get(self.base_url, params=params, headers=headers) as response:
            html = await response.text()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        papers = soup.find_all('div', class_='gs_ri', limit=max_results)
        
        for paper in papers:
            title_elem = paper.find('h3', class_='gs_rt')
            snippet_elem = paper.find('div', class_='gs_rs')
            authors_elem = paper.find('div', class_='gs_a')
            
            if not title_elem:
                continue
            
            link = title_elem.find('a')
            
            results.append(SourceResult(
                source_name="Google Scholar",
                title=title_elem.get_text(strip=True),
                url=link['href'] if link and 'href' in link.attrs else '',
                snippet=snippet_elem.get_text(strip=True) if snippet_elem else '',
                relevance_score=0.85,
                author=authors_elem.get_text(strip=True).split('-')[0] if authors_elem else None,
                metadata={'source_type': 'academic'}
            ))
        
        return results


# ============================================================
# NEWS & MEDIA SOURCES
# ============================================================

class NewsAPIOrg(BaseDataSource):
    """NewsAPI - News aggregation API"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("NewsAPI", api_key or os.getenv('NEWS_API_KEY'))
        self.base_url = "https://newsapi.org/v2"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search news articles"""
        await self.initialize()
        
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'pageSize': max_results,
            'sortBy': 'relevancy',
            'apiKey': self.api_key
        }
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
        
        results = []
        for article in data.get('articles', []):
            results.append(SourceResult(
                source_name=f"NewsAPI ({article.get('source', {}).get('name', 'Unknown')})",
                title=article.get('title', ''),
                url=article.get('url', ''),
                snippet=article.get('description', '') or article.get('content', '')[:300],
                relevance_score=0.75,
                pub_date=article.get('publishedAt'),
                author=article.get('author'),
                metadata={'source_type': 'news'}
            ))
        
        return results


class WikipediaAPI(BaseDataSource):
    """Wikipedia - Free encyclopedia"""
    
    def __init__(self):
        super().__init__("Wikipedia")
        self.base_url = "https://en.wikipedia.org/w/api.php"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search Wikipedia articles"""
        await self.initialize()
        
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': max_results,
            'format': 'json'
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
        
        results = []
        for item in data.get('query', {}).get('search', []):
            page_id = item['pageid']
            
            results.append(SourceResult(
                source_name="Wikipedia",
                title=item['title'],
                url=f"https://en.wikipedia.org/?curid={page_id}",
                snippet=item['snippet'].replace('<span class="searchmatch">', '').replace('</span>', ''),
                relevance_score=0.8,
                metadata={'page_id': page_id, 'source_type': 'encyclopedia'}
            ))
        
        return results


# ============================================================
# SEARCH ENGINES
# ============================================================

class DuckDuckGoSearch(BaseDataSource):
    """DuckDuckGo - Privacy-focused search"""
    
    def __init__(self):
        super().__init__("DuckDuckGo")
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search using DuckDuckGo"""
        from duckduckgo_search import AsyncDDGS
        
        results = []
        
        async with AsyncDDGS() as ddgs:
            search_results = await ddgs.text(query, max_results=max_results)
            
            for item in search_results:
                results.append(SourceResult(
                    source_name="DuckDuckGo",
                    title=item.get('title', ''),
                    url=item.get('href', ''),
                    snippet=item.get('body', ''),
                    relevance_score=0.7,
                    metadata={'source_type': 'web'}
                ))
        
        return results


class BraveSearchAPI(BaseDataSource):
    """Brave Search - Privacy-first search API"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Brave Search", api_key or os.getenv('BRAVE_API_KEY'))
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search using Brave Search API"""
        await self.initialize()
        
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
        }
        
        params = {
            'q': query,
            'count': max_results
        }
        
        async with self.session.get(self.base_url, params=params, headers=headers) as response:
            data = await response.json()
        
        results = []
        for item in data.get('web', {}).get('results', []):
            results.append(SourceResult(
                source_name="Brave Search",
                title=item.get('title', ''),
                url=item.get('url', ''),
                snippet=item.get('description', ''),
                relevance_score=0.75,
                metadata={'source_type': 'web'}
            ))
        
        return results


# ============================================================
# GOVERNMENT & OFFICIAL SOURCES
# ============================================================

class DataGovAPI(BaseDataSource):
    """Data.gov - US Government open data"""
    
    def __init__(self):
        super().__init__("Data.gov")
        self.base_url = "https://catalog.data.gov/api/3/action/package_search"
    
    async def search(self, query: str, max_results: int = 10) -> List[SourceResult]:
        """Search government datasets"""
        await self.initialize()
        
        params = {
            'q': query,
            'rows': max_results
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
        
        results = []
        for dataset in data.get('result', {}).get('results', []):
            results.append(SourceResult(
                source_name="Data.gov",
                title=dataset.get('title', ''),
                url=f"https://catalog.data.gov/dataset/{dataset.get('name', '')}",
                snippet=dataset.get('notes', '')[:300],
                relevance_score=0.88,
                metadata={
                    'organization': dataset.get('organization', {}).get('title'),
                    'source_type': 'government'
                }
            ))
        
        return results


# ============================================================
# DATA SOURCE AGGREGATOR
# ============================================================

class DataSourceAggregator:
    """Aggregate results from multiple data sources"""
    
    def __init__(self):
        # Build sources with defensive guards so missing optional libs don't break initialization
        sources = {}

        def _safe_add(key, ctor):
            try:
                sources[key] = ctor()
            except Exception as e:
                print(f"[WARN] Data source '{key}' initialization failed: {e}")

        # Fact-checkers
        _safe_add('factcheck', FactCheckOrgScraper)
        _safe_add('politifact', PolitiFactScraper)
        _safe_add('snopes', SnopesScraper)

        # Academic
        _safe_add('arxiv', ArXivAPI)
        _safe_add('pubmed', PubMedAPI)
        _safe_add('semantic_scholar', SemanticScholarAPI)
        _safe_add('google_scholar', GoogleScholarScraper)

        # News
        _safe_add('newsapi', NewsAPIOrg)
        _safe_add('wikipedia', WikipediaAPI)

        # Search
        _safe_add('duckduckgo', DuckDuckGoSearch)
        _safe_add('brave', BraveSearchAPI)

        # Government
        _safe_add('datagov', DataGovAPI)

        self.sources = sources
    
    async def search_all(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        max_per_source: int = 5
    ) -> Dict[str, List[SourceResult]]:
        """Search across multiple sources"""
        
        if source_types is None:
            source_types = list(self.sources.keys())
        
        tasks = {}
        for source_name in source_types:
            if source_name in self.sources:
                tasks[source_name] = self.sources[source_name].search(query, max_per_source)
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        aggregated = {}
        for source_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                print(f"⚠️ Error from {source_name}: {result}")
                aggregated[source_name] = []
            else:
                aggregated[source_name] = result
        
        return aggregated
    
    async def search_priority(
        self,
        query: str,
        priority_sources: List[str],
        max_results: int = 20
    ) -> List[SourceResult]:
        """Search with priority ordering"""
        
        all_results = []
        
        for source_name in priority_sources:
            if source_name in self.sources:
                try:
                    results = await self.sources[source_name].search(query, max_results)
                    all_results.extend(results)
                    
                    if len(all_results) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error from {source_name}: {e}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return all_results[:max_results]
    
    async def close_all(self):
        """Close all data source sessions"""
        for source in self.sources.values():
            await source.close()


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def example_usage():
    """Example of using data source aggregator"""
    
    aggregator = DataSourceAggregator()
    
    query = "climate change causes"
    
    print("="*60)
    print(f"Searching: {query}")
    print("="*60)
    
    # Search across all sources
    results = await aggregator.search_all(
        query,
        source_types=['factcheck', 'arxiv', 'wikipedia', 'duckduckgo'],
        max_per_source=3
    )
    
    for source_name, source_results in results.items():
        print(f"\n{source_name.upper()} ({len(source_results)} results):")
        for i, result in enumerate(source_results, 1):
            print(f"  {i}. [{result.relevance_score:.2f}] {result.title[:60]}...")
            print(f"     {result.url}")
    
    # Clean up
    await aggregator.close_all()


if __name__ == "__main__":
    asyncio.run(example_usage())
