#!/usr/bin/env python3
"""
VERITY API v10 - COMPREHENSIVE STRESS TEST SUITE
=================================================
50+ exhaustive test cases covering ALL verification capabilities.

Test Categories:
1. NUANCED CLAIMS (health, economics, environment, technology)
2. CLEAR TRUE CLAIMS (scientific facts, historical events)
3. CLEAR FALSE CLAIMS (debunked myths, conspiracy theories)
4. URL VERIFICATION (news articles, research papers)
5. RESEARCH PAPER VERIFICATION (DOI, arXiv, PubMed)
6. STATISTICAL CLAIMS (data interpretation, percentages)
7. RECENT EVENTS (2024-2026 news verification)
8. ADVERSARIAL CLAIMS (misleading, out-of-context, edge cases)
9. LONG-FORM DOCUMENTS (multi-paragraph verification)
10. RANDOMLY GENERATED CONTENT (stress testing)

This tests the FULL 21-point verification system recommended for best-in-class.
"""

import httpx
import time
import json
import random
import string
import asyncio
from datetime import datetime
from typing import Dict, Any, List

API_URL = "http://localhost:8000"
VERIFY_ENDPOINT = f"{API_URL}/verify"  # Correct endpoint from api_server_v10.py
HEADERS = {"X-API-Key": "demo-key-12345"}

# =============================================================================
# TEST CATEGORIES - 50+ EXHAUSTIVE TEST CASES
# =============================================================================

CATEGORY_1_NUANCED_HEALTH = [
    {
        "id": "NH-001",
        "category": "Nuanced Health",
        "claim": """According to recent systematic reviews, moderate coffee consumption (3-4 cups per day) 
        has been associated with reduced risk of cardiovascular disease, type 2 diabetes, and certain 
        neurodegenerative conditions. However, excessive consumption exceeding 6 cups daily may lead to 
        anxiety, sleep disturbances, and potential cardiovascular stress in susceptible individuals. 
        The relationship between coffee and health outcomes is modified by genetic polymorphisms in 
        CYP1A2 and other caffeine metabolism genes.""",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Complex health claim with genetic nuance"
    },
    {
        "id": "NH-002",
        "category": "Nuanced Health",
        "claim": """Intermittent fasting protocols including 16:8 time-restricted eating have demonstrated 
        metabolic benefits in randomized controlled trials, showing improvements in insulin sensitivity, 
        reduction in inflammatory markers (CRP, IL-6), and modest weight loss. However, the long-term 
        effects on muscle mass preservation, hormonal balance in women, and sustainability remain 
        subjects of ongoing research with conflicting evidence.""",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Nutrition claim with scientific references"
    },
    {
        "id": "NH-003", 
        "category": "Nuanced Health",
        "claim": """Red meat consumption is definitively linked to increased all-cause mortality and should 
        be completely eliminated from human diets according to all major health organizations worldwide.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Oversimplified absolute claim on nuanced topic"
    },
]

CATEGORY_2_NUANCED_ECONOMICS = [
    {
        "id": "NE-001",
        "category": "Nuanced Economics",
        "claim": """The implementation of Universal Basic Income (UBI) programs, as tested in Finland's 
        2017-2018 experiment with 2,000 unemployed individuals receiving €560/month, showed improved 
        well-being and mental health scores but did not significantly increase employment rates compared 
        to the control group. The Stockton Economic Empowerment Demonstration (SEED) in California 
        showed recipients were more likely to obtain full-time employment, suggesting program design 
        and local economic conditions significantly moderate outcomes.""",
        "expected": "true",
        "difficulty": "expert",
        "notes": "Factual claim about specific UBI experiments"
    },
    {
        "id": "NE-002",
        "category": "Nuanced Economics",
        "claim": """Minimum wage increases invariably lead to widespread job losses and business closures, 
        as demonstrated consistently across all economic studies and historical implementations globally.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Oversimplified absolute claim on contested topic"
    },
    {
        "id": "NE-003",
        "category": "Nuanced Economics",
        "claim": """Cryptocurrency markets, particularly Bitcoin and Ethereum, exhibit characteristics of 
        both legitimate financial innovation (decentralized finance, smart contracts, cross-border 
        transactions) and speculative bubbles with significant fraud risk (rug pulls, Ponzi schemes, 
        market manipulation). Regulatory approaches vary significantly across jurisdictions, with the 
        EU's MiCA framework and US SEC enforcement actions representing divergent strategies.""",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Balanced crypto assessment"
    },
]

