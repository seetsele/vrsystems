"""
Verity Systems - API Server v4.0
Production-Ready with Enhanced Infrastructure

Integrates:
- Enhanced verification engine with LiteLLM, Groq, OpenRouter, DeepSeek
- Redis caching for horizontal scaling
- Circuit breakers and retry logic
- Extended data sources (Academic, News, Knowledge bases)
- Prometheus metrics endpoint
- Health monitoring
- Graceful shutdown

Author: Verity Systems
License: MIT
"""

import os
import time
import asyncio
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import logging
import json
import hashlib

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, BackgroundTasks
from fastapi.security import HTTPBearer, APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, field_validator
import uvicorn

# Import enhanced modules
from verity_enhanced_orchestrator import (
    EnhancedVerifier,
    VerifierConfig,
    EnhancedVerificationResult,
    get_verifier,
    shutdown_verifier,
    RateLimitExceededError
)
from verity_resilience import (
    StructuredLogger,
    MetricsCollector,
    GracefulShutdown
)

# Import modules integration layer
from verity_modules_integration import (
    get_modules_integrator,
    VerityModulesIntegrator,
    IntegratedAnalysis
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = StructuredLogger('VerityAPIv4')


# ============================================================
# CONFIGURATION
# ============================================================

class AppConfig:
    """Application configuration"""
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    API_VERSION = "4.0.0"
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Cache
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Timeouts
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", 60.0))


config = AppConfig()


# ============================================================
# LIFESPAN MANAGEMENT
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Verity API Server v4.0...")
    
    # Initialize verifier
    verifier_config = VerifierConfig(
        enable_llm_verification=True,
        enable_caching=True,
        enable_data_sources=True,
        redis_url=config.REDIS_URL,
        request_timeout_seconds=config.REQUEST_TIMEOUT
    )
    
    app.state.verifier = await get_verifier(verifier_config)
    app.state.metrics = MetricsCollector()
    app.state.shutdown = GracefulShutdown()
    
    # Track startup
    app.state.startup_time = datetime.now()
    app.state.request_count = 0
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Graceful shutdown
    logger.info("Shutting down Verity API Server v4.0...")
    await shutdown_verifier()
    logger.info("Shutdown complete")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Verity Systems API v4",
    description="""
## 🚀 Production-Ready AI Fact-Checking Platform

### Features

- **Multi-LLM Verification**: LiteLLM, Groq, OpenRouter, DeepSeek, Together AI
- **Extended Data Sources**: Semantic Scholar, PubMed, arXiv, NewsAPI, Wikidata
- **Redis Caching**: Horizontal scaling with distributed cache
- **Circuit Breakers**: Automatic failover and recovery
- **Prometheus Metrics**: Full observability
- **Health Monitoring**: Real-time health checks

### Quick Start

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v4/verify",
    json={"claim": "The Earth is approximately 4.5 billion years old"}
)
print(response.json())
```

### Endpoints

- `POST /api/v4/verify` - Verify a single claim
- `POST /api/v4/batch` - Verify multiple claims
- `GET /health` - Health check
- `GET /health/detailed` - Detailed component health
- `GET /metrics` - Prometheus metrics
- `GET /status` - API status and uptime
    """,
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================
# MIDDLEWARE
# ============================================================

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS if config.ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
        "X-Process-Time",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining"
    ]
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request tracking and timing"""
    start_time = time.time()
    
    # Generate request ID
    request_id = hashlib.md5(
        f"{time.time()}{request.client.host}".encode()
    ).hexdigest()[:16]
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate timing
    process_time = (time.time() - start_time) * 1000
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms",
        request_id=request_id
    )
    
    # Track metrics
    app.state.request_count += 1
    app.state.metrics.record_request(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=process_time / 1000
    )
    
    return response


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class VerifyRequest(BaseModel):
    """Verification request model"""
    claim: str = Field(..., min_length=10, max_length=10000, description="The claim to verify")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional verification settings")
    
    @field_validator('claim')
    @classmethod
    def sanitize_claim(cls, v: str) -> str:
        # Basic sanitization
        v = v.strip()
        v = ' '.join(v.split())  # Normalize whitespace
        return v


class BatchVerifyRequest(BaseModel):
    """Batch verification request"""
    claims: List[str] = Field(..., min_length=1, max_length=10, description="Claims to verify")
    options: Optional[Dict[str, Any]] = None


class VerifyResponse(BaseModel):
    """Verification response model"""
    request_id: str
    claim: str
    verdict: str
    confidence: float
    summary: str
    explanation: str
    source_count: int
    warnings: List[str]
    processing_time_ms: float
    cache_hit: bool
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime_seconds: float
    timestamp: str


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    return {"message": "Verity API v4.0 - Visit /docs for documentation"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Basic health check"""
    uptime = (datetime.now() - app.state.startup_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version=config.API_VERSION,
        uptime_seconds=uptime,
        timestamp=datetime.now().isoformat()
    )


