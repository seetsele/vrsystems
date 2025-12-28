"""
Verity Systems - Resilience & Monitoring Layer
Comprehensive error handling, health checks, and observability.

Features:
- Circuit breaker pattern with adaptive thresholds
- Retry with exponential backoff + jitter
- Health check endpoints for all providers
- Prometheus metrics export
- Structured logging with correlation IDs
- Dead letter queue for failed requests
- Graceful degradation

Author: Verity Systems
License: MIT
"""

import os
import asyncio
import aiohttp
import logging
import json
import time
import uuid
import traceback
import functools
from typing import Optional, Dict, Any, List, Callable, Awaitable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
from contextlib import asynccontextmanager
import hashlib

logger = logging.getLogger('VerityResilience')

T = TypeVar('T')


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class ResilienceConfig:
    """Configuration for resilience features"""
    
    # Circuit Breaker
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout: int = 60  # seconds
    circuit_half_open_max_calls: int = 3
    
    # Retry
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    retry_jitter: float = 0.1
    
    # Timeouts
    default_timeout: float = 30.0
    connect_timeout: float = 10.0
    
    # Health Checks
    health_check_interval: int = 60  # seconds
    health_check_timeout: float = 5.0
    
    # Dead Letter Queue
    dlq_max_size: int = 1000
    dlq_retention_hours: int = 24


DEFAULT_CONFIG = ResilienceConfig()


# ============================================================
# CORRELATION ID & STRUCTURED LOGGING
# ============================================================

class CorrelationContext:
    """Thread-local correlation ID context"""
    _current_id: Optional[str] = None
    
    @classmethod
    def get_id(cls) -> str:
        if cls._current_id is None:
            cls._current_id = str(uuid.uuid4())[:8]
        return cls._current_id
    
    @classmethod
    def set_id(cls, correlation_id: str):
        cls._current_id = correlation_id
    
    @classmethod
    def new_id(cls) -> str:
        cls._current_id = str(uuid.uuid4())[:8]
        return cls._current_id
    
    @classmethod
    def clear(cls):
        cls._current_id = None


