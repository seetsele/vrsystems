"""
VERITY UNIFIED LANGCHAIN ORCHESTRATOR
======================================
Complete integration of all platform components using LangChain:
- 15+ Specialized AI Models
- 50+ Platform Integrations
- Real-time Collaboration
- Analytics & BI Dashboard
- Public Claim Database
- White-label Platform
- Innovation Features (Deepfake, Blockchain, Gamification)

Uses LangChain for:
- Chain-of-thought reasoning
- Multi-agent coordination
- Tool integration
- Memory management
- Structured output parsing
"""

from __future__ import annotations
import asyncio
import os
import sys
import time
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Load environment
from dotenv import load_dotenv
DOTENV_PATH = os.path.join(ROOT, 'python-tools', '.env')
if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

# ============================================================
# LANGCHAIN IMPORTS
# ============================================================

try:
    from langchain.chains import LLMChain, SequentialChain
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.language_models import BaseLLM
    from langchain_core.callbacks import CallbackManager
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LLMChain = None
    PromptTemplate = None

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain.tools import Tool, StructuredTool
    LANGCHAIN_AGENTS_AVAILABLE = True
except ImportError:
    LANGCHAIN_AGENTS_AVAILABLE = False

try:
    from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
    LANGCHAIN_MEMORY_AVAILABLE = True
except ImportError:
    LANGCHAIN_MEMORY_AVAILABLE = False

# ============================================================
# PLATFORM COMPONENT IMPORTS
# ============================================================

# Base providers
try:
    from providers.base_provider import VerificationResult
    from providers.ai_models.all_models import ALL_AI_MODELS, create_provider
    from providers.data_sources.all_sources import DataSourceAggregator
except ImportError as e:
    print(f"[WARN] Base providers import failed: {e}")
    ALL_AI_MODELS = {}

# Specialized AI Models (18 domain-specific models)
try:
    from providers.ai_models.specialized_models import (
        SPECIALIZED_MODELS,
        verify_with_best_model,
        get_specialized_model,
        BioGPTProvider,
        PubMedBERTProvider,
        FinBERTProvider,
        LegalBERTProvider,
        SciBERTProvider,
        ClimateBERTProvider,
        SecurityBERTProvider,
    )
    SPECIALIZED_MODELS_AVAILABLE = True
    # Create a simple orchestrator wrapper
    class SpecializedModelOrchestrator:
        def __init__(self):
            self.models = SPECIALIZED_MODELS
        async def verify(self, claim: str, domain: str = None):
            if domain and domain in self.models:
                model = self.models[domain]()
                return await model.verify_claim(claim)
            return await verify_with_best_model(claim)
except ImportError as e:
    print(f"[WARN] Specialized models import failed: {e}")
    SPECIALIZED_MODELS_AVAILABLE = False
    SpecializedModelOrchestrator = None

# Free Providers (33 free APIs)
try:
    import sys
    _python_tools = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'python-tools')
    if _python_tools not in sys.path:
        sys.path.insert(0, _python_tools)
    from free_provider_config import FreeProviderManager, FREE_PROVIDERS
    FREE_PROVIDERS_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Free providers import failed: {e}")
    FREE_PROVIDERS_AVAILABLE = False
    FreeProviderManager = None

# Platform Integrations (50+)
try:
    from providers.integrations.comprehensive_integrations import (
        IntegrationManager, WebhookHandler, SlackIntegration,
        DiscordIntegration, TeamsIntegration, NotionIntegration
    )
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    IntegrationManager = None

# Real-time Collaboration
try:
    from backend.collaboration.realtime_collab import (
        CollaborationServer, CollaborationRoom, CRDTDocument,
        VectorClock, GCounter, ORSet, LWWMap
    )
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False
    CollaborationServer = None

# Analytics Engine
try:
    from backend.analytics.analytics_engine import (
        AnalyticsEngine, MetricsCollector, ReportGenerator,
        DashboardBuilder, AlertManager
    )
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    AnalyticsEngine = None

# Public Claims Database
try:
    from backend.database.public_claims_db import (
        ClaimDatabase, create_claims_router
    )
    CLAIMS_DB_AVAILABLE = True
except ImportError:
    CLAIMS_DB_AVAILABLE = False
    ClaimDatabase = None

# White-label Platform
try:
    from backend.whitelabel.platform import (
        TenantManager, TenantContext, IndustryVertical,
        WhiteLabelConfig, BrandingConfig
    )
    WHITELABEL_AVAILABLE = True
except ImportError:
    WHITELABEL_AVAILABLE = False
    TenantManager = None

# Innovation Features
try:
    from backend.innovation.innovation_features import (
        DeepfakeDetector, VerificationBlockchain, GamificationSystem,
        MediaType, ManipulationType, DeepfakeResult
    )
    INNOVATION_AVAILABLE = True
except ImportError:
    INNOVATION_AVAILABLE = False
    DeepfakeDetector = None