CATEGORY_3_NUANCED_ENVIRONMENT = [
    {
        "id": "ENV-001",
        "category": "Nuanced Environment",
        "claim": """Electric vehicles produce zero emissions during operation but their total lifecycle 
        carbon footprint depends on electricity grid composition, battery manufacturing processes, 
        and vehicle lifespan. A 2024 meta-analysis in Nature Climate Change found EVs reduce lifecycle 
        emissions by 50-70% compared to internal combustion vehicles in most European countries, but 
        only 20-30% in coal-heavy grids like Poland. Battery recycling infrastructure remains limited, 
        with only 5% of lithium-ion batteries currently recycled globally.""",
        "expected": "true",
        "difficulty": "expert",
        "notes": "Nuanced EV environmental impact"
    },
    {
        "id": "ENV-002",
        "category": "Nuanced Environment",
        "claim": """Nuclear power is completely safe with zero environmental impact and should replace 
        all fossil fuel and renewable energy sources immediately as the only viable solution to 
        climate change.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Oversimplified nuclear claim"
    },
    {
        "id": "ENV-003",
        "category": "Nuanced Environment",
        "claim": """Organic farming is always better for the environment than conventional agriculture 
        in every measurable metric including land use, water consumption, and carbon emissions per 
        unit of food produced.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Absolute claim on nuanced agricultural topic"
    },
]

CATEGORY_4_CLEAR_TRUE_SCIENTIFIC = [
    {
        "id": "TS-001",
        "category": "True Scientific",
        "claim": """The speed of light in a vacuum is approximately 299,792,458 meters per second, 
        a fundamental constant denoted as 'c' in physics. This value was precisely measured and 
        defined by the International Bureau of Weights and Measures in 1983, and forms the basis 
        for the definition of the meter in the SI system.""",
        "expected": "true",
        "difficulty": "easy",
        "notes": "Fundamental physics constant"
    },
    {
        "id": "TS-002",
        "category": "True Scientific",
        "claim": """The human genome contains approximately 3 billion base pairs of DNA organized 
        into 23 pairs of chromosomes. The Human Genome Project, completed in 2003, identified 
        approximately 20,000-25,000 protein-coding genes, significantly fewer than the initial 
        estimates of 100,000 genes.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Established genomics fact"
    },
    {
        "id": "TS-003",
        "category": "True Scientific",
        "claim": """Water molecules consist of two hydrogen atoms covalently bonded to one oxygen 
        atom, with a bond angle of approximately 104.5 degrees. This molecular geometry gives 
        water its unique properties including high surface tension, high specific heat capacity, 
        and the unusual property of ice being less dense than liquid water.""",
        "expected": "true",
        "difficulty": "easy",
        "notes": "Basic chemistry fact"
    },
    {
        "id": "TS-004",
        "category": "True Scientific",
        "claim": """Antibiotics are effective treatments for bacterial infections but have no 
        therapeutic effect against viral infections. The overuse and misuse of antibiotics has 
        led to the emergence of antibiotic-resistant bacteria, identified by the WHO as one of 
        the top 10 global public health threats.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Public health fact"
    },
]

