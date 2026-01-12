"""
Verity API v10 Enhanced Test Suite
===================================
Tests the improved fact-checking system with focus on:
- MIXED verdict accuracy (target: 90%+)
- Multi-loop verification (12-15 loops)
- Nuance detection
- Reduced timeouts
- Content extraction (URLs, PDFs)

This test focuses on the previously failing claims to verify improvements.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List

API_URL = "http://localhost:8000/verify"

# =============================================================================
# TEST CLAIMS - FOCUSED ON PREVIOUSLY FAILING CATEGORIES
# =============================================================================

TEST_CLAIMS = [
    # =========================================================================
    # MIXED CLAIMS - Previously 20% accuracy, targeting 90%+
    # =========================================================================
    {
        "id": 1,
        "claim": "Coffee is bad for your health",
        "expected": "mixed",
        "category": "Nuanced Health",
        "difficulty": "hard",
        "notes": "Previously returned FALSE. Should be MIXED - coffee has both benefits and risks"
    },
    {
        "id": 2,
        "claim": "AI will replace all human jobs within 10 years",
        "expected": "mixed",
        "category": "Technology Nuance",
        "difficulty": "hard",
        "notes": "Previously returned FALSE. Should be MIXED - AI will replace some jobs, create others"
    },
    {
        "id": 3,
        "claim": "Electric vehicles are completely carbon-neutral",
        "expected": "mixed",
        "category": "Environmental Nuance",
        "difficulty": "hard",
        "notes": "Previously returned FALSE. Should be MIXED - lower emissions but not zero"
    },
    {
        "id": 4,
        "claim": "Eating eggs daily is dangerous for heart health",
        "expected": "mixed",
        "category": "Nutrition Nuance",
        "difficulty": "hard",
        "notes": "Previously returned FALSE. Should be MIXED - context-dependent"
    },
    {
        "id": 5,
        "claim": "Raising the minimum wage always leads to job losses",
        "expected": "mixed",
        "category": "Economic Nuance",
        "difficulty": "hard",
        "notes": "Should be MIXED - economic studies show varying effects"
    },
    
    # =========================================================================
    # ADDITIONAL NUANCED CLAIMS - Testing nuance detection
    # =========================================================================
    {
        "id": 6,
        "claim": "Sugar is toxic to the human body",
        "expected": "mixed",
        "category": "Nutrition Nuance",
        "difficulty": "medium",
        "notes": "Should be MIXED - excess is harmful, but body needs some glucose"
    },
    {
        "id": 7,
        "claim": "Working from home is always more productive than office work",
        "expected": "mixed",
        "category": "Workplace Nuance",
        "difficulty": "medium",
        "notes": "Should be MIXED - depends on job type, person, and context"
    },
    {
        "id": 8,
        "claim": "Organic food is healthier than non-organic food",
        "expected": "mixed",
        "category": "Nutrition Nuance",
        "difficulty": "medium",
        "notes": "Should be MIXED - less pesticides but not necessarily more nutritious"
    },
    {
        "id": 9,
        "claim": "Cryptocurrency is a scam",
        "expected": "mixed",
        "category": "Finance Nuance",
        "difficulty": "hard",
        "notes": "Should be MIXED - some are legit, some are scams"
    },
    {
        "id": 10,
        "claim": "Social media causes depression in teenagers",
        "expected": "mixed",
        "category": "Psychology Nuance",
        "difficulty": "hard",
        "notes": "Should be MIXED - correlation exists but causation is complex"
    },
    
    # =========================================================================
    # CLEAR TRUE CLAIMS - Baseline accuracy check
    # =========================================================================
    {
        "id": 11,
        "claim": "Water is composed of hydrogen and oxygen atoms",
        "expected": "true",
        "category": "Scientific Fact",
        "difficulty": "easy",
        "notes": "Basic chemistry fact"
    },
    {
        "id": 12,
        "claim": "The human heart has four chambers",
        "expected": "true",
        "category": "Medical Fact",
        "difficulty": "easy",
        "notes": "Basic anatomy fact"
    },
    {
        "id": 13,
        "claim": "Albert Einstein developed the theory of general relativity",
        "expected": "true",
        "category": "Historical Fact",
        "difficulty": "easy",
        "notes": "Well-documented historical fact"
    },
    
    # =========================================================================
    # CLEAR FALSE CLAIMS - Misinformation detection
    # =========================================================================
    {
        "id": 14,
        "claim": "5G cell towers cause COVID-19 infections",
        "expected": "false",
        "category": "Health Misinformation",
        "difficulty": "medium",
        "notes": "Debunked conspiracy theory"
    },
    {
        "id": 15,
        "claim": "Humans only use 10% of their brain",
        "expected": "false",
        "category": "Scientific Misinformation",
        "difficulty": "medium",
        "notes": "Common myth, thoroughly debunked"
    },
    {
        "id": 16,
        "claim": "The Great Wall of China is visible from the Moon with the naked eye",
        "expected": "false",
        "category": "Historical Misinformation",
        "difficulty": "medium",
        "notes": "Commonly believed myth, astronauts have confirmed it's not visible"
    },
    
    # =========================================================================
    # URL/RESEARCH PAPER CLAIMS - Testing content extraction
    # =========================================================================
    {
        "id": 17,
        "claim": "According to https://www.who.int, vaccines are safe and effective",
        "expected": "true",
        "category": "URL Verification",
        "difficulty": "medium",
        "notes": "Should extract WHO content and verify"
    },
    {
        "id": 18,
        "claim": "The 2024 Nobel Prize in Physics was awarded for AI research on neural networks (DOI: 10.1126/science.adp7799)",
        "expected": "true",
        "category": "Research Paper",
        "difficulty": "hard",
        "notes": "Should verify with research paper extraction"
    },
]


async def test_claim(session: aiohttp.ClientSession, claim_data: Dict) -> Dict:
    """Test a single claim and return results."""
    start_time = time.time()
    
    try:
        async with session.post(
            API_URL,
            json={"claim": claim_data["claim"], "tier": "enterprise"},
            timeout=aiohttp.ClientTimeout(total=180)  # 3 minute timeout
        ) as response:
            elapsed = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Determine if correct
                actual_verdict = data.get("verdict", "unknown").lower()
                expected_verdict = claim_data["expected"].lower()
                
                # Allow for similar verdicts
                is_correct = (
                    actual_verdict == expected_verdict or
                    (expected_verdict == "mixed" and actual_verdict in ["partially_true", "mostly_true", "mostly_false", "mixed"]) or
                    (expected_verdict == "true" and actual_verdict in ["true", "mostly_true"]) or
                    (expected_verdict == "false" and actual_verdict in ["false", "mostly_false"])
                )
                
                return {
                    "id": claim_data["id"],
                    "claim": claim_data["claim"][:80] + "..." if len(claim_data["claim"]) > 80 else claim_data["claim"],
                    "category": claim_data["category"],
                    "expected": expected_verdict,
                    "actual": actual_verdict,
                    "confidence": data.get("confidence", 0),
                    "is_correct": is_correct,
                    "verification_loops": data.get("cross_validation", {}).get("verification_loops", 0),
                    "nuance_detected": data.get("nuance_analysis", {}).get("is_nuanced", False),
                    "nuance_score": data.get("nuance_analysis", {}).get("nuance_score", 0),
                    "override_applied": data.get("nuance_analysis", {}).get("override_applied", False),
                    "providers_count": len(data.get("providers_used", [])),
                    "sources_count": len(data.get("sources", [])),
                    "elapsed_seconds": round(elapsed, 2),
                    "status": "success"
                }
            else:
                return {
                    "id": claim_data["id"],
                    "claim": claim_data["claim"][:60],
                    "category": claim_data["category"],
                    "expected": claim_data["expected"],
                    "actual": "error",
                    "is_correct": False,
                    "elapsed_seconds": round(elapsed, 2),
                    "status": f"error_{response.status}"
                }
    
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return {
            "id": claim_data["id"],
            "claim": claim_data["claim"][:60],
            "category": claim_data["category"],
            "expected": claim_data["expected"],
            "actual": "timeout",
            "is_correct": False,
            "elapsed_seconds": round(elapsed, 2),
            "status": "timeout"
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "id": claim_data["id"],
            "claim": claim_data["claim"][:60],
            "category": claim_data["category"],
            "expected": claim_data["expected"],
            "actual": "error",
            "is_correct": False,
            "elapsed_seconds": round(elapsed, 2),
            "status": f"exception: {str(e)[:50]}"
        }


async def run_tests():
    """Run all tests and generate report."""
    print("=" * 70)
    print("VERITY API v10 ENHANCED TEST SUITE")
    print("=" * 70)
    print(f"Testing {len(TEST_CLAIMS)} claims...")
    print(f"Focus: MIXED verdict accuracy improvement (20% → 90%+ target)")
    print("=" * 70)
    print()
    
    start_time = time.time()
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test claims sequentially to avoid rate limiting
        for i, claim_data in enumerate(TEST_CLAIMS, 1):
            print(f"[{i}/{len(TEST_CLAIMS)}] Testing: {claim_data['claim'][:60]}...")
            result = await test_claim(session, claim_data)
            results.append(result)
            
            status_icon = "✅" if result["is_correct"] else "❌"
            print(f"    {status_icon} Expected: {result['expected']}, Got: {result['actual']} "
                  f"({result.get('confidence', 0)*100:.1f}% conf, {result['elapsed_seconds']}s)")
            
            if result.get("nuance_detected"):
                print(f"    📊 Nuance detected (score: {result.get('nuance_score', 0):.2f})")
            if result.get("override_applied"):
                print(f"    🔄 Nuance override applied!")
            
            print()
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    total_time = time.time() - start_time
    
    # ==========================================================================
    # GENERATE REPORT
    # ==========================================================================
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    # Overall stats
    total = len(results)
    correct = sum(1 for r in results if r["is_correct"])
    errors = sum(1 for r in results if r["status"] != "success")
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    print(f"\n📈 OVERALL ACCURACY: {accuracy:.1f}% ({correct}/{total})")
    print(f"   ⏱️  Total Time: {total_time/60:.1f} minutes")
    print(f"   📦 Avg Response Time: {sum(r['elapsed_seconds'] for r in results)/len(results):.1f}s")
    print(f"   ⚠️  Errors/Timeouts: {errors}")
    
    # Accuracy by expected verdict
    print("\n📋 ACCURACY BY VERDICT TYPE:")
    for verdict in ["mixed", "true", "false"]:
        verdict_results = [r for r in results if r["expected"] == verdict]
        if verdict_results:
            verdict_correct = sum(1 for r in verdict_results if r["is_correct"])
            verdict_accuracy = (verdict_correct / len(verdict_results)) * 100
            status = "🎯" if verdict_accuracy >= 90 else "⚠️" if verdict_accuracy >= 70 else "❌"
            print(f"   {status} {verdict.upper()}: {verdict_accuracy:.1f}% ({verdict_correct}/{len(verdict_results)})")
    
    # Nuance detection stats
    nuance_results = [r for r in results if r["expected"] == "mixed"]
    if nuance_results:
        print("\n🔍 NUANCE DETECTION ANALYSIS:")
        nuance_detected = sum(1 for r in nuance_results if r.get("nuance_detected"))
        overrides_applied = sum(1 for r in nuance_results if r.get("override_applied"))
        print(f"   Nuance detected: {nuance_detected}/{len(nuance_results)}")
        print(f"   Overrides applied: {overrides_applied}/{len(nuance_results)}")
        avg_nuance_score = sum(r.get("nuance_score", 0) for r in nuance_results) / len(nuance_results)
        print(f"   Avg nuance score: {avg_nuance_score:.3f}")
    
    # Verification loops stats
    avg_loops = sum(r.get("verification_loops", 0) for r in results) / len(results)
    avg_providers = sum(r.get("providers_count", 0) for r in results) / len(results)
    print(f"\n🔄 VERIFICATION STATS:")
    print(f"   Avg verification loops: {avg_loops:.1f}")
    print(f"   Avg providers used: {avg_providers:.1f}")
    
    # Failed claims
    failed = [r for r in results if not r["is_correct"]]
    if failed:
        print(f"\n❌ FAILED CLAIMS ({len(failed)}):")
        for r in failed:
            print(f"   #{r['id']} - {r['category']}")
            print(f"      Claim: {r['claim']}")
            print(f"      Expected: {r['expected']}, Got: {r['actual']}")
    
    # Save report
    report = {
        "test_date": datetime.now().isoformat(),
        "api_version": "10.0.0",
        "total_claims": total,
        "accuracy": round(accuracy, 2),
        "correct": correct,
        "errors": errors,
        "total_time_seconds": round(total_time, 2),
        "results": results,
        "by_verdict": {
            verdict: {
                "total": len([r for r in results if r["expected"] == verdict]),
                "correct": sum(1 for r in results if r["expected"] == verdict and r["is_correct"]),
                "accuracy": round(
                    sum(1 for r in results if r["expected"] == verdict and r["is_correct"]) / 
                    len([r for r in results if r["expected"] == verdict]) * 100, 2
                ) if [r for r in results if r["expected"] == verdict] else 0
            }
            for verdict in ["mixed", "true", "false"]
        }
    }
    
    with open("v10_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Report saved to v10_test_report.json")
    print("=" * 70)
    
    # Final assessment
    mixed_accuracy = report["by_verdict"]["mixed"]["accuracy"]
    if mixed_accuracy >= 90:
        print("✅ SUCCESS: MIXED claim accuracy >= 90%!")
    elif mixed_accuracy >= 70:
        print("⚠️  PARTIAL SUCCESS: MIXED claim accuracy improved but < 90%")
    else:
        print("❌ NEEDS MORE WORK: MIXED claim accuracy still below 70%")
    
    return report


if __name__ == "__main__":
    asyncio.run(run_tests())
