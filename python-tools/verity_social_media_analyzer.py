"""
Verity Social Media & Viral Content Analyzer
=============================================
Detect and analyze viral misinformation patterns.

Features:
- Viral spread pattern detection
- Bot/coordinated behavior indicators
- Emotional manipulation scoring
- Share velocity analysis
- First-source tracing
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum


class ContentType(Enum):
    """Types of social media content"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    MIXED = "mixed"


class ViralityLevel(Enum):
    """Virality classification"""
    LOW = "low"              # Normal sharing
    MODERATE = "moderate"    # Some viral activity
    HIGH = "high"            # Viral content
    EXTREME = "extreme"      # Super-viral / likely coordinated


class ManipulationType(Enum):
    """Types of potential manipulation"""
    EMOTIONAL_APPEAL = "emotional_appeal"
    OUTRAGE_BAIT = "outrage_bait"
    FEAR_MONGERING = "fear_mongering"
    FALSE_URGENCY = "false_urgency"
    AUTHORITY_FRAUD = "authority_fraud"
    ASTROTURFING = "astroturfing"
    COORDINATED_AMPLIFICATION = "coordinated_amplification"


@dataclass
class ViralityMetrics:
    """Metrics about content virality"""
    share_velocity: float = 0.0  # Shares per hour
    engagement_ratio: float = 0.0  # Engagement / reach
    amplification_score: float = 0.0  # How much it's being boosted
    organic_score: float = 1.0  # Likelihood of organic spread
    bot_activity_score: float = 0.0  # Likelihood of bot involvement
    coordination_score: float = 0.0  # Likelihood of coordinated sharing


@dataclass
class SocialMediaAnalysis:
    """Analysis result for social media content"""
    content_type: ContentType
    virality_level: ViralityLevel
    virality_metrics: ViralityMetrics
    manipulation_types: List[ManipulationType] = field(default_factory=list)
    emotional_score: float = 0.0
    credibility_score: float = 0.5
    red_flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class EmotionalContentAnalyzer:
    """
    Analyze emotional manipulation in content.
    """
    
    # High-emotion trigger words
    OUTRAGE_WORDS = {
        'shocking', 'outrageous', 'disgusting', 'horrifying', 'unbelievable',
        'scandal', 'exposed', 'corrupt', 'evil', 'destroy', 'attack', 'betray',
        'shameful', 'disgrace', 'criminal', 'traitor', 'enemy', 'hate', 'worst'
    }
    
    FEAR_WORDS = {
        'danger', 'threat', 'warning', 'alert', 'emergency', 'crisis', 'deadly',
        'catastrophic', 'devastating', 'terrifying', 'alarming', 'critical',
        'urgent', 'imminent', 'collapse', 'disaster', 'chaos', 'death', 'kill'
    }
    
    URGENCY_WORDS = {
        'breaking', 'just in', 'developing', 'urgent', 'immediately', 'now',
        'hurry', 'limited time', 'act now', 'before it\'s too late', 'last chance',
        'share this', 'spread the word', 'everyone needs to know', 'going viral'
    }
    
    SENSATIONAL_PHRASES = [
        r'you won\'t believe',
        r'what .* doesn\'t want you to know',
        r'the truth about',
        r'exposed',
        r'finally revealed',
        r'they don\'t want you to see',
        r'mainstream media won\'t tell you',
        r'wake up',
        r'open your eyes',
        r'do your research',
        r'share before .* deleted',
        r'this changes everything',
    ]
    
    @classmethod
    def analyze_emotional_content(cls, text: str) -> Dict:
        """Analyze emotional manipulation in text"""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        result = {
            "outrage_score": 0.0,
            "fear_score": 0.0,
            "urgency_score": 0.0,
            "sensationalism_score": 0.0,
            "total_emotional_score": 0.0,
            "detected_triggers": [],
            "manipulation_types": []
        }
        
        # Count outrage words
        outrage_matches = words & cls.OUTRAGE_WORDS
        result["outrage_score"] = min(1.0, len(outrage_matches) / 3)
        if outrage_matches:
            result["detected_triggers"].extend(list(outrage_matches)[:5])
        
        # Count fear words
        fear_matches = words & cls.FEAR_WORDS
        result["fear_score"] = min(1.0, len(fear_matches) / 3)
        if fear_matches:
            result["detected_triggers"].extend(list(fear_matches)[:5])
        
        # Count urgency words
        urgency_matches = words & cls.URGENCY_WORDS
        result["urgency_score"] = min(1.0, len(urgency_matches) / 2)
        if urgency_matches:
            result["detected_triggers"].extend(list(urgency_matches)[:3])
        
        # Check sensational phrases
        phrase_count = 0
        for phrase in cls.SENSATIONAL_PHRASES:
            if re.search(phrase, text_lower):
                phrase_count += 1
                result["detected_triggers"].append(phrase)
        
        result["sensationalism_score"] = min(1.0, phrase_count / 2)
        
        # Calculate total emotional score
        result["total_emotional_score"] = (
            result["outrage_score"] * 0.3 +
            result["fear_score"] * 0.3 +
            result["urgency_score"] * 0.2 +
            result["sensationalism_score"] * 0.2
        )
        
        # Determine manipulation types
        if result["outrage_score"] > 0.5:
            result["manipulation_types"].append(ManipulationType.OUTRAGE_BAIT)
        if result["fear_score"] > 0.5:
            result["manipulation_types"].append(ManipulationType.FEAR_MONGERING)
        if result["urgency_score"] > 0.5:
            result["manipulation_types"].append(ManipulationType.FALSE_URGENCY)
        if result["sensationalism_score"] > 0.3:
            result["manipulation_types"].append(ManipulationType.EMOTIONAL_APPEAL)
        
        return result