# Master Orchestrator (existing)
try:
    from orchestration.langchain.master_orchestrator import (
        LangChainMasterOrchestrator, VerificationConfig,
        ConsensusResult, ModelSelector, VerdictAggregator
    )
    MASTER_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    MASTER_ORCHESTRATOR_AVAILABLE = False
    LangChainMasterOrchestrator = None


# ============================================================
# VERIFICATION MODES
# ============================================================

class VerificationMode(Enum):
    """Available verification modes"""
    QUICK = "quick"           # Fast, 3-5 models
    STANDARD = "standard"     # Balanced, 7-10 models
    THOROUGH = "thorough"     # Comprehensive, 15+ models
    EXPERT = "expert"         # Domain-specific specialized models
    ULTIMATE = "ultimate"     # All models + blockchain + all features


class VerificationDomain(Enum):
    """Specialized verification domains"""
    GENERAL = "general"
    MEDICAL = "medical"
    LEGAL = "legal"
    FINANCIAL = "financial"
    SCIENTIFIC = "scientific"
    POLITICAL = "political"
    CLIMATE = "climate"
    TECHNOLOGY = "technology"
    HISTORY = "history"
    SPORTS = "sports"


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

class VerityTools:
    """LangChain tools for fact-checking operations"""
    
    def __init__(self, orchestrator: 'UnifiedOrchestrator'):
        self.orchestrator = orchestrator
    
    def get_tools(self) -> List:
        """Get all available LangChain tools"""
        if not LANGCHAIN_AGENTS_AVAILABLE:
            return []
        
        tools = [
            Tool(
                name="verify_claim",
                description="Verify a factual claim using AI models",
                func=self._verify_claim_sync,
                coroutine=self._verify_claim_async
            ),
            Tool(
                name="search_sources",
                description="Search for sources and evidence about a topic",
                func=self._search_sources_sync,
                coroutine=self._search_sources_async
            ),
            Tool(
                name="analyze_media",
                description="Analyze image/video/audio for manipulation or deepfakes",
                func=self._analyze_media_sync,
                coroutine=self._analyze_media_async
            ),
            Tool(
                name="check_domain_expert",
                description="Get expert domain-specific verification (medical, legal, financial)",
                func=self._domain_expert_sync,
                coroutine=self._domain_expert_async
            ),
            Tool(
                name="get_claim_history",
                description="Check if a claim has been verified before in the public database",
                func=self._get_claim_history_sync,
                coroutine=self._get_claim_history_async
            )
        ]
        
        return tools
    
    def _verify_claim_sync(self, claim: str) -> str:
        return asyncio.run(self._verify_claim_async(claim))
    
    async def _verify_claim_async(self, claim: str) -> str:
        result = await self.orchestrator.verify_claim(claim)
        return json.dumps({
            "verdict": result.verdict,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        })
    
    def _search_sources_sync(self, query: str) -> str:
        return asyncio.run(self._search_sources_async(query))
    
    async def _search_sources_async(self, query: str) -> str:
        sources = await self.orchestrator.search_sources(query)
        return json.dumps(sources[:5])
    
    def _analyze_media_sync(self, url: str) -> str:
        return asyncio.run(self._analyze_media_async(url))
    
    async def _analyze_media_async(self, url: str) -> str:
        result = await self.orchestrator.analyze_media(url)
        return json.dumps(result)
    
    def _domain_expert_sync(self, claim: str) -> str:
        return asyncio.run(self._domain_expert_async(claim))
    
    async def _domain_expert_async(self, claim: str) -> str:
        result = await self.orchestrator.verify_with_experts(claim)
        return json.dumps(result)
    
    def _get_claim_history_sync(self, claim: str) -> str:
        return asyncio.run(self._get_claim_history_async(claim))
    
    async def _get_claim_history_async(self, claim: str) -> str:
        history = await self.orchestrator.get_claim_history(claim)
        return json.dumps(history)


# ============================================================
# LANGCHAIN CHAINS
# ============================================================

