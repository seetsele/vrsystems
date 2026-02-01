"""
PART 3: LANGCHAIN MASTER ORCHESTRATOR - COMPLETE IMPLEMENTATION
Coordinates all 50+ AI models for fact-checking with intelligent routing
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment from repo `python-tools/.env` if present so API keys are available
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOTENV_PATH = os.path.join(ROOT, 'python-tools', '.env')
if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

# Ensure project root is on sys.path so top-level packages like `providers` are importable
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Prefer numpy when available but provide a lightweight fallback for environments
# without numpy (useful for local smoke tests).
try:
    import numpy as np
except Exception:
    import statistics as _stats

    class _NPFallback:
        @staticmethod
        def mean(x):
            if not x:
                return 0.0
            return float(_stats.mean(x))

        @staticmethod
        def std(x):
            if not x:
                return 0.0
            # population std deviation to match numpy.std default
            return float(_stats.pstdev(x))

    np = _NPFallback()

try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_core.language_models import BaseLLM
    from langchain_core.callbacks import CallbackManager
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_cohere import ChatCohere
except Exception:
    LLMChain = None
    PromptTemplate = None
    BaseLLM = object
    CallbackManager = None
    ChatOpenAI = ChatAnthropic = ChatGoogleGenerativeAI = ChatGroq = ChatCohere = None

from providers.base_provider import VerificationResult
from providers.ai_models.all_models import ALL_AI_MODELS, create_provider
from providers.data_sources.all_sources import DataSourceAggregator

# Import unified data providers for comprehensive fact-checking
try:
    from providers.unified_data_providers import (
        MasterDataProviderAggregator,
        UnifiedFactCheckers,
        UnifiedAcademicSources,
        UnifiedKnowledgeBases,
        UnifiedSearchEngines,
        DataSourceResult
    )
    UNIFIED_PROVIDERS_AVAILABLE = True
except ImportError:
    UNIFIED_PROVIDERS_AVAILABLE = False
    MasterDataProviderAggregator = None


@dataclass
class VerificationConfig:
    """Configuration for verification process"""
    min_models: int = 3
    max_models: int = 10
    confidence_threshold: float = 70.0
    consensus_threshold: float = 0.6
    use_free_models_first: bool = True
    enable_reasoning_chain: bool = True
    enable_source_verification: bool = True
    max_cost_per_claim: float = 0.10
    timeout_seconds: int = 30


@dataclass
class ConsensusResult:
    """Aggregated result from multiple models"""
    final_verdict: str
    confidence: float
    reasoning: str
    model_count: int
    agreement_percentage: float
    individual_results: List[VerificationResult]
    total_cost: float
    total_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelSelector:
    """Intelligent model selection based on claim characteristics"""
    
    # Domain keywords for specialized model selection
    DOMAIN_KEYWORDS = {
        "medical": {
            "keywords": ["disease", "symptom", "treatment", "drug", "medication", "diagnosis", 
                        "cancer", "diabetes", "heart", "blood", "surgery", "hospital", "patient",
                        "health", "medical", "clinical", "vaccine", "therapy", "infection"],
            "models": ["biogpt", "pubmedbert", "biobert", "nutritionbert"],
            "free_sources": ["pubmed"]
        },
        "legal": {
            "keywords": ["law", "legal", "court", "judge", "statute", "regulation", "contract",
                        "lawsuit", "attorney", "plaintiff", "defendant", "verdict", "ruling"],
            "models": ["legalbert", "caselawbert"],
            "free_sources": ["wikipedia"]
        },
        "financial": {
            "keywords": ["stock", "market", "investment", "earnings", "revenue", "profit",
                        "bank", "interest rate", "inflation", "gdp", "economy", "fiscal",
                        "monetary", "treasury", "fed", "sec", "trading", "bond", "equity"],
            "models": ["finbert", "fingpt", "econbert"],
            "free_sources": ["wikipedia"]
        },
        "scientific": {
            "keywords": ["research", "study", "experiment", "hypothesis", "theory", "evidence",
                        "peer-reviewed", "journal", "publication", "methodology", "data",
                        "physics", "chemistry", "biology", "mathematics", "quantum"],
            "models": ["scibert", "galactica"],
            "free_sources": ["arxiv", "pubmed"]
        },
        "climate": {
            "keywords": ["climate", "global warming", "greenhouse", "carbon", "emissions",
                        "temperature", "sea level", "arctic", "weather", "renewable",
                        "fossil fuel", "paris agreement", "ipcc", "environmental"],
            "models": ["climatebert"],
            "free_sources": ["arxiv", "wikipedia"]
        },
        "technology": {
            "keywords": ["software", "hardware", "programming", "algorithm", "cybersecurity",
                        "hack", "vulnerability", "malware", "encryption", "data breach"],
            "models": ["techbert", "securitybert"],
            "free_sources": ["arxiv", "wikipedia"]
        },
        "politics": {
            "keywords": ["president", "congress", "senate", "election", "vote", "democrat",
                        "republican", "legislation", "policy", "government", "political"],
            "models": ["polibert", "votebert"],
            "free_sources": ["wikipedia"]
        },
        "sports": {
            "keywords": ["game", "match", "score", "championship", "league", "tournament",
                        "player", "team", "coach", "season", "athlete", "olympics"],
            "models": ["sportsbert"],
            "free_sources": ["wikipedia"]
        },
        "geography": {
            "keywords": ["country", "city", "population", "capital", "border", "continent",
                        "ocean", "river", "mountain", "geography", "nation", "territory"],
            "models": ["geobert"],
            "free_sources": ["wikipedia"]
        },
        "history": {
            "keywords": ["history", "historical", "century", "war", "revolution", "ancient",
                        "medieval", "empire", "civilization", "treaty", "era", "period"],
            "models": ["historybert"],
            "free_sources": ["wikipedia"]
        }
    }
    
    def __init__(self, config: VerificationConfig):
        self.config = config
        # Check if specialized models are available
        self._specialized_available = False
        try:
            from providers.ai_models.specialized_models import SPECIALIZED_MODELS
            self._specialized_models = SPECIALIZED_MODELS
            self._specialized_available = True
        except ImportError:
            self._specialized_models = {}
        
        # Check if free providers are available
        self._free_providers_available = False
        try:
            from providers.ai_models.all_models import get_free_model_names
            self._free_models = get_free_model_names()
            self._free_providers_available = True
        except ImportError:
            self._free_models = []
    
    def _detect_domain(self, claim: str) -> tuple:
        """Detect claim domain and return (domain, specialized_models, free_sources, confidence)"""
        claim_lower = claim.lower()
        domain_scores = {}
        
        for domain, config in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in config["keywords"] if kw in claim_lower)
            if score > 0:
                domain_scores[domain] = (score, config["models"], config.get("free_sources", []))
        
        if not domain_scores:
            return None, [], [], 0.0
        
        best_domain = max(domain_scores.items(), key=lambda x: x[1][0])
        domain_name = best_domain[0]
        score, models, free_sources = best_domain[1]
        confidence = min(0.95, 0.4 + (score * 0.15))
        
        return domain_name, models, free_sources, confidence
        
    def select_models(self, claim: str, context: Optional[Dict] = None) -> List[str]:
        """Select optimal models for a given claim"""
        
        # Analyze claim characteristics
        claim_length = len(claim.split())
        complexity = self._estimate_complexity(claim)
        requires_search = self._requires_web_search(claim)
        
        # Detect domain for specialized models
        detected_domain, specialized_models, free_sources, domain_confidence = self._detect_domain(claim)
        
        selected = []
        
        # ALWAYS add free providers first (no cost)
        if self._free_providers_available:
            selected.extend(["wikipedia", "free_providers"])
            # Add domain-specific free sources
            if free_sources:
                selected.extend(free_sources)
        
        # Add specialized models if domain detected and available
        if detected_domain and self._specialized_available and domain_confidence > 0.5:
            for model_name in specialized_models:
                if model_name in self._specialized_models or model_name in ALL_AI_MODELS:
                    selected.append(model_name)
            print(f"[INFO] Detected domain: {detected_domain} (confidence: {domain_confidence:.0%})")
            print(f"[INFO] Using specialized models: {specialized_models}")
            if free_sources:
                print(f"[INFO] Using free sources: {free_sources}")
        
        if self.config.use_free_models_first:
            # Start with fast, free models
            selected.extend([
                "groq_llama33_70b",
                "groq_mixtral_8x7b",
                "groq_deepseek_r1",
                "ollama_llama33_70b",
                "ollama_qwen25_72b"
            ])
        
        # Add search-augmented model if needed
        if requires_search:
            selected.append("perplexity_sonar")
        
        # Add premium models for complex claims
        if complexity > 0.7:
            selected.extend([
                "openai_gpt4o",
                "anthropic_claude_opus_4",
                "google_gemini_pro"
            ])
        elif complexity > 0.4:
            selected.extend([
                "anthropic_claude_sonnet_4",
                "openai_gpt4o_mini"
            ])
        
        # Add diversity with different model architectures
        selected.extend([
            "cohere_command_r_plus",
            "ollama_mistral_large",
            "together_llama3_70b"
        ])
        
        # Ensure we have between min and max models
        selected = list(dict.fromkeys(selected))  # Remove duplicates
        selected = selected[:self.config.max_models]
        
        if len(selected) < self.config.min_models:
            # Add more free models to reach minimum
            free_models = [k for k in ALL_AI_MODELS.keys() if 'ollama' in k or 'groq' in k]
            selected.extend(free_models[:self.config.min_models - len(selected)])
        
        return selected[:self.config.max_models]
    
    def _estimate_complexity(self, claim: str) -> float:
        """Estimate claim complexity (0-1)"""
        factors = []
        
        # Length factor
        word_count = len(claim.split())
        factors.append(min(word_count / 100, 1.0))
        
        # Technical terms
        technical_terms = ['quantum', 'algorithm', 'molecular', 'statistical', 'genetic']
        tech_count = sum(1 for term in technical_terms if term.lower() in claim.lower())
        factors.append(min(tech_count / 3, 1.0))
        
        # Numbers and dates (often require verification)
        import re
        numbers = len(re.findall(r'\d+', claim))
        factors.append(min(numbers / 5, 1.0))
        
        return np.mean(factors)
    
    def _requires_web_search(self, claim: str) -> bool:
        """Check if claim requires web search"""
        search_indicators = [
            'current', 'today', 'recent', 'latest', 'now',
            '2024', '2025', 'this year', 'this month'
        ]
        return any(indicator in claim.lower() for indicator in search_indicators)


class VerdictAggregator:
    """Aggregate verdicts from multiple models using advanced consensus algorithms"""
    
    VERDICT_WEIGHTS = {
        'TRUE': 1.0,
        'FALSE': -1.0,
        'MISLEADING': -0.5,
        'UNVERIFIABLE': 0.0,
        'ERROR': 0.0
    }
    
    def aggregate(self, results: List[VerificationResult]) -> ConsensusResult:
        """Aggregate multiple verification results into consensus"""
        
        if not results:
            return self._create_error_result("No results to aggregate")
        
        # Filter out errors
        valid_results = [r for r in results if r.verdict != 'ERROR']
        
        if not valid_results:
            return self._create_error_result("All models returned errors")
        
        # Calculate weighted scores
        weighted_scores = []
        for result in valid_results:
            weight = self.VERDICT_WEIGHTS.get(result.verdict, 0.0)
            confidence_weight = result.confidence / 100.0
            weighted_scores.append(weight * confidence_weight)
        
        # Calculate consensus
        avg_score = np.mean(weighted_scores)
        std_score = np.std(weighted_scores)
        
        # Determine final verdict
        if avg_score > 0.5:
            final_verdict = 'TRUE'
        elif avg_score < -0.5:
            final_verdict = 'FALSE'
        elif avg_score < -0.2:
            final_verdict = 'MISLEADING'
        else:
            final_verdict = 'UNVERIFIABLE'
        
        # Calculate agreement percentage
        verdict_counts = {}
        for result in valid_results:
            verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1
        
        max_count = max(verdict_counts.values())
        agreement = (max_count / len(valid_results)) * 100
        
        # Calculate final confidence
        base_confidence = abs(avg_score) * 100
        agreement_bonus = (agreement - 50) * 0.5  # Bonus for high agreement
        uncertainty_penalty = std_score * 20  # Penalty for high disagreement
        
        final_confidence = max(0, min(100, base_confidence + agreement_bonus - uncertainty_penalty))
        
        # Synthesize reasoning
        reasoning = self._synthesize_reasoning(valid_results, final_verdict)
        
        # Calculate totals
        total_cost = sum(r.cost for r in results)
        total_time = max(r.response_time for r in results)
        
        return ConsensusResult(
            final_verdict=final_verdict,
            confidence=final_confidence,
            reasoning=reasoning,
            model_count=len(valid_results),
            agreement_percentage=agreement,
            individual_results=valid_results,
            total_cost=total_cost,
            total_time=total_time
        )
    
    def _synthesize_reasoning(self, results: List[VerificationResult], verdict: str) -> str:
        """Synthesize reasoning from multiple models"""
        
        # Get reasoning from models that agree with final verdict
        supporting_reasoning = [
            r.reasoning for r in results 
            if r.verdict == verdict and r.reasoning
        ]
        
        if not supporting_reasoning:
            supporting_reasoning = [r.reasoning for r in results if r.reasoning]
        
        if not supporting_reasoning:
            return f"Based on {len(results)} models, verdict: {verdict}"
        
        # Extract key points (simple approach - could use LLM for better synthesis)
        all_reasoning = " ".join(supporting_reasoning)
        
        # Truncate if too long
        if len(all_reasoning) > 500:
            all_reasoning = all_reasoning[:500] + "..."
        
        return f"Consensus from {len(results)} models: {all_reasoning}"
    
    def _create_error_result(self, message: str) -> ConsensusResult:
        """Create error consensus result"""
        return ConsensusResult(
            final_verdict='ERROR',
            confidence=0.0,
            reasoning=message,
            model_count=0,
            agreement_percentage=0.0,
            individual_results=[],
            total_cost=0.0,
            total_time=0.0
        )


class LangChainMasterOrchestrator:
    """
    Master orchestrator that coordinates all AI models using LangChain
    Implements intelligent routing, consensus, and cost optimization
    """
    def __init__(self, config: Optional[VerificationConfig] = None):
        self.config = config or VerificationConfig()
        self.selector = ModelSelector(self.config)
        self.aggregator = VerdictAggregator()
        self.data_aggregator = DataSourceAggregator()
        
        # Initialize unified data providers for comprehensive fact-checking
        if UNIFIED_PROVIDERS_AVAILABLE:
            self.unified_providers = MasterDataProviderAggregator()
        else:
            self.unified_providers = None
            
        # Cache for instantiated provider adapters to avoid repeated init
        # Key: model_name -> provider instance
        self.model_cache: Dict[str, Any] = {}
        self.total_cost = 0.0

    # Provider registration / caching helpers
    def get_cached_provider(self, model_name: str) -> Optional[Any]:
        """Return a cached provider instance if available."""
        return self.model_cache.get(model_name)

    def register_provider(self, model_name: str, cache: bool = True) -> Optional[Any]:
        """Attempt to create and optionally cache a provider adapter.

        This method intentionally performs a lightweight, best-effort
        instantiation: failures are caught and logged rather than
        propagated so startup isn't blocked by optional providers.
        """
        try:
            provider = create_provider(model_name)
            if cache and provider is not None:
                self.model_cache[model_name] = provider
            return provider
        except Exception as e:
            print(f"[WARN] register_provider failed for {model_name}: {e}")
            return None

    def register_all_providers(self, model_names: Optional[List[str]] = None, max_register: Optional[int] = 50) -> List[str]:
        """Register a batch of providers by name and return the list of successfully registered names.

        By default this will attempt to register all providers discovered in ALL_AI_MODELS,
        but callers can provide a smaller list to limit startup work. The optional
        `max_register` parameter prevents accidentally attempting to instantiate
        an extremely large list at once.
        """
        if model_names is None:
            model_names = list(ALL_AI_MODELS.keys())

        registered = []
        for i, name in enumerate(model_names):
            if max_register is not None and i >= max_register:
                break
            prov = self.register_provider(name, cache=True)
            if prov is not None:
                registered.append(name)
        return registered
        
    async def verify_claim(
        self,
        claim: str,
        context: Optional[Dict] = None,
        selected_models: Optional[List[str]] = None
    ) -> ConsensusResult:
        """
        Verify a claim using multiple AI models and return consensus
        
        Args:
            claim: The claim to verify
            context: Optional context about the claim
            selected_models: Optional list of specific models to use
            
        Returns:
            ConsensusResult with aggregated verdict
        """
        
        # Select models if not provided
        if not selected_models:
            selected_models = self.selector.select_models(claim, context)
        
        print(f"Verifying claim with {len(selected_models)} models...")
        print(f"Models: {', '.join(selected_models[:5])}{'...' if len(selected_models) > 5 else ''}")
        
        # Initialize providers via factory to support callables/classes/fallbacks
        providers = []
        for model_name in selected_models:
            try:
                # Prefer cached provider instances when available
                provider = self.get_cached_provider(model_name)
                if provider is None:
                    provider = self.register_provider(model_name, cache=True)
                if provider is None:
                    raise RuntimeError("provider initialization returned None")
                providers.append(provider)
            except Exception as e:
                print(f"[WARN] Failed to initialize {model_name}: {e}")
        
        if not providers:
            return self.aggregator._create_error_result("No providers could be initialized")
        
        # If claim likely requires a web search, gather top sources and include
        sources_list = []
        if self.selector._requires_web_search(claim) and self.config.enable_source_verification:
            try:
                ds_results = await self.data_aggregator.search_priority(
                    claim,
                    priority_sources=['wikipedia', 'arxiv', 'newsapi', 'duckduckgo'],
                    max_results=5,
                )
                sources_list = [r.url for r in ds_results if r and getattr(r, 'url', None)]
            except Exception as e:
                    print(f"[WARN] Data source lookup failed: {e}")

        # Run verification in parallel with timeout
        try:
            results = await asyncio.wait_for(
                self._run_parallel_verification(providers, claim, sources=sources_list),
                timeout=self.config.timeout_seconds
            )
        except asyncio.TimeoutError:
            print(f"[WARN] Verification timeout after {self.config.timeout_seconds}s")
            results = []
        
        # Check cost limit
        total_cost = sum(r.cost for r in results if r)
        self.total_cost = total_cost
        if total_cost > self.config.max_cost_per_claim:
            print(f"[WARN] Cost limit reached: ${total_cost:.4f}")
        
        # Aggregate results
        consensus = self.aggregator.aggregate(results)
        
        print(f"Consensus: {consensus.final_verdict} ({consensus.confidence:.1f}% confidence)")
        print(f"Total cost: ${consensus.total_cost:.4f}")
        print(f"Total time: {consensus.total_time:.2f}s")
        
        return consensus

    async def verify_claim_all_providers(self, claim: str, selected_models: Optional[List[str]] = None, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Run every provider adapter (or the selected set) and return raw dict results.

        Useful for upstream systems that require per-provider outputs (not aggregated).
        """
        if selected_models is None:
            selected_models = list(ALL_AI_MODELS.keys())

        providers = []
        for model_name in selected_models:
            try:
                provider = self.get_cached_provider(model_name)
                if provider is None:
                    provider = self.register_provider(model_name, cache=True)
                if provider is None:
                    raise RuntimeError("provider initialization returned None")
                providers.append(provider)
            except Exception as e:
                providers.append({'__init_error__': str(e), 'model': model_name})

        async def _call_provider(p):
            if isinstance(p, dict):
                return {
                    'provider': p.get('model', 'unknown'),
                    'verdict': 'ERROR',
                    'confidence': 0.0,
                    'reasoning': p.get('__init_error__', 'init failed'),
                    'cost': 0.0,
                    'response_time': 0.0,
                    'raw_response': None
                }
            try:
                # forward sources if provided so per-provider calls can use them
                if sources:
                    res = await p.verify_claim_with_retry(claim, sources=sources)
                else:
                    res = await p.verify_claim_with_retry(claim)
                return {
                    'provider': getattr(res, 'provider', str(p)),
                    'verdict': getattr(res, 'verdict', 'UNVERIFIABLE'),
                    'confidence': float(getattr(res, 'confidence', 0.0)),
                    'reasoning': getattr(res, 'reasoning', ''),
                    'cost': float(getattr(res, 'cost', 0.0)),
                    'response_time': float(getattr(res, 'response_time', 0.0)),
                    'raw_response': getattr(res, 'raw_response', None)
                }
            except Exception as e:
                return {
                    'provider': getattr(p, '__class__', type(p)).__name__,
                    'verdict': 'ERROR',
                    'confidence': 0.0,
                    'reasoning': str(e),
                    'cost': 0.0,
                    'response_time': 0.0,
                    'raw_response': None
                }

        tasks = [_call_provider(p) for p in providers]
        results = await asyncio.gather(*tasks)
        try:
            self.total_cost = sum(r.get('cost', 0.0) for r in results if isinstance(r, dict))
        except Exception:
            pass
        return results
    
    async def _run_parallel_verification(
        self,
        providers: List[Any],
        claim: str
        , sources: Optional[List[str]] = None
    ) -> List[VerificationResult]:
        """Run verification across all providers in parallel"""
        
        tasks = []
        for provider in providers:
            if sources:
                tasks.append(provider.verify_claim_with_retry(claim, sources=sources))
            else:
                tasks.append(provider.verify_claim_with_retry(claim))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None values
        valid_results = []
        for result in results:
            if isinstance(result, VerificationResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"⚠️ Model error: {result}")
        
        return valid_results
    
    async def verify_batch(
        self,
        claims: List[str],
        batch_size: int = 5
    ) -> List[ConsensusResult]:
        """Verify multiple claims in batches"""
        
        results = []
        
        for i in range(0, len(claims), batch_size):
            batch = claims[i:i+batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1} ({len(batch)} claims)...")
            
            batch_tasks = [self.verify_claim(claim) for claim in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Brief pause between batches
            if i + batch_size < len(claims):
                await asyncio.sleep(1)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get orchestrator statistics"""
        stats = {
            "config": {
                "min_models": self.config.min_models,
                "max_models": self.config.max_models,
                "confidence_threshold": self.config.confidence_threshold,
                "max_cost_per_claim": self.config.max_cost_per_claim
            },
            "available_models": len(ALL_AI_MODELS)
        }
        
        # Add unified provider statistics if available
        if self.unified_providers:
            stats["data_providers"] = self.unified_providers.get_all_available_providers()
            stats["total_data_providers"] = self.unified_providers.get_provider_count()
        
        return stats

    async def comprehensive_verify(
        self,
        claim: str,
        entities: List[str] = None,
        use_all_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive verification using ALL available data sources:
        - AI Models (GPT-4, Claude, Gemini, etc.)
        - Fact-Checkers (Snopes, PolitiFact, FactCheck.org, etc.)
        - Academic Sources (PubMed, arXiv, Semantic Scholar, etc.)
        - Knowledge Bases (Wikipedia, Wikidata)
        - Search Engines (DuckDuckGo, Brave)
        
        Returns a comprehensive report with verdicts from all sources.
        """
        results = {
            "claim": claim,
            "ai_consensus": None,
            "fact_checker_results": [],
            "academic_results": [],
            "knowledge_base_results": [],
            "search_results": [],
            "unified_consensus": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. Get AI model consensus
        ai_result = await self.verify_claim(claim)
        results["ai_consensus"] = {
            "verdict": ai_result.final_verdict,
            "confidence": ai_result.confidence,
            "agreement": ai_result.agreement_percentage,
            "model_count": ai_result.model_count,
            "reasoning": ai_result.reasoning
        }
        
        # 2. Query unified data providers if available
        if self.unified_providers and use_all_sources:
            try:
                data_results = await self.unified_providers.comprehensive_check(
                    claim=claim,
                    entities=entities,
                    include_fact_checkers=True,
                    include_academic=True,
                    include_knowledge=True,
                    include_search=True
                )
                
                # Convert results
                for category, cat_results in data_results.items():
                    key_map = {
                        'fact_checkers': 'fact_checker_results',
                        'academic': 'academic_results',
                        'knowledge_bases': 'knowledge_base_results',
                        'search': 'search_results'
                    }
                    
                    if category in key_map:
                        results[key_map[category]] = [
                            {
                                'provider': r.provider,
                                'verdict': r.verdict,
                                'confidence': r.confidence,
                                'reasoning': r.reasoning,
                                'source_url': r.source_url
                            }
                            for r in cat_results
                        ]
                
                # Get unified consensus from data providers
                data_consensus = self.unified_providers.aggregate_verdicts(data_results)
                results["data_consensus"] = data_consensus
                
            except Exception as e:
                print(f"[WARN] Unified providers check failed: {e}")
        
        # 3. Calculate overall unified consensus
        all_verdicts = []
        all_confidences = []
        
        # Add AI consensus
        if results["ai_consensus"]:
            all_verdicts.append(results["ai_consensus"]["verdict"])
            all_confidences.append(results["ai_consensus"]["confidence"])
        
        # Add data provider results
        for key in ["fact_checker_results", "academic_results", "knowledge_base_results"]:
            for r in results.get(key, []):
                if r["verdict"] != "UNVERIFIABLE":
                    all_verdicts.append(r["verdict"])
                    all_confidences.append(r["confidence"])
        
        # Calculate final unified verdict
        if all_verdicts:
            verdict_counts = {}
            for v in all_verdicts:
                verdict_counts[v] = verdict_counts.get(v, 0) + 1
            
            final_verdict = max(verdict_counts, key=verdict_counts.get)
            agreement = verdict_counts[final_verdict] / len(all_verdicts)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            results["unified_consensus"] = {
                "final_verdict": final_verdict,
                "confidence": min(95, avg_confidence * agreement),
                "agreement": agreement * 100,
                "total_sources": len(all_verdicts),
                "verdict_breakdown": verdict_counts
            }
        
        return results

    async def close(self):
        """Cleanup resources used by orchestrator"""
        try:
            await self.data_aggregator.close_all()
        except Exception:
            pass


# ============================================================
# ADVANCED LANGCHAIN CHAINS
# ============================================================

class ReasoningChain:
    """Chain-of-thought reasoning for complex claims"""
    def __init__(self, llm: BaseLLM = None):
        self.llm = llm

        # If LangChain is available, use LLMChain; otherwise fall back to provider-based call
        self.use_langchain = (LLMChain is not None and PromptTemplate is not None and llm is not None)
        if self.use_langchain:
            self.template = """You are a fact-checking expert. Break down this claim step-by-step:

Claim: {claim}

Step 1: Identify the key factual components
Step 2: Evaluate each component
Step 3: Consider context and nuance
Step 4: Reach a verdict

Respond in format:
VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE]
CONFIDENCE: [0-100]
REASONING: [detailed explanation]
"""
            self.prompt = PromptTemplate(template=self.template, input_variables=["claim"])
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        else:
            # Fallback: use a provider (OpenAI/GPT-3.5) if available
            try:
                from providers.ai_models.all_models import create_provider
                self.fallback_provider = create_provider('openai_gpt35_turbo')
            except Exception:
                self.fallback_provider = None

    async def analyze(self, claim: str) -> str:
        """Run chain-of-thought analysis using LangChain or fallback provider"""
        if self.use_langchain:
            result = await self.chain.arun(claim=claim)
            return result

        # Fallback behavior
        if self.fallback_provider:
            try:
                res = await self.fallback_provider.verify_claim_with_retry(claim)
                return getattr(res, 'reasoning', str(res))
            except Exception:
                return """VERDICT: UNVERIFIABLE\nCONFIDENCE: 0\nREASONING: Reasoning unavailable (fallback failed)"""

        return """VERDICT: UNVERIFIABLE\nCONFIDENCE: 0\nREASONING: Reasoning unavailable (no LLM configured)"""


class SourceVerificationChain:
    """Chain for verifying sources and citations"""
    def __init__(self, llm: BaseLLM = None):
        self.llm = llm
        self.use_langchain = (LLMChain is not None and PromptTemplate is not None and llm is not None)
        if self.use_langchain:
            self.template = """Analyze the credibility of these sources for the claim:

Claim: {claim}
Sources: {sources}

Evaluate:
1. Source reliability
2. Publication date relevance
3. Potential bias
4. Factual accuracy

Provide credibility score (0-100) and explanation.
"""
            self.prompt = PromptTemplate(template=self.template, input_variables=["claim", "sources"])
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        else:
            try:
                from providers.ai_models.all_models import create_provider
                self.fallback_provider = create_provider('openai_gpt35_turbo')
            except Exception:
                self.fallback_provider = None

    async def verify(self, claim: str, sources: List[str]) -> str:
        """Verify source credibility using LangChain or fallback provider"""
        if self.use_langchain:
            sources_text = "\n".join(f"- {s}" for s in sources)
            result = await self.chain.arun(claim=claim, sources=sources_text)
            return result

        if self.fallback_provider:
            try:
                prompt = f"Claim: {claim}\nSources:\n" + "\n".join(sources[:10])
                res = await self.fallback_provider.verify_claim_with_retry(prompt)
                return getattr(res, 'reasoning', str(res))
            except Exception:
                return "Credibility analysis unavailable (fallback failed)"

        return "Credibility analysis unavailable (no LLM configured)"


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def main():
    """Example usage of the orchestrator"""
    
    # Initialize orchestrator
    config = VerificationConfig(
        min_models=3,
        max_models=8,
        use_free_models_first=True,
        max_cost_per_claim=0.05
    )
    
    orchestrator = LangChainMasterOrchestrator(config)
    
    # Test claims
    test_claims = [
        "The Earth orbits around the Sun",
        "Water freezes at 0°C at sea level",
        "AI will replace all human jobs by 2030"
    ]
    
    # Verify single claim
    print("=" * 60)
    print("SINGLE CLAIM VERIFICATION")
    print("=" * 60)
    
    result = await orchestrator.verify_claim(test_claims[0])
    
    print(f"\nFinal Result:")
    print(f"  Verdict: {result.final_verdict}")
    print(f"  Confidence: {result.confidence:.1f}%")
    print(f"  Agreement: {result.agreement_percentage:.1f}%")
    print(f"  Models Used: {result.model_count}")
    print(f"  Reasoning: {result.reasoning[:200]}...")
    
    # Verify batch
    print("\n" + "=" * 60)
    print("BATCH VERIFICATION")
    print("=" * 60)
    
    batch_results = await orchestrator.verify_batch(test_claims)
    
    for claim, result in zip(test_claims, batch_results):
        print(f"\nClaim: {claim}")
        print(f"Verdict: {result.final_verdict} ({result.confidence:.1f}%)")

    # Cleanup resources
    await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())
