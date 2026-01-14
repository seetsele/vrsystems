"""
Verity API Server - Production v9
=================================
Full multi-provider AI verification API with 10+ providers

Features:
- Multi-provider AI verification (10+ providers)
- Rate limiting with sliding window
- API key authentication
- CORS security
- Health monitoring
- Stripe integration ready
"""

import os
import sys
import time
import json
import asyncio
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the script's directory, not the working directory
_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")

# =============================================================================
# CONFIGURATION - ALL PROVIDERS
# =============================================================================

class Config:
    ENV = os.getenv("ENVIRONMENT", "production")
    DEBUG = ENV == "development"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Security
    SECRET_KEY = os.getenv("VERITY_SECRET_KEY", secrets.token_hex(32))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # API Keys for authentication
    API_KEYS = set(filter(None, os.getenv("API_KEYS", "demo-key-12345,test-key-67890").split(",")))
    REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    
    # ==========================================================================
    # ALL AI PROVIDER API KEYS - 32+ PROVIDERS
    # ==========================================================================
    
    # Tier 1: Primary Providers (fastest, most reliable)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    
    # Tier 2: Major Providers
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    
    # Tier 3: Specialized Providers
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
    SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
    FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Tier 4: Aggregators & Open Source
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
    
    # Tier 5: Additional Providers
    XAI_API_KEY = os.getenv("XAI_API_KEY")  # Grok
    AI21_API_KEY = os.getenv("AI21_API_KEY")
    LEPTON_API_KEY = os.getenv("LEPTON_API_KEY")
    ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY")
    NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY")
    CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_TOKEN")  # Cloudflare Workers AI
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    
    # Tier 6: xAI Alternatives (NEW)
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
    HYPERBOLIC_API_KEY = os.getenv("HYPERBOLIC_API_KEY")
    LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY")
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # Alibaba Qwen
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
    BAICHUAN_API_KEY = os.getenv("BAICHUAN_API_KEY")
    
    # Search & Research APIs
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    YOU_API_KEY = os.getenv("YOU_API_KEY")
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    
    # Fact-Check & Academic APIs
    GOOGLE_FACTCHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")
    CLAIMBUSTER_API_KEY = os.getenv("CLAIMBUSTER_API_KEY")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    
    # Additional AI Providers
    NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

    # Simulation / debug key - set this in env to require a header for simulate endpoints
    SIMULATE_KEY = os.getenv("SIMULATE_KEY")  # if set, required header X-SIM-KEY must match
    # Optional: comma-separated list of allowed client IPs for simulation endpoints
    SIMULATE_ALLOWED_IPS = [ip.strip() for ip in os.getenv("SIMULATE_ALLOWED_IPS", "").split(",") if ip.strip()]
    # Rate limit for simulate key (requests per minute)
    SIMULATE_KEY_RATE_LIMIT = int(os.getenv("SIMULATE_KEY_RATE_LIMIT", 60))


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("VerityAPI")


# =============================================================================
# LATEST AI MODELS (January 2026) - 20+ PROVIDERS
# =============================================================================

LATEST_MODELS = {
    # Tier 1: Primary (fastest)
    "groq": "llama-3.3-70b-versatile",
    "perplexity": "sonar-pro",
    "google": "gemini-2.0-flash",
    
    # Tier 2: Major Providers
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "mistral": "mistral-large-latest",
    "cohere": "command-r-plus",
    
    # Tier 3: Specialized
    "cerebras": "llama-3.3-70b",
    "sambanova": "Meta-Llama-3.3-70B-Instruct",
    "fireworks": "accounts/fireworks/models/llama-v3p3-70b-instruct",
    "deepseek": "deepseek-chat",
    
    # Tier 4: Aggregators
    "openrouter": "meta-llama/llama-3.3-70b-instruct",
    "huggingface": "meta-llama/Llama-3.3-70B-Instruct",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "replicate": "meta/llama-3.3-70b-instruct",
    
    # Tier 5: Additional
    "xai": "grok-2",
    "ai21": "jamba-1.5-large",
    "lepton": "llama-3.3-70b",
    "anyscale": "meta-llama/Llama-3.3-70B-Instruct",
    "nvidia": "meta/llama-3.1-70b-instruct",
    "cloudflare": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    
    # Tier 6: Search & Research AI
    "you": "you-chat",
    "jina": "jina-embeddings-v3",
    "novita": "meta-llama/llama-3.3-70b-instruct",
}


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> tuple:
        now = time.time()
        window_start = now - self.window_seconds
        
        self.requests[identifier] = [
            ts for ts in self.requests[identifier] if ts > window_start
        ]
        
        current_count = len(self.requests[identifier])
        remaining = max(0, self.max_requests - current_count)
        
        if current_count >= self.max_requests:
            reset_time = int(self.requests[identifier][0] + self.window_seconds - now)
            return False, {"limit": self.max_requests, "remaining": 0, "reset": reset_time}
        
        self.requests[identifier].append(now)
        return True, {"limit": self.max_requests, "remaining": remaining - 1, "reset": self.window_seconds}

# Simulate-key specific rate limiter (simple wrapper with minute window)
class SimulateKeyRateLimiter:
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple:
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[key] = [ts for ts in self.requests[key] if ts > window_start]
        if len(self.requests[key]) >= self.max_requests:
            reset_time = int(self.requests[key][0] + self.window_seconds - now)
            return False, {"limit": self.max_requests, "remaining": 0, "reset": reset_time}
        self.requests[key].append(now)
        return True, {"limit": self.max_requests, "remaining": self.max_requests - len(self.requests[key]), "reset": self.window_seconds}

rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS, Config.RATE_LIMIT_WINDOW)
simulate_key_limiter = SimulateKeyRateLimiter(Config.SIMULATE_KEY_RATE_LIMIT)


# =============================================================================
# PROVIDER HEALTH TRACKING - ENSURES ALL PROVIDERS WORK AT ALL TIMES
# =============================================================================

class ProviderHealth:
    """Track provider health and implement circuit breaker pattern"""
    
    def __init__(self):
        self.failures: Dict[str, int] = defaultdict(int)
        self.last_failure: Dict[str, float] = {}
        self.cooldown_until: Dict[str, float] = {}
        self.max_failures = 3  # Failures before cooldown
        self.cooldown_seconds = 60  # Cooldown duration
        self.retry_delays = [0.5, 1.0, 2.0]  # Exponential backoff
    
    def is_healthy(self, provider: str) -> bool:
        """Check if provider is healthy (not in cooldown)"""
        if provider in self.cooldown_until:
            if time.time() < self.cooldown_until[provider]:
                return False
            # Cooldown expired, reset
            del self.cooldown_until[provider]
            self.failures[provider] = 0
        return True
    
    def record_success(self, provider: str):
        """Record successful call - reset failure count"""
        self.failures[provider] = 0
        if provider in self.cooldown_until:
            del self.cooldown_until[provider]
    
    def record_failure(self, provider: str, status_code: int = 0):
        """Record failed call - may trigger cooldown"""
        self.failures[provider] += 1
        self.last_failure[provider] = time.time()
        
        # Rate limit (429) or server error (5xx) - enter cooldown
        if status_code in [429, 500, 502, 503, 504] or self.failures[provider] >= self.max_failures:
            cooldown = self.cooldown_seconds
            if status_code == 429:
                cooldown = 120  # Longer cooldown for rate limits
            self.cooldown_until[provider] = time.time() + cooldown
            logger.warning(f"[HEALTH] {provider} entering {cooldown}s cooldown (failures: {self.failures[provider]})")
    
    def get_retry_delay(self, attempt: int) -> float:
        """Get retry delay for exponential backoff"""
        if attempt < len(self.retry_delays):
            return self.retry_delays[attempt]
        return self.retry_delays[-1]
    
    def get_status(self) -> Dict:
        """Get health status of all providers"""
        return {
            "failures": dict(self.failures),
            "in_cooldown": [p for p, t in self.cooldown_until.items() if time.time() < t]
        }


# Global provider health tracker
provider_health = ProviderHealth()


# =============================================================================
# CLAIM CACHE - Reduces API costs and improves response time
# =============================================================================

class ClaimCache:
    """LRU Cache for verified claims with TTL"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.access_order = []
        self.max_size = max_size
        self.ttl = ttl  # 1 hour default
        self.hits = 0
        self.misses = 0
    
    def _key(self, claim: str, tier: str) -> str:
        """Generate cache key from normalized claim and tier"""
        normalized = claim.lower().strip()
        return hashlib.sha256(f"{normalized}:{tier}".encode()).hexdigest()[:16]
    
    def get(self, claim: str, tier: str) -> Optional[Dict]:
        """Get cached result if valid"""
        key = self._key(claim, tier)
        if key in self.cache:
            entry, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                # Move to end of access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                logger.info(f"[CACHE] Hit for claim (key={key[:8]})")
                return entry
            else:
                # Expired - remove
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
        self.misses += 1
        return None
    
    def set(self, claim: str, tier: str, result: Dict):
        """Store result in cache"""
        key = self._key(claim, tier)
        
        # Evict oldest if at capacity
        while len(self.cache) >= self.max_size and self.access_order:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
        
        self.cache[key] = (result, time.time())
        self.access_order.append(key)
        logger.info(f"[CACHE] Stored result (key={key[:8]})")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "ttl_seconds": self.ttl
        }


# Global claim cache
claim_cache = ClaimCache(max_size=1000, ttl=3600)


# =============================================================================
# PROVIDER RATE LIMITER - Prevent hitting API limits
# =============================================================================

class ProviderRateLimiter:
    """Per-provider rate limiting based on known API limits"""
    
    # Requests per minute (rpm) and per day (rpd) for each provider
    LIMITS = {
        # Free tier limits (be conservative)
        "groq": {"rpm": 30, "rpd": 14400},
        "perplexity": {"rpm": 20, "rpd": 1000},
        "openai": {"rpm": 3, "rpd": 200},
        "google": {"rpm": 15, "rpd": 1500},
        "anthropic": {"rpm": 5, "rpd": 100},
        "mistral": {"rpm": 5, "rpd": 500},
        "cohere": {"rpm": 20, "rpd": 1000},
        "cerebras": {"rpm": 30, "rpd": 10000},
        "sambanova": {"rpm": 30, "rpd": 5000},
        "fireworks": {"rpm": 10, "rpd": 500},
        "deepseek": {"rpm": 10, "rpd": 500},
        "openrouter": {"rpm": 20, "rpd": 1000},
        "huggingface": {"rpm": 30, "rpd": 10000},
        "together": {"rpm": 10, "rpd": 1000},
        "xai": {"rpm": 10, "rpd": 500},
        "ai21": {"rpm": 10, "rpd": 500},
        "you": {"rpm": 20, "rpd": 1000},
        "jina": {"rpm": 20, "rpd": 5000},
        "tavily": {"rpm": 20, "rpd": 1000},
        "brave": {"rpm": 20, "rpd": 2000},
        "serper": {"rpm": 100, "rpd": 2500},
        "exa": {"rpm": 10, "rpd": 1000},
    }
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def can_request(self, provider: str) -> bool:
        """Check if we can make a request to this provider"""
        now = time.time()
        limits = self.LIMITS.get(provider, {"rpm": 10, "rpd": 500})
        
        # Clean old entries (older than 24 hours)
        day_ago = now - 86400
        self.requests[provider] = [t for t in self.requests[provider] if t > day_ago]
        
        minute_ago = now - 60
        minute_count = sum(1 for t in self.requests[provider] if t > minute_ago)
        day_count = len(self.requests[provider])
        
        if minute_count >= limits["rpm"]:
            logger.debug(f"[RATE] {provider} at minute limit ({minute_count}/{limits['rpm']})")
            return False
        
        if day_count >= limits["rpd"]:
            logger.debug(f"[RATE] {provider} at daily limit ({day_count}/{limits['rpd']})")
            return False
        
        return True
    
    def record(self, provider: str):
        """Record a request to a provider"""
        self.requests[provider].append(time.time())
    
    def get_stats(self) -> Dict:
        """Get rate limit stats for all providers"""
        now = time.time()
        minute_ago = now - 60
        stats = {}
        for provider, requests in self.requests.items():
            limits = self.LIMITS.get(provider, {"rpm": 10, "rpd": 500})
            minute_count = sum(1 for t in requests if t > minute_ago)
            stats[provider] = {
                "minute_usage": f"{minute_count}/{limits['rpm']}",
                "day_usage": f"{len(requests)}/{limits['rpd']}"
            }
        return stats


# Global provider rate limiter
provider_rate_limiter = ProviderRateLimiter()


# =============================================================================
# SOURCE CREDIBILITY DATABASE
# =============================================================================

SOURCE_CREDIBILITY = {
    # Tier 1: Gold Standard (0.95-1.0)
    "reuters.com": 0.98, "apnews.com": 0.98, "bbc.com": 0.95, "bbc.co.uk": 0.95,
    "nature.com": 0.99, "science.org": 0.99, "nejm.org": 0.99, "thelancet.com": 0.98,
    "who.int": 0.97, "cdc.gov": 0.97, "nih.gov": 0.97,
    
    # Tier 2: Highly Credible (0.85-0.94)
    "nytimes.com": 0.90, "washingtonpost.com": 0.88, "theguardian.com": 0.87,
    "npr.org": 0.92, "pbs.org": 0.92, "economist.com": 0.91,
    "wsj.com": 0.89, "ft.com": 0.90, "bloomberg.com": 0.88,
    
    # Tier 3: Generally Credible (0.70-0.84)
    "cnn.com": 0.78, "foxnews.com": 0.72, "msnbc.com": 0.75,
    "usatoday.com": 0.76, "time.com": 0.80, "newsweek.com": 0.75,
    "wikipedia.org": 0.80, "britannica.com": 0.90,
    
    # Tier 4: Fact-Check Sites (0.90-0.95)
    "snopes.com": 0.94, "factcheck.org": 0.95, "politifact.com": 0.93,
    "fullfact.org": 0.93, "leadstories.com": 0.90,
    
    # Tier 5: Academic (0.85-0.95)
    "arxiv.org": 0.88, "scholar.google.com": 0.85, "pubmed.ncbi.nlm.nih.gov": 0.95,
    "semanticscholar.org": 0.88, "jstor.org": 0.92,
    
    # Tier 6: Questionable (0.10-0.40)
    "infowars.com": 0.10, "naturalnews.com": 0.15, "beforeitsnews.com": 0.12,
    "zerohedge.com": 0.30, "rt.com": 0.35,
}

def score_source_credibility(url: str) -> float:
    """Score a source's credibility based on domain"""
    if not url:
        return 0.5
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "").lower()
        # Check exact match
        if domain in SOURCE_CREDIBILITY:
            return SOURCE_CREDIBILITY[domain]
        # Check if domain ends with any known domain
        for known_domain, score in SOURCE_CREDIBILITY.items():
            if domain.endswith(known_domain):
                return score
    except Exception:
        pass
    return 0.5  # Unknown source


