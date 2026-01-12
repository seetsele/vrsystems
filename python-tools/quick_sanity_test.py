#!/usr/bin/env python3
"""
Quick sanity test - run 10 representative tests to validate the system.
"""

import httpx
import time
import json
import asyncio

API_URL = "http://localhost:8000"
VERIFY_ENDPOINT = f"{API_URL}/verify"
HEADERS = {"X-API-Key": "demo-key-12345"}

# 10 representative tests
QUICK_TESTS = [
    {"id": "Q1", "claim": "The speed of light is approximately 299,792,458 meters per second.", "expected": "true"},
    {"id": "Q2", "claim": "The Great Wall of China is visible from space with the naked eye.", "expected": "false"},
    {"id": "Q3", "claim": "Coffee consumption has both benefits and risks depending on the amount consumed.", "expected": "mixed"},
    {"id": "Q4", "claim": "Humans only use 10% of their brains.", "expected": "false"},
    {"id": "Q5", "claim": "Water is made of two hydrogen atoms and one oxygen atom.", "expected": "true"},
    {"id": "Q6", "claim": "Vaccines cause autism according to all scientific studies.", "expected": "false"},
    {"id": "Q7", "claim": "Electric vehicles have zero lifecycle emissions and are perfect for the environment.", "expected": "mixed"},
    {"id": "Q8", "claim": "The Apollo 11 mission landed humans on the Moon in 1969.", "expected": "true"},
    {"id": "Q9", "claim": "Climate change is entirely natural with no human contribution whatsoever.", "expected": "false"},
    {"id": "Q10", "claim": "Minimum wage increases have complex and debated effects on employment.", "expected": "mixed"},
]


async def run_quick_test(test):
    """Run a single test."""
    async with httpx.AsyncClient() as client:
        start = time.time()
        try:
            response = await client.post(
                VERIFY_ENDPOINT,
                headers=HEADERS,
                json={"claim": test["claim"], "mode": "full"},
                timeout=300.0
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                verdict = data.get("verdict", "unknown").lower()
                
                # Normalize
                if "true" in verdict or verdict == "verified":
                    actual = "true"
                elif "false" in verdict or verdict == "debunked":
                    actual = "false"
                elif "mixed" in verdict or "partial" in verdict or "nuanced" in verdict:
                    actual = "mixed"
                else:
                    actual = verdict
                
                passed = actual == test["expected"]
                return {
                    "id": test["id"],
                    "expected": test["expected"],
                    "actual": actual,
                    "passed": passed,
                    "duration": duration,
                    "confidence": data.get("confidence", 0)
                }
            else:
                return {
                    "id": test["id"],
                    "expected": test["expected"],
                    "actual": "error",
                    "passed": False,
                    "error": f"HTTP {response.status_code}",
                    "duration": time.time() - start
                }
        except Exception as e:
            return {
                "id": test["id"],
                "expected": test["expected"],
                "actual": "error",
                "passed": False,
                "error": str(e),
                "duration": time.time() - start
            }


async def main():
    print("=" * 60)
    print("QUICK SANITY TEST - 10 Tests")
    print("=" * 60)
    
    results = []
    for i, test in enumerate(QUICK_TESTS):
        print(f"\n[{i+1}/10] {test['id']}: {test['claim'][:60]}...")
        result = await run_quick_test(test)
        results.append(result)
        
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status} - Expected: {test['expected']}, Got: {result['actual']} ({result['duration']:.1f}s)")
        
        if result.get("error"):
            print(f"  Error: {result['error']}")
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/10 passed ({passed*10}%)")
    print("=" * 60)
    
    # Breakdown
    true_tests = [r for r in results if r["expected"] == "true"]
    false_tests = [r for r in results if r["expected"] == "false"]
    mixed_tests = [r for r in results if r["expected"] == "mixed"]
    
    true_acc = sum(1 for r in true_tests if r["passed"]) / len(true_tests) * 100 if true_tests else 0
    false_acc = sum(1 for r in false_tests if r["passed"]) / len(false_tests) * 100 if false_tests else 0
    mixed_acc = sum(1 for r in mixed_tests if r["passed"]) / len(mixed_tests) * 100 if mixed_tests else 0
    
    print(f"TRUE accuracy:  {true_acc:.0f}%")
    print(f"FALSE accuracy: {false_acc:.0f}%")
    print(f"MIXED accuracy: {mixed_acc:.0f}%")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