CATEGORY_5_CLEAR_TRUE_HISTORICAL = [
    {
        "id": "TH-001",
        "category": "True Historical",
        "claim": """The Apollo 11 mission successfully landed the first humans on the Moon on 
        July 20, 1969. Commander Neil Armstrong and Lunar Module Pilot Buzz Aldrin landed the 
        Apollo Lunar Module Eagle while Command Module Pilot Michael Collins remained in lunar 
        orbit. Armstrong became the first human to walk on the Moon, followed by Aldrin 
        approximately 19 minutes later.""",
        "expected": "true",
        "difficulty": "easy",
        "notes": "Established historical event"
    },
    {
        "id": "TH-002",
        "category": "True Historical",
        "claim": """The Berlin Wall, officially known as the Anti-Fascist Protection Rampart by 
        the East German government, was constructed beginning on August 13, 1961 and fell on 
        November 9, 1989. The wall physically divided Berlin for 28 years and became a symbol 
        of the Iron Curtain separating Western Europe from the Eastern Bloc.""",
        "expected": "true",
        "difficulty": "easy",
        "notes": "20th century historical fact"
    },
    {
        "id": "TH-003",
        "category": "True Historical",
        "claim": """The 2024 Nobel Prize in Physics was awarded to John J. Hopfield and Geoffrey 
        E. Hinton for their foundational discoveries and inventions that enabled machine learning 
        with artificial neural networks. This marked the first time the physics prize recognized 
        contributions to artificial intelligence and computational neuroscience.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Recent verifiable event (2024)"
    },
]

CATEGORY_6_CLEAR_FALSE_MYTHS = [
    {
        "id": "FM-001",
        "category": "False Myths",
        "claim": """The Great Wall of China is visible from space with the naked eye, making it 
        the only man-made structure visible from orbit. NASA astronauts have confirmed this 
        repeatedly in official reports since the Apollo missions.""",
        "expected": "false",
        "difficulty": "easy",
        "notes": "Debunked myth - Wall not visible from space"
    },
    {
        "id": "FM-002",
        "category": "False Myths",
        "claim": """Humans only use 10% of their brain capacity, and unlocking the remaining 90% 
        could grant supernatural abilities including telekinesis, perfect memory, and heightened 
        intelligence. This has been confirmed by neuroscientific research using brain imaging 
        techniques.""",
        "expected": "false",
        "difficulty": "easy",
        "notes": "Classic debunked neuromyth"
    },
    {
        "id": "FM-003",
        "category": "False Myths",
        "claim": """The flat Earth theory is supported by measurable evidence including the 
        inability to detect curvature at sea level, the behavior of water always seeking level, 
        and the impossibility of continuous orbital motion. Modern physics calculations prove 
        that a spherical Earth rotating at over 1,000 mph would fling all objects off its surface.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Conspiracy theory with pseudo-scientific language"
    },
    {
        "id": "FM-004",
        "category": "False Myths",
        "claim": """Vaccines cause autism, as demonstrated by the groundbreaking research of 
        Dr. Andrew Wakefield published in The Lancet in 1998. Subsequent studies by the CDC 
        have been covered up but confirmed the MMR-autism connection in internal documents 
        released by whistleblowers.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Dangerous medical misinformation"
    },
    {
        "id": "FM-005",
        "category": "False Myths",
        "claim": """5G cellular networks operate at frequencies that cause COVID-19 infections 
        and weaken the human immune system. This has been confirmed by leaked documents from 
        telecommunications companies and independent research by concerned citizens.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Recent debunked conspiracy"
    },
]

CATEGORY_7_URL_VERIFICATION = [
    {
        "id": "URL-001",
        "category": "URL Verification",
        "claim": "https://www.who.int/news-room/fact-sheets/detail/antibiotic-resistance",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Legitimate WHO resource",
        "type": "url"
    },
    {
        "id": "URL-002",
        "category": "URL Verification",
        "claim": "https://www.nature.com/articles/s41586-024-07315-7",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Nature journal article (may or may not exist)",
        "type": "url"
    },
    {
        "id": "URL-003",
        "category": "URL Verification",
        "claim": """Verify this news article for accuracy and bias: 
        https://www.reuters.com/technology/artificial-intelligence/""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "News source analysis",
        "type": "url"
    },
]

CATEGORY_8_RESEARCH_PAPERS = [
    {
        "id": "RP-001",
        "category": "Research Papers",
        "claim": """Verify the findings of this paper: DOI:10.1038/s41586-020-2649-2 
        "Language models are few-shot learners" by Brown et al., which claims that GPT-3 
        with 175 billion parameters demonstrates strong few-shot learning capabilities 
        across diverse NLP tasks without fine-tuning.""",
        "expected": "true",
        "difficulty": "hard",
        "notes": "GPT-3 paper verification"
    },
    {
        "id": "RP-002",
        "category": "Research Papers",
        "claim": """According to arXiv:2303.08774, the paper titled "GPT-4 Technical Report" 
        by OpenAI describes a large multimodal model capable of processing both text and 
        image inputs, demonstrating human-level performance on various professional and 
        academic benchmarks including passing the bar exam with a score in the top 10%.""",
        "expected": "true",
        "difficulty": "hard",
        "notes": "GPT-4 paper verification"
    },
    {
        "id": "RP-003",
        "category": "Research Papers",
        "claim": """The IPCC Sixth Assessment Report (AR6) Climate Change 2023 Synthesis Report 
        states that global surface temperature has increased by approximately 1.1°C since 
        pre-industrial times (1850-1900), with the increase largely attributable to human 
        activities including fossil fuel combustion and land use changes.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "IPCC report verification"
    },
    {
        "id": "RP-004",
        "category": "Research Papers",
        "claim": """PubMed ID: 12345678 describes a study that found drinking eight glasses of 
        water per day is medically necessary for all adults and prevents cancer. This has been 
        replicated in over 500 peer-reviewed studies with statistical significance p < 0.001.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Likely fabricated or misrepresented study"
    },
]

CATEGORY_9_STATISTICAL = [
    {
        "id": "ST-001",
        "category": "Statistical Claims",
        "claim": """According to the World Bank's 2023 data, global extreme poverty rate 
        (defined as living on less than $2.15/day in 2017 PPP) fell from approximately 
        38% in 1990 to about 8.5% in 2023, representing a reduction of nearly 1.2 billion 
        people living in extreme poverty despite population growth.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Verifiable World Bank statistics"
    },
    {
        "id": "ST-002",
        "category": "Statistical Claims",
        "claim": """Violent crime in the United States has decreased by approximately 50% 
        since its peak in the early 1990s, according to FBI Uniform Crime Report data. 
        However, public perception of crime has not followed this trend, with Gallup polls 
        showing most Americans believe crime is increasing.""",
        "expected": "true",
        "difficulty": "hard",
        "notes": "Counterintuitive but true crime statistics"
    },
    {
        "id": "ST-003",
        "category": "Statistical Claims",
        "claim": """99.7% of climate scientists agree that human-caused climate change is real, 
        as evidenced by a peer-reviewed study published in Environmental Research Letters 
        analyzing over 88,000 climate-related papers from 2012-2020.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Climate consensus study (actual figure ~97-99%)"
    },
    {
        "id": "ST-004",
        "category": "Statistical Claims",
        "claim": """According to official government statistics, unemployment in the United 
        States dropped to 0.5% in January 2025, representing the lowest unemployment rate 
        ever recorded in any developed nation's history.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Fabricated statistic"
    },
]

