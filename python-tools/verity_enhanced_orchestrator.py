"""
Verity Systems - Enhanced Verification Orchestrator
Integrates all new infrastructure with the verification engine:
- UnifiedLLMGateway (LiteLLM, Ollama, Groq, OpenRouter, DeepSeek, Together AI)
- Resilience layer (Circuit breakers, retries, health checks)
- Caching layer (Redis + Memory)
- Extended data sources (Academic, News, Knowledge bases)

This module provides a production-ready verification pipeline.

Author: Verity Systems
License: MIT
"""

import os
import asyncio
import aiohttp
import logging
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# Import Verity modules
from verity_supermodel import (
    VeritySuperModel,
    VerificationResult,
    VerificationStatus,
    VerificationSource,
    SourceCredibility,
    SecurityManager
)

# Import new infrastructure
from verity_unified_llm import UnifiedLLMGateway, LLMFactChecker
from verity_resilience import (
    ResilientHTTPClient,
    HealthChecker,
    MetricsCollector,
    GracefulShutdown,
    StructuredLogger
)
from verity_cache import VerificationCache, RequestCoalescer
from verity_data_sources import FactCheckAggregator, SourceResult

logger = StructuredLogger("EnhancedVerifier")


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class VerifierConfig:
    """Configuration for the enhanced verifier"""
    
    # LLM settings
    enable_llm_verification: bool = True
    llm_timeout_seconds: float = 30.0
    llm_fallback_enabled: bool = True
    
    # Cache settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    redis_url: Optional[str] = None
    
    # Data source settings
    enable_data_sources: bool = True
    max_sources_per_type: int = 5
    min_source_credibility: float = 0.6
    
    # Verification settings
    min_confidence_threshold: float = 0.3
    require_multiple_sources: bool = True
    enable_ai_consensus: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout_seconds: float = 60.0
    
    # Health check settings
    health_check_interval_seconds: int = 60
    
    @classmethod
    def from_env(cls) -> "VerifierConfig":
        """Load config from environment variables"""
        return cls(
            enable_llm_verification=os.getenv("ENABLE_LLM_VERIFICATION", "true").lower() == "true",
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            redis_url=os.getenv("REDIS_URL"),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT", "60")),
        )


# ============================================================
# ENHANCED VERIFICATION RESULT
# ============================================================

@dataclass
class EnhancedVerificationResult:
    """Extended verification result with additional metadata"""
    
    # Core result
    claim: str
    status: VerificationStatus
    confidence_score: float
    
    # Sources
    traditional_sources: List[VerificationSource]
    extended_sources: List[Dict]
    llm_analysis: Dict
    
    # Analysis
    summary: str
    explanation: str
    warnings: List[str]
    
    # Metadata
    request_id: str
    timestamp: datetime
    processing_time_ms: float
    cache_hit: bool
    providers_used: List[str]
    
    # Evidence
    supporting_evidence: List[Dict]
    contradicting_evidence: List[Dict]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "verdict": {
                "status": self.status.value,
                "confidence": round(self.confidence_score, 4),
                "summary": self.summary
            },
            "analysis": {
                "explanation": self.explanation,
                "supporting_evidence": self.supporting_evidence,
                "contradicting_evidence": self.contradicting_evidence
            },
            "sources": {
                "traditional_count": len(self.traditional_sources),
                "extended_count": len(self.extended_sources),
                "providers": self.providers_used
            },
            "llm_analysis": self.llm_analysis,
            "warnings": self.warnings,
            "metadata": {
                "request_id": self.request_id,
                "timestamp": self.timestamp.isoformat(),
                "processing_time_ms": round(self.processing_time_ms, 2),
                "cache_hit": self.cache_hit
            }
        }


# ============================================================
# ENHANCED VERIFIER
# ============================================================