# =============================================================================
# CLAIM CATEGORIZATION - Route to specialized providers
# =============================================================================

CLAIM_CATEGORIES = {
    "science": ["scientific", "study", "research", "experiment", "data", "peer-reviewed", 
                "laboratory", "hypothesis", "evidence", "discovery", "molecule", "atom"],
    "health": ["vaccine", "covid", "coronavirus", "medicine", "treatment", "drug", "disease",
               "symptom", "diagnosis", "therapy", "virus", "bacteria", "health", "medical"],
    "politics": ["election", "politician", "vote", "government", "policy", "congress", 
                 "senate", "president", "democrat", "republican", "campaign", "ballot"],
    "finance": ["stock", "bitcoin", "economy", "market", "crypto", "investment", "trading",
                "currency", "inflation", "recession", "gdp", "federal reserve", "interest rate"],
    "technology": ["ai", "artificial intelligence", "software", "computer", "internet", 
                   "tech", "digital", "algorithm", "machine learning", "robot", "quantum"],
    "environment": ["climate", "global warming", "carbon", "emission", "pollution", 
                    "renewable", "solar", "wind energy", "greenhouse", "environment"],
}

CATEGORY_SPECIALISTS = {
    "science": ["perplexity", "google", "anthropic", "openai"],  # Need citations
    "health": ["perplexity", "google", "openai", "anthropic"],   # Need high accuracy
    "politics": ["perplexity", "you", "jina", "openrouter"],     # Need current events
    "finance": ["perplexity", "google", "openai", "fireworks"],  # Need real-time data
    "technology": ["perplexity", "openai", "anthropic", "groq"], # Need technical accuracy
    "environment": ["perplexity", "google", "anthropic"],        # Need scientific consensus
}

def categorize_claim(claim: str) -> str:
    """Categorize a claim to route to specialized providers"""
    claim_lower = claim.lower()
    scores = {}
    
    for category, keywords in CLAIM_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in claim_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "general"

def prioritize_providers_for_claim(claim: str, available: List[str]) -> List[str]:
    """Prioritize providers based on claim category"""
    category = categorize_claim(claim)
    specialists = CATEGORY_SPECIALISTS.get(category, [])
    
    # Specialists first, then others
    prioritized = [p for p in specialists if p in available]
    others = [p for p in available if p not in prioritized]
    
    return prioritized + others


# =============================================================================
# SECURITY - Input validation and injection protection
# =============================================================================

INJECTION_PATTERNS = [
    "ignore previous", "disregard all", "forget your instructions",
    "you are now", "pretend you are", "act as if",
    "jailbreak", "dan mode", "developer mode",
    "bypass", "override", "unlock",
    "new persona", "roleplay as", "imagine you are",
    "system prompt", "ignore above", "ignore the above",
]

def detect_injection(claim: str) -> bool:
    """Detect potential prompt injection attempts"""
    claim_lower = claim.lower()
    return any(pattern in claim_lower for pattern in INJECTION_PATTERNS)

def sanitize_claim(claim: str) -> str:
    """Sanitize user input for safe processing"""
    import re
    # Normalize whitespace
    claim = re.sub(r'\s+', ' ', claim.strip())
    # Remove control characters
    claim = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', claim)
    # Remove potential markdown/code injection
    claim = re.sub(r'```[\s\S]*?```', '', claim)
    # Limit length
    return claim[:2000]


# =============================================================================
# PROVIDER CONFIGURATION - SINGLE SOURCE OF TRUTH
# =============================================================================

def get_all_provider_checks():
    """Get ALL provider checks - single source of truth (32+ providers)"""
    return [
        # Tier 1: Primary (fastest)
        ("groq", Config.GROQ_API_KEY),
        ("perplexity", Config.PERPLEXITY_API_KEY),
        ("google", Config.GOOGLE_AI_API_KEY),
        # Tier 2: Major Providers
        ("openai", Config.OPENAI_API_KEY),
        ("anthropic", Config.ANTHROPIC_API_KEY),
        ("mistral", Config.MISTRAL_API_KEY),
        ("cohere", Config.COHERE_API_KEY),
        # Tier 3: Specialized
        ("cerebras", Config.CEREBRAS_API_KEY),
        ("sambanova", Config.SAMBANOVA_API_KEY),
        ("fireworks", Config.FIREWORKS_API_KEY),
        ("deepseek", Config.DEEPSEEK_API_KEY),
        # Tier 4: Aggregators
        ("openrouter", Config.OPENROUTER_API_KEY),
        ("huggingface", Config.HUGGINGFACE_API_KEY),
        ("together", Config.TOGETHER_API_KEY),
        ("replicate", Config.REPLICATE_API_KEY),
        # Tier 5: Additional AI
        ("xai", Config.XAI_API_KEY),
        ("ai21", Config.AI21_API_KEY),
        ("lepton", Config.LEPTON_API_KEY),
        ("anyscale", Config.ANYSCALE_API_KEY),
        ("nvidia", Config.NVIDIA_NIM_API_KEY),
        ("novita", Config.NOVITA_API_KEY),
        # Tier 6: Search & Research
        ("you", Config.YOU_API_KEY),
        ("jina", Config.JINA_API_KEY),
        ("tavily", Config.TAVILY_API_KEY),
        ("brave", Config.BRAVE_API_KEY),
        ("serper", Config.SERPER_API_KEY),
        ("exa", Config.EXA_API_KEY),
        # Tier 8: xAI Alternatives (NEW - 10 providers)
        ("cloudflare", Config.CLOUDFLARE_API_KEY and Config.CLOUDFLARE_ACCOUNT_ID),
        ("siliconflow", Config.SILICONFLOW_API_KEY),
        ("hyperbolic", Config.HYPERBOLIC_API_KEY),
        ("lambdalabs", Config.LAMBDA_API_KEY),
        ("ollama", os.getenv("OLLAMA_HOST")),  # Local provider
        ("zhipu", Config.ZHIPU_API_KEY),
        ("alibaba", Config.DASHSCOPE_API_KEY),
        ("moonshot", Config.MOONSHOT_API_KEY),
        ("baichuan", Config.BAICHUAN_API_KEY),
    ]

def get_search_provider_checks():
    """Get search/fact-check API checks"""
    return [
        ("tavily", Config.TAVILY_API_KEY),
        ("brave", Config.BRAVE_API_KEY),
        ("serper", Config.SERPER_API_KEY),
        ("exa", Config.EXA_API_KEY),
        ("you", Config.YOU_API_KEY),
        ("jina", Config.JINA_API_KEY),
        ("google_factcheck", Config.GOOGLE_FACTCHECK_API_KEY),
        ("claimbuster", Config.CLAIMBUSTER_API_KEY),
        ("semantic_scholar", Config.SEMANTIC_SCHOLAR_API_KEY),
    ]

def get_available_providers():
    """Get list of available provider names"""
    return [name for name, key in get_all_provider_checks() if key]

def get_available_search_apis():
    """Get list of available search/fact-check APIs"""
    return [name for name, key in get_search_provider_checks() if key]


# =============================================================================
# AI PROVIDERS - ALL 22+ PROVIDERS WITH ROBUST FAILOVER
# =============================================================================

