"""
VERITY TIERED VERIFICATION SYSTEM
=================================
LangChain-powered verification with tier-based model access.

This module integrates:
- ALL AI models (commercial, specialized, free)
- Tier-based access control
- LangChain orchestration
- Multi-platform support (web, desktop, mobile, browser extension)
"""

from __future__ import annotations
import os
import sys
import asyncio
import time
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Ensure paths
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment
from dotenv import load_dotenv
load_dotenv(ROOT / "python-tools" / ".env")

# ============================================================
# TIER CONFIGURATION
# ============================================================

class TierName(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    PROFESSIONAL = "professional"
    AGENCY = "agency"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


@dataclass
class TierModelAccess:
    """Models available for each tier"""
    tier: TierName
    max_models: int
    ensemble_voting: int
    commercial_models: List[str]
    specialized_models: List[str]
    free_providers: List[str]
    max_verifications_per_month: int
    verification_speed: str  # standard, priority, premium, dedicated
    features: Dict[str, bool] = field(default_factory=dict)


# ============================================================
# TIER DEFINITIONS
# ============================================================

TIER_MODEL_ACCESS = {
    TierName.FREE: TierModelAccess(
        tier=TierName.FREE,
        max_models=1,
        ensemble_voting=1,
        commercial_models=[],  # No commercial models
        specialized_models=[],  # No specialized models
        free_providers=["wikipedia"],  # Only Wikipedia
        max_verifications_per_month=50,
        verification_speed="standard",
        features={
            "batch_processing": False,
            "api_access": False,
            "real_time_search": False,
            "academic_sources": False,
        }
    ),
    TierName.STARTER: TierModelAccess(
        tier=TierName.STARTER,
        max_models=3,
        ensemble_voting=1,
        commercial_models=["groq_llama33_70b"],  # 1 free commercial
        specialized_models=["biogpt", "finbert", "legalbert"],  # 3 specialized
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=500,
        verification_speed="standard",
        features={
            "batch_processing": True,
            "api_access": False,
            "real_time_search": False,
            "academic_sources": True,
        }
    ),
    TierName.PRO: TierModelAccess(
        tier=TierName.PRO,
        max_models=5,
        ensemble_voting=3,
        commercial_models=["groq_llama33_70b", "groq_mixtral_8x7b", "perplexity_sonar"],
        specialized_models=["biogpt", "pubmedbert", "finbert", "legalbert", "scibert", "polibert"],
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=2500,
        verification_speed="priority",
        features={
            "batch_processing": True,
            "api_access": False,
            "real_time_search": True,
            "academic_sources": True,
            "fact_checker_sources": True,
        }
    ),
    TierName.PROFESSIONAL: TierModelAccess(
        tier=TierName.PROFESSIONAL,
        max_models=8,
        ensemble_voting=5,
        commercial_models=[
            "groq_llama33_70b", "groq_mixtral_8x7b", "groq_deepseek_r1",
            "perplexity_sonar", "openai_gpt4o_mini"
        ],
        specialized_models=[
            "biogpt", "pubmedbert", "biobert", "finbert", "fingpt",
            "legalbert", "scibert", "climatebert", "polibert", "geobert"
        ],
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=7500,
        verification_speed="priority",
        features={
            "batch_processing": True,
            "api_access": True,
            "real_time_search": True,
            "academic_sources": True,
            "fact_checker_sources": True,
            "government_sources": True,
        }
    ),
    TierName.AGENCY: TierModelAccess(
        tier=TierName.AGENCY,
        max_models=12,
        ensemble_voting=10,
        commercial_models=[
            "groq_llama33_70b", "groq_mixtral_8x7b", "groq_deepseek_r1",
            "perplexity_sonar", "perplexity_sonar_pro",
            "openai_gpt4o_mini", "openai_gpt4o",
            "cohere_command_r", "together_llama3_70b"
        ],
        specialized_models=[
            "biogpt", "pubmedbert", "biobert", "nutritionbert",
            "finbert", "fingpt", "econbert",
            "legalbert", "caselawbert",
            "scibert", "galactica", "climatebert",
            "polibert", "sportsbert", "geobert", "historybert", "techbert"
        ],
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=20000,
        verification_speed="premium",
        features={
            "batch_processing": True,
            "api_access": True,
            "real_time_search": True,
            "academic_sources": True,
            "fact_checker_sources": True,
            "government_sources": True,
            "unlimited_sources": True,
        }
    ),
    TierName.BUSINESS: TierModelAccess(
        tier=TierName.BUSINESS,
        max_models=15,
        ensemble_voting=15,
        commercial_models=[
            "groq_llama33_70b", "groq_mixtral_8x7b", "groq_deepseek_r1",
            "perplexity_sonar", "perplexity_sonar_pro",
            "openai_gpt4o_mini", "openai_gpt4o", "openai_o1_mini",
            "anthropic_claude_sonnet_4", "anthropic_claude_haiku",
            "google_gemini_flash", "google_gemini_pro",
            "cohere_command_r", "cohere_command_r_plus",
            "together_llama3_70b", "together_mixtral"
        ],
        specialized_models=[
            "biogpt", "pubmedbert", "biobert", "nutritionbert",
            "finbert", "fingpt", "econbert",
            "legalbert", "caselawbert",
            "scibert", "galactica", "climatebert",
            "polibert", "votebert", "sportsbert",
            "geobert", "historybert", "techbert", "securitybert"
        ],
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=50000,
        verification_speed="premium",
        features={
            "batch_processing": True,
            "api_access": True,
            "api_streaming": True,
            "real_time_search": True,
            "academic_sources": True,
            "fact_checker_sources": True,
            "government_sources": True,
            "unlimited_sources": True,
            "deepfake_detection": True,
            "automated_monitoring": True,
        }
    ),
    TierName.ENTERPRISE: TierModelAccess(
        tier=TierName.ENTERPRISE,
        max_models=999,  # Unlimited
        ensemble_voting=50,
        commercial_models=[
            # ALL commercial models
            "groq_llama33_70b", "groq_mixtral_8x7b", "groq_deepseek_r1",
            "perplexity_sonar", "perplexity_sonar_pro",
            "openai_gpt4o_mini", "openai_gpt4o", "openai_gpt35_turbo", "openai_o1", "openai_o1_mini",
            "anthropic_claude_opus_4", "anthropic_claude_sonnet_4", "anthropic_claude_haiku",
            "google_gemini_flash", "google_gemini_pro", "google_gemini_ultra",
            "cohere_command_r", "cohere_command_r_plus", "cohere_command",
            "together_llama3_70b", "together_mixtral", "together_default",
            "ollama_llama33_70b", "ollama_qwen25_72b", "ollama_mistral_large"
        ],
        specialized_models=[
            # ALL specialized models
            "biogpt", "pubmedbert", "biobert", "nutritionbert",
            "finbert", "fingpt", "econbert",
            "legalbert", "caselawbert",
            "scibert", "galactica", "climatebert",
            "polibert", "votebert", "sportsbert",
            "geobert", "historybert", "techbert", "securitybert"
        ],
        free_providers=["wikipedia", "arxiv", "pubmed", "free_providers"],
        max_verifications_per_month=999999,  # Unlimited
        verification_speed="dedicated",
        features={
            "batch_processing": True,
            "api_access": True,
            "api_streaming": True,
            "api_unlimited": True,
            "real_time_search": True,
            "academic_sources": True,
            "fact_checker_sources": True,
            "government_sources": True,
            "unlimited_sources": True,
            "deepfake_detection": True,
            "automated_monitoring": True,
            "custom_model_training": True,
            "white_label": True,
            "dedicated_infrastructure": True,
        }
    ),
}


# ============================================================
# TIER HELPER FUNCTIONS
# ============================================================

def get_tier_info(tier: TierName) -> Dict[str, Any]:
    """
    Get detailed information about a subscription tier.
    Returns all tier capabilities and limits.
    """
    access = TIER_MODEL_ACCESS.get(tier)
    if not access:
        return {"error": f"Tier {tier} not found"}
    
    return {
        "name": tier.value,
        "max_models": access.max_models,
        "ensemble_voting": access.ensemble_voting,
        "commercial_models": access.commercial_models,
        "commercial_models_count": len(access.commercial_models),
        "specialized_models": access.specialized_models,
        "specialized_models_count": len(access.specialized_models),
        "free_providers": access.free_providers,
        "max_verifications": access.max_verifications_per_month,
        "verification_speed": access.verification_speed,
        "features": access.features,
        "total_models": (
            len(access.commercial_models) + 
            len(access.specialized_models) + 
            len(access.free_providers)
        ),
    }


def get_tier_model_list(tier: TierName) -> Dict[str, List[str]]:
    """Get all models available for a given tier."""
    access = TIER_MODEL_ACCESS.get(tier)
    if not access:
        return {"commercial": [], "specialized": [], "free": []}
    
    return {
        "commercial": access.commercial_models,
        "specialized": access.specialized_models,
        "free": access.free_providers
    }


def check_tier_model_access(tier: TierName, model_name: str) -> bool:
    """Check if a given model is accessible for a tier."""
    access = TIER_MODEL_ACCESS.get(tier)
    if not access:
        return False
    
    all_allowed = (
        access.commercial_models + 
        access.specialized_models + 
        access.free_providers
    )
    return model_name.lower() in [m.lower() for m in all_allowed]


def get_tier_from_string(tier_str: str) -> TierName:
    """Convert string to TierName enum with fallback to FREE."""
    try:
        return TierName(tier_str.lower())
    except ValueError:
        return TierName.FREE


# ============================================================
# LANGCHAIN IMPORTS
# ============================================================

LANGCHAIN_AVAILABLE = False
try:
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.prompts import PromptTemplate, ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
        from langchain_core.runnables import RunnableParallel, RunnablePassthrough
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        pass

try:
    from langchain_openai import ChatOpenAI
    OPENAI_LANGCHAIN = True
except ImportError:
    OPENAI_LANGCHAIN = False

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_LANGCHAIN = True
except ImportError:
    ANTHROPIC_LANGCHAIN = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_LANGCHAIN = True
except ImportError:
    GOOGLE_LANGCHAIN = False

try:
    from langchain_groq import ChatGroq
    GROQ_LANGCHAIN = True
except ImportError:
    GROQ_LANGCHAIN = False


# ============================================================
# MODEL REGISTRY IMPORTS
# ============================================================

try:
    from providers.ai_models.all_models import (
        ALL_AI_MODELS,
        get_all_model_names,
        get_commercial_model_names,
        get_specialized_model_names,
        get_free_model_names,
        get_models_for_domain,
        DOMAIN_MODEL_MAPPING
    )
    ALL_MODELS_AVAILABLE = True
except ImportError:
    ALL_MODELS_AVAILABLE = False
    ALL_AI_MODELS = {}

try:
    from providers.ai_models.specialized_models import SPECIALIZED_MODELS
    SPECIALIZED_AVAILABLE = True
except ImportError:
    SPECIALIZED_AVAILABLE = False
    SPECIALIZED_MODELS = {}


# ============================================================
# VERIFICATION RESULT
# ============================================================

@dataclass
class TieredVerificationResult:
    """Result from tiered verification system"""
    request_id: str
    claim: str
    verdict: str
    confidence: float
    veriscore: float
    reasoning: str
    
    # Tier info
    tier: str
    models_used: List[str]
    models_allowed: int
    
    # Details
    domain_detected: str
    domain_confidence: float
    individual_results: List[Dict]
    sources: List[str]
    evidence: Dict[str, Any]
    
    # Metadata
    processing_time_ms: int
    timestamp: str
    cost_estimate: float
    
    # Platform
    platform: str  # web, desktop, mobile, browser_extension, api


# ============================================================
# LANGCHAIN VERIFICATION CHAINS
# ============================================================

class TieredLangChainVerifier:
    """LangChain-based verification with tier awareness"""
    
    def __init__(self, tier: TierName = TierName.FREE):
        self.tier = tier
        self.tier_access = TIER_MODEL_ACCESS.get(tier, TIER_MODEL_ACCESS[TierName.FREE])
        self._llms = {}
        self._chains = {}
        self._init_langchain()
    
    def _init_langchain(self):
        """Initialize LangChain models based on tier"""
        if not LANGCHAIN_AVAILABLE:
            return
        
        # Initialize available LLMs based on tier
        if GROQ_LANGCHAIN and os.getenv("GROQ_API_KEY"):
            if "groq_llama33_70b" in self.tier_access.commercial_models:
                self._llms["groq"] = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    api_key=os.getenv("GROQ_API_KEY")
                )
        
        if OPENAI_LANGCHAIN and os.getenv("OPENAI_API_KEY"):
            if any("openai" in m for m in self.tier_access.commercial_models):
                model = "gpt-4o-mini" if "openai_gpt4o_mini" in self.tier_access.commercial_models else "gpt-3.5-turbo"
                if "openai_gpt4o" in self.tier_access.commercial_models:
                    model = "gpt-4o"
                self._llms["openai"] = ChatOpenAI(
                    model=model,
                    temperature=0,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
        
        if ANTHROPIC_LANGCHAIN and os.getenv("ANTHROPIC_API_KEY"):
            if any("anthropic" in m for m in self.tier_access.commercial_models):
                model = "claude-3-5-haiku-20241022"
                if "anthropic_claude_sonnet_4" in self.tier_access.commercial_models:
                    model = "claude-sonnet-4-20250514"
                if "anthropic_claude_opus_4" in self.tier_access.commercial_models:
                    model = "claude-opus-4-20250514"
                self._llms["anthropic"] = ChatAnthropic(
                    model=model,
                    temperature=0,
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
        
        if GOOGLE_LANGCHAIN and os.getenv("GOOGLE_AI_API_KEY"):
            if any("google" in m for m in self.tier_access.commercial_models):
                self._llms["google"] = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0,
                    google_api_key=os.getenv("GOOGLE_AI_API_KEY")
                )
        
        # Create verification chain
        self._create_chains()
    
    def _create_chains(self):
        """Create LangChain verification chains"""
        if not self._llms:
            return
        
        # Primary verification prompt
        verify_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a fact-checking expert. Analyze claims carefully and provide structured verification results.

Your response must be valid JSON with this exact structure:
{{
    "verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIABLE" | "MIXED",
    "confidence": 0-100,
    "reasoning": "Your detailed analysis",
    "key_evidence": ["evidence1", "evidence2"],
    "sources_needed": ["source1", "source2"]
}}"""),
            ("human", "Verify this claim: {claim}\n\nContext: {context}")
        ])
        
        # Domain detection prompt
        domain_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the claim and detect its primary domain.

Domains: medical, legal, financial, scientific, climate, technology, politics, sports, geography, history, general

Your response must be valid JSON:
{{
    "primary_domain": "domain_name",
    "confidence": 0-100,
    "secondary_domains": ["domain1", "domain2"],
    "keywords_detected": ["keyword1", "keyword2"]
}}"""),
            ("human", "Claim: {claim}")
        ])
        
        # Synthesis prompt for combining results
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are synthesizing multiple verification results into a final verdict.

