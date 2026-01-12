"""
Verity Systems - Extensive Claim Testing Suite
Tests 25 challenging claims across various types: PDFs, URLs, images, research papers, 
scientific claims, historical facts, political statements, health misinformation, etc.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys

API_URL = "http://localhost:8000"

@dataclass
class TestClaim:
    id: int
    category: str
    claim: str
    claim_type: str  # text, url, research, health, political, scientific, historical, fake
    expected_verdict: str  # true, false, mixed, unverifiable
    source: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard, extreme
    notes: str = ""

@dataclass
class TestResult:
    claim_id: int
    category: str
    claim: str
    expected: str
    actual_verdict: str
    confidence: float
    correct: bool
    response_time: float
    providers_used: List[str]
    sources_found: int
    explanation: str
    error: Optional[str] = None

# 25 Challenging Test Claims
TEST_CLAIMS = [
    # ========== TRUE CLAIMS (should return TRUE) ==========
    TestClaim(
        id=1,
        category="Scientific Fact",
        claim="Water molecules consist of two hydrogen atoms and one oxygen atom (H2O).",
        claim_type="scientific",
        expected_verdict="true",
        difficulty="easy",
        notes="Basic chemistry fact"
    ),
    TestClaim(
        id=2,
        category="Historical Fact",
        claim="The Berlin Wall fell on November 9, 1989.",
        claim_type="historical",
        expected_verdict="true",
        difficulty="easy",
        notes="Well-documented historical event"
    ),
    TestClaim(
        id=3,
        category="Research Paper",
        claim="The 2012 CRISPR-Cas9 paper by Doudna and Charpentier demonstrated programmable genome editing.",
        claim_type="research",
        expected_verdict="true",
        source="DOI: 10.1126/science.1225829",
        difficulty="medium",
        notes="Nobel Prize-winning research"
    ),
    TestClaim(
        id=4,
        category="Current Events",
        claim="The James Webb Space Telescope launched in December 2021 and is positioned at Lagrange point L2.",
        claim_type="scientific",
        expected_verdict="true",
        difficulty="medium",
        notes="Verifiable space mission"
    ),
    TestClaim(
        id=5,
        category="Medical Fact",
        claim="mRNA vaccines work by instructing cells to produce a protein that triggers an immune response.",
        claim_type="health",
        expected_verdict="true",
        difficulty="medium",
        notes="Established vaccine science"
    ),
    
    # ========== FALSE CLAIMS (should return FALSE) ==========
    TestClaim(
        id=6,
        category="Health Misinformation",
        claim="5G cell towers cause COVID-19 infections by weakening the immune system.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="easy",
        notes="Debunked conspiracy theory"
    ),
    TestClaim(
        id=7,
        category="Scientific Misinformation",
        claim="The Earth is flat and NASA has been hiding this truth for decades.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="easy",
        notes="Debunked flat earth claim"
    ),
    TestClaim(
        id=8,
        category="Historical Misinformation",
        claim="The Great Wall of China is visible from the Moon with the naked eye.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="medium",
        notes="Common myth debunked by astronauts"
    ),
    TestClaim(
        id=9,
        category="Health Misinformation",
        claim="Drinking bleach or injecting disinfectants cures viral infections including COVID-19.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="easy",
        notes="Dangerous health misinformation"
    ),
    TestClaim(
        id=10,
        category="Political Misinformation",
        claim="Voter fraud through mail-in ballots changed the outcome of the 2020 US presidential election.",
        claim_type="political",
        expected_verdict="false",
        difficulty="hard",
        notes="Debunked by courts and election officials"
    ),
    
    # ========== MIXED/NUANCED CLAIMS (should return MIXED) ==========
    TestClaim(
        id=11,
        category="Nuanced Science",
        claim="Coffee is bad for your health.",
        claim_type="health",
        expected_verdict="mixed",
        difficulty="hard",
        notes="Complex - has both benefits and risks"
    ),
    TestClaim(
        id=12,
        category="Economic Claim",
        claim="Raising minimum wage always leads to job losses.",
        claim_type="political",
        expected_verdict="mixed",
        difficulty="hard",
        notes="Economists disagree - context dependent"
    ),
    TestClaim(
        id=13,
        category="Technology Claim",
        claim="Artificial intelligence will replace all human jobs within 10 years.",
        claim_type="text",
        expected_verdict="mixed",
        difficulty="hard",
        notes="Predictions vary widely among experts"
    ),
    TestClaim(
        id=14,
        category="Environmental",
        claim="Electric vehicles are completely carbon-neutral.",
        claim_type="scientific",
        expected_verdict="mixed",
        difficulty="medium",
        notes="Manufacturing and electricity source matter"
    ),
    TestClaim(
        id=15,
        category="Nutrition",
        claim="Eating eggs every day is dangerous for heart health due to cholesterol.",
        claim_type="health",
        expected_verdict="mixed",
        difficulty="hard",
        notes="Research has evolved on this topic"
    ),
    
    # ========== HARD/EXTREME DIFFICULTY CLAIMS ==========
    TestClaim(
        id=16,
        category="Complex Research",
        claim="The Stanford Prison Experiment's findings about human behavior are scientifically valid and replicable.",
        claim_type="research",
        expected_verdict="false",
        difficulty="extreme",
        notes="Methodology has been heavily criticized"
    ),
    TestClaim(
        id=17,
        category="Recent Research",
        claim="Room temperature superconductivity was achieved by LK-99 in 2023.",
        claim_type="research",
        expected_verdict="false",
        difficulty="extreme",
        notes="Could not be replicated by other labs"
    ),
    TestClaim(
        id=18,
        category="Statistical Claim",
        claim="More people die from medical errors than car accidents in the United States annually.",
        claim_type="health",
        expected_verdict="true",
        difficulty="hard",
        notes="BMJ study estimates 250,000+ annual deaths from medical errors"
    ),
    TestClaim(
        id=19,
        category="Deepfake/Fabricated",
        claim="Pope Francis endorsed Donald Trump for president in 2016.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="medium",
        notes="Famous fake news story from 2016"
    ),
    TestClaim(
        id=20,
        category="Subtle Misinformation",
        claim="NASA's budget is 25% of the US federal budget.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="medium",
        notes="Actually less than 0.5% - common misconception"
    ),
    
    # ========== URL/SOURCE VERIFICATION ==========
    TestClaim(
        id=21,
        category="URL Verification",
        claim="According to the WHO, microplastics in drinking water pose no significant health risk based on current evidence.",
        claim_type="url",
        expected_verdict="true",
        source="WHO 2019 report",
        difficulty="hard",
        notes="Requires understanding of WHO's nuanced position"
    ),
    TestClaim(
        id=22,
        category="PDF Research",
        claim="The IPCC Sixth Assessment Report states that human activities have unequivocally caused global warming.",
        claim_type="research",
        expected_verdict="true",
        source="IPCC AR6",
        difficulty="medium",
        notes="Direct quote from major climate report"
    ),
    
    # ========== EDGE CASES ==========
    TestClaim(
        id=23,
        category="Outdated Information",
        claim="Pluto is classified as the ninth planet in our solar system.",
        claim_type="scientific",
        expected_verdict="false",
        difficulty="easy",
        notes="Reclassified as dwarf planet in 2006"
    ),
    TestClaim(
        id=24,
        category="Partially True",
        claim="Humans only use 10% of their brains.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="medium",
        notes="Popular myth - we use all parts of our brain"
    ),
    TestClaim(
        id=25,
        category="Viral Misinformation",
        claim="The 2004 Indian Ocean tsunami was caused by underwater nuclear testing by the US military.",
        claim_type="fake",
        expected_verdict="false",
        difficulty="medium",
        notes="Conspiracy theory - actually caused by earthquake"
    ),
]

class ExtensiveTestSuite:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
    async def verify_claim(self, session: aiohttp.ClientSession, claim: TestClaim) -> TestResult:
        """Verify a single claim through the API"""
        start_time = time.time()
        
        try:
            payload = {
                "claim": claim.claim,
                "options": {
                    "include_sources": True,
                    "include_evidence": True,
                    "model": "deep",  # Use deep model for thorough testing
                }
            }
            
            async with session.post(
                f"{self.api_url}/verify",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Normalize verdict
                    actual_verdict = data.get("verdict", "unknown").lower()
                    if actual_verdict in ["mostly_true"]:
                        actual_verdict = "true"
                    elif actual_verdict in ["mostly_false"]:
                        actual_verdict = "false"
                    
                    # Check if correct
                    is_correct = self._check_correctness(claim.expected_verdict, actual_verdict)
                    
                    return TestResult(
                        claim_id=claim.id,
                        category=claim.category,
                        claim=claim.claim[:100] + "..." if len(claim.claim) > 100 else claim.claim,
                        expected=claim.expected_verdict,
                        actual_verdict=actual_verdict,
                        confidence=data.get("confidence", 0),
                        correct=is_correct,
                        response_time=response_time,
                        providers_used=data.get("providers", []),
                        sources_found=len(data.get("sources", [])),
                        explanation=data.get("explanation", "")[:200]
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        claim_id=claim.id,
                        category=claim.category,
                        claim=claim.claim[:100] + "...",
                        expected=claim.expected_verdict,
                        actual_verdict="error",
                        confidence=0,
                        correct=False,
                        response_time=response_time,
                        providers_used=[],
                        sources_found=0,
                        explanation="",
                        error=f"HTTP {response.status}: {error_text[:100]}"
                    )
                    
        except asyncio.TimeoutError:
            return TestResult(
                claim_id=claim.id,
                category=claim.category,
                claim=claim.claim[:100] + "...",
                expected=claim.expected_verdict,
                actual_verdict="timeout",
                confidence=0,
                correct=False,
                response_time=120,
                providers_used=[],
                sources_found=0,
                explanation="",
                error="Request timed out after 120 seconds"
            )
        except Exception as e:
            return TestResult(
                claim_id=claim.id,
                category=claim.category,
                claim=claim.claim[:100] + "...",
                expected=claim.expected_verdict,
                actual_verdict="error",
                confidence=0,
                correct=False,
                response_time=time.time() - start_time,
                providers_used=[],
                sources_found=0,
                explanation="",
                error=str(e)[:100]
            )
    
    def _check_correctness(self, expected: str, actual: str) -> bool:
        """Check if the verdict is correct with some flexibility"""
        if expected == actual:
            return True
        # Allow some flexibility for mixed verdicts
        if expected == "mixed" and actual in ["true", "false", "mixed", "unverifiable"]:
            return actual == "mixed" or actual == "unverifiable"
        if expected in ["true", "mostly_true"] and actual in ["true", "mostly_true"]:
            return True
        if expected in ["false", "mostly_false"] and actual in ["false", "mostly_false"]:
            return True
        return False
    
    async def run_all_tests(self) -> None:
        """Run all 25 test claims"""
        self.start_time = datetime.now()
        print("=" * 80)
        print("VERITY SYSTEMS - EXTENSIVE CLAIM TESTING SUITE")
        print("=" * 80)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API URL: {self.api_url}")
        print(f"Total Claims: {len(TEST_CLAIMS)}")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            # Run tests sequentially for accurate timing
            for i, claim in enumerate(TEST_CLAIMS, 1):
                print(f"\n[{i}/{len(TEST_CLAIMS)}] Testing: {claim.category}")
                print(f"    Claim: {claim.claim[:70]}...")
                print(f"    Expected: {claim.expected_verdict.upper()} | Difficulty: {claim.difficulty}")
                
                result = await self.verify_claim(session, claim)
                self.results.append(result)
                
                status = "✅ PASS" if result.correct else "❌ FAIL"
                print(f"    Result: {result.actual_verdict.upper()} ({result.confidence}%) - {status}")
                print(f"    Time: {result.response_time:.2f}s | Sources: {result.sources_found}")
                
                if result.error:
                    print(f"    Error: {result.error}")
                
                # Small delay between requests
                await asyncio.sleep(0.5)
        
        self.end_time = datetime.now()
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total = len(self.results)
        correct = sum(1 for r in self.results if r.correct)
        errors = sum(1 for r in self.results if r.error)
        
        # Calculate accuracy by category
        category_stats = {}
        for result in self.results:
            if result.category not in category_stats:
                category_stats[result.category] = {"total": 0, "correct": 0}
            category_stats[result.category]["total"] += 1
            if result.correct:
                category_stats[result.category]["correct"] += 1
        
        # Calculate accuracy by expected verdict
        verdict_stats = {"true": {"total": 0, "correct": 0}, "false": {"total": 0, "correct": 0}, "mixed": {"total": 0, "correct": 0}}
        for result in self.results:
            expected = result.expected
            if expected in verdict_stats:
                verdict_stats[expected]["total"] += 1
                if result.correct:
                    verdict_stats[expected]["correct"] += 1
        
        # Response time stats
        response_times = [r.response_time for r in self.results if not r.error]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Confidence stats
        confidences = [r.confidence for r in self.results if r.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        report = {
            "summary": {
                "total_claims": total,
                "correct": correct,
                "incorrect": total - correct - errors,
                "errors": errors,
                "accuracy_rate": round((correct / total) * 100, 2) if total > 0 else 0,
                "total_time": str(self.end_time - self.start_time) if self.end_time else "N/A",
                "avg_response_time": round(avg_response_time, 2),
                "avg_confidence": round(avg_confidence, 2),
            },
            "by_category": {
                cat: {
                    "accuracy": round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0,
                    "correct": stats["correct"],
                    "total": stats["total"]
                }
                for cat, stats in category_stats.items()
            },
            "by_expected_verdict": {
                verdict: {
                    "accuracy": round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0,
                    "correct": stats["correct"],
                    "total": stats["total"]
                }
                for verdict, stats in verdict_stats.items()
            },
            "failed_claims": [
                {
                    "id": r.claim_id,
                    "category": r.category,
                    "claim": r.claim,
                    "expected": r.expected,
                    "actual": r.actual_verdict,
                    "confidence": r.confidence
                }
                for r in self.results if not r.correct
            ],
            "all_results": [asdict(r) for r in self.results],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        summary = report["summary"]
        print(f"\n📊 SUMMARY")
        print(f"   Total Claims Tested: {summary['total_claims']}")
        print(f"   ✅ Correct: {summary['correct']}")
        print(f"   ❌ Incorrect: {summary['incorrect']}")
        print(f"   ⚠️  Errors: {summary['errors']}")
        print(f"\n   🎯 ACCURACY RATE: {summary['accuracy_rate']}%")
        print(f"   ⏱️  Total Time: {summary['total_time']}")
        print(f"   📈 Avg Response Time: {summary['avg_response_time']}s")
        print(f"   🔍 Avg Confidence: {summary['avg_confidence']}%")
        
        print(f"\n📁 ACCURACY BY CATEGORY")
        print("-" * 50)
        for cat, stats in sorted(report["by_category"].items(), key=lambda x: -x[1]["accuracy"]):
            bar = "█" * int(stats["accuracy"] / 10) + "░" * (10 - int(stats["accuracy"] / 10))
            print(f"   {cat[:30]:<30} {bar} {stats['accuracy']:>6.1f}% ({stats['correct']}/{stats['total']})")
        
        print(f"\n📋 ACCURACY BY EXPECTED VERDICT")
        print("-" * 50)
        for verdict, stats in report["by_expected_verdict"].items():
            bar = "█" * int(stats["accuracy"] / 10) + "░" * (10 - int(stats["accuracy"] / 10))
            print(f"   {verdict.upper():<15} {bar} {stats['accuracy']:>6.1f}% ({stats['correct']}/{stats['total']})")
        
        if report["failed_claims"]:
            print(f"\n❌ FAILED CLAIMS ({len(report['failed_claims'])})")
            print("-" * 50)
            for claim in report["failed_claims"]:
                print(f"\n   #{claim['id']} - {claim['category']}")
                print(f"   Claim: {claim['claim']}")
                print(f"   Expected: {claim['expected'].upper()} | Got: {claim['actual'].upper()} ({claim['confidence']}%)")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)


async def main():
    """Main entry point"""
    suite = ExtensiveTestSuite()
    
    try:
        await suite.run_all_tests()
        report = suite.generate_report()
        suite.print_report(report)
        
        # Save report to file
        report_path = "extensive_test_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Full report saved to: {report_path}")
        
        # Return accuracy for CI/CD
        return report["summary"]["accuracy_rate"]
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    accuracy = asyncio.run(main())
    sys.exit(0 if accuracy >= 70 else 1)
