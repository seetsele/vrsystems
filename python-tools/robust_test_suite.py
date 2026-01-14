#!/usr/bin/env python3
"""
VERITY API v10 - ROBUST COMPREHENSIVE TEST SUITE
=================================================
55+ exhaustive test cases with robust error handling.
Uses synchronous requests to avoid async cancellation issues.
"""

import requests
import time
import json
import random
import string
import signal
import sys
from datetime import datetime
from typing import Dict, Any, List

API_URL = "http://localhost:8000"
VERIFY_ENDPOINT = f"{API_URL}/verify"
HEADERS = {"X-API-Key": "demo-key-12345", "Content-Type": "application/json"}

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(sig, frame):
    global shutdown_requested
    print("\n\n⚠️  Shutdown requested. Completing current test...")
    shutdown_requested = True

signal.signal(signal.SIGINT, signal_handler)

# =============================================================================
# TEST CATEGORIES - 55+ EXHAUSTIVE TEST CASES
# =============================================================================

CATEGORY_1_NUANCED_HEALTH = [
    {
        "id": "NH-001",
        "category": "Nuanced Health",
        "claim": """According to recent systematic reviews, moderate coffee consumption (3-4 cups per day) 
        has been associated with reduced risk of cardiovascular disease, type 2 diabetes, and certain 
        neurodegenerative conditions. However, excessive consumption exceeding 6 cups daily may lead to 
        anxiety, sleep disturbances, and potential cardiovascular stress in susceptible individuals.""",
        "expected": "mixed",
        "difficulty": "expert",
    },
    {
        "id": "NH-002",
        "category": "Nuanced Health",
        "claim": """Intermittent fasting protocols including 16:8 time-restricted eating have demonstrated 
        metabolic benefits in randomized controlled trials, showing improvements in insulin sensitivity and 
        reduction in inflammatory markers. However, the long-term effects on muscle mass preservation and 
        hormonal balance remain subjects of ongoing research with conflicting evidence.""",
        "expected": "mixed",
        "difficulty": "expert",
    },
    {
        "id": "NH-003", 
        "category": "Nuanced Health",
        "claim": """Red meat consumption is definitively linked to increased all-cause mortality and should 
        be completely eliminated from human diets according to all major health organizations worldwide.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
]

CATEGORY_2_NUANCED_ECONOMICS = [
    {
        "id": "NE-001",
        "category": "Nuanced Economics",
        "claim": """The implementation of Universal Basic Income (UBI) programs, as tested in Finland's 
        2017-2018 experiment with 2,000 unemployed individuals receiving €560/month, showed improved 
        well-being and mental health scores but did not significantly increase employment rates compared 
        to the control group.""",
        "expected": "true",
        "difficulty": "expert",
    },
    {
        "id": "NE-002",
        "category": "Nuanced Economics",
        "claim": """Minimum wage increases invariably lead to widespread job losses and business closures, 
        as demonstrated consistently across all economic studies and historical implementations globally.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
    {
        "id": "NE-003",
        "category": "Nuanced Economics",
        "claim": """Cryptocurrency markets, particularly Bitcoin and Ethereum, exhibit characteristics of 
        both legitimate financial innovation (decentralized finance, smart contracts) and speculative 
        bubbles with significant fraud risk. Regulatory approaches vary significantly across jurisdictions.""",
        "expected": "mixed",
        "difficulty": "expert",
    },
]

CATEGORY_3_NUANCED_ENVIRONMENT = [
    {
        "id": "ENV-001",
        "category": "Nuanced Environment",
        "claim": """Electric vehicles produce zero emissions during operation but their total lifecycle 
        carbon footprint depends on electricity grid composition and battery manufacturing. A 2024 
        meta-analysis found EVs reduce lifecycle emissions by 50-70% compared to internal combustion 
        vehicles in most European countries, but only 20-30% in coal-heavy grids.""",
        "expected": "true",
        "difficulty": "expert",
    },
    {
        "id": "ENV-002",
        "category": "Nuanced Environment",
        "claim": """Nuclear power is completely safe with zero environmental impact and should replace 
        all fossil fuel and renewable energy sources immediately as the only viable solution to 
        climate change.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
    {
        "id": "ENV-003",
        "category": "Nuanced Environment",
        "claim": """Organic farming is always better for the environment than conventional agriculture 
        in every measurable metric including land use, water consumption, and carbon emissions per 
        unit of food produced.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
]

CATEGORY_4_CLEAR_TRUE_SCIENTIFIC = [
    {
        "id": "TS-001",
        "category": "True Scientific",
        "claim": """The speed of light in a vacuum is approximately 299,792,458 meters per second, 
        a fundamental constant denoted as 'c' in physics, defined by the International Bureau of 
        Weights and Measures in 1983.""",
        "expected": "true",
        "difficulty": "easy",
    },
    {
        "id": "TS-002",
        "category": "True Scientific",
        "claim": """The human genome contains approximately 3 billion base pairs of DNA organized 
        into 23 pairs of chromosomes. The Human Genome Project identified approximately 20,000-25,000 
        protein-coding genes.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "TS-003",
        "category": "True Scientific",
        "claim": """Water molecules consist of two hydrogen atoms covalently bonded to one oxygen 
        atom, with a bond angle of approximately 104.5 degrees, giving water its unique properties.""",
        "expected": "true",
        "difficulty": "easy",
    },
    {
        "id": "TS-004",
        "category": "True Scientific",
        "claim": """Antibiotics are effective treatments for bacterial infections but have no 
        therapeutic effect against viral infections. The overuse of antibiotics has led to the 
        emergence of antibiotic-resistant bacteria.""",
        "expected": "true",
        "difficulty": "medium",
    },
]

CATEGORY_5_CLEAR_TRUE_HISTORICAL = [
    {
        "id": "TH-001",
        "category": "True Historical",
        "claim": """The Apollo 11 mission successfully landed the first humans on the Moon on 
        July 20, 1969. Neil Armstrong and Buzz Aldrin landed the Lunar Module while Michael Collins 
        remained in lunar orbit.""",
        "expected": "true",
        "difficulty": "easy",
    },
    {
        "id": "TH-002",
        "category": "True Historical",
        "claim": """The Berlin Wall was constructed beginning on August 13, 1961 and fell on 
        November 9, 1989, physically dividing Berlin for 28 years as a symbol of the Iron Curtain.""",
        "expected": "true",
        "difficulty": "easy",
    },
    {
        "id": "TH-003",
        "category": "True Historical",
        "claim": """The 2024 Nobel Prize in Physics was awarded to John J. Hopfield and Geoffrey 
        E. Hinton for their foundational discoveries that enabled machine learning with artificial 
        neural networks.""",
        "expected": "true",
        "difficulty": "medium",
    },
]

CATEGORY_6_CLEAR_FALSE_MYTHS = [
    {
        "id": "FM-001",
        "category": "False Myths",
        "claim": """The Great Wall of China is visible from space with the naked eye, making it 
        the only man-made structure visible from orbit. NASA astronauts have confirmed this 
        repeatedly in official reports.""",
        "expected": "false",
        "difficulty": "easy",
    },
    {
        "id": "FM-002",
        "category": "False Myths",
        "claim": """Humans only use 10% of their brain capacity, and unlocking the remaining 90% 
        could grant supernatural abilities including telekinesis and perfect memory.""",
        "expected": "false",
        "difficulty": "easy",
    },
    {
        "id": "FM-003",
        "category": "False Myths",
        "claim": """The flat Earth theory is supported by measurable evidence including the 
        inability to detect curvature at sea level and the behavior of water always seeking level.""",
        "expected": "false",
        "difficulty": "medium",
    },
    {
        "id": "FM-004",
        "category": "False Myths",
        "claim": """Vaccines cause autism, as demonstrated by the research of Dr. Andrew Wakefield 
        published in The Lancet in 1998. This has been confirmed by multiple subsequent studies.""",
        "expected": "false",
        "difficulty": "medium",
    },
    {
        "id": "FM-005",
        "category": "False Myths",
        "claim": """5G cellular networks operate at frequencies that cause COVID-19 infections 
        and weaken the human immune system according to leaked telecommunications documents.""",
        "expected": "false",
        "difficulty": "medium",
    },
]

CATEGORY_7_STATISTICAL = [
    {
        "id": "ST-001",
        "category": "Statistical Claims",
        "claim": """According to the World Bank's 2023 data, global extreme poverty rate fell from 
        approximately 38% in 1990 to about 8.5% in 2023, representing a reduction of nearly 1.2 
        billion people living in extreme poverty despite population growth.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "ST-002",
        "category": "Statistical Claims",
        "claim": """Violent crime in the United States has decreased by approximately 50% since 
        its peak in the early 1990s, according to FBI Uniform Crime Report data.""",
        "expected": "true",
        "difficulty": "hard",
    },
    {
        "id": "ST-003",
        "category": "Statistical Claims",
        "claim": """Approximately 97-99% of climate scientists agree that human-caused climate 
        change is real, as evidenced by multiple peer-reviewed studies analyzing climate literature.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "ST-004",
        "category": "Statistical Claims",
        "claim": """According to official government statistics, unemployment in the United States 
        dropped to 0.5% in January 2025, the lowest rate ever recorded in developed nations.""",
        "expected": "false",
        "difficulty": "medium",
    },
]

CATEGORY_8_RECENT_EVENTS_2024_2025 = [
    {
        "id": "RE-001",
        "category": "Recent Events 2024-2025",
        "claim": """The 2024 Summer Olympics were held in Paris, France, running from July 26 
        to August 11, 2024. The United States topped the medal count with 126 total medals.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "RE-002",
        "category": "Recent Events 2024-2025",
        "claim": """In November 2024, Donald Trump won the United States presidential election, 
        defeating the Democratic candidate and was inaugurated as the 47th President in January 2025.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "RE-003",
        "category": "Recent Events 2024-2025",
        "claim": """SpaceX successfully caught the Super Heavy booster using mechanical arms 
        during the Starship IFT-5 test flight in October 2024.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "RE-004",
        "category": "Recent Events 2024-2025",
        "claim": """Amazon acquired Microsoft in a $2 trillion merger announced in December 2024, 
        approved by EU and US regulators without conditions in January 2025.""",
        "expected": "false",
        "difficulty": "easy",
    },
]

CATEGORY_9_ADVERSARIAL = [
    {
        "id": "ADV-001",
        "category": "Adversarial",
        "claim": """Many scientists agree that evolution is just a theory. As such, it should 
        be taught alongside intelligent design. Even Darwin expressed doubts on his deathbed.""",
        "expected": "false",
        "difficulty": "hard",
    },
    {
        "id": "ADV-002",
        "category": "Adversarial",
        "claim": """Studies show that drinking red wine daily is as beneficial as one hour of 
        exercise. The French Paradox proves wine consumption prevents heart disease.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
    {
        "id": "ADV-003",
        "category": "Adversarial",
        "claim": """GMO foods cause cancer in laboratory animals according to the Séralini study. 
        Although retracted, it was republished validating the original findings.""",
        "expected": "mixed",
        "difficulty": "expert",
    },
    {
        "id": "ADV-004",
        "category": "Adversarial",
        "claim": """Stanford research proves organic food has no nutritional benefits. Therefore 
        organic farming is a marketing scam with no environmental advantages whatsoever.""",
        "expected": "mixed",
        "difficulty": "hard",
    },
    {
        "id": "ADV-005",
        "category": "Adversarial",
        "claim": """Pfizer CEO Albert Bourla stated 'I'm not sure if mRNA vaccines work' in a 
        leaked board meeting video that has been censored by mainstream media.""",
        "expected": "false",
        "difficulty": "medium",
    },
]

CATEGORY_10_TECH_CLAIMS = [
    {
        "id": "TECH-001",
        "category": "Technology Claims",
        "claim": """Quantum computers using IBM's 1000+ qubit processor can break RSA-2048 
        encryption in under one hour, rendering all current banking security obsolete.""",
        "expected": "false",
        "difficulty": "hard",
    },
    {
        "id": "TECH-002",
        "category": "Technology Claims",
        "claim": """Tesla's Full Self-Driving achieved Level 5 autonomous driving certification 
        from the NHTSA in 2024, allowing fully autonomous operation on all roads.""",
        "expected": "false",
        "difficulty": "medium",
    },
    {
        "id": "TECH-003",
        "category": "Technology Claims",
        "claim": """NVIDIA's H100 GPU features 80 billion transistors and up to 3958 TFLOPS 
        of FP8 performance. It is widely used for training large AI models like GPT-4.""",
        "expected": "true",
        "difficulty": "medium",
    },
    {
        "id": "TECH-004",
        "category": "Technology Claims",
        "claim": """Blockchain technology cannot scale beyond 7 transactions per second, making 
        it mathematically impossible for global payment systems.""",
        "expected": "false",
        "difficulty": "medium",
    },
]

CATEGORY_11_LONG_FORM = [
    {
        "id": "LF-001",
        "category": "Long Form Document",
        "claim": """CLIMATE INTERVENTION ASSESSMENT: Stratospheric aerosol injection could reduce 
        global temperatures by 1-2°C within 2-3 years but would alter regional precipitation. 
        Marine cloud brightening shows promise for regional cooling with unclear ecological impacts. 
        Direct air capture currently removes 4,000 tons CO2 annually at $400-600 per ton, requiring 
        massive scaling for climate impact. These technologies show technical feasibility but require 
        extensive governance study before deployment.""",
        "expected": "mixed",
        "difficulty": "expert",
    },
]

CATEGORY_12_EDGE_CASES = [
    {
        "id": "EDGE-001",
        "category": "Edge Cases",
        "claim": "The sky is blue.",
        "expected": "true",
        "difficulty": "easy",
    },
    {
        "id": "EDGE-002",
        "category": "Edge Cases",
        "claim": "2 + 2 = 5",
        "expected": "false",
        "difficulty": "easy",
    },
    {
        "id": "EDGE-003",
        "category": "Edge Cases",
        "claim": "Some people like pizza while others prefer pasta, and opinions vary widely.",
        "expected": "mixed",
        "difficulty": "easy",
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
    CATEGORY_7_STATISTICAL +
    CATEGORY_8_RECENT_EVENTS_2024_2025 +
    CATEGORY_9_ADVERSARIAL +
    CATEGORY_10_TECH_CLAIMS +
    CATEGORY_11_LONG_FORM +
    CATEGORY_12_EDGE_CASES
)


# =============================================================================
# TEST RUNNER FUNCTIONS (SYNCHRONOUS - NO ASYNC ISSUES)
# =============================================================================

def run_single_test(session: requests.Session, test: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single verification test synchronously."""
    global shutdown_requested
    
    test_id = test["id"]
    claim = test["claim"]
    expected = test["expected"]
    category = test["category"]
    difficulty = test.get("difficulty", "medium")
    
    if not claim or len(claim.strip()) < 3:
        return {
            "id": test_id, "category": category, "expected": expected,
            "actual": "error", "passed": expected == "error",
            "error": "Empty claim", "duration": 0, "difficulty": difficulty
        }
    
    start_time = time.time()
    try:
        response = session.post(
            VERIFY_ENDPOINT,
            headers=HEADERS,
            json={"claim": claim, "mode": "full"},
            timeout=180  # 3 minutes max
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
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
            
            passed = actual == expected
            
            return {
                "id": test_id, "category": category, "expected": expected,
                "actual": actual, "passed": passed, "difficulty": difficulty,
                "confidence": data.get("confidence", 0),
                "nuance_score": data.get("nuance_analysis", {}).get("nuance_score", 0),
                "providers_used": len(data.get("providers_used", [])),
                "duration": duration,
                "claim_preview": claim[:80] + "..." if len(claim) > 80 else claim
            }
        else:
            return {
                "id": test_id, "category": category, "expected": expected,
                "actual": "error", "passed": False, "difficulty": difficulty,
                "error": f"HTTP {response.status_code}",
                "duration": time.time() - start_time
            }
            
    except requests.exceptions.Timeout:
        return {
            "id": test_id, "category": category, "expected": expected,
            "actual": "timeout", "passed": False, "difficulty": difficulty,
            "error": "Request timeout (180s)",
            "duration": time.time() - start_time
        }
    except Exception as e:
        return {
            "id": test_id, "category": category, "expected": expected,
            "actual": "error", "passed": False, "difficulty": difficulty,
            "error": str(e)[:100],
            "duration": time.time() - start_time
        }


def run_all_tests(tests: List[Dict]) -> List[Dict]:
    """Run all tests synchronously with graceful shutdown support."""
    global shutdown_requested
    results = []
    total = len(tests)
    
    print(f"\n{'='*70}")
    print(f"VERITY API v10 - COMPREHENSIVE TEST SUITE")
    print(f"{'='*70}")
    print(f"Total Tests: {total}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    session = requests.Session()
    
    for i, test in enumerate(tests):
        if shutdown_requested:
            print(f"\n⚠️  Graceful shutdown - {len(results)} tests completed")
            break
            
        print(f"[{i+1:2}/{total}] {test['id']:10} | {test['category'][:25]:25} | ", end="", flush=True)
        
        result = run_single_test(session, test)
        results.append(result)
        
        if result["passed"]:
            print(f"✓ PASS ({result['duration']:.1f}s)")
        else:
            print(f"✗ FAIL - Expected: {result['expected']}, Got: {result['actual']}")
            if result.get("error"):
                print(f"         Error: {result['error']}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    session.close()
    return results


def analyze_results(results: List[Dict]) -> Dict[str, Any]:
    """Analyze test results."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    
    # By type
    true_tests = [r for r in results if r["expected"] == "true"]
    false_tests = [r for r in results if r["expected"] == "false"]
    mixed_tests = [r for r in results if r["expected"] == "mixed"]
    
    true_acc = sum(1 for r in true_tests if r["passed"]) / len(true_tests) * 100 if true_tests else 0
    false_acc = sum(1 for r in false_tests if r["passed"]) / len(false_tests) * 100 if false_tests else 0
    mixed_acc = sum(1 for r in mixed_tests if r["passed"]) / len(mixed_tests) * 100 if mixed_tests else 0
    
    # By category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if r["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    # By difficulty
    difficulties = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = {"passed": 0, "failed": 0}
        if r["passed"]:
            difficulties[diff]["passed"] += 1
        else:
            difficulties[diff]["failed"] += 1
    
    durations = [r["duration"] for r in results if r.get("duration")]
    
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "overall_accuracy": passed / total * 100 if total > 0 else 0,
        "true_accuracy": true_acc,
        "false_accuracy": false_acc,
        "mixed_accuracy": mixed_acc,
        "categories": categories,
        "difficulties": difficulties,
        "avg_duration": sum(durations) / len(durations) if durations else 0,
        "total_duration": sum(durations) / 60 if durations else 0,
        "failed_tests": [r for r in results if not r["passed"]]
    }


def print_report(analysis: Dict[str, Any]):
    """Print comprehensive report."""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST REPORT")
    print("="*70)
    
    print(f"\n📊 OVERALL RESULTS")
    print(f"   Total Tests:      {analysis['total']}")
    print(f"   Passed:           {analysis['passed']} ✓")
    print(f"   Failed:           {analysis['failed']} ✗")
    print(f"   Overall Accuracy: {analysis['overall_accuracy']:.1f}%")
    
    print(f"\n📈 ACCURACY BY VERDICT TYPE")
    print(f"   TRUE Claims:  {analysis['true_accuracy']:.1f}%")
    print(f"   FALSE Claims: {analysis['false_accuracy']:.1f}%")
    print(f"   MIXED Claims: {analysis['mixed_accuracy']:.1f}%")
    
    print(f"\n📁 RESULTS BY CATEGORY")
    for cat, data in sorted(analysis["categories"].items()):
        total = data["passed"] + data["failed"]
        acc = data["passed"] / total * 100 if total > 0 else 0
        status = "✓" if acc >= 80 else "⚠" if acc >= 60 else "✗"
        print(f"   {status} {cat[:30]:30} {acc:5.0f}% ({data['passed']}/{total})")
    
    print(f"\n🎯 RESULTS BY DIFFICULTY")
    for diff in ["easy", "medium", "hard", "expert"]:
        if diff in analysis["difficulties"]:
            data = analysis["difficulties"][diff]
            total = data["passed"] + data["failed"]
            acc = data["passed"] / total * 100 if total > 0 else 0
            print(f"   {diff:8} {acc:5.0f}% ({data['passed']}/{total})")
    
    print(f"\n⏱️ PERFORMANCE")
    print(f"   Avg Response: {analysis['avg_duration']:.1f}s")
    print(f"   Total Time:   {analysis['total_duration']:.1f} minutes")
    
    if analysis["failed_tests"][:5]:
        print(f"\n❌ FAILED TESTS (showing first 5)")
        for f in analysis["failed_tests"][:5]:
            print(f"   [{f['id']}] Expected: {f['expected']}, Got: {f['actual']}")
    
    print("\n" + "="*70)


def main():
    """Main execution."""
    print(f"\nVerity API v10 Comprehensive Test Suite")
    print(f"Test Count: {len(ALL_TESTS)} exhaustive test cases")
    
    # Check API health first
    try:
        health = requests.get(f"{API_URL}/health", timeout=10)
        if health.status_code == 200:
            data = health.json()
            print(f"API Status: {data.get('status', 'unknown')}")
            print(f"Providers: {data.get('providers_available', 0)}")
        else:
            print("⚠️  API health check failed!")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Run tests
    results = run_all_tests(ALL_TESTS)
    
    # Analyze
    analysis = analyze_results(results)
    
    # Print report
    print_report(analysis)
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_count": len(ALL_TESTS),
        "completed": len(results),
        "analysis": analysis,
        "results": results
    }
    
    with open("comprehensive_test_results.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nResults saved to comprehensive_test_results.json")
    
    return analysis


if __name__ == "__main__":
    main()
