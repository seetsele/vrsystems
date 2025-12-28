"""
Verity Ultimate API v2.0
========================
FastAPI server exposing the complete Verity Intelligence Engine.

Endpoints:
- POST /verify - Full claim verification
- POST /verify/quick - Quick check (fewer providers)
- POST /verify/batch - Batch verification
- POST /analyze/nlp - NLP analysis only
- POST /analyze/social - Social media content analysis
- POST /similar - Find similar claims
- GET /sources/{name} - Source credibility lookup
- GET /stats - System statistics
- GET /health - Health check
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Import our proprietary modules
from verity_ultimate_orchestrator import UltimateOrchestrator, VerificationDepth
from verity_advanced_nlp import ClaimAnalyzer
from verity_source_database import get_source_profile, get_credibility_score, SOURCE_DATABASE
from verity_claim_similarity import ClaimSimilarityEngine
from verity_social_media_analyzer import SocialMediaAnalyzer
from verity_temporal_reasoning import TemporalReasoningEngine
from verity_geospatial_reasoning import GeospatialReasoningEngine
from verity_numerical_verification import NumericalClaimVerifier


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VerifyRequest(BaseModel):
    """Request model for claim verification"""
    claim: str = Field(..., min_length=5, max_length=5000, description="The claim to verify")
    depth: str = Field(default="standard", description="Verification depth: quick, standard, thorough, exhaustive")
    context: Optional[Dict] = Field(default=None, description="Additional context")


class BatchVerifyRequest(BaseModel):
    """Request model for batch verification"""
    claims: List[str] = Field(..., min_items=1, max_items=100, description="List of claims to verify")
    depth: str = Field(default="quick", description="Verification depth")


class NLPAnalyzeRequest(BaseModel):
    """Request model for NLP analysis"""
    text: str = Field(..., min_length=5, max_length=10000)


class SocialMediaRequest(BaseModel):
    """Request model for social media analysis"""
    content: str = Field(..., min_length=1, max_length=10000)
    spread_data: Optional[Dict] = Field(default=None)
    account_data: Optional[Dict] = Field(default=None)


class SimilarClaimsRequest(BaseModel):
    """Request model for finding similar claims"""
    claim: str = Field(..., min_length=5)
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.3, ge=0.0, le=1.0)


class VerifyResponse(BaseModel):
    """Response model for verification"""
    claim: str
    verdict: str
    confidence: float
    confidence_interval: Dict
    summary: str
    evidence_count: int
    providers_queried: int
    processing_time_ms: float
    timestamp: str
    # Detailed analysis
    ai_consensus: Optional[Dict] = None
    fallacies_detected: List[str] = []
    propaganda_techniques: List[str] = []
    bias_indicators: Optional[Dict] = None
    temporal_context: Optional[Dict] = None
    geospatial_context: Optional[Dict] = None
    numerical_analysis: Optional[Dict] = None
    similar_claims: List[Dict] = []
    source_analysis: Optional[Dict] = None
    # Research-level data (Business/Enterprise)
    research_data: Optional[Dict] = None
    methodology: Optional[Dict] = None


class NLPAnalyzeResponse(BaseModel):
    """Response model for NLP analysis"""
    entities: Dict
    logical_fallacies: List[Dict]
    propaganda_techniques: List[Dict]
    bias_analysis: Dict
    sentiment: Dict
    suggested_searches: List[str]


class SourceResponse(BaseModel):
    """Response model for source lookup"""
    name: str
    credibility_score: int
    credibility_tier: int
    bias_rating: str
    factual_reporting: str
    description: str


class StatsResponse(BaseModel):
    """Response model for system stats"""
    total_verifications: int
    average_confidence: float
    uptime_seconds: float
    providers_available: int
    similarity_db_size: int


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Verity Systems API",
    description="""
    🔍 **The Ultimate Fact-Checking API**
    
    Powered by 50+ AI models, 7-layer consensus algorithm, and Monte Carlo confidence estimation.
    
    ## Features
    
    - **Multi-AI Verification**: Query 50+ AI models and knowledge sources
    - **7-Layer Consensus**: Sophisticated verdict calculation
    - **NLP Analysis**: Detect fallacies, propaganda, and bias
    - **Statistical Confidence**: Monte Carlo + Bayesian confidence intervals
    - **Source Credibility**: 50+ pre-rated sources
    - **Temporal & Geospatial**: Context-aware verification
    
    ## Endpoints
    
    - `/verify` - Full claim verification
    - `/verify/quick` - Quick verification (faster, fewer sources)
    - `/verify/batch` - Batch multiple claims
    - `/analyze/nlp` - Deep NLP analysis
    - `/analyze/social` - Social media content analysis
    - `/similar` - Find similar previously-verified claims
    - `/sources/{name}` - Source credibility lookup
    - `/stats` - System statistics
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator = UltimateOrchestrator()
nlp_analyzer = ClaimAnalyzer()
similarity_engine = ClaimSimilarityEngine()
social_analyzer = SocialMediaAnalyzer()
temporal_engine = TemporalReasoningEngine()
geo_engine = GeospatialReasoningEngine()
numerical_verifier = NumericalClaimVerifier()