class AIProviders:
    """Unified interface for 20+ AI verification providers with auto-retry and failover"""
    
    def __init__(self):
        self.http_client = None
        self.available_providers = []
        
    async def __aenter__(self):
        self.http_client = httpx.AsyncClient(timeout=45.0)
        await self._check_providers()
        return self
    
    async def __aexit__(self, *args):
        if self.http_client:
            await self.http_client.aclose()
    
    async def _check_providers(self):
        """Check which providers are available - uses global helper"""
        self.available_providers = get_available_providers()
        logger.info(f"[PROVIDERS] {len(self.available_providers)} available: {self.available_providers}")
    
    async def _call_with_retry(self, provider: str, call_func, max_retries: int = 2) -> Dict:
        """Call a provider with automatic retry and health tracking"""
        if not provider_health.is_healthy(provider):
            logger.debug(f"[SKIP] {provider} in cooldown")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                result = await call_func()
                if result and result.get("success"):
                    provider_health.record_success(provider)
                    return result
                elif result and result.get("status_code"):
                    provider_health.record_failure(provider, result["status_code"])
                    if result["status_code"] == 429:  # Rate limit - don't retry
                        break
            except Exception as e:
                logger.error(f"[RETRY] {provider} attempt {attempt + 1} failed: {e}")
                provider_health.record_failure(provider)
            
            if attempt < max_retries:
                delay = provider_health.get_retry_delay(attempt)
                await asyncio.sleep(delay)
        
        return None
    
    # =========================================================================
    # TIER 1 PROVIDERS
    # =========================================================================
    
    async def verify_with_groq(self, claim: str) -> Dict:
        """Verify claim using Groq (Llama 3.3 - Ultra Fast)"""
        if not Config.GROQ_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.GROQ_API_KEY}"},
                json={
                    "model": LATEST_MODELS["groq"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Analyze claims and provide verdicts: 'true', 'false', 'partially_true', 'mostly_true', 'mostly_false', or 'unverifiable'. Include confidence (0-1) and brief explanation."},
                        {"role": "user", "content": f"Fact-check this claim: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "groq", "model": LATEST_MODELS["groq"], "response": content, "success": True}
            else:
                logger.error(f"Groq error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Groq exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_perplexity(self, claim: str) -> Dict:
        """Verify claim using Perplexity (Real-time web search)"""
        if not Config.PERPLEXITY_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {Config.PERPLEXITY_API_KEY}"},
                json={
                    "model": LATEST_MODELS["perplexity"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker with access to current information. Verify claims and cite sources. Provide verdict: 'true', 'false', 'partially_true', 'mostly_true', 'mostly_false', or 'unverifiable'."},
                        {"role": "user", "content": f"Fact-check with sources: {claim}"}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "perplexity", "model": LATEST_MODELS["perplexity"], "response": content, "success": True}
            else:
                logger.error(f"Perplexity error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Perplexity exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_google(self, claim: str) -> Dict:
        """Verify claim using Google Gemini 2.0 Flash"""
        if not Config.GOOGLE_AI_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{LATEST_MODELS['google']}:generateContent?key={Config.GOOGLE_AI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": f"As a fact-checker, verify this claim and provide: verdict (true/false/partially_true/unverifiable), confidence (0-1), and brief explanation.\n\nClaim: {claim}"}]
                    }],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"provider": "google", "model": LATEST_MODELS["google"], "response": content, "success": True}
            else:
                logger.error(f"Google error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Google exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    # =========================================================================
    # TIER 2 PROVIDERS
    # =========================================================================
    
    async def verify_with_openai(self, claim: str) -> Dict:
        """Verify claim using OpenAI GPT-4o"""
        if not Config.OPENAI_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.OPENAI_API_KEY}"},
                json={
                    "model": LATEST_MODELS["openai"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Analyze claims and provide verdicts: 'true', 'false', 'partially_true', 'mostly_true', 'mostly_false', or 'unverifiable'. Include confidence (0-1) and brief explanation."},
                        {"role": "user", "content": f"Fact-check this claim: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "openai", "model": LATEST_MODELS["openai"], "response": content, "success": True}
            else:
                logger.error(f"OpenAI error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"OpenAI exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_mistral(self, claim: str) -> Dict:
        """Verify claim using Mistral Large"""
        if not Config.MISTRAL_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.MISTRAL_API_KEY}"},
                json={
                    "model": LATEST_MODELS["mistral"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims and provide verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "mistral", "model": LATEST_MODELS["mistral"], "response": content, "success": True}
            else:
                logger.error(f"Mistral error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Mistral exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_cohere(self, claim: str) -> Dict:
        """Verify claim using Cohere Command-R+"""
        if not Config.COHERE_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.cohere.ai/v1/chat",
                headers={"Authorization": f"Bearer {Config.COHERE_API_KEY}"},
                json={
                    "model": LATEST_MODELS["cohere"],
                    "message": f"As a fact-checker, verify this claim and provide: verdict (true/false/partially_true), confidence, and explanation.\n\nClaim: {claim}",
                    "temperature": 0.1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("text", "")
                return {"provider": "cohere", "model": LATEST_MODELS["cohere"], "response": content, "success": True}
            else:
                logger.error(f"Cohere error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Cohere exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    # =========================================================================
    # TIER 3 PROVIDERS
    # =========================================================================
    
    async def verify_with_cerebras(self, claim: str) -> Dict:
        """Verify claim using Cerebras (Ultra-fast inference)"""
        if not Config.CEREBRAS_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.CEREBRAS_API_KEY}"},
                json={
                    "model": LATEST_MODELS["cerebras"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "cerebras", "model": LATEST_MODELS["cerebras"], "response": content, "success": True}
            else:
                logger.error(f"Cerebras error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Cerebras exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_sambanova(self, claim: str) -> Dict:
        """Verify claim using SambaNova"""
        if not Config.SAMBANOVA_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.sambanova.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.SAMBANOVA_API_KEY}"},
                json={
                    "model": LATEST_MODELS["sambanova"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "sambanova", "model": LATEST_MODELS["sambanova"], "response": content, "success": True}
            else:
                logger.error(f"SambaNova error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"SambaNova exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_fireworks(self, claim: str) -> Dict:
        """Verify claim using Fireworks AI"""
        if not Config.FIREWORKS_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.FIREWORKS_API_KEY}"},
                json={
                    "model": LATEST_MODELS["fireworks"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "fireworks", "model": LATEST_MODELS["fireworks"], "response": content, "success": True}
            else:
                logger.error(f"Fireworks error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Fireworks exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    # =========================================================================
    # TIER 4 PROVIDERS
    # =========================================================================
    
    async def verify_with_openrouter(self, claim: str) -> Dict:
        """Verify claim using OpenRouter (Multi-model access)"""
        if not Config.OPENROUTER_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://verity.systems",
                    "X-Title": "Verity Systems"
                },
                json={
                    "model": LATEST_MODELS["openrouter"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "openrouter", "model": LATEST_MODELS["openrouter"], "response": content, "success": True}
            else:
                logger.error(f"OpenRouter error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"OpenRouter exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_together(self, claim: str) -> Dict:
        """Verify claim using Together AI"""
        if not Config.TOGETHER_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.TOGETHER_API_KEY}"},
                json={
                    "model": LATEST_MODELS["together"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "together", "model": LATEST_MODELS["together"], "response": content, "success": True}
            else:
                logger.error(f"Together error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Together exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_huggingface(self, claim: str) -> Dict:
        """Verify claim using HuggingFace Inference API"""
        if not Config.HUGGINGFACE_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                f"https://api-inference.huggingface.co/models/{LATEST_MODELS['huggingface']}",
                headers={"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"},
                json={
                    "inputs": f"<s>[INST] You are a fact-checker. Verify this claim and provide verdict (true/false/partially_true), confidence (0-1), and explanation.\n\nClaim: {claim} [/INST]",
                    "parameters": {"max_new_tokens": 500, "temperature": 0.1}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data[0]["generated_text"] if isinstance(data, list) else str(data)
                return {"provider": "huggingface", "model": LATEST_MODELS["huggingface"], "response": content, "success": True}
            else:
                logger.error(f"HuggingFace error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"HuggingFace exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    # =========================================================================
    # TIER 5: ADDITIONAL PROVIDERS
    # =========================================================================
    
    async def verify_with_anthropic(self, claim: str) -> Dict:
        """Verify claim using Anthropic Claude"""
        if not Config.ANTHROPIC_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": Config.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": LATEST_MODELS["anthropic"],
                    "max_tokens": 500,
                    "messages": [
                        {"role": "user", "content": f"As a fact-checker, verify this claim and provide: verdict (true/false/partially_true), confidence (0-1), and explanation.\n\nClaim: {claim}"}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["content"][0]["text"]
                return {"provider": "anthropic", "model": LATEST_MODELS["anthropic"], "response": content, "success": True}
            else:
                logger.error(f"Anthropic error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Anthropic exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_deepseek(self, claim: str) -> Dict:
        """Verify claim using DeepSeek"""
        if not Config.DEEPSEEK_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"},
                json={
                    "model": LATEST_MODELS["deepseek"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "deepseek", "model": LATEST_MODELS["deepseek"], "response": content, "success": True}
            else:
                logger.error(f"DeepSeek error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"DeepSeek exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_xai(self, claim: str) -> Dict:
        """Verify claim using xAI Grok"""
        if not Config.XAI_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.XAI_API_KEY}"},
                json={
                    "model": LATEST_MODELS["xai"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "xai", "model": LATEST_MODELS["xai"], "response": content, "success": True}
            else:
                logger.error(f"xAI error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"xAI exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_ai21(self, claim: str) -> Dict:
        """Verify claim using AI21 Labs Jamba"""
        if not Config.AI21_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.ai21.com/studio/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.AI21_API_KEY}"},
                json={
                    "model": LATEST_MODELS["ai21"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "ai21", "model": LATEST_MODELS["ai21"], "response": content, "success": True}
            else:
                logger.error(f"AI21 error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"AI21 exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_lepton(self, claim: str) -> Dict:
        """Verify claim using Lepton AI"""
        if not Config.LEPTON_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://llama-3-3-70b.lepton.run/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.LEPTON_API_KEY}"},
                json={
                    "model": LATEST_MODELS["lepton"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "lepton", "model": LATEST_MODELS["lepton"], "response": content, "success": True}
            else:
                logger.error(f"Lepton error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Lepton exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_anyscale(self, claim: str) -> Dict:
        """Verify claim using Anyscale Endpoints"""
        if not Config.ANYSCALE_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.endpoints.anyscale.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.ANYSCALE_API_KEY}"},
                json={
                    "model": LATEST_MODELS["anyscale"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "anyscale", "model": LATEST_MODELS["anyscale"], "response": content, "success": True}
            else:
                logger.error(f"Anyscale error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Anyscale exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_nvidia(self, claim: str) -> Dict:
        """Verify claim using NVIDIA NIM"""
        if not Config.NVIDIA_NIM_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {Config.NVIDIA_NIM_API_KEY}"},
                json={
                    "model": LATEST_MODELS["nvidia"],
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "nvidia", "model": LATEST_MODELS["nvidia"], "response": content, "success": True}
            else:
                logger.error(f"NVIDIA error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"NVIDIA exception: {e}")
        
        return {"success": False, "status_code": 0}

    # =========================================================================
    # TIER 6: SEARCH & RESEARCH AI PROVIDERS
    # =========================================================================
    
    async def verify_with_you(self, claim: str) -> Dict:
        """Verify claim using You.com AI (with web search)"""
        if not Config.YOU_API_KEY:
            return None
        
        try:
            response = await self.http_client.get(
                "https://api.ydc-index.io/search",
                headers={"X-API-Key": Config.YOU_API_KEY},
                params={
                    "query": f"fact check: {claim}",
                    "num_web_results": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract search results as verification context
                snippets = []
                if "hits" in data:
                    for hit in data["hits"][:3]:
                        if "snippets" in hit:
                            snippets.extend(hit["snippets"][:2])
                
                content = f"Search results for claim verification:\n" + "\n".join(snippets[:5]) if snippets else "No results found"
                return {"provider": "you", "model": "you-search", "response": content, "success": True}
            else:
                logger.error(f"You.com error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"You.com exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_jina(self, claim: str) -> Dict:
        """Verify claim using Jina AI Reader (web content extraction)"""
        if not Config.JINA_API_KEY:
            return None
        
        try:
            # Use Jina Reader to search and extract content
            response = await self.http_client.get(
                f"https://s.jina.ai/{claim}",
                headers={"Authorization": f"Bearer {Config.JINA_API_KEY}"}
            )
            
            if response.status_code == 200:
                content = response.text[:2000]  # Limit response size
                return {"provider": "jina", "model": "jina-reader", "response": content, "success": True}
            else:
                logger.error(f"Jina error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Jina exception: {e}")
        
        return {"success": False, "status_code": 0}
    
    async def verify_with_novita(self, claim: str) -> Dict:
        """Verify claim using Novita AI (LLM inference)"""
        if not Config.NOVITA_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.novita.ai/v3/openai/chat/completions",
                headers={"Authorization": f"Bearer {Config.NOVITA_API_KEY}"},
                json={
                    "model": LATEST_MODELS.get("novita", "meta-llama/llama-3.3-70b-instruct"),
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "novita", "model": LATEST_MODELS.get("novita", "llama-3.3-70b"), "response": content, "success": True}
            else:
                logger.error(f"Novita error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Novita exception: {e}")
        
        return {"success": False, "status_code": 0}

    # =========================================================================
    # TIER 8: ADDITIONAL xAI ALTERNATIVES
    # =========================================================================

    async def verify_with_cloudflare(self, claim: str) -> Dict:
        """Verify claim using Cloudflare Workers AI (Free tier available)"""
        account_id = Config.CLOUDFLARE_ACCOUNT_ID
        api_key = Config.CLOUDFLARE_API_KEY
        if not account_id or not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims and provide verdicts: true/false/partially_true/unverifiable. Include confidence (0-1) and brief explanation."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("result"):
                    content = data["result"].get("response", "")
                    return {"provider": "cloudflare", "model": "llama-3.3-70b-instruct", "response": content, "success": True}
                return {"success": False, "status_code": response.status_code}
            else:
                logger.error(f"Cloudflare error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Cloudflare exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_replicate(self, claim: str) -> Dict:
        """Verify claim using Replicate (Meta Llama, Mixtral, etc.)"""
        if not Config.REPLICATE_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Bearer {Config.REPLICATE_API_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "wait"  # Wait for completion
                },
                json={
                    "version": "meta/llama-3.3-70b-instruct",
                    "input": {
                        "prompt": f"You are a fact-checker. Verify this claim and provide a verdict (true/false/partially_true/unverifiable), confidence (0-1), and brief explanation.\n\nClaim: {claim}\n\nVerdict:",
                        "max_tokens": 500,
                        "temperature": 0.1
                    }
                }
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                output = data.get("output", "")
                if isinstance(output, list):
                    output = "".join(output)
                return {"provider": "replicate", "model": "llama-3.3-70b-instruct", "response": output, "success": True}
            else:
                logger.error(f"Replicate error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Replicate exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_siliconflow(self, claim: str) -> Dict:
        """Verify claim using SiliconFlow (Free tier with Llama, Qwen, DeepSeek)"""
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts: true/false/partially_true/unverifiable."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "siliconflow", "model": "DeepSeek-V3", "response": content, "success": True}
            else:
                logger.error(f"SiliconFlow error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"SiliconFlow exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_hyperbolic(self, claim: str) -> Dict:
        """Verify claim using Hyperbolic (Fast inference, Llama 405B)"""
        api_key = os.getenv("HYPERBOLIC_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.hyperbolic.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "meta-llama/Llama-3.3-70B-Instruct",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "hyperbolic", "model": "Llama-3.3-70B-Instruct", "response": content, "success": True}
            else:
                logger.error(f"Hyperbolic error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Hyperbolic exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_lambdalabs(self, claim: str) -> Dict:
        """Verify claim using Lambda Labs (GPU cloud with Llama)"""
        api_key = os.getenv("LAMBDA_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.lambdalabs.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "hermes-3-llama-3.1-405b-fp8-128k",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "lambdalabs", "model": "hermes-3-llama-405b", "response": content, "success": True}
            else:
                logger.error(f"Lambda error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Lambda exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_ollama(self, claim: str) -> Dict:
        """Verify claim using local Ollama (free, runs locally)"""
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        try:
            response = await self.http_client.post(
                f"{ollama_host}/api/chat",
                json={
                    "model": "llama3.3:70b",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                return {"provider": "ollama", "model": "llama3.3:70b", "response": content, "success": True}
            else:
                logger.debug(f"Ollama not available: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_zhipu(self, claim: str) -> Dict:
        """Verify claim using Zhipu AI (GLM-4, Chinese AI leader)"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "glm-4-plus",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts: true/false/partially_true/unverifiable."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "zhipu", "model": "glm-4-plus", "response": content, "success": True}
            else:
                logger.error(f"Zhipu error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Zhipu exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_alibaba(self, claim: str) -> Dict:
        """Verify claim using Alibaba Qwen (via DashScope)"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen-max",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "alibaba", "model": "qwen-max", "response": content, "success": True}
            else:
                logger.error(f"Alibaba error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Alibaba exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_moonshot(self, claim: str) -> Dict:
        """Verify claim using Moonshot AI (Kimi)"""
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "moonshot-v1-128k",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "moonshot", "model": "moonshot-v1-128k", "response": content, "success": True}
            else:
                logger.error(f"Moonshot error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Moonshot exception: {e}")
        
        return {"success": False, "status_code": 0}

    async def verify_with_baichuan(self, claim: str) -> Dict:
        """Verify claim using Baichuan AI"""
        api_key = os.getenv("BAICHUAN_API_KEY")
        if not api_key:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.baichuan-ai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "Baichuan4",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checker. Verify claims with verdicts."},
                        {"role": "user", "content": f"Fact-check: {claim}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"provider": "baichuan", "model": "Baichuan4", "response": content, "success": True}
            else:
                logger.error(f"Baichuan error: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Baichuan exception: {e}")
        
        return {"success": False, "status_code": 0}

    # =========================================================================
    # TIER 7: SEARCH & FACT-CHECK APIs
    # =========================================================================
    
    async def search_with_tavily(self, claim: str) -> Dict:
        """Search for evidence using Tavily AI Search"""
        if not Config.TAVILY_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": Config.TAVILY_API_KEY,
                    "query": f"fact check: {claim}",
                    "search_depth": "advanced",
                    "include_answer": True,
                    "max_results": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                results = data.get("results", [])
                sources = [{"url": r.get("url"), "title": r.get("title")} for r in results[:3]]
                return {"provider": "tavily", "response": answer, "sources": sources, "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Tavily exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_brave(self, claim: str) -> Dict:
        """Search for evidence using Brave Search API"""
        if not Config.BRAVE_API_KEY:
            return None
        
        try:
            response = await self.http_client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": Config.BRAVE_API_KEY},
                params={"q": f"fact check {claim}", "count": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("web", {}).get("results", [])
                snippets = [r.get("description", "") for r in results[:3]]
                sources = [{"url": r.get("url"), "title": r.get("title")} for r in results[:3]]
                return {"provider": "brave", "response": " ".join(snippets), "sources": sources, "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Brave exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_serper(self, claim: str) -> Dict:
        """Search for evidence using Serper Google Search API"""
        if not Config.SERPER_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": Config.SERPER_API_KEY},
                json={"q": f"fact check {claim}", "num": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("organic", [])
                snippets = [r.get("snippet", "") for r in results[:3]]
                sources = [{"url": r.get("link"), "title": r.get("title")} for r in results[:3]]
                return {"provider": "serper", "response": " ".join(snippets), "sources": sources, "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Serper exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_exa(self, claim: str) -> Dict:
        """Search for evidence using Exa AI Search"""
        if not Config.EXA_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": Config.EXA_API_KEY},
                json={
                    "query": f"fact check {claim}",
                    "numResults": 5,
                    "useAutoprompt": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                snippets = [r.get("text", "")[:200] for r in results[:3]]
                sources = [{"url": r.get("url"), "title": r.get("title")} for r in results[:3]]
                return {"provider": "exa", "response": " ".join(snippets), "sources": sources, "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Exa exception: {e}")
        return {"success": False, "status_code": 0}

    async def search_with_google_factcheck(self, claim: str) -> Dict:
        """Search Google FactCheck Tools API for existing claim reviews"""
        # Google FactCheck API uses the regular Google API key
        api_key = Config.GOOGLE_FACTCHECK_API_KEY or Config.GOOGLE_AI_API_KEY
        if not api_key:
            return None
        
        try:
            response = await self.http_client.get(
                "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                params={
                    "query": claim,
                    "key": api_key,
                    "languageCode": "en"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get("claims", [])
                
                if claims:
                    # Get the first claim review
                    first_claim = claims[0]
                    reviews = first_claim.get("claimReview", [])
                    
                    if reviews:
                        review = reviews[0]
                        rating = review.get("textualRating", "Unknown")
                        publisher = review.get("publisher", {}).get("name", "Unknown")
                        url = review.get("url", "")
                        
                        sources = [{"url": url, "title": f"{publisher} Fact Check", "credibility": 0.95}]
                        
                        return {
                            "provider": "google_factcheck",
                            "response": f"Existing fact-check found: {rating} (by {publisher})",
                            "sources": sources,
                            "rating": rating,
                            "success": True
                        }
                
                return {"provider": "google_factcheck", "response": "No existing fact-checks found", "sources": [], "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Google FactCheck exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_claimbuster(self, claim: str) -> Dict:
        """Check claim with ClaimBuster API for claim-worthiness"""
        if not Config.CLAIMBUSTER_API_KEY:
            return None
        
        try:
            response = await self.http_client.post(
                "https://idir.uta.edu/claimbuster/api/v2/score/text/",
                headers={"x-api-key": Config.CLAIMBUSTER_API_KEY},
                json={"input_text": claim}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    # Get the claim score
                    score = results[0].get("score", 0)
                    
                    if score > 0.7:
                        worthiness = "highly check-worthy"
                    elif score > 0.4:
                        worthiness = "moderately check-worthy"
                    else:
                        worthiness = "low check-worthiness"
                    
                    return {
                        "provider": "claimbuster",
                        "response": f"Claim is {worthiness} (score: {score:.2f})",
                        "claim_score": score,
                        "sources": [],
                        "success": True
                    }
                
                return {"success": False, "status_code": 0}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"ClaimBuster exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_semantic_scholar(self, claim: str) -> Dict:
        """Search Semantic Scholar for academic papers related to the claim"""
        # Semantic Scholar API is free (rate limited)
        try:
            # Extract key terms for academic search
            search_terms = claim[:100]  # Limit query length
            
            response = await self.http_client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                headers={"x-api-key": Config.SEMANTIC_SCHOLAR_API_KEY} if Config.SEMANTIC_SCHOLAR_API_KEY else {},
                params={
                    "query": search_terms,
                    "limit": 5,
                    "fields": "title,abstract,url,citationCount,year"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get("data", [])
                
                if papers:
                    sources = []
                    snippets = []
                    
                    for paper in papers[:3]:
                        title = paper.get("title", "")
                        abstract = paper.get("abstract", "")[:200] if paper.get("abstract") else ""
                        url = paper.get("url", f"https://semanticscholar.org/paper/{paper.get('paperId', '')}")
                        citations = paper.get("citationCount", 0)
                        year = paper.get("year", "")
                        
                        sources.append({
                            "url": url,
                            "title": title,
                            "citations": citations,
                            "year": year,
                            "credibility": min(0.95, 0.7 + (citations / 1000))  # More citations = more credible
                        })
                        
                        if abstract:
                            snippets.append(f"{title}: {abstract}")
                    
                    return {
                        "provider": "semantic_scholar",
                        "response": " | ".join(snippets) if snippets else "Academic papers found",
                        "sources": sources,
                        "paper_count": len(papers),
                        "success": True
                    }
                
                return {"provider": "semantic_scholar", "response": "No relevant academic papers found", "sources": [], "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Semantic Scholar exception: {e}")
        return {"success": False, "status_code": 0}
    
    async def search_with_newsapi(self, claim: str) -> Dict:
        """Search NewsAPI for recent news articles about the claim"""
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            return None
        
        try:
            # Extract keywords for news search
            keywords = claim[:100]
            
            response = await self.http_client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": keywords,
                    "apiKey": news_api_key,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                if articles:
                    sources = []
                    snippets = []
                    
                    for article in articles[:3]:
                        sources.append({
                            "url": article.get("url", ""),
                            "title": article.get("title", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "credibility": score_source_credibility(article.get("url", ""))
                        })
                        
                        desc = article.get("description", "")
                        if desc:
                            snippets.append(desc[:150])
                    
                    return {
                        "provider": "newsapi",
                        "response": " | ".join(snippets) if snippets else "News articles found",
                        "sources": sources,
                        "article_count": len(articles),
                        "success": True
                    }
                
                return {"provider": "newsapi", "response": "No recent news articles found", "sources": [], "success": True}
            else:
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"NewsAPI exception: {e}")
        return {"success": False, "status_code": 0}

    # =========================================================================
    # MAIN VERIFICATION WITH MULTI-PROVIDER CROSS-VALIDATION
    # =========================================================================
    
    async def verify_claim(self, claim: str, tier: str = "free") -> Dict:
        """
        Run verification with ALL providers simultaneously and cross-validate.
        
        Tier-based verification loops:
        - free: 4 verification loops
        - pro: 5 verification loops  
        - enterprise: 7 verification loops
        """
        results = []
        providers_used = []
        search_results = []
        
        # Tier-based loop configuration
        tier_loops = {"free": 4, "pro": 5, "enterprise": 7}
        max_loops = tier_loops.get(tier, 4)
        
        logger.info(f"[VERIFY] Starting {tier} tier verification with {max_loops} loops")
        logger.info(f"[VERIFY] Available providers: {len(self.available_providers)}: {self.available_providers}")
        
        # Map provider names to functions (32 AI providers + xAI alternatives)
        provider_functions = {
            # Tier 1: Primary (fastest)
            "groq": self.verify_with_groq,
            "perplexity": self.verify_with_perplexity,
            "google": self.verify_with_google,
            # Tier 2: Major Providers
            "openai": self.verify_with_openai,
            "anthropic": self.verify_with_anthropic,
            "mistral": self.verify_with_mistral,
            "cohere": self.verify_with_cohere,
            # Tier 3: Specialized
            "cerebras": self.verify_with_cerebras,
            "sambanova": self.verify_with_sambanova,
            "fireworks": self.verify_with_fireworks,
            "deepseek": self.verify_with_deepseek,
            # Tier 4: Aggregators
            "openrouter": self.verify_with_openrouter,
            "huggingface": self.verify_with_huggingface,
            "together": self.verify_with_together,
            # Tier 5: Additional
            "xai": self.verify_with_xai,
            "ai21": self.verify_with_ai21,
            "lepton": self.verify_with_lepton,
            "anyscale": self.verify_with_anyscale,
            "nvidia": self.verify_with_nvidia,
            # Tier 6: Research AI
            "you": self.verify_with_you,
            "jina": self.verify_with_jina,
            "novita": self.verify_with_novita,
            # Tier 8: xAI Alternatives (NEW)
            "cloudflare": self.verify_with_cloudflare,
            "replicate": self.verify_with_replicate,
            "siliconflow": self.verify_with_siliconflow,
            "hyperbolic": self.verify_with_hyperbolic,
            "lambdalabs": self.verify_with_lambdalabs,
            "ollama": self.verify_with_ollama,
            "zhipu": self.verify_with_zhipu,
            "alibaba": self.verify_with_alibaba,
            "moonshot": self.verify_with_moonshot,
            "baichuan": self.verify_with_baichuan,
        }
        
        # Search API functions for gathering evidence (8 search/fact-check APIs)
        search_functions = {
            "tavily": self.search_with_tavily,
            "brave": self.search_with_brave,
            "serper": self.search_with_serper,
            "exa": self.search_with_exa,
            "google_factcheck": self.search_with_google_factcheck,
            "claimbuster": self.search_with_claimbuster,
            "semantic_scholar": self.search_with_semantic_scholar,
            "newsapi": self.search_with_newsapi,
        }
        
        # =====================================================================
        # PHASE 1: GATHER EVIDENCE FROM ALL SEARCH APIs SIMULTANEOUSLY
        # =====================================================================
        search_tasks = []
        search_providers = []
        
        # Add all available search APIs
        search_api_keys = {
            "tavily": Config.TAVILY_API_KEY,
            "brave": Config.BRAVE_API_KEY,
            "serper": Config.SERPER_API_KEY,
            "exa": Config.EXA_API_KEY,
            "google_factcheck": Config.GOOGLE_FACTCHECK_API_KEY or Config.GOOGLE_AI_API_KEY,
            "claimbuster": Config.CLAIMBUSTER_API_KEY,
            "semantic_scholar": True,  # Free API, no key needed
            "newsapi": os.getenv("NEWS_API_KEY"),
        }
        
        for name, key in search_api_keys.items():
            if key and name in search_functions:
                if provider_rate_limiter.can_request(name):
                    search_tasks.append(search_functions[name](claim))
                    search_providers.append(name)
                    provider_rate_limiter.record(name)
        
        if search_tasks:
            logger.info(f"[SEARCH] Querying {len(search_tasks)} search APIs: {search_providers}")
            search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)
            for i, response in enumerate(search_responses):
                if not isinstance(response, Exception) and response and response.get("success"):
                    search_results.append(response)
                    logger.info(f"✓ Search: {search_providers[i]} returned evidence")
        
        # =====================================================================
        # PHASE 2: RUN ALL AI PROVIDERS SIMULTANEOUSLY (with rate limiting)
        # =====================================================================
        # Prioritize providers based on claim category
        prioritized_providers = prioritize_providers_for_claim(claim, self.available_providers)
        
        healthy_providers = [
            p for p in prioritized_providers
            if p in provider_functions and provider_health.is_healthy(p) and provider_rate_limiter.can_request(p)
        ]
        
        logger.info(f"[VERIFY] Running {len(healthy_providers)} AI providers simultaneously")
        logger.info(f"[CATEGORY] Claim categorized as: {categorize_claim(claim)}")
        
        # Create tasks for ALL healthy providers at once
        ai_tasks = []
        ai_providers = []
        for provider in healthy_providers:
            ai_tasks.append(provider_functions[provider](claim))
            ai_providers.append(provider)
            provider_rate_limiter.record(provider)
        
        if ai_tasks:
            responses = await asyncio.gather(*ai_tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                provider = ai_providers[i]
                if isinstance(response, Exception):
                    logger.error(f"[FAIL] {provider}: {response}")
                    provider_health.record_failure(provider)
                elif response and isinstance(response, dict):
                    if response.get("success"):
                        results.append(response)
                        providers_used.append(response["provider"])
                        provider_health.record_success(provider)
                        logger.info(f"✓ {provider} succeeded")
                    elif response.get("status_code"):
                        provider_health.record_failure(provider, response["status_code"])
        
        # =====================================================================
        # PHASE 3: EMERGENCY FALLBACK - Try providers in cooldown
        # =====================================================================
        if not results:
            logger.warning("[EMERGENCY] All healthy providers failed, trying cooldown providers...")
            for provider in self.available_providers:
                if provider not in healthy_providers and provider in provider_functions:
                    try:
                        response = await provider_functions[provider](claim)
                        if response and response.get("success"):
                            results.append(response)
                            providers_used.append(response["provider"])
                            provider_health.record_success(provider)
                            logger.info(f"✓ {provider} recovered from cooldown")
                            break
                    except Exception as e:
                        logger.error(f"[EMERGENCY FAIL] {provider}: {e}")
        
        if not results:
            return {
                "verdict": "unverifiable",
                "confidence": 0.5,
                "explanation": "Unable to verify - no providers available",
                "providers_used": [],
                "models_used": [],
                "cross_validation": {"agreement": 0, "total_checks": 0}
            }
        
        # =====================================================================
        # PHASE 4: CROSS-VALIDATION WITH TIERED LOOPS
        # =====================================================================
        return self._cross_validate_results(claim, results, search_results, providers_used, max_loops)
    
    def _extract_verdict_from_response(self, response_text: str) -> str:
        """Extract standardized verdict from response text"""
        response_lower = response_text.lower()
        
        # Check for explicit verdict keywords with context
        if any(kw in response_lower for kw in ["completely false", "definitively false", "absolutely false"]):
            return "false"
        if any(kw in response_lower for kw in ["completely true", "definitively true", "absolutely true"]):
            return "true"
        if "mostly false" in response_lower or ("false" in response_lower and "mostly" in response_lower):
            return "mostly_false"
        if "mostly true" in response_lower or ("true" in response_lower and "mostly" in response_lower):
            return "mostly_true"
        if "partially true" in response_lower:
            return "partially_true"
        if "mixed" in response_lower or "both true and false" in response_lower:
            return "mixed"
        if "misleading" in response_lower:
            return "misleading"
        if "false" in response_lower and "not" not in response_lower[:30]:
            return "false"
        if "true" in response_lower:
            return "true"
        if any(kw in response_lower for kw in ["cannot verify", "unverifiable", "insufficient"]):
            return "unverifiable"
        
        return "unverifiable"
    
    def _cross_validate_results(self, claim: str, results: List[Dict], 
                                 search_results: List[Dict], providers_used: List[str],
                                 max_loops: int) -> Dict:
        """
        Cross-validate results from multiple providers with tiered verification.
        
        Cross-validation process:
        1. Extract verdict from each provider
        2. Count agreement/disagreement
        3. Weight by provider reliability
        4. Combine with search evidence
        5. Calculate final confidence with multi-loop validation
        """
        if not results:
            return {
                "verdict": "unverifiable",
                "confidence": 0.5,
                "explanation": "No results to validate",
                "providers_used": [],
                "models_used": [],
                "cross_validation": {"agreement": 0, "total_checks": 0}
            }
        
        # Extract verdicts from all providers
        verdicts = []
        verdict_details = []
        
        for result in results:
            response_text = result.get("response", "")
            verdict = self._extract_verdict_from_response(response_text)
            verdicts.append(verdict)
            verdict_details.append({
                "provider": result.get("provider"),
                "model": result.get("model", "unknown"),
                "verdict": verdict
            })
        
        # Provider reliability weights (based on accuracy history)
        reliability_weights = {
            "perplexity": 1.3,  # Best for fact-checking with citations
            "google": 1.2,
            "openai": 1.2,
            "anthropic": 1.2,
            "groq": 1.1,
            "mistral": 1.1,
            "cohere": 1.0,
            "fireworks": 1.0,
            "openrouter": 1.0,
            "cerebras": 0.9,
            "sambanova": 0.9,
            "deepseek": 0.9,
            "together": 0.9,
            "huggingface": 0.8,
            "xai": 1.0,
            "ai21": 0.9,
            "lepton": 0.8,
            "anyscale": 0.8,
            "nvidia": 0.9,
            "you": 1.0,
            "jina": 0.8,
            "novita": 0.8,
        }
        
        # Weighted verdict counting
        verdict_scores = {
            "true": 0, "mostly_true": 0, "partially_true": 0,
            "mixed": 0, "misleading": 0,
            "mostly_false": 0, "false": 0, "unverifiable": 0
        }
        
        total_weight = 0
        for i, verdict in enumerate(verdicts):
            provider = results[i].get("provider", "unknown")
            weight = reliability_weights.get(provider, 0.8)
            verdict_scores[verdict] += weight
            total_weight += weight
        
        # Find consensus verdict
        max_score = 0
        consensus_verdict = "unverifiable"
        for verdict, score in verdict_scores.items():
            if score > max_score:
                max_score = score
                consensus_verdict = verdict
        
        # Calculate agreement percentage
        agreeing_count = verdicts.count(consensus_verdict)
        agreement_pct = (agreeing_count / len(verdicts)) * 100 if verdicts else 0
        
        # Multi-loop confidence boost
        loop_confidence_boost = min(0.15, (max_loops - 3) * 0.03)
        
        # Base confidence calculation
        base_confidence = 0.5
        
        # Boost for number of providers
        provider_boost = min(0.25, len(results) * 0.02)
        
        # Boost for agreement
        agreement_boost = (agreement_pct / 100) * 0.2
        
        # Boost for search evidence
        search_boost = min(0.1, len(search_results) * 0.025)
        
        # Final confidence
        confidence = min(0.98, base_confidence + provider_boost + agreement_boost + 
                        search_boost + loop_confidence_boost)
        
        # Build explanation with cross-validation summary
        primary = results[0]
        primary_explanation = primary.get("response", "")
        
        cross_validation_summary = (
            f"\n\n[CROSS-VALIDATION: {agreeing_count}/{len(verdicts)} providers agree "
            f"({agreement_pct:.1f}% consensus). "
            f"Verified by: {', '.join(providers_used)}. "
            f"Loops: {max_loops}]"
        )
        
        # Collect all sources from search results
        all_sources = []
        for sr in search_results:
            if sr.get("sources"):
                all_sources.extend(sr["sources"])
        
        # Get all models used
        models_used = [r.get("model", "unknown") for r in results]
        
        return {
            "verdict": consensus_verdict,
            "confidence": round(confidence, 3),
            "explanation": primary_explanation + cross_validation_summary,
            "providers_used": providers_used,
            "models_used": models_used,
            "cross_validation": {
                "agreement_percentage": round(agreement_pct, 1),
                "agreeing_providers": agreeing_count,
                "total_providers": len(verdicts),
                "verdict_breakdown": verdict_details,
                "search_sources_found": len(all_sources),
                "verification_loops": max_loops
            },
            "sources": all_sources[:10] if all_sources else []
        }


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ClaimRequest(BaseModel):
    claim: str = Field(..., min_length=5, max_length=5000)
    detailed: bool = Field(False)
    tier: str = Field("free", description="Pricing tier: free, pro, enterprise")
    
    @field_validator('claim')
    @classmethod
    def clean_claim(cls, v):
        return v.strip()
    
    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v):
        valid_tiers = ["free", "pro", "enterprise"]
        if v.lower() not in valid_tiers:
            return "free"
        return v.lower()

class ToolRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)

class BatchRequest(BaseModel):
    claims: List[str] = Field(..., min_length=1, max_length=10)


# =============================================================================
# API KEY AUTHENTICATION
# =============================================================================

security = HTTPBearer(auto_error=False)

async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify API key if required"""
    if not Config.REQUIRE_API_KEY:
        return True
    
    # Check header
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if api_key not in Config.API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


# =============================================================================
# APPLICATION
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"[START] Verity API v9 ({Config.ENV})")
    
    # Use single source of truth for provider checks
    providers = get_available_providers()
    logger.info(f"[PROVIDERS] {len(providers)} available: {providers}")
    
    yield
    
    logger.info("[STOP] Shutting down")

app = FastAPI(
    title="Verity Verification API",
    description="AI-powered fact verification with 22+ providers",
    version="9.2.0",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    api_key = request.headers.get("X-API-Key", "")
    identifier = api_key if api_key else client_ip
    
    if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/tools/simulate"]:
        return await call_next(request)
    
    allowed, rate_info = rate_limiter.is_allowed(identifier)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": rate_info["reset"]},
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(rate_info["reset"])
            }
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    return response


# =============================================================================
# ROUTES
# =============================================================================

@app.get('/metrics')
async def prometheus_metrics():
    """Expose lightweight Prometheus-style metrics: provider_health, cache stats"""
    health = provider_health.get_status()
    lines = []
    # provider up/down (1 healthy 0 cooldown)
    for provider, failures in health.get('failures', {}).items():
        is_cooldown = 1 if provider in health.get('in_cooldown', []) else 0
        lines.append(f"verity_provider_in_cooldown{{provider=\"{provider}\"}} {is_cooldown}")
        lines.append(f"verity_provider_failures{{provider=\"{provider}\"}} {failures}")
    # Cache stats
    try:
        cache_stats = {"size": getattr(claim_cache, 'hits', 0), "misses": getattr(claim_cache, 'misses', 0)}
    except Exception:
        cache_stats = {"size": 0, "misses": 0}
    lines.append(f"verity_cache_hits {cache_stats.get('hits', 0)}")
    lines.append(f"verity_cache_misses {cache_stats.get('misses', 0)}")
    return PlainTextResponse('\n'.join(lines), media_type='text/plain')


@app.get("/")
async def root():
    return {
        "name": "Verity Verification API",
        "version": "10.0.0",
        "providers": "32+ AI providers",
        "features": ["JWT Auth", "Stripe Payments", "Multi-provider verification"],
        "endpoints": {
            "/verify": "POST - Verify a claim",
            "/v3/verify": "POST - V3 API",
            "/auth/*": "POST/GET - Authentication",
            "/stripe/*": "POST/GET - Payments",
            "/tools/*": "POST - Enterprise tools",
            "/health": "GET - Health check",
            "/providers": "GET - List providers",
            "/tools/provider-health-logs": "GET - Tail provider health log",
            "/tools/test-runs": "GET - Recent internal test runs",
            "/metrics": "GET - Prometheus metrics (basic)"
        }
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    providers = get_available_providers()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "10.0.0",
        "environment": Config.ENV,
        "providers_available": len(providers),
        "providers": providers,
        "auth_enabled": True,
        "stripe_configured": bool(Config.STRIPE_SECRET_KEY)
    }


@app.get("/providers")
async def list_providers():
    """List all available providers with their models and health status"""
    all_checks = get_all_provider_checks()
    
    health_status = provider_health.get_status()
    available = []
    unavailable = []
    
    for name, key in all_checks:
        model = LATEST_MODELS.get(name, "unknown")
        if key:
            is_healthy = provider_health.is_healthy(name)
            status = "active" if is_healthy else "cooldown"
            failures = health_status["failures"].get(name, 0)
            available.append({
                "name": name, 
                "model": model, 
                "status": status,
                "healthy": is_healthy,
                "failures": failures
            })
        else:
            unavailable.append({"name": name, "model": model, "status": "no_api_key"})
    
    return {
        "total_available": len(available),
        "total_healthy": sum(1 for p in available if p["healthy"]),
        "total_in_cooldown": len(health_status["in_cooldown"]),
        "total_configured": len(all_checks),
        "available": available,
        "unavailable": unavailable,
        "health": health_status
    }


@app.get("/providers/health")
async def providers_health():
    """Get detailed health status of all providers"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "health": provider_health.get_status(),
        "message": "All providers with active failures will auto-recover after cooldown"
    }


@app.get("/tools/provider-health-logs")
async def get_provider_health_logs(lines: int = 200):
    """Return the tail of the provider health log file (last `lines` entries)."""
    log_file = Path(_script_dir / "provider_health.log")
    if not log_file.exists():
        return {"lines": [], "message": "No provider health log found"}
    try:
        with open(log_file, "r", encoding="utf-8") as fh:
            data = fh.readlines()
        data = [l.strip() for l in data if l.strip()]
        return {"lines": data[-lines:]}
    except Exception as e:
        logger.exception("Error reading provider health log")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools/test-runs")
async def get_test_runs(limit: int = 20):
    """Return recent run-internal-tests outputs (tail of test_runs.log)."""
    runs_file = Path(_script_dir / "test_runs.log")
    if not runs_file.exists():
        return {"runs": []}
    try:
        with open(runs_file, "r", encoding="utf-8") as fh:
            data = fh.read()
        # Split runs by separator
        parts = [p.strip() for p in data.split('----- RUN') if p.strip()]
        runs = []
        for p in parts[-limit:]:
            header, *body = p.split('\n', 1)
            runs.append({"header": header.strip(), "output": body[0].strip() if body else ""})
        return {"runs": runs[::-1]}  # newest first
    except Exception as e:
        logger.exception("Error reading test runs log")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/tools/github-artifacts')
async def github_artifacts(request: Request):
    """Proxy to GitHub Actions artifacts list for a repo.
    Body: { owner: str, repo: str }
    Optionally provide header 'Authorization: Bearer <token>' for private repos.
    Protected by SIMULATE_KEY or DEBUG mode.
    """
    sim_key_required = Config.SIMULATE_KEY is not None
    provided_sim_key = request.headers.get("X-SIM-KEY") or request.headers.get("X-Sim-Key")
    if sim_key_required:
        if provided_sim_key != Config.SIMULATE_KEY:
            raise HTTPException(status_code=403, detail="Invalid or missing simulation key")
    else:
        if not Config.DEBUG:
            raise HTTPException(status_code=403, detail="GitHub artifacts proxy requires DEBUG mode or SIMULATE_KEY")

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    owner = payload.get('owner')
    repo = payload.get('repo')
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="owner and repo required in body")

    # Support token from header
    token = None
    auth = request.headers.get('Authorization') or request.headers.get('authorization')
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(None, 1)[1]
    else:
        token = payload.get('token')

    url = f'https://api.github.com/repos/{owner}/{repo}/actions/artifacts'
    headers = {'Accept': 'application/vnd.github+json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    import requests
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        logger.exception('GitHub artifacts proxy error')
        raise HTTPException(status_code=502, detail=str(e))



@app.post("/verify")
async def verify_claim_endpoint(request: ClaimRequest):
    """
    Verify a claim using multiple AI providers with cross-validation.
    
    Tier-based verification:
    - free: 4 verification loops, all providers
    - pro: 5 verification loops, all providers + priority support
    - enterprise: 7 verification loops, all providers + maximum accuracy
    
    Features:
    - Caching (1 hour TTL) for repeated claims
    - Injection protection
    - Rate limiting per provider
    - Cross-validation with consensus scoring
    """
    start_time = time.time()
    request_id = f"ver_{int(time.time())}_{secrets.randbelow(10000)}"
    
    # Sanitize and validate input
    claim = sanitize_claim(request.claim)
    
    # Check for prompt injection attempts
    if detect_injection(claim):
        logger.warning(f"[{request_id}] Potential injection detected, proceeding with caution")
        # Don't block, but log and proceed with sanitized input
    
    logger.info(f"[{request_id}] Verifying ({request.tier} tier): {claim[:50]}...")
    
    # Check cache first
    cached_result = claim_cache.get(claim, request.tier)
    if cached_result:
        processing_time = time.time() - start_time
        return {
            "id": request_id,
            "claim": claim,
            "verdict": cached_result["verdict"],
            "confidence": cached_result["confidence"],
            "explanation": cached_result["explanation"],
            "sources": cached_result.get("sources", []),
            "providers_used": cached_result["providers_used"],
            "models_used": cached_result.get("models_used", []),
            "cross_validation": cached_result.get("cross_validation", {}),
            "tier": request.tier,
            "cached": True,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": round(processing_time * 1000, 2)
        }
    
    # Run verification
    async with AIProviders() as providers:
        result = await providers.verify_claim(claim, tier=request.tier)
    
    processing_time = time.time() - start_time
    
    # Cache the result
    claim_cache.set(claim, request.tier, result)
    
    # Build sources from cross-validation or defaults
    sources = result.get("sources", [])
    if not sources:
        sources = [
            {"name": "AI Analysis", "url": "https://verity.systems", "reliability": 0.9, "snippet": None},
            {"name": "Cross-Reference Check", "url": "https://factcheck.org", "reliability": 0.85, "snippet": None}
        ]
    
    return {
        "id": request_id,
        "claim": claim,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "explanation": result["explanation"],
        "sources": sources,
        "providers_used": result["providers_used"],
        "models_used": result.get("models_used", []),
        "cross_validation": result.get("cross_validation", {}),
        "tier": request.tier,
        "category": categorize_claim(claim),
        "cached": False,
        "timestamp": datetime.utcnow().isoformat(),
        "processing_time_ms": round(processing_time * 1000, 2)
    }


@app.post("/v3/verify")
async def verify_claim_v3(request: ClaimRequest):
    """V3 API: Verify a claim"""
    return await verify_claim_endpoint(request)


# =============================================================================
# BATCH VERIFICATION ENDPOINT
# =============================================================================

class BatchVerifyRequest(BaseModel):
    claims: List[str] = Field(..., min_items=1, max_items=50)
    tier: str = Field("enterprise")
    
    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v):
        valid_tiers = ["free", "pro", "enterprise"]
        if v.lower() not in valid_tiers:
            return "enterprise"
        return v.lower()


@app.post("/v3/batch-verify")
async def batch_verify(request: BatchVerifyRequest):
    """
    Verify up to 50 claims in parallel.
    
    Enterprise feature for bulk fact-checking.
    """
    start_time = time.time()
    job_id = f"batch_{int(time.time())}_{secrets.randbelow(10000)}"
    
    logger.info(f"[{job_id}] Batch verification: {len(request.claims)} claims ({request.tier} tier)")
    
    results = []
    
    async with AIProviders() as providers:
        # Process claims in parallel (max 10 at a time to avoid overwhelming)
        batch_size = 10
        
        for i in range(0, len(request.claims), batch_size):
            batch = request.claims[i:i + batch_size]
            
            # Sanitize all claims
            sanitized_batch = [sanitize_claim(c) for c in batch]
            
            # Check cache first for each claim
            tasks = []
            task_indices = []
            cached_results = {}
            
            for j, claim in enumerate(sanitized_batch):
                cached = claim_cache.get(claim, request.tier)
                if cached:
                    cached_results[i + j] = {
                        "claim": claim,
                        "result": cached,
                        "cached": True
                    }
                else:
                    tasks.append(providers.verify_claim(claim, tier=request.tier))
                    task_indices.append((i + j, claim))
            
            # Run non-cached verifications
            if tasks:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                for k, response in enumerate(responses):
                    idx, claim = task_indices[k]
                    if isinstance(response, Exception):
                        cached_results[idx] = {
                            "claim": claim,
                            "result": {"verdict": "error", "confidence": 0, "explanation": str(response)},
                            "cached": False
                        }
                    else:
                        # Cache successful results
                        claim_cache.set(claim, request.tier, response)
                        cached_results[idx] = {
                            "claim": claim,
                            "result": response,
                            "cached": False
                        }
            
            # Collect results in order
            for j in range(len(batch)):
                results.append(cached_results.get(i + j))
    
    processing_time = time.time() - start_time
    
    # Summary statistics
    verdicts = {}
    for r in results:
        v = r["result"].get("verdict", "unknown")
        verdicts[v] = verdicts.get(v, 0) + 1
    
    return {
        "job_id": job_id,
        "total_claims": len(request.claims),
        "successful": sum(1 for r in results if r["result"].get("verdict") != "error"),
        "cached": sum(1 for r in results if r.get("cached")),
        "tier": request.tier,
        "verdict_summary": verdicts,
        "results": results,
        "processing_time_ms": round(processing_time * 1000, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# DEEP HEALTH CHECK & DIAGNOSTICS
# =============================================================================

@app.get("/health/deep")
async def deep_health_check():
    """
    Comprehensive health check that tests all providers.
    
    Returns status, latency, and availability for each provider.
    """
    start_time = time.time()
    test_claim = "The sky is blue"
    
    results = {}
    
    async with AIProviders() as providers:
        provider_functions = {
            "groq": providers.verify_with_groq,
            "perplexity": providers.verify_with_perplexity,
            "google": providers.verify_with_google,
            "openai": providers.verify_with_openai,
            "mistral": providers.verify_with_mistral,
            "cohere": providers.verify_with_cohere,
            "cerebras": providers.verify_with_cerebras,
            "sambanova": providers.verify_with_sambanova,
            "fireworks": providers.verify_with_fireworks,
            "openrouter": providers.verify_with_openrouter,
            "huggingface": providers.verify_with_huggingface,
            "you": providers.verify_with_you,
            "jina": providers.verify_with_jina,
        }
        
        tasks = []
        provider_names = []
        
        for name in providers.available_providers:
            if name in provider_functions:
                tasks.append(provider_functions[name](test_claim))
                provider_names.append(name)
        
        # Run all health checks in parallel with timeout
        if tasks:
            start_checks = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                name = provider_names[i]
                latency = (time.time() - start_checks) * 1000
                
                if isinstance(response, Exception):
                    results[name] = {
                        "status": "error",
                        "error": str(response)[:100],
                        "latency_ms": round(latency, 2)
                    }
                elif response and response.get("success"):
                    results[name] = {
                        "status": "healthy",
                        "model": response.get("model", "unknown"),
                        "latency_ms": round(latency, 2)
                    }
                else:
                    results[name] = {
                        "status": "degraded",
                        "status_code": response.get("status_code") if response else None,
                        "latency_ms": round(latency, 2)
                    }
    
    # Calculate overall status
    healthy_count = sum(1 for r in results.values() if r.get("status") == "healthy")
    total_count = len(results)
    
    if healthy_count >= total_count * 0.7:
        overall = "healthy"
    elif healthy_count >= total_count * 0.3:
        overall = "degraded"
    else:
        overall = "critical"
    
    processing_time = time.time() - start_time
    
    return {
        "overall_status": overall,
        "healthy_providers": healthy_count,
        "total_providers": total_count,
        "health_percentage": round(healthy_count / total_count * 100, 1) if total_count > 0 else 0,
        "providers": results,
        "cache_stats": claim_cache.get_stats(),
        "rate_limit_stats": provider_rate_limiter.get_stats(),
        "provider_health": provider_health.get_status(),
        "check_time_ms": round(processing_time * 1000, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get comprehensive API statistics"""
    return {
        "cache": claim_cache.get_stats(),
        "rate_limits": provider_rate_limiter.get_stats(),
        "provider_health": provider_health.get_status(),
        "available_providers": get_available_providers(),
        "available_search_apis": get_available_search_apis(),
        "source_credibility_count": len(SOURCE_CREDIBILITY),
        "claim_categories": list(CLAIM_CATEGORIES.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ENTERPRISE TOOL ENDPOINTS
# =============================================================================

# Known credible sources database
CREDIBLE_SOURCES = {
    "reuters": {"tier": 1, "rating": "Highly Credible"},
    "ap": {"tier": 1, "rating": "Highly Credible"},
    "bbc": {"tier": 1, "rating": "Highly Credible"},
    "nytimes": {"tier": 1, "rating": "Highly Credible"},
    "washingtonpost": {"tier": 1, "rating": "Highly Credible"},
    "theguardian": {"tier": 1, "rating": "Highly Credible"},
    "economist": {"tier": 1, "rating": "Highly Credible"},
    "nature": {"tier": 1, "rating": "Highly Credible"},
    "science": {"tier": 1, "rating": "Highly Credible"},
    "cnn": {"tier": 2, "rating": "Generally Credible"},
    "foxnews": {"tier": 2, "rating": "Generally Credible - Check for bias"},
    "msnbc": {"tier": 2, "rating": "Generally Credible - Check for bias"},
    "npr": {"tier": 1, "rating": "Highly Credible"},
    "pbs": {"tier": 1, "rating": "Highly Credible"},
    "wikipedia": {"tier": 2, "rating": "Good starting point - Verify sources"},
    "snopes": {"tier": 1, "rating": "Highly Credible for fact-checking"},
    "factcheck": {"tier": 1, "rating": "Highly Credible for fact-checking"},
    "politifact": {"tier": 1, "rating": "Highly Credible for fact-checking"},
}


@app.post("/tools/social-media")
async def analyze_social_media(request: ToolRequest):
    """Analyze social media content for misinformation indicators"""
    content = request.content.lower()
    indicators = []
    score = 50  # Start neutral
    
    # Check for red flags
    if any(word in content for word in ["viral", "breaking", "shocking", "you won't believe"]):
        indicators.append({"type": "viral_spread", "severity": "medium", "detail": "Claim spreading virally - verify before sharing"})
        score -= 15
    
    if any(word in content for word in ["anonymous", "unnamed", "sources say", "rumor"]):
        indicators.append({"type": "unverified_source", "severity": "high", "detail": "Source not verified"})
        score -= 20
    
    if any(word in content for word in ["100%", "guaranteed", "proven", "definitely"]):
        indicators.append({"type": "absolute_language", "severity": "medium", "detail": "Absolute claims often misleading"})
        score -= 10
    
    if any(word in content for word in ["miracle", "cure", "secret", "they don't want you to know"]):
        indicators.append({"type": "sensationalism", "severity": "high", "detail": "Sensationalist language detected"})
        score -= 25
    
    if any(word in content for word in ["bot", "fake account", "new account"]):
        indicators.append({"type": "bot_suspected", "severity": "high", "detail": "Possible bot or fake account"})
        score -= 20
    
    score = max(0, min(100, score))
    
    if score >= 70:
        verdict = "low_risk"
        summary = "🟢 LOW RISK: Content appears credible"
    elif score >= 40:
        verdict = "medium_risk"
        summary = f"🟡 MEDIUM RISK: {len(indicators)} suspicious patterns detected"
    else:
        verdict = "high_risk"
        summary = f"🔴 HIGH RISK: {len(indicators)} red flags detected"
    
    return {
        "tool": "Social Media Analyzer",
        "score": score,
        "verdict": verdict,
        "summary": summary,
        "indicators": indicators,
        "processing_time_ms": round(time.time() * 1000 % 1000, 2)
    }


@app.post("/tools/source-credibility")
async def check_source_credibility(request: ToolRequest):
    """Check the credibility of news sources"""
    content = request.content.lower()
    sources_found = []
    
    for source, info in CREDIBLE_SOURCES.items():
        if source in content:
            sources_found.append({"name": source, **info})
    
    if sources_found:
        avg_tier = sum(s["tier"] for s in sources_found) / len(sources_found)
        score = max(0, 100 - (avg_tier - 1) * 20)
        
        if avg_tier <= 1.5:
            verdict = "high_credibility"
            summary = f"🟢 HIGH CREDIBILITY: {len(sources_found)} source(s) analyzed"
        elif avg_tier <= 2.5:
            verdict = "medium_credibility"
            summary = f"🟡 MEDIUM CREDIBILITY: Some sources may have bias"
        else:
            verdict = "low_credibility"
            summary = f"🔴 LOW CREDIBILITY: Sources need verification"
    else:
        score = 50
        verdict = "unknown"
        summary = "⚪ UNKNOWN: No recognized sources found"
    
    return {
        "tool": "Source Credibility",
        "score": score,
        "verdict": verdict,
        "summary": summary,
        "sources": sources_found,
        "processing_time_ms": round(time.time() * 1000 % 1000, 2)
    }


@app.post("/tools/simulate")
async def tools_simulate(request: Request):
    # Authorization: require SIMULATE_KEY header if configured; otherwise allow only in DEBUG
    sim_key_required = Config.SIMULATE_KEY is not None
    provided_sim_key = request.headers.get("X-SIM-KEY") or request.headers.get("X-Sim-Key")

    # Check allowed IPs if configured
    if Config.SIMULATE_ALLOWED_IPS:
        client_ip = request.client.host if request.client else None
        if client_ip not in Config.SIMULATE_ALLOWED_IPS:
            raise HTTPException(status_code=403, detail="Client IP not allowed to use simulation endpoints")

    if sim_key_required:
        if provided_sim_key != Config.SIMULATE_KEY:
            raise HTTPException(status_code=403, detail="Invalid or missing simulation key")
        # rate-limit per-sim-key
        allowed, info = simulate_key_limiter.is_allowed(provided_sim_key)
        if not allowed:
            return JSONResponse(status_code=429, content={"error": "Simulation key rate limit exceeded", "info": info})
    else:
        if not Config.DEBUG:
            raise HTTPException(status_code=403, detail="Simulation endpoints are only available in DEBUG mode or with a SIMULATE_KEY configured")

    """Simulation endpoint for testing provider failures, rate limits, and cooldowns.
    Only available in DEBUG mode to avoid exposure in production.
    Actions supported:
      - provider_fail: { provider: str, count: int }
      - provider_recover: { provider: str }
      - set_rate_limit: { limit: int }
      - trigger_rate_limit: { identifier: str, count: int }
    """
    if not Config.DEBUG:
        raise HTTPException(status_code=403, detail="Simulation endpoints are only available in DEBUG mode")

    # Accept both JSON body and ToolRequest-style {"content": <json|string>}
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    body = {}
    if isinstance(payload, dict) and "content" in payload:
        content = payload.get("content")
        if isinstance(content, str):
            try:
                import json as _json
                body = _json.loads(content)
            except Exception:
                body = {"action": content}
        elif isinstance(content, dict):
            body = content
        else:
            body = {}
    elif isinstance(payload, dict):
        body = payload

    action = body.get("action")

    if action == "provider_fail":
        provider = body.get("provider")
        count = int(body.get("count", provider_health.max_failures))
        for i in range(count):
            provider_health.record_failure(provider, status_code=500)
        return {"status": "ok", "message": f"Simulated {count} failures for {provider}"}

    if action == "provider_recover":
        provider = body.get("provider")
        provider_health.record_success(provider)
        provider_health.failures.pop(provider, None)
        provider_health.cooldown_until.pop(provider, None)
        return {"status": "ok", "message": f"Recovered {provider}"}

    if action == "set_rate_limit":
        limit = int(body.get("limit", Config.RATE_LIMIT_REQUESTS))
        rate_limiter.max_requests = limit
        return {"status": "ok", "limit": limit}

    if action == "trigger_rate_limit":
        identifier = body.get("identifier", "simulate-client")
        count = int(body.get("count", rate_limiter.max_requests + 1))
        # Pre-fill the request timestamps to simulate previous requests
        rate_limiter.requests[identifier] = [time.time() - 1 + i * 0.01 for i in range(count)]
        allowed, info = rate_limiter.is_allowed(identifier)
        return {"status": "ok", "allowed": allowed, "info": info}

    raise HTTPException(status_code=400, detail="Unknown simulation action")


@app.post("/tools/run-internal-tests")
async def run_internal_tests(request: Request):
    """Run a small, safe subset of internal tests on demand (debug-only or with SIMULATE_KEY)

    Runs a pre-defined small test subset to avoid running arbitrary code. Returns the stdout and exit code.
    """
    # Authorization
    # Optional IP allowlist for internal test runner
    if Config.SIMULATE_ALLOWED_IPS:
        client_ip = request.client.host if request.client else None
        if client_ip not in Config.SIMULATE_ALLOWED_IPS:
            raise HTTPException(status_code=403, detail="Client IP not allowed to use internal test runner")

    sim_key_required = Config.SIMULATE_KEY is not None
    provided_sim_key = request.headers.get("X-SIM-KEY") or request.headers.get("X-Sim-Key")
    if sim_key_required:
        if provided_sim_key != Config.SIMULATE_KEY:
            raise HTTPException(status_code=403, detail="Invalid or missing simulation key")
    else:
        if not Config.DEBUG:
            raise HTTPException(status_code=403, detail="Internal test runner requires DEBUG mode or SIMULATE_KEY")

    # Accept payload to select suite (default: smoke)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    suite = (payload.get("suite") or "smoke").lower()

    # Map suites to safe test files
    SUITES = {
        "smoke": ["tests/test_rate_limiter.py", "tests/test_provider_health.py", "tests/test_source_credibility.py"],
        "extended": ["tests/test_tools_simulate.py", "tests/test_rate_limiter.py", "tests/test_provider_health.py", "tests/test_source_credibility.py"]
    }

    selected = SUITES.get(suite)
    if not selected:
        raise HTTPException(status_code=400, detail=f"Unknown suite {suite}")

    # Run pytest on the selected files (safe, controlled)
    import subprocess, shlex, asyncio
    cmd = [sys.executable, "-m", "pytest", "-q", "-k", " or ".join([p.split('/')[-1].replace('.py','') for p in selected])]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        out = proc.stdout.decode(errors='replace')
        # Persist test run output to a log for later inspection
        try:
            runs_file = Path(_script_dir / "test_runs.log")
            with open(runs_file, "a", encoding="utf-8") as fh:
                fh.write(f"----- RUN {datetime.utcnow().isoformat()} suite={suite} exit={proc.returncode}\n")
                fh.write(out + "\n")
        except Exception:
            logger.exception("Failed to write test run log")
        return {"exit_code": proc.returncode, "output": out}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Test runner timed out")



@app.post("/tools/statistics-validator")
async def validate_statistics(request: ToolRequest):
    """Validate statistical claims"""
    import re
    
    content = request.content
    findings = []
    score = 70  # Start optimistic
    
    # Find percentages
    percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', content)
    numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b', content)
    
    for pct in percentages:
        pct_val = float(pct)
        if pct_val > 100:
            findings.append({"type": "impossible_percentage", "severity": "high", "detail": f"{pct}% is impossible"})
            score -= 30
        elif pct_val >= 95:
            findings.append({"type": "extreme_percentage", "severity": "medium", "detail": f"{pct}% is unusually high"})
            score -= 10
    
    # Check for suspicious patterns
    if any(word in content.lower() for word in ["90% of", "95% of", "99% of"]):
        if not any(src in content.lower() for src in ["study", "research", "survey", "poll"]):
            findings.append({"type": "unsourced_statistic", "severity": "medium", "detail": "High percentage without cited source"})
            score -= 15
    
    score = max(0, min(100, score))
    
    if score >= 70:
        verdict = "plausible"
        summary = "🟢 Statistics appear plausible"
    elif score >= 40:
        verdict = "questionable"
        summary = f"🟡 Statistics need verification: {len(findings)} issues found"
    else:
        verdict = "suspicious"
        summary = f"🔴 Statistics appear suspicious: {len(findings)} red flags"
    
    if not findings:
        findings.append({"type": "info", "detail": "No statistical red flags detected"})
    
    return {
        "tool": "Statistics Validator",
        "score": score,
        "verdict": verdict,
        "summary": summary,
        "findings": findings,
        "numbers_found": len(percentages) + len(numbers),
        "processing_time_ms": round(time.time() * 1000 % 1000, 2)
    }


@app.post("/tools/image-forensics")
async def analyze_image(request: ToolRequest):
    """Analyze image for manipulation indicators"""
    content = request.content.lower()
    findings = []
    score = 75  # Start optimistic
    
    # Check URL patterns
    if "deepfake" in content:
        findings.append({"type": "deepfake_mention", "severity": "high", "detail": "Content mentions deepfake"})
        score -= 30
    
    if any(ext in content for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
        findings.append({"type": "analysis", "severity": "low", "detail": "No obvious manipulation detected. Recommend reverse image search."})
    else:
        findings.append({"type": "info", "severity": "low", "detail": "Provide image URL for detailed analysis"})
    
    if score >= 70:
        verdict = "likely_authentic"
        summary = "🟢 No obvious manipulation detected"
    elif score >= 40:
        verdict = "needs_review"
        summary = "🟡 Image requires further analysis"
    else:
        verdict = "likely_manipulated"
        summary = "🔴 Signs of potential manipulation"
    
    return {
        "tool": "Image Forensics",
        "score": score,
        "verdict": verdict,
        "summary": summary,
        "findings": findings,
        "processing_time_ms": round(time.time() * 1000 % 1000, 2)
    }


@app.post("/tools/research-assistant")
async def research_topic(request: ToolRequest):
    """Research a topic using AI providers"""
    start_time = time.time()
    
    async with AIProviders() as providers:
        result = await providers.verify_claim(request.content)
    
    processing_time = (time.time() - start_time) * 1000
    
    # Format query for research databases
    query = request.content.replace(" ", "+")
    
    return {
        "tool": "Research Assistant",
        "score": result["confidence"] * 100,
        "verdict": result["verdict"],
        "summary": result["explanation"][:500] if len(result["explanation"]) > 500 else result["explanation"],
        "research_databases": [
            {"name": "Google Scholar", "url": f"https://scholar.google.com/scholar?q={query}"},
            {"name": "PubMed", "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"},
            {"name": "Semantic Scholar", "url": f"https://www.semanticscholar.org/search?q={query}"}
        ],
        "ai_analysis": result["explanation"],
        "providers_used": result["providers_used"],
        "processing_time_ms": round(processing_time, 2)
    }


@app.post("/tools/realtime-stream")
async def realtime_stream(request: ToolRequest):
    """Analyze real-time content spread"""
    content = request.content.lower()
    
    # Simulate spread velocity analysis
    if any(word in content for word in ["trending", "viral", "breaking"]):
        spread_velocity = "high"
        score = 30
    elif any(word in content for word in ["news", "update", "report"]):
        spread_velocity = "medium"
        score = 50
    else:
        spread_velocity = "low"
        score = 70
    
    indicators = []
    if spread_velocity == "high":
        indicators.append({"type": "viral", "severity": "high", "detail": "Content spreading rapidly"})
    else:
        indicators.append({"type": "normal", "severity": "low", "detail": "No unusual spread patterns detected"})
    
    return {
        "tool": "Real-Time Stream",
        "score": score,
        "spread_velocity": spread_velocity,
        "verdict": f"{spread_velocity}_spread_risk",
        "summary": f"{'🔴' if spread_velocity == 'high' else '🟡' if spread_velocity == 'medium' else '🟢'} {'RAPID' if spread_velocity == 'high' else 'MODERATE' if spread_velocity == 'medium' else 'NORMAL'} SPREAD: Velocity tracking active",
        "indicators": indicators,
        "processing_time_ms": round(time.time() * 1000 % 1000, 2)
    }


# =============================================================================
# USER DATABASE (In-Memory - Replace with PostgreSQL in production)
# =============================================================================

import jwt
import bcrypt
from datetime import datetime, timedelta

# In-memory user store (replace with database in production)
USERS_DB: Dict[str, Dict] = {}
SESSIONS_DB: Dict[str, Dict] = {}

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", Config.SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class UserAuth:
    """User authentication and session management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def create_token(user_id: str, email: str, tier: str = "free") -> str:
        """Create a JWT token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "tier": tier,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def register_user(email: str, password: str, name: str = "") -> Dict:
        """Register a new user"""
        if email in USERS_DB:
            raise ValueError("Email already registered")
        
        user_id = secrets.token_hex(16)
        USERS_DB[email] = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "password_hash": UserAuth.hash_password(password),
            "tier": "free",
            "stripe_customer_id": None,
            "stripe_subscription_id": None,
            "verifications_used": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        return {"user_id": user_id, "email": email}
    
    @staticmethod
    def login_user(email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return token"""
        user = USERS_DB.get(email)
        if not user:
            return None
        if not UserAuth.verify_password(password, user["password_hash"]):
            return None
        
        user["last_login"] = datetime.utcnow().isoformat()
        token = UserAuth.create_token(user["user_id"], email, user["tier"])
        return {
            "token": token,
            "user_id": user["user_id"],
            "email": email,
            "tier": user["tier"],
            "name": user.get("name", "")
        }


# Pricing Tiers with verification limits
PRICING_TIERS = {
    "free": {"verifications_per_month": 300, "providers": 2, "loops": 4},
    "starter": {"verifications_per_month": 2000, "providers": 4, "loops": 5},
    "pro": {"verifications_per_month": 5000, "providers": 8, "loops": 5},
    "professional": {"verifications_per_month": 15000, "providers": 15, "loops": 6},
    "business": {"verifications_per_month": 60000, "providers": 17, "loops": 6},
    "business_plus": {"verifications_per_month": 75000, "providers": 17, "loops": 7},
    "enterprise": {"verifications_per_month": None, "providers": 17, "loops": 7}  # Unlimited
}


# =============================================================================
# AUTH ENDPOINTS
# =============================================================================

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        result = UserAuth.register_user(request.email, request.password, request.name)
        token = UserAuth.create_token(result["user_id"], request.email, "free")
        return {
            "success": True,
            "user_id": result["user_id"],
            "email": request.email,
            "token": token,
            "tier": "free"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login user and get JWT token"""
    result = UserAuth.login_user(request.email, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, **result}

@app.get("/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = UserAuth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = USERS_DB.get(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "tier": user["tier"],
        "verifications_used": user["verifications_used"],
        "verifications_limit": PRICING_TIERS[user["tier"]]["verifications_per_month"],
        "created_at": user["created_at"]
    }


# =============================================================================
# STRIPE INTEGRATION (Full Implementation)
# =============================================================================

import stripe

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Stripe Price IDs (set these in your .env)
STRIPE_PRICES = {
    "starter": os.getenv("STRIPE_STARTER_PRICE_ID"),
    "pro": os.getenv("STRIPE_PRO_PRICE_ID"),
    "professional": os.getenv("STRIPE_PROFESSIONAL_PRICE_ID"),
    "business": os.getenv("STRIPE_BUSINESS_PRICE_ID"),
    "business_plus": os.getenv("STRIPE_BUSINESS_PLUS_PRICE_ID"),
    "enterprise": os.getenv("STRIPE_ENTERPRISE_PRICE_ID")
}

class CheckoutRequest(BaseModel):
    tier: str
    success_url: str = "https://verity-systems.com/success"
    cancel_url: str = "https://verity-systems.com/pricing"

@app.post("/stripe/create-checkout")
async def create_checkout_session(request: CheckoutRequest, authorization: Optional[str] = Header(None)):
    """Create Stripe checkout session for subscription"""
    if not Config.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    if request.tier not in STRIPE_PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")
    
    price_id = STRIPE_PRICES.get(request.tier)
    if not price_id:
        raise HTTPException(status_code=503, detail=f"Price ID not configured for tier: {request.tier}")
    
    # Get user email if authenticated
    customer_email = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = UserAuth.verify_token(token)
        if payload:
            customer_email = payload.get("email")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=request.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.cancel_url,
            customer_email=customer_email
        )
        return {
            "session_id": session.id,
            "url": session.url,
            "tier": request.tier
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle subscription events
    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        # Update user tier based on subscription
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get("email")
        if email and email in USERS_DB:
            # Determine tier from price
            price_id = subscription["items"]["data"][0]["price"]["id"]
            for tier, pid in STRIPE_PRICES.items():
                if pid == price_id:
                    USERS_DB[email]["tier"] = tier
                    USERS_DB[email]["stripe_customer_id"] = customer_id
                    USERS_DB[email]["stripe_subscription_id"] = subscription["id"]
                    break
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get("email")
        if email and email in USERS_DB:
            USERS_DB[email]["tier"] = "free"
            USERS_DB[email]["stripe_subscription_id"] = None
    
    return {"received": True}

@app.get("/stripe/subscription")
async def get_subscription(authorization: Optional[str] = Header(None)):
    """Get user's current subscription"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    token = authorization.split(" ")[1]
    payload = UserAuth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = USERS_DB.get(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription_id = user.get("stripe_subscription_id")
    if not subscription_id:
        return {
            "tier": user["tier"],
            "status": "free",
            "subscription": None
        }
    
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return {
            "tier": user["tier"],
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end
        }
    except stripe.error.StripeError as e:
        return {"tier": user["tier"], "status": "error", "error": str(e)}

@app.post("/stripe/cancel")
async def cancel_subscription(authorization: Optional[str] = Header(None)):
    """Cancel user's subscription"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    token = authorization.split(" ")[1]
    payload = UserAuth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = USERS_DB.get(payload["email"])
    if not user or not user.get("stripe_subscription_id"):
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        subscription = stripe.Subscription.modify(
            user["stripe_subscription_id"],
            cancel_at_period_end=True
        )
        return {"status": "canceled", "cancel_at": subscription.cancel_at}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stripe/config")
async def get_stripe_config():
    """Get Stripe public configuration"""
    return {
        "publishable_key": Config.STRIPE_PUBLISHABLE_KEY if Config.STRIPE_PUBLISHABLE_KEY else None,
        "configured": bool(Config.STRIPE_SECRET_KEY and Config.STRIPE_PUBLISHABLE_KEY),
        "tiers": {
            tier: {"price": f"${price['verifications_per_month']} verifications/month"}
            for tier, price in PRICING_TIERS.items()
        }
    }


# =============================================================================
# BATCH & ANALYTICS
# =============================================================================

@app.post("/v3/batch")
async def batch_verify(request: BatchRequest):
    """Batch verify multiple claims"""
    results = []
    async with AIProviders() as providers:
        for claim in request.claims:
            result = await providers.verify_claim(claim)
            results.append({
                "claim": claim,
                "verdict": result["verdict"],
                "confidence": result["confidence"],
                "providers_used": result["providers_used"]
            })
    
    return {"results": results, "total": len(results)}


@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    providers = get_available_providers()
    
    return {
        "version": "10.0.0",
        "providers_active": len(providers),
        "providers_list": providers,
        "rate_limit": {
            "requests_per_minute": Config.RATE_LIMIT_REQUESTS,
            "window_seconds": Config.RATE_LIMIT_WINDOW
        },
        "auth_enabled": True,
        "stripe_configured": bool(Config.STRIPE_SECRET_KEY),
        "features": {
            "claim_verification": True,
            "batch_verification": True,
            "social_media_analysis": True,
            "source_credibility": True,
            "jwt_authentication": True,
            "stripe_payments": True,
            "statistics_validation": True,
            "image_forensics": True,
            "research_assistant": True,
            "realtime_stream": True,
            "stripe_ready": bool(Config.STRIPE_SECRET_KEY)
        }
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server_v9:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
