"""
Verity API Server - PRODUCTION EDITION
======================================
Industry-leading fact verification with enterprise security

Features:
- 3-Pass Verification with 75+ sources
- JWT Authentication
- Rate Limiting (sliding window)
- Request Validation
- CORS Security
- Comprehensive Logging
- Health Monitoring
- Graceful Shutdown
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
from functools import wraps
from collections import defaultdict
from contextlib import asynccontextmanager

import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Application configuration from environment variables"""
    
    # Environment
    ENV = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENV == "development"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Security
    SECRET_KEY = os.getenv("VERITY_SECRET_KEY", secrets.token_hex(32))
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 24))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))  # seconds
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # API Keys (for demo mode)
    API_KEYS = set(os.getenv("API_KEYS", "demo-key-12345,test-key-67890").split(","))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure structured logging for production"""
    log_format = json.dumps({
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "logger": "%(name)s",
        "message": "%(message)s",
        "module": "%(module)s",
        "function": "%(funcName)s",
        "line": "%(lineno)d"
    }) if Config.ENV == "production" else "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("verity_api.log") if Config.ENV == "production" else logging.NullHandler()
        ]
    )
    return logging.getLogger("VerityAPI")

logger = setup_logging()


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """Check if request is allowed and return rate limit info"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[identifier] = [
            ts for ts in self.requests[identifier] 
            if ts > window_start
        ]
        
        current_count = len(self.requests[identifier])
        remaining = max(0, self.max_requests - current_count)
        
        if current_count >= self.max_requests:
            reset_time = int(self.requests[identifier][0] + self.window_seconds - now)
            return False, {
                "limit": self.max_requests,
                "remaining": 0,
                "reset": reset_time
            }
        
        self.requests[identifier].append(now)
        return True, {
            "limit": self.max_requests,
            "remaining": remaining - 1,
            "reset": self.window_seconds
        }

rate_limiter = RateLimiter(Config.RATE_LIMIT_REQUESTS, Config.RATE_LIMIT_WINDOW)


# =============================================================================
# AUTHENTICATION
# =============================================================================

security = HTTPBearer(auto_error=False)

class AuthService:
    """JWT Authentication Service"""
    
    @staticmethod
    def create_token(user_id: str, tier: str = "free") -> str:
        """Create a JWT token"""
        payload = {
            "sub": user_id,
            "tier": tier,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS),
            "jti": secrets.token_hex(16)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def verify_api_key(api_key: str) -> bool:
        """Verify an API key"""
        return api_key in Config.API_KEYS

auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> dict:
    """Dependency to get current authenticated user"""
    
    # Check API key first
    if x_api_key and auth_service.verify_api_key(x_api_key):
        return {"user_id": f"api_key_{hashlib.md5(x_api_key.encode()).hexdigest()[:8]}", "tier": "api"}
    
    # Check JWT token
    if credentials:
        payload = auth_service.verify_token(credentials.credentials)
        if payload:
            return {"user_id": payload["sub"], "tier": payload.get("tier", "free")}
    
    # Allow anonymous access in development
    if Config.DEBUG:
        return {"user_id": "anonymous", "tier": "demo"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication",
        headers={"WWW-Authenticate": "Bearer"}
    )


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ClaimRequest(BaseModel):
    claim: str = Field(..., min_length=5, max_length=5000, description="The claim to verify")
    detailed: bool = Field(False, description="Include detailed pass breakdown")
    
    @validator('claim')
    def clean_claim(cls, v):
        # Basic sanitization
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Claim must be at least 5 characters")
        return v

class URLRequest(BaseModel):
    url: str = Field(..., description="URL to analyze")
    
    @validator('url')
    def validate_url(cls, v):
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

class TextRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="Text to analyze")

class BatchRequest(BaseModel):
    items: List[Dict[str, str]] = Field(..., max_items=100, description="Items to process")
    max_concurrent: int = Field(5, ge=1, le=20, description="Max concurrent requests")

