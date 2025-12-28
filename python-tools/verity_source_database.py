"""
Verity Source Credibility & Bias Database
==========================================
Comprehensive database of source credibility ratings.

Data compiled from:
- Media Bias/Fact Check (MBFC)
- NewsGuard
- AllSides
- Ad Fontes Media
- Academic research

This is CRITICAL for accurate fact-checking.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class FactualReporting(Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MOSTLY_FACTUAL = "mostly_factual"
    MIXED = "mixed"
    LOW = "low"
    VERY_LOW = "very_low"


class BiasRating(Enum):
    EXTREME_LEFT = "extreme_left"
    LEFT = "left"
    LEFT_CENTER = "left_center"
    CENTER = "center"
    RIGHT_CENTER = "right_center"
    RIGHT = "right"
    EXTREME_RIGHT = "extreme_right"
    PRO_SCIENCE = "pro_science"
    CONSPIRACY = "conspiracy"
    PSEUDOSCIENCE = "pseudoscience"
    SATIRE = "satire"


class CredibilityTier(Enum):
    TIER_1 = 1  # Highly credible - can be cited as primary source
    TIER_2 = 2  # Generally reliable - good for corroboration
    TIER_3 = 3  # Mixed reliability - use with caution
    TIER_4 = 4  # Unreliable - not suitable for fact-checking
    TIER_5 = 5  # Known misinformation source


@dataclass
class SourceProfile:
    name: str
    domain: str
    factual_reporting: FactualReporting
    bias_rating: BiasRating
    credibility_tier: CredibilityTier
    credibility_score: float  # 0-100
    description: str
    founded: Optional[int] = None
    country: str = "USA"
    type: str = "news"  # news, academic, government, blog, social, etc.


# Comprehensive source database
SOURCE_DATABASE: Dict[str, SourceProfile] = {
    # ===========================================
    # TIER 1: HIGHLY CREDIBLE SOURCES
    # ===========================================
    
    # Academic & Scientific
    "nature.com": SourceProfile(
        name="Nature",
        domain="nature.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=98,
        description="Premier peer-reviewed scientific journal",
        founded=1869,
        country="UK",
        type="academic"
    ),
    "science.org": SourceProfile(
        name="Science Magazine",
        domain="science.org",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=98,
        description="Peer-reviewed scientific journal by AAAS",
        founded=1880,
        type="academic"
    ),
    "thelancet.com": SourceProfile(
        name="The Lancet",
        domain="thelancet.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=97,
        description="Leading medical journal",
        founded=1823,
        country="UK",
        type="academic"
    ),
    "nejm.org": SourceProfile(
        name="New England Journal of Medicine",
        domain="nejm.org",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=98,
        description="Premier medical journal",
        founded=1812,
        type="academic"
    ),
    "pubmed.ncbi.nlm.nih.gov": SourceProfile(
        name="PubMed",
        domain="pubmed.ncbi.nlm.nih.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=97,
        description="NIH medical literature database",
        type="database"
    ),
    "arxiv.org": SourceProfile(
        name="arXiv",
        domain="arxiv.org",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=92,
        description="Preprint server for scientific papers",
        founded=1991,
        type="academic"
    ),
    
    # Government Sources
    "cdc.gov": SourceProfile(
        name="Centers for Disease Control",
        domain="cdc.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=96,
        description="US federal health agency",
        founded=1946,
        type="government"
    ),
    "who.int": SourceProfile(
        name="World Health Organization",
        domain="who.int",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=95,
        description="UN health agency",
        founded=1948,
        country="International",
        type="government"
    ),
    "nasa.gov": SourceProfile(
        name="NASA",
        domain="nasa.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=98,
        description="US space agency",
        founded=1958,
        type="government"
    ),
    "fda.gov": SourceProfile(
        name="Food and Drug Administration",
        domain="fda.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=94,
        description="US regulatory agency",
        founded=1906,
        type="government"
    ),
    "nih.gov": SourceProfile(
        name="National Institutes of Health",
        domain="nih.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.PRO_SCIENCE,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=97,
        description="US medical research agency",
        founded=1887,
        type="government"
    ),
    "census.gov": SourceProfile(
        name="US Census Bureau",
        domain="census.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=96,
        description="US statistical agency",
        founded=1902,
        type="government"
    ),
    "bls.gov": SourceProfile(
        name="Bureau of Labor Statistics",
        domain="bls.gov",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=96,
        description="US labor statistics",
        founded=1884,
        type="government"
    ),
    
    # Wire Services
    "apnews.com": SourceProfile(
        name="Associated Press",
        domain="apnews.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=94,
        description="Major wire service",
        founded=1846,
        type="news"
    ),
    "reuters.com": SourceProfile(
        name="Reuters",
        domain="reuters.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=94,
        description="International wire service",
        founded=1851,
        country="UK",
        type="news"
    ),
    "afp.com": SourceProfile(
        name="Agence France-Presse",
        domain="afp.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=93,
        description="French wire service",
        founded=1835,
        country="France",
        type="news"
    ),
    
    # Fact-Checkers
    "snopes.com": SourceProfile(
        name="Snopes",
        domain="snopes.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=92,
        description="Fact-checking website",
        founded=1994,
        type="fact_check"
    ),
    "politifact.com": SourceProfile(
        name="PolitiFact",
        domain="politifact.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=91,
        description="Political fact-checking",
        founded=2007,
        type="fact_check"
    ),
    "factcheck.org": SourceProfile(
        name="FactCheck.org",
        domain="factcheck.org",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=93,
        description="Nonpartisan fact-checking",
        founded=2003,
        type="fact_check"
    ),
    "fullfact.org": SourceProfile(
        name="Full Fact",
        domain="fullfact.org",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_1,
        credibility_score=92,
        description="UK fact-checking charity",
        founded=2010,
        country="UK",
        type="fact_check"
    ),
    
    # ===========================================
    # TIER 2: GENERALLY RELIABLE
    # ===========================================
    
    # Major News - Left-Center
    "nytimes.com": SourceProfile(
        name="New York Times",
        domain="nytimes.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=87,
        description="Major US newspaper",
        founded=1851,
        type="news"
    ),
    "washingtonpost.com": SourceProfile(
        name="Washington Post",
        domain="washingtonpost.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=86,
        description="Major US newspaper",
        founded=1877,
        type="news"
    ),
    "theguardian.com": SourceProfile(
        name="The Guardian",
        domain="theguardian.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=85,
        description="UK newspaper",
        founded=1821,
        country="UK",
        type="news"
    ),
    "npr.org": SourceProfile(
        name="NPR",
        domain="npr.org",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=88,
        description="US public radio",
        founded=1970,
        type="news"
    ),
    "bbc.com": SourceProfile(
        name="BBC",
        domain="bbc.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.LEFT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=88,
        description="UK public broadcaster",
        founded=1922,
        country="UK",
        type="news"
    ),
    
    # Major News - Center
    "economist.com": SourceProfile(
        name="The Economist",
        domain="economist.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=90,
        description="Weekly news magazine",
        founded=1843,
        country="UK",
        type="news"
    ),
    "bloomberg.com": SourceProfile(
        name="Bloomberg",
        domain="bloomberg.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=87,
        description="Financial news",
        founded=1981,
        type="news"
    ),
    
    # Major News - Right-Center
    "wsj.com": SourceProfile(
        name="Wall Street Journal",
        domain="wsj.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.RIGHT_CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=86,
        description="Financial newspaper",
        founded=1889,
        type="news"
    ),
    
    # Knowledge Sources
    "wikipedia.org": SourceProfile(
        name="Wikipedia",
        domain="wikipedia.org",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=82,
        description="Online encyclopedia",
        founded=2001,
        type="encyclopedia"
    ),
    "britannica.com": SourceProfile(
        name="Encyclopedia Britannica",
        domain="britannica.com",
        factual_reporting=FactualReporting.VERY_HIGH,
        bias_rating=BiasRating.CENTER,
        credibility_tier=CredibilityTier.TIER_2,
        credibility_score=92,
        description="Traditional encyclopedia",
        founded=1768,
        country="UK",
        type="encyclopedia"
    ),
    
    # ===========================================
    # TIER 3: MIXED RELIABILITY
    # ===========================================
    
    # News - Left Bias
    "cnn.com": SourceProfile(
        name="CNN",
        domain="cnn.com",
        factual_reporting=FactualReporting.MOSTLY_FACTUAL,
        bias_rating=BiasRating.LEFT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=72,
        description="24-hour news network",
        founded=1980,
        type="news"
    ),
    "msnbc.com": SourceProfile(
        name="MSNBC",
        domain="msnbc.com",
        factual_reporting=FactualReporting.MIXED,
        bias_rating=BiasRating.LEFT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=65,
        description="News and opinion",
        founded=1996,
        type="news"
    ),
    "huffpost.com": SourceProfile(
        name="HuffPost",
        domain="huffpost.com",
        factual_reporting=FactualReporting.MOSTLY_FACTUAL,
        bias_rating=BiasRating.LEFT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=68,
        description="Online news and opinion",
        founded=2005,
        type="news"
    ),
    "vox.com": SourceProfile(
        name="Vox",
        domain="vox.com",
        factual_reporting=FactualReporting.HIGH,
        bias_rating=BiasRating.LEFT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=75,
        description="Explanatory journalism",
        founded=2014,
        type="news"
    ),
    
    # News - Right Bias
    "foxnews.com": SourceProfile(
        name="Fox News",
        domain="foxnews.com",
        factual_reporting=FactualReporting.MIXED,
        bias_rating=BiasRating.RIGHT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=62,
        description="24-hour news network",
        founded=1996,
        type="news"
    ),
    "nypost.com": SourceProfile(
        name="New York Post",
        domain="nypost.com",
        factual_reporting=FactualReporting.MIXED,
        bias_rating=BiasRating.RIGHT_CENTER,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=65,
        description="Tabloid newspaper",
        founded=1801,
        type="news"
    ),
    "dailymail.co.uk": SourceProfile(
        name="Daily Mail",
        domain="dailymail.co.uk",
        factual_reporting=FactualReporting.LOW,
        bias_rating=BiasRating.RIGHT,
        credibility_tier=CredibilityTier.TIER_3,
        credibility_score=55,
        description="UK tabloid",
        founded=1896,
        country="UK",
        type="news"
    ),
    
    # ===========================================
    # TIER 4: UNRELIABLE
    # ===========================================
    
    # Extreme Left
    "dailykos.com": SourceProfile(
        name="Daily Kos",
        domain="dailykos.com",
        factual_reporting=FactualReporting.MIXED,
        bias_rating=BiasRating.EXTREME_LEFT,
        credibility_tier=CredibilityTier.TIER_4,
        credibility_score=45,
        description="Progressive blog",
        founded=2002,
        type="blog"
    ),
    
    # Extreme Right
    "breitbart.com": SourceProfile(
        name="Breitbart",
        domain="breitbart.com",
        factual_reporting=FactualReporting.LOW,
        bias_rating=BiasRating.EXTREME_RIGHT,
        credibility_tier=CredibilityTier.TIER_4,
        credibility_score=35,
        description="Far-right news",
        founded=2007,
        type="news"
    ),
    "oann.com": SourceProfile(
        name="OAN",
        domain="oann.com",
        factual_reporting=FactualReporting.LOW,
        bias_rating=BiasRating.EXTREME_RIGHT,
        credibility_tier=CredibilityTier.TIER_4,
        credibility_score=30,
        description="Right-wing network",
        founded=2013,
        type="news"
    ),
    "newsmax.com": SourceProfile(
        name="Newsmax",
        domain="newsmax.com",
        factual_reporting=FactualReporting.LOW,
        bias_rating=BiasRating.EXTREME_RIGHT,
        credibility_tier=CredibilityTier.TIER_4,
        credibility_score=38,
        description="Right-wing network",
        founded=1998,
        type="news"
    ),
    "dailywire.com": SourceProfile(
        name="Daily Wire",
        domain="dailywire.com",
        factual_reporting=FactualReporting.MIXED,
        bias_rating=BiasRating.RIGHT,
        credibility_tier=CredibilityTier.TIER_4,
        credibility_score=48,
        description="Conservative news",
        founded=2015,
        type="news"
    ),
    
    # ===========================================
    # TIER 5: KNOWN MISINFORMATION
    # ===========================================
    
    "naturalnews.com": SourceProfile(
        name="Natural News",
        domain="naturalnews.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.PSEUDOSCIENCE,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=8,
        description="Conspiracy and pseudoscience",
        type="conspiracy"
    ),
    "infowars.com": SourceProfile(
        name="InfoWars",
        domain="infowars.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.CONSPIRACY,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=5,
        description="Conspiracy theories",
        founded=1999,
        type="conspiracy"
    ),
    "thegatewaypundit.com": SourceProfile(
        name="Gateway Pundit",
        domain="thegatewaypundit.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.EXTREME_RIGHT,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=10,
        description="Far-right misinformation",
        founded=2004,
        type="conspiracy"
    ),
    "beforeitsnews.com": SourceProfile(
        name="Before It's News",
        domain="beforeitsnews.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.CONSPIRACY,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=3,
        description="User-generated conspiracy content",
        founded=2008,
        type="conspiracy"
    ),
    "thebabylonbee.com": SourceProfile(
        name="Babylon Bee",
        domain="thebabylonbee.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.SATIRE,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=5,
        description="Satire site (often mistaken for news)",
        founded=2016,
        type="satire"
    ),
    "theonion.com": SourceProfile(
        name="The Onion",
        domain="theonion.com",
        factual_reporting=FactualReporting.VERY_LOW,
        bias_rating=BiasRating.SATIRE,
        credibility_tier=CredibilityTier.TIER_5,
        credibility_score=5,
        description="Satire site",
        founded=1988,
        type="satire"
    ),
}


def get_source_profile(domain: str) -> Optional[SourceProfile]:
    """Get source profile by domain"""
    # Normalize domain
    domain = domain.lower().strip()
    domain = domain.replace("www.", "")
    
    # Direct match
    if domain in SOURCE_DATABASE:
        return SOURCE_DATABASE[domain]
    
    # Try partial matches
    for db_domain, profile in SOURCE_DATABASE.items():
        if db_domain in domain or domain in db_domain:
            return profile
    
    return None


def get_credibility_score(domain: str) -> float:
    """Get credibility score (0-100) for a domain"""
    profile = get_source_profile(domain)
    if profile:
        return profile.credibility_score
    return 50.0  # Unknown sources get middle score


def get_bias_rating(domain: str) -> Optional[BiasRating]:
    """Get bias rating for a domain"""
    profile = get_source_profile(domain)
    if profile:
        return profile.bias_rating
    return None


def is_reliable_source(domain: str, min_tier: CredibilityTier = CredibilityTier.TIER_2) -> bool:
    """Check if source meets minimum reliability tier"""
    profile = get_source_profile(domain)
    if profile:
        return profile.credibility_tier.value <= min_tier.value
    return False


def get_sources_by_tier(tier: CredibilityTier) -> List[SourceProfile]:
    """Get all sources in a specific tier"""
    return [p for p in SOURCE_DATABASE.values() if p.credibility_tier == tier]


def get_fact_check_sources() -> List[SourceProfile]:
    """Get all fact-checking sources"""
    return [p for p in SOURCE_DATABASE.values() if p.type == "fact_check"]


def get_academic_sources() -> List[SourceProfile]:
    """Get all academic sources"""
    return [p for p in SOURCE_DATABASE.values() if p.type == "academic"]


__all__ = [
    'SourceProfile', 'FactualReporting', 'BiasRating', 'CredibilityTier',
    'SOURCE_DATABASE', 'get_source_profile', 'get_credibility_score',
    'get_bias_rating', 'is_reliable_source', 'get_sources_by_tier',
    'get_fact_check_sources', 'get_academic_sources'
]