CATEGORY_10_RECENT_EVENTS_2024_2025 = [
    {
        "id": "RE-001",
        "category": "Recent Events 2024-2025",
        "claim": """The 2024 Summer Olympics were held in Paris, France, running from July 26 
        to August 11, 2024. The United States topped the medal count with 126 total medals 
        (40 gold), followed by China with 91 medals (40 gold). Notable events included 
        swimming, athletics, and the debut of breaking as an Olympic sport.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Verifiable recent event"
    },
    {
        "id": "RE-002",
        "category": "Recent Events 2024-2025",
        "claim": """In November 2024, Donald Trump won the United States presidential election, 
        defeating the Democratic candidate. The election was certified by Congress in 
        January 2025, and Trump was inaugurated as the 47th President on January 20, 2025.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Verifiable recent political event"
    },
    {
        "id": "RE-003",
        "category": "Recent Events 2024-2025",
        "claim": """SpaceX successfully launched the Starship rocket on its fifth integrated 
        flight test (IFT-5) in October 2024, achieving the historic first catch of the 
        Super Heavy booster using the launch tower's mechanical arms, nicknamed 'chopsticks.'""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Verifiable SpaceX milestone"
    },
    {
        "id": "RE-004",
        "category": "Recent Events 2024-2025",
        "claim": """Amazon acquired Microsoft in a landmark $2 trillion merger announced in 
        December 2024, creating the world's largest technology company. The merger was 
        approved by EU and US regulators without conditions in January 2025.""",
        "expected": "false",
        "difficulty": "easy",
        "notes": "Fabricated corporate event"
    },
]

CATEGORY_11_ADVERSARIAL = [
    {
        "id": "ADV-001",
        "category": "Adversarial",
        "claim": """Many scientists agree that evolution is just a theory. As such, it should 
        be taught alongside alternative explanations like intelligent design in schools. 
        Even Darwin himself expressed doubts about his own theory on his deathbed.""",
        "expected": "false",
        "difficulty": "hard",
        "notes": "Misleading use of 'theory' + false deathbed claim"
    },
    {
        "id": "ADV-002",
        "category": "Adversarial",
        "claim": """Studies show that drinking a glass of red wine daily is as beneficial as 
        one hour of exercise. The French Paradox proves that wine consumption prevents heart 
        disease, and doctors recommend wine as part of a healthy lifestyle.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Exaggerated claim with partial truths"
    },
    {
        "id": "ADV-003",
        "category": "Adversarial",
        "claim": """According to some researchers, GMO foods cause cancer in laboratory animals. 
        The Séralini study from 2012 demonstrated tumor growth in rats fed GM corn, and 
        although it was retracted, it was later republished in another journal, validating 
        the original findings.""",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Real retracted study with complex publication history"
    },
    {
        "id": "ADV-004",
        "category": "Adversarial",
        "claim": """Research from Stanford University proves that organic food has no nutritional 
        benefits compared to conventional food. Therefore, organic farming is a marketing scam 
        with no environmental or health advantages whatsoever.""",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Real study extrapolated to false conclusion"
    },
    {
        "id": "ADV-005",
        "category": "Adversarial",
        "claim": """The Pfizer CEO Albert Bourla stated publicly that 'I'm not sure if mRNA 
        vaccines work' in a leaked video from a board meeting. This admission has been 
        censored by mainstream media but is available on alternative news platforms.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Fabricated quote attributed to real person"
    },
]

CATEGORY_12_LONG_FORM_DOCUMENT = [
    {
        "id": "LF-001",
        "category": "Long Form Document",
        "claim": """
        EXECUTIVE SUMMARY: CLIMATE INTERVENTION ASSESSMENT

        This document presents findings from a comprehensive 5-year study on geoengineering 
        approaches to climate change mitigation. Our research team analyzed three primary 
        intervention strategies:

        1. STRATOSPHERIC AEROSOL INJECTION (SAI)
        The injection of sulfate aerosols into the stratosphere could reduce global 
        temperatures by 1-2°C within 2-3 years. However, regional precipitation patterns 
        would be significantly altered, potentially causing drought in monsoon-dependent 
        regions. Annual costs estimated at $2-8 billion USD.

        2. MARINE CLOUD BRIGHTENING (MCB)
        Spraying sea salt particles to increase cloud reflectivity shows promise for 
        regional cooling. Pilot studies off the California coast demonstrated 5-10% 
        increase in cloud albedo. Long-term ecological impacts on marine ecosystems 
        remain unclear.

        3. DIRECT AIR CAPTURE (DAC)
        Current DAC facilities remove approximately 4,000 tons CO2 annually at costs of 
        $400-600 per ton. Scaling to meaningful climate impact (1 gigaton/year) would 
        require 250,000 facilities and approximately $500 billion annual investment.

        CONCLUSION: While these technologies show technical feasibility, governance 
        frameworks, ethical considerations, and unintended consequences require extensive 
        further study before deployment recommendations can be made.
        """,
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Complex multi-topic document with reasonable claims"
    },
    {
        "id": "LF-002",
        "category": "Long Form Document",
        "claim": """
        MARKET ANALYSIS REPORT: AI INDUSTRY TRENDS Q4 2024

        The artificial intelligence market continues exponential growth with several key 
        developments in the final quarter of 2024:

        LARGE LANGUAGE MODELS:
        - OpenAI launched GPT-4 Turbo with 128K context window and improved reasoning
        - Anthropic's Claude 3.5 Sonnet achieved industry-leading benchmarks
        - Google DeepMind's Gemini models integrated across Google products
        - Meta released Llama 3.1 with 405 billion parameters as open source

        MARKET VALUATION:
        - OpenAI valued at approximately $150 billion after latest funding round
        - Anthropic secured $4 billion investment from Amazon
        - Global AI market projected to reach $1.8 trillion by 2030

        REGULATORY DEVELOPMENTS:
        - EU AI Act implementation began with initial provisions
        - US Executive Order on AI Safety established new guidelines
        - China released interim measures for generative AI services

        INDUSTRY CONCERNS:
        - AI safety researchers warn of capability acceleration
        - Copyright lawsuits against AI training on protected content
        - Job displacement in creative and knowledge work sectors

        This report represents the most accurate assessment of AI industry trends as of 
        December 2024. All figures sourced from company announcements and industry analysts.
        """,
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Industry report with mostly accurate figures"
    },
]

CATEGORY_13_RANDOMLY_GENERATED = [
    {
        "id": "RNG-001",
        "category": "Randomly Generated",
        "claim": "Professor James T. Middlethwaite of the Thornburg Institute discovered in 2023 "
                 "that exposure to infrared radiation from common household appliances increases "
                 "melatonin production by 47%, potentially curing insomnia in 89% of participants.",
        "expected": "mixed",
        "difficulty": "hard",
        "notes": "Plausible-sounding fabrication"
    },
    {
        "id": "RNG-002",
        "category": "Randomly Generated",
        "claim": "The Pemberton-Clarke Effect, first described in the Journal of Advanced "
                 "Materials Science (Vol. 47, Issue 3, 2024), demonstrates that nano-crystalline "
                 "structures exhibit self-healing properties at room temperature, revolutionizing "
                 "the development of damage-resistant consumer electronics.",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Academic-style fabrication"
    },
    {
        "id": "RNG-003",
        "category": "Randomly Generated",
        "claim": "According to declassified NSA documents released in February 2024, the "
                 "ECHELON surveillance program processed an average of 2.7 billion communications "
                 "daily between 2018-2023, with 94% of intercepted data originating from allied "
                 "nations including the UK, Germany, and Japan.",
        "expected": "mixed",
        "difficulty": "expert",
        "notes": "Government conspiracy-style claim"
    },
]

CATEGORY_14_TECH_CLAIMS = [
    {
        "id": "TECH-001",
        "category": "Technology Claims",
        "claim": """Quantum computers using IBM's 1000+ qubit Eagle processor can break 
        RSA-2048 encryption in under one hour, rendering all current banking security 
        obsolete as of 2024.""",
        "expected": "false",
        "difficulty": "hard",
        "notes": "Exaggerated quantum computing capability"
    },
    {
        "id": "TECH-002",
        "category": "Technology Claims",
        "claim": """Tesla's Full Self-Driving (FSD) software achieved Level 5 autonomous 
        driving certification from the NHTSA in 2024, allowing Tesla vehicles to operate 
        without any human intervention on all road types and conditions.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Fabricated regulatory claim"
    },
    {
        "id": "TECH-003",
        "category": "Technology Claims",
        "claim": """NVIDIA's H100 Tensor Core GPU, released in 2022, features 80 billion 
        transistors, up to 3958 TFLOPS of FP8 performance, and 80GB of HBM3 memory. It 
        is currently the most widely used GPU for training large AI models including 
        GPT-4 and Claude.""",
        "expected": "true",
        "difficulty": "medium",
        "notes": "Accurate technical specifications"
    },
    {
        "id": "TECH-004",
        "category": "Technology Claims",
        "claim": """Blockchain technology fundamentally cannot scale to handle more than 
        7 transactions per second, making it inherently unsuitable for global payment 
        systems. This limitation is mathematically proven and cannot be overcome.""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Outdated/incorrect Bitcoin limitation applied broadly"
    },
]

CATEGORY_15_EDGE_CASES = [
    {
        "id": "EDGE-001",
        "category": "Edge Cases",
        "claim": "",
        "expected": "error",
        "difficulty": "easy",
        "notes": "Empty claim test"
    },
    {
        "id": "EDGE-002",
        "category": "Edge Cases",
        "claim": "The sky is blue.",
        "expected": "true",
        "difficulty": "easy",
        "notes": "Minimal claim"
    },
    {
        "id": "EDGE-003",
        "category": "Edge Cases",
        "claim": "".join(random.choices(string.ascii_letters + " ", k=500)),
        "expected": "error",
        "difficulty": "easy",
        "notes": "Random string test"
    },
    {
        "id": "EDGE-004",
        "category": "Edge Cases",
        "claim": "Is water wet? This is actually a question not a claim.",
        "expected": "mixed",
        "difficulty": "easy",
        "notes": "Question instead of claim"
    },
    {
        "id": "EDGE-005",
        "category": "Edge Cases",
        "claim": """🚀 According to 👨‍🔬 scientists 🧬 at 🏛️ Harvard, eating 🍕 pizza 
        daily can increase 💪 muscle mass by 500% 📈 within 2 weeks! #Science #Gains""",
        "expected": "false",
        "difficulty": "medium",
        "notes": "Emoji-laden social media style"
    },
]