class BotActivityDetector:
    """
    Detect potential bot or coordinated inauthentic behavior.
    """
    
    # Patterns suggesting automated/coordinated activity
    BOT_INDICATORS = [
        "identical_text_multiple_accounts",
        "unusual_posting_times",
        "high_volume_short_period",
        "new_account_high_engagement",
        "copy_paste_responses",
        "generic_profile_patterns",
        "synchronized_posting"
    ]
    
    @classmethod
    def analyze_account_patterns(cls, account_data: Dict) -> Dict:
        """Analyze account for bot-like behavior"""
        result = {
            "bot_probability": 0.0,
            "coordination_probability": 0.0,
            "indicators_found": [],
            "risk_level": "low"
        }
        
        bot_score = 0.0
        
        # Check account age vs activity
        account_age_days = account_data.get("account_age_days", 365)
        post_count = account_data.get("post_count", 0)
        
        if account_age_days < 30 and post_count > 100:
            bot_score += 0.3
            result["indicators_found"].append("new_account_high_activity")
        
        # Check posting patterns
        posts_per_day = account_data.get("posts_per_day", 1)
        if posts_per_day > 50:
            bot_score += 0.2
            result["indicators_found"].append("inhuman_posting_frequency")
        
        # Check engagement ratios
        followers = account_data.get("followers", 1)
        following = account_data.get("following", 1)
        
        if following > 0 and followers / following < 0.01:
            bot_score += 0.15
            result["indicators_found"].append("suspicious_follow_ratio")
        
        # Check for default/stock profile
        has_default_avatar = account_data.get("has_default_avatar", False)
        has_generic_bio = account_data.get("has_generic_bio", False)
        
        if has_default_avatar:
            bot_score += 0.1
            result["indicators_found"].append("default_avatar")
        
        if has_generic_bio:
            bot_score += 0.05
            result["indicators_found"].append("generic_bio")
        
        # Check for coordinated behavior
        similar_accounts = account_data.get("similar_accounts_posting_same", 0)
        if similar_accounts > 5:
            result["coordination_probability"] = min(1.0, similar_accounts / 20)
            result["indicators_found"].append("coordinated_posting_detected")
        
        result["bot_probability"] = min(1.0, bot_score)
        
        # Set risk level
        if bot_score > 0.6:
            result["risk_level"] = "high"
        elif bot_score > 0.3:
            result["risk_level"] = "moderate"
        else:
            result["risk_level"] = "low"
        
        return result


