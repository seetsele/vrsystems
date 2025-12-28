"""
Verity Systems - Caching Layer
Multi-level caching with Redis, in-memory, and request coalescing.

Features:
- Redis distributed cache (with fallback to in-memory)
- LRU in-memory cache with TTL
- Request coalescing (deduplication)
- Cache warming and invalidation
- Prometheus metrics

Author: Verity Systems
License: MIT
"""

import os
import asyncio
import logging
import json
import hashlib
import time
import functools
from typing import Optional, Dict, Any, List, Callable, Awaitable, TypeVar, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
from contextlib import asynccontextmanager
import pickle

logger = logging.getLogger('VerityCache')

T = TypeVar('T')


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class CacheConfig:
    """Cache configuration"""
    
    # Redis settings
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379'))
    redis_db: int = 0
    redis_prefix: str = "verity:"
    
    # In-memory cache
    memory_max_size: int = 10000
    
    # TTL defaults (in seconds)
    default_ttl: int = 3600  # 1 hour
    verification_ttl: int = 86400  # 24 hours for verifications
    provider_result_ttl: int = 1800  # 30 min for provider results
    health_check_ttl: int = 60  # 1 min for health checks
    
    # Request coalescing
    coalesce_window_ms: int = 100  # Window for coalescing identical requests
    
    # Metrics
    enable_metrics: bool = True


DEFAULT_CACHE_CONFIG = CacheConfig()


# ============================================================
# CACHE KEY GENERATION
# ============================================================

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a deterministic cache key"""
    # Create a string representation of args and kwargs
    key_data = json.dumps({
        "args": args,
        "kwargs": kwargs
    }, sort_keys=True, default=str)
    
    # Hash it for consistent length
    key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    return f"{prefix}:{key_hash}"


def normalize_claim(claim: str) -> str:
    """Normalize a claim for consistent caching"""
    # Lowercase
    normalized = claim.lower()
    
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    
    # Remove punctuation at the end
    normalized = normalized.rstrip(".,!?;:")
    
    return normalized


def claim_cache_key(claim: str) -> str:
    """Generate cache key for a claim"""
    normalized = normalize_claim(claim)
    claim_hash = hashlib.sha256(normalized.encode()).hexdigest()[:16]
    return f"claim:{claim_hash}"


# ============================================================
# IN-MEMORY LRU CACHE WITH TTL
# ============================================================

@dataclass
class CacheEntry:
    """Entry in the cache with metadata"""
    value: Any
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    hits: int = 0


class MemoryCache:
    """
    Thread-safe in-memory LRU cache with TTL support.
    """
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        
        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if datetime.utcnow() > entry.expires_at:
                del self._cache[key]
                self.misses += 1
                return None
            
            # Update access order (LRU)
            self._cache.move_to_end(key)
            entry.hits += 1
            self.hits += 1
            
            return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        """Set value in cache with TTL"""
        async with self._lock:
            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self.evictions += 1
            
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=datetime.utcnow() + timedelta(seconds=ttl)
            )
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries"""
        now = datetime.utcnow()
        removed = 0
        
        async with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if now > entry.expires_at
            ]
            for key in keys_to_remove:
                del self._cache[key]
                removed += 1
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / max(1, total_requests)
        
        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4),
            "evictions": self.evictions
        }


# ============================================================
# REDIS CACHE
# ============================================================

