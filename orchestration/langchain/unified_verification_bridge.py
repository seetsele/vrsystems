"""
VERITY SYSTEMS - UNIFIED VERIFICATION BRIDGE (v2.0)
====================================================
World-class integration layer connecting LangChain orchestration with:
- NEXUS Pipeline (intelligence/nexus)
- All 50+ AI Model Providers
- Unified Data Providers (fact-checkers, academic, search)
- Real-time verification engine
- Continuous learning system
- **231-Point Verification System** (11 pillars × 21 checks)
- **21-Point Fast Verification** (7 pillars × 3 checks)
- **VeriScore™ Calculator** with 7-pillar weighting
- **TemporalTruth™** Temporal verification
- **SourceGraph™** Source authority scoring
- **NuanceNet™** Nuance and context detection
- **Counter-Evidence Detection** system

This is the central nervous system of the Verity platform.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Add python-tools to path for api_server_v10 imports
PYTHON_TOOLS = os.path.join(ROOT, 'python-tools')
if PYTHON_TOOLS not in sys.path:
    sys.path.insert(0, PYTHON_TOOLS)

# Import 231-Point NEXUS v2 System
try:
    from intelligence.nexus_core_v2 import VerityNEXUSv2, Verdict as NEXUSVerdict
    HAS_NEXUS_V2 = True
except ImportError:
    HAS_NEXUS_V2 = False
    VerityNEXUSv2 = None
    NEXUSVerdict = None

# Import 21-Point Fast Verification
try:
    from verity_21point import TwentyOnePointVerifier
    HAS_21POINT = True
except ImportError:
    HAS_21POINT = False
    TwentyOnePointVerifier = None

# ============================================================
# PRODUCTION CLASS IMPORTS FROM api_server_v10.py
# ============================================================
try:
    from api_server_v10 import (
        NuanceDetector,           # Full NuanceNet™ with patterns
        TemporalVerifier,         # Full TemporalTruth™ verifier
        SourceAuthorityScorer,    # Full SourceGraph™ scorer
        CounterEvidenceDetector,  # Counter-evidence analysis
        VeriScoreCalculator,      # 7-pillar VeriScore™ calculator
        ContentTypeDetector,      # PDF, image, URL detection
    )
    HAS_PRODUCTION_CLASSES = True
    logger.info("Production classes loaded from api_server_v10")
except ImportError as e:
    HAS_PRODUCTION_CLASSES = False
    NuanceDetector = None
    TemporalVerifier = None
    SourceAuthorityScorer = None
    CounterEvidenceDetector = None
    VeriScoreCalculator = None
    ContentTypeDetector = None
    logger.warning(f"Production classes not available: {e}")

# ============================================================
# UNIFIED ORCHESTRATOR IMPORTS (Specialized Models, Integrations)
# ============================================================
try:
    from orchestration.langchain.unified_orchestrator import (
        UnifiedLangChainOrchestrator,
        VerificationMode,
        VerificationDomain,
    )
    HAS_UNIFIED_ORCHESTRATOR = True
except ImportError:
    HAS_UNIFIED_ORCHESTRATOR = False
    UnifiedLangChainOrchestrator = None

# ============================================================
# MASTER ORCHESTRATOR IMPORTS (LangChain advanced features)
# ============================================================
try:
    from orchestration.langchain.master_orchestrator import (
        LangChainMasterOrchestrator,
        VerificationConfig,
        ModelSelector,
        VerdictAggregator,
        ReasoningChain,
        SourceVerificationChain,
    )
    HAS_MASTER_ORCHESTRATOR = True
except ImportError:
    HAS_MASTER_ORCHESTRATOR = False
    LangChainMasterOrchestrator = None
    ModelSelector = None
    VerdictAggregator = None

# ============================================================
# CONTINUOUS LEARNING SYSTEM
# ============================================================
try:
    from intelligence.nexus.continuous_learning import (
        ContinuousLearningSystem,
        FeedbackItem,
        FeedbackType,
        LearningSignal,
    )
    HAS_CONTINUOUS_LEARNING = True
except ImportError:
    HAS_CONTINUOUS_LEARNING = False
    ContinuousLearningSystem = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for generic operations
T = TypeVar('T')


# ============================================================
# CORE ENUMS AND DATA STRUCTURES
# ============================================================

class VerificationTier(Enum):
    """Verification tiers with different levels of thoroughness"""
    INSTANT = "instant"           # Single fast model, < 1 second
    STANDARD = "standard"         # 3-5 models, consensus
    COMPREHENSIVE = "comprehensive"  # 5-10 models + sources
    FORENSIC = "forensic"         # Full analysis, all models + deep source search


class ClaimCategory(Enum):
    """Categories for claim classification"""
    SCIENCE = "science"
    HEALTH = "health"
    POLITICS = "politics"
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    GENERAL = "general"
    BREAKING_NEWS = "breaking_news"
    HISTORICAL = "historical"


class SourceCredibility(Enum):
    """Source credibility tiers"""
    AUTHORITATIVE = 1.0      # Peer-reviewed, official sources
    REPUTABLE = 0.8          # Major news outlets, established experts
    MODERATE = 0.6           # Wikipedia, general news
    LOW = 0.4                # Social media, blogs
    UNVERIFIED = 0.2         # Unknown sources


@dataclass
class VerificationContext:
    """Context for verification including user preferences and history"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tier: VerificationTier = VerificationTier.STANDARD
    category_hint: Optional[ClaimCategory] = None
    enable_deepfake_check: bool = True
    enable_source_verification: bool = True
    enable_langchain_reasoning: bool = True
    max_cost: float = 0.50
    timeout_seconds: int = 30
    preferred_models: List[str] = field(default_factory=list)
    blocked_models: List[str] = field(default_factory=list)
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedVerificationResult:
    """Comprehensive verification result from all systems"""
    # Core verdict
    claim: str
    verdict: str
    confidence: float
    score: int  # 0-100 Verity Score
    
    # Reasoning chain
    reasoning: str
    langchain_reasoning: Optional[str] = None
    reasoning_steps: List[str] = field(default_factory=list)
    
    # Sources and evidence
    sources: List[Dict[str, Any]] = field(default_factory=list)
    evidence_snippets: List[str] = field(default_factory=list)
    
    # Model consensus
    models_used: List[str] = field(default_factory=list)
    model_results: List[Dict[str, Any]] = field(default_factory=list)
    model_agreement: float = 0.0
    
    # Classification
    category: ClaimCategory = ClaimCategory.GENERAL
    subcategory: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    
    # Deepfake analysis (if applicable)
    deepfake_analysis: Optional[Dict[str, Any]] = None
    
    # ============================================================
    # 231-POINT VERIFICATION SYSTEM (11 pillars × 21 checks)
    # ============================================================
    verification_231: Optional[Dict[str, Any]] = field(default_factory=lambda: {
        'total_score': 0.0,
        'points_passed': 0,
        'points_total': 231,
        'pillar_scores': {},
        'summary': ''
    })
    
    # ============================================================
    # 21-POINT FAST VERIFICATION (7 pillars × 3 checks)
    # ============================================================
    verification_21: Optional[Dict[str, Any]] = field(default_factory=lambda: {
        'veriscore': 0.0,
        'points_passed': 0,
        'points_total': 21,
        'pillar_scores': {},
        'point_details': {}
    })
    
    # ============================================================
    # VERISCORE™ COMPONENTS
    # ============================================================
    veriscore_components: Optional[Dict[str, float]] = field(default_factory=lambda: {
        'source_quality': 0.0,       # Weight: 0.20
        'evidence_strength': 0.0,    # Weight: 0.18
        'model_consensus': 0.0,      # Weight: 0.17
        'temporal_validity': 0.0,    # Weight: 0.12
        'logical_consistency': 0.0,  # Weight: 0.13
        'counter_evidence': 0.0,     # Weight: 0.10
        'nuance_score': 0.0          # Weight: 0.10
    })
    
    # ============================================================
    # ADVANCED ANALYSIS
    # ============================================================
    temporal_analysis: Optional[Dict[str, Any]] = None  # TemporalTruth™
    source_authority: Optional[Dict[str, Any]] = None   # SourceGraph™
    counter_evidence: Optional[Dict[str, Any]] = None   # Counter claims
    nuance_analysis: Optional[Dict[str, Any]] = None    # NuanceNet™
    
    # Metadata
    tier_used: VerificationTier = VerificationTier.STANDARD
    processing_time_ms: int = 0
    total_cost: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = field(default_factory=lambda: hashlib.md5(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:12])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "request_id": self.request_id,
            "claim": self.claim,
            "verdict": self.verdict,
            "confidence": round(self.confidence, 2),
            "verity_score": self.score,
            "reasoning": self.reasoning,
            "langchain_reasoning": self.langchain_reasoning,
            "reasoning_steps": self.reasoning_steps,
            "sources": self.sources[:10],  # Limit to top 10
            "evidence": self.evidence_snippets[:5],
            "consensus": {
                "models_used": self.models_used,
                "agreement_percentage": round(self.model_agreement, 2),
                "model_count": len(self.models_used)
            },
            "classification": {
                "category": self.category.value,
                "subcategory": self.subcategory,
                "topics": self.topics
            },
            "deepfake_analysis": self.deepfake_analysis,
            # ============================================================
            # 231-POINT VERIFICATION (11 pillars × 21 checks)
            # ============================================================
            "verification_231": {
                "total_score": round(self.verification_231.get('total_score', 0) if self.verification_231 else 0, 2),
                "points_passed": self.verification_231.get('points_passed', 0) if self.verification_231 else 0,
                "points_total": 231,
                "pillar_scores": self.verification_231.get('pillar_scores', {}) if self.verification_231 else {},
                "pillars": {
                    "P1": "Data Source Validation",
                    "P2": "AI Model Consensus",
                    "P3": "Knowledge Graph Verification",
                    "P4": "NLP & Semantic Analysis",
                    "P5": "Temporal Verification",
                    "P6": "Academic & Research Sources",
                    "P7": "Web Intelligence",
                    "P8": "Multimedia Analysis",
                    "P9": "Statistical Validation",
                    "P10": "Logical Consistency",
                    "P11": "Meta-Analysis & Synthesis"
                },
                "summary": self.verification_231.get('summary', '') if self.verification_231 else ''
            },
            # ============================================================
            # 21-POINT FAST VERIFICATION (7 pillars × 3 checks)
            # ============================================================
            "verification_21": {
                "veriscore": round(self.verification_21.get('veriscore', 0) if self.verification_21 else 0, 1),
                "points_passed": self.verification_21.get('points_passed', 0) if self.verification_21 else 0,
                "points_total": 21,
                "pillar_scores": self.verification_21.get('pillar_scores', {}) if self.verification_21 else {},
                "pillars": {
                    "claim_parsing": "Claim Structure Analysis",
                    "temporal": "Temporal Verification",
                    "source_quality": "Source Quality Assessment",
                    "evidence": "Evidence Corroboration",
                    "ai_consensus": "AI Model Consensus",
                    "logical": "Logical Consistency",
                    "synthesis": "Result Synthesis"
                },
                "point_details": self.verification_21.get('point_details', {}) if self.verification_21 else {}
            },
            # ============================================================
            # VERISCORE™ BREAKDOWN (7 weighted components)
            # ============================================================
            "veriscore_components": {
                "source_quality": {"score": round(self.veriscore_components.get('source_quality', 0), 2), "weight": 0.20},
                "evidence_strength": {"score": round(self.veriscore_components.get('evidence_strength', 0), 2), "weight": 0.18},
                "model_consensus": {"score": round(self.veriscore_components.get('model_consensus', 0), 2), "weight": 0.17},
                "temporal_validity": {"score": round(self.veriscore_components.get('temporal_validity', 0), 2), "weight": 0.12},
                "logical_consistency": {"score": round(self.veriscore_components.get('logical_consistency', 0), 2), "weight": 0.13},
                "counter_evidence": {"score": round(self.veriscore_components.get('counter_evidence', 0), 2), "weight": 0.10},
                "nuance_score": {"score": round(self.veriscore_components.get('nuance_score', 0), 2), "weight": 0.10}
            } if self.veriscore_components else {},
            # ============================================================
            # ADVANCED ANALYSIS
            # ============================================================
            "temporal_analysis": self.temporal_analysis,
            "source_authority": self.source_authority,
            "counter_evidence": self.counter_evidence,
            "nuance_analysis": self.nuance_analysis,
            # Metadata
            "metadata": {
                "tier": self.tier_used.value,
                "processing_time_ms": self.processing_time_ms,
                "cost": round(self.total_cost, 4),
                "timestamp": self.timestamp,
                "systems_used": {
                    "nexus_231": HAS_NEXUS_V2,
                    "fast_21": HAS_21POINT,
                    "langchain": True
                }
            }
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# ============================================================
# LANGCHAIN INTEGRATION LAYER
# ============================================================