class ViralPatternAnalyzer:
    """
    Analyze viral spread patterns for signs of manipulation.
    """
    
    @classmethod
    def analyze_spread_pattern(cls, spread_data: Dict) -> ViralityMetrics:
        """Analyze how content is spreading"""
        metrics = ViralityMetrics()
        
        # Calculate share velocity
        shares = spread_data.get("total_shares", 0)
        hours_since_posted = max(1, spread_data.get("hours_since_posted", 1))
        metrics.share_velocity = shares / hours_since_posted
        
        # Calculate engagement ratio
        reach = spread_data.get("reach", 1)
        engagement = spread_data.get("engagement", 0)  # likes + comments + shares
        metrics.engagement_ratio = engagement / reach if reach > 0 else 0
        
        # Calculate amplification score
        original_follower_count = spread_data.get("original_poster_followers", 100)
        if original_follower_count > 0:
            amplification = shares / original_follower_count
            metrics.amplification_score = min(1.0, amplification / 10)
        
        # Estimate organic vs artificial spread
        # Organic spread typically follows exponential curve with slower start
        early_shares = spread_data.get("shares_first_hour", 0)
        total_shares = spread_data.get("total_shares", 1)
        
        early_share_ratio = early_shares / total_shares if total_shares > 0 else 0
        
        # Artificial boost often shows unnaturally high early shares
        if early_share_ratio > 0.5 and shares > 1000:
            metrics.organic_score = 0.3
            metrics.bot_activity_score = 0.5
        else:
            metrics.organic_score = 0.8
            metrics.bot_activity_score = 0.1
        
        # Check for coordination indicators
        unique_sharers = spread_data.get("unique_sharers", shares)
        if shares > 0 and unique_sharers / shares < 0.5:
            # Same accounts sharing multiple times
            metrics.coordination_score = 0.6
        
        return metrics


class MisinformationPatternDetector:
    """
    Detect common misinformation patterns.
    """
    
    MISINFO_PATTERNS = {
        "fake_expert": [
            r'dr\.?\s+\w+\s+says',
            r'scientists?\s+say',
            r'studies?\s+show',
            r'research\s+proves',
            r'experts?\s+agree',
        ],
        "appeal_to_hidden_knowledge": [
            r'they\s+don\'t\s+want\s+you\s+to\s+know',
            r'hidden\s+truth',
            r'what\s+.+\s+won\'t\s+tell\s+you',
            r'cover[\-\s]?up',
            r'suppressed\s+information',
        ],
        "false_dichotomy": [
            r'either\s+.+\s+or',
            r'you\'re\s+either\s+.+\s+or',
            r'there\s+are\s+only\s+two',
            r'pick\s+a\s+side',
        ],
        "bandwagon": [
            r'everyone\s+knows',
            r'millions\s+of\s+people',
            r'going\s+viral',
            r'trending',
            r'people\s+are\s+saying',
        ],
        "conspiracy_markers": [
            r'deep\s+state',
            r'new\s+world\s+order',
            r'global\s+elite',
            r'wake\s+up\s+sheeple',
            r'big\s+pharma',
            r'mainstream\s+media\s+lies',
            r'plandemic',
            r'false\s+flag',
        ]
    }
    
    @classmethod
    def detect_patterns(cls, text: str) -> Dict:
        """Detect misinformation patterns in text"""
        text_lower = text.lower()
        
        result = {
            "patterns_detected": [],
            "pattern_scores": {},
            "overall_risk_score": 0.0,
            "red_flags": []
        }
        
        total_score = 0.0
        pattern_weights = {
            "fake_expert": 0.15,
            "appeal_to_hidden_knowledge": 0.25,
            "false_dichotomy": 0.1,
            "bandwagon": 0.1,
            "conspiracy_markers": 0.4
        }
        
        for pattern_type, patterns in cls.MISINFO_PATTERNS.items():
            matches = 0
            matched_phrases = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
                    matched_phrases.append(pattern)
            
            if matches > 0:
                score = min(1.0, matches / len(patterns) * 2)
                result["pattern_scores"][pattern_type] = score
                result["patterns_detected"].append({
                    "type": pattern_type,
                    "matches": matched_phrases[:3],
                    "score": score
                })
                
                total_score += score * pattern_weights.get(pattern_type, 0.1)
        
        result["overall_risk_score"] = min(1.0, total_score)
        
        # Generate red flags
        if result["overall_risk_score"] > 0.5:
            result["red_flags"].append("High misinformation pattern density")
        
        if "conspiracy_markers" in result["pattern_scores"]:
            if result["pattern_scores"]["conspiracy_markers"] > 0.3:
                result["red_flags"].append("Contains conspiracy theory markers")
        
        if "appeal_to_hidden_knowledge" in result["pattern_scores"]:
            result["red_flags"].append("Appeals to hidden/suppressed knowledge")
        
        return result


