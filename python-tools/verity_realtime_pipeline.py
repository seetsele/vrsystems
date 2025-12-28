"""
Verity Real-Time Pipeline
=========================
High-performance async pipeline for real-time fact-checking.

Features:
- Streaming results as they arrive
- Priority queue for providers
- Circuit breaker for failing providers
- Rate limiting per provider
- Connection pooling
- Request deduplication
- Response caching with TTL
"""

import asyncio
import aiohttp
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, AsyncGenerator, Any
from collections import defaultdict
from enum import Enum
import json


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    RATE_LIMITED = "rate_limited"


@dataclass
class ProviderHealth:
    """Track health status of a provider"""
    name: str
    status: ProviderStatus = ProviderStatus.HEALTHY
    consecutive_failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    avg_response_time_ms: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    rate_limit_reset: Optional[datetime] = None


@dataclass
class CachedResult:
    """Cached verification result"""
    claim_hash: str
    result: Dict
    timestamp: datetime
    ttl_seconds: int = 3600  # 1 hour default
    
    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)


@dataclass
class PipelineConfig:
    """Configuration for the pipeline"""
    max_concurrent_requests: int = 20
    request_timeout_seconds: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_seconds: int = 60
    rate_limit_per_second: float = 10.0
    cache_ttl_seconds: int = 3600
    enable_streaming: bool = True
    retry_count: int = 2


class CircuitBreaker:
    """
    Circuit breaker pattern for provider fault tolerance.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Provider failing, requests blocked
    - HALF_OPEN: Testing if provider recovered
    """
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures: Dict[str, int] = defaultdict(int)
        self.last_failure_time: Dict[str, datetime] = {}
        self.state: Dict[str, str] = defaultdict(lambda: "CLOSED")
    
    def record_success(self, provider: str):
        """Record successful call"""
        self.failures[provider] = 0
        self.state[provider] = "CLOSED"
    
    def record_failure(self, provider: str):
        """Record failed call"""
        self.failures[provider] += 1
        self.last_failure_time[provider] = datetime.now()
        
        if self.failures[provider] >= self.failure_threshold:
            self.state[provider] = "OPEN"
    
    def can_execute(self, provider: str) -> bool:
        """Check if we can make a call to this provider"""
        state = self.state[provider]
        
        if state == "CLOSED":
            return True
        
        if state == "OPEN":
            # Check if reset timeout has passed
            last_failure = self.last_failure_time.get(provider)
            if last_failure:
                elapsed = (datetime.now() - last_failure).total_seconds()
                if elapsed >= self.reset_timeout:
                    self.state[provider] = "HALF_OPEN"
                    return True
            return False
        
        if state == "HALF_OPEN":
            return True
        
        return False


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    """
    
    def __init__(self, rate: float = 10.0, burst: int = 20):
        self.rate = rate  # Tokens per second
        self.burst = burst  # Max tokens
        self.tokens: Dict[str, float] = defaultdict(lambda: float(burst))
        self.last_update: Dict[str, float] = defaultdict(time.time)
    
    async def acquire(self, provider: str):
        """Wait for rate limit token"""
        while True:
            now = time.time()
            elapsed = now - self.last_update[provider]
            self.tokens[provider] = min(
                self.burst,
                self.tokens[provider] + elapsed * self.rate
            )
            self.last_update[provider] = now
            
            if self.tokens[provider] >= 1:
                self.tokens[provider] -= 1
                return
            
            # Wait for token
            wait_time = (1 - self.tokens[provider]) / self.rate
            await asyncio.sleep(wait_time)


class ResultCache:
    """
    LRU cache for verification results.
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CachedResult] = {}
        self.access_order: List[str] = []
    
    def _hash_claim(self, claim: str) -> str:
        """Generate hash for claim"""
        normalized = claim.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def get(self, claim: str) -> Optional[Dict]:
        """Get cached result if exists and not expired"""
        claim_hash = self._hash_claim(claim)
        
        if claim_hash in self.cache:
            cached = self.cache[claim_hash]
            if not cached.is_expired():
                # Move to end (most recently used)
                if claim_hash in self.access_order:
                    self.access_order.remove(claim_hash)
                self.access_order.append(claim_hash)
                return cached.result
            else:
                # Expired, remove
                del self.cache[claim_hash]
                if claim_hash in self.access_order:
                    self.access_order.remove(claim_hash)
        
        return None
    
    def set(self, claim: str, result: Dict, ttl: int = None):
        """Cache a result"""
        claim_hash = self._hash_claim(claim)
        
        # Evict oldest if at capacity
        while len(self.cache) >= self.max_size and self.access_order:
            oldest = self.access_order.pop(0)
            if oldest in self.cache:
                del self.cache[oldest]
        
        self.cache[claim_hash] = CachedResult(
            claim_hash=claim_hash,
            result=result,
            timestamp=datetime.now(),
            ttl_seconds=ttl or self.default_ttl
        )
        self.access_order.append(claim_hash)
    
    def clear(self):
        """Clear all cached results"""
        self.cache.clear()
        self.access_order.clear()