@app.get("/health/detailed", tags=["Health"])
async def detailed_health():
    """Detailed component health check"""
    verifier: EnhancedVerifier = app.state.verifier
    health = await verifier.get_health_status()
    
    # Add API-level info
    uptime = (datetime.now() - app.state.startup_time).total_seconds()
    health["api"] = {
        "version": config.API_VERSION,
        "uptime_seconds": uptime,
        "total_requests": app.state.request_count
    }
    
    return health


@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics = app.state.metrics
    
    # Build Prometheus format
    lines = []
    
    # Request counts
    lines.append("# HELP verity_requests_total Total number of requests")
    lines.append("# TYPE verity_requests_total counter")
    lines.append(f'verity_requests_total {app.state.request_count}')
    
    # Get detailed metrics
    all_metrics = metrics.get_all_metrics()
    
    # Request latencies
    lines.append("# HELP verity_request_duration_seconds Request duration in seconds")
    lines.append("# TYPE verity_request_duration_seconds histogram")
    for endpoint, data in all_metrics.get("latencies", {}).items():
        avg = data.get("avg", 0)
        lines.append(f'verity_request_duration_seconds_sum{{endpoint="{endpoint}"}} {avg * data.get("count", 1)}')
        lines.append(f'verity_request_duration_seconds_count{{endpoint="{endpoint}"}} {data.get("count", 0)}')
    
    # Circuit breaker status
    lines.append("# HELP verity_circuit_breaker_status Circuit breaker status (0=closed, 1=open, 2=half-open)")
    lines.append("# TYPE verity_circuit_breaker_status gauge")
    for provider, status in all_metrics.get("circuit_breakers", {}).items():
        status_value = {"closed": 0, "open": 1, "half_open": 2}.get(status.lower(), 0)
        lines.append(f'verity_circuit_breaker_status{{provider="{provider}"}} {status_value}')
    
    # Uptime
    uptime = (datetime.now() - app.state.startup_time).total_seconds()
    lines.append("# HELP verity_uptime_seconds Server uptime in seconds")
    lines.append("# TYPE verity_uptime_seconds gauge")
    lines.append(f"verity_uptime_seconds {uptime}")
    
    return "\n".join(lines)