Consider:
- Agreement between models
- Confidence levels
- Quality of evidence
- Domain expertise relevance

Your response must be valid JSON:
{{
    "final_verdict": "TRUE" | "FALSE" | "MISLEADING" | "UNVERIFIABLE" | "MIXED",
    "final_confidence": 0-100,
    "synthesis_reasoning": "Why this verdict",
    "agreement_analysis": "How models agreed/disagreed",
    "recommended_sources": ["source1", "source2"]
}}"""),
            ("human", "Claim: {claim}\n\nIndividual Results:\n{results}")
        ])
        
        # Create chains for each available LLM
        for name, llm in self._llms.items():
            self._chains[f"{name}_verify"] = verify_prompt | llm | StrOutputParser()
            self._chains[f"{name}_domain"] = domain_prompt | llm | StrOutputParser()
            self._chains[f"{name}_synthesis"] = synthesis_prompt | llm | StrOutputParser()
    
    async def detect_domain(self, claim: str) -> Dict[str, Any]:
        """Detect claim domain using LangChain"""
        if not self._chains:
            return self._fallback_domain_detection(claim)
        
        # Use first available chain
        chain_name = next((k for k in self._chains if k.endswith("_domain")), None)
        if not chain_name:
            return self._fallback_domain_detection(claim)
        
        try:
            result = await self._chains[chain_name].ainvoke({"claim": claim})
            return self._parse_json_response(result)
        except Exception as e:
            print(f"[WARN] LangChain domain detection failed: {e}")
            return self._fallback_domain_detection(claim)
    
    def _fallback_domain_detection(self, claim: str) -> Dict[str, Any]:
        """Fallback keyword-based domain detection"""
        claim_lower = claim.lower()
        
        domain_keywords = {
            "medical": ["disease", "symptom", "treatment", "drug", "health", "patient", "vaccine"],
            "legal": ["law", "court", "judge", "legal", "lawsuit", "statute"],
            "financial": ["stock", "market", "investment", "bank", "economy", "gdp"],
            "scientific": ["research", "study", "experiment", "hypothesis", "data"],
            "climate": ["climate", "warming", "carbon", "emissions", "temperature"],
            "technology": ["software", "algorithm", "cybersecurity", "data", "ai"],
            "politics": ["president", "election", "congress", "government", "vote"],
            "sports": ["game", "match", "championship", "player", "team"],
            "geography": ["country", "city", "population", "border", "continent"],
            "history": ["history", "century", "war", "ancient", "revolution"],
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in claim_lower)
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return {"primary_domain": "general", "confidence": 50}
        
        best = max(scores.items(), key=lambda x: x[1])
        return {
            "primary_domain": best[0],
            "confidence": min(95, 50 + best[1] * 15),
            "keywords_detected": [kw for kw in domain_keywords[best[0]] if kw in claim_lower]
        }
    
    async def verify_with_langchain(
        self,
        claim: str,
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """Run verification using all available LangChain models"""
        results = []
        
        for chain_name, chain in self._chains.items():
            if not chain_name.endswith("_verify"):
                continue
            
            provider = chain_name.replace("_verify", "")
            try:
                start = time.time()
                response = await chain.ainvoke({"claim": claim, "context": context})
                elapsed = time.time() - start
                
                parsed = self._parse_json_response(response)
                parsed["provider"] = provider
                parsed["response_time_ms"] = int(elapsed * 1000)
                results.append(parsed)
                
            except Exception as e:
                print(f"[WARN] LangChain verification failed for {provider}: {e}")
                results.append({
                    "provider": provider,
                    "verdict": "ERROR",
                    "confidence": 0,
                    "reasoning": str(e)
                })
        
        return results
    
    async def synthesize_results(
        self,
        claim: str,
        results: List[Dict]
    ) -> Dict[str, Any]:
        """Synthesize multiple results into final verdict"""
        if not self._chains:
            return self._fallback_synthesis(results)
        
        chain_name = next((k for k in self._chains if k.endswith("_synthesis")), None)
        if not chain_name:
            return self._fallback_synthesis(results)
        
        try:
            results_str = json.dumps(results, indent=2)
            response = await self._chains[chain_name].ainvoke({
                "claim": claim,
                "results": results_str
            })
            return self._parse_json_response(response)
        except Exception as e:
            print(f"[WARN] LangChain synthesis failed: {e}")
            return self._fallback_synthesis(results)
    
    def _fallback_synthesis(self, results: List[Dict]) -> Dict[str, Any]:
        """Fallback synthesis without LangChain"""
        if not results:
            return {"final_verdict": "UNVERIFIABLE", "final_confidence": 0}
        
        verdicts = [r.get("verdict", "UNVERIFIABLE") for r in results if r.get("verdict") != "ERROR"]
        confidences = [r.get("confidence", 0) for r in results if r.get("confidence", 0) > 0]
        
        if not verdicts:
            return {"final_verdict": "UNVERIFIABLE", "final_confidence": 0}
        
        # Majority vote
        from collections import Counter
        vote = Counter(verdicts).most_common(1)[0]
        
        avg_conf = sum(confidences) / len(confidences) if confidences else 50
        
        # Agreement bonus
        agreement = vote[1] / len(verdicts)
        if agreement >= 0.8:
            avg_conf = min(95, avg_conf * 1.1)
        
        return {
            "final_verdict": vote[0],
            "final_confidence": round(avg_conf, 2),
            "agreement_percentage": round(agreement * 100, 2),
            "models_agreed": vote[1],
            "total_models": len(verdicts)
        }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Safely parse JSON from LLM response"""
        try:
            # Try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return {"raw_response": response, "parse_error": True}


