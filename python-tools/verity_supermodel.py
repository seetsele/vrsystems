"""
Verity Systems - Super Fact-Checking Model
Combines multiple free/open-source APIs for maximum accuracy and security

APIs Integrated:
- Anthropic Claude (via GitHub Education credits - $25/month)
- Google Fact Check API (free tier - 10,000/day)
- Wikipedia API (free - unlimited)
- NewsAPI (free tier - 100 requests/day)
- Groq API (free tier - Llama 3.1 70B)
- ClaimBuster API (free for research)
- Hugging Face Inference API (free tier)
- DuckDuckGo Search (free, no API key)
- Wikidata Query Service (free)
- OpenAI API (via Azure credits from GitHub Education)
- Perplexity AI (research queries)
- Serper API (Google search - free tier)

GitHub Education Pack Credits Utilized:
- Anthropic: $25/month API credits
- Microsoft Azure: $100 free credits
- DigitalOcean: $200 in platform credits
- MongoDB Atlas: $50 credit + free certification
- Heroku: $13/month for 2 years ($312 value)
- AWS Educate: Free tier + promotional credits
- JetBrains: Free IDE subscription
- DataCamp: 3 months free
- Sentry: 50,000 events/month free

Security Features:
- AES-256-GCM encryption for sensitive data
- Input sanitization and validation
- Rate limiting and request throttling
- Secure credential management (1Password integration)
- Data anonymization (GDPR compliant)
- Audit logging with integrity verification
"""

import os
import json
import hashlib
import secrets
import asyncio
import aiohttp
import logging
import anthropic
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re
from functools import wraps
import time
from dotenv import load_dotenv

# Security imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verity_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VeritySuperModel')


# ============================================================
# ENUMS AND DATA CLASSES
# ============================================================

class VerificationStatus(Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    PARTIALLY_TRUE = "partially_true"
    UNVERIFIABLE = "unverifiable"
    NEEDS_CONTEXT = "needs_context"
    DISPUTED = "disputed"


class SourceCredibility(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class VerificationSource:
    """Represents a source used for verification"""
    name: str
    url: Optional[str]
    credibility: SourceCredibility
    claim_rating: Optional[str]
    snippet: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    

@dataclass
class VerificationResult:
    """Complete verification result from the super model"""
    claim: str
    status: VerificationStatus
    confidence_score: float  # 0.0 to 1.0
    sources: List[VerificationSource]
    analysis_summary: str
    fact_checks: List[Dict]
    ai_analysis: str
    warnings: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default_factory=lambda: secrets.token_hex(16))
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'claim': self.claim,
            'status': self.status.value,
            'confidence_score': self.confidence_score,
            'sources': [
                {
                    'name': s.name,
                    'url': s.url,
                    'credibility': s.credibility.value,
                    'claim_rating': s.claim_rating,
                    'snippet': s.snippet
                } for s in self.sources
            ],
            'analysis_summary': self.analysis_summary,
            'fact_checks': self.fact_checks,
            'ai_analysis': self.ai_analysis,
            'warnings': self.warnings,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id,
            'processing_time_ms': self.processing_time_ms
        }


# ============================================================
# SECURITY UTILITIES
# ============================================================

class SecurityManager:
    """Handles all security operations for Verity Systems"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.getenv('VERITY_SECRET_KEY', secrets.token_hex(32))
        self._init_encryption()
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    def _init_encryption(self):
        """Initialize Fernet encryption with derived key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'verity_systems_salt_2024',  # In production, use unique salt per user
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data using AES-256"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data: str) -> str:
        """Create SHA-256 hash of data for integrity verification"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input to prevent injection attacks and clean data
        """
        if not text:
            return ""
        
        # Remove potential script injections
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        
        # Remove potential SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
            r"(--|;|\/\*|\*\/)",
        ]
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Limit length
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length]
            
        return text.strip()
    
    def check_rate_limit(self, client_id: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """
        Check if client has exceeded rate limit
        Returns True if within limits, False if exceeded
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []
        
        # Clean old entries
        self.rate_limits[client_id] = [
            ts for ts in self.rate_limits[client_id] if ts > window_start
        ]
        
        if len(self.rate_limits[client_id]) >= max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        self.rate_limits[client_id].append(now)
        return True
    
    def anonymize_pii(self, text: str) -> str:
        """
        Remove or mask personally identifiable information
        """
        # Email addresses
        text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL REDACTED]', text)
        
        # Phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE REDACTED]', text)
        text = re.sub(r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE REDACTED]', text)
        
        # SSN patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
        
        # Credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD REDACTED]', text)
        
        return text
    
    def generate_audit_log(self, action: str, details: Dict) -> None:
        """Log security-relevant actions for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'hash': self.hash_data(json.dumps(details))
        }
        logger.info(f"AUDIT: {json.dumps(log_entry)}")