class VerityChains:
    """LangChain chains for verification workflows"""
    
    def __init__(self, llm=None):
        self.llm = llm or self._get_default_llm()
        self.chains = {}
        
        if LANGCHAIN_AVAILABLE and self.llm:
            self._setup_chains()
    
    def _get_default_llm(self):
        """Get default LLM based on available API keys"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Try providers in order of preference
        if os.getenv("GROQ_API_KEY"):
            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="llama-3.3-70b-versatile",
                temperature=0.1
            )
        if os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4o-mini",
                temperature=0.1
            )
        if os.getenv("ANTHROPIC_API_KEY"):
            return ChatAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model="claude-3-5-sonnet-20241022",
                temperature=0.1
            )
        return None
    
    def _setup_chains(self):
        """Setup all verification chains"""
        
        # Claim Analysis Chain
        self.chains["analyze_claim"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""Analyze this claim for fact-checking:

Claim: {claim}

Provide analysis in JSON format:
{{
    "claim_type": "factual|opinion|prediction|mixed",
    "key_entities": ["entity1", "entity2"],
    "time_sensitive": true/false,
    "requires_expertise": ["domain1", "domain2"],
    "verifiable_components": ["component1", "component2"],
    "complexity_score": 1-10
}}

Analysis:""",
                input_variables=["claim"]
            ),
            output_key="analysis"
        )
        
        # Evidence Synthesis Chain
        self.chains["synthesize_evidence"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""Synthesize the evidence for this claim:

Claim: {claim}

Evidence from multiple sources:
{evidence}

Model verdicts:
{verdicts}

Provide a comprehensive synthesis in JSON format:
{{
    "supporting_evidence": ["point1", "point2"],
    "contradicting_evidence": ["point1", "point2"],
    "evidence_quality": "high|medium|low",
    "consensus_level": "strong|moderate|weak|conflicting",
    "key_sources": ["source1", "source2"],
    "nuance_factors": ["factor1", "factor2"]
}}

Synthesis:""",
                input_variables=["claim", "evidence", "verdicts"]
            ),
            output_key="synthesis"
        )
        
        # Final Verdict Chain
        self.chains["final_verdict"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""Determine the final verdict for this claim:

Claim: {claim}

Analysis: {analysis}
Evidence Synthesis: {synthesis}
Model Consensus: {consensus}

Provide final verdict in JSON format:
{{
    "verdict": "TRUE|FALSE|MISLEADING|MIXED|UNVERIFIABLE",
    "confidence": 0-100,
    "veriscore": 0-100,
    "reasoning": "detailed explanation",
    "caveats": ["caveat1", "caveat2"],
    "recommendations": ["recommendation1"]
}}

Final Verdict:""",
                input_variables=["claim", "analysis", "synthesis", "consensus"]
            ),
            output_key="verdict"
        )
        
        # Domain Detection Chain
        self.chains["detect_domain"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template="""Detect the domain(s) for this claim:

Claim: {claim}

Available domains: medical, legal, financial, scientific, political, climate, technology, history, sports, general

Respond with JSON:
{{
    "primary_domain": "domain",
    "secondary_domains": ["domain1", "domain2"],
    "confidence": 0-100,
    "specialist_required": true/false
}}

Domain Detection:""",
                input_variables=["claim"]
            ),
            output_key="domain"
        )
    
    async def run_chain(self, chain_name: str, **kwargs) -> str:
        """Run a specific chain"""
        if chain_name not in self.chains:
            raise ValueError(f"Unknown chain: {chain_name}")
        
        chain = self.chains[chain_name]
        result = await chain.arun(**kwargs)
        return result
    
    async def run_full_verification_pipeline(self, claim: str, evidence: List[Dict], verdicts: List[Dict]) -> Dict:
        """Run the complete verification pipeline"""
        # Step 1: Analyze claim
        analysis = await self.run_chain("analyze_claim", claim=claim)
        
        # Step 2: Detect domain
        domain = await self.run_chain("detect_domain", claim=claim)
        
        # Step 3: Synthesize evidence
        synthesis = await self.run_chain(
            "synthesize_evidence",
            claim=claim,
            evidence=json.dumps(evidence),
            verdicts=json.dumps(verdicts)
        )
        
        # Step 4: Generate final verdict
        consensus = self._calculate_consensus(verdicts)
        verdict = await self.run_chain(
            "final_verdict",
            claim=claim,
            analysis=analysis,
            synthesis=synthesis,
            consensus=json.dumps(consensus)
        )
        
        return {
            "analysis": self._safe_json_parse(analysis),
            "domain": self._safe_json_parse(domain),
            "synthesis": self._safe_json_parse(synthesis),
            "verdict": self._safe_json_parse(verdict)
        }
    
    def _calculate_consensus(self, verdicts: List[Dict]) -> Dict:
        """Calculate consensus from model verdicts"""
        if not verdicts:
            return {"level": "none", "agreement": 0}
        
        verdict_counts = {}
        for v in verdicts:
            verdict = v.get("verdict", "UNKNOWN")
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        max_count = max(verdict_counts.values())
        agreement = (max_count / len(verdicts)) * 100
        
        return {
            "verdict_distribution": verdict_counts,
            "dominant_verdict": max(verdict_counts, key=verdict_counts.get),
            "agreement_percentage": agreement,
            "level": "strong" if agreement >= 70 else "moderate" if agreement >= 50 else "weak"
        }
    
    def _safe_json_parse(self, text: str) -> Dict:
        """Safely parse JSON from LLM output"""
        try:
            # Find JSON in text
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {"raw": text}


# ============================================================
# UNIFIED ORCHESTRATOR
# ============================================================

