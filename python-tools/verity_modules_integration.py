"""
Verity Systems - Unified Modules Integration
=============================================
Integrates ALL available verity modules into a single powerful interface.

This module brings together:
1. Advanced NLP Analysis (fallacy detection, propaganda, bias)
2. Claim Similarity Engine (find related fact-checks)
3. Monte Carlo Confidence (probabilistic confidence intervals)
4. Source Credibility Database (credibility ratings)
5. Consensus Engine (multi-source voting)
6. Evidence Graph (knowledge graphs)
7. Numerical Verification (stats/numbers validation)
8. Temporal Reasoning (time-based verification)
9. Geospatial Reasoning (location verification)
10. Social Media Analyzer (viral claim tracking)
11. Adaptive Learning (self-improving AI)

This is the SECRET SAUCE that makes Verity unbeatable.

Author: Verity Systems
License: MIT
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import all the powerful modules
try:
    from verity_advanced_nlp import (
        ClaimAnalyzer as AdvancedNLPAnalyzer,  # Using ClaimAnalyzer as AdvancedNLPAnalyzer
        ClaimAnalysis,
        ExtractedEntity,
        LogicalFallacy,
        PropagandaTechnique,
        BiasType
    )
    HAS_ADVANCED_NLP = True
except ImportError as e:
    HAS_ADVANCED_NLP = False
    logging.warning(f"Advanced NLP module not available: {e}")

try:
    from verity_claim_similarity import (
        ClaimSimilarityEngine,
        ClaimRecord,
        SimilarityMatch
    )
    HAS_CLAIM_SIMILARITY = True
except ImportError as e:
    HAS_CLAIM_SIMILARITY = False
    logging.warning(f"Claim Similarity module not available: {e}")

try:
    from verity_monte_carlo import (
        MonteCarloConfidenceEngine,
        MonteCarloResult,
        SourceEvidence,
        VerdictCategory
    )
    HAS_MONTE_CARLO = True
except ImportError as e:
    HAS_MONTE_CARLO = False
    logging.warning(f"Monte Carlo module not available: {e}")

try:
    from verity_source_database import (
        get_source_profile as get_source_credibility,
        SourceProfile,
        CredibilityTier,
        FactualReporting,
        BiasRating
    )
    HAS_SOURCE_DB = True
    
    # Create a wrapper class for the source database
    class SourceCredibilityDB:
        """Wrapper class for source database functions"""
        def get_source(self, domain: str) -> Optional[SourceProfile]:
            return get_source_credibility(domain)
        
        def get_batch(self, domains: List[str]) -> Dict[str, SourceProfile]:
            results = {}
            for domain in domains:
                profile = get_source_credibility(domain)
                if profile:
                    results[domain] = profile
            return results
    
except ImportError as e:
    HAS_SOURCE_DB = False
    logging.warning(f"Source Database module not available: {e}")

try:
    from verity_consensus_engine import (
        ConsensusEngine,
    )
    # Create wrapper dataclasses
    @dataclass
    class ConsensusResult:
        verdict: str
        confidence: float
        agreement_level: float
        dissenting_sources: List[str]
        majority_percentage: float
    
    @dataclass
    class SourceVote:
        source: str
        verdict: str
        confidence: float
        weight: float = 1.0
        
    HAS_CONSENSUS = True
except ImportError as e:
    HAS_CONSENSUS = False
    logging.warning(f"Consensus Engine module not available: {e}")

try:
    from verity_evidence_graph import (
        EvidenceGraphBuilder as EvidenceGraph,
        GraphNode as EvidenceNode,
        GraphEdge as EvidenceEdge
    )
    HAS_EVIDENCE_GRAPH = True
except ImportError as e:
    HAS_EVIDENCE_GRAPH = False
    logging.warning(f"Evidence Graph module not available: {e}")

try:
    from verity_numerical_verification import (
        NumericalClaimVerifier as NumericalVerifier,
        NumericalClaim,
        ExtractedNumber
    )
    # Create wrapper result class
    @dataclass
    class NumericalResult:
        has_claims: bool
        claims: List[Any]
        overall_plausibility: float
        warnings: List[str]
    HAS_NUMERICAL = True
except ImportError as e:
    HAS_NUMERICAL = False
    logging.warning(f"Numerical Verification module not available: {e}")

try:
    from verity_temporal_reasoning import (
        TemporalReasoningEngine as TemporalReasoner,
        TemporalReference as TemporalClaim,
    )
    # Create wrapper result class
    @dataclass
    class TemporalResult:
        has_claims: bool
        references: List[Any]
        chronology_valid: bool
        anachronisms: List[str]
        warnings: List[str]
    HAS_TEMPORAL = True
except ImportError as e:
    HAS_TEMPORAL = False
    logging.warning(f"Temporal Reasoning module not available: {e}")

try:
    from verity_geospatial_reasoning import (
        GeospatialReasoningEngine as GeospatialReasoner,
        GeoLocation as LocationClaim,
        GeoContext
    )
    # Create wrapper result class
    @dataclass
    class GeospatialResult:
        has_claims: bool
        locations: List[Any]
        validity_score: float
        distance_claims: List[Any]
        warnings: List[str]
    HAS_GEOSPATIAL = True
except ImportError as e:
    HAS_GEOSPATIAL = False
    logging.warning(f"Geospatial Reasoning module not available: {e}")

try:
    from verity_social_media_analyzer import (
        SocialMediaAnalyzer,
        SocialMediaAnalysis as ViralClaimReport,
        ViralityMetrics as PlatformMetrics
    )
    HAS_SOCIAL_MEDIA = True
except ImportError as e:
    HAS_SOCIAL_MEDIA = False
    logging.warning(f"Social Media Analyzer module not available: {e}")

try:
    from verity_adaptive_learning import (
        AdaptiveLearningSystem as AdaptiveLearner,
        FeedbackEntry as FeedbackRecord,
        ProviderPerformance as ModelPerformance
    )
    HAS_ADAPTIVE_LEARNING = True
except ImportError as e:
    HAS_ADAPTIVE_LEARNING = False
    logging.warning(f"Adaptive Learning module not available: {e}")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerityModules")


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class IntegratedAnalysis:
    """Complete analysis from all modules"""
    
    # Core claim
    claim: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # NLP Analysis
    nlp_analysis: Optional[Dict] = None
    detected_fallacies: List[str] = field(default_factory=list)
    detected_propaganda: List[str] = field(default_factory=list)
    detected_bias: List[str] = field(default_factory=list)
    entities: List[Dict] = field(default_factory=list)
    
    # Similarity
    similar_claims: List[Dict] = field(default_factory=list)
    related_fact_checks: List[Dict] = field(default_factory=list)
    
    # Confidence
    monte_carlo_result: Optional[Dict] = None
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    probability_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Source Analysis
    source_credibility_scores: Dict[str, float] = field(default_factory=dict)
    source_profiles: List[Dict] = field(default_factory=list)
    
    # Consensus
    consensus_result: Optional[Dict] = None
    agreement_level: float = 0.0
    
    # Evidence Graph
    evidence_graph: Optional[Dict] = None
    
    # Specialized Verification
    numerical_analysis: Optional[Dict] = None
    temporal_analysis: Optional[Dict] = None
    geospatial_analysis: Optional[Dict] = None
    
    # Social Media
    social_media_metrics: Optional[Dict] = None
    virality_score: float = 0.0
    
    # Adaptive Learning
    model_recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    modules_used: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "claim": self.claim,
            "timestamp": self.timestamp.isoformat(),
            "nlp": {
                "analysis": self.nlp_analysis,
                "fallacies": self.detected_fallacies,
                "propaganda": self.detected_propaganda,
                "bias": self.detected_bias,
                "entities": self.entities
            },
            "similarity": {
                "similar_claims": self.similar_claims,
                "related_fact_checks": self.related_fact_checks
            },
            "confidence": {
                "monte_carlo": self.monte_carlo_result,
                "interval": self.confidence_interval,
                "probabilities": self.probability_distribution
            },
            "sources": {
                "credibility_scores": self.source_credibility_scores,
                "profiles": self.source_profiles
            },
            "consensus": self.consensus_result,
            "agreement_level": self.agreement_level,
            "evidence_graph": self.evidence_graph,
            "specialized": {
                "numerical": self.numerical_analysis,
                "temporal": self.temporal_analysis,
                "geospatial": self.geospatial_analysis
            },
            "social_media": self.social_media_metrics,
            "virality_score": self.virality_score,
            "recommendations": self.model_recommendations,
            "metadata": {
                "modules_used": self.modules_used,
                "processing_time_ms": self.processing_time_ms
            }
        }


# ============================================================
# UNIFIED MODULES INTEGRATOR
# ============================================================

class VerityModulesIntegrator:
    """
    The Ultimate Integration Layer
    
    Combines all Verity modules into a single, powerful interface
    that provides comprehensive claim analysis beyond basic fact-checking.
    """
    
    def __init__(self):
        """Initialize all available modules"""
        self._initialized = False
        
        # Initialize modules
        self.nlp_analyzer: Optional[AdvancedNLPAnalyzer] = None
        self.similarity_engine: Optional[ClaimSimilarityEngine] = None
        self.monte_carlo: Optional[MonteCarloConfidenceEngine] = None
        self.source_db: Optional[SourceCredibilityDB] = None
        self.consensus_engine: Optional[ConsensusEngine] = None
        self.evidence_graph: Optional[EvidenceGraph] = None
        self.numerical_verifier: Optional[NumericalVerifier] = None
        self.temporal_reasoner: Optional[TemporalReasoner] = None
        self.geospatial_reasoner: Optional[GeospatialReasoner] = None
        self.social_analyzer: Optional[SocialMediaAnalyzer] = None
        self.adaptive_learner: Optional[AdaptiveLearner] = None
        
        self._module_status: Dict[str, bool] = {}
        
        # Auto-initialize on construction
        self.initialize()
    
    def initialize(self) -> Dict[str, bool]:
        """Initialize all available modules and return status"""
        if self._initialized:
            return self._module_status
        
        logger.info("Initializing Verity Modules Integrator...")
        
        # Advanced NLP
        if HAS_ADVANCED_NLP:
            try:
                self.nlp_analyzer = AdvancedNLPAnalyzer()
                self._module_status["advanced_nlp"] = True
                logger.info("✓ Advanced NLP Analyzer initialized")
            except Exception as e:
                self._module_status["advanced_nlp"] = False
                logger.error(f"✗ Advanced NLP failed: {e}")
        else:
            self._module_status["advanced_nlp"] = False
        
        # Claim Similarity
        if HAS_CLAIM_SIMILARITY:
            try:
                self.similarity_engine = ClaimSimilarityEngine()
                self._module_status["claim_similarity"] = True
                logger.info("✓ Claim Similarity Engine initialized")
            except Exception as e:
                self._module_status["claim_similarity"] = False
                logger.error(f"✗ Claim Similarity failed: {e}")
        else:
            self._module_status["claim_similarity"] = False
        
        # Monte Carlo
        if HAS_MONTE_CARLO:
            try:
                self.monte_carlo = MonteCarloConfidenceEngine(simulations=5000)
                self._module_status["monte_carlo"] = True
                logger.info("✓ Monte Carlo Engine initialized")
            except Exception as e:
                self._module_status["monte_carlo"] = False
                logger.error(f"✗ Monte Carlo failed: {e}")
        else:
            self._module_status["monte_carlo"] = False
        
        # Source Database
        if HAS_SOURCE_DB:
            try:
                self.source_db = SourceCredibilityDB()
                self._module_status["source_database"] = True
                logger.info("✓ Source Credibility Database initialized")
            except Exception as e:
                self._module_status["source_database"] = False
                logger.error(f"✗ Source Database failed: {e}")
        else:
            self._module_status["source_database"] = False
        
        # Consensus Engine
        if HAS_CONSENSUS:
            try:
                self.consensus_engine = ConsensusEngine()
                self._module_status["consensus_engine"] = True
                logger.info("✓ Consensus Engine initialized")
            except Exception as e:
                self._module_status["consensus_engine"] = False
                logger.error(f"✗ Consensus Engine failed: {e}")
        else:
            self._module_status["consensus_engine"] = False
        
        # Evidence Graph
        if HAS_EVIDENCE_GRAPH:
            try:
                self.evidence_graph = EvidenceGraph()
                self._module_status["evidence_graph"] = True
                logger.info("✓ Evidence Graph initialized")
            except Exception as e:
                self._module_status["evidence_graph"] = False
                logger.error(f"✗ Evidence Graph failed: {e}")
        else:
            self._module_status["evidence_graph"] = False
        
        # Numerical Verification
        if HAS_NUMERICAL:
            try:
                self.numerical_verifier = NumericalVerifier()
                self._module_status["numerical_verification"] = True
                logger.info("✓ Numerical Verifier initialized")
            except Exception as e:
                self._module_status["numerical_verification"] = False
                logger.error(f"✗ Numerical Verification failed: {e}")
        else:
            self._module_status["numerical_verification"] = False
        
        # Temporal Reasoning
        if HAS_TEMPORAL:
            try:
                self.temporal_reasoner = TemporalReasoner()
                self._module_status["temporal_reasoning"] = True
                logger.info("✓ Temporal Reasoner initialized")
            except Exception as e:
                self._module_status["temporal_reasoning"] = False
                logger.error(f"✗ Temporal Reasoning failed: {e}")
        else:
            self._module_status["temporal_reasoning"] = False
        
        # Geospatial Reasoning
        if HAS_GEOSPATIAL:
            try:
                self.geospatial_reasoner = GeospatialReasoner()
                self._module_status["geospatial_reasoning"] = True
                logger.info("✓ Geospatial Reasoner initialized")
            except Exception as e:
                self._module_status["geospatial_reasoning"] = False
                logger.error(f"✗ Geospatial Reasoning failed: {e}")
        else:
            self._module_status["geospatial_reasoning"] = False
        
        # Social Media Analyzer
        if HAS_SOCIAL_MEDIA:
            try:
                self.social_analyzer = SocialMediaAnalyzer()
                self._module_status["social_media"] = True
                logger.info("✓ Social Media Analyzer initialized")
            except Exception as e:
                self._module_status["social_media"] = False
                logger.error(f"✗ Social Media Analyzer failed: {e}")
        else:
            self._module_status["social_media"] = False
        
        # Adaptive Learning
        if HAS_ADAPTIVE_LEARNING:
            try:
                self.adaptive_learner = AdaptiveLearner()
                self._module_status["adaptive_learning"] = True
                logger.info("✓ Adaptive Learner initialized")
            except Exception as e:
                self._module_status["adaptive_learning"] = False
                logger.error(f"✗ Adaptive Learning failed: {e}")
        else:
            self._module_status["adaptive_learning"] = False
        
        self._initialized = True
        
        # Summary
        active = sum(1 for v in self._module_status.values() if v)
        total = len(self._module_status)
        logger.info(f"Initialization complete: {active}/{total} modules active")
        
        return self._module_status
    
    def get_module_status(self) -> Dict[str, bool]:
        """Get status of all modules"""
        if not self._initialized:
            self.initialize()
        return self._module_status
    
    # ============================================================
    # INDIVIDUAL ANALYSIS METHODS
    # ============================================================
    
    def analyze_nlp(self, claim: str) -> Optional[Dict]:
        """
        Perform advanced NLP analysis on a claim.
        
        Returns:
            - Detected logical fallacies
            - Propaganda techniques
            - Bias indicators
            - Named entities
            - Sentiment and subjectivity
            - Key phrases
        """
        if not self.nlp_analyzer:
            return None
        
        try:
            analysis: ClaimAnalysis = self.nlp_analyzer.analyze(claim)
            return {
                "claim_type": analysis.claim_type if hasattr(analysis, 'claim_type') else "factual",
                "fallacies": [
                    {"type": f[0].value if hasattr(f[0], 'value') else str(f[0]), "confidence": f[1]}
                    for f in analysis.fallacies
                ] if hasattr(analysis, 'fallacies') else [],
                "propaganda": [
                    {"technique": p[0].value if hasattr(p[0], 'value') else str(p[0]), "confidence": p[1]}
                    for p in analysis.propaganda_techniques
                ] if hasattr(analysis, 'propaganda_techniques') else [],
                "bias": [
                    {"type": b[0].value if hasattr(b[0], 'value') else str(b[0]), "confidence": b[1]}
                    for b in analysis.bias_indicators
                ] if hasattr(analysis, 'bias_indicators') else [],
                "entities": [
                    {"text": e.text, "type": e.entity_type.value if hasattr(e.entity_type, 'value') else str(e.entity_type), "confidence": e.confidence}
                    for e in analysis.entities
                ] if hasattr(analysis, 'entities') else [],
                "sentiment": analysis.sentiment_score if hasattr(analysis, 'sentiment_score') else 0.0,
                "subjectivity": analysis.subjectivity_score if hasattr(analysis, 'subjectivity_score') else 0.0,
                "complexity": analysis.complexity_score if hasattr(analysis, 'complexity_score') else 0.5,
                "verifiability": analysis.verifiability_score if hasattr(analysis, 'verifiability_score') else 0.5,
                "key_phrases": analysis.key_phrases if hasattr(analysis, 'key_phrases') else [],
                "suggested_searches": analysis.suggested_searches if hasattr(analysis, 'suggested_searches') else []
            }
        except Exception as e:
            logger.error(f"NLP analysis error: {e}")
            return None
    
    def find_similar_claims(self, claim: str, limit: int = 10) -> List[Dict]:
        """
        Find similar claims that have been previously fact-checked.
        
        Returns list of:
            - Similar claim text
            - Similarity score
            - Previous verdict (if available)
            - Source of fact-check
        """
        if not self.similarity_engine:
            return []
        
        try:
            matches: List[SimilarityMatch] = self.similarity_engine.find_similar(claim, top_k=limit)
            return [
                {
                    "claim": m.claim.claim_text if hasattr(m.claim, 'claim_text') else str(m.claim),
                    "similarity_score": m.similarity if hasattr(m, 'similarity') else getattr(m, 'score', 0),
                    "verdict": m.claim.verdict if hasattr(m.claim, 'verdict') else None,
                    "source": getattr(m.claim, 'sources', [None])[0] if hasattr(m.claim, 'sources') else None,
                    "date": m.claim.timestamp.isoformat() if hasattr(m.claim, 'timestamp') and m.claim.timestamp else None
                }
                for m in matches
            ]
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    def calculate_monte_carlo_confidence(
        self,
        evidence_list: List[Dict]
    ) -> Optional[Dict]:
        """
        Run Monte Carlo simulation on evidence to get probabilistic confidence.
        
        Args:
            evidence_list: List of dicts with keys:
                - source_name: str
                - verdict: 'true', 'false', 'mixed', 'unknown'
                - confidence: float (0-1)
                - credibility: float (0-1)
        
        Returns:
            - Final verdict
            - Mean confidence
            - 95% confidence interval
            - Probability of each verdict
        """
        if not self.monte_carlo:
            return None
        
        try:
            # Convert to SourceEvidence objects
            source_evidence = [
                SourceEvidence(
                    source_name=e.get("source_name", "unknown"),
                    verdict=VerdictCategory(e.get("verdict", "unknown")),
                    confidence=e.get("confidence", 0.5),
                    credibility=e.get("credibility", 0.5)
                )
                for e in evidence_list
            ]
            
            result: MonteCarloResult = self.monte_carlo.simulate(source_evidence)
            
            return {
                "verdict": result.verdict.value,
                "mean_confidence": result.mean_confidence,
                "confidence_interval": {
                    "lower": result.confidence_interval[0],
                    "upper": result.confidence_interval[1]
                },
                "probabilities": {
                    "true": result.probability_true,
                    "false": result.probability_false,
                    "mixed": result.probability_mixed
                },
                "simulations": result.simulation_count,
                "convergence_score": result.convergence_score
            }
        except Exception as e:
            logger.error(f"Monte Carlo error: {e}")
            return None
    
    def get_source_credibility(self, domain: str) -> Optional[Dict]:
        """
        Get credibility information for a source domain.
        
        Returns:
            - Credibility score (0-100)
            - Factual reporting rating
            - Bias rating
            - Credibility tier (1-5)
            - Description
        """
        if not self.source_db:
            return None
        
        try:
            profile: SourceProfile = self.source_db.get_source(domain)
            if profile:
                return {
                    "name": profile.name,
                    "domain": profile.domain,
                    "credibility_score": profile.credibility_score,
                    "factual_reporting": profile.factual_reporting.value,
                    "bias_rating": profile.bias_rating.value,
                    "credibility_tier": profile.credibility_tier.value,
                    "description": profile.description,
                    "type": profile.type,
                    "country": profile.country
                }
            return None
        except Exception as e:
            logger.error(f"Source credibility error: {e}")
            return None
    
    def get_batch_source_credibility(self, domains: List[str]) -> Dict[str, Dict]:
        """Get credibility for multiple domains"""
        results = {}
        for domain in domains:
            profile = self.get_source_credibility(domain)
            if profile:
                results[domain] = profile
        return results
    
    def build_consensus(self, votes: List[Dict]) -> Optional[Dict]:
        """
        Build consensus from multiple source votes.
        
        Args:
            votes: List of dicts with keys:
                - source: str
                - verdict: str
                - confidence: float
                - weight: float (optional)
        """
        if not self.consensus_engine:
            return None
        
        try:
            source_votes = [
                SourceVote(
                    source=v.get("source", "unknown"),
                    verdict=v.get("verdict", "unknown"),
                    confidence=v.get("confidence", 0.5),
                    weight=v.get("weight", 1.0)
                )
                for v in votes
            ]
            
            result: ConsensusResult = self.consensus_engine.compute(source_votes)
            
            return {
                "verdict": result.verdict,
                "confidence": result.confidence,
                "agreement_level": result.agreement_level,
                "dissenting_sources": result.dissenting_sources,
                "majority_percentage": result.majority_percentage
            }
        except Exception as e:
            logger.error(f"Consensus error: {e}")
            return None
    
    def analyze_numerical_claims(self, claim: str, reference_value: float = None) -> Optional[Dict]:
        """
        Analyze and verify numerical claims in text.
        
        Detects:
            - Statistics
            - Percentages
            - Comparisons
            - Growth rates
        """
        if not self.numerical_verifier:
            return None
        
        try:
            # Parse the claim first
            parsed = self.numerical_verifier.parse_claim(claim)
            
            if not parsed:
                return {
                    "has_numerical_claims": False,
                    "claims": [],
                    "explanation": "No numerical claims detected"
                }
            
            # Verify if we have a reference value
            if reference_value is not None:
                verification = self.numerical_verifier.verify_numerical_claim(
                    claim, 
                    reference_value=reference_value
                )
            else:
                verification = self.numerical_verifier.verify_numerical_claim(claim)
            
            # Extract number info
            number_info = []
            if parsed.value:
                number_info.append({
                    "value": parsed.value.value if hasattr(parsed.value, 'value') else str(parsed.value),
                    "type": parsed.comparison_type or "equals",
                    "subject": parsed.subject,
                    "context": parsed.context
                })
            
            return {
                "has_numerical_claims": True,
                "claims": number_info,
                "parsed_subject": parsed.subject,
                "comparison_type": parsed.comparison_type,
                "verification": verification,
                "overall_plausibility": verification.get("plausibility", 0.5) if isinstance(verification, dict) else 0.5
            }
        except Exception as e:
            logger.error(f"Numerical analysis error: {e}")
            return None
    
    def analyze_temporal_claims(self, claim: str) -> Optional[Dict]:
        """
        Analyze and verify temporal (time-based) claims.
        
        Detects:
            - Date references
            - Time periods
            - Sequences
            - Anachronisms
        """
        if not self.temporal_reasoner:
            return None
        
        try:
            # Use analyze_claim method
            context = self.temporal_reasoner.analyze_claim(claim)
            
            # Extract temporal references
            references = []
            if hasattr(context, 'references') and context.references:
                for ref in context.references:
                    references.append({
                        "text": ref.original_text if hasattr(ref, 'original_text') else str(ref),
                        "type": ref.reference_type.value if hasattr(ref, 'reference_type') and hasattr(ref.reference_type, 'value') else "unknown",
                        "resolved_date": ref.resolved_date.isoformat() if hasattr(ref, 'resolved_date') and ref.resolved_date else None
                    })
            
            return {
                "has_temporal_claims": len(references) > 0,
                "temporal_references": references,
                "truth_temporality": context.truth_temporality.value if hasattr(context, 'truth_temporality') and hasattr(context.truth_temporality, 'value') else "unknown",
                "historical_period": context.historical_period if hasattr(context, 'historical_period') else None,
                "relevant_events": context.relevant_events if hasattr(context, 'relevant_events') else [],
                "requires_temporal_context": context.requires_historical_context if hasattr(context, 'requires_historical_context') else False
            }
        except Exception as e:
            logger.error(f"Temporal analysis error: {e}")
            return None
    
    def analyze_geospatial_claims(self, claim: str) -> Optional[Dict]:
        """
        Analyze and verify location-based claims.
        
        Detects:
            - Place names
            - Geographic relationships
            - Distance claims
            - Location inconsistencies
        """
        if not self.geospatial_reasoner:
            return None
        
        try:
            # Use analyze_claim method
            context = self.geospatial_reasoner.analyze_claim(claim)
            
            # Extract locations
            locations = []
            if hasattr(context, 'locations') and context.locations:
                for loc in context.locations:
                    locations.append({
                        "name": loc.name if hasattr(loc, 'name') else str(loc),
                        "type": loc.location_type.value if hasattr(loc, 'location_type') and hasattr(loc.location_type, 'value') else "unknown",
                        "confidence": loc.confidence if hasattr(loc, 'confidence') else 0.5
                    })
            
            return {
                "has_location_claims": len(locations) > 0,
                "locations": locations,
                "is_location_sensitive": context.is_location_sensitive if hasattr(context, 'is_location_sensitive') else False,
                "sensitivity_type": context.sensitivity_type if hasattr(context, 'sensitivity_type') else None,
                "implied_jurisdiction": context.implied_jurisdiction if hasattr(context, 'implied_jurisdiction') else None,
                "geographic_validity": 1.0
            }
        except Exception as e:
            logger.error(f"Geospatial analysis error: {e}")
            return None
    
    def analyze_social_media(self, content: str, spread_data: Dict = None, account_data: Dict = None) -> Optional[Dict]:
        """
        Analyze social media content for misinformation patterns.
        
        Returns:
            - Virality assessment
            - Emotional manipulation score
            - Bot activity indicators
            - Credibility score
            - Red flags
        """
        if not self.social_analyzer:
            return None
        
        try:
            # Use the analyze method with proper parameters
            analysis = self.social_analyzer.analyze(
                content=content,
                spread_data=spread_data or {},
                account_data=account_data or {}
            )
            
            return {
                "content_type": analysis.content_type if hasattr(analysis, 'content_type') else "unknown",
                "virality_level": analysis.virality_level if hasattr(analysis, 'virality_level') else "unknown",
                "emotional_score": analysis.emotional_analysis.get("total_emotional_score", 0) if hasattr(analysis, 'emotional_analysis') else 0,
                "credibility_score": analysis.credibility_score if hasattr(analysis, 'credibility_score') else 0.5,
                "red_flags": analysis.red_flags if hasattr(analysis, 'red_flags') else [],
                "recommendations": analysis.recommendations if hasattr(analysis, 'recommendations') else [],
                "virality_metrics": {
                    "velocity_score": analysis.virality_metrics.velocity_score if hasattr(analysis, 'virality_metrics') else 0,
                    "reach_score": analysis.virality_metrics.reach_score if hasattr(analysis, 'virality_metrics') else 0,
                    "bot_activity_score": analysis.virality_metrics.bot_activity_score if hasattr(analysis, 'virality_metrics') else 0
                } if hasattr(analysis, 'virality_metrics') else {}
            }
        except Exception as e:
            logger.error(f"Social media analysis error: {e}")
            return None
    
    # ============================================================
    # COMPREHENSIVE ANALYSIS
    # ============================================================
    
    async def analyze_complete(
        self,
        claim: str,
        evidence: List[Dict] = None,
        sources_used: List[str] = None
    ) -> IntegratedAnalysis:
        """
        Perform COMPLETE analysis using ALL available modules.
        
        This is the ULTIMATE analysis that combines:
        - NLP analysis (fallacies, propaganda, bias)
        - Similar claims search
        - Monte Carlo confidence
        - Source credibility
        - Specialized verification (numerical, temporal, geospatial)
        - Social media metrics
        
        Args:
            claim: The claim to analyze
            evidence: Optional evidence list for Monte Carlo
            sources_used: Optional list of source domains for credibility check
        
        Returns:
            IntegratedAnalysis with all results
        """
        import time
        start_time = time.time()
        
        if not self._initialized:
            self.initialize()
        
        result = IntegratedAnalysis(claim=claim)
        modules_used = []
        
        # Run all analyses
        # (In production, these could be parallelized with asyncio.gather)
        
        # 1. NLP Analysis
        if self.nlp_analyzer:
            nlp_result = self.analyze_nlp(claim)
            if nlp_result:
                result.nlp_analysis = nlp_result
                result.detected_fallacies = [f["type"] for f in nlp_result.get("fallacies", [])]
                result.detected_propaganda = [p["technique"] for p in nlp_result.get("propaganda", [])]
                result.detected_bias = [b["type"] for b in nlp_result.get("bias", [])]
                result.entities = nlp_result.get("entities", [])
                modules_used.append("advanced_nlp")
        
        # 2. Similar Claims
        if self.similarity_engine:
            similar = self.find_similar_claims(claim, limit=5)
            if similar:
                result.similar_claims = similar
                result.related_fact_checks = [s for s in similar if s.get("verdict")]
                modules_used.append("claim_similarity")
        
        # 3. Monte Carlo Confidence
        if self.monte_carlo and evidence:
            mc_result = self.calculate_monte_carlo_confidence(evidence)
            if mc_result:
                result.monte_carlo_result = mc_result
                result.confidence_interval = (
                    mc_result["confidence_interval"]["lower"],
                    mc_result["confidence_interval"]["upper"]
                )
                result.probability_distribution = mc_result["probabilities"]
                modules_used.append("monte_carlo")
        
        # 4. Source Credibility
        if self.source_db and sources_used:
            credibility_results = self.get_batch_source_credibility(sources_used)
            result.source_credibility_scores = {
                domain: data["credibility_score"]
                for domain, data in credibility_results.items()
            }
            result.source_profiles = list(credibility_results.values())
            modules_used.append("source_database")
        
        # 5. Numerical Verification
        if self.numerical_verifier:
            num_result = self.analyze_numerical_claims(claim)
            if num_result:
                result.numerical_analysis = num_result
                modules_used.append("numerical_verification")
        
        # 6. Temporal Reasoning
        if self.temporal_reasoner:
            temp_result = self.analyze_temporal_claims(claim)
            if temp_result:
                result.temporal_analysis = temp_result
                modules_used.append("temporal_reasoning")
        
        # 7. Geospatial Reasoning
        if self.geospatial_reasoner:
            geo_result = self.analyze_geospatial_claims(claim)
            if geo_result:
                result.geospatial_analysis = geo_result
                modules_used.append("geospatial_reasoning")
        
        # 8. Social Media
        if self.social_analyzer:
            social_result = self.analyze_social_media(claim)
            if social_result:
                result.social_media_metrics = social_result
                result.virality_score = social_result.get("virality_score", 0.0)
                modules_used.append("social_media")
        
        # Finalize
        result.modules_used = modules_used
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def analyze_complete_sync(
        self,
        claim: str,
        evidence: List[Dict] = None,
        sources_used: List[str] = None
    ) -> IntegratedAnalysis:
        """Synchronous version of analyze_complete"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.analyze_complete(claim, evidence, sources_used)
        )


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_integrator_instance: Optional[VerityModulesIntegrator] = None