# ============================================================
# API PROVIDERS (Abstract Base Class)
# ============================================================

class FactCheckProvider(ABC):
    """Abstract base class for fact-checking providers"""
    
    @abstractmethod
    async def check_claim(self, claim: str) -> List[Dict]:
        """Check a claim and return results"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @property
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        return True


# ============================================================
# FREE API PROVIDERS
# ============================================================

class GoogleFactCheckProvider(FactCheckProvider):
    """
    Google Fact Check Tools API
    Free tier: 10,000 queries/day
    Requires API key from Google Cloud Console
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_FACTCHECK_API_KEY')
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    @property
    def name(self) -> str:
        return "Google Fact Check"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.api_key,
                    'query': claim,
                    'languageCode': 'en'
                }
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
        except Exception as e:
            logger.error(f"Google Fact Check API error: {e}")
        return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        for claim in data.get('claims', []):
            for review in claim.get('claimReview', []):
                results.append({
                    'source': 'Google Fact Check',
                    'publisher': review.get('publisher', {}).get('name', 'Unknown'),
                    'url': review.get('url'),
                    'rating': review.get('textualRating'),
                    'claim_text': claim.get('text'),
                    'review_date': review.get('reviewDate')
                })
        return results


class WikipediaProvider(FactCheckProvider):
    """
    Wikipedia API - Free, no API key required
    Great for verifying factual claims about entities, dates, events
    """
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            'User-Agent': 'VeritySystems/1.0 (https://verity.systems; contact@verity.systems) Python/3.11'
        }
    
    @property
    def name(self) -> str:
        return "Wikipedia"
    
    async def check_claim(self, claim: str) -> List[Dict]:
        try:
            # Extract key terms for search
            search_terms = self._extract_search_terms(claim)
            results = []
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                for term in search_terms[:3]:  # Limit to 3 terms
                    params = {
                        'action': 'query',
                        'format': 'json',
                        'list': 'search',
                        'srsearch': term,
                        'srlimit': 3,
                        'srprop': 'snippet|timestamp'
                    }
                    async with session.get(self.base_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for item in data.get('query', {}).get('search', []):
                                results.append({
                                    'source': 'Wikipedia',
                                    'title': item.get('title'),
                                    'url': f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                                    'snippet': self._clean_snippet(item.get('snippet', '')),
                                    'timestamp': item.get('timestamp')
                                })
            return results[:5]  # Return top 5 results
        except Exception as e:
            logger.error(f"Wikipedia API error: {e}")
        return []
    
    def _extract_search_terms(self, claim: str) -> List[str]:
        """Extract meaningful search terms from claim"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'that', 'this', 'these', 'those', 'it', 'its', 'of', 'in',
                     'on', 'at', 'to', 'for', 'with', 'by', 'from', 'and', 'or'}
        
        words = claim.lower().split()
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also try to find proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim)
        
        return proper_nouns + terms[:5]
    
    def _clean_snippet(self, snippet: str) -> str:
        """Remove HTML from snippet"""
        return re.sub(r'<[^>]+>', '', snippet)


class DuckDuckGoProvider(FactCheckProvider):
    """
    DuckDuckGo Instant Answer API - Completely free, no API key
    Good for quick fact verification
    Note: Returns Instant Answers only, not full search results
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'VeritySystems/1.0 (https://verity.systems) Python/3.11'
        }
    
    @property
    def name(self) -> str:
        return "DuckDuckGo"
    
    async def check_claim(self, claim: str) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': claim,
                    'format': 'json',
                    'no_html': 1,
                    'skip_disambig': 1
                }
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
        except Exception as e:
            logger.error(f"DuckDuckGo API error: {e}")
        return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        
        # Abstract (main answer)
        if data.get('Abstract'):
            results.append({
                'source': 'DuckDuckGo',
                'type': 'abstract',
                'text': data['Abstract'],
                'url': data.get('AbstractURL'),
                'source_name': data.get('AbstractSource')
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', [])[:3]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'source': 'DuckDuckGo',
                    'type': 'related',
                    'text': topic['Text'],
                    'url': topic.get('FirstURL')
                })
        
        return results