class EnhancedVerifier:
    """
    Production-ready verification engine combining all infrastructure:
    
    1. Traditional fact-check APIs (Google, ClaimBuster, etc.)
    2. Extended data sources (Academic, News, Knowledge bases)
    3. Multi-LLM consensus (LiteLLM, Groq, DeepSeek, etc.)
    4. Redis caching for performance
    5. Circuit breakers for resilience
    6. Prometheus metrics for observability
    """
    
    def __init__(self, config: VerifierConfig = None):
        self.config = config or VerifierConfig.from_env()
        
        # Core components
        self.security = SecurityManager()
        self.super_model = VeritySuperModel()
        
        # New infrastructure
        self.llm_gateway: Optional[UnifiedLLMGateway] = None
        self.llm_checker: Optional[LLMFactChecker] = None
        self.data_sources: Optional[FactCheckAggregator] = None
        self.cache: Optional[VerificationCache] = None
        self.coalescer: Optional[RequestCoalescer] = None
        self.health_checker: Optional[HealthChecker] = None
        self.metrics = MetricsCollector()
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize all components"""
        if self._initialized:
            return
        
        logger.info("Initializing Enhanced Verifier")
        
        # Create shared session
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout_seconds)
        )
        
        # Initialize LLM gateway
        if self.config.enable_llm_verification:
            logger.info("Initializing LLM Gateway")
            self.llm_gateway = UnifiedLLMGateway()
            self.llm_checker = LLMFactChecker(self.llm_gateway)
        
        # Initialize data sources
        if self.config.enable_data_sources:
            logger.info("Initializing Data Sources")
            self.data_sources = FactCheckAggregator(self._session)
        
        # Initialize cache
        if self.config.enable_caching:
            logger.info("Initializing Cache")
            from verity_cache import CacheConfig
            cache_config = CacheConfig(
                redis_url=self.config.redis_url or 'redis://localhost:6379',
                default_ttl=self.config.cache_ttl_seconds,
                verification_ttl=self.config.cache_ttl_seconds
            )
            self.cache = VerificationCache(cache_config)
            self.coalescer = RequestCoalescer()
        
        # Initialize health checker
        self.health_checker = HealthChecker()
        
        self._initialized = True
        logger.info("Enhanced Verifier initialized successfully")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all components"""
        logger.info("Shutting down Enhanced Verifier")
        
        if self.data_sources:
            await self.data_sources.close()
        
        if self._session:
            await self._session.close()
        
        self._initialized = False
        logger.info("Enhanced Verifier shutdown complete")
    
    async def verify_claim(
        self,
        claim: str,
        user_id: Optional[str] = None,
        options: Dict[str, Any] = None
    ) -> EnhancedVerificationResult:
        """
        Verify a claim using all available resources.
        
        Args:
            claim: The claim to verify
            user_id: Optional user ID for rate limiting
            options: Optional verification options
        
        Returns:
            EnhancedVerificationResult with comprehensive analysis
        """
        start_time = time.time()
        request_id = hashlib.md5(f"{claim}{time.time()}".encode()).hexdigest()[:16]
        
        # Initialize if needed
        if not self._initialized:
            await self.initialize()
        
        # Sanitize input
        claim = self.security.sanitize_input(claim)
        
        # Check rate limit
        if user_id and not self.security.check_rate_limit(user_id):
            raise RateLimitExceededError(f"Rate limit exceeded for user {user_id}")
        
        # Check cache first
        cache_hit = False
        if self.cache:
            cached = await self.cache.get_verification(claim)
            if cached:
                logger.info(f"Cache hit for claim: {claim[:50]}...", request_id=request_id)
                cache_hit = True
                # Update with cache hit info and return
                cached["metadata"]["cache_hit"] = True
                return self._dict_to_result(cached, request_id, cache_hit=True)
        
        # Use request coalescing for concurrent identical requests
        if self.coalescer:
            async def verify_func():
                return await self._do_verification(claim, request_id, options or {})
            
            result_dict = await self.coalescer.execute(claim, verify_func)
        else:
            result_dict = await self._do_verification(claim, request_id, options or {})
        
        # Cache the result
        if self.cache and not cache_hit:
            await self.cache.set_verification(claim, result_dict)
        
        # Track metrics
        processing_time = (time.time() - start_time) * 1000
        self.metrics.record_request(
            endpoint="verify_claim",
            method="POST",
            status_code=200,
            duration=processing_time / 1000
        )
        
        result_dict["metadata"]["processing_time_ms"] = processing_time
        
        return self._dict_to_result(result_dict, request_id, cache_hit=cache_hit)
    
    async def _do_verification(
        self,
        claim: str,
        request_id: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform the actual verification across all sources.
        """
        logger.info(f"Starting verification for: {claim[:100]}...", request_id=request_id)
        
        providers_used = []
        warnings = []
        
        # Run verifications in parallel
        tasks = []
        
        # 1. Traditional fact-check (supermodel)
        tasks.append(self._run_traditional_verification(claim))
        providers_used.append("traditional_apis")
        
        # 2. Extended data sources
        if self.data_sources:
            tasks.append(self._run_extended_sources(claim))
            providers_used.append("extended_sources")
        
        # 3. LLM verification
        if self.llm_checker:
            tasks.append(self._run_llm_verification(claim))
            providers_used.append("llm_consensus")
        
        # Wait for all with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.request_timeout_seconds
            )
        except asyncio.TimeoutError:
            warnings.append("Some verification sources timed out")
            results = [None] * len(tasks)
        
        # Process results
        traditional_result = results[0] if len(results) > 0 else None
        extended_result = results[1] if len(results) > 1 else None
        llm_result = results[2] if len(results) > 2 else None
        
        # Handle exceptions
        if isinstance(traditional_result, Exception):
            warnings.append(f"Traditional verification failed: {str(traditional_result)[:100]}")
            traditional_result = None
        
        if isinstance(extended_result, Exception):
            warnings.append(f"Extended sources failed: {str(extended_result)[:100]}")
            extended_result = None
        
        if isinstance(llm_result, Exception):
            warnings.append(f"LLM verification failed: {str(llm_result)[:100]}")
            llm_result = None
        
        # Combine results
        combined = self._combine_results(
            claim=claim,
            traditional=traditional_result,
            extended=extended_result,
            llm=llm_result,
            warnings=warnings,
            providers_used=providers_used,
            request_id=request_id
        )
        
        return combined
    
    async def _run_traditional_verification(self, claim: str) -> VerificationResult:
        """Run traditional fact-check APIs"""
        return await self.super_model.verify_claim(claim)
    
    async def _run_extended_sources(self, claim: str) -> Dict[str, Any]:
        """Run extended data sources"""
        if not self.data_sources:
            return {}
        
        evidence = await self.data_sources.get_evidence_for_claim(
            claim,
            min_credibility=self.config.min_source_credibility
        )
        
        return evidence
    
    async def _run_llm_verification(self, claim: str) -> Dict[str, Any]:
        """Run multi-LLM consensus verification"""
        if not self.llm_checker:
            return {}
        
        result = await self.llm_checker.multi_model_verification(claim)
        return result
    
    def _combine_results(
        self,
        claim: str,
        traditional: Optional[VerificationResult],
        extended: Optional[Dict],
        llm: Optional[Dict],
        warnings: List[str],
        providers_used: List[str],
        request_id: str
    ) -> Dict[str, Any]:
        """
        Combine results from all sources into a unified verdict.
        Uses weighted voting based on source credibility.
        """
        verdicts = []
        confidences = []
        
        # Extract traditional verdict
        traditional_sources = []
        if traditional:
            verdicts.append((traditional.status.value, traditional.confidence_score, 0.4))
            confidences.append(traditional.confidence_score)
            traditional_sources = [
                {
                    "name": s.name,
                    "url": s.url,
                    "credibility": s.credibility.value,
                    "rating": s.claim_rating
                }
                for s in traditional.sources
            ]
        
        # Extract extended source verdict
        extended_sources = []
        if extended and extended.get("evidence_count", 0) > 0:
            # Use evidence strength as confidence
            evidence_strength = extended.get("evidence_strength", 0.5)
            confidences.append(evidence_strength)
            
            extended_sources = extended.get("top_sources", [])
        
        # Extract LLM verdict
        llm_analysis = {}
        if llm and llm.get("consensus"):
            llm_consensus = llm["consensus"]
            
            # Map LLM verdict to status
            llm_verdict = llm_consensus.get("verdict", "").upper()
            llm_confidence = llm_consensus.get("confidence", 0.5)
            
            status_map = {
                "TRUE": VerificationStatus.VERIFIED_TRUE.value,
                "FALSE": VerificationStatus.VERIFIED_FALSE.value,
                "PARTIALLY_TRUE": VerificationStatus.PARTIALLY_TRUE.value,
                "UNVERIFIABLE": VerificationStatus.UNVERIFIABLE.value,
            }
            
            mapped_status = status_map.get(llm_verdict, VerificationStatus.NEEDS_CONTEXT.value)
            verdicts.append((mapped_status, llm_confidence, 0.35))
            confidences.append(llm_confidence)
            
            llm_analysis = {
                "consensus": llm_consensus,
                "model_responses": llm.get("model_responses", []),
                "agreement_rate": llm.get("agreement_rate", 0)
            }
        
        # Calculate final verdict using weighted voting
        final_status, final_confidence = self._weighted_consensus(verdicts)
        
        # Override confidence if below threshold
        if final_confidence < self.config.min_confidence_threshold:
            warnings.append("Low confidence result - limited evidence available")
        
        # Determine supporting vs contradicting evidence
        supporting = []
        contradicting = []
        
        for source in traditional_sources + extended_sources:
            if isinstance(source, dict):
                rating = source.get("rating", "").lower() if source.get("rating") else ""
                if any(w in rating for w in ["true", "correct", "verified"]):
                    supporting.append(source)
                elif any(w in rating for w in ["false", "incorrect", "fake"]):
                    contradicting.append(source)
        
        # Generate explanation
        explanation = self._generate_explanation(
            claim=claim,
            status=final_status,
            traditional=traditional,
            extended=extended,
            llm=llm_analysis
        )
        
        # Generate summary
        summary = self._generate_summary(final_status, len(traditional_sources), len(extended_sources))
        
        return {
            "claim": claim,
            "verdict": {
                "status": final_status,
                "confidence": final_confidence,
                "summary": summary
            },
            "analysis": {
                "explanation": explanation,
                "supporting_evidence": supporting,
                "contradicting_evidence": contradicting
            },
            "sources": {
                "traditional": traditional_sources,
                "extended": extended_sources,
                "providers": providers_used
            },
            "llm_analysis": llm_analysis,
            "warnings": warnings,
            "metadata": {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": 0,  # Will be updated
                "cache_hit": False
            }
        }
    
    def _weighted_consensus(
        self,
        verdicts: List[Tuple[str, float, float]]
    ) -> Tuple[str, float]:
        """
        Calculate consensus using weighted voting.
        
        Args:
            verdicts: List of (status, confidence, weight) tuples
        
        Returns:
            (final_status, final_confidence)
        """
        if not verdicts:
            return VerificationStatus.UNVERIFIABLE.value, 0.0
        
        # Group verdicts
        status_scores = {}
        total_weight = 0
        
        for status, confidence, weight in verdicts:
            weighted_score = confidence * weight
            if status not in status_scores:
                status_scores[status] = 0
            status_scores[status] += weighted_score
            total_weight += weight
        
        if total_weight == 0:
            return VerificationStatus.UNVERIFIABLE.value, 0.0
        
        # Normalize scores
        for status in status_scores:
            status_scores[status] /= total_weight
        
        # Find highest scoring status
        best_status = max(status_scores.items(), key=lambda x: x[1])
        
        return best_status[0], best_status[1]
    
    def _generate_explanation(
        self,
        claim: str,
        status: str,
        traditional: Optional[VerificationResult],
        extended: Optional[Dict],
        llm: Dict
    ) -> str:
        """Generate a detailed explanation of the verification result"""
        
        parts = []
        
        # Status explanation
        status_explanations = {
            VerificationStatus.VERIFIED_TRUE.value: "This claim has been verified as TRUE based on multiple reliable sources.",
            VerificationStatus.VERIFIED_FALSE.value: "This claim has been verified as FALSE based on contradicting evidence.",
            VerificationStatus.PARTIALLY_TRUE.value: "This claim contains some truth but is incomplete or partially inaccurate.",
            VerificationStatus.UNVERIFIABLE.value: "This claim could not be verified due to insufficient evidence.",
            VerificationStatus.NEEDS_CONTEXT.value: "This claim requires additional context for proper verification.",
            VerificationStatus.DISPUTED.value: "This claim is disputed - sources disagree on its accuracy."
        }
        parts.append(status_explanations.get(status, "The verification status is unclear."))
        
        # Source summary
        if traditional and traditional.sources:
            parts.append(f"Consulted {len(traditional.sources)} traditional fact-checking sources.")
        
        if extended and extended.get("evidence_count"):
            parts.append(f"Found {extended['evidence_count']} pieces of supporting evidence from academic and news sources.")
        
        if llm and llm.get("consensus"):
            agreement = llm.get("agreement_rate", 0)
            parts.append(f"AI analysis showed {agreement:.0%} agreement across multiple language models.")
        
        return " ".join(parts)
    
    def _generate_summary(
        self,
        status: str,
        traditional_count: int,
        extended_count: int
    ) -> str:
        """Generate a brief summary"""
        status_labels = {
            VerificationStatus.VERIFIED_TRUE.value: "TRUE",
            VerificationStatus.VERIFIED_FALSE.value: "FALSE",
            VerificationStatus.PARTIALLY_TRUE.value: "PARTIALLY TRUE",
            VerificationStatus.UNVERIFIABLE.value: "UNVERIFIABLE",
            VerificationStatus.NEEDS_CONTEXT.value: "NEEDS CONTEXT",
            VerificationStatus.DISPUTED.value: "DISPUTED"
        }
        
        label = status_labels.get(status, "UNKNOWN")
        total_sources = traditional_count + extended_count
        
        return f"Verdict: {label} (based on {total_sources} sources)"
    
    def _dict_to_result(
        self,
        data: Dict,
        request_id: str,
        cache_hit: bool = False
    ) -> EnhancedVerificationResult:
        """Convert dictionary to EnhancedVerificationResult"""
        
        verdict = data.get("verdict", {})
        analysis = data.get("analysis", {})
        sources = data.get("sources", {})
        metadata = data.get("metadata", {})
        
        return EnhancedVerificationResult(
            claim=data.get("claim", ""),
            status=VerificationStatus(verdict.get("status", "unverifiable")),
            confidence_score=verdict.get("confidence", 0.0),
            traditional_sources=[],  # Would need conversion
            extended_sources=sources.get("extended", []),
            llm_analysis=data.get("llm_analysis", {}),
            summary=verdict.get("summary", ""),
            explanation=analysis.get("explanation", ""),
            warnings=data.get("warnings", []),
            request_id=request_id,
            timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
            processing_time_ms=metadata.get("processing_time_ms", 0),
            cache_hit=cache_hit,
            providers_used=sources.get("providers", []),
            supporting_evidence=analysis.get("supporting_evidence", []),
            contradicting_evidence=analysis.get("contradicting_evidence", [])
        )
    
    # ========================================
    # HEALTH & METRICS
    # ========================================
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all components"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check traditional APIs
        if self.super_model:
            providers = []
            for provider in self.super_model.providers:
                if provider.is_available:
                    providers.append(provider.name)
            health["components"]["traditional_apis"] = {
                "status": "healthy" if providers else "degraded",
                "available_providers": providers
            }
        
        # Check LLM gateway
        if self.llm_gateway:
            available_providers = self.llm_gateway.get_available_providers()
            health["components"]["llm_gateway"] = {
                "status": "healthy" if available_providers else "degraded",
                "available_providers": available_providers
            }
        
        # Check data sources
        if self.data_sources:
            available = self.data_sources.get_available_sources()
            health["components"]["data_sources"] = {
                "status": "healthy" if available else "degraded",
                "available_sources": available
            }
        
        # Check cache
        if self.cache:
            # VerificationCache wraps MultiLevelCache which has redis
            has_redis = hasattr(self.cache, 'cache') and hasattr(self.cache.cache, 'redis') and self.cache.cache.redis is not None
            health["components"]["cache"] = {
                "status": "healthy",
                "type": "redis" if has_redis else "memory"
            }
        
        # Determine overall status
        degraded = any(
            c.get("status") == "degraded"
            for c in health["components"].values()
        )
        health["status"] = "degraded" if degraded else "healthy"
        
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.get_all_metrics()


# ============================================================
# EXCEPTIONS
# ============================================================

class VerificationError(Exception):
    """Base verification error"""
    pass


class RateLimitExceededError(VerificationError):
    """Rate limit exceeded"""
    pass


class VerificationTimeoutError(VerificationError):
    """Verification timed out"""
    pass


# ============================================================
# SINGLETON / FACTORY
# ============================================================

_instance: Optional[EnhancedVerifier] = None


async def get_verifier(config: VerifierConfig = None) -> EnhancedVerifier:
    """Get or create the singleton Enhanced Verifier instance"""
    global _instance
    
    if _instance is None:
        _instance = EnhancedVerifier(config)
        await _instance.initialize()
    
    return _instance


async def shutdown_verifier():
    """Shutdown the singleton instance"""
    global _instance
    
    if _instance:
        await _instance.shutdown()
        _instance = None


# ============================================================
# MAIN / TESTING
# ============================================================

async def main():
    """Test the enhanced verifier"""
    
    print("\n" + "=" * 70)
    print("🚀 VERITY ENHANCED VERIFICATION ENGINE")
    print("=" * 70)
    
    config = VerifierConfig(
        enable_llm_verification=True,
        enable_caching=True,
        enable_data_sources=True
    )
    
    verifier = EnhancedVerifier(config)
    await verifier.initialize()
    
    test_claims = [
        "The Earth is approximately 4.5 billion years old",
        "Water boils at 100 degrees Celsius at sea level",
        "The Great Wall of China is visible from space with the naked eye",
    ]
    
    for claim in test_claims:
        print(f"\n📝 Claim: {claim}")
        print("-" * 50)
        
        try:
            result = await verifier.verify_claim(claim)
            
            print(f"✅ Verdict: {result.status.value}")
            print(f"📊 Confidence: {result.confidence_score:.1%}")
            print(f"⏱️  Time: {result.processing_time_ms:.0f}ms")
            print(f"📚 Sources: {len(result.traditional_sources) + len(result.extended_sources)}")
            print(f"💾 Cache Hit: {result.cache_hit}")
            
            if result.warnings:
                print(f"⚠️  Warnings: {', '.join(result.warnings)}")
            
            print(f"\n📋 {result.summary}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Health check
    print("\n" + "=" * 70)
    print("🏥 HEALTH STATUS")
    print("=" * 70)
    
    health = await verifier.get_health_status()
    print(json.dumps(health, indent=2))
    
    # Shutdown
    await verifier.shutdown()
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