@dataclass
class UnifiedVerificationResult:
    """Complete verification result from unified orchestrator"""
    claim: str
    verdict: str
    confidence: float
    veriscore: float
    
    # Reasoning and evidence
    reasoning: str
    evidence: List[Dict[str, Any]]
    sources: List[str]
    
    # Domain analysis
    domain: str
    domain_confidence: float
    
    # Model consensus
    model_count: int
    model_verdicts: List[Dict[str, Any]]
    agreement_percentage: float
    
    # Additional analysis
    nuance_analysis: Optional[Dict] = None
    deepfake_analysis: Optional[Dict] = None
    blockchain_record: Optional[str] = None
    
    # Metadata
    mode: str = "standard"
    processing_time_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = ""
    
    # Gamification
    points_earned: int = 0


class UnifiedOrchestrator:
    """
    Unified LangChain orchestrator integrating all Verity components.
    
    This is the main entry point for all verification operations,
    coordinating:
    - Multiple AI models via LangChain
    - Specialized domain experts
    - Platform integrations
    - Real-time collaboration
    - Analytics and metrics
    - Blockchain verification records
    - Gamification system
    """
    
    def __init__(
        self,
        mode: VerificationMode = VerificationMode.STANDARD,
        config: Optional[Dict] = None
    ):
        self.mode = mode
        self.config = config or {}
        
        # Initialize components
        self._init_components()
        
        # LangChain setup
        self.chains = VerityChains()
        self.tools = VerityTools(self)
        
        # Metrics
        self.total_verifications = 0
        self.total_cost = 0.0
    
    def _init_components(self):
        """Initialize all platform components"""
        
        # Core orchestrator
        if MASTER_ORCHESTRATOR_AVAILABLE:
            self.master = LangChainMasterOrchestrator(
                config=VerificationConfig(
                    min_models=self._get_min_models(),
                    max_models=self._get_max_models(),
                    use_free_models_first=True,
                    max_cost_per_claim=0.10
                )
            )
        else:
            self.master = None
        
        # Specialized models
        if SPECIALIZED_MODELS_AVAILABLE and SpecializedModelOrchestrator:
            self.specialists = SpecializedModelOrchestrator()
        else:
            self.specialists = None
        
        # Free providers (33 free APIs)
        if FREE_PROVIDERS_AVAILABLE and FreeProviderManager:
            self.free_providers = FreeProviderManager()
        else:
            self.free_providers = None
        
        # Integrations
        if INTEGRATIONS_AVAILABLE and IntegrationManager:
            self.integrations = IntegrationManager()
        else:
            self.integrations = None
        
        # Collaboration
        if COLLABORATION_AVAILABLE and CollaborationServer:
            self.collaboration = CollaborationServer()
        else:
            self.collaboration = None
        
        # Analytics
        if ANALYTICS_AVAILABLE and AnalyticsEngine:
            self.analytics = AnalyticsEngine()
        else:
            self.analytics = None
        
        # Claims database
        if CLAIMS_DB_AVAILABLE and ClaimDatabase:
            database_url = os.getenv("DATABASE_URL", "")
            if database_url:
                self.claims_db = ClaimDatabase(database_url)
            else:
                self.claims_db = None
        else:
            self.claims_db = None
        
        # White-label
        if WHITELABEL_AVAILABLE and TenantManager:
            self.tenants = TenantManager()
        else:
            self.tenants = None
        
        # Innovation features
        if INNOVATION_AVAILABLE:
            self.deepfake_detector = DeepfakeDetector() if DeepfakeDetector else None
            self.blockchain = VerificationBlockchain() if VerificationBlockchain else None
            self.gamification = GamificationSystem() if GamificationSystem else None
        else:
            self.deepfake_detector = None
            self.blockchain = None
            self.gamification = None
    
    def _get_min_models(self) -> int:
        """Get minimum models based on mode"""
        return {
            VerificationMode.QUICK: 3,
            VerificationMode.STANDARD: 5,
            VerificationMode.THOROUGH: 10,
            VerificationMode.EXPERT: 3,
            VerificationMode.ULTIMATE: 15
        }.get(self.mode, 5)
    
    def _get_max_models(self) -> int:
        """Get maximum models based on mode"""
        return {
            VerificationMode.QUICK: 5,
            VerificationMode.STANDARD: 10,
            VerificationMode.THOROUGH: 20,
            VerificationMode.EXPERT: 10,
            VerificationMode.ULTIMATE: 50
        }.get(self.mode, 10)
    
    async def verify_claim(
        self,
        claim: str,
        mode: Optional[VerificationMode] = None,
        domain: Optional[VerificationDomain] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        include_blockchain: bool = False,
        context: Optional[Dict] = None
    ) -> UnifiedVerificationResult:
        """
        Main verification entry point.
        
        Coordinates all components using LangChain for intelligent routing.
        """
        start_time = time.time()
        request_id = f"ver_{int(time.time())}_{hashlib.md5(claim.encode()).hexdigest()[:8]}"
        mode = mode or self.mode
        
        # Track verification
        self.total_verifications += 1
        
        # Step 1: Check claims database for existing verification
        existing = await self._check_existing_verification(claim)
        if existing and not context.get("force_reverify", False) if context else True:
            existing.request_id = request_id
            return existing
        
        # Step 2: Detect domain if not specified
        detected_domain = domain
        if not detected_domain and self.chains.chains.get("detect_domain"):
            try:
                domain_result = await self.chains.run_chain("detect_domain", claim=claim)
                domain_data = self.chains._safe_json_parse(domain_result)
                detected_domain = VerificationDomain(domain_data.get("primary_domain", "general"))
            except:
                detected_domain = VerificationDomain.GENERAL
        
        # Step 3: Run verification based on mode
        if mode == VerificationMode.EXPERT and self.specialists:
            result = await self._verify_with_specialists(claim, detected_domain)
        elif mode == VerificationMode.ULTIMATE:
            result = await self._verify_ultimate(claim, detected_domain, include_blockchain)
        else:
            result = await self._verify_standard(claim, mode, detected_domain)
        
        # Step 4: Run LangChain pipeline for enhanced analysis
        if self.chains.chains:
            try:
                pipeline_result = await self.chains.run_full_verification_pipeline(
                    claim=claim,
                    evidence=result.evidence,
                    verdicts=result.model_verdicts
                )
                # Enhance result with LangChain analysis
                result.reasoning = pipeline_result.get("verdict", {}).get("reasoning", result.reasoning)
                result.nuance_analysis = pipeline_result.get("synthesis", {})
            except Exception as e:
                print(f"[WARN] LangChain pipeline failed: {e}")
        
        # Step 5: Blockchain record (if requested)
        if include_blockchain and self.blockchain:
            try:
                block_hash = await self._record_to_blockchain(claim, result)
                result.blockchain_record = block_hash
            except Exception as e:
                print(f"[WARN] Blockchain record failed: {e}")
        
        # Step 6: Gamification points
        if self.gamification and user_id:
            try:
                points = await self._award_points(user_id, result)
                result.points_earned = points
            except:
                pass
        
        # Step 7: Store in claims database
        if self.claims_db:
            try:
                await self._store_verification(claim, result)
            except:
                pass
        
        # Step 8: Track analytics
        if self.analytics:
            try:
                await self._track_analytics(result)
            except:
                pass
        
        # Finalize
        result.mode = mode.value
        result.request_id = request_id
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        
        return result
    
    async def _verify_standard(
        self,
        claim: str,
        mode: VerificationMode,
        domain: VerificationDomain
    ) -> UnifiedVerificationResult:
        """Standard verification using master orchestrator"""
        if not self.master:
            return self._create_error_result(claim, "Master orchestrator not available")
        
        consensus = await self.master.verify_claim(claim)
        
        return UnifiedVerificationResult(
            claim=claim,
            verdict=consensus.final_verdict,
            confidence=consensus.confidence,
            veriscore=self._calculate_veriscore(consensus),
            reasoning=consensus.reasoning,
            evidence=[],
            sources=[r.sources[0] if r.sources else "" for r in consensus.individual_results[:5]],
            domain=domain.value,
            domain_confidence=0.8,
            model_count=consensus.model_count,
            model_verdicts=[
                {
                    "provider": r.provider,
                    "verdict": r.verdict,
                    "confidence": r.confidence
                }
                for r in consensus.individual_results
            ],
            agreement_percentage=consensus.agreement_percentage
        )
    
    async def _verify_with_specialists(
        self,
        claim: str,
        domain: VerificationDomain
    ) -> UnifiedVerificationResult:
        """Verification using specialized domain models"""
        if not self.specialists:
            return await self._verify_standard(claim, VerificationMode.STANDARD, domain)
        
        # Get specialist for domain
        specialist_result = await self.specialists.verify_claim(claim, domain=domain.value)
        
        # Also run standard verification for comparison
        standard_result = await self._verify_standard(claim, VerificationMode.STANDARD, domain)
        
        # Merge results, prioritizing specialist
        return UnifiedVerificationResult(
            claim=claim,
            verdict=specialist_result.verdict if specialist_result.confidence > 70 else standard_result.verdict,
            confidence=max(specialist_result.confidence, standard_result.confidence),
            veriscore=self._calculate_veriscore_from_result(specialist_result),
            reasoning=f"[Expert: {domain.value}] {specialist_result.reasoning}",
            evidence=specialist_result.raw_response.get("sources", []) if specialist_result.raw_response else [],
            sources=specialist_result.sources or [],
            domain=domain.value,
            domain_confidence=0.95,
            model_count=standard_result.model_count + 1,
            model_verdicts=standard_result.model_verdicts + [{
                "provider": f"specialist_{domain.value}",
                "verdict": specialist_result.verdict,
                "confidence": specialist_result.confidence
            }],
            agreement_percentage=standard_result.agreement_percentage
        )
    
    async def _verify_with_free_providers(
        self,
        claim: str
    ) -> UnifiedVerificationResult:
        """Verification using free providers (Wikipedia, arXiv, PubMed, etc.)"""
        if not self.free_providers:
            return self._create_error_result(claim, "Free providers not available")
        
        try:
            result = await self.free_providers.verify_claim(claim)
            
            # Parse verdict from result
            verdict = result.get("verdict", "UNVERIFIABLE")
            if isinstance(verdict, dict):
                verdict = verdict.get("verdict", "UNVERIFIABLE")
            
            # Extract confidence
            confidence = result.get("confidence", 50)
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except:
                    confidence = 50
            
            return UnifiedVerificationResult(
                claim=claim,
                verdict=str(verdict),
                confidence=float(confidence),
                veriscore=confidence * 0.9,
                reasoning=result.get("reasoning", result.get("analysis", "")),
                evidence=result.get("raw_evidence", {}),
                sources=result.get("evidence_sources", []),
                domain="general",
                domain_confidence=0.7,
                model_count=len(result.get("evidence_sources", [])),
                model_verdicts=[{
                    "provider": "free_providers",
                    "verdict": str(verdict),
                    "confidence": float(confidence)
                }],
                agreement_percentage=confidence
            )
        except Exception as e:
            return self._create_error_result(claim, f"Free provider verification failed: {e}")
    
    async def _verify_ultimate(
        self,
        claim: str,
        domain: VerificationDomain,
        include_blockchain: bool
    ) -> UnifiedVerificationResult:
        """Ultimate verification using ALL available resources:
        - Commercial AI providers (OpenAI, Anthropic, Google, Groq, etc.)
        - Specialized domain models (BioGPT, FinBERT, LegalBERT, etc.)
        - Free providers (Wikipedia, arXiv, PubMed, etc.)
        """
        tasks = []
        
        # Standard verification (commercial models)
        tasks.append(self._verify_standard(claim, VerificationMode.THOROUGH, domain))
        
        # Specialist verification (18 domain models)
        if self.specialists:
            tasks.append(self._verify_with_specialists(claim, domain))
        
        # Free providers verification (33 free APIs)
        if self.free_providers:
            tasks.append(self._verify_with_free_providers(claim))
        
        # Also run specialized models directly if available in ALL_AI_MODELS
        try:
            from providers.ai_models.all_models import get_specialized_model_names, ALL_AI_MODELS
            specialized_names = get_specialized_model_names()
            
            # Get domain-relevant specialized models
            domain_models = {
                "medical": ["biogpt", "pubmedbert", "biobert"],
                "legal": ["legalbert", "caselawbert"],
                "financial": ["finbert", "fingpt", "econbert"],
                "scientific": ["scibert", "galactica"],
                "climate": ["climatebert"],
                "technology": ["techbert", "securitybert"],
                "politics": ["polibert", "votebert"],
            }
            relevant_models = domain_models.get(domain.value, ["scibert", "wikipedia"])
            
            for model_name in relevant_models:
                if model_name in ALL_AI_MODELS:
                    tasks.append(self._run_single_model(claim, model_name))
        except ImportError:
            pass
        
        # Run all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        valid_results = [r for r in results if isinstance(r, UnifiedVerificationResult)]
        
        if not valid_results:
            return self._create_error_result(claim, "All verification methods failed")
        
        # Aggregate results
        final_verdict = self._aggregate_verdicts([r.verdict for r in valid_results])
        total_models = sum(r.model_count for r in valid_results)
        all_model_verdicts = []
        for r in valid_results:
            all_model_verdicts.extend(r.model_verdicts)
        
        avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        
        return UnifiedVerificationResult(
            claim=claim,
            verdict=final_verdict,
            confidence=avg_confidence,
            veriscore=self._calculate_ultimate_veriscore(valid_results),
            reasoning=self._merge_reasoning(valid_results),
            evidence=valid_results[0].evidence,
            sources=list(set(s for r in valid_results for s in r.sources)),
            domain=domain.value,
            domain_confidence=0.95,
            model_count=total_models,
            model_verdicts=all_model_verdicts,
            agreement_percentage=self._calculate_agreement(all_model_verdicts)
        )
    
    async def _run_single_model(
        self,
        claim: str,
        model_name: str
    ) -> UnifiedVerificationResult:
        """Run a single model from ALL_AI_MODELS"""
        try:
            from providers.ai_models.all_models import ALL_AI_MODELS
            
            adapter_factory = ALL_AI_MODELS.get(model_name)
            if not adapter_factory:
                return self._create_error_result(claim, f"Model {model_name} not found")
            
            # Create adapter instance
            if callable(adapter_factory):
                adapter = adapter_factory()
            else:
                adapter = adapter_factory
            
            # Run verification
            result = await adapter.verify_claim_with_retry(claim)
            
            return UnifiedVerificationResult(
                claim=claim,
                verdict=result.verdict,
                confidence=result.confidence,
                veriscore=result.confidence * 0.9,
                reasoning=result.reasoning,
                evidence={},
                sources=result.sources if hasattr(result, 'sources') and result.sources else [],
                domain="general",
                domain_confidence=0.8,
                model_count=1,
                model_verdicts=[{
                    "provider": model_name,
                    "verdict": result.verdict,
                    "confidence": result.confidence
                }],
                agreement_percentage=result.confidence
            )
        except Exception as e:
            return self._create_error_result(claim, f"Model {model_name} failed: {e}")
    
    async def _check_existing_verification(self, claim: str) -> Optional[UnifiedVerificationResult]:
        """Check if claim has been verified recently"""
        if not self.claims_db:
            return None
        
        try:
            existing = await self.claims_db.search_claim(claim)
            if existing and existing.get("verified_at"):
                # Return cached if less than 24 hours old
                return None  # For now, always reverify
        except:
            pass
        return None
    
    async def _record_to_blockchain(self, claim: str, result: UnifiedVerificationResult) -> str:
        """Record verification to blockchain"""
        if not self.blockchain:
            return ""
        
        data = {
            "claim_hash": hashlib.sha256(claim.encode()).hexdigest(),
            "verdict": result.verdict,
            "confidence": result.confidence,
            "model_count": result.model_count,
            "timestamp": result.timestamp
        }
        
        return await self.blockchain.add_verification(data)
    
    async def _award_points(self, user_id: str, result: UnifiedVerificationResult) -> int:
        """Award gamification points"""
        if not self.gamification:
            return 0
        
        base_points = 10
        if result.confidence >= 90:
            base_points += 5
        if result.model_count >= 10:
            base_points += 5
        
        await self.gamification.award_points(user_id, base_points, "verification")
        return base_points
    
    async def _store_verification(self, claim: str, result: UnifiedVerificationResult):
        """Store verification in claims database"""
        if not self.claims_db:
            return
        
        await self.claims_db.store_claim(
            claim=claim,
            verdict=result.verdict,
            confidence=result.confidence,
            sources=result.sources,
            model_count=result.model_count
        )
    
    async def _track_analytics(self, result: UnifiedVerificationResult):
        """Track analytics for verification"""
        if not self.analytics:
            return
        
        await self.analytics.track_event("verification", {
            "verdict": result.verdict,
            "confidence": result.confidence,
            "model_count": result.model_count,
            "processing_time_ms": result.processing_time_ms
        })
    
    def _calculate_veriscore(self, consensus: 'ConsensusResult') -> float:
        """Calculate VeriScore from consensus"""
        base_score = consensus.confidence
        agreement_bonus = (consensus.agreement_percentage - 50) * 0.3
        model_bonus = min(consensus.model_count * 2, 10)
        return min(100, base_score + agreement_bonus + model_bonus)
    
    def _calculate_veriscore_from_result(self, result: 'VerificationResult') -> float:
        """Calculate VeriScore from single result"""
        return result.confidence
    
    def _calculate_ultimate_veriscore(self, results: List[UnifiedVerificationResult]) -> float:
        """Calculate VeriScore from multiple results"""
        if not results:
            return 0
        return sum(r.veriscore for r in results) / len(results)
    
    def _aggregate_verdicts(self, verdicts: List[str]) -> str:
        """Aggregate multiple verdicts"""
        if not verdicts:
            return "UNVERIFIABLE"
        
        counts = {}
        for v in verdicts:
            counts[v] = counts.get(v, 0) + 1
        
        return max(counts, key=counts.get)
    
    def _merge_reasoning(self, results: List[UnifiedVerificationResult]) -> str:
        """Merge reasoning from multiple results"""
        if not results:
            return ""
        
        reasonings = [r.reasoning for r in results if r.reasoning]
        return " | ".join(reasonings[:3])
    
    def _calculate_agreement(self, verdicts: List[Dict]) -> float:
        """Calculate agreement percentage"""
        if not verdicts:
            return 0
        
        counts = {}
        for v in verdicts:
            verdict = v.get("verdict", "UNKNOWN")
            counts[verdict] = counts.get(verdict, 0) + 1
        
        max_count = max(counts.values())
        return (max_count / len(verdicts)) * 100
    
    def _create_error_result(self, claim: str, error: str) -> UnifiedVerificationResult:
        """Create error result"""
        return UnifiedVerificationResult(
            claim=claim,
            verdict="ERROR",
            confidence=0,
            veriscore=0,
            reasoning=error,
            evidence=[],
            sources=[],
            domain="general",
            domain_confidence=0,
            model_count=0,
            model_verdicts=[],
            agreement_percentage=0
        )
    
    # ============================================================
    # ADDITIONAL METHODS
    # ============================================================
    
    async def search_sources(self, query: str) -> List[Dict]:
        """Search for sources"""
        if self.master and hasattr(self.master, 'data_aggregator'):
            results = await self.master.data_aggregator.search_priority(
                query,
                priority_sources=['wikipedia', 'arxiv', 'newsapi'],
                max_results=10
            )
            return [{"url": r.url, "title": r.title} for r in results if r]
        return []
    
    async def analyze_media(self, url_or_data: Union[str, bytes]) -> Dict:
        """Analyze media for deepfakes"""
        if not self.deepfake_detector:
            return {"error": "Deepfake detector not available"}
        
        if isinstance(url_or_data, str):
            # Assume URL, fetch data
            return {"status": "url_analysis_not_implemented"}
        
        result = await self.deepfake_detector.analyze_image(url_or_data)
        return result.__dict__
    
    async def verify_with_experts(self, claim: str) -> Dict:
        """Verify with domain experts"""
        return await self._verify_with_specialists(
            claim,
            VerificationDomain.GENERAL
        ).__dict__
    
    async def get_claim_history(self, claim: str) -> Dict:
        """Get claim verification history"""
        if not self.claims_db:
            return {"error": "Claims database not available"}
        
        history = await self.claims_db.get_claim_history(claim)
        return history or {}
    
    async def send_notification(
        self,
        platform: str,
        message: str,
        channel: Optional[str] = None
    ):
        """Send notification via integration"""
        if not self.integrations:
            return {"error": "Integrations not available"}
        
        return await self.integrations.send_notification(platform, message, channel)
    
    async def close(self):
        """Cleanup all resources"""
        if self.master:
            await self.master.close()
        if self.specialists:
            await self.specialists.close()
        if self.collaboration:
            await self.collaboration.shutdown()
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "mode": self.mode.value,
            "total_verifications": self.total_verifications,
            "total_cost": self.total_cost,
            "components": {
                "master_orchestrator": self.master is not None,
                "specialized_models": self.specialists is not None,
                "integrations": self.integrations is not None,
                "collaboration": self.collaboration is not None,
                "analytics": self.analytics is not None,
                "claims_db": self.claims_db is not None,
                "deepfake_detector": self.deepfake_detector is not None,
                "blockchain": self.blockchain is not None,
                "gamification": self.gamification is not None,
                "langchain_available": LANGCHAIN_AVAILABLE,
                "langchain_chains": len(self.chains.chains) if self.chains else 0
            }
        }