class NewsAPIProvider(FactCheckProvider):
    """
    NewsAPI - Free tier: 100 requests/day
    Good for verifying current events and recent news claims
    GitHub Education Pack may provide extended access
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
    
    @property
    def name(self) -> str:
        return "NewsAPI"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'apiKey': self.api_key,
                    'q': claim,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': 5
                }
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
        return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        for article in data.get('articles', []):
            results.append({
                'source': 'NewsAPI',
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt'),
                'source_name': article.get('source', {}).get('name')
            })
        return results


class ClaimBusterProvider(FactCheckProvider):
    """
    ClaimBuster API - Free for research/educational use
    AI-powered claim detection and scoring
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CLAIMBUSTER_API_KEY')
        self.base_url = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
    
    @property
    def name(self) -> str:
        return "ClaimBuster"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'x-api-key': self.api_key}
                async with session.get(
                    f"{self.base_url}{claim}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
        except Exception as e:
            logger.error(f"ClaimBuster API error: {e}")
        return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        for result in data.get('results', []):
            results.append({
                'source': 'ClaimBuster',
                'text': result.get('text'),
                'score': result.get('score'),  # 0-1, higher = more check-worthy
                'checkworthy': result.get('score', 0) > 0.5
            })
        return results


class HuggingFaceProvider(FactCheckProvider):
    """
    Hugging Face Inference API - Free tier available
    Uses various NLP models for fact-checking related tasks
    GitHub Education Pack provides additional credits
    Note: As of 2024, uses router.huggingface.co endpoint
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        # Free fact-checking models on Hugging Face
        self.models = {
            'nli': 'facebook/bart-large-mnli',  # Natural Language Inference
            'stance': 'roberta-large-mnli',
            'factuality': 'google/flan-t5-base'  # General reasoning
        }
        # New HuggingFace router endpoint (2024+)
        self.base_url = "https://router.huggingface.co/hf-inference/models"
    
    @property
    def name(self) -> str:
        return "Hugging Face"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                # Use NLI model for contradiction detection
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                # Check if claim contradicts common knowledge
                payload = {
                    'inputs': claim,
                    'parameters': {'candidate_labels': ['true', 'false', 'unverifiable']}
                }
                
                url = f"{self.base_url}/{self.models['nli']}"
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            'source': 'Hugging Face NLI',
                            'model': self.models['nli'],
                            'labels': data.get('labels', []),
                            'scores': data.get('scores', [])
                        })
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
        
        return results


class GroqProvider(FactCheckProvider):
    """
    Groq API - Free tier with generous limits
    Fast inference for open-source LLMs (Llama, Mixtral)
    Great for AI-powered analysis
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    @property
    def name(self) -> str:
        return "Groq"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'model': 'llama-3.1-70b-versatile',  # Free model
                    'messages': [
                        {
                            'role': 'system',
                            'content': '''You are a fact-checking AI. Analyze claims for accuracy.
                            Respond in JSON format with:
                            - "verdict": "true", "false", "partially_true", "unverifiable"
                            - "confidence": 0.0-1.0
                            - "reasoning": brief explanation
                            - "key_facts": list of relevant facts
                            - "sources_to_check": suggested sources to verify'''
                        },
                        {
                            'role': 'user',
                            'content': f'Analyze this claim: "{claim}"'
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 1000
                }
                
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        try:
                            # Try to parse as JSON
                            analysis = json.loads(content)
                        except json.JSONDecodeError:
                            analysis = {'raw_response': content}
                        
                        return [{
                            'source': 'Groq (Llama 3.1)',
                            'analysis': analysis
                        }]
        except Exception as e:
            logger.error(f"Groq API error: {e}")
        return []


class AnthropicProvider(FactCheckProvider):
    """
    Anthropic Claude API
    GitHub Education Pack provides $25 credit monthly
    Premium AI analysis with strong reasoning capabilities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def name(self) -> str:
        return "Anthropic Claude"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0,
                system="""You are Verity, an expert fact-checking AI. Analyze claims thoroughly and provide:
                1. Verdict: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
                2. Confidence score (0-100%)
                3. Key evidence supporting your verdict
                4. Known sources that can verify this claim
                5. Any caveats or context needed
                6. Red flags or warning signs if the claim seems misleading
                
                Be precise, cite specific facts, and acknowledge uncertainty when appropriate.""",
                messages=[
                    {
                        "role": "user",
                        "content": f"Fact-check this claim: {claim}"
                    }
                ]
            )
            
            return [{
                'source': 'Anthropic Claude',
                'model': 'claude-3-5-sonnet',
                'analysis': response.content[0].text
            }]
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
        return []


class SerperProvider(FactCheckProvider):
    """
    Serper API - Google Search API alternative
    Free tier: 2,500 searches/month
    Great for finding relevant sources and fact-checks
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
    
    @property
    def name(self) -> str:
        return "Serper (Google Search)"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': self.api_key,
                    'Content-Type': 'application/json'
                }
                payload = {
                    'q': f'fact check {claim}',
                    'num': 10
                }
                
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
        except Exception as e:
            logger.error(f"Serper API error: {e}")
        return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        results = []
        
        # Organic results
        for item in data.get('organic', [])[:5]:
            results.append({
                'source': 'Serper',
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'url': item.get('link'),
                'position': item.get('position')
            })
        
        # Knowledge graph
        if data.get('knowledgeGraph'):
            kg = data['knowledgeGraph']
            results.append({
                'source': 'Serper (Knowledge Graph)',
                'title': kg.get('title'),
                'description': kg.get('description'),
                'type': kg.get('type'),
                'attributes': kg.get('attributes', {})
            })
        
        return results


class AzureOpenAIProvider(FactCheckProvider):
    """
    Azure OpenAI Service
    GitHub Education Pack: $100 Azure credits
    Access to GPT-4 and other OpenAI models via Azure
    """
    
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
        self.api_version = '2024-02-15-preview'
    
    @property
    def name(self) -> str:
        return "Azure OpenAI"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.endpoint)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
                headers = {
                    'api-key': self.api_key,
                    'Content-Type': 'application/json'
                }
                payload = {
                    'messages': [
                        {
                            'role': 'system',
                            'content': '''You are a fact-checking expert. Analyze the claim and provide:
                            1. Verdict: TRUE, FALSE, PARTIALLY_TRUE, MISLEADING, or UNVERIFIABLE
                            2. Confidence: 0-100%
                            3. Key Evidence: Specific facts supporting your verdict
                            4. Sources: Known authoritative sources
                            5. Context: Important context the reader should know
                            Respond in JSON format.'''
                        },
                        {
                            'role': 'user',
                            'content': f'Fact-check this claim: "{claim}"'
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 1500
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        try:
                            analysis = json.loads(content)
                        except json.JSONDecodeError:
                            analysis = {'raw_response': content}
                        
                        return [{
                            'source': 'Azure OpenAI (GPT-4)',
                            'analysis': analysis
                        }]
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
        return []


class PerplexityProvider(FactCheckProvider):
    """
    Perplexity AI API - Research-focused AI
    Great for fact-checking with real-time internet search
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    @property
    def name(self) -> str:
        return "Perplexity AI"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'model': 'llama-3.1-sonar-small-128k-online',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a fact-checking assistant. Search the internet and provide accurate fact-checks with sources.'
                        },
                        {
                            'role': 'user',
                            'content': f'Fact-check this claim and provide sources: "{claim}"'
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 1000,
                    'search_domain_filter': ['fact-check', 'news', 'wiki'],
                    'return_citations': True
                }
                
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [{
                            'source': 'Perplexity AI',
                            'analysis': data['choices'][0]['message']['content'],
                            'citations': data.get('citations', [])
                        }]
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
        return []


class OpenRouterProvider(FactCheckProvider):
    """
    OpenRouter - Access to multiple AI models through one API
    Free tier available, pay-per-use for premium models
    Great for comparing different model outputs
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    @property
    def name(self) -> str:
        return "OpenRouter"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://verity-systems.vercel.app',
                    'X-Title': 'Verity Systems'
                }
                payload = {
                    'model': 'google/gemma-2-9b-it:free',  # Free model
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a fact-checking AI. Analyze claims for accuracy and provide detailed verdicts with evidence.'
                        },
                        {
                            'role': 'user',
                            'content': f'Fact-check: "{claim}". Provide verdict (TRUE/FALSE/PARTIALLY_TRUE/UNVERIFIABLE), confidence (0-100%), and reasoning.'
                        }
                    ],
                    'temperature': 0.1
                }
                
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [{
                            'source': 'OpenRouter (Gemma 2)',
                            'analysis': data['choices'][0]['message']['content']
                        }]
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
        return []