class StructuredLogger:
    """Structured logging with correlation IDs and metrics"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.metrics: Dict[str, int] = {}
        
        # Configure UTF-8 encoding for Windows console compatibility
        import sys
        if sys.platform == 'win32' and not getattr(self, '_encoding_fixed', False):
            try:
                # Set stdout/stderr to use UTF-8 with error replacement
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                if hasattr(sys.stderr, 'reconfigure'):
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                StructuredLogger._encoding_fixed = True
            except Exception:
                pass
    
    def _sanitize_for_logging(self, text: str) -> str:
        """Remove problematic Unicode characters for Windows console"""
        # Replace common Unicode symbols with ASCII alternatives
        replacements = {
            '\u2717': '[x]',  # ✗
            '\u2713': '[v]',  # ✓
            '\u2192': '->',   # →
            '\u2190': '<-',   # ←
            '\u2022': '*',    # •
            '\u25B6': '>',    # ▶
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text
    
    def _format_message(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "correlation_id": CorrelationContext.get_id(),
            "message": self._sanitize_for_logging(message),
            **kwargs
        }
    
    def info(self, message: str, **kwargs):
        log_data = self._format_message("INFO", message, **kwargs)
        try:
            self.logger.info(json.dumps(log_data))
        except UnicodeEncodeError:
            self.logger.info(json.dumps(log_data, ensure_ascii=True))
        
    def warning(self, message: str, **kwargs):
        log_data = self._format_message("WARNING", message, **kwargs)
        try:
            self.logger.warning(json.dumps(log_data))
        except UnicodeEncodeError:
            self.logger.warning(json.dumps(log_data, ensure_ascii=True))
        
    def error(self, message: str, exception: Exception = None, **kwargs):
        if exception:
            kwargs["exception_type"] = type(exception).__name__
            kwargs["exception_message"] = str(exception)
            kwargs["traceback"] = traceback.format_exc()
        log_data = self._format_message("ERROR", message, **kwargs)
        try:
            self.logger.error(json.dumps(log_data))
        except UnicodeEncodeError:
            self.logger.error(json.dumps(log_data, ensure_ascii=True))
        self._increment_metric("errors")
        
    def _increment_metric(self, name: str):
        self.metrics[name] = self.metrics.get(name, 0) + 1


structured_logger = StructuredLogger('VerityResilience')


# ============================================================
# CIRCUIT BREAKER
# ============================================================

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreaker:
    """
    Circuit breaker implementation with adaptive thresholds.
    
    States:
    - CLOSED: Normal operation, tracking failures
    - OPEN: Too many failures, reject all calls immediately
    - HALF_OPEN: Testing recovery, allow limited calls
    """
    
    name: str
    config: ResilienceConfig = field(default_factory=lambda: DEFAULT_CONFIG)
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    half_open_calls: int = 0
    
    # Metrics
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0
    
    def can_execute(self) -> bool:
        """Check if a call can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.config.circuit_recovery_timeout:
                    self._transition_to_half_open()
                    return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.circuit_half_open_max_calls
            
        return False
    
    def record_success(self):
        """Record a successful call"""
        self.total_calls += 1
        self.total_successes += 1
        self.success_count += 1
        self.last_success_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.circuit_half_open_max_calls:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self, exception: Exception = None):
        """Record a failed call"""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            # Immediately open on failure during half-open
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.circuit_failure_threshold:
                self._transition_to_open()
    
    def _transition_to_open(self):
        structured_logger.warning(
            f"Circuit breaker {self.name} OPENED",
            circuit=self.name,
            failure_count=self.failure_count
        )
        self.state = CircuitState.OPEN
        self.half_open_calls = 0
        
    def _transition_to_half_open(self):
        structured_logger.info(
            f"Circuit breaker {self.name} testing recovery (HALF_OPEN)",
            circuit=self.name
        )
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        
    def _transition_to_closed(self):
        structured_logger.info(
            f"Circuit breaker {self.name} recovered (CLOSED)",
            circuit=self.name
        )
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "failure_rate": self.total_failures / max(1, self.total_calls),
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class CircuitBreakerRegistry:
    """Registry for all circuit breakers"""
    
    _breakers: Dict[str, CircuitBreaker] = {}
    
    @classmethod
    def get(cls, name: str, config: ResilienceConfig = None) -> CircuitBreaker:
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(
                name=name,
                config=config or DEFAULT_CONFIG
            )
        return cls._breakers[name]
    
    @classmethod
    def get_all_stats(cls) -> List[Dict[str, Any]]:
        return [breaker.get_stats() for breaker in cls._breakers.values()]


# ============================================================
# RETRY WITH EXPONENTIAL BACKOFF
# ============================================================

class RetryExhausted(Exception):
    """All retry attempts have been exhausted"""
    def __init__(self, message: str, attempts: int, last_exception: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    *args,
    config: ResilienceConfig = None,
    retryable_exceptions: tuple = (aiohttp.ClientError, asyncio.TimeoutError),
    on_retry: Callable[[int, Exception], None] = None,
    **kwargs
) -> T:
    """
    Execute function with retry and exponential backoff.
    
    Args:
        func: Async function to execute
        config: Resilience configuration
        retryable_exceptions: Tuple of exceptions that trigger retry
        on_retry: Callback called on each retry
        
    Returns:
        Result of the function
        
    Raises:
        RetryExhausted: If all retries fail
    """
    config = config or DEFAULT_CONFIG
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e
            
            if attempt >= config.max_retries:
                break
                
            # Calculate delay with exponential backoff and jitter
            delay = min(
                config.retry_base_delay * (2 ** attempt),
                config.retry_max_delay
            )
            # Add jitter
            import random
            jitter = delay * config.retry_jitter * random.random()
            delay += jitter
            
            structured_logger.warning(
                f"Retry {attempt + 1}/{config.max_retries}",
                attempt=attempt + 1,
                delay=delay,
                exception=str(e)
            )
            
            if on_retry:
                on_retry(attempt + 1, e)
                
            await asyncio.sleep(delay)
        except Exception as e:
            # Non-retryable exception
            last_exception = e
            break
    
    raise RetryExhausted(
        f"All {config.max_retries} retries exhausted",
        attempts=config.max_retries,
        last_exception=last_exception
    )