class TokenRequest(BaseModel):
    api_key: str = Field(..., description="API key to exchange for token")


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown handlers"""
    # Startup
    logger.info(f"[START] Verity API v7 ({Config.ENV} mode)")
    logger.info(f"[LISTEN] {Config.HOST}:{Config.PORT}")
    
    # Validate critical environment variables
    missing_vars = []
    recommended_vars = ["GROQ_API_KEY", "GOOGLE_AI_API_KEY", "PERPLEXITY_API_KEY"]
    for var in recommended_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"[WARN] Missing recommended API keys: {', '.join(missing_vars)}")
        logger.warning("   Some providers will be unavailable")
    
    yield
    
    # Shutdown
    logger.info("[STOP] Shutting down Verity API")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Verity Verification API",
    description="Industry-leading AI-powered fact verification with 75+ sources",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS if Config.ENV == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

if Config.ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*.verity.systems", "localhost"]
    )


# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    # Get client identifier
    client_ip = request.client.host if request.client else "unknown"
    api_key = request.headers.get("X-API-Key", "")
    identifier = api_key if api_key else client_ip
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Check rate limit
    allowed, rate_info = rate_limiter.is_allowed(identifier)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "retry_after": rate_info["reset"]
            },
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(rate_info["reset"])
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
    
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.2f}ms | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/")
async def root():
    """API Information"""
    return {
        "name": "Verity Verification API",
        "version": "7.0.0",
        "environment": Config.ENV,
        "features": [
            "3-pass verification",
            "75+ data sources",
            "Cross-referencing",
            "Consensus voting",
            "URL analysis",
            "Batch processing",
            "JWT authentication",
            "Rate limiting"
        ],
        "endpoints": {
            "/verify": "POST - Verify a claim",
            "/analyze/url": "POST - Analyze URL content",
            "/analyze/text": "POST - Analyze text content",
            "/batch": "POST - Batch processing",
            "/token": "POST - Get JWT token",
            "/health": "GET - Health check",
            "/stats": "GET - System statistics"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "7.0.0",
        "environment": Config.ENV
    }


@app.post("/token")
async def get_token(request: TokenRequest):
    """Exchange API key for JWT token"""
    if not auth_service.verify_api_key(request.api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    token = auth_service.create_token(
        user_id=f"api_{hashlib.md5(request.api_key.encode()).hexdigest()[:8]}",
        tier="api"
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": Config.JWT_EXPIRY_HOURS * 3600
    }


@app.post("/verify")
async def verify_claim(
    request: ClaimRequest,
    user: dict = Depends(get_current_user)
):
    """
    Verify a claim using 3-pass verification system
    
    - **Pass 1**: Search providers (Tavily, Brave, Serper)
    - **Pass 2**: AI cross-validation (Groq, Gemini, Perplexity, Mistral)
    - **Pass 3**: High-trust sources (Academic, Government)
    """
    logger.info(f"Verifying claim for user {user['user_id']}: {request.claim[:50]}...")
    
    try:
        from verity_ultimate_verification import UltimateVerificationOrchestrator
        
        async with UltimateVerificationOrchestrator() as orchestrator:
            result = await orchestrator.verify_claim(request.claim)
        
        response = {
            "claim": result.claim,
            "verdict": result.final_verdict,
            "confidence": result.final_confidence,
            "category": result.category.value,
            "consistency": result.consistency_score,
            "sources": result.total_sources,
            "cross_references": result.cross_references,
            "time": result.time,
            "timestamp": result.timestamp
        }
        
        if request.detailed:
            response["passes"] = {
                name: {
                    "verdict": consensus.verdict,
                    "confidence": consensus.confidence,
                    "agreement": consensus.agreement,
                    "sources_agree": consensus.sources_agree,
                    "sources_disagree": consensus.sources_disagree,
                    "evidence": consensus.evidence
                }
                for name, consensus in result.pass_results.items()
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.post("/analyze/url")
async def analyze_url(
    request: URLRequest,
    user: dict = Depends(get_current_user)
):
    """Analyze URL content for credibility and claims"""
    logger.info(f"Analyzing URL for user {user['user_id']}: {request.url}")
    
    try:
        from verity_comprehensive_analyzer import ComprehensiveAnalyzer
        
        async with ComprehensiveAnalyzer() as analyzer:
            result = await analyzer.analyze_url(request.url)
        
        return result
        
    except Exception as e:
        logger.error(f"URL analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/text")
async def analyze_text(
    request: TextRequest,
    user: dict = Depends(get_current_user)
):
    """Extract and verify claims from text"""
    logger.info(f"Analyzing text for user {user['user_id']}: {len(request.text)} chars")
    
    try:
        from verity_comprehensive_analyzer import ComprehensiveAnalyzer
        
        async with ComprehensiveAnalyzer() as analyzer:
            result = await analyzer.analyze_text(request.text)
        
        return result
        
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/batch")
async def batch_process(
    request: BatchRequest,
    user: dict = Depends(get_current_user)
):
    """Batch process multiple claims or URLs"""
    logger.info(f"Batch processing {len(request.items)} items for user {user['user_id']}")
    
    try:
        from verity_comprehensive_analyzer import ComprehensiveAnalyzer
        
        async with ComprehensiveAnalyzer() as analyzer:
            result = await analyzer.batch_analyze(request.items, request.max_concurrent)
        
        return {
            "total": result.total,
            "processed": result.processed,
            "failed": result.failed,
            "time": result.time,
            "results": result.results
        }
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """System statistics and capabilities"""
    return {
        "version": "7.0.0",
        "verification": {
            "passes": 3,
            "providers": 75,
            "consensus_algorithm": "weighted_voting"
        },
        "categories": [
            "Academic", "Government", "News", 
            "Knowledge Graphs", "Search", "AI Models"
        ],
        "features": {
            "three_pass_verification": True,
            "cross_referencing": True,
            "consensus_voting": True,
            "url_analysis": True,
            "text_analysis": True,
            "batch_processing": True,
            "rate_limiting": True,
            "jwt_authentication": True
        },
        "rate_limits": {
            "requests_per_window": Config.RATE_LIMIT_REQUESTS,
            "window_seconds": Config.RATE_LIMIT_WINDOW
        }
    }


@app.get("/providers")
async def get_providers():
    """List all verification providers by tier"""
    try:
        from verity_ultimate_verification import TRUST_WEIGHTS
        
        tiers = {
            "tier1_authoritative": [],
            "tier2_academic": [],
            "tier3_knowledge": [],
            "tier4_news": [],
            "tier5_search": [],
            "tier6_ai": []
        }
        
        for provider, weight in TRUST_WEIGHTS.items():
            if weight == 1.0:
                tiers["tier1_authoritative"].append({"name": provider, "weight": weight})
            elif weight >= 0.9:
                tiers["tier2_academic"].append({"name": provider, "weight": weight})
            elif weight >= 0.85:
                tiers["tier3_knowledge"].append({"name": provider, "weight": weight})
            elif weight >= 0.75:
                tiers["tier4_news"].append({"name": provider, "weight": weight})
            elif weight >= 0.7:
                tiers["tier5_search"].append({"name": provider, "weight": weight})
            else:
                tiers["tier6_ai"].append({"name": provider, "weight": weight})
        
        return tiers
        
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        return {"error": "Could not load providers"}


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server_production:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,  # Disabled to prevent restart loops
        workers=1,
        log_level=Config.LOG_LEVEL.lower(),
        access_log=True
    )