class RedisCache:
    """
    Redis-backed distributed cache.
    Falls back to None (not memory) if Redis is unavailable.
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or DEFAULT_CACHE_CONFIG
        self._client = None
        self._available = None
        
        # Metrics
        self.hits = 0
        self.misses = 0
        self.errors = 0
    
    async def _get_client(self):
        """Get or create Redis client"""
        if self._client is not None:
            return self._client
        
        try:
            import redis.asyncio as redis
            self._client = redis.from_url(
                self.config.redis_url,
                db=self.config.redis_db,
                decode_responses=False  # We'll handle encoding
            )
            # Test connection
            await self._client.ping()
            self._available = True
            logger.info("Redis connection established")
            return self._client
        except ImportError:
            logger.warning("redis package not installed. Run: pip install redis")
            self._available = False
            return None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self._available = False
            return None
    
    @property
    async def is_available(self) -> bool:
        """Check if Redis is available"""
        if self._available is None:
            await self._get_client()
        return self._available or False
    
    def _make_key(self, key: str) -> str:
        """Create full Redis key with prefix"""
        return f"{self.config.redis_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        client = await self._get_client()
        if not client:
            return None
        
        try:
            full_key = self._make_key(key)
            data = await client.get(full_key)
            
            if data is None:
                self.misses += 1
                return None
            
            self.hits += 1
            return pickle.loads(data)
            
        except Exception as e:
            self.errors += 1
            logger.warning(f"Redis get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """Set value in Redis with TTL"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            full_key = self._make_key(key)
            data = pickle.dumps(value)
            await client.setex(full_key, ttl, data)
            return True
            
        except Exception as e:
            self.errors += 1
            logger.warning(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            full_key = self._make_key(key)
            result = await client.delete(full_key)
            return result > 0
            
        except Exception as e:
            self.errors += 1
            logger.warning(f"Redis delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        client = await self._get_client()
        if not client:
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in client.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                return await client.delete(*keys)
            return 0
            
        except Exception as e:
            self.errors += 1
            logger.warning(f"Redis delete_pattern error: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / max(1, total_requests)
        
        return {
            "type": "redis",
            "available": self._available,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4),
            "errors": self.errors
        }


# ============================================================
# MULTI-LEVEL CACHE
# ============================================================

class MultiLevelCache:
    """
    Multi-level cache with L1 (memory) and L2 (Redis).
    
    Read: Check L1 -> Check L2 -> Miss
    Write: Write to L1 and L2
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or DEFAULT_CACHE_CONFIG
        self.l1 = MemoryCache(max_size=self.config.memory_max_size)
        self.l2 = RedisCache(config)
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache, checking L1 then L2"""
        # Check L1 first
        value = await self.l1.get(key)
        if value is not None:
            return value
        
        # Check L2
        if await self.l2.is_available:
            value = await self.l2.get(key)
            if value is not None:
                # Populate L1 for faster subsequent access
                await self.l1.set(key, value, ttl=self.config.default_ttl)
                return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ):
        """Set in both cache levels"""
        ttl = ttl or self.config.default_ttl
        
        # Write to L1
        await self.l1.set(key, value, ttl)
        
        # Write to L2 if available
        if await self.l2.is_available:
            await self.l2.set(key, value, ttl)
    
    async def delete(self, key: str):
        """Delete from both cache levels"""
        await self.l1.delete(key)
        if await self.l2.is_available:
            await self.l2.delete(key)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        count = 0
        
        # L2 pattern delete (Redis)
        if await self.l2.is_available:
            count = await self.l2.delete_pattern(pattern)
        
        # L1 doesn't support pattern delete, clear all
        # In production, you might want a more sophisticated approach
        if pattern == "*":
            await self.l1.clear()
        
        return count
    
    async def start_cleanup(self, interval: int = 300):
        """Start background cleanup task"""
        if self._cleanup_task is not None:
            return
        
        async def _cleanup_loop():
            while True:
                try:
                    removed = await self.l1.cleanup_expired()
                    if removed > 0:
                        logger.debug(f"Cleaned up {removed} expired cache entries")
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(interval)
        
        self._cleanup_task = asyncio.create_task(_cleanup_loop())
    
    async def stop_cleanup(self):
        """Stop background cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def close(self):
        """Close all cache connections"""
        await self.stop_cleanup()
        await self.l2.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache levels"""
        return {
            "l1": self.l1.get_stats(),
            "l2": self.l2.get_stats()
        }


# ============================================================
# REQUEST COALESCING
# ============================================================

class RequestCoalescer:
    """
    Coalesce identical concurrent requests.
    
    If multiple identical requests come in within a short window,
    only one actual request is made and the result is shared.
    """
    
    def __init__(self, window_ms: int = 100):
        self.window_ms = window_ms
        self._pending: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
        
        # Metrics
        self.coalesced_count = 0
        self.total_requests = 0
    
    async def execute(
        self,
        key: str,
        func: Callable[[], Awaitable[T]]
    ) -> T:
        """
        Execute function with request coalescing.
        
        If an identical request is already in flight, wait for it.
        Otherwise, execute the function and cache the result briefly.
        """
        self.total_requests += 1
        
        async with self._lock:
            if key in self._pending:
                # Request already in flight, wait for it
                self.coalesced_count += 1
                logger.debug(f"Coalescing request: {key}")
        
        if key in self._pending:
            return await self._pending[key]
        
        # Create a future for this request
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        
        async with self._lock:
            self._pending[key] = future
        
        try:
            result = await func()
            future.set_result(result)
            return result
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Remove from pending after a short delay
            async def _cleanup():
                await asyncio.sleep(self.window_ms / 1000)
                async with self._lock:
                    if key in self._pending and self._pending[key] is future:
                        del self._pending[key]
            
            asyncio.create_task(_cleanup())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coalescing statistics"""
        return {
            "total_requests": self.total_requests,
            "coalesced_count": self.coalesced_count,
            "coalesce_rate": self.coalesced_count / max(1, self.total_requests),
            "pending_count": len(self._pending)
        }


# ============================================================
# CACHED DECORATOR
# ============================================================

def cached(
    key_prefix: str,
    ttl: int = None,
    cache: MultiLevelCache = None,
    key_builder: Callable[..., str] = None
):
    """
    Decorator for caching async function results.
    
    Args:
        key_prefix: Prefix for cache keys
        ttl: Time-to-live in seconds
        cache: Cache instance to use
        key_builder: Custom function to build cache key from args
    
    Usage:
        @cached("my_func", ttl=300)
        async def my_func(arg1, arg2):
            return expensive_computation()
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        # Use a global cache if none provided
        _cache = cache
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            nonlocal _cache
            if _cache is None:
                _cache = _global_cache
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = generate_cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await _cache.set(cache_key, result, ttl or DEFAULT_CACHE_CONFIG.default_ttl)
            
            return result
        
        return wrapper
    return decorator


# ============================================================
# VERIFICATION CACHE MANAGER
# ============================================================

class VerificationCache:
    """
    Specialized cache for claim verification results.
    
    Features:
    - Claim normalization for better hit rates
    - Provider-level caching
    - Partial result caching
    - Cache warming for common claims
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or DEFAULT_CACHE_CONFIG
        self.cache = MultiLevelCache(config)
        self.coalescer = RequestCoalescer()
    
    async def get_verification(self, claim: str) -> Optional[Dict[str, Any]]:
        """Get cached verification result for a claim"""
        key = claim_cache_key(claim)
        return await self.cache.get(key)
    
    async def set_verification(
        self,
        claim: str,
        result: Dict[str, Any],
        ttl: int = None
    ):
        """Cache a verification result"""
        key = claim_cache_key(claim)
        ttl = ttl or self.config.verification_ttl
        await self.cache.set(key, result, ttl)
    
    async def get_provider_result(
        self,
        provider: str,
        claim: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached result from a specific provider"""
        claim_key = claim_cache_key(claim)
        key = f"provider:{provider}:{claim_key}"
        return await self.cache.get(key)
    
    async def set_provider_result(
        self,
        provider: str,
        claim: str,
        result: Dict[str, Any],
        ttl: int = None
    ):
        """Cache result from a specific provider"""
        claim_key = claim_cache_key(claim)
        key = f"provider:{provider}:{claim_key}"
        ttl = ttl or self.config.provider_result_ttl
        await self.cache.set(key, result, ttl)
    
    async def execute_with_coalescing(
        self,
        claim: str,
        func: Callable[[], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Execute verification with request coalescing"""
        key = claim_cache_key(claim)
        
        # Check cache first
        cached = await self.cache.get(key)
        if cached is not None:
            return cached
        
        # Execute with coalescing
        result = await self.coalescer.execute(key, func)
        
        # Cache the result
        await self.set_verification(claim, result)
        
        return result
    
    async def invalidate_claim(self, claim: str):
        """Invalidate all cached data for a claim"""
        claim_key = claim_cache_key(claim)
        await self.cache.delete(claim_key)
        # Also invalidate provider-specific caches
        await self.cache.invalidate_pattern(f"provider:*:{claim_key}")
    
    async def warm_cache(self, common_claims: List[str], verify_func):
        """Pre-populate cache with common claims"""
        logger.info(f"Warming cache with {len(common_claims)} claims")
        
        for claim in common_claims:
            try:
                # Check if already cached
                if await self.get_verification(claim) is None:
                    result = await verify_func(claim)
                    await self.set_verification(claim, result)
                    logger.debug(f"Warmed cache for: {claim[:50]}...")
            except Exception as e:
                logger.warning(f"Failed to warm cache for claim: {e}")
    
    async def close(self):
        """Close cache connections"""
        await self.cache.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache": self.cache.get_stats(),
            "coalescer": self.coalescer.get_stats()
        }


# ============================================================
# GLOBAL CACHE INSTANCE
# ============================================================

_global_cache: Optional[MultiLevelCache] = None
_verification_cache: Optional[VerificationCache] = None


async def init_cache(config: CacheConfig = None) -> MultiLevelCache:
    """Initialize global cache"""
    global _global_cache, _verification_cache
    
    config = config or DEFAULT_CACHE_CONFIG
    _global_cache = MultiLevelCache(config)
    _verification_cache = VerificationCache(config)
    
    # Start background cleanup
    await _global_cache.start_cleanup()
    
    logger.info("Cache system initialized")
    return _global_cache


async def get_cache() -> MultiLevelCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        await init_cache()
    return _global_cache


async def get_verification_cache() -> VerificationCache:
    """Get verification-specific cache"""
    global _verification_cache
    if _verification_cache is None:
        await init_cache()
    return _verification_cache


async def close_cache():
    """Close global cache"""
    global _global_cache, _verification_cache
    
    if _global_cache:
        await _global_cache.close()
        _global_cache = None
    
    if _verification_cache:
        await _verification_cache.close()
        _verification_cache = None


# ============================================================
# MAIN / TESTING
# ============================================================

async def main():
    """Test caching functionality"""
    
    print("=== Testing Memory Cache ===")
    memory_cache = MemoryCache(max_size=100)
    
    await memory_cache.set("key1", "value1", ttl=60)
    value = await memory_cache.get("key1")
    print(f"Get key1: {value}")
    
    # Test miss
    value = await memory_cache.get("nonexistent")
    print(f"Get nonexistent: {value}")
    
    print(f"Memory cache stats: {memory_cache.get_stats()}")
    
    print("\n=== Testing Multi-Level Cache ===")
    cache = MultiLevelCache()
    
    await cache.set("test_key", {"data": "test_value"}, ttl=300)
    result = await cache.get("test_key")
    print(f"Multi-level get: {result}")
    print(f"Cache stats: {cache.get_stats()}")
    
    print("\n=== Testing Request Coalescer ===")
    coalescer = RequestCoalescer()
    
    call_count = 0
    
    async def expensive_operation():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return f"result_{call_count}"
    
    # Simulate concurrent identical requests
    results = await asyncio.gather(
        coalescer.execute("same_key", expensive_operation),
        coalescer.execute("same_key", expensive_operation),
        coalescer.execute("same_key", expensive_operation)
    )
    
    print(f"Coalesced results: {results}")
    print(f"Actual calls made: {call_count}")
    print(f"Coalescer stats: {coalescer.get_stats()}")
    
    print("\n=== Testing Verification Cache ===")
    ver_cache = VerificationCache()
    
    test_claim = "The Earth is round."
    test_result = {"verdict": "TRUE", "confidence": 0.99}
    
    await ver_cache.set_verification(test_claim, test_result)
    cached = await ver_cache.get_verification(test_claim)
    print(f"Verification cache result: {cached}")
    
    # Test normalization
    similar_claim = "  The Earth is round  "
    cached_similar = await ver_cache.get_verification(similar_claim)
    print(f"Normalized claim cache hit: {cached_similar}")
    
    print(f"\nVerification cache stats: {ver_cache.get_stats()}")
    
    # Cleanup
    await cache.close()
    await ver_cache.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