class SocialMediaAnalyzer:
    """
    Main analyzer combining all social media analysis components.
    """
    
    def __init__(self):
        self.emotional_analyzer = EmotionalContentAnalyzer()
        self.bot_detector = BotActivityDetector()
        self.viral_analyzer = ViralPatternAnalyzer()
        self.misinfo_detector = MisinformationPatternDetector()
    
    def analyze(
        self,
        content: str,
        spread_data: Dict = None,
        account_data: Dict = None
    ) -> SocialMediaAnalysis:
        """
        Comprehensive social media content analysis.
        """
        spread_data = spread_data or {}
        account_data = account_data or {}
        
        # Determine content type
        content_type = self._determine_content_type(content, spread_data)
        
        # Analyze emotional manipulation
        emotional_analysis = self.emotional_analyzer.analyze_emotional_content(content)
        
        # Analyze virality
        virality_metrics = self.viral_analyzer.analyze_spread_pattern(spread_data)
        
        # Detect bot activity
        bot_analysis = self.bot_detector.analyze_account_patterns(account_data)
        
        # Update virality metrics with bot analysis
        virality_metrics.bot_activity_score = bot_analysis["bot_probability"]
        virality_metrics.coordination_score = bot_analysis["coordination_probability"]
        
        # Detect misinformation patterns
        misinfo_analysis = self.misinfo_detector.detect_patterns(content)
        
        # Determine virality level
        virality_level = self._determine_virality_level(virality_metrics)
        
        # Calculate credibility score
        credibility_score = self._calculate_credibility(
            emotional_analysis,
            bot_analysis,
            misinfo_analysis
        )
        
        # Compile red flags
        red_flags = []
        if emotional_analysis["total_emotional_score"] > 0.6:
            red_flags.append("High emotional manipulation detected")
        if bot_analysis["bot_probability"] > 0.5:
            red_flags.append("Likely bot or automated activity")
        if bot_analysis["coordination_probability"] > 0.5:
            red_flags.append("Possible coordinated amplification")
        red_flags.extend(misinfo_analysis["red_flags"])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            credibility_score,
            red_flags,
            virality_level
        )
        
        return SocialMediaAnalysis(
            content_type=content_type,
            virality_level=virality_level,
            virality_metrics=virality_metrics,
            manipulation_types=emotional_analysis["manipulation_types"],
            emotional_score=emotional_analysis["total_emotional_score"],
            credibility_score=credibility_score,
            red_flags=red_flags,
            recommendations=recommendations
        )
    
    def _determine_content_type(self, content: str, spread_data: Dict) -> ContentType:
        """Determine the type of content"""
        if spread_data.get("has_image"):
            if spread_data.get("has_video"):
                return ContentType.MIXED
            return ContentType.IMAGE
        if spread_data.get("has_video"):
            return ContentType.VIDEO
        if spread_data.get("has_link"):
            return ContentType.LINK
        return ContentType.TEXT
    
    def _determine_virality_level(self, metrics: ViralityMetrics) -> ViralityLevel:
        """Determine virality level from metrics"""
        if metrics.share_velocity > 10000:
            return ViralityLevel.EXTREME
        if metrics.share_velocity > 1000:
            return ViralityLevel.HIGH
        if metrics.share_velocity > 100:
            return ViralityLevel.MODERATE
        return ViralityLevel.LOW
    
    def _calculate_credibility(
        self,
        emotional: Dict,
        bot: Dict,
        misinfo: Dict
    ) -> float:
        """Calculate overall credibility score"""
        # Start with base credibility
        credibility = 1.0
        
        # Reduce for emotional manipulation
        credibility -= emotional["total_emotional_score"] * 0.3
        
        # Reduce for bot activity
        credibility -= bot["bot_probability"] * 0.2
        
        # Reduce for misinformation patterns
        credibility -= misinfo["overall_risk_score"] * 0.4
        
        return max(0.0, min(1.0, credibility))
    
    def _generate_recommendations(
        self,
        credibility: float,
        red_flags: List[str],
        virality: ViralityLevel
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if credibility < 0.3:
            recommendations.append("⚠️ High risk content - verify with authoritative sources before sharing")
        elif credibility < 0.5:
            recommendations.append("⚡ Exercise caution - multiple warning signs detected")
        
        if virality == ViralityLevel.EXTREME:
            recommendations.append("🔥 Viral content often spreads faster than it can be verified")
        
        if len(red_flags) >= 3:
            recommendations.append("🚩 Multiple red flags detected - skepticism advised")
        
        if "bot" in str(red_flags).lower():
            recommendations.append("🤖 Possible artificial amplification - check original sources")
        
        recommendations.append("✅ Cross-reference claims with established fact-checkers")
        
        return recommendations


__all__ = [
    'SocialMediaAnalyzer', 'SocialMediaAnalysis', 'ViralityMetrics',
    'EmotionalContentAnalyzer', 'BotActivityDetector', 'ViralPatternAnalyzer',
    'MisinformationPatternDetector', 'ContentType', 'ViralityLevel', 'ManipulationType'
]