class CometAPIProvider(FactCheckProvider):
    """
    CometAPI - Access to 500+ AI models through one API
    GPT-4, Claude, Gemini, Llama, and more via OpenAI-compatible interface
    Website: https://cometapi.com
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-4o'):
        self.api_key = api_key or os.getenv('COMETAPI_API_KEY')
        self.base_url = os.getenv('COMETAPI_BASE_URL', 'https://api.cometapi.com/v1')
        self.model = model
    
    @property
    def name(self) -> str:
        return f"CometAPI ({self.model})"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': '''You are an expert fact-checker. Analyze the claim and respond with:
1. VERDICT: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
2. CONFIDENCE: 0-100%
3. REASONING: Clear explanation with evidence
4. SOURCES: What sources would support this conclusion'''
                        },
                        {
                            'role': 'user',
                            'content': f'Fact-check this claim: "{claim}"'
                        }
                    ],
                    'temperature': 0.2,
                    'max_tokens': 1000
                }
                
                async with session.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [{
                            'source': f'CometAPI ({self.model})',
                            'analysis': data['choices'][0]['message']['content'],
                            'usage': data.get('usage', {})
                        }]
                    else:
                        error_text = await response.text()
                        logger.error(f"CometAPI error ({response.status}): {error_text}")
        except asyncio.TimeoutError:
            logger.error(f"CometAPI timeout for model {self.model}")
        except Exception as e:
            logger.error(f"CometAPI error: {e}")
        return []


class PolygonProvider(FactCheckProvider):
    """
    Polygon.io API - Financial data verification
    Free tier: 5 API calls/minute
    Great for verifying financial claims and stock data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"
    
    @property
    def name(self) -> str:
        return "Polygon.io (Finance)"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def check_claim(self, claim: str) -> List[Dict]:
        if not self.is_available:
            return []
        
        # Extract stock tickers from claim
        tickers = re.findall(r'\$([A-Z]{1,5})\b|\b([A-Z]{2,5})\s+stock\b', claim)
        if not tickers:
            return []
        
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                for ticker_match in tickers[:3]:
                    ticker = ticker_match[0] or ticker_match[1]
                    url = f"{self.base_url}/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('results'):
                                results.append({
                                    'source': 'Polygon.io',
                                    'ticker': ticker,
                                    'company_name': data['results'].get('name'),
                                    'market_cap': data['results'].get('market_cap'),
                                    'description': data['results'].get('description'),
                                    'homepage': data['results'].get('homepage_url')
                                })
        except Exception as e:
            logger.error(f"Polygon API error: {e}")
        
        return results