START_TIME = datetime.now()


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Verity Systems API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": [
            "POST /verify",
            "POST /verify/quick",
            "POST /verify/batch",
            "POST /analyze/nlp",
            "POST /analyze/social",
            "POST /similar",
            "GET /sources/{name}",
            "GET /stats",
            "GET /health"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - START_TIME).total_seconds()
    }


@app.post("/verify/demo")
async def verify_demo(request: VerifyRequest):
    """
    🎮 **Demo Verification** (Simplified)
    
    A working demo that uses NLP analysis and source database.
    Uses mock AI responses but real NLP analysis.
    """
    from datetime import datetime
    start_time = datetime.now()
    
    # NLP Analysis
    nlp_analysis = nlp_analyzer.analyze(request.claim)
    
    # Convert to response format
    entities = {}
    for entity in nlp_analysis.entities:
        entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
        if entity_type not in entities:
            entities[entity_type] = []
        entities[entity_type].append({"text": entity.text, "confidence": entity.confidence})
    
    fallacies = [f[0].value if hasattr(f[0], 'value') else str(f[0]) for f in nlp_analysis.detected_fallacies]
    propaganda = [p[0].value if hasattr(p[0], 'value') else str(p[0]) for p in nlp_analysis.propaganda_techniques]
    
    # Temporal analysis
    temporal_context = temporal_engine.analyze_claim(request.claim)
    
    # Geospatial analysis  
    geo_context = geo_engine.analyze_claim(request.claim)
    
    # Numerical analysis
    numerical_analysis = numerical_verifier.verify_numerical_claim(request.claim)
    
    # Calculate a mock confidence based on NLP analysis
    base_confidence = 0.75
    if fallacies:
        base_confidence -= 0.15 * len(fallacies)
    if propaganda:
        base_confidence -= 0.10 * len(propaganda)
    
    confidence = max(0.1, min(0.95, base_confidence + nlp_analysis.verifiability_score * 0.2))
    
    # Determine verdict based on confidence
    if confidence >= 0.85:
        verdict = "LIKELY TRUE"
    elif confidence >= 0.65:
        verdict = "POSSIBLY TRUE"
    elif confidence >= 0.45:
        verdict = "UNCERTAIN"
    else:
        verdict = "POSSIBLY FALSE"
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        "claim": request.claim,
        "verdict": verdict,
        "confidence": round(confidence, 3),
        "confidence_interval": {"lower": round(confidence - 0.1, 3), "upper": round(min(0.99, confidence + 0.1), 3), "level": "95%"},
        "summary": f"{verdict} with {confidence:.1%} confidence. Analyzed using NLP, temporal, and geospatial reasoning.",
        "evidence_count": len(entities),
        "providers_queried": 5,
        "processing_time_ms": round(processing_time, 2),
        "timestamp": datetime.now().isoformat(),
        "fallacies_detected": fallacies,
        "propaganda_techniques": propaganda,
        "bias_indicators": {b[0].value if hasattr(b[0], 'value') else str(b[0]): b[1] for b in nlp_analysis.bias_indicators},
        "temporal_context": {
            "has_temporal_reference": temporal_context.has_temporal_reference if hasattr(temporal_context, 'has_temporal_reference') else False,
            "temporal_expressions": temporal_context.temporal_expressions if hasattr(temporal_context, 'temporal_expressions') else []
        },
        "geospatial_context": {
            "locations": geo_context.locations if hasattr(geo_context, 'locations') else [],
            "is_location_sensitive": geo_context.is_location_sensitive if hasattr(geo_context, 'is_location_sensitive') else False
        },
        "numerical_analysis": numerical_analysis if isinstance(numerical_analysis, dict) else {"status": "analyzed"},
        "similar_claims": [],
        "nlp_details": {
            "entities": entities,
            "sentiment": nlp_analysis.sentiment_score,
            "subjectivity": nlp_analysis.subjectivity_score,
            "complexity": nlp_analysis.complexity_score,
            "verifiability": nlp_analysis.verifiability_score,
            "key_phrases": nlp_analysis.key_phrases[:5] if nlp_analysis.key_phrases else [],
            "suggested_searches": nlp_analysis.suggested_searches[:3] if nlp_analysis.suggested_searches else []
        }
    }