# ============================================================
# MAIN TIERED VERIFICATION ORCHESTRATOR
# ============================================================

class TieredVerificationOrchestrator:
    """
    Main orchestrator for tiered verification across all platforms.
    
    Integrates:
    - LangChain for AI orchestration
    - Tier-based model access
    - All AI models (commercial, specialized, free)
    - Multi-platform support
    """
    
    def __init__(
        self,
        tier: TierName = TierName.FREE,
        platform: str = "web"
    ):
        self.tier = tier
        self.tier_access = TIER_MODEL_ACCESS.get(tier, TIER_MODEL_ACCESS[TierName.FREE])
        self.platform = platform
        
        # Initialize LangChain verifier
        self.langchain_verifier = TieredLangChainVerifier(tier)
        
        # Usage tracking
        self.verifications_this_month = 0
        self.total_cost = 0.0
    
    def get_allowed_models(self) -> Dict[str, List[str]]:
        """Get models allowed for current tier"""
        return {
            "commercial": self.tier_access.commercial_models,
            "specialized": self.tier_access.specialized_models,
            "free": self.tier_access.free_providers,
            "max_total": self.tier_access.max_models,
            "ensemble_voting": self.tier_access.ensemble_voting
        }
    
    def check_usage_limit(self) -> Dict[str, Any]:
        """Check if user is within usage limits"""
        remaining = self.tier_access.max_verifications_per_month - self.verifications_this_month
        return {
            "within_limit": remaining > 0,
            "remaining": remaining,
            "total_allowed": self.tier_access.max_verifications_per_month,
            "used": self.verifications_this_month
        }
    
    async def verify(
        self,
        claim: str,
        context: str = "",
        force_models: Optional[List[str]] = None,
        include_free_providers: bool = True
    ) -> TieredVerificationResult:
        """
        Main verification method with tier-based access control.
        """
        start_time = time.time()
        request_id = f"ver_{self.tier.value}_{int(time.time())}_{hashlib.md5(claim.encode()).hexdigest()[:8]}"
        
        # Check usage limit
        usage = self.check_usage_limit()
        if not usage["within_limit"]:
            return TieredVerificationResult(
                request_id=request_id,
                claim=claim,
                verdict="LIMIT_EXCEEDED",
                confidence=0,
                veriscore=0,
                reasoning=f"Monthly verification limit exceeded. Upgrade tier for more verifications.",
                tier=self.tier.value,
                models_used=[],
                models_allowed=self.tier_access.max_models,
                domain_detected="",
                domain_confidence=0,
                individual_results=[],
                sources=[],
                evidence={},
                processing_time_ms=0,
                timestamp=datetime.now().isoformat(),
                cost_estimate=0,
                platform=self.platform
            )
        
        # Step 1: Detect domain
        domain_result = await self.langchain_verifier.detect_domain(claim)
        domain = domain_result.get("primary_domain", "general")
        domain_confidence = domain_result.get("confidence", 50)
        
        # Step 2: Select models based on tier and domain
        selected_models = self._select_models_for_tier(domain, force_models)
        
        # Step 3: Run verification with all selected models
        all_results = []
        
        # Run LangChain verification (commercial models)
        if self.langchain_verifier._chains:
            langchain_results = await self.langchain_verifier.verify_with_langchain(claim, context)
            all_results.extend(langchain_results)
        
        # Run specialized models
        specialized_results = await self._run_specialized_models(claim, domain, selected_models)
        all_results.extend(specialized_results)
        
        # Run free providers (always available)
        if include_free_providers:
            free_results = await self._run_free_providers(claim)
            all_results.extend(free_results)
        
        # Step 4: Synthesize results
        synthesis = await self.langchain_verifier.synthesize_results(claim, all_results)
        
        # Calculate veriscore
        veriscore = self._calculate_veriscore(synthesis, all_results, domain_confidence)
        
        # Track usage
        self.verifications_this_month += 1
        
        # Calculate cost estimate
        cost = self._estimate_cost(all_results)
        self.total_cost += cost
        
        return TieredVerificationResult(
            request_id=request_id,
            claim=claim,
            verdict=synthesis.get("final_verdict", "UNVERIFIABLE"),
            confidence=synthesis.get("final_confidence", 50),
            veriscore=veriscore,
            reasoning=synthesis.get("synthesis_reasoning", ""),
            tier=self.tier.value,
            models_used=[r.get("provider", "unknown") for r in all_results],
            models_allowed=self.tier_access.max_models,
            domain_detected=domain,
            domain_confidence=domain_confidence,
            individual_results=all_results,
            sources=synthesis.get("recommended_sources", []),
            evidence=domain_result,
            processing_time_ms=int((time.time() - start_time) * 1000),
            timestamp=datetime.now().isoformat(),
            cost_estimate=cost,
            platform=self.platform
        )
    
    def _select_models_for_tier(
        self,
        domain: str,
        force_models: Optional[List[str]] = None
    ) -> List[str]:
        """Select models based on tier access and domain"""
        if force_models:
            # Filter forced models to only allowed ones
            allowed = (
                self.tier_access.commercial_models +
                self.tier_access.specialized_models +
                self.tier_access.free_providers
            )
            return [m for m in force_models if m in allowed][:self.tier_access.max_models]
        
        selected = []
        
        # Add domain-specific specialized models
        domain_models = DOMAIN_MODEL_MAPPING.get(domain, []) if ALL_MODELS_AVAILABLE else []
        for model in domain_models:
            if model in self.tier_access.specialized_models and model not in selected:
                selected.append(model)
        
        # Add commercial models up to limit
        for model in self.tier_access.commercial_models:
            if len(selected) >= self.tier_access.max_models:
                break
            if model not in selected:
                selected.append(model)
        
        # Fill remaining with specialized models
        for model in self.tier_access.specialized_models:
            if len(selected) >= self.tier_access.max_models:
                break
            if model not in selected:
                selected.append(model)
        
        return selected
    
    async def _run_specialized_models(
        self,
        claim: str,
        domain: str,
        selected_models: List[str]
    ) -> List[Dict[str, Any]]:
        """Run specialized domain models"""
        results = []
        
        if not ALL_MODELS_AVAILABLE:
            return results
        
        for model_name in selected_models:
            if model_name not in ALL_AI_MODELS:
                continue
            
            if model_name not in self.tier_access.specialized_models:
                continue
            
            try:
                start = time.time()
                adapter_factory = ALL_AI_MODELS[model_name]
                
                if callable(adapter_factory):
                    adapter = adapter_factory()
                else:
                    adapter = adapter_factory
                
                result = await adapter.verify_claim_with_retry(claim)
                
                results.append({
                    "provider": model_name,
                    "verdict": result.verdict,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "response_time_ms": int((time.time() - start) * 1000),
                    "model_type": "specialized"
                })
            except Exception as e:
                print(f"[WARN] Specialized model {model_name} failed: {e}")
        
        return results
    
    async def _run_free_providers(self, claim: str) -> List[Dict[str, Any]]:
        """Run free providers (Wikipedia, arXiv, PubMed)"""
        results = []
        
        if not ALL_MODELS_AVAILABLE:
            return results
        
        for provider_name in self.tier_access.free_providers:
            if provider_name not in ALL_AI_MODELS:
                continue
            
            try:
                start = time.time()
                adapter_factory = ALL_AI_MODELS[provider_name]
                
                if callable(adapter_factory):
                    adapter = adapter_factory()
                else:
                    adapter = adapter_factory
                
                result = await adapter.verify_claim_with_retry(claim)
                
                results.append({
                    "provider": provider_name,
                    "verdict": result.verdict,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "response_time_ms": int((time.time() - start) * 1000),
                    "model_type": "free",
                    "cost": 0
                })
            except Exception as e:
                print(f"[WARN] Free provider {provider_name} failed: {e}")
        
        return results
    
    def _calculate_veriscore(
        self,
        synthesis: Dict,
        results: List[Dict],
        domain_confidence: float
    ) -> float:
        """Calculate Veriscore (0-100)"""
        base_score = synthesis.get("final_confidence", 50)
        
        # Agreement bonus
        agreement = synthesis.get("agreement_percentage", 50)
        agreement_bonus = (agreement - 50) / 10  # -5 to +5
        
        # Domain confidence bonus
        domain_bonus = (domain_confidence - 50) / 20  # -2.5 to +2.5
        
        # Model count bonus (more models = more reliable)
        model_count = len([r for r in results if r.get("verdict") != "ERROR"])
        model_bonus = min(5, model_count / 2)
        
        veriscore = base_score + agreement_bonus + domain_bonus + model_bonus
        return round(max(0, min(100, veriscore)), 2)
    
    def _estimate_cost(self, results: List[Dict]) -> float:
        """Estimate verification cost"""
        cost = 0.0
        
        for r in results:
            provider = r.get("provider", "")
            model_type = r.get("model_type", "")
            
            if model_type == "free":
                continue
            
            # Estimated costs per call
            costs = {
                "groq": 0.0001,
                "openai": 0.005,
                "anthropic": 0.008,
                "google": 0.002,
                "perplexity": 0.003,
                "cohere": 0.002,
                "together": 0.001,
            }
            
            for key, c in costs.items():
                if key in provider.lower():
                    cost += c
                    break
        
        return round(cost, 6)