class RealTimePipeline:
    """
    High-performance async pipeline for fact-checking.
    
    Features:
    - Parallel execution with semaphore control
    - Circuit breaker for fault tolerance
    - Rate limiting per provider
    - Result caching
    - Streaming results
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_breaker_threshold,
            reset_timeout=self.config.circuit_breaker_reset_seconds
        )
        self.rate_limiter = RateLimiter(rate=self.config.rate_limit_per_second)
        self.cache = ResultCache(default_ttl=self.config.cache_ttl_seconds)
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
    
    def _get_provider_health(self, provider: str) -> ProviderHealth:
        """Get or create health tracker for provider"""
        if provider not in self.provider_health:
            self.provider_health[provider] = ProviderHealth(name=provider)
        return self.provider_health[provider]
    
    async def execute_with_retry(
        self,
        provider: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Optional[Dict]:
        """Execute a provider call with retry logic"""
        health = self._get_provider_health(provider)
        
        for attempt in range(self.config.retry_count + 1):
            # Check circuit breaker
            if not self.circuit_breaker.can_execute(provider):
                health.status = ProviderStatus.CIRCUIT_OPEN
                return None
            
            # Rate limiting
            await self.rate_limiter.acquire(provider)
            
            try:
                async with self.semaphore:
                    start_time = time.time()
                    
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=self.config.request_timeout_seconds
                    )
                    
                    # Record success
                    elapsed_ms = (time.time() - start_time) * 1000
                    self._record_success(provider, elapsed_ms)
                    
                    return result
                    
            except asyncio.TimeoutError:
                self._record_failure(provider, "timeout")
            except Exception as e:
                self._record_failure(provider, str(e))
            
            # Exponential backoff for retry
            if attempt < self.config.retry_count:
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def _record_success(self, provider: str, response_time_ms: float):
        """Record successful provider call"""
        health = self._get_provider_health(provider)
        health.total_requests += 1
        health.successful_requests += 1
        health.last_success = datetime.now()
        health.consecutive_failures = 0
        health.status = ProviderStatus.HEALTHY
        
        # Update average response time (exponential moving average)
        if health.avg_response_time_ms == 0:
            health.avg_response_time_ms = response_time_ms
        else:
            health.avg_response_time_ms = (
                health.avg_response_time_ms * 0.9 + response_time_ms * 0.1
            )
        
        self.circuit_breaker.record_success(provider)
    
    def _record_failure(self, provider: str, reason: str):
        """Record failed provider call"""
        health = self._get_provider_health(provider)
        health.total_requests += 1
        health.last_failure = datetime.now()
        health.consecutive_failures += 1
        
        if health.consecutive_failures >= 3:
            health.status = ProviderStatus.DEGRADED
        
        self.circuit_breaker.record_failure(provider)
    
    async def stream_verify(
        self,
        claim: str,
        providers: List[Dict],
        session: aiohttp.ClientSession
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream verification results as they arrive.
        
        Yields results from each provider as they complete.
        """
        # Check cache first
        cached = self.cache.get(claim)
        if cached:
            yield {
                "type": "cached",
                "provider": "cache",
                "result": cached,
                "timestamp": datetime.now().isoformat()
            }
            return
        
        # Create tasks for all providers
        tasks = []
        for provider_config in providers:
            provider_name = provider_config.get("name")
            provider_func = provider_config.get("func")
            
            if provider_name and provider_func:
                task = asyncio.create_task(
                    self._execute_provider(provider_name, provider_func, claim, session)
                )
                tasks.append((provider_name, task))
        
        # Yield results as they complete
        pending = {task for _, task in tasks}
        task_names = {task: name for name, task in tasks}
        
        while pending:
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in done:
                provider_name = task_names.get(task, "unknown")
                try:
                    result = task.result()
                    if result:
                        yield {
                            "type": "result",
                            "provider": provider_name,
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                except Exception as e:
                    yield {
                        "type": "error",
                        "provider": provider_name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
        
        # Signal completion
        yield {
            "type": "complete",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_provider(
        self,
        provider_name: str,
        provider_func: Callable,
        claim: str,
        session: aiohttp.ClientSession
    ) -> Optional[Dict]:
        """Execute a single provider - only pass claim, not session (most providers don't need it)"""
        return await self.execute_with_retry(
            provider_name,
            provider_func,
            claim  # Only pass claim, not session
        )
    
    async def batch_verify(
        self,
        claims: List[str],
        providers: List[Dict],
        session: aiohttp.ClientSession,
        max_concurrent_claims: int = 5
    ) -> List[Dict]:
        """
        Verify multiple claims in parallel.
        """
        semaphore = asyncio.Semaphore(max_concurrent_claims)
        
        async def verify_single(claim: str) -> Dict:
            async with semaphore:
                results = []
                async for result in self.stream_verify(claim, providers, session):
                    if result["type"] == "result":
                        results.append(result)
                
                return {
                    "claim": claim,
                    "results": results,
                    "provider_count": len(results)
                }
        
        tasks = [verify_single(claim) for claim in claims]
        return await asyncio.gather(*tasks)
    
    def get_provider_stats(self) -> Dict:
        """Get statistics for all providers"""
        stats = {}
        
        for name, health in self.provider_health.items():
            success_rate = (
                health.successful_requests / health.total_requests
                if health.total_requests > 0 else 0
            )
            
            stats[name] = {
                "status": health.status.value,
                "total_requests": health.total_requests,
                "successful_requests": health.successful_requests,
                "success_rate": success_rate,
                "avg_response_time_ms": health.avg_response_time_ms,
                "consecutive_failures": health.consecutive_failures,
                "last_success": health.last_success.isoformat() if health.last_success else None,
                "last_failure": health.last_failure.isoformat() if health.last_failure else None,
                "circuit_state": self.circuit_breaker.state.get(name, "CLOSED")
            }
        
        return stats
    
    def reset_provider(self, provider: str):
        """Reset a provider's health status"""
        if provider in self.provider_health:
            self.provider_health[provider] = ProviderHealth(name=provider)
        self.circuit_breaker.state[provider] = "CLOSED"
        self.circuit_breaker.failures[provider] = 0


class StreamingResponseBuilder:
    """
    Builds streaming responses for real-time fact-checking.
    
    Useful for:
    - SSE (Server-Sent Events)
    - WebSocket streaming
    - Progressive UI updates
    """
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing"""
        self.start_time = datetime.now()
        self.results = []
        self.errors = []
    
    def add_result(self, provider: str, result: Dict):
        """Add a provider result"""
        self.results.append({
            "provider": provider,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, provider: str, error: str):
        """Add an error"""
        self.errors.append({
            "provider": provider,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def complete(self) -> Dict:
        """Build final response"""
        self.end_time = datetime.now()
        
        duration_ms = (
            (self.end_time - self.start_time).total_seconds() * 1000
            if self.start_time else 0
        )
        
        return {
            "results": self.results,
            "errors": self.errors,
            "summary": {
                "total_providers": len(self.results) + len(self.errors),
                "successful": len(self.results),
                "failed": len(self.errors),
                "duration_ms": duration_ms
            },
            "completed_at": self.end_time.isoformat() if self.end_time else None
        }
    
    def to_sse_events(self) -> List[str]:
        """Convert to Server-Sent Events format"""
        events = []
        
        for result in self.results:
            events.append(f"event: result\ndata: {json.dumps(result)}\n\n")
        
        for error in self.errors:
            events.append(f"event: error\ndata: {json.dumps(error)}\n\n")
        
        events.append(f"event: complete\ndata: {json.dumps(self.complete())}\n\n")
        
        return events


__all__ = [
    'RealTimePipeline', 'PipelineConfig', 'CircuitBreaker',
    'RateLimiter', 'ResultCache', 'ProviderHealth', 'ProviderStatus',
    'StreamingResponseBuilder'
]