def with_retry(
    config: ResilienceConfig = None,
    retryable_exceptions: tuple = (aiohttp.ClientError, asyncio.TimeoutError)
):
    """Decorator for retry with exponential backoff"""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_with_backoff(
                func, *args,
                config=config,
                retryable_exceptions=retryable_exceptions,
                **kwargs
            )
        return wrapper
    return decorator


# ============================================================
# HEALTH CHECKS
# ============================================================

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    healthy: bool
    latency_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class HealthChecker:
    """
    Health check manager for all external dependencies.
    """
    
    def __init__(self, config: ResilienceConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.checks: Dict[str, Callable[[], Awaitable[HealthCheckResult]]] = {}
        self.last_results: Dict[str, HealthCheckResult] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    def register(self, name: str, check_func: Callable[[], Awaitable[HealthCheckResult]]):
        """Register a health check function"""
        self.checks[name] = check_func
        
    async def check_one(self, name: str) -> HealthCheckResult:
        """Run a single health check"""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                healthy=False,
                latency_ms=0,
                message=f"Unknown health check: {name}"
            )
        
        start = time.time()
        try:
            result = await asyncio.wait_for(
                self.checks[name](),
                timeout=self.config.health_check_timeout
            )
            result.latency_ms = (time.time() - start) * 1000
            self.last_results[name] = result
            return result
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                name=name,
                healthy=False,
                latency_ms=(time.time() - start) * 1000,
                message="Health check timed out"
            )
            self.last_results[name] = result
            return result
        except Exception as e:
            result = HealthCheckResult(
                name=name,
                healthy=False,
                latency_ms=(time.time() - start) * 1000,
                message=str(e)
            )
            self.last_results[name] = result
            return result
    
    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        results = {}
        for name in self.checks:
            results[name] = await self.check_one(name)
        return results
    
    async def start_background_checks(self):
        """Start background health check loop"""
        if self._running:
            return
            
        self._running = True
        
        async def _check_loop():
            while self._running:
                await self.check_all()
                await asyncio.sleep(self.config.health_check_interval)
        
        self._task = asyncio.create_task(_check_loop())
        structured_logger.info("Background health checks started")
        
    async def stop_background_checks(self):
        """Stop background health checks"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.last_results:
            return {"status": "unknown", "checks": {}}
        
        all_healthy = all(r.healthy for r in self.last_results.values())
        some_healthy = any(r.healthy for r in self.last_results.values())
        
        if all_healthy:
            status = "healthy"
        elif some_healthy:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                name: {
                    "healthy": result.healthy,
                    "latency_ms": round(result.latency_ms, 2),
                    "message": result.message,
                    "last_check": result.timestamp.isoformat()
                }
                for name, result in self.last_results.items()
            }
        }


# ============================================================
# DEAD LETTER QUEUE
# ============================================================

@dataclass
class DeadLetterItem:
    """Item in the dead letter queue"""
    id: str
    timestamp: datetime
    request_type: str
    request_data: Dict[str, Any]
    error_message: str
    exception_type: str
    retry_count: int = 0
    correlation_id: str = ""


class DeadLetterQueue:
    """
    Dead letter queue for failed requests.
    Stores failed requests for later processing or analysis.
    """
    
    def __init__(self, config: ResilienceConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.queue: deque = deque(maxlen=self.config.dlq_max_size)
        self._lock = asyncio.Lock()
        
    async def add(
        self,
        request_type: str,
        request_data: Dict[str, Any],
        exception: Exception
    ) -> str:
        """Add a failed request to the DLQ"""
        item = DeadLetterItem(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            request_type=request_type,
            request_data=request_data,
            error_message=str(exception),
            exception_type=type(exception).__name__,
            correlation_id=CorrelationContext.get_id()
        )
        
        async with self._lock:
            self.queue.append(item)
            
        structured_logger.warning(
            "Request added to DLQ",
            dlq_id=item.id,
            request_type=request_type,
            error=str(exception)
        )
        
        return item.id
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all items in the DLQ"""
        async with self._lock:
            return [
                {
                    "id": item.id,
                    "timestamp": item.timestamp.isoformat(),
                    "request_type": item.request_type,
                    "request_data": item.request_data,
                    "error_message": item.error_message,
                    "exception_type": item.exception_type,
                    "retry_count": item.retry_count,
                    "correlation_id": item.correlation_id
                }
                for item in self.queue
            ]
    
    async def get_by_id(self, item_id: str) -> Optional[DeadLetterItem]:
        """Get a specific item by ID"""
        async with self._lock:
            for item in self.queue:
                if item.id == item_id:
                    return item
        return None
    
    async def remove(self, item_id: str) -> bool:
        """Remove an item from the DLQ"""
        async with self._lock:
            for item in self.queue:
                if item.id == item_id:
                    self.queue.remove(item)
                    return True
        return False
    
    async def retry_item(
        self,
        item_id: str,
        retry_func: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> Optional[Any]:
        """Retry a failed request"""
        item = await self.get_by_id(item_id)
        if not item:
            return None
        
        try:
            result = await retry_func(item.request_data)
            await self.remove(item_id)
            structured_logger.info(
                "DLQ item successfully retried",
                dlq_id=item_id
            )
            return result
        except Exception as e:
            item.retry_count += 1
            item.error_message = str(e)
            structured_logger.error(
                "DLQ retry failed",
                dlq_id=item_id,
                retry_count=item.retry_count,
                exception=e
            )
            return None
    
    async def cleanup_old(self):
        """Remove items older than retention period"""
        cutoff = datetime.utcnow() - timedelta(hours=self.config.dlq_retention_hours)
        removed = 0
        
        async with self._lock:
            items_to_remove = [
                item for item in self.queue
                if item.timestamp < cutoff
            ]
            for item in items_to_remove:
                self.queue.remove(item)
                removed += 1
        
        if removed > 0:
            structured_logger.info(f"Cleaned up {removed} old DLQ items")
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get DLQ statistics"""
        return {
            "size": len(self.queue),
            "max_size": self.config.dlq_max_size,
            "oldest_item": self.queue[0].timestamp.isoformat() if self.queue else None,
            "by_type": self._count_by_type(),
            "by_error": self._count_by_error()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for item in self.queue:
            counts[item.request_type] = counts.get(item.request_type, 0) + 1
        return counts
    
    def _count_by_error(self) -> Dict[str, int]:
        counts = {}
        for item in self.queue:
            counts[item.exception_type] = counts.get(item.exception_type, 0) + 1
        return counts


# ============================================================
# METRICS COLLECTOR (Prometheus-compatible)
# ============================================================

class MetricsCollector:
    """
    Collect and expose metrics in Prometheus format.
    """
    
    def __init__(self):
        self.counters: Dict[str, Dict[str, int]] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        
    def increment_counter(self, name: str, labels: Dict[str, str] = None, value: int = 1):
        """Increment a counter metric"""
        key = self._make_key(name, labels)
        if key not in self.counters:
            self.counters[key] = {"labels": labels or {}, "value": 0}
        self.counters[key]["value"] += value
        
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram observation"""
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        # Keep last 1000 observations
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        # Counters
        for key, data in self.counters.items():
            lines.append(f"{key} {data['value']}")
        
        # Gauges
        for key, value in self.gauges.items():
            lines.append(f"{key} {value}")
        
        # Histograms (as summary)
        for key, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                lines.append(f"{key}_count {len(values)}")
                lines.append(f"{key}_sum {sum(values)}")
                # Percentiles
                for p in [0.5, 0.9, 0.99]:
                    idx = int(len(sorted_values) * p)
                    lines.append(f'{key}{{quantile="{p}"}} {sorted_values[min(idx, len(sorted_values)-1)]}')
        
        return "\n".join(lines)
    
    def get_json_metrics(self) -> Dict[str, Any]:
        """Export metrics as JSON"""
        result = {
            "counters": {},
            "gauges": {},
            "histograms": {}
        }
        
        for key, data in self.counters.items():
            result["counters"][key] = data["value"]
        
        for key, value in self.gauges.items():
            result["gauges"][key] = value
        
        for key, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                result["histograms"][key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p50": sorted_values[len(sorted_values) // 2],
                    "p90": sorted_values[int(len(sorted_values) * 0.9)],
                    "p99": sorted_values[int(len(sorted_values) * 0.99)]
                }
        
        return result

    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """
        Record an API request for metrics.
        
        Args:
            endpoint: The API endpoint path
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP response status code
            duration: Request duration in seconds
        """
        # Track request count
        self.increment_counter("http_requests_total", {
            "endpoint": endpoint,
            "method": method,
            "status": str(status_code)
        })
        
        # Track latency
        self.observe_histogram("http_request_duration_seconds", duration, {
            "endpoint": endpoint,
            "method": method
        })
        
        # Track errors
        if status_code >= 400:
            self.increment_counter("http_errors_total", {
                "endpoint": endpoint,
                "method": method,
                "status": str(status_code)
            })
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics for the API status endpoint."""
        result = {
            "latencies": {},
            "circuit_breakers": {}
        }
        
        # Aggregate latency data by endpoint
        for key, values in self.histograms.items():
            if "http_request_duration" in key and values:
                sorted_values = sorted(values)
                result["latencies"][key] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p50": sorted_values[len(sorted_values) // 2],
                    "p90": sorted_values[int(len(sorted_values) * 0.9)]
                }
        
        return result


# Global metrics instance
metrics = MetricsCollector()


# ============================================================
# RESILIENT HTTP CLIENT
# ============================================================

class ResilientHTTPClient:
    """
    HTTP client with built-in resilience features.
    
    Features:
    - Circuit breaker per host
    - Retry with exponential backoff
    - Connection pooling
    - Timeout handling
    - Metrics collection
    """
    
    def __init__(self, config: ResilienceConfig = None):
        self.config = config or DEFAULT_CONFIG
        self._session: Optional[aiohttp.ClientSession] = None
        self.dlq = DeadLetterQueue(config)
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.config.default_timeout,
                connect=self.config.connect_timeout
            )
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def request(
        self,
        method: str,
        url: str,
        circuit_name: str = None,
        use_circuit_breaker: bool = True,
        use_retry: bool = True,
        add_to_dlq_on_failure: bool = False,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make an HTTP request with resilience features.
        
        Args:
            method: HTTP method
            url: Request URL
            circuit_name: Name for circuit breaker (defaults to host)
            use_circuit_breaker: Enable circuit breaker
            use_retry: Enable retry
            add_to_dlq_on_failure: Add to dead letter queue on failure
            **kwargs: Additional arguments for aiohttp request
            
        Returns:
            aiohttp.ClientResponse
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        circuit_name = circuit_name or parsed.netloc
        
        start_time = time.time()
        
        # Check circuit breaker
        if use_circuit_breaker:
            breaker = CircuitBreakerRegistry.get(circuit_name, self.config)
            if not breaker.can_execute():
                metrics.increment_counter("http_circuit_open", {"host": circuit_name})
                raise Exception(f"Circuit breaker open for {circuit_name}")
        
        async def _make_request():
            session = await self.get_session()
            async with session.request(method, url, **kwargs) as response:
                # Force read body to ensure connection is released
                await response.read()
                return response
        
        try:
            if use_retry:
                response = await retry_with_backoff(
                    _make_request,
                    config=self.config
                )
            else:
                response = await _make_request()
            
            # Record success
            duration = time.time() - start_time
            metrics.increment_counter("http_requests_total", {"host": circuit_name, "status": str(response.status)})
            metrics.observe_histogram("http_request_duration_seconds", duration, {"host": circuit_name})
            
            if use_circuit_breaker:
                breaker.record_success()
            
            return response
            
        except Exception as e:
            # Record failure
            duration = time.time() - start_time
            metrics.increment_counter("http_requests_total", {"host": circuit_name, "status": "error"})
            metrics.observe_histogram("http_request_duration_seconds", duration, {"host": circuit_name})
            
            if use_circuit_breaker:
                breaker.record_failure(e)
            
            if add_to_dlq_on_failure:
                await self.dlq.add(
                    request_type=f"HTTP_{method}",
                    request_data={"url": url, "kwargs": str(kwargs)},
                    exception=e
                )
            
            raise


# ============================================================
# STARTUP HEALTH VALIDATION
# ============================================================

async def validate_provider_health(providers: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate all provider API keys and connectivity on startup.
    
    Returns dict of provider_name -> is_healthy
    """
    results = {}
    
    # Define health check for each provider type
    checks = {
        "groq": {
            "env_var": "GROQ_API_KEY",
            "test_url": "https://api.groq.com/openai/v1/models"
        },
        "openrouter": {
            "env_var": "OPENROUTER_API_KEY",
            "test_url": "https://openrouter.ai/api/v1/models"
        },
        "anthropic": {
            "env_var": "ANTHROPIC_API_KEY",
            "test_url": None  # No simple test endpoint
        },
        "deepseek": {
            "env_var": "DEEPSEEK_API_KEY",
            "test_url": "https://api.deepseek.com/v1/models"
        },
        "together_ai": {
            "env_var": "TOGETHER_API_KEY",
            "test_url": "https://api.together.xyz/v1/models"
        },
        "google": {
            "env_var": "GOOGLE_AI_API_KEY",
            "test_url": None
        },
        "perplexity": {
            "env_var": "PERPLEXITY_API_KEY",
            "test_url": None
        },
        "huggingface": {
            "env_var": "HUGGINGFACE_API_KEY",
            "test_url": "https://api-inference.huggingface.co/status"
        }
    }
    
    client = ResilientHTTPClient()
    
    try:
        for provider, config in checks.items():
            api_key = os.getenv(config["env_var"])
            
            if not api_key:
                results[provider] = False
                structured_logger.warning(
                    f"Provider {provider} not configured",
                    provider=provider,
                    env_var=config["env_var"]
                )
                continue
            
            if config["test_url"]:
                try:
                    response = await client.request(
                        "GET",
                        config["test_url"],
                        headers={"Authorization": f"Bearer {api_key}"},
                        use_retry=False,
                        use_circuit_breaker=False
                    )
                    results[provider] = response.status == 200
                except Exception as e:
                    results[provider] = False
                    structured_logger.warning(
                        f"Provider {provider} health check failed",
                        provider=provider,
                        error=str(e)
                    )
            else:
                # Assume healthy if key is set (no test endpoint)
                results[provider] = True
                
    finally:
        await client.close()
    
    # Log summary
    healthy = [p for p, h in results.items() if h]
    unhealthy = [p for p, h in results.items() if not h]
    
    structured_logger.info(
        "Provider health validation complete",
        healthy=healthy,
        unhealthy=unhealthy
    )
    
    return results


# ============================================================
# GRACEFUL SHUTDOWN
# ============================================================

class GracefulShutdown:
    """Handle graceful shutdown of services"""
    
    def __init__(self):
        self._shutting_down = False
        self._cleanup_tasks: List[Callable[[], Awaitable[None]]] = []
        
    def register_cleanup(self, func: Callable[[], Awaitable[None]]):
        """Register a cleanup function to run on shutdown"""
        self._cleanup_tasks.append(func)
        
    async def shutdown(self, timeout: float = 30.0):
        """Execute graceful shutdown"""
        if self._shutting_down:
            return
            
        self._shutting_down = True
        structured_logger.info("Initiating graceful shutdown...")
        
        for task in self._cleanup_tasks:
            try:
                await asyncio.wait_for(task(), timeout=timeout / len(self._cleanup_tasks))
            except asyncio.TimeoutError:
                structured_logger.warning(f"Cleanup task timed out: {task.__name__}")
            except Exception as e:
                structured_logger.error(f"Cleanup task failed: {task.__name__}", exception=e)
        
        structured_logger.info("Graceful shutdown complete")
    
    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down


# Global shutdown handler
shutdown_handler = GracefulShutdown()


# ============================================================
# CONTEXT MANAGERS
# ============================================================

@asynccontextmanager
async def resilient_operation(
    name: str,
    use_circuit_breaker: bool = True,
    use_retry: bool = True
):
    """
    Context manager for resilient operations.
    
    Usage:
        async with resilient_operation("my_api_call") as ctx:
            result = await my_api.call()
            ctx.record_success()
    """
    correlation_id = CorrelationContext.new_id()
    breaker = CircuitBreakerRegistry.get(name) if use_circuit_breaker else None
    start_time = time.time()
    
    class Context:
        def __init__(self):
            self.success = False
            
        def record_success(self):
            self.success = True
            if breaker:
                breaker.record_success()
    
    ctx = Context()
    
    try:
        if breaker and not breaker.can_execute():
            raise Exception(f"Circuit breaker open for {name}")
        yield ctx
    except Exception as e:
        if breaker:
            breaker.record_failure(e)
        metrics.increment_counter("operations_failed", {"name": name})
        raise
    finally:
        duration = time.time() - start_time
        metrics.observe_histogram("operation_duration_seconds", duration, {"name": name})
        CorrelationContext.clear()


# ============================================================
# MAIN / TESTING
# ============================================================

async def main():
    """Test resilience features"""
    
    # Test circuit breaker
    print("=== Testing Circuit Breaker ===")
    breaker = CircuitBreakerRegistry.get("test_service")
    
    for i in range(10):
        if breaker.can_execute():
            print(f"Call {i+1}: Executing...")
            if i < 5:
                breaker.record_success()
            else:
                breaker.record_failure(Exception("Simulated failure"))
        else:
            print(f"Call {i+1}: Rejected by circuit breaker")
        print(f"  State: {breaker.state.value}, Failures: {breaker.failure_count}")
    
    print(f"\nCircuit breaker stats: {breaker.get_stats()}")
    
    # Test health checker
    print("\n=== Testing Health Checker ===")
    health_checker = HealthChecker()
    
    async def test_check():
        return HealthCheckResult(name="test", healthy=True, latency_ms=0, message="OK")
    
    health_checker.register("test_service", test_check)
    results = await health_checker.check_all()
    print(f"Health check results: {results}")
    
    # Test DLQ
    print("\n=== Testing Dead Letter Queue ===")
    dlq = DeadLetterQueue()
    item_id = await dlq.add("test_request", {"data": "test"}, Exception("Test error"))
    print(f"Added item to DLQ: {item_id}")
    print(f"DLQ stats: {dlq.get_stats()}")
    
    # Test metrics
    print("\n=== Testing Metrics ===")
    metrics.increment_counter("test_counter", {"label": "value"})
    metrics.set_gauge("test_gauge", 42.0)
    metrics.observe_histogram("test_histogram", 0.5)
    print(f"JSON metrics: {json.dumps(metrics.get_json_metrics(), indent=2)}")
    
    # Validate providers
    print("\n=== Validating Providers ===")
    results = await validate_provider_health({})
    print(f"Provider health: {results}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