# ============================================================
# PLATFORM-SPECIFIC CLIENTS
# ============================================================

class WebClient:
    """Web platform client"""
    
    def __init__(self, api_key: str, tier: TierName = TierName.FREE):
        self.api_key = api_key
        self.orchestrator = TieredVerificationOrchestrator(tier, platform="web")
    
    async def verify(self, claim: str, **kwargs) -> TieredVerificationResult:
        return await self.orchestrator.verify(claim, **kwargs)


class DesktopClient:
    """Desktop app client"""
    
    def __init__(self, api_key: str, tier: TierName = TierName.FREE):
        self.api_key = api_key
        self.orchestrator = TieredVerificationOrchestrator(tier, platform="desktop")
    
    async def verify(self, claim: str, **kwargs) -> TieredVerificationResult:
        return await self.orchestrator.verify(claim, **kwargs)


class MobileClient:
    """Mobile app client"""
    
    def __init__(self, api_key: str, tier: TierName = TierName.FREE):
        self.api_key = api_key
        self.orchestrator = TieredVerificationOrchestrator(tier, platform="mobile")
    
    async def verify(self, claim: str, **kwargs) -> TieredVerificationResult:
        return await self.orchestrator.verify(claim, **kwargs)


class BrowserExtensionClient:
    """Browser extension client"""
    
    def __init__(self, api_key: str, tier: TierName = TierName.FREE):
        self.api_key = api_key
        self.orchestrator = TieredVerificationOrchestrator(tier, platform="browser_extension")
    
    async def verify(self, claim: str, **kwargs) -> TieredVerificationResult:
        return await self.orchestrator.verify(claim, **kwargs)