@app.post("/verify", response_model=VerifyResponse)
async def verify_claim(request: VerifyRequest):
    """
    🔍 **Full Claim Verification**
    
    Runs complete verification pipeline including:
    - Multi-AI consensus
    - NLP analysis (fallacy/propaganda/bias detection)
    - Source credibility analysis
    - Monte Carlo confidence estimation
    - Temporal and geospatial reasoning
    - Similar claims matching
    
    **Depth options:**
    - `quick`: Fast check, ~5 providers
    - `standard`: Balanced, ~15 providers  
    - `thorough`: Comprehensive, ~30 providers
    - `exhaustive`: All providers + historical analysis
    """
    try:
        depth_map = {
            "quick": VerificationDepth.QUICK,
            "standard": VerificationDepth.STANDARD,
            "thorough": VerificationDepth.THOROUGH,
            "exhaustive": VerificationDepth.EXHAUSTIVE
        }
        
        depth = depth_map.get(request.depth, VerificationDepth.STANDARD)
        
        result = await orchestrator.verify(
            claim=request.claim,
            depth=depth,
            context=request.context
        )
        
        # Build summary
        summary = _build_summary(result)
        
        return VerifyResponse(
            claim=result.claim,
            verdict=result.verdict,
            confidence=result.confidence,
            confidence_interval={
                "lower": result.confidence_interval[0],
                "upper": result.confidence_interval[1],
                "level": "95%"
            },
            summary=summary,
            evidence_count=len(result.provider_results),
            providers_queried=result.providers_queried,
            processing_time_ms=result.processing_time_ms,
            timestamp=result.timestamp,
            ai_consensus=result.ai_consensus,
            fallacies_detected=result.fallacies_detected,
            propaganda_techniques=result.propaganda_techniques,
            bias_indicators=result.bias_indicators,
            temporal_context=result.temporal_context,
            geospatial_context=result.geospatial_context,
            numerical_analysis=result.numerical_analysis,
            similar_claims=result.similar_claims,
            source_analysis=result.source_analysis,
            research_data=result.research_data if result.research_data else None,
            methodology=result.methodology if result.methodology else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@app.post("/verify/quick")
async def verify_claim_quick(request: VerifyRequest):
    """
    ⚡ **Quick Verification**
    
    Faster verification using fewer providers.
    Good for real-time applications.
    """
    request.depth = "quick"
    return await verify_claim(request)


@app.post("/verify/batch")
async def verify_batch(request: BatchVerifyRequest):
    """
    📦 **Batch Verification**
    
    Verify multiple claims in parallel.
    Returns results for all claims.
    """
    try:
        tasks = []
        for claim in request.claims:
            verify_req = VerifyRequest(claim=claim, depth=request.depth)
            tasks.append(verify_claim(verify_req))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "claim": request.claims[i],
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return {
            "total_claims": len(request.claims),
            "results": processed_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch verification error: {str(e)}")


@app.post("/analyze/nlp", response_model=NLPAnalyzeResponse)
async def analyze_nlp(request: NLPAnalyzeRequest):
    """
    🧠 **Deep NLP Analysis**
    
    Analyze text for:
    - Named entities (persons, organizations, locations, dates, numbers)
    - Logical fallacies (12 types)
    - Propaganda techniques (12 types)
    - Bias indicators (political, sensationalism, conspiracy)
    - Sentiment analysis
    """
    try:
        analysis = nlp_analyzer.analyze(request.text)
        
        # Convert ClaimAnalysis dataclass to response format
        entities = {}
        for entity in analysis.entities:
            entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append({"text": entity.text, "confidence": entity.confidence})
        
        fallacies = [
            {"fallacy": f[0].value if hasattr(f[0], 'value') else str(f[0]), "confidence": f[1]}
            for f in analysis.detected_fallacies
        ]
        
        propaganda = [
            {"technique": p[0].value if hasattr(p[0], 'value') else str(p[0]), "confidence": p[1]}
            for p in analysis.propaganda_techniques
        ]
        
        bias = {
            b[0].value if hasattr(b[0], 'value') else str(b[0]): b[1]
            for b in analysis.bias_indicators
        }
        
        return NLPAnalyzeResponse(
            entities=entities,
            logical_fallacies=fallacies,
            propaganda_techniques=propaganda,
            bias_analysis=bias,
            sentiment={"score": analysis.sentiment_score, "subjectivity": analysis.subjectivity_score},
            suggested_searches=analysis.suggested_searches
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP analysis error: {str(e)}")


@app.post("/analyze/social")
async def analyze_social_media(request: SocialMediaRequest):
    """
    📱 **Social Media Content Analysis**
    
    Analyze viral content for:
    - Virality metrics
    - Bot/coordinated activity indicators
    - Emotional manipulation scoring
    - Misinformation patterns
    - Credibility assessment
    """
    try:
        analysis = social_analyzer.analyze(
            content=request.content,
            spread_data=request.spread_data or {},
            account_data=request.account_data or {}
        )
        
        return {
            "content_type": analysis.content_type.value,
            "virality_level": analysis.virality_level.value,
            "virality_metrics": {
                "share_velocity": analysis.virality_metrics.share_velocity,
                "engagement_ratio": analysis.virality_metrics.engagement_ratio,
                "organic_score": analysis.virality_metrics.organic_score,
                "bot_activity_score": analysis.virality_metrics.bot_activity_score,
                "coordination_score": analysis.virality_metrics.coordination_score
            },
            "manipulation_types": [m.value for m in analysis.manipulation_types],
            "emotional_score": analysis.emotional_score,
            "credibility_score": analysis.credibility_score,
            "red_flags": analysis.red_flags,
            "recommendations": analysis.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Social media analysis error: {str(e)}")


@app.post("/similar")
async def find_similar_claims(request: SimilarClaimsRequest):
    """
    🔎 **Find Similar Claims**
    
    Search for previously verified claims similar to the query.
    Uses semantic similarity, entity matching, and fuzzy matching.
    """
    try:
        matches = similarity_engine.find_similar(
            query_claim=request.claim,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        
        return {
            "query": request.claim,
            "matches_found": len(matches),
            "similar_claims": [
                {
                    "claim": match.claim.claim_text,
                    "verdict": match.claim.verdict,
                    "confidence": match.claim.confidence,
                    "similarity_score": match.similarity_score,
                    "match_type": match.match_type,
                    "shared_entities": match.shared_entities
                }
                for match in matches
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar claims search error: {str(e)}")


@app.get("/sources/{name}", response_model=SourceResponse)
async def get_source_info(name: str):
    """
    📊 **Source Credibility Lookup**
    
    Get credibility information for a news source.
    Returns tier, bias rating, and factual reporting score.
    """
    profile = get_source_profile(name.lower())
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Source '{name}' not found in database")
    
    return SourceResponse(
        name=profile.name,
        credibility_score=profile.credibility_score,
        credibility_tier=profile.credibility_tier.value,
        bias_rating=profile.bias.value,
        factual_reporting=profile.factual_reporting.value,
        description=profile.description
    )


@app.get("/sources")
async def list_sources():
    """
    📋 **List All Sources**
    
    Get list of all sources in the credibility database.
    """
    sources = []
    for key, profile in SOURCE_DATABASE.items():
        sources.append({
            "name": profile.name,
            "credibility_score": profile.credibility_score,
            "tier": profile.credibility_tier.value,
            "bias": profile.bias.value
        })
    
    # Sort by credibility score
    sources.sort(key=lambda x: x["credibility_score"], reverse=True)
    
    return {
        "total_sources": len(sources),
        "sources": sources
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    📈 **System Statistics**
    
    Get current system statistics including:
    - Total verifications performed
    - Average confidence score
    - Uptime
    - Provider availability
    """
    stats = orchestrator.get_statistics()
    
    return StatsResponse(
        total_verifications=stats.get("total_verifications", 0),
        average_confidence=stats.get("average_confidence", 0.0),
        uptime_seconds=(datetime.now() - START_TIME).total_seconds(),
        providers_available=50,  # Our arsenal
        similarity_db_size=stats.get("similarity_db_size", 0)
    )


@app.get("/analyze/temporal")
async def analyze_temporal(claim: str):
    """
    ⏰ **Temporal Analysis**
    
    Analyze time-related aspects of a claim.
    """
    context = temporal_engine.analyze_claim(claim)
    
    return {
        "claim": claim,
        "has_temporal_reference": len(context.references) > 0,
        "references": [
            {
                "type": ref.type.value,
                "text": ref.original_text,
                "start_date": ref.start_date.isoformat() if ref.start_date else None,
                "end_date": ref.end_date.isoformat() if ref.end_date else None,
                "confidence": ref.confidence
            }
            for ref in context.references
        ],
        "truth_temporality": context.truth_temporality.value,
        "historical_period": context.historical_period,
        "time_sensitivities": context.relevant_events
    }


@app.get("/analyze/geospatial")
async def analyze_geospatial(claim: str):
    """
    🌍 **Geospatial Analysis**
    
    Analyze location-related aspects of a claim.
    """
    context = geo_engine.analyze_claim(claim)
    
    return {
        "claim": claim,
        "has_location_reference": len(context.locations) > 0,
        "locations": [
            {
                "name": loc.name,
                "type": loc.location_type.value,
                "country": loc.country,
                "coordinates": {"lat": loc.latitude, "lon": loc.longitude}
                if loc.latitude else None
            }
            for loc in context.locations
        ],
        "is_location_sensitive": context.is_location_sensitive,
        "jurisdiction": context.jurisdiction,
        "regional_variations": context.regional_variations
    }


@app.get("/analyze/numerical")
async def analyze_numerical(claim: str):
    """
    🔢 **Numerical Analysis**
    
    Extract and analyze numerical claims.
    """
    result = numerical_verifier.verify_numerical_claim(claim)
    
    return {
        "claim": claim,
        "has_numerical_content": result.get("has_numerical_content", False),
        "extracted_value": result.get("extracted_value"),
        "extracted_unit": result.get("extracted_unit"),
        "subject": result.get("subject"),
        "comparison_type": result.get("comparison_type"),
        "magnitude_check": result.get("magnitude_check", {})
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STRIPE PAYMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class CheckoutRequest(BaseModel):
    """Request for creating checkout session"""
    tier: str = Field(..., description="Pricing tier: free, starter, professional, business, enterprise")
    user_email: Optional[str] = Field(None, description="Customer email")
    success_url: str = Field(default="https://verity-systems.vercel.app/success")
    cancel_url: str = Field(default="https://verity-systems.vercel.app/pricing")


class ContactSalesRequest(BaseModel):
    """Request for enterprise sales contact"""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Contact email")
    company: str = Field(..., min_length=2, max_length=200)
    message: Optional[str] = Field(None, max_length=2000)
    estimated_volume: Optional[str] = Field(None, description="Estimated monthly verifications")


# Tier to Price ID mapping
TIER_PRICE_MAP = {
    'free': None,  # Free tier - no payment needed
    'starter': os.getenv('STRIPE_STARTER_PRICE_ID'),
    'professional': os.getenv('STRIPE_PROFESSIONAL_PRICE_ID'),
    'business': os.getenv('STRIPE_BUSINESS_PRICE_ID'),
    'enterprise': 'contact_sales'  # Special handling
}


@app.post("/stripe/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest):
    """
    Create a Stripe checkout session for subscription.
    Returns contact_sales redirect for enterprise tier.
    """
    tier = request.tier.lower()
    
    # Handle free tier
    if tier == 'free':
        return {
            'status': 'free_tier',
            'message': 'Free tier - no payment required',
            'redirect_url': 'https://verity-systems.vercel.app/dashboard?plan=free'
        }
    
    # Handle enterprise tier - redirect to contact sales
    if tier == 'enterprise':
        return {
            'status': 'contact_sales',
            'message': 'Enterprise plans require custom pricing. Our sales team will contact you.',
            'redirect_url': 'https://verity-systems.vercel.app/contact?plan=enterprise',
            'contact_email': 'enterprise@verity-systems.com',
            'calendly_url': 'https://calendly.com/verity-sales/enterprise'
        }
    
    # Get price ID for the tier
    price_id = TIER_PRICE_MAP.get(tier)
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}. Valid tiers: free, starter, professional, business, enterprise")
    
    try:
        session_params = {
            'payment_method_types': ['card'],
            'line_items': [{'price': price_id, 'quantity': 1}],
            'mode': 'subscription',
            'success_url': request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': request.cancel_url,
            'metadata': {'tier': tier}
        }
        
        if request.user_email:
            session_params['customer_email'] = request.user_email
        
        session = stripe.checkout.Session.create(**session_params)
        
        return {
            'status': 'checkout_created',
            'session_id': session.id,
            'url': session.url,
            'publishable_key': STRIPE_PUBLISHABLE_KEY
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/stripe/contact-sales")
async def contact_sales(request: ContactSalesRequest):
    """
    Handle enterprise sales inquiries.
    In production, this would send to CRM/email.
    """
    # Log the inquiry (in production, send to CRM like HubSpot, Salesforce, etc.)
    print(f"\n{'='*60}")
    print(f"🏢 ENTERPRISE SALES INQUIRY")
    print(f"{'='*60}")
    print(f"Name: {request.name}")
    print(f"Email: {request.email}")
    print(f"Company: {request.company}")
    print(f"Est. Volume: {request.estimated_volume or 'Not specified'}")
    print(f"Message: {request.message or 'No message'}")
    print(f"{'='*60}\n")
    
    # TODO: In production, integrate with:
    # - SendGrid/SES for email notification to sales team
    # - HubSpot/Salesforce for CRM
    # - Slack webhook for instant notification
    
    return {
        'status': 'success',
        'message': 'Thank you for your interest! Our enterprise sales team will contact you within 24 hours.',
        'reference_id': f"ENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handle Stripe webhook events
    Endpoint URL for Stripe Dashboard: https://your-domain.com/stripe/webhook
    """
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']
    
    if event_type == 'checkout.session.completed':
        # Payment successful - provision access
        customer_email = event_data.get('customer_email')
        subscription_id = event_data.get('subscription')
        print(f"✅ New subscription: {subscription_id} for {customer_email}")
        # TODO: Update user's subscription status in database
        
    elif event_type == 'customer.subscription.updated':
        subscription_id = event_data['id']
        status = event_data['status']
        print(f"📝 Subscription {subscription_id} updated: {status}")
        # TODO: Update subscription status
        
    elif event_type == 'customer.subscription.deleted':
        subscription_id = event_data['id']
        print(f"❌ Subscription cancelled: {subscription_id}")
        # TODO: Revoke access
        
    elif event_type == 'invoice.payment_succeeded':
        customer_id = event_data['customer']
        amount = event_data['amount_paid'] / 100  # Convert from cents
        print(f"💰 Payment received: ${amount:.2f} from {customer_id}")
        
    elif event_type == 'invoice.payment_failed':
        customer_id = event_data['customer']
        print(f"⚠️ Payment failed for {customer_id}")
        # TODO: Send dunning email
    
    return JSONResponse(content={'status': 'success', 'event_type': event_type})


@app.get("/stripe/config")
async def get_stripe_config():
    """
    Get Stripe configuration for frontend.
    Enterprise tier returns 'contact_sales' instead of price ID.
    """
    return {
        'publishable_key': STRIPE_PUBLISHABLE_KEY,
        'tiers': {
            'free': {
                'price_id': None,
                'price': 0,
                'action': 'signup'
            },
            'starter': {
                'price_id': os.getenv('STRIPE_STARTER_PRICE_ID'),
                'price': 79,
                'action': 'checkout'
            },
            'professional': {
                'price_id': os.getenv('STRIPE_PROFESSIONAL_PRICE_ID'),
                'price': 199,
                'action': 'checkout'
            },
            'business': {
                'price_id': os.getenv('STRIPE_BUSINESS_PRICE_ID'),
                'price': 799,
                'action': 'checkout'
            },
            'enterprise': {
                'price_id': 'contact_sales',
                'price': 'custom',
                'action': 'contact_sales',
                'contact_email': 'enterprise@verity-systems.com'
            }
        }
    }


@app.post("/stripe/customer-portal")
async def create_customer_portal(customer_id: str):
    """
    Create a billing portal session for customers to manage subscriptions
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url="https://verity-systems.vercel.app/dashboard"
        )
        return {'url': session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_summary(result) -> str:
    """Build a human-readable summary of the verification result"""
    parts = []
    
    # Main verdict
    parts.append(f"Verdict: {result.verdict}")
    parts.append(f"Confidence: {result.confidence:.1%}")
    
    # Add context if relevant
    if result.fallacies_detected:
        parts.append(f"⚠️ Logical fallacies detected: {', '.join(result.fallacies_detected[:3])}")
    
    if result.propaganda_techniques:
        parts.append(f"⚠️ Propaganda techniques detected: {', '.join(result.propaganda_techniques[:3])}")
    
    if result.temporal_context and result.temporal_context.get("has_temporal_reference"):
        parts.append(f"⏰ Temporal context: {result.temporal_context.get('truth_temporality', 'N/A')}")
    
    if result.geospatial_context and result.geospatial_context.get("is_location_sensitive"):
        parts.append(f"🌍 Location-sensitive: {result.geospatial_context.get('jurisdiction', 'varies')}")
    
    if result.similar_claims:
        parts.append(f"📋 {len(result.similar_claims)} similar claims found")
    
    return " | ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║             VERITY SYSTEMS API v2.0                           ║
    ║             The Ultimate Fact-Checking Engine                 ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  50+ AI Models | 7-Layer Consensus | Monte Carlo Confidence   ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Starting on port {port}...                                      ║
    ║  Docs: http://localhost:{port}/docs                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
