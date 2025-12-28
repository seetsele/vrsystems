"""
Verity Intelligence Engine - Part 4: Adaptive Learning System
=============================================================
The system that makes Verity SMARTER over time.

ADAPTIVE LEARNING FEATURES:
==========================
1. Feedback Loop Integration
   - Learn from user corrections
   - Track accuracy over time
   - Improve provider weighting

2. Provider Performance Tracking
   - Monitor which providers are most accurate
   - Dynamically adjust routing
   - Identify failing providers

3. Claim Pattern Recognition
   - Identify similar claims
   - Reuse cached verdicts
   - Build claim templates

4. Confidence Calibration
   - Track predicted vs actual outcomes
   - Adjust confidence scores
   - Reduce overconfidence

5. Domain Expertise Growth
   - Learn which providers excel in which domains
   - Build specialized routing tables
   - Improve over time
"""

import asyncio
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import os

from verity_intelligence_engine import Verdict, ClaimType


@dataclass
class FeedbackEntry:
    """User feedback on a verdict"""
    claim_hash: str
    original_verdict: Verdict
    user_verdict: Verdict
    confidence_was: float
    timestamp: datetime
    feedback_type: str  # 'correction', 'confirmation', 'dispute'
    notes: str = ""


@dataclass
class ProviderPerformance:
    """Track provider accuracy over time"""
    provider_name: str
    total_queries: int = 0
    correct_verdicts: int = 0
    incorrect_verdicts: int = 0
    average_response_time_ms: float = 0.0
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    domain_accuracy: Dict[str, float] = field(default_factory=dict)


@dataclass
class CachedVerdict:
    """Cached verdict for a claim"""
    claim_hash: str
    original_claim: str
    verdict: Verdict
    confidence: float
    timestamp: datetime
    hit_count: int = 0
    sources_count: int = 0