@app.get("/status", tags=["Status"])
async def api_status():
    """API status and statistics"""
    uptime = (datetime.now() - app.state.startup_time).total_seconds()
    
    return {
        "status": "operational",
        "version": config.API_VERSION,
        "uptime_seconds": uptime,
        "uptime_human": str(timedelta(seconds=int(uptime))),
        "total_requests": app.state.request_count,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/verify", response_model=VerifyResponse, tags=["Verification"])
async def verify_claim(request: VerifyRequest, req: Request):
    """
    Verify a single claim.
    
    This endpoint uses multiple AI models, fact-checking APIs, and
    academic sources to verify the truthfulness of a claim.
    
    **Example:**
    ```json
    {
        "claim": "The Great Wall of China is visible from space"
    }
    ```
    """
    start_time = time.time()
    request_id = req.state.request_id
    
    try:
        verifier: EnhancedVerifier = app.state.verifier
        
        # Get client ID for rate limiting (use IP for now)
        client_id = req.client.host if req.client else "unknown"
        
        # Perform verification
        result = await verifier.verify_claim(
            claim=request.claim,
            user_id=client_id,
            options=request.options
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return VerifyResponse(
            request_id=request_id,
            claim=request.claim,
            verdict=result.status.value,
            confidence=round(result.confidence_score, 4),
            summary=result.summary,
            explanation=result.explanation,
            source_count=len(result.traditional_sources) + len(result.extended_sources),
            warnings=result.warnings,
            processing_time_ms=round(processing_time, 2),
            cache_hit=result.cache_hit,
            timestamp=datetime.now().isoformat()
        )
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    except Exception as e:
        logger.error(f"Verification error: {e}", request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@app.post("/api/v4/verify/detailed", tags=["Verification"])
async def verify_claim_detailed(request: VerifyRequest, req: Request):
    """
    Verify a claim with full detailed response.
    
    Returns complete information including:
    - All sources consulted
    - LLM analysis from multiple models
    - Supporting and contradicting evidence
    - Processing metadata
    """
    start_time = time.time()
    request_id = req.state.request_id
    
    try:
        verifier: EnhancedVerifier = app.state.verifier
        client_id = req.client.host if req.client else "unknown"
        
        result = await verifier.verify_claim(
            claim=request.claim,
            user_id=client_id,
            options=request.options
        )
        
        # Return full result
        return result.to_dict()
        
    except RateLimitExceededError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    except Exception as e:
        logger.error(f"Verification error: {e}", request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v4/batch", tags=["Verification"])
async def batch_verify(request: BatchVerifyRequest, req: Request, background_tasks: BackgroundTasks):
    """
    Verify multiple claims in a single request.
    
    Limited to 10 claims per request to prevent abuse.
    Claims are processed in parallel for efficiency.
    """
    request_id = req.state.request_id
    start_time = time.time()
    
    try:
        verifier: EnhancedVerifier = app.state.verifier
        client_id = req.client.host if req.client else "unknown"
        
        # Process claims in parallel
        tasks = [
            verifier.verify_claim(claim, user_id=client_id, options=request.options)
            for claim in request.claims
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format results
        formatted = []
        for claim, result in zip(request.claims, results):
            if isinstance(result, Exception):
                formatted.append({
                    "claim": claim,
                    "error": str(result),
                    "verdict": None
                })
            else:
                formatted.append({
                    "claim": claim,
                    "verdict": result.status.value,
                    "confidence": round(result.confidence_score, 4),
                    "summary": result.summary
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "request_id": request_id,
            "claims_processed": len(request.claims),
            "results": formatted,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch verification error: {e}", request_id=request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v4/providers", tags=["Info"])
async def list_providers():
    """List all available verification providers"""
    verifier: EnhancedVerifier = app.state.verifier
    health = await verifier.get_health_status()
    
    providers = {
        "traditional_apis": health["components"].get("traditional_apis", {}).get("available_providers", []),
        "llm_providers": health["components"].get("llm_gateway", {}).get("available_providers", []),
        "data_sources": health["components"].get("data_sources", {}).get("available_sources", [])
    }
    
    total = sum(len(v) for v in providers.values())
    
    return {
        "total_providers": total,
        "providers": providers
    }


# ============================================================
# ADVANCED ANALYSIS ENDPOINTS
# ============================================================

class NLPAnalysisRequest(BaseModel):
    """Request for NLP analysis"""
    claim: str = Field(..., min_length=5, max_length=10000)


class SimilarityRequest(BaseModel):
    """Request for similar claims search"""
    claim: str = Field(..., min_length=5, max_length=10000)
    limit: int = Field(10, ge=1, le=50)


class SourceCredibilityRequest(BaseModel):
    """Request for source credibility check"""
    domains: Optional[List[str]] = Field(None, min_length=1, max_length=50, alias="sources")
    sources: Optional[List[str]] = Field(None, min_length=1, max_length=50)
    
    @property
    def get_domains(self) -> List[str]:
        return self.domains or self.sources or []


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo confidence analysis"""
    claim: Optional[str] = Field(None, min_length=5)
    evidence: Optional[List[Dict[str, Any]]] = None
    evidence_scores: Optional[List[float]] = None
    
    @property
    def get_evidence(self) -> List[Dict[str, Any]]:
        if self.evidence:
            return self.evidence
        if self.evidence_scores:
            return [{"score": s, "source": f"source_{i}"} for i, s in enumerate(self.evidence_scores)]
        return []


class ComprehensiveAnalysisRequest(BaseModel):
    """Request for comprehensive claim analysis"""
    claim: str = Field(..., min_length=5, max_length=10000)
    evidence: Optional[List[Dict[str, Any]]] = None
    sources_used: Optional[List[str]] = None


@app.get("/api/v4/modules", tags=["Advanced Analysis"])
async def list_modules():
    """
    List all available analysis modules and their status.
    
    Shows which advanced capabilities are active.
    """
    integrator = get_modules_integrator()
    status = integrator.get_module_status()
    
    active = sum(1 for v in status.values() if v)
    
    return {
        "total_modules": len(status),
        "active_modules": active,
        "modules": status,
        "descriptions": {
            "advanced_nlp": "Fallacy, propaganda, and bias detection",
            "claim_similarity": "Find similar fact-checked claims",
            "monte_carlo": "Probabilistic confidence intervals",
            "source_database": "Source credibility ratings",
            "consensus_engine": "Multi-source voting aggregation",
            "evidence_graph": "Knowledge graph analysis",
            "numerical_verification": "Statistics and numbers validation",
            "temporal_reasoning": "Time-based claim verification",
            "geospatial_reasoning": "Location-based verification",
            "social_media": "Viral claim tracking",
            "adaptive_learning": "Self-improving AI"
        }
    }


@app.post("/api/v4/analyze/nlp", tags=["Advanced Analysis"])
async def analyze_nlp(request: NLPAnalysisRequest):
    """
    Perform advanced NLP analysis on a claim.
    
    Detects:
    - **Logical fallacies** (ad hominem, strawman, etc.)
    - **Propaganda techniques** (fear mongering, loaded language, etc.)
    - **Bias indicators** (political, emotional, sensational)
    - **Named entities** (people, organizations, locations, numbers)
    - **Sentiment and subjectivity scores**
    - **Verifiability assessment**
    
    This is useful for understanding the rhetorical structure of a claim
    before fact-checking it.
    """
    integrator = get_modules_integrator()
    
    result = integrator.analyze_nlp(request.claim)
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="NLP analysis module not available"
        )
    
    return {
        "claim": request.claim,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/similar", tags=["Advanced Analysis"])
async def find_similar_claims(request: SimilarityRequest):
    """
    Find similar claims that have been previously fact-checked.
    
    Uses TF-IDF and semantic similarity to find related claims.
    This helps avoid redundant fact-checking and leverage existing work.
    
    Returns:
    - Similar claim text
    - Similarity score (0-1)
    - Previous verdict (if available)
    - Source of original fact-check
    """
    integrator = get_modules_integrator()
    
    results = integrator.find_similar_claims(request.claim, limit=request.limit)
    
    if not results and not integrator._module_status.get("claim_similarity"):
        raise HTTPException(
            status_code=503,
            detail="Claim similarity module not available"
        )
    
    return {
        "claim": request.claim,
        "similar_claims": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/sources", tags=["Advanced Analysis"])
async def check_source_credibility(request: SourceCredibilityRequest):
    """
    Check the credibility of news sources and websites.
    
    Database includes ratings for:
    - Major news organizations
    - Scientific journals
    - Government sources
    - Known misinformation sources
    
    Returns:
    - Credibility score (0-100)
    - Factual reporting rating
    - Political bias rating
    - Credibility tier (1-5)
    """
    integrator = get_modules_integrator()
    
    domains = request.get_domains
    if not domains:
        raise HTTPException(status_code=400, detail="Must provide 'sources' or 'domains' field")
    
    results = integrator.get_batch_source_credibility(domains)
    
    if not results and not integrator._module_status.get("source_database"):
        raise HTTPException(
            status_code=503,
            detail="Source credibility module not available"
        )
    
    return {
        "sources_requested": len(domains),
        "sources_found": len(results),
        "results": results,
        "not_found": [d for d in domains if d not in results],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/confidence", tags=["Advanced Analysis"])
async def monte_carlo_confidence(request: MonteCarloRequest):
    """
    Calculate probabilistic confidence using Monte Carlo simulation.
    
    Provide evidence from multiple sources, each with:
    - source_name: Name of the source
    - verdict: 'true', 'false', 'mixed', or 'unknown'
    - confidence: How confident the source is (0-1)
    - credibility: How credible the source is (0-1)
    
    Or simply provide evidence_scores as a list of floats.
    
    Returns:
    - Final verdict with probability
    - 95% confidence interval
    - Probability distribution across verdicts
    - Convergence score
    """
    integrator = get_modules_integrator()
    
    evidence = request.get_evidence
    if not evidence:
        raise HTTPException(status_code=400, detail="Must provide 'evidence' or 'evidence_scores' field")
    
    result = integrator.calculate_monte_carlo_confidence(evidence)
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Monte Carlo module not available"
        )
    
    return {
        "evidence_count": len(evidence),
        "result": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/numerical", tags=["Advanced Analysis"])
async def analyze_numerical_claims(request: NLPAnalysisRequest):
    """
    Analyze numerical claims and statistics in text.
    
    Detects and validates:
    - Percentages
    - Statistics
    - Comparisons
    - Growth rates
    - Financial figures
    """
    integrator = get_modules_integrator()
    
    result = integrator.analyze_numerical_claims(request.claim)
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Numerical verification module not available"
        )
    
    return {
        "claim": request.claim,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/temporal", tags=["Advanced Analysis"])
async def analyze_temporal_claims(request: NLPAnalysisRequest):
    """
    Analyze time-based claims in text.
    
    Detects:
    - Date references
    - Time periods
    - Historical sequences
    - Anachronisms
    """
    integrator = get_modules_integrator()
    
    result = integrator.analyze_temporal_claims(request.claim)
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Temporal reasoning module not available"
        )
    
    return {
        "claim": request.claim,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/geospatial", tags=["Advanced Analysis"])
async def analyze_geospatial_claims(request: NLPAnalysisRequest):
    """
    Analyze location-based claims in text.
    
    Detects:
    - Place names
    - Geographic relationships
    - Distance claims
    - Location inconsistencies
    """
    integrator = get_modules_integrator()
    
    result = integrator.analyze_geospatial_claims(request.claim)
    
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Geospatial reasoning module not available"
        )
    
    return {
        "claim": request.claim,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v4/analyze/comprehensive", tags=["Advanced Analysis"])
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    """
    Perform COMPREHENSIVE analysis using ALL available modules.
    
    This is the ultimate analysis endpoint that combines:
    - NLP analysis (fallacies, propaganda, bias)
    - Similar claims search
    - Monte Carlo confidence (if evidence provided)
    - Source credibility (if sources provided)
    - Numerical verification
    - Temporal reasoning
    - Geospatial analysis
    
    Use this for deep investigation of complex claims.
    """
    integrator = get_modules_integrator()
    
    result = await integrator.analyze_complete(
        claim=request.claim,
        evidence=request.evidence,
        sources_used=request.sources_used
    )
    
    return result.to_dict()


# ============================================================
# V3 COMPATIBILITY ENDPOINTS
# ============================================================
# These endpoints maintain backwards compatibility with the frontend

class V3VerifyRequest(BaseModel):
    """V3 API verification request"""
    claim: str = Field(..., min_length=5, max_length=10000)
    check_type: Optional[str] = Field("comprehensive", description="Type of check: quick, standard, comprehensive")


@app.post("/v3/verify", tags=["V3 Compatibility"])
async def v3_verify(request: V3VerifyRequest, req: Request):
    """
    V3-compatible verification endpoint.
    
    Provides backwards compatibility with older frontend versions.
    """
    try:
        verifier: EnhancedVerifier = app.state.verifier
        client_id = req.client.host if req.client else "unknown"
        
        result = await verifier.verify_claim(
            claim=request.claim,
            user_id=client_id,
            options={"check_type": request.check_type}
        )
        
        # Format in V3 style
        return {
            "success": True,
            "claim": request.claim,
            "result": {
                "verdict": result.status.value,
                "confidence": round(result.confidence_score, 4),
                "summary": result.summary,
                "explanation": result.explanation
            },
            "sources": {
                "count": len(result.traditional_sources) + len(result.extended_sources),
                "providers": result.providers_used
            },
            "warnings": result.warnings,
            "cached": result.cache_hit,
            "timestamp": datetime.now().isoformat()
        }
    except RateLimitExceededError:
        return {"success": False, "error": "Rate limit exceeded"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/v3/quick-check", tags=["V3 Compatibility"])
async def v3_quick_check(request: V3VerifyRequest, req: Request):
    """Quick check endpoint for V3 compatibility"""
    request.check_type = "quick"
    return await v3_verify(request, req)


@app.post("/v3/verify/batch", tags=["V3 Compatibility"])
async def v3_batch_verify(claims: List[str], req: Request):
    """Batch verification for V3 compatibility"""
    results = []
    for claim in claims[:10]:  # Limit to 10
        try:
            v3_req = V3VerifyRequest(claim=claim)
            result = await v3_verify(v3_req, req)
            results.append(result)
        except Exception as e:
            results.append({"success": False, "claim": claim, "error": str(e)})
    
    return {
        "success": True,
        "count": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/v3/providers", tags=["V3 Compatibility"])
async def v3_list_providers():
    """List providers for V3 compatibility"""
    return await list_providers()


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


# ============================================================
# MAIN
# ============================================================

def run():
    """Run the server"""
    uvicorn.run(
        "api_server_v4:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    run()