# ============================================================
# FASTAPI INTEGRATION
# ============================================================

def create_unified_router():
    """Create FastAPI router for unified orchestrator"""
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    
    router = APIRouter(prefix="/unified", tags=["Unified Orchestrator"])
    
    # Singleton orchestrator
    _orchestrator = None
    
    def get_orchestrator() -> UnifiedOrchestrator:
        nonlocal _orchestrator
        if _orchestrator is None:
            _orchestrator = UnifiedOrchestrator(mode=VerificationMode.STANDARD)
        return _orchestrator
    
    class VerifyRequest(BaseModel):
        claim: str
        mode: str = "standard"
        domain: Optional[str] = None
        include_blockchain: bool = False
        user_id: Optional[str] = None
    
    @router.post("/verify")
    async def verify_claim(req: VerifyRequest):
        orchestrator = get_orchestrator()
        
        mode = VerificationMode(req.mode) if req.mode in [m.value for m in VerificationMode] else VerificationMode.STANDARD
        domain = VerificationDomain(req.domain) if req.domain and req.domain in [d.value for d in VerificationDomain] else None
        
        result = await orchestrator.verify_claim(
            claim=req.claim,
            mode=mode,
            domain=domain,
            include_blockchain=req.include_blockchain,
            user_id=req.user_id
        )
        
        return result.__dict__
    
    @router.get("/status")
    async def get_status():
        orchestrator = get_orchestrator()
        return orchestrator.get_status()
    
    @router.post("/analyze-media")
    async def analyze_media(url: str):
        orchestrator = get_orchestrator()
        return await orchestrator.analyze_media(url)
    
    @router.get("/claim-history/{claim_hash}")
    async def get_claim_history(claim_hash: str):
        orchestrator = get_orchestrator()
        return await orchestrator.get_claim_history(claim_hash)
    
    return router


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def main():
    """Example usage"""
    print("=" * 60)
    print("VERITY UNIFIED LANGCHAIN ORCHESTRATOR")
    print("=" * 60)
    
    # Initialize
    orchestrator = UnifiedOrchestrator(mode=VerificationMode.STANDARD)
    
    print("\nOrchestrator Status:")
    status = orchestrator.get_status()
    for key, value in status["components"].items():
        icon = "✅" if value else "❌"
        print(f"  {icon} {key}: {value}")
    
    # Test verification
    test_claim = "The Earth orbits around the Sun"
    print(f"\nVerifying: {test_claim}")
    
    result = await orchestrator.verify_claim(test_claim)
    
    print(f"\nResult:")
    print(f"  Verdict: {result.verdict}")
    print(f"  Confidence: {result.confidence:.1f}%")
    print(f"  VeriScore: {result.veriscore:.1f}")
    print(f"  Models Used: {result.model_count}")
    print(f"  Processing Time: {result.processing_time_ms}ms")
    
    # Cleanup
    await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(main())