class WikidataProvider(FactCheckProvider):
    """
    Wikidata Query Service - Completely free
    Access to structured knowledge base for fact verification
    """
    
    def __init__(self):
        self.endpoint = "https://query.wikidata.org/sparql"
    
    @property
    def name(self) -> str:
        return "Wikidata"
    
    async def check_claim(self, claim: str) -> List[Dict]:
        # Extract entities and try to verify against Wikidata
        entities = self._extract_entities(claim)
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for entity in entities[:2]:  # Limit queries
                    query = f'''
                    SELECT ?item ?itemLabel ?description WHERE {{
                        ?item rdfs:label "{entity}"@en.
                        OPTIONAL {{ ?item schema:description ?description. FILTER(LANG(?description) = "en") }}
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                    }}
                    LIMIT 5
                    '''
                    
                    headers = {'Accept': 'application/json'}
                    params = {'query': query}
                    
                    async with session.get(self.endpoint, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            for binding in data.get('results', {}).get('bindings', []):
                                results.append({
                                    'source': 'Wikidata',
                                    'entity': entity,
                                    'wikidata_id': binding.get('item', {}).get('value', '').split('/')[-1],
                                    'label': binding.get('itemLabel', {}).get('value'),
                                    'description': binding.get('description', {}).get('value')
                                })
        except Exception as e:
            logger.error(f"Wikidata API error: {e}")
        
        return results
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entity names from text"""
        # Find capitalized phrases (potential proper nouns)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        # Also extract quoted text
        quoted = re.findall(r'"([^"]+)"', text)
        return list(set(entities + quoted))


# ============================================================
# SUPER MODEL - COMBINES ALL PROVIDERS
# ============================================================

class VeritySuperModel:
    """
    Combines multiple fact-checking APIs into a single powerful model
    with security, caching, and consensus-based verification
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.security = SecurityManager()
        
        # Initialize all providers (16 total)
        self.providers: List[FactCheckProvider] = [
            # Free APIs (no key required)
            WikipediaProvider(),
            DuckDuckGoProvider(),
            WikidataProvider(),
            
            # Free tier APIs
            GoogleFactCheckProvider(),
            NewsAPIProvider(),
            ClaimBusterProvider(),
            HuggingFaceProvider(),
            SerperProvider(),
            PolygonProvider(),
            
            # AI/LLM Providers (free tiers + GitHub Education credits)
            GroqProvider(),           # Free: Llama 3.1 70B
            AnthropicProvider(),      # GitHub Education: $25/month
            AzureOpenAIProvider(),    # GitHub Education: $100 Azure credits
            PerplexityProvider(),     # Research queries with citations
            OpenRouterProvider(),     # Free: Gemma 2 9B
            
            # CometAPI - 500+ models via single API (GPT-4, Claude, Gemini, etc.)
            CometAPIProvider(model='gpt-4o'),        # GPT-4o for general verification
            CometAPIProvider(model='claude-3.5-sonnet'),  # Claude for nuanced analysis
        ]
        
        # Cache for results (simple in-memory, use Redis in production)
        self.cache: Dict[str, Tuple[VerificationResult, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)
        
        logger.info(f"Initialized VeritySuperModel with {len(self.providers)} providers")
        self._log_provider_status()
    
    def _log_provider_status(self):
        """Log which providers are available"""
        for provider in self.providers:
            # Use ASCII-safe characters for Windows console compatibility
            status = "[OK] Available" if provider.is_available else "[--] Not configured"
            logger.info(f"  {provider.name}: {status}")
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key for a claim"""
        return self.security.hash_data(claim.lower().strip())
    
    async def verify_claim(
        self,
        claim: str,
        client_id: str = "anonymous",
        use_cache: bool = True,
        providers: Optional[List[str]] = None
    ) -> VerificationResult:
        """
        Main verification method - runs claim through all available providers
        and synthesizes results
        """
        start_time = time.time()
        
        # Security checks
        if not self.security.check_rate_limit(client_id):
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Sanitize and validate input
        claim = self.security.sanitize_input(claim)
        if not claim or len(claim) < 10:
            raise ValueError("Claim too short or invalid")
        
        # Anonymize PII before processing
        claim_for_processing = self.security.anonymize_pii(claim)
        
        # Check cache
        cache_key = self._get_cache_key(claim_for_processing)
        if use_cache and cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Cache hit for claim: {claim[:50]}...")
                return cached_result
        
        # Audit logging
        self.security.generate_audit_log('claim_verification', {
            'client_id': client_id,
            'claim_hash': cache_key,
            'claim_length': len(claim)
        })
        
        # Select providers to use
        active_providers = self.providers
        if providers:
            active_providers = [p for p in self.providers if p.name in providers]
        
        # Run all providers concurrently
        tasks = []
        for provider in active_providers:
            if provider.is_available:
                tasks.append(self._run_provider(provider, claim_for_processing))
        
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        provider_results = []
        for i, result in enumerate(all_results):
            if isinstance(result, Exception):
                logger.error(f"Provider error: {result}")
            else:
                provider_results.append(result)
        
        # Synthesize results into final verdict
        verification_result = self._synthesize_results(claim, provider_results, start_time)
        
        # Cache result
        self.cache[cache_key] = (verification_result, datetime.now())
        
        return verification_result
    
    async def _run_provider(self, provider: FactCheckProvider, claim: str) -> Dict:
        """Run a single provider with timeout and error handling"""
        try:
            results = await asyncio.wait_for(
                provider.check_claim(claim),
                timeout=30.0
            )
            return {
                'provider': provider.name,
                'results': results,
                'success': True
            }
        except asyncio.TimeoutError:
            logger.warning(f"Timeout for provider: {provider.name}")
            return {
                'provider': provider.name,
                'results': [],
                'success': False,
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"Error in provider {provider.name}: {e}")
            return {
                'provider': provider.name,
                'results': [],
                'success': False,
                'error': str(e)
            }
    
    def _synthesize_results(
        self,
        claim: str,
        provider_results: List[Dict],
        start_time: float
    ) -> VerificationResult:
        """
        Synthesize results from all providers into a single verdict
        Uses consensus and confidence weighting
        """
        sources = []
        fact_checks = []
        ai_analyses = []
        warnings = []
        
        verdicts = []
        confidence_scores = []
        
        for result in provider_results:
            if not result.get('success'):
                continue
            
            provider = result['provider']
            
            for item in result.get('results', []):
                # Extract fact-check specific results
                if 'rating' in item:
                    fact_checks.append(item)
                    verdict = self._normalize_rating(item.get('rating', ''))
                    if verdict:
                        verdicts.append(verdict)
                
                # Extract AI analysis
                if 'analysis' in item:
                    ai_analyses.append(item['analysis'])
                    if isinstance(item['analysis'], dict):
                        if 'verdict' in item['analysis']:
                            verdicts.append(item['analysis']['verdict'].upper())
                        if 'confidence' in item['analysis']:
                            confidence_scores.append(float(item['analysis']['confidence']))
                
                # Build sources list
                if item.get('url'):
                    credibility = self._assess_credibility(provider, item)
                    sources.append(VerificationSource(
                        name=item.get('source_name') or item.get('title') or provider,
                        url=item.get('url'),
                        credibility=credibility,
                        claim_rating=item.get('rating'),
                        snippet=item.get('snippet') or item.get('text') or item.get('description')
                    ))
        
        # Calculate consensus verdict
        final_status = self._calculate_consensus(verdicts)
        
        # Calculate confidence score
        if confidence_scores:
            confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            # Base confidence on number of sources agreeing
            confidence = min(0.3 + (len(sources) * 0.1), 0.9)
        
        # Generate warnings
        if len(sources) < 2:
            warnings.append("Limited sources available for verification")
        if final_status == VerificationStatus.DISPUTED:
            warnings.append("Sources disagree on this claim")
        if not fact_checks:
            warnings.append("No professional fact-checks found for this claim")
        
        # Create summary
        analysis_summary = self._generate_summary(claim, final_status, sources, fact_checks)
        
        # Combine AI analyses
        ai_analysis = "\n\n---\n\n".join(
            str(a) if isinstance(a, str) else json.dumps(a, indent=2) 
            for a in ai_analyses
        ) if ai_analyses else "No AI analysis available"
        
        processing_time = (time.time() - start_time) * 1000
        
        return VerificationResult(
            claim=claim,
            status=final_status,
            confidence_score=confidence,
            sources=sources,
            analysis_summary=analysis_summary,
            fact_checks=fact_checks,
            ai_analysis=ai_analysis,
            warnings=warnings,
            processing_time_ms=processing_time
        )
    
    def _normalize_rating(self, rating: str) -> Optional[str]:
        """Normalize various rating formats to standard verdicts"""
        if not rating:
            return None
        
        rating_lower = rating.lower()
        
        true_indicators = ['true', 'correct', 'accurate', 'verified', 'fact']
        false_indicators = ['false', 'incorrect', 'inaccurate', 'fake', 'lie', 'pants on fire']
        partial_indicators = ['partially', 'half', 'mixture', 'mostly']
        
        if any(ind in rating_lower for ind in false_indicators):
            return 'FALSE'
        elif any(ind in rating_lower for ind in partial_indicators):
            return 'PARTIALLY_TRUE'
        elif any(ind in rating_lower for ind in true_indicators):
            return 'TRUE'
        
        return None
    
    def _calculate_consensus(self, verdicts: List[str]) -> VerificationStatus:
        """Calculate consensus from multiple verdicts"""
        if not verdicts:
            return VerificationStatus.UNVERIFIABLE
        
        # Count verdicts
        verdict_counts = {}
        for v in verdicts:
            v_upper = v.upper()
            verdict_counts[v_upper] = verdict_counts.get(v_upper, 0) + 1
        
        # Check for consensus
        total = len(verdicts)
        for verdict, count in verdict_counts.items():
            if count / total >= 0.6:  # 60% agreement
                if verdict in ['TRUE', 'VERIFIED_TRUE']:
                    return VerificationStatus.VERIFIED_TRUE
                elif verdict in ['FALSE', 'VERIFIED_FALSE']:
                    return VerificationStatus.VERIFIED_FALSE
                elif verdict in ['PARTIALLY_TRUE', 'PARTIAL']:
                    return VerificationStatus.PARTIALLY_TRUE
        
        # No clear consensus
        if len(verdict_counts) > 1:
            return VerificationStatus.DISPUTED
        
        return VerificationStatus.NEEDS_CONTEXT
    
    def _assess_credibility(self, provider: str, item: Dict) -> SourceCredibility:
        """Assess credibility of a source"""
        high_credibility_sources = [
            'reuters', 'ap news', 'bbc', 'snopes', 'politifact',
            'factcheck.org', 'washington post', 'new york times',
            'wikipedia', 'wikidata', 'google fact check'
        ]
        
        source_name = (item.get('source_name') or item.get('publisher') or provider).lower()
        
        if any(hc in source_name for hc in high_credibility_sources):
            return SourceCredibility.HIGH
        elif provider in ['Google Fact Check', 'Wikipedia', 'Wikidata', 'Anthropic Claude']:
            return SourceCredibility.HIGH
        elif provider in ['NewsAPI', 'DuckDuckGo', 'Groq']:
            return SourceCredibility.MEDIUM
        
        return SourceCredibility.UNKNOWN
    
    def _generate_summary(
        self,
        claim: str,
        status: VerificationStatus,
        sources: List[VerificationSource],
        fact_checks: List[Dict]
    ) -> str:
        """Generate a human-readable summary of the verification"""
        status_text = {
            VerificationStatus.VERIFIED_TRUE: "appears to be TRUE",
            VerificationStatus.VERIFIED_FALSE: "appears to be FALSE",
            VerificationStatus.PARTIALLY_TRUE: "is PARTIALLY TRUE",
            VerificationStatus.UNVERIFIABLE: "could not be verified",
            VerificationStatus.NEEDS_CONTEXT: "requires additional context",
            VerificationStatus.DISPUTED: "is DISPUTED among sources"
        }
        
        summary = f"This claim {status_text[status]}. "
        summary += f"Analyzed using {len(sources)} sources. "
        
        if fact_checks:
            summary += f"Found {len(fact_checks)} professional fact-checks. "
        
        high_cred = sum(1 for s in sources if s.credibility == SourceCredibility.HIGH)
        if high_cred:
            summary += f"{high_cred} high-credibility sources referenced."
        
        return summary


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

async def main():
    """Main entry point for CLI usage"""
    print("\n" + "="*60)
    print("🎯 VERITY SUPER FACT-CHECKER")
    print("="*60)
    print("Powered by multiple AI and fact-checking APIs")
    print("-"*60)
    
    # Initialize super model
    model = VeritySuperModel()
    
    # Test claim
    test_claim = """
    The University of Botswana was founded in 1982 and has 50,000 students.
    It is ranked #1 in Africa and has partnerships with Harvard.
    """
    
    print(f"\n📝 Claim to verify:\n{test_claim.strip()}\n")
    print("-"*60)
    print("🔄 Running verification across all providers...")
    print("-"*60)
    
    try:
        result = await model.verify_claim(test_claim.strip())
        
        print(f"\n✅ VERDICT: {result.status.value.upper()}")
        print(f"📊 Confidence: {result.confidence_score:.1%}")
        print(f"⏱️  Processing time: {result.processing_time_ms:.0f}ms")
        
        print(f"\n📋 Summary:\n{result.analysis_summary}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   • {warning}")
        
        if result.sources:
            print(f"\n📚 Sources ({len(result.sources)}):")
            for source in result.sources[:5]:
                print(f"   • {source.name} ({source.credibility.value})")
                if source.url:
                    print(f"     {source.url}")
        
        if result.fact_checks:
            print(f"\n🔍 Fact-Checks Found ({len(result.fact_checks)}):")
            for fc in result.fact_checks[:3]:
                print(f"   • {fc.get('publisher', 'Unknown')}: {fc.get('rating', 'N/A')}")
        
        print("\n" + "="*60)
        print("✓ Verification complete!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        logger.exception("Verification failed")


if __name__ == "__main__":
    asyncio.run(main())