class APIClient:
    """API client for programmatic access"""
    
    def __init__(self, api_key: str, tier: TierName = TierName.PROFESSIONAL):
        if tier in [TierName.FREE, TierName.STARTER, TierName.PRO]:
            raise ValueError("API access requires Professional tier or higher")
        
        self.api_key = api_key
        self.orchestrator = TieredVerificationOrchestrator(tier, platform="api")
    
    async def verify(self, claim: str, **kwargs) -> TieredVerificationResult:
        return await self.orchestrator.verify(claim, **kwargs)
    
    async def batch_verify(self, claims: List[str], **kwargs) -> List[TieredVerificationResult]:
        """Batch verification for API clients"""
        tasks = [self.orchestrator.verify(claim, **kwargs) for claim in claims]
        return await asyncio.gather(*tasks)


# ============================================================
# FACTORY FUNCTION
# ============================================================

def create_verification_client(
    api_key: str,
    tier: Union[str, TierName],
    platform: str = "web"
) -> Union[WebClient, DesktopClient, MobileClient, BrowserExtensionClient, APIClient]:
    """
    Factory to create appropriate client based on platform.
    
    Args:
        api_key: User's API key
        tier: Subscription tier
        platform: Platform type (web, desktop, mobile, browser_extension, api)
    
    Returns:
        Appropriate client instance
    """
    if isinstance(tier, str):
        tier = TierName(tier)
    
    clients = {
        "web": WebClient,
        "desktop": DesktopClient,
        "mobile": MobileClient,
        "browser_extension": BrowserExtensionClient,
        "api": APIClient,
    }
    
    client_class = clients.get(platform, WebClient)
    return client_class(api_key, tier)


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

