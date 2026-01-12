"""
Verity API - Circuit Breaker Pattern
====================================
Implements resilient provider failover with circuit breakers
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Callable, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation, requests flow through
    OPEN = "open"          # Circuit tripped, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for individual AI providers.
    
    Prevents cascading failures by failing fast when a provider is down.
    """
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3
    
    # State
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: Optional[float] = field(default=None)
    half_open_calls: int = field(default=0)
    
    # Metrics
    total_calls: int = field(default=0)
    total_failures: int = field(default=0)
    total_successes: int = field(default=0)
    
    def can_execute(self) -> bool:
        """Check if request can proceed"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker {self.name}: OPEN -> HALF_OPEN")
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
            
        return True
    
    def record_success(self):
        """Record successful call"""
        self.total_calls += 1
        self.total_successes += 1
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                # All test calls succeeded, close circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name}: HALF_OPEN -> CLOSED")
        else:
            # Reset failure count on success in closed state
            if self.success_count >= self.failure_threshold:
                self.failure_count = 0
                self.success_count = 0
    
    def record_failure(self):
        """Record failed call"""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure during recovery, reopen circuit
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name}: HALF_OPEN -> OPEN (failure during recovery)")
        elif self.failure_count >= self.failure_threshold:
            # Threshold reached, trip circuit
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name}: CLOSED -> OPEN (threshold reached)")
    
    def get_stats(self) -> Dict:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "success_rate": round(self.total_successes / max(self.total_calls, 1) * 100, 2),
            "last_failure": self.last_failure_time
        }


class ProviderManager:
    """
    Manages multiple AI providers with circuit breakers and failover.
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.provider_priority: list = []
        self.request_dedup: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour cache
        
    def register_provider(self, name: str, priority: int = 50, 
                         failure_threshold: int = 5, recovery_timeout: int = 60):
        """Register a provider with circuit breaker"""
        self.circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        self.provider_priority.append((priority, name))
        self.provider_priority.sort(key=lambda x: x[0])
        logger.info(f"Registered provider: {name} (priority: {priority})")
        
    def get_available_providers(self) -> list:
        """Get list of available providers in priority order"""
        available = []
        for priority, name in self.provider_priority:
            cb = self.circuit_breakers.get(name)
            if cb and cb.can_execute():
                available.append(name)
        return available
    
    def get_healthy_providers(self) -> list:
        """Get providers with closed circuits only"""
        return [name for name, cb in self.circuit_breakers.items() 
                if cb.state == CircuitState.CLOSED]
    
    async def execute_with_failover(self, providers: dict, claim: str) -> Optional[Dict]:
        """
        Execute verification with automatic failover.
        
        Args:
            providers: Dict mapping provider name to async callable
            claim: The claim to verify
            
        Returns:
            Result from first successful provider, or None if all fail
        """
        # Check cache first
        cache_key = self._get_cache_key(claim)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for claim: {claim[:50]}...")
                return cached['result']
        
        # Check for in-flight duplicate request
        if cache_key in self.request_dedup:
            logger.info(f"Deduplicating request for claim: {claim[:50]}...")
            return await self.request_dedup[cache_key]
        
        # Create dedup future
        future = asyncio.Future()
        self.request_dedup[cache_key] = future
        
        try:
            result = await self._execute_with_failover_internal(providers, claim)
            
            # Cache result
            if result:
                self.cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
            
            future.set_result(result)
            return result
            
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            del self.request_dedup[cache_key]
    
    async def _execute_with_failover_internal(self, providers: dict, claim: str) -> Optional[Dict]:
        """Internal failover logic"""
        available = self.get_available_providers()
        
        if not available:
            logger.error("No providers available - all circuits open")
            raise Exception("All AI providers are currently unavailable. Please try again later.")
        
        errors = []
        
        for provider_name in available:
            if provider_name not in providers:
                continue
                
            cb = self.circuit_breakers[provider_name]
            
            if not cb.can_execute():
                continue
                
            try:
                logger.info(f"Trying provider: {provider_name}")
                result = await providers[provider_name](claim)
                cb.record_success()
                
                # Add provider info to result
                if isinstance(result, dict):
                    result['provider'] = provider_name
                
                return result
                
            except Exception as e:
                cb.record_failure()
                errors.append(f"{provider_name}: {str(e)}")
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        # All providers failed
        logger.error(f"All providers failed: {errors}")
        return None
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key for claim"""
        import hashlib
        normalized = claim.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def record_success(self, provider_name: str):
        """Record successful call for provider"""
        if provider_name in self.circuit_breakers:
            self.circuit_breakers[provider_name].record_success()
    
    def record_failure(self, provider_name: str):
        """Record failed call for provider"""
        if provider_name in self.circuit_breakers:
            self.circuit_breakers[provider_name].record_failure()
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all providers"""
        stats = {
            "providers": {},
            "summary": {
                "total": len(self.circuit_breakers),
                "healthy": 0,
                "degraded": 0,
                "unavailable": 0
            }
        }
        
        for name, cb in self.circuit_breakers.items():
            stats["providers"][name] = cb.get_stats()
            
            if cb.state == CircuitState.CLOSED:
                stats["summary"]["healthy"] += 1
            elif cb.state == CircuitState.HALF_OPEN:
                stats["summary"]["degraded"] += 1
            else:
                stats["summary"]["unavailable"] += 1
        
        return stats
    
    def reset_circuit(self, provider_name: str):
        """Manually reset a circuit breaker"""
        if provider_name in self.circuit_breakers:
            cb = self.circuit_breakers[provider_name]
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            cb.success_count = 0
            logger.info(f"Circuit breaker {provider_name} manually reset")
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logger.info("Response cache cleared")