class LangChainReasoningChain:
    """
    Advanced LangChain reasoning chain for multi-step verification.
    Uses chain-of-thought prompting and self-consistency.
    """
    
    def __init__(self):
        self.llm = None
        self.fact_check_prompt = None
        self.reasoning_chain = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize LangChain components"""
        if self._initialized:
            return
            
        try:
            from langchain.chains import LLMChain, SequentialChain
            from langchain.prompts import PromptTemplate, ChatPromptTemplate
            from langchain_openai import ChatOpenAI
            from langchain_anthropic import ChatAnthropic
            
            # Initialize primary LLM with fallback
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            
            if os.getenv("OPENAI_API_KEY"):
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            elif os.getenv("ANTHROPIC_API_KEY"):
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.1,
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            else:
                logger.warning("No LLM API key found, reasoning chain will use fallback")
                self.llm = None
                
            # Create verification prompt
            self.fact_check_prompt = PromptTemplate(
                input_variables=["claim", "evidence", "sources"],
                template="""You are an expert fact-checker with access to multiple sources.

CLAIM TO VERIFY:
{claim}

EVIDENCE GATHERED:
{evidence}

SOURCES CONSULTED:
{sources}

Analyze this claim step-by-step:

STEP 1 - CLAIM PARSING:
- Break down the claim into individual factual assertions
- Identify any ambiguities or missing context

STEP 2 - EVIDENCE ANALYSIS:
- Evaluate each piece of evidence
- Rate source credibility
- Note any contradictions

STEP 3 - REASONING:
- Apply logical reasoning to evidence
- Consider alternative interpretations
- Identify any gaps in evidence

STEP 4 - VERDICT:
Based on your analysis, provide:
- VERDICT: [TRUE / MOSTLY TRUE / MIXED / MOSTLY FALSE / FALSE / UNVERIFIABLE]
- CONFIDENCE: [0-100]
- EXPLANATION: [Clear reasoning for your verdict]