# =============================================================================
# COMBINE ALL CATEGORIES
# =============================================================================

ALL_TESTS = (
    CATEGORY_1_NUANCED_HEALTH +
    CATEGORY_2_NUANCED_ECONOMICS +
    CATEGORY_3_NUANCED_ENVIRONMENT +
    CATEGORY_4_CLEAR_TRUE_SCIENTIFIC +
    CATEGORY_5_CLEAR_TRUE_HISTORICAL +
    CATEGORY_6_CLEAR_FALSE_MYTHS +
    CATEGORY_7_URL_VERIFICATION +
    CATEGORY_8_RESEARCH_PAPERS +
    CATEGORY_9_STATISTICAL +
    CATEGORY_10_RECENT_EVENTS_2024_2025 +
    CATEGORY_11_ADVERSARIAL +
    CATEGORY_12_LONG_FORM_DOCUMENT +
    CATEGORY_13_RANDOMLY_GENERATED +
    CATEGORY_14_TECH_CLAIMS +
    CATEGORY_15_EDGE_CASES
)


# =============================================================================
# TEST RUNNER FUNCTIONS
# =============================================================================

async def run_single_test(client: httpx.AsyncClient, test: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single verification test."""
    test_id = test["id"]
    claim = test["claim"]
    expected = test["expected"]
    category = test["category"]
    
    # Skip empty claims for certain edge case tests
    if not claim or len(claim.strip()) < 3:
        return {
            "id": test_id,
            "category": category,
            "expected": expected,
            "actual": "error",
            "passed": expected == "error",
            "error": "Empty or too short claim",
            "duration": 0
        }
    
    start_time = time.time()
    try:
        # Determine endpoint based on test type
        test_type = test.get("type", "text")
        
        if test_type == "url":
            response = await client.post(
                VERIFY_ENDPOINT,
                headers=HEADERS,
                json={
                    "claim": claim,
                    "mode": "full",
                    "type": "url"
                },
                timeout=300.0  # 5 minutes for comprehensive verification
            )
        else:
            response = await client.post(
                VERIFY_ENDPOINT,
                headers=HEADERS,
                json={
                    "claim": claim,
                    "mode": "full"
                },
                timeout=300.0  # 5 minutes for comprehensive verification
            )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract verdict
            verdict = data.get("verdict", "unknown").lower()
            
            # Normalize verdicts
            if "true" in verdict or verdict == "verified":
                actual = "true"
            elif "false" in verdict or verdict == "debunked" or "refuted" in verdict:
                actual = "false"
            elif "mixed" in verdict or "partial" in verdict or "nuanced" in verdict:
                actual = "mixed"
            else:
                actual = "unknown"
            
            # Check if passed
            passed = actual == expected
            
            return {
                "id": test_id,
                "category": category,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "confidence": data.get("confidence", 0),
                "nuance_score": data.get("nuance_analysis", {}).get("nuance_score", 0),
                "providers_used": data.get("providers_used", []),
                "duration": duration,
                "claim_preview": claim[:100] + "..." if len(claim) > 100 else claim
            }
        else:
            return {
                "id": test_id,
                "category": category,
                "expected": expected,
                "actual": "error",
                "passed": expected == "error",
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "duration": time.time() - start_time
            }
            
    except Exception as e:
        return {
            "id": test_id,
            "category": category,
            "expected": expected,
            "actual": "error",
            "passed": expected == "error",
            "error": str(e),
            "duration": time.time() - start_time
        }


async def run_all_tests(tests: List[Dict], batch_size: int = 3) -> List[Dict]:
    """Run all tests with rate limiting."""
    results = []
    total = len(tests)
    
    print(f"\n{'='*80}")
    print(f"STARTING COMPREHENSIVE TEST SUITE: {total} TESTS")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient() as client:
        for i, test in enumerate(tests):
            print(f"[{i+1}/{total}] Testing {test['id']}: {test['category']}")
            
            result = await run_single_test(client, test)
            results.append(result)
            
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"         {status} - Expected: {test['expected']}, Got: {result['actual']}")
            
            if result.get("error"):
                print(f"         Error: {result['error'][:80]}")
            
            # Rate limiting - wait between tests
            if i < total - 1:
                await asyncio.sleep(1.5)
    
    return results


def analyze_results(results: List[Dict]) -> Dict[str, Any]:
    """Analyze test results and generate comprehensive report."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    
    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0, "tests": []}
        if r["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
        categories[cat]["tests"].append(r)
    
    # Calculate accuracy by expected result type
    true_tests = [r for r in results if r["expected"] == "true"]
    false_tests = [r for r in results if r["expected"] == "false"]
    mixed_tests = [r for r in results if r["expected"] == "mixed"]
    
    true_accuracy = sum(1 for r in true_tests if r["passed"]) / len(true_tests) * 100 if true_tests else 0
    false_accuracy = sum(1 for r in false_tests if r["passed"]) / len(false_tests) * 100 if false_tests else 0
    mixed_accuracy = sum(1 for r in mixed_tests if r["passed"]) / len(mixed_tests) * 100 if mixed_tests else 0
    
    # Difficulty breakdown
    difficulties = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = {"passed": 0, "failed": 0}
        if r["passed"]:
            difficulties[diff]["passed"] += 1
        else:
            difficulties[diff]["failed"] += 1
    
    # Calculate average metrics
    durations = [r["duration"] for r in results if r.get("duration")]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    confidences = [r["confidence"] for r in results if r.get("confidence")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "overall_accuracy": passed / total * 100 if total > 0 else 0
        },
        "accuracy_by_type": {
            "true_claims": {"count": len(true_tests), "accuracy": true_accuracy},
            "false_claims": {"count": len(false_tests), "accuracy": false_accuracy},
            "mixed_claims": {"count": len(mixed_tests), "accuracy": mixed_accuracy}
        },
        "categories": categories,
        "difficulties": difficulties,
        "metrics": {
            "avg_duration_seconds": avg_duration,
            "avg_confidence": avg_confidence,
            "total_duration_minutes": sum(durations) / 60 if durations else 0
        },
        "failed_tests": [r for r in results if not r["passed"]]
    }