# Global provider manager instance
provider_manager = ProviderManager()


# ============================================================================
# RATE LIMITER WITH SLIDING WINDOW
# ============================================================================

class RateLimiter:
    """
    Token bucket rate limiter with sliding window.
    """
    
    def __init__(self, rate: int = 100, window: int = 60):
        """
        Args:
            rate: Maximum requests allowed per window
            window: Time window in seconds
        """
        self.rate = rate
        self.window = window
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple:
        """
        Check if request is allowed.
        
        Returns:
            Tuple of (is_allowed, remaining, reset_time)
        """
        now = time.time()
        window_start = now - self.window
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        current_count = len(self.requests[key])
        remaining = max(0, self.rate - current_count)
        
        if current_count >= self.rate:
            # Calculate reset time
            reset_time = self.requests[key][0] + self.window - now
            return False, remaining, reset_time
        
        # Allow request
        self.requests[key].append(now)
        return True, remaining - 1, self.window
    
    def get_usage(self, key: str) -> Dict:
        """Get rate limit usage for a key"""
        now = time.time()
        window_start = now - self.window
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        return {
            "used": len(self.requests[key]),
            "limit": self.rate,
            "remaining": max(0, self.rate - len(self.requests[key])),
            "window": self.window,
            "resets_at": now + self.window
        }


# ============================================================================
# HEALTH CHECK SYSTEM
# ============================================================================

class HealthChecker:
    """
    Performs health checks on providers.
    """
    
    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self.last_check: Dict[str, Dict] = {}
        self.check_interval = 60  # seconds
    
    async def check_provider(self, name: str, test_func: Callable) -> Dict:
        """
        Check health of a single provider.
        
        Args:
            name: Provider name
            test_func: Async function to test provider
            
        Returns:
            Health status dict
        """
        start_time = time.time()
        
        try:
            await test_func()
            latency = time.time() - start_time
            
            status = {
                "name": name,
                "status": "healthy",
                "latency_ms": round(latency * 1000, 2),
                "timestamp": time.time(),
                "message": "OK"
            }
            
            self.provider_manager.record_success(name)
            
        except Exception as e:
            status = {
                "name": name,
                "status": "unhealthy",
                "latency_ms": None,
                "timestamp": time.time(),
                "message": str(e)
            }
            
            self.provider_manager.record_failure(name)
        
        self.last_check[name] = status
        return status
    
    async def check_all(self, test_funcs: Dict[str, Callable]) -> Dict:
        """
        Check health of all providers.
        
        Args:
            test_funcs: Dict mapping provider name to test function
            
        Returns:
            Overall health status
        """
        results = await asyncio.gather(*[
            self.check_provider(name, func)
            for name, func in test_funcs.items()
        ], return_exceptions=True)
        
        healthy = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "healthy")
        total = len(results)
        
        return {
            "status": "healthy" if healthy == total else "degraded" if healthy > 0 else "unhealthy",
            "healthy_count": healthy,
            "total_count": total,
            "providers": [r for r in results if isinstance(r, dict)],
            "timestamp": time.time()
        }
    
    def get_overall_status(self) -> str:
        """Get overall system health status"""
        stats = self.provider_manager.get_all_stats()
        
        if stats["summary"]["healthy"] == stats["summary"]["total"]:
            return "healthy"
        elif stats["summary"]["healthy"] > 0:
            return "degraded"
        else:
            return "unhealthy"


# Export classes
__all__ = [
    'CircuitBreaker',
    'CircuitState', 
    'ProviderManager',
    'provider_manager',
    'RateLimiter',
    'HealthChecker'
]