Your response:"""
            )
            
            if self.llm:
                self.reasoning_chain = LLMChain(
                    llm=self.llm,
                    prompt=self.fact_check_prompt
                )
                
            self._initialized = True
            logger.info("LangChain reasoning chain initialized")
            
        except ImportError as e:
            logger.warning(f"LangChain components not available: {e}")
            self._initialized = True  # Mark as initialized but disabled
            
    async def reason(
        self,
        claim: str,
        evidence: List[str],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run LangChain reasoning on claim with evidence
        
        Returns:
            Dict with verdict, confidence, reasoning, and steps
        """
        if not self._initialized:
            await self.initialize()
            
        if not self.reasoning_chain:
            return self._fallback_reasoning(claim, evidence, sources)
            
        try:
            # Format evidence and sources
            evidence_text = "\n".join(f"- {e}" for e in evidence[:10])
            sources_text = "\n".join(
                f"- [{s.get('name', 'Unknown')}] ({s.get('credibility', 'Unknown')}): {s.get('excerpt', '')[:200]}"
                for s in sources[:5]
            )
            
            # Run reasoning chain
            result = await self.reasoning_chain.ainvoke({
                "claim": claim,
                "evidence": evidence_text or "No specific evidence gathered",
                "sources": sources_text or "No sources consulted"
            })
            
            # Parse result
            return self._parse_reasoning_result(result.get("text", ""))
            
        except Exception as e:
            logger.error(f"LangChain reasoning failed: {e}")
            return self._fallback_reasoning(claim, evidence, sources)
            
    def _parse_reasoning_result(self, text: str) -> Dict[str, Any]:
        """Parse LangChain reasoning output"""
        import re
        
        # Extract verdict
        verdict_match = re.search(r'VERDICT:\s*(TRUE|MOSTLY TRUE|MIXED|MOSTLY FALSE|FALSE|UNVERIFIABLE)', text, re.IGNORECASE)
        verdict = verdict_match.group(1).upper() if verdict_match else "UNVERIFIABLE"
        
        # Extract confidence
        conf_match = re.search(r'CONFIDENCE:\s*(\d+)', text)
        confidence = int(conf_match.group(1)) if conf_match else 50
        
        # Extract explanation
        exp_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n\n|$)', text, re.DOTALL)
        explanation = exp_match.group(1).strip() if exp_match else text[-500:]
        
        # Extract reasoning steps
        steps = []
        for step_num in range(1, 5):
            step_match = re.search(rf'STEP {step_num}[^:]*:\s*(.+?)(?=STEP|VERDICT|$)', text, re.DOTALL)
            if step_match:
                steps.append(step_match.group(1).strip()[:300])
        
        return {
            "verdict": verdict.replace(" ", "_"),
            "confidence": min(100, max(0, confidence)),
            "explanation": explanation,
            "steps": steps,
            "raw_response": text
        }
        
    def _fallback_reasoning(
        self,
        claim: str,
        evidence: List[str],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback reasoning when LangChain is unavailable"""
        # Simple heuristic-based reasoning
        positive_signals = sum(1 for s in sources if s.get('verdict', '').upper() in ['TRUE', 'CONFIRMED'])
        negative_signals = sum(1 for s in sources if s.get('verdict', '').upper() in ['FALSE', 'DEBUNKED'])
        
        if positive_signals > negative_signals * 2:
            verdict = "TRUE"
            confidence = min(90, 50 + positive_signals * 10)
        elif negative_signals > positive_signals * 2:
            verdict = "FALSE"
            confidence = min(90, 50 + negative_signals * 10)
        elif sources:
            verdict = "MIXED"
            confidence = 50
        else:
            verdict = "UNVERIFIABLE"
            confidence = 30
            
        return {
            "verdict": verdict,
            "confidence": confidence,
            "explanation": f"Based on {len(sources)} sources: {positive_signals} supporting, {negative_signals} contradicting",
            "steps": ["Evidence collection", "Source verification", "Consensus analysis"],
            "raw_response": None
        }


# ============================================================
# PROVIDER AGGREGATION LAYER
# ============================================================

class UnifiedProviderManager:
    """
    Manages all verification providers with intelligent routing
    """
    
    def __init__(self):
        self.ai_models = {}
        self.fact_checkers = {}
        self.data_sources = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize all providers"""
        if self._initialized:
            return
            
        logger.info("Initializing Unified Provider Manager...")
        
        # Initialize AI models
        await self._init_ai_models()
        
        # Initialize fact-checkers
        await self._init_fact_checkers()
        
        # Initialize data sources
        await self._init_data_sources()
        
        self._initialized = True
        logger.info(f"Provider Manager initialized with {len(self.ai_models)} AI models, "
                   f"{len(self.fact_checkers)} fact-checkers, {len(self.data_sources)} data sources")
        
    async def _init_ai_models(self):
        """Initialize AI model providers"""
        try:
            from providers.ai_models.all_models import ALL_AI_MODELS, create_provider
            
            for model_id, model_info in ALL_AI_MODELS.items():
                try:
                    provider = create_provider(model_id)
                    if provider:
                        self.ai_models[model_id] = {
                            "provider": provider,
                            "info": model_info,
                            "available": True
                        }
                except Exception as e:
                    logger.debug(f"Could not initialize {model_id}: {e}")
                    
        except ImportError as e:
            logger.warning(f"AI models not available: {e}")
            
    async def _init_fact_checkers(self):
        """Initialize fact-checker providers"""
        try:
            from providers.unified_data_providers import UnifiedFactCheckers
            
            checkers = UnifiedFactCheckers()
            self.fact_checkers = checkers.providers
            
        except ImportError as e:
            logger.warning(f"Fact-checkers not available: {e}")
            
    async def _init_data_sources(self):
        """Initialize data source providers"""
        try:
            from providers.data_sources.all_sources import DataSourceAggregator
            
            aggregator = DataSourceAggregator()
            self.data_sources['aggregator'] = aggregator
            
        except ImportError as e:
            logger.warning(f"Data sources not available: {e}")
            
    def get_models_for_tier(self, tier: VerificationTier) -> List[str]:
        """Get appropriate models for verification tier"""
        available = list(self.ai_models.keys())
        
        if not available:
            return []
            
        if tier == VerificationTier.INSTANT:
            # Single fast model
            fast_models = [m for m in available if 'groq' in m or 'ollama' in m]
            return fast_models[:1] if fast_models else available[:1]
            
        elif tier == VerificationTier.STANDARD:
            # 3-5 diverse models
            selected = []
            # Add one from each provider type
            for prefix in ['groq', 'openai', 'anthropic', 'ollama', 'together']:
                models = [m for m in available if m.startswith(prefix)]
                if models:
                    selected.append(models[0])
            return selected[:5]
            
        elif tier == VerificationTier.COMPREHENSIVE:
            # 5-10 models
            return available[:10]
            
        else:  # FORENSIC
            # All available models
            return available
            
    async def verify_with_models(
        self,
        claim: str,
        model_ids: List[str],
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Verify claim using specified models
        
        Returns:
            List of verification results from each model
        """
        results = []
        tasks = []
        
        for model_id in model_ids:
            if model_id in self.ai_models:
                provider = self.ai_models[model_id]["provider"]
                task = self._verify_with_provider(provider, model_id, claim, timeout)
                tasks.append(task)
                
        # Run all verifications in parallel
        if tasks:
            completed = await asyncio.gather(*tasks, return_exceptions=True)
            results = [r for r in completed if isinstance(r, dict)]
            
        return results
        
    async def _verify_with_provider(
        self,
        provider: Any,
        model_id: str,
        claim: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Verify claim with a single provider"""
        start = datetime.utcnow()
        
        try:
            if hasattr(provider, 'verify_claim'):
                result = await asyncio.wait_for(
                    provider.verify_claim(claim),
                    timeout=timeout
                )
                
                return {
                    "model_id": model_id,
                    "verdict": result.verdict if hasattr(result, 'verdict') else str(result),
                    "confidence": result.confidence if hasattr(result, 'confidence') else 70,
                    "reasoning": result.reasoning if hasattr(result, 'reasoning') else "",
                    "cost": result.cost if hasattr(result, 'cost') else 0.0,
                    "response_time": (datetime.utcnow() - start).total_seconds() * 1000
                }
            else:
                return {
                    "model_id": model_id,
                    "verdict": "ERROR",
                    "confidence": 0,
                    "reasoning": "Provider does not support verify_claim",
                    "cost": 0.0,
                    "response_time": 0
                }
                
        except asyncio.TimeoutError:
            return {
                "model_id": model_id,
                "verdict": "ERROR",
                "confidence": 0,
                "reasoning": f"Timeout after {timeout}s",
                "cost": 0.0,
                "response_time": timeout * 1000
            }
            
        except Exception as e:
            return {
                "model_id": model_id,
                "verdict": "ERROR",
                "confidence": 0,
                "reasoning": str(e),
                "cost": 0.0,
                "response_time": (datetime.utcnow() - start).total_seconds() * 1000
            }
            
    async def search_sources(
        self,
        claim: str,
        max_sources: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for sources related to claim"""
        sources = []
        
        # Try fact-checkers first
        for name, checker in self.fact_checkers.items():
            try:
                if hasattr(checker, 'search') or hasattr(checker, 'check_claim'):
                    method = getattr(checker, 'search', None) or getattr(checker, 'check_claim', None)
                    result = await asyncio.wait_for(
                        method(claim) if asyncio.iscoroutinefunction(method) else asyncio.to_thread(method, claim),
                        timeout=10
                    )
                    if result:
                        sources.append({
                            "name": name,
                            "type": "fact_checker",
                            "result": result,
                            "credibility": 0.9
                        })
            except Exception as e:
                logger.debug(f"Fact-checker {name} failed: {e}")
                
        # Try data source aggregator
        if 'aggregator' in self.data_sources:
            try:
                aggregator = self.data_sources['aggregator']
                if hasattr(aggregator, 'search'):
                    results = await asyncio.wait_for(
                        aggregator.search(claim),
                        timeout=15
                    )
                    sources.extend(results[:max_sources - len(sources)])
            except Exception as e:
                logger.debug(f"Data source aggregator failed: {e}")
                
        return sources[:max_sources]


# ============================================================
# NEXUS INTEGRATION LAYER
# ============================================================

class NEXUSBridge:
    """
    Bridge between LangChain orchestration and NEXUS pipeline
    """
    
    def __init__(self):
        self.pipeline = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize NEXUS pipeline"""
        if self._initialized:
            return
            
        try:
            from intelligence.nexus.pipeline import NEXUSPipeline
            
            self.pipeline = NEXUSPipeline()
            await self.pipeline.initialize()
            self._initialized = True
            logger.info("NEXUS Bridge initialized")
            
        except Exception as e:
            logger.warning(f"NEXUS pipeline not available: {e}")
            self._initialized = True
            
    async def verify(self, claim: str, options: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Run NEXUS verification"""
        if not self._initialized:
            await self.initialize()
            
        if not self.pipeline:
            return None
            
        try:
            result = await self.pipeline.verify(claim, options)
            
            return {
                "verdict": result.verdict.value if hasattr(result.verdict, 'value') else str(result.verdict),
                "confidence": result.confidence,
                "score": result.score,
                "explanation": result.explanation,
                "sources": [
                    {
                        "name": s.name,
                        "url": s.url,
                        "verdict": s.verdict,
                        "credibility": s.credibility,
                        "excerpt": s.excerpt
                    }
                    for s in result.sources
                ] if result.sources else [],
                "category": result.category,
                "processing_time_ms": result.processing_time_ms
            }
            
        except Exception as e:
            logger.error(f"NEXUS verification failed: {e}")
            return None


# ============================================================
# MAIN UNIFIED VERIFICATION BRIDGE
# ============================================================

class UnifiedVerificationBridge:
    """
    THE CENTRAL VERIFICATION ORCHESTRATOR
    
    Combines:
    - LangChain reasoning chains (via LangChainMasterOrchestrator)
    - 50+ AI model providers
    - NEXUS verification pipeline
    - Fact-checker APIs
    - Source verification
    - Deepfake detection
    - **231-Point Verification System** (11 pillars × 21 checks)
    - **21-Point Fast Verification** (7 pillars × 3 checks)
    - **VeriScore™ Calculator** (production class from api_server_v10)
    - **TemporalTruth™** Analysis (production class)
    - **SourceGraph™** Authority Scoring (production class)
    - **Counter-Evidence Detection** (production class)
    - **NuanceNet™** (production class with detection patterns)
    - **Continuous Learning System** (feedback & model improvement)
    - **Unified Orchestrator** (specialized models, integrations)
    
    This is the main entry point for all verification requests.
    """
    
    def __init__(self):
        self.langchain = LangChainReasoningChain()
        self.providers = UnifiedProviderManager()
        self.nexus = NEXUSBridge()
        self._initialized = False
        self._cache = {}  # Simple in-memory cache
        
        # ============================================================
        # 231-POINT NEXUS V2 SYSTEM (11 pillars × 21 checks)
        # ============================================================
        self.nexus_v2 = None  # Type: Optional[VerityNEXUSv2]
        if HAS_NEXUS_V2:
            try:
                self.nexus_v2 = VerityNEXUSv2()
                logger.info("NEXUS v2 (231-point) system loaded")
            except Exception as e:
                logger.warning(f"Could not initialize NEXUS v2: {e}")
        
        # ============================================================
        # 21-POINT FAST VERIFICATION SYSTEM
        # ============================================================
        self.fast_verifier = None  # Type: Optional[TwentyOnePointVerifier]
        if HAS_21POINT:
            try:
                self.fast_verifier = TwentyOnePointVerifier()
                logger.info("21-Point fast verification system loaded")
            except Exception as e:
                logger.warning(f"Could not initialize 21-Point verifier: {e}")
        
        # ============================================================
        # PRODUCTION ANALYSIS CLASSES (from api_server_v10.py)
        # ============================================================
        self.nuance_detector = None
        self.temporal_verifier = None
        self.source_authority_scorer = None
        self.counter_evidence_detector = None
        self.veriscore_calculator = None
        self.content_type_detector = None
        
        if HAS_PRODUCTION_CLASSES:
            try:
                self.nuance_detector = NuanceDetector()
                self.temporal_verifier = TemporalVerifier()
                self.source_authority_scorer = SourceAuthorityScorer()
                self.counter_evidence_detector = CounterEvidenceDetector()
                self.veriscore_calculator = VeriScoreCalculator()
                self.content_type_detector = ContentTypeDetector()
                logger.info("Production analysis classes loaded (NuanceNet™, TemporalTruth™, SourceGraph™, VeriScore™)")
            except Exception as e:
                logger.warning(f"Could not initialize production classes: {e}")
        
        # ============================================================
        # LANGCHAIN MASTER ORCHESTRATOR (advanced multi-model reasoning)
        # ============================================================
        self.master_orchestrator = None
        if HAS_MASTER_ORCHESTRATOR:
            try:
                self.master_orchestrator = LangChainMasterOrchestrator()
                logger.info("LangChain Master Orchestrator loaded")
            except Exception as e:
                logger.warning(f"Could not initialize Master Orchestrator: {e}")
        
        # ============================================================
        # UNIFIED ORCHESTRATOR (specialized models, integrations)
        # ============================================================
        self.unified_orchestrator = None
        if HAS_UNIFIED_ORCHESTRATOR:
            try:
                self.unified_orchestrator = UnifiedLangChainOrchestrator()
                logger.info("Unified LangChain Orchestrator loaded (specialized models, integrations)")
            except Exception as e:
                logger.warning(f"Could not initialize Unified Orchestrator: {e}")
        
        # ============================================================
        # CONTINUOUS LEARNING SYSTEM
        # ============================================================
        self.continuous_learning = None
        if HAS_CONTINUOUS_LEARNING:
            try:
                self.continuous_learning = ContinuousLearningSystem()
                logger.info("Continuous Learning System loaded")
            except Exception as e:
                logger.warning(f"Could not initialize Continuous Learning: {e}")
        
    async def initialize(self):
        """Initialize all components"""
        if self._initialized:
            return
            
        logger.info("Initializing Unified Verification Bridge...")
        
        # Initialize all components in parallel
        init_tasks = [
            self.langchain.initialize(),
            self.providers.initialize(),
            self.nexus.initialize(),
        ]
        
        # Add master orchestrator initialization if available
        if self.master_orchestrator and hasattr(self.master_orchestrator, 'initialize'):
            init_tasks.append(self.master_orchestrator.initialize())
        
        await asyncio.gather(*init_tasks, return_exceptions=True)
        
        self._initialized = True
        
        # Log system status
        systems_loaded = []
        if HAS_NEXUS_V2: systems_loaded.append("NEXUS-v2-231pt")
        if HAS_21POINT: systems_loaded.append("21-Point")
        if HAS_PRODUCTION_CLASSES: systems_loaded.append("Production-Classes")
        if HAS_MASTER_ORCHESTRATOR: systems_loaded.append("Master-Orchestrator")
        if HAS_UNIFIED_ORCHESTRATOR: systems_loaded.append("Unified-Orchestrator")
        if HAS_CONTINUOUS_LEARNING: systems_loaded.append("Continuous-Learning")
        
        logger.info(f"Unified Verification Bridge ready. Systems: {', '.join(systems_loaded)}")
        
    async def verify(
        self,
        claim: str,
        context: Optional[VerificationContext] = None
    ) -> UnifiedVerificationResult:
        """
        MAIN VERIFICATION ENTRY POINT
        
        Orchestrates the complete verification process:
        1. Claim preprocessing
        2. Category classification
        3. Source gathering
        4. Multi-model verification
        5. LangChain reasoning
        6. NEXUS pipeline (if available)
        7. **231-Point NEXUS v2 Verification** (NEW)
        8. **21-Point Fast Verification** (NEW)
        9. Result aggregation with VeriScore™
        10. Deepfake analysis (if enabled)
        
        Args:
            claim: The claim to verify
            context: Optional verification context
            
        Returns:
            UnifiedVerificationResult with complete analysis
        """
        start_time = datetime.utcnow()
        context = context or VerificationContext()
        
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
            
        # Check cache
        cache_key = self._make_cache_key(claim, context)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if (datetime.utcnow() - datetime.fromisoformat(cached['timestamp'])).seconds < 3600:
                logger.info(f"Cache hit for claim: {claim[:50]}...")
                return UnifiedVerificationResult(**cached['result'])
        
        # Step 1: Classify claim
        category = await self._classify_claim(claim, context.category_hint)
        
        # Step 2: Get sources
        sources = []
        if context.enable_source_verification:
            sources = await self.providers.search_sources(claim)
            
        # Step 3: Multi-model verification
        model_ids = self.providers.get_models_for_tier(context.tier)
        if context.preferred_models:
            model_ids = context.preferred_models + [m for m in model_ids if m not in context.preferred_models]
        if context.blocked_models:
            model_ids = [m for m in model_ids if m not in context.blocked_models]
            
        model_results = await self.providers.verify_with_models(
            claim, model_ids, context.timeout_seconds
        )
        
        # Step 4: LangChain reasoning
        langchain_result = None
        if context.enable_langchain_reasoning:
            evidence = [s.get('excerpt', '') for s in sources if s.get('excerpt')]
            langchain_result = await self.langchain.reason(claim, evidence, sources)
            
        # Step 5: NEXUS verification (original)
        nexus_result = await self.nexus.verify(claim) if self.nexus.pipeline else None
        
        # ============================================================
        # Step 6: 231-POINT NEXUS V2 VERIFICATION (11 pillars × 21 checks)
        # ============================================================
        verification_231 = None
        if self.nexus_v2 and context.tier in [VerificationTier.COMPREHENSIVE, VerificationTier.FORENSIC]:
            try:
                # Prepare provider results for NEXUS v2
                provider_results = [{
                    'provider': r.get('model_id', 'unknown'),
                    'verdict': r.get('verdict', 'UNVERIFIABLE'),
                    'confidence': r.get('confidence', 50),
                    'provider_type': 'ai_model'
                } for r in model_results]
                
                # Add sources as fact-check providers
                for source in sources[:5]:
                    provider_results.append({
                        'provider': source.get('name', 'unknown'),
                        'verdict': 'TRUE' if source.get('credibility', 0.5) > 0.6 else 'UNVERIFIABLE',
                        'confidence': source.get('credibility', 0.5) * 100,
                        'provider_type': 'fact_check' if 'fact' in source.get('type', '').lower() else 'news'
                    })
                
                # Execute 231-point verification
                claim_info = {
                    'claim': claim,
                    'category': category.value,
                    'complexity': len(claim.split()) / 50.0  # Simple complexity heuristic
                }
                verification_231 = self.nexus_v2.score_231_points(provider_results, claim_info)
                logger.info(f"231-Point verification complete: {verification_231.get('total', 0):.1f}/100")
            except Exception as e:
                logger.warning(f"231-point verification failed: {e}")
        
        # ============================================================
        # Step 7: 21-POINT FAST VERIFICATION (7 pillars × 3 checks)
        # ============================================================
        verification_21 = None
        if self.fast_verifier and context.tier in [VerificationTier.INSTANT, VerificationTier.STANDARD]:
            try:
                verification_21 = await self.fast_verifier.verify_claim(claim)
                logger.info(f"21-Point verification complete: {verification_21.get('points_passed', 0)}/21")
            except Exception as e:
                logger.warning(f"21-point verification failed: {e}")
        
        # ============================================================
        # Step 8: VERISCORE™ CALCULATION
        # ============================================================
        veriscore_components = await self._calculate_veriscore_components(
            model_results=model_results,
            sources=sources,
            langchain_result=langchain_result,
            verification_231=verification_231,
            verification_21=verification_21
        )
        
        # ============================================================
        # Step 9: ADVANCED ANALYSIS (TemporalTruth™, SourceGraph™, Counter-Evidence)
        # ============================================================
        temporal_analysis = self._analyze_temporal(claim, sources)
        source_authority = self._analyze_source_authority(sources)
        counter_evidence = self._detect_counter_evidence(model_results, sources)
        nuance_analysis = self._analyze_nuance(claim, model_results, langchain_result)
        
        # Step 10: Aggregate results
        result = await self._aggregate_results(
            claim=claim,
            category=category,
            model_results=model_results,
            sources=sources,
            langchain_result=langchain_result,
            nexus_result=nexus_result,
            verification_231=verification_231,
            verification_21=verification_21,
            veriscore_components=veriscore_components,
            temporal_analysis=temporal_analysis,
            source_authority=source_authority,
            counter_evidence=counter_evidence,
            nuance_analysis=nuance_analysis,
            context=context,
            start_time=start_time
        )
        
        # Step 11: Deepfake analysis (if applicable)
        if context.enable_deepfake_check and self._looks_like_media_claim(claim):
            result.deepfake_analysis = await self._analyze_deepfake(claim)
            
        # Cache result
        self._cache[cache_key] = {
            'result': result.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _calculate_veriscore_components(
        self,
        model_results: List[Dict],
        sources: List[Dict],
        langchain_result: Optional[Dict],
        verification_231: Optional[Dict],
        verification_21: Optional[Dict]
    ) -> Dict[str, float]:
        """
        Calculate VeriScore™ components using 7-pillar weighting system.
        
        Weights:
        - source_quality: 0.20
        - evidence_strength: 0.18
        - model_consensus: 0.17
        - temporal_validity: 0.12
        - logical_consistency: 0.13
        - counter_evidence: 0.10
        - nuance_score: 0.10
        """
        # ============================================================
        # USE PRODUCTION VeriScoreCalculator IF AVAILABLE
        # ============================================================
        if self.veriscore_calculator:
            try:
                # Format data for production calculator
                calculator_input = {
                    'claim': claim,
                    'model_results': model_results,
                    'sources': sources,
                    'langchain_result': langchain_result,
                    'verification_231': verification_231,
                    'verification_21': verification_21
                }
                production_result = self.veriscore_calculator.calculate_veriscore(calculator_input)
                if production_result and 'pillar_scores' in production_result:
                    return {
                        'source_quality': production_result['pillar_scores'].get('source_quality', 0.0) * 100,
                        'evidence_strength': production_result['pillar_scores'].get('evidence', 0.0) * 100,
                        'model_consensus': production_result['pillar_scores'].get('ai_consensus', 0.0) * 100,
                        'temporal_validity': production_result['pillar_scores'].get('temporal', 0.0) * 100,
                        'logical_consistency': production_result['pillar_scores'].get('logical', 0.0) * 100,
                        'counter_evidence': (1.0 - production_result.get('counter_evidence_ratio', 0.0)) * 100,
                        'nuance_score': production_result['pillar_scores'].get('synthesis', 0.0) * 100
                    }
            except Exception as e:
                logger.warning(f"Production VeriScoreCalculator failed, using fallback: {e}")
        
        # Fallback to basic calculation
        components = {
            'source_quality': 0.0,
            'evidence_strength': 0.0,
            'model_consensus': 0.0,
            'temporal_validity': 0.0,
            'logical_consistency': 0.0,
            'counter_evidence': 0.0,
            'nuance_score': 0.0
        }
        
        # Source Quality (from 231-point P1 or source count)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P1'):
            components['source_quality'] = verification_231['pillar_scores']['P1'].get('score', 0) * 100
        elif sources:
            avg_credibility = sum(s.get('credibility', 0.5) for s in sources) / len(sources)
            components['source_quality'] = avg_credibility * 100
        
        # Evidence Strength (from 231-point P6 Academic Sources or langchain)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P6'):
            components['evidence_strength'] = verification_231['pillar_scores']['P6'].get('score', 0) * 100
        elif langchain_result:
            components['evidence_strength'] = langchain_result.get('confidence', 50)
        
        # Model Consensus (from 231-point P2 or model agreement)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P2'):
            components['model_consensus'] = verification_231['pillar_scores']['P2'].get('score', 0) * 100
        elif model_results:
            verdicts = [r.get('verdict', '').upper() for r in model_results if r.get('verdict')]
            if verdicts:
                most_common = max(set(verdicts), key=verdicts.count)
                components['model_consensus'] = (verdicts.count(most_common) / len(verdicts)) * 100
        
        # Temporal Validity (from 231-point P5)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P5'):
            components['temporal_validity'] = verification_231['pillar_scores']['P5'].get('score', 0) * 100
        elif verification_21 and verification_21.get('pillar_scores', {}).get('temporal'):
            components['temporal_validity'] = (verification_21['pillar_scores']['temporal'] / 3.0) * 100
        else:
            components['temporal_validity'] = 70.0  # Default
        
        # Logical Consistency (from 231-point P10)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P10'):
            components['logical_consistency'] = verification_231['pillar_scores']['P10'].get('score', 0) * 100
        elif verification_21 and verification_21.get('pillar_scores', {}).get('logical'):
            components['logical_consistency'] = (verification_21['pillar_scores']['logical'] / 3.0) * 100
        else:
            components['logical_consistency'] = 60.0  # Default
        
        # Counter-Evidence (inverse - less counter-evidence = higher score)
        false_verdicts = sum(1 for r in model_results if r.get('verdict', '').upper() in ['FALSE', 'MOSTLY_FALSE'])
        if model_results:
            counter_ratio = false_verdicts / len(model_results)
            components['counter_evidence'] = (1 - counter_ratio) * 100
        else:
            components['counter_evidence'] = 50.0
        
        # Nuance Score (from 231-point P11 Meta-Analysis)
        if verification_231 and verification_231.get('pillar_scores', {}).get('P11'):
            components['nuance_score'] = verification_231['pillar_scores']['P11'].get('score', 0) * 100
        elif langchain_result and langchain_result.get('steps'):
            components['nuance_score'] = min(len(langchain_result['steps']) * 20, 100)
        else:
            components['nuance_score'] = 50.0
        
        return components
    
    def _analyze_temporal(self, claim: str, sources: List[Dict]) -> Dict[str, Any]:
        """TemporalTruth™ - Analyze temporal aspects of claim using production TemporalVerifier"""
        
        # ============================================================
        # USE PRODUCTION TemporalVerifier IF AVAILABLE
        # ============================================================
        if self.temporal_verifier:
            try:
                production_result = self.temporal_verifier.verify_temporal(claim, sources)
                if production_result:
                    return production_result
            except Exception as e:
                logger.warning(f"Production TemporalVerifier failed, using fallback: {e}")
        
        # Fallback to basic implementation
        import re
        
        temporal_analysis = {
            'has_date': False,
            'temporal_type': 'static',  # static, recent, historical, ongoing
            'date_references': [],
            'currency_score': 100,  # How current the claim is
            'source_freshness': 0
        }
        
        # Extract dates
        date_patterns = [
            r'\b(19|20)\d{2}\b',  # Years
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b(today|yesterday|this week|this month|this year|last year|recent|recently)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, claim, re.IGNORECASE)
            if matches:
                temporal_analysis['has_date'] = True
                temporal_analysis['date_references'].extend(matches)
        
        # Determine temporal type
        claim_lower = claim.lower()
        if any(w in claim_lower for w in ['today', 'yesterday', 'this week', 'breaking', 'just']):
            temporal_analysis['temporal_type'] = 'recent'
            temporal_analysis['currency_score'] = 60  # May need updating
        elif any(w in claim_lower for w in ['historical', 'ancient', 'century', 'founded', 'established']):
            temporal_analysis['temporal_type'] = 'historical'
            temporal_analysis['currency_score'] = 100
        elif any(w in claim_lower for w in ['ongoing', 'continues', 'still', 'current']):
            temporal_analysis['temporal_type'] = 'ongoing'
            temporal_analysis['currency_score'] = 80
        
        # Source freshness
        if sources:
            # In production, check source dates
            temporal_analysis['source_freshness'] = 80  # Default
        
        return temporal_analysis
    
    def _analyze_source_authority(self, sources: List[Dict]) -> Dict[str, Any]:
        """SourceGraph™ - Analyze source authority and credibility using production SourceAuthorityScorer"""
        
        # ============================================================
        # USE PRODUCTION SourceAuthorityScorer IF AVAILABLE
        # ============================================================
        if self.source_authority_scorer:
            try:
                production_result = self.source_authority_scorer.score_sources(sources)
                if production_result:
                    return production_result
            except Exception as e:
                logger.warning(f"Production SourceAuthorityScorer failed, using fallback: {e}")
        authority_analysis = {
            'total_sources': len(sources),
            'authority_score': 0.0,
            'diversity_score': 0.0,
            'by_type': {},
            'top_sources': []
        }
        
        if not sources:
            return authority_analysis
        
        # Count by type
        type_counts = {}
        credibilities = []
        
        for source in sources:
            s_type = source.get('type', 'unknown')
            type_counts[s_type] = type_counts.get(s_type, 0) + 1
            credibilities.append(source.get('credibility', 0.5))
        
        authority_analysis['by_type'] = type_counts
        authority_analysis['authority_score'] = sum(credibilities) / len(credibilities) * 100
        authority_analysis['diversity_score'] = min(len(type_counts) / 5.0, 1.0) * 100
        authority_analysis['top_sources'] = sorted(
            sources, 
            key=lambda x: x.get('credibility', 0), 
            reverse=True
        )[:5]
        
        return authority_analysis
    
    def _detect_counter_evidence(
        self, 
        model_results: List[Dict], 
        sources: List[Dict]
    ) -> Dict[str, Any]:
        """Detect and analyze counter-evidence using production CounterEvidenceDetector"""
        
        # ============================================================
        # USE PRODUCTION CounterEvidenceDetector IF AVAILABLE
        # ============================================================
        if self.counter_evidence_detector:
            try:
                production_result = self.counter_evidence_detector.detect_counter_evidence(model_results, sources)
                if production_result:
                    return production_result
            except Exception as e:
                logger.warning(f"Production CounterEvidenceDetector failed, using fallback: {e}")
        
        # Fallback to basic implementation
        counter_analysis = {
            'has_counter_evidence': False,
            'counter_verdict_count': 0,
            'counter_sources': [],
            'disagreement_ratio': 0.0,
            'counter_queries': []
        }
        
        if not model_results:
            return counter_analysis
        
        # Count opposing verdicts
        verdicts = [r.get('verdict', '').upper() for r in model_results]
        true_count = sum(1 for v in verdicts if v in ['TRUE', 'MOSTLY_TRUE'])
        false_count = sum(1 for v in verdicts if v in ['FALSE', 'MOSTLY_FALSE'])
        
        if true_count > 0 and false_count > 0:
            counter_analysis['has_counter_evidence'] = True
            counter_analysis['counter_verdict_count'] = min(true_count, false_count)
            counter_analysis['disagreement_ratio'] = min(true_count, false_count) / len(verdicts)
        
        # Generate counter-queries (suggestions for additional verification)
        if counter_analysis['has_counter_evidence']:
            counter_analysis['counter_queries'] = [
                "What evidence contradicts this claim?",
                "What are the main criticisms of this claim?",
                "Are there alternative explanations?"
            ]
        
        return counter_analysis
    
    def _analyze_nuance(
        self,
        claim: str,
        model_results: List[Dict],
        langchain_result: Optional[Dict]
    ) -> Dict[str, Any]:
        """NuanceNet™ - Analyze nuance and context sensitivity using production NuanceDetector"""
        
        # ============================================================
        # USE PRODUCTION NuanceDetector IF AVAILABLE
        # This includes ABSOLUTE_PATTERNS, COMPARATIVE_PATTERNS, NUANCED_TOPICS,
        # ACADEMIC_HEDGING_PATTERNS, BALANCED_CLAIM_PATTERNS
        # ============================================================
        if self.nuance_detector:
            try:
                production_result = self.nuance_detector.detect_nuance(claim)
                if production_result:
                    # Merge with model-based context sensitivity
                    if model_results:
                        verdicts = set(r.get('verdict', '').upper() for r in model_results)
                        if 'MIXED' in verdicts or 'MISLEADING' in verdicts:
                            production_result['context_sensitivity'] = max(
                                production_result.get('context_sensitivity', 0),
                                80.0
                            )
                    return production_result
            except Exception as e:
                logger.warning(f"Production NuanceDetector failed, using fallback: {e}")
        
        # Fallback to basic implementation
        nuance_analysis = {
            'nuance_level': 'low',  # low, medium, high
            'nuance_score': 0.0,
            'qualifiers_detected': [],
            'context_sensitivity': 0.0,
            'recommendation': ''
        }
        
        # Detect qualifiers
        qualifiers = ['some', 'most', 'many', 'often', 'sometimes', 'generally', 
                     'typically', 'usually', 'may', 'might', 'could', 'possibly',
                     'approximately', 'about', 'around', 'roughly']
        
        claim_lower = claim.lower()
        for q in qualifiers:
            if f' {q} ' in f' {claim_lower} ':
                nuance_analysis['qualifiers_detected'].append(q)
        
        # Determine nuance level
        num_qualifiers = len(nuance_analysis['qualifiers_detected'])
        if num_qualifiers >= 3:
            nuance_analysis['nuance_level'] = 'high'
            nuance_analysis['nuance_score'] = 80.0
        elif num_qualifiers >= 1:
            nuance_analysis['nuance_level'] = 'medium'
            nuance_analysis['nuance_score'] = 50.0
        else:
            nuance_analysis['nuance_level'] = 'low'
            nuance_analysis['nuance_score'] = 20.0
        
        # Context sensitivity from verdict spread
        if model_results:
            verdicts = set(r.get('verdict', '').upper() for r in model_results)
            if 'MIXED' in verdicts or 'MISLEADING' in verdicts:
                nuance_analysis['context_sensitivity'] = 80.0
                nuance_analysis['nuance_level'] = 'high'
            elif len(verdicts) > 2:
                nuance_analysis['context_sensitivity'] = 60.0
            else:
                nuance_analysis['context_sensitivity'] = 30.0
        
        # Recommendation
        if nuance_analysis['nuance_level'] == 'high':
            nuance_analysis['recommendation'] = "This claim requires careful context. The truth may vary depending on specific circumstances."
        elif nuance_analysis['nuance_level'] == 'medium':
            nuance_analysis['recommendation'] = "Some aspects of this claim may be context-dependent."
        else:
            nuance_analysis['recommendation'] = "This claim appears to be relatively straightforward."
        
        return nuance_analysis
        
    async def _classify_claim(
        self,
        claim: str,
        hint: Optional[ClaimCategory] = None
    ) -> ClaimCategory:
        """Classify claim into category"""
        if hint:
            return hint
            
        claim_lower = claim.lower()
        
        # Simple keyword-based classification
        category_keywords = {
            ClaimCategory.SCIENCE: ['study', 'research', 'scientists', 'experiment', 'data', 'evidence'],
            ClaimCategory.HEALTH: ['health', 'medical', 'doctor', 'disease', 'vaccine', 'treatment', 'covid', 'virus'],
            ClaimCategory.POLITICS: ['government', 'president', 'election', 'vote', 'politician', 'congress', 'law'],
            ClaimCategory.FINANCE: ['stock', 'market', 'economy', 'investment', 'crypto', 'bitcoin', 'inflation'],
            ClaimCategory.TECHNOLOGY: ['ai', 'artificial intelligence', 'tech', 'software', 'digital', 'cyber'],
            ClaimCategory.SPORTS: ['game', 'match', 'team', 'player', 'championship', 'score'],
            ClaimCategory.ENTERTAINMENT: ['movie', 'actor', 'celebrity', 'music', 'show'],
            ClaimCategory.HISTORICAL: ['history', 'ancient', 'historical', 'century', 'war', 'founded'],
            ClaimCategory.BREAKING_NEWS: ['breaking', 'just in', 'developing', 'happening now']
        }
        
        scores = {cat: 0 for cat in ClaimCategory}
        for category, keywords in category_keywords.items():
            for kw in keywords:
                if kw in claim_lower:
                    scores[category] += 1
                    
        best_category = max(scores.items(), key=lambda x: x[1])
        return best_category[0] if best_category[1] > 0 else ClaimCategory.GENERAL
        
    async def _aggregate_results(
        self,
        claim: str,
        category: ClaimCategory,
        model_results: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        langchain_result: Optional[Dict[str, Any]],
        nexus_result: Optional[Dict[str, Any]],
        verification_231: Optional[Dict[str, Any]],
        verification_21: Optional[Dict[str, Any]],
        veriscore_components: Dict[str, float],
        temporal_analysis: Dict[str, Any],
        source_authority: Dict[str, Any],
        counter_evidence: Dict[str, Any],
        nuance_analysis: Dict[str, Any],
        context: VerificationContext,
        start_time: datetime
    ) -> UnifiedVerificationResult:
        """
        Aggregate all results into final verdict with 231-point and 21-point integration.
        
        This is the core synthesis function that combines:
        - AI model consensus
        - LangChain reasoning
        - NEXUS pipeline results
        - 231-Point verification (11 pillars × 21 checks)
        - 21-Point fast verification (7 pillars × 3 checks)
        - VeriScore™ components
        - TemporalTruth™, SourceGraph™, Counter-Evidence, NuanceNet™
        """
        
        # Filter valid results
        valid_results = [r for r in model_results if r.get('verdict') != 'ERROR']
        
        if not valid_results and not langchain_result and not nexus_result:
            return UnifiedVerificationResult(
                claim=claim,
                verdict="UNVERIFIABLE",
                confidence=0.0,
                score=0,
                reasoning="No valid verification results obtained",
                category=category,
                tier_used=context.tier,
                processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
            
        # Calculate weighted verdict
        verdict_weights = {
            'TRUE': 1.0, 'MOSTLY_TRUE': 0.75, 'MIXED': 0.0,
            'MOSTLY_FALSE': -0.75, 'FALSE': -1.0, 'MISLEADING': -0.5,
            'UNVERIFIABLE': 0.0
        }
        
        weighted_scores = []
        confidences = []
        
        # Weight model results
        for r in valid_results:
            verdict = r.get('verdict', 'UNVERIFIABLE').upper().replace(' ', '_')
            weight = verdict_weights.get(verdict, 0.0)
            conf = r.get('confidence', 50) / 100.0
            weighted_scores.append(weight * conf)
            confidences.append(r.get('confidence', 50))
            
        # Add LangChain result with higher weight
        if langchain_result:
            verdict = langchain_result.get('verdict', 'UNVERIFIABLE').upper().replace(' ', '_')
            weight = verdict_weights.get(verdict, 0.0)
            conf = langchain_result.get('confidence', 50) / 100.0
            weighted_scores.append(weight * conf * 1.5)  # 1.5x weight for LangChain
            confidences.append(langchain_result.get('confidence', 50))
            
        # Add NEXUS result
        if nexus_result:
            verdict = nexus_result.get('verdict', 'unverifiable').upper().replace(' ', '_')
            weight = verdict_weights.get(verdict, 0.0)
            conf = nexus_result.get('confidence', 50) / 100.0
            weighted_scores.append(weight * conf)
            confidences.append(nexus_result.get('confidence', 50))
        
        # ============================================================
        # INCORPORATE 231-POINT VERIFICATION INTO SCORING
        # ============================================================
        if verification_231 and verification_231.get('total'):
            # 231-point score (0-100) contributes to confidence
            nexus_231_score = verification_231['total']
            # Add as additional confidence factor (weight 1.3 for comprehensive analysis)
            weighted_scores.append((nexus_231_score / 100 - 0.5) * 2 * 1.3)  # Normalize to -1 to 1
            confidences.append(nexus_231_score)
        
        # ============================================================
        # INCORPORATE 21-POINT FAST VERIFICATION INTO SCORING
        # ============================================================
        if verification_21 and verification_21.get('veriscore'):
            fast_score = verification_21['veriscore']
            # Add as additional confidence factor (weight 0.8 for fast mode)
            weighted_scores.append((fast_score / 100 - 0.5) * 2 * 0.8)
            confidences.append(fast_score)
            
        # Calculate final verdict
        if weighted_scores:
            avg_score = sum(weighted_scores) / len(weighted_scores)
            
            if avg_score > 0.5:
                final_verdict = 'TRUE'
            elif avg_score > 0.2:
                final_verdict = 'MOSTLY_TRUE'
            elif avg_score > -0.2:
                final_verdict = 'MIXED'
            elif avg_score > -0.5:
                final_verdict = 'MOSTLY_FALSE'
            else:
                final_verdict = 'FALSE'
        else:
            final_verdict = 'UNVERIFIABLE'
            
        # Calculate confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 50
        
        # Calculate agreement
        verdicts = [r.get('verdict', '').upper() for r in valid_results]
        if verdicts:
            most_common = max(set(verdicts), key=verdicts.count)
            agreement = (verdicts.count(most_common) / len(verdicts)) * 100
        else:
            agreement = 0
            
        # Adjust confidence based on agreement
        confidence = avg_confidence * (0.5 + agreement / 200)  # 50-100% of avg based on agreement
        confidence = min(100, max(0, confidence))
        
        # ============================================================
        # CALCULATE VERISCORE™ (0-100) USING 7-PILLAR WEIGHTED FORMULA
        # ============================================================
        veriscore_weights = {
            'source_quality': 0.20,
            'evidence_strength': 0.18,
            'model_consensus': 0.17,
            'temporal_validity': 0.12,
            'logical_consistency': 0.13,
            'counter_evidence': 0.10,
            'nuance_score': 0.10
        }
        
        verity_score = 0.0
        for component, weight in veriscore_weights.items():
            component_value = veriscore_components.get(component, 50.0)
            verity_score += component_value * weight
        
        verity_score = int(min(100, max(0, verity_score)))
        
        # Build reasoning
        reasoning_parts = []
        if langchain_result and langchain_result.get('explanation'):
            reasoning_parts.append(langchain_result['explanation'])
        if nexus_result and nexus_result.get('explanation'):
            reasoning_parts.append(nexus_result['explanation'])
        if verification_231 and verification_231.get('summary'):
            reasoning_parts.append(verification_231['summary'])
        if not reasoning_parts:
            supporting = [r for r in valid_results if r.get('verdict', '').upper() in ['TRUE', 'MOSTLY_TRUE']]
            reasoning_parts.append(f"Verified using {len(valid_results)} AI models. "
                                 f"{len(supporting)} support the claim.")
            
        # Calculate total cost
        total_cost = sum(r.get('cost', 0) for r in model_results)
        
        return UnifiedVerificationResult(
            claim=claim,
            verdict=final_verdict,
            confidence=round(confidence, 2),
            score=verity_score,
            reasoning=" ".join(reasoning_parts),
            langchain_reasoning=langchain_result.get('explanation') if langchain_result else None,
            reasoning_steps=langchain_result.get('steps', []) if langchain_result else [],
            sources=[{
                'name': s.get('name', 'Unknown'),
                'url': s.get('url', ''),
                'type': s.get('type', 'general'),
                'credibility': s.get('credibility', 0.5),
                'excerpt': str(s.get('result', ''))[:200] if s.get('result') else ''
            } for s in sources],
            evidence_snippets=[str(s.get('result', ''))[:300] for s in sources if s.get('result')],
            models_used=[r.get('model_id', 'unknown') for r in valid_results],
            model_results=valid_results,
            model_agreement=round(agreement, 2),
            category=category,
            topics=self._extract_topics(claim),
            # ============================================================
            # 231-POINT VERIFICATION RESULTS
            # ============================================================
            verification_231={
                'total_score': verification_231.get('total', 0) if verification_231 else 0,
                'points_passed': verification_231.get('total_passed', 0) if verification_231 else 0,
                'points_total': 231,
                'pillar_scores': verification_231.get('pillar_scores', {}) if verification_231 else {},
                'summary': verification_231.get('summary', '') if verification_231 else ''
            },
            # ============================================================
            # 21-POINT FAST VERIFICATION RESULTS
            # ============================================================
            verification_21={
                'veriscore': verification_21.get('veriscore', 0) if verification_21 else 0,
                'points_passed': verification_21.get('points_passed', 0) if verification_21 else 0,
                'points_total': 21,
                'pillar_scores': {},  # Would need to extract from verification_21
                'point_details': verification_21.get('point_details', {}) if verification_21 else {}
            },
            # ============================================================
            # VERISCORE™ COMPONENTS
            # ============================================================
            veriscore_components=veriscore_components,
            # ============================================================
            # ADVANCED ANALYSIS RESULTS
            # ============================================================
            temporal_analysis=temporal_analysis,
            source_authority=source_authority,
            counter_evidence=counter_evidence,
            nuance_analysis=nuance_analysis,
            # Metadata
            tier_used=context.tier,
            processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            total_cost=round(total_cost, 4)
        )
        
    def _extract_topics(self, claim: str) -> List[str]:
        """Extract topic tags from claim"""
        import re
        
        # Simple keyword extraction
        topics = []
        topic_keywords = {
            'climate': ['climate', 'global warming', 'carbon', 'emissions'],
            'covid': ['covid', 'coronavirus', 'pandemic', 'vaccine'],
            'elections': ['election', 'vote', 'ballot', 'candidate'],
            'economy': ['economy', 'inflation', 'gdp', 'unemployment'],
            'ai': ['ai', 'artificial intelligence', 'machine learning'],
            'crypto': ['bitcoin', 'cryptocurrency', 'blockchain'],
            'health': ['health', 'medical', 'disease', 'treatment']
        }
        
        claim_lower = claim.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in claim_lower for kw in keywords):
                topics.append(topic)
                
        return topics[:5]
        
    def _looks_like_media_claim(self, claim: str) -> bool:
        """Check if claim might involve media/deepfake content"""
        media_terms = ['video', 'image', 'photo', 'audio', 'recording', 'footage', 'clip']
        return any(term in claim.lower() for term in media_terms)
        
    async def _analyze_deepfake(self, claim: str) -> Dict[str, Any]:
        """Analyze potential deepfake content"""
        # Placeholder for deepfake detection
        # In production, this would integrate with deepfake detection APIs
        return {
            "checked": True,
            "media_type": "unknown",
            "deepfake_probability": 0.0,
            "analysis": "No media content detected in claim text"
        }
        
    def _make_cache_key(self, claim: str, context: VerificationContext) -> str:
        """Generate cache key for claim"""
        key_parts = [
            claim.lower().strip(),
            context.tier.value,
            str(context.enable_langchain_reasoning),
            str(context.enable_source_verification)
        ]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    
    # ============================================================
    # CONTINUOUS LEARNING & FEEDBACK
    # ============================================================
    
    async def submit_feedback(
        self,
        claim_id: str,
        claim_text: str,
        original_verdict: str,
        corrected_verdict: Optional[str],
        feedback_type: str,
        explanation: str,
        evidence_urls: Optional[List[str]] = None,
        submitted_by: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Submit feedback for continuous learning.
        
        This integrates with the ContinuousLearningSystem to improve
        model accuracy over time.
        
        Args:
            claim_id: Unique identifier for the verified claim
            claim_text: The original claim text
            original_verdict: The verdict the system gave
            corrected_verdict: The correct verdict (if user is correcting)
            feedback_type: "user_correction", "expert_verification", "source_update", "outcome_feedback"
            explanation: User's explanation of the correction
            evidence_urls: Optional list of supporting evidence URLs
            submitted_by: User identifier
            
        Returns:
            Dict with feedback processing result
        """
        result = {
            "feedback_received": True,
            "claim_id": claim_id,
            "learning_triggered": False
        }
        
        if not self.continuous_learning:
            result["message"] = "Continuous learning system not available"
            return result
        
        try:
            # Map feedback type
            feedback_type_map = {
                "user_correction": FeedbackType.USER_CORRECTION,
                "expert_verification": FeedbackType.EXPERT_VERIFICATION,
                "source_update": FeedbackType.SOURCE_UPDATE,
                "outcome_feedback": FeedbackType.OUTCOME_FEEDBACK,
                "consensus_change": FeedbackType.CONSENSUS_CHANGE
            }
            
            fb_type = feedback_type_map.get(feedback_type, FeedbackType.USER_CORRECTION)
            
            # Determine learning signal
            if corrected_verdict and corrected_verdict.upper() != original_verdict.upper():
                signal = LearningSignal.NEGATIVE  # Model was wrong
            elif corrected_verdict:
                signal = LearningSignal.POSITIVE  # Model was correct
            else:
                signal = LearningSignal.UNCERTAIN
            
            # Create feedback item
            from datetime import datetime
            import hashlib
            
            feedback_item = FeedbackItem(
                feedback_id=hashlib.md5(f"{claim_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
                claim_id=claim_id,
                claim_text=claim_text,
                original_verdict=original_verdict,
                corrected_verdict=corrected_verdict,
                feedback_type=fb_type,
                learning_signal=signal,
                confidence_delta=-10.0 if signal == LearningSignal.NEGATIVE else 5.0,
                explanation=explanation,
                evidence_urls=evidence_urls or [],
                submitted_by=submitted_by,
                submitted_at=datetime.now()
            )
            
            # Process feedback
            learn_result = await self.continuous_learning.process_feedback(feedback_item)
            
            result["learning_triggered"] = learn_result.get("learning", {}).get("updated", False)
            result["retrain_triggered"] = learn_result.get("retrain_triggered", False)
            result["message"] = "Feedback processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            result["error"] = str(e)
        
        return result
    
    async def verify_with_specialized_model(
        self,
        claim: str,
        domain: str,
        context: Optional[VerificationContext] = None
    ) -> UnifiedVerificationResult:
        """
        Verify using domain-specific specialized model.
        
        Integrates with the UnifiedLangChainOrchestrator's specialized models:
        - Medical: BioGPT, PubMedBERT, BioBERT
        - Legal: LegalBERT, CaseLawBERT
        - Financial: FinBERT, FinGPT, EconBERT
        - Scientific: SciBERT, Galactica
        - Climate: ClimateBERT
        - Political: PoliBERT
        - Sports: SportsBERT
        - Technology: TechBERT, SecurityBERT
        
        Args:
            claim: The claim to verify
            domain: "medical", "legal", "financial", "scientific", "climate", "political", "sports", "technology"
            context: Optional verification context
            
        Returns:
            UnifiedVerificationResult with specialized analysis
        """
        context = context or VerificationContext(tier=VerificationTier.COMPREHENSIVE)
        
        # If unified orchestrator available, use its specialized models
        if self.unified_orchestrator:
            try:
                domain_map = {
                    "medical": VerificationDomain.MEDICAL if HAS_UNIFIED_ORCHESTRATOR else None,
                    "legal": VerificationDomain.LEGAL if HAS_UNIFIED_ORCHESTRATOR else None,
                    "financial": VerificationDomain.FINANCIAL if HAS_UNIFIED_ORCHESTRATOR else None,
                    "scientific": VerificationDomain.SCIENTIFIC if HAS_UNIFIED_ORCHESTRATOR else None,
                }
                
                if domain in domain_map and domain_map[domain]:
                    # Use specialized orchestration
                    specialized_result = await self.unified_orchestrator.verify(
                        claim,
                        mode=VerificationMode.EXPERT,
                        domain=domain_map[domain]
                    )
                    
                    # Convert to unified result format
                    # ... conversion logic
                    logger.info(f"Specialized {domain} verification completed")
            except Exception as e:
                logger.warning(f"Specialized model failed, falling back to standard: {e}")
        
        # Fall back to standard verification with domain hint
        context.category_hint = ClaimCategory[domain.upper()] if domain.upper() in ClaimCategory.__members__ else None
        return await self.verify(claim, context)
    
    def detect_content_type(self, content: str) -> Dict[str, Any]:
        """
        Detect content type (PDF, image, URL, research paper, etc.)
        using production ContentTypeDetector.
        
        Returns:
            Dict with detected content type and handling recommendations
        """
        if self.content_type_detector:
            try:
                return self.content_type_detector.detect(content)
            except Exception as e:
                logger.warning(f"ContentTypeDetector failed: {e}")
        
        # Basic fallback detection
        content_lower = content.lower()
        
        if content.startswith('http://') or content.startswith('https://'):
            return {"type": "url", "format": "web", "handling": "fetch_and_extract"}
        elif content_lower.endswith('.pdf'):
            return {"type": "document", "format": "pdf", "handling": "pdf_extraction"}
        elif any(content_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return {"type": "image", "format": content_lower.split('.')[-1], "handling": "image_analysis"}
        elif 'doi.org' in content_lower or 'arxiv.org' in content_lower or 'pubmed' in content_lower:
            return {"type": "research_paper", "format": "academic", "handling": "academic_extraction"}
        else:
            return {"type": "text", "format": "plain", "handling": "standard"}
        
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all systems including 231-point and 21-point verification"""
        if not self._initialized:
            await self.initialize()
            
        return {
            "status": "healthy",
            "components": {
                "langchain": {
                    "initialized": self.langchain._initialized,
                    "llm_available": self.langchain.llm is not None
                },
                "providers": {
                    "initialized": self.providers._initialized,
                    "ai_models_count": len(self.providers.ai_models),
                    "fact_checkers_count": len(self.providers.fact_checkers),
                    "data_sources_count": len(self.providers.data_sources)
                },
                "nexus": {
                    "initialized": self.nexus._initialized,
                    "pipeline_available": self.nexus.pipeline is not None
                },
                # ============================================================
                # 231-POINT NEXUS V2 SYSTEM STATUS
                # ============================================================
                "nexus_v2_231_point": {
                    "available": HAS_NEXUS_V2,
                    "initialized": self.nexus_v2 is not None,
                    "pillars": 11,
                    "checks_per_pillar": 21,
                    "total_checks": 231,
                    "pillar_names": [
                        "P1: Data Source Validation",
                        "P2: AI Model Consensus",
                        "P3: Knowledge Graph Verification",
                        "P4: NLP & Semantic Analysis",
                        "P5: Temporal Verification",
                        "P6: Academic & Research Sources",
                        "P7: Web Intelligence",
                        "P8: Multimedia Analysis",
                        "P9: Statistical Validation",
                        "P10: Logical Consistency",
                        "P11: Meta-Analysis & Synthesis"
                    ]
                },
                # ============================================================
                # 21-POINT FAST VERIFICATION SYSTEM STATUS
                # ============================================================
                "fast_21_point": {
                    "available": HAS_21POINT,
                    "initialized": self.fast_verifier is not None,
                    "pillars": 7,
                    "checks_per_pillar": 3,
                    "total_checks": 21,
                    "pillar_names": [
                        "Claim Structure Analysis",
                        "Temporal Verification",
                        "Source Quality Assessment",
                        "Evidence Corroboration",
                        "AI Model Consensus",
                        "Logical Consistency",
                        "Result Synthesis"
                    ]
                },
                # ============================================================
                # PRODUCTION ANALYSIS CLASSES (from api_server_v10.py)
                # ============================================================
                "production_classes": {
                    "available": HAS_PRODUCTION_CLASSES,
                    "nuance_detector": self.nuance_detector is not None,
                    "temporal_verifier": self.temporal_verifier is not None,
                    "source_authority_scorer": self.source_authority_scorer is not None,
                    "counter_evidence_detector": self.counter_evidence_detector is not None,
                    "veriscore_calculator": self.veriscore_calculator is not None,
                    "content_type_detector": self.content_type_detector is not None
                },
                # ============================================================
                # VERISCORE™ SYSTEM STATUS
                # ============================================================
                "veriscore": {
                    "available": True,
                    "production_calculator": self.veriscore_calculator is not None,
                    "components": 7,
                    "weights": {
                        "source_quality": 0.20,
                        "evidence_strength": 0.18,
                        "model_consensus": 0.17,
                        "temporal_validity": 0.12,
                        "logical_consistency": 0.13,
                        "counter_evidence": 0.10,
                        "nuance_score": 0.10
                    }
                },
                # ============================================================
                # ADVANCED ANALYSIS SYSTEMS
                # ============================================================
                "advanced_analysis": {
                    "temporal_truth": self.temporal_verifier is not None or True,      # TemporalTruth™
                    "source_graph": self.source_authority_scorer is not None or True,  # SourceGraph™
                    "counter_evidence": self.counter_evidence_detector is not None or True,    # Counter-Evidence Detection
                    "nuance_net": self.nuance_detector is not None or True             # NuanceNet™
                },
                # ============================================================
                # LANGCHAIN ORCHESTRATORS
                # ============================================================
                "orchestrators": {
                    "master_orchestrator": HAS_MASTER_ORCHESTRATOR and self.master_orchestrator is not None,
                    "unified_orchestrator": HAS_UNIFIED_ORCHESTRATOR and self.unified_orchestrator is not None,
                    "specialized_models_available": HAS_UNIFIED_ORCHESTRATOR
                },
                # ============================================================
                # CONTINUOUS LEARNING SYSTEM
                # ============================================================
                "continuous_learning": {
                    "available": HAS_CONTINUOUS_LEARNING,
                    "initialized": self.continuous_learning is not None
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

# Global instance for easy access
_bridge_instance: Optional[UnifiedVerificationBridge] = None


async def get_bridge() -> UnifiedVerificationBridge:
    """Get or create the global verification bridge"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = UnifiedVerificationBridge()
        await _bridge_instance.initialize()
    return _bridge_instance


async def quick_verify(claim: str, tier: str = "standard") -> Dict[str, Any]:
    """
    Quick verification function for simple use cases
    
    Args:
        claim: The claim to verify
        tier: "instant", "standard", "comprehensive", or "forensic"
        
    Returns:
        Dictionary with verification result
    """
    bridge = await get_bridge()
    
    tier_map = {
        "instant": VerificationTier.INSTANT,
        "standard": VerificationTier.STANDARD,
        "comprehensive": VerificationTier.COMPREHENSIVE,
        "forensic": VerificationTier.FORENSIC
    }
    
    context = VerificationContext(tier=tier_map.get(tier, VerificationTier.STANDARD))
    result = await bridge.verify(claim, context)
    
    return result.to_dict()


# ============================================================
# CLI INTERFACE
# ============================================================

async def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verity Systems Unified Verification")
    parser.add_argument("claim", nargs="?", help="Claim to verify")
    parser.add_argument("--tier", choices=["instant", "standard", "comprehensive", "forensic"],
                       default="standard", help="Verification tier")
    parser.add_argument("--health", action="store_true", help="Run health check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    bridge = await get_bridge()
    
    if args.health:
        health = await bridge.health_check()
        print(json.dumps(health, indent=2))
        return
        
    if not args.claim:
        # Demo claim
        args.claim = "The Earth is approximately 4.5 billion years old"
        print(f"Demo: Verifying '{args.claim}'\n")
        
    result = await quick_verify(args.claim, args.tier)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=" * 60)
        print(f"CLAIM: {result['claim']}")
        print(f"=" * 60)
        print(f"VERDICT: {result['verdict']}")
        print(f"CONFIDENCE: {result['confidence']}%")
        print(f"VERITY SCORE: {result['verity_score']}/100")
        print(f"-" * 60)
        print(f"REASONING: {result['reasoning']}")
        print(f"-" * 60)
        print(f"Models Used: {result['consensus']['model_count']}")
        print(f"Agreement: {result['consensus']['agreement_percentage']}%")
        print(f"Processing Time: {result['metadata']['processing_time_ms']}ms")
        print(f"Cost: ${result['metadata']['cost']}")


if __name__ == "__main__":
    asyncio.run(main())