async def verify_claim_tiered(
    claim: str,
    tier: Union[str, TierName] = TierName.FREE,
    platform: str = "web",
    **kwargs
) -> TieredVerificationResult:
    """
    Convenience function for quick verification.
    
    Example:
        result = await verify_claim_tiered(
            "COVID vaccines are effective",
            tier="pro",
            platform="web"
        )
    """
    if isinstance(tier, str):
        tier = TierName(tier)
    
    orchestrator = TieredVerificationOrchestrator(tier, platform)
    return await orchestrator.verify(claim, **kwargs)


def get_tier_info(tier: Union[str, TierName]) -> Dict[str, Any]:
    """Get information about a tier's capabilities"""
    if isinstance(tier, str):
        tier = TierName(tier)
    
    access = TIER_MODEL_ACCESS.get(tier)
    if not access:
        return {"error": "Unknown tier"}
    
    return {
        "tier": tier.value,
        "max_models": access.max_models,
        "ensemble_voting": access.ensemble_voting,
        "commercial_models_count": len(access.commercial_models),
        "specialized_models_count": len(access.specialized_models),
        "free_providers_count": len(access.free_providers),
        "max_verifications": access.max_verifications_per_month,
        "verification_speed": access.verification_speed,
        "features": access.features,
        "commercial_models": access.commercial_models,
        "specialized_models": access.specialized_models,
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("TIERED VERIFICATION SYSTEM TEST")
        print("=" * 60)
        
        # Test each tier
        for tier in [TierName.FREE, TierName.STARTER, TierName.PRO, TierName.ENTERPRISE]:
            print(f"\n--- Testing {tier.value.upper()} tier ---")
            info = get_tier_info(tier)
            print(f"Max models: {info['max_models']}")
            print(f"Commercial: {info['commercial_models_count']}")
            print(f"Specialized: {info['specialized_models_count']}")
            print(f"Max verifications: {info['max_verifications']}")
        
        # Test verification
        print("\n--- Running verification test ---")
        result = await verify_claim_tiered(
            "Aspirin can help prevent heart attacks in high-risk patients",
            tier=TierName.PRO,
            platform="web"
        )
        
        print(f"Claim: {result.claim}")
        print(f"Verdict: {result.verdict}")
        print(f"Confidence: {result.confidence}%")
        print(f"Veriscore: {result.veriscore}")
        print(f"Domain: {result.domain_detected}")
        print(f"Models used: {len(result.models_used)}")
        print(f"Processing time: {result.processing_time_ms}ms")
        
    asyncio.run(test())