class AdaptiveLearningSystem:
    """
    Makes Verity smarter over time through:
    1. User feedback integration
    2. Provider performance tracking
    3. Verdict caching
    4. Confidence calibration
    """
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.join(
            os.path.dirname(__file__), '.verity_learning'
        )
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.provider_performance: Dict[str, ProviderPerformance] = {}
        self.feedback_history: List[FeedbackEntry] = []
        self.verdict_cache: Dict[str, CachedVerdict] = {}
        self.confidence_calibration: Dict[str, List[float]] = defaultdict(list)
        
        # Domain-specific routing weights (learned over time)
        self.domain_weights: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        self._load_state()
    
    def _hash_claim(self, claim: str) -> str:
        """Generate hash for a claim (for caching)"""
        normalized = claim.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    # ===========================================
    # FEEDBACK INTEGRATION
    # ===========================================
    
    def record_feedback(
        self,
        claim: str,
        original_verdict: Verdict,
        user_verdict: Verdict,
        confidence_was: float,
        notes: str = ""
    ):
        """
        Record user feedback on a verdict.
        
        This is CRITICAL for improving accuracy.
        We track:
        - What we predicted
        - What the user says is correct
        - Our confidence at the time
        """
        claim_hash = self._hash_claim(claim)
        
        if original_verdict == user_verdict:
            feedback_type = 'confirmation'
        elif user_verdict == Verdict.DISPUTED:
            feedback_type = 'dispute'
        else:
            feedback_type = 'correction'
        
        entry = FeedbackEntry(
            claim_hash=claim_hash,
            original_verdict=original_verdict,
            user_verdict=user_verdict,
            confidence_was=confidence_was,
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            notes=notes
        )
        
        self.feedback_history.append(entry)
        
        # Update calibration data
        self._update_calibration(confidence_was, original_verdict == user_verdict)
        
        self._save_state()
        
        return feedback_type
    
    def get_correction_rate(self, days: int = 30) -> Dict:
        """Get rate of user corrections over time"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [f for f in self.feedback_history if f.timestamp > cutoff]
        
        if not recent:
            return {'total': 0, 'correction_rate': 0.0}
        
        corrections = len([f for f in recent if f.feedback_type == 'correction'])
        confirmations = len([f for f in recent if f.feedback_type == 'confirmation'])
        
        return {
            'total': len(recent),
            'corrections': corrections,
            'confirmations': confirmations,
            'correction_rate': corrections / len(recent) if recent else 0,
            'accuracy_estimate': confirmations / len(recent) if recent else 0
        }
    
    # ===========================================
    # PROVIDER PERFORMANCE TRACKING
    # ===========================================
    
    def record_provider_result(
        self,
        provider_name: str,
        was_correct: bool,
        response_time_ms: float,
        claim_type: ClaimType = None,
        had_error: bool = False
    ):
        """
        Track individual provider performance.
        
        This lets us:
        - Identify best providers for each domain
        - Route away from failing providers
        - Optimize response times
        """
        if provider_name not in self.provider_performance:
            self.provider_performance[provider_name] = ProviderPerformance(
                provider_name=provider_name
            )
        
        perf = self.provider_performance[provider_name]
        perf.total_queries += 1
        
        if had_error:
            perf.failure_count += 1
            perf.last_failure = datetime.now()
        else:
            if was_correct:
                perf.correct_verdicts += 1
            else:
                perf.incorrect_verdicts += 1
            
            # Update moving average response time
            perf.average_response_time_ms = (
                perf.average_response_time_ms * 0.9 + response_time_ms * 0.1
            )
        
        # Update domain-specific accuracy
        if claim_type and not had_error:
            domain = claim_type.value if hasattr(claim_type, 'value') else str(claim_type)
            if domain not in perf.domain_accuracy:
                perf.domain_accuracy[domain] = 0.5
            
            # Exponential moving average
            current = perf.domain_accuracy[domain]
            perf.domain_accuracy[domain] = current * 0.9 + (1.0 if was_correct else 0.0) * 0.1
        
        self._save_state()
    
    def get_provider_ranking(self, claim_type: ClaimType = None) -> List[Tuple[str, float]]:
        """
        Get providers ranked by accuracy.
        
        If claim_type is specified, uses domain-specific accuracy.
        """
        rankings = []
        
        for name, perf in self.provider_performance.items():
            if perf.total_queries < 5:
                continue  # Not enough data
            
            # Check for recent failures
            if perf.last_failure:
                time_since_failure = (datetime.now() - perf.last_failure).seconds
                if time_since_failure < 300:  # 5 minutes
                    continue  # Skip recently failed providers
            
            # Calculate accuracy
            domain_key = claim_type.value if hasattr(claim_type, 'value') else str(claim_type) if claim_type else None
            if domain_key and domain_key in perf.domain_accuracy:
                accuracy = perf.domain_accuracy[domain_key]
            else:
                total = perf.correct_verdicts + perf.incorrect_verdicts
                accuracy = perf.correct_verdicts / total if total > 0 else 0.5
            
            rankings.append((name, accuracy))
        
        # Sort by accuracy descending
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
    
    def get_provider_weights(self, claim_type: ClaimType = None) -> Dict[str, float]:
        """
        Get provider weights for consensus calculation.
        
        Better providers get higher weights.
        """
        rankings = self.get_provider_ranking(claim_type)
        
        if not rankings:
            return {}
        
        # Normalize to sum to 1.0
        total = sum(acc for _, acc in rankings)
        return {name: acc / total for name, acc in rankings}
    
    # ===========================================
    # VERDICT CACHING
    # ===========================================
    
    def cache_verdict(
        self,
        claim: str,
        verdict: Verdict,
        confidence: float,
        sources_count: int = 0
    ):
        """
        Cache a verdict for reuse.
        
        Caching allows us to:
        - Return instant results for repeated claims
        - Save API costs
        - Improve consistency
        """
        claim_hash = self._hash_claim(claim)
        
        self.verdict_cache[claim_hash] = CachedVerdict(
            claim_hash=claim_hash,
            original_claim=claim[:500],  # Store truncated
            verdict=verdict,
            confidence=confidence,
            timestamp=datetime.now(),
            sources_count=sources_count
        )
        
        self._save_state()
    
    def get_cached_verdict(
        self,
        claim: str,
        max_age_hours: int = 24
    ) -> Optional[CachedVerdict]:
        """
        Retrieve cached verdict if available and fresh.
        """
        claim_hash = self._hash_claim(claim)
        
        if claim_hash not in self.verdict_cache:
            return None
        
        cached = self.verdict_cache[claim_hash]
        
        # Check age
        age = datetime.now() - cached.timestamp
        if age.total_seconds() > max_age_hours * 3600:
            return None  # Too old
        
        # Increment hit count
        cached.hit_count += 1
        
        return cached
    
    def get_similar_claims(self, claim: str, threshold: float = 0.8) -> List[CachedVerdict]:
        """
        Find similar claims in cache.
        
        Uses simple word overlap for now (could use embeddings later).
        """
        claim_words = set(claim.lower().split())
        similar = []
        
        for cached in self.verdict_cache.values():
            cached_words = set(cached.original_claim.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(claim_words & cached_words)
            union = len(claim_words | cached_words)
            similarity = intersection / union if union > 0 else 0
            
            if similarity >= threshold:
                similar.append(cached)
        
        return similar
    
    # ===========================================
    # CONFIDENCE CALIBRATION
    # ===========================================
    
    def _update_calibration(self, confidence_was: float, was_correct: bool):
        """Update confidence calibration data"""
        # Bucket by confidence level
        bucket = round(confidence_was, 1)
        bucket_key = str(bucket)
        
        self.confidence_calibration[bucket_key].append(1.0 if was_correct else 0.0)
    
    def get_calibration_adjustment(self, raw_confidence: float) -> float:
        """
        Adjust confidence based on historical accuracy.
        
        If we're historically overconfident at 0.9 (say, only 75% accurate),
        we should reduce our displayed confidence.
        """
        bucket = round(raw_confidence, 1)
        bucket_key = str(bucket)
        
        history = self.confidence_calibration.get(bucket_key, [])
        
        if len(history) < 10:
            # Not enough data, return as-is
            return raw_confidence
        
        # Calculate actual accuracy at this confidence level
        actual_accuracy = sum(history) / len(history)
        
        # Adjust confidence toward actual accuracy
        # But don't change too drastically
        adjustment = (actual_accuracy - raw_confidence) * 0.5
        adjusted = raw_confidence + adjustment
        
        return max(0.1, min(0.95, adjusted))
    
    def get_calibration_report(self) -> Dict:
        """Get report on confidence calibration"""
        report = {}
        
        for bucket, history in self.confidence_calibration.items():
            if len(history) >= 5:
                actual = sum(history) / len(history)
                predicted = float(bucket)
                report[bucket] = {
                    'predicted_confidence': predicted,
                    'actual_accuracy': actual,
                    'sample_size': len(history),
                    'calibration_error': abs(predicted - actual)
                }
        
        return report
    
    # ===========================================
    # DOMAIN EXPERTISE GROWTH
    # ===========================================
    
    def update_domain_weights(self, claim_type: ClaimType, provider_name: str, success: bool):
        """
        Update domain-specific weights for providers.
        
        Over time, this teaches the system which providers
        are best for which types of claims.
        """
        domain = claim_type.value if hasattr(claim_type, 'value') else str(claim_type)
        
        if provider_name not in self.domain_weights[domain]:
            self.domain_weights[domain][provider_name] = 0.5
        
        # Exponential moving average
        current = self.domain_weights[domain][provider_name]
        self.domain_weights[domain][provider_name] = (
            current * 0.95 + (1.0 if success else 0.0) * 0.05
        )
        
        self._save_state()
    
    def get_best_providers_for_domain(self, claim_type: ClaimType, top_n: int = 5) -> List[str]:
        """Get the best providers for a specific claim type"""
        domain = claim_type.value if hasattr(claim_type, 'value') else str(claim_type)
        weights = self.domain_weights.get(domain, {})
        
        if not weights:
            return []
        
        sorted_providers = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_providers[:top_n]]
    
    # ===========================================
    # PERSISTENCE
    # ===========================================
    
    def _save_state(self):
        """Save learning state to disk"""
        state = {
            'provider_performance': {
                k: asdict(v) for k, v in self.provider_performance.items()
            },
            'feedback_history': [
                {
                    **asdict(f),
                    'original_verdict': f.original_verdict.value if hasattr(f.original_verdict, 'value') else str(f.original_verdict),
                    'user_verdict': f.user_verdict.value if hasattr(f.user_verdict, 'value') else str(f.user_verdict),
                    'timestamp': f.timestamp.isoformat()
                }
                for f in self.feedback_history[-1000:]  # Keep last 1000
            ],
            'verdict_cache': {
                k: {
                    **asdict(v),
                    'verdict': v.verdict.value if hasattr(v.verdict, 'value') else str(v.verdict),
                    'timestamp': v.timestamp.isoformat()
                }
                for k, v in list(self.verdict_cache.items())[-10000:]  # Keep last 10k
            },
            'confidence_calibration': dict(self.confidence_calibration),
            'domain_weights': dict(self.domain_weights),
            'last_updated': datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.storage_dir, 'learning_state.json')
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def _load_state(self):
        """Load learning state from disk"""
        filepath = os.path.join(self.storage_dir, 'learning_state.json')
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Restore provider performance
            for name, data in state.get('provider_performance', {}).items():
                if 'last_failure' in data and data['last_failure']:
                    data['last_failure'] = datetime.fromisoformat(data['last_failure'])
                self.provider_performance[name] = ProviderPerformance(**data)
            
            # Restore confidence calibration
            self.confidence_calibration = defaultdict(
                list, state.get('confidence_calibration', {})
            )
            
            # Restore domain weights
            self.domain_weights = defaultdict(dict, state.get('domain_weights', {}))
            
        except Exception as e:
            print(f"Warning: Could not load learning state: {e}")
    
    def get_learning_summary(self) -> Dict:
        """Get summary of what the system has learned"""
        return {
            'providers_tracked': len(self.provider_performance),
            'feedback_entries': len(self.feedback_history),
            'cached_verdicts': len(self.verdict_cache),
            'domains_learned': len(self.domain_weights),
            'calibration_data_points': sum(
                len(v) for v in self.confidence_calibration.values()
            ),
            'correction_rate': self.get_correction_rate(),
            'top_providers': self.get_provider_ranking()[:5]
        }


__all__ = ['AdaptiveLearningSystem', 'FeedbackEntry', 'ProviderPerformance', 'CachedVerdict']