def get_modules_integrator() -> VerityModulesIntegrator:
    """Get singleton instance of the modules integrator"""
    global _integrator_instance
    
    if _integrator_instance is None:
        _integrator_instance = VerityModulesIntegrator()
        _integrator_instance.initialize()
    
    return _integrator_instance


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VERITY MODULES INTEGRATOR - TEST")
    print("=" * 60)
    
    # Initialize
    integrator = get_modules_integrator()
    
    print("\nModule Status:")
    for module, status in integrator.get_module_status().items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {module}: {'Active' if status else 'Inactive'}")
    
    # Test claim
    test_claim = "The COVID-19 vaccine has been proven to cause autism in 35% of children according to a 2023 CDC study."
    
    print(f"\nTest Claim: {test_claim}")
    print("-" * 60)
    
    # NLP Analysis
    if integrator.nlp_analyzer:
        print("\n📊 NLP Analysis:")
        nlp = integrator.analyze_nlp(test_claim)
        if nlp:
            print(f"  Verifiability: {nlp.get('verifiability', 0):.2f}")
            print(f"  Subjectivity: {nlp.get('subjectivity', 0):.2f}")
            if nlp.get('fallacies'):
                print(f"  Fallacies: {[f['type'] for f in nlp['fallacies']]}")
            if nlp.get('entities'):
                print(f"  Entities: {[e['text'] for e in nlp['entities'][:5]]}")
    
    # Source Credibility
    if integrator.source_db:
        print("\n🔍 Source Credibility Check:")
        for domain in ["cdc.gov", "nature.com", "infowars.com"]:
            profile = integrator.get_source_credibility(domain)
            if profile:
                print(f"  {domain}: {profile['credibility_score']}/100 ({profile['factual_reporting']})")
    
    print("\n" + "=" * 60)
    print("Integration test complete!")