def print_report(analysis: Dict[str, Any]):
    """Print comprehensive test report."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT - VERITY API v10")
    print("="*80)
    
    s = analysis["summary"]
    print(f"\n📊 OVERALL RESULTS")
    print(f"   Total Tests:     {s['total_tests']}")
    print(f"   Passed:          {s['passed']} ✓")
    print(f"   Failed:          {s['failed']} ✗")
    print(f"   Overall Accuracy: {s['overall_accuracy']:.1f}%")
    
    print(f"\n📈 ACCURACY BY CLAIM TYPE")
    at = analysis["accuracy_by_type"]
    print(f"   TRUE Claims:     {at['true_claims']['accuracy']:.1f}% ({at['true_claims']['count']} tests)")
    print(f"   FALSE Claims:    {at['false_claims']['accuracy']:.1f}% ({at['false_claims']['count']} tests)")
    print(f"   MIXED Claims:    {at['mixed_claims']['accuracy']:.1f}% ({at['mixed_claims']['count']} tests)")
    
    print(f"\n📁 RESULTS BY CATEGORY")
    for cat, data in sorted(analysis["categories"].items()):
        total = data["passed"] + data["failed"]
        acc = data["passed"] / total * 100 if total > 0 else 0
        status = "✓" if acc >= 80 else "⚠" if acc >= 60 else "✗"
        print(f"   {status} {cat}: {acc:.0f}% ({data['passed']}/{total})")
    
    print(f"\n🎯 RESULTS BY DIFFICULTY")
    for diff, data in sorted(analysis["difficulties"].items()):
        total = data["passed"] + data["failed"]
        acc = data["passed"] / total * 100 if total > 0 else 0
        print(f"   {diff}: {acc:.0f}% ({data['passed']}/{total})")
    
    m = analysis["metrics"]
    print(f"\n⏱️ PERFORMANCE METRICS")
    print(f"   Avg Response Time: {m['avg_duration_seconds']:.2f}s")
    print(f"   Avg Confidence:    {m['avg_confidence']:.1f}%")
    print(f"   Total Test Time:   {m['total_duration_minutes']:.1f} minutes")
    
    if analysis["failed_tests"]:
        print(f"\n❌ FAILED TESTS ({len(analysis['failed_tests'])})")
        for f in analysis["failed_tests"][:10]:
            print(f"\n   [{f['id']}] {f['category']}")
            print(f"   Expected: {f['expected']}, Got: {f['actual']}")
            if f.get("claim_preview"):
                print(f"   Claim: {f['claim_preview'][:80]}...")
    
    print("\n" + "="*80)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main test execution."""
    print(f"\nVerity API v10 Comprehensive Test Suite")
    print(f"Test Count: {len(ALL_TESTS)} exhaustive test cases")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = await run_all_tests(ALL_TESTS)
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Print report
    print_report(analysis)
    
    # Save results to JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_count": len(ALL_TESTS),
        "analysis": analysis,
        "raw_results": results
    }
    
    with open("comprehensive_test_results.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nResults saved to comprehensive_test_results.json")
    
    return analysis


if __name__ == "__main__":
    asyncio.run(main())
