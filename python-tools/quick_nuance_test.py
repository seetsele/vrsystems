#!/usr/bin/env python3
"""
Quick test of the 3 claims that failed in the first test.
These were failing because nuance detection wasn't triggering.
"""

import httpx
import time
import json
from typing import Dict, Any

API_URL = "http://localhost:8000"

# Just the 3 failed claims
FAILED_CLAIMS = [
    {"claim": "Coffee is bad for your health", "expected": "mixed", "name": "Coffee Health"},
    {"claim": "Electric vehicles are completely carbon-neutral", "expected": "mixed", "name": "EV Carbon"},
    {"claim": "Cryptocurrency is a scam", "expected": "mixed", "name": "Crypto Scam"},
]

def test_claim(claim_data: Dict) -> Dict[str, Any]:
    """Test a single claim."""
    try:
        start = time.time()
        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{API_URL}/verify",
                json={
                    "claim": claim_data["claim"],
                    "tier": "enterprise"
                },
                headers={"X-API-Key": "demo-key-12345"}
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                verdict = result.get("verdict", "").lower()
                confidence = result.get("confidence", 0)
                
                # Check for MIXED variants
                is_mixed = verdict in ["mixed", "mostly_true", "mostly_false", "partially_true"]
                expected_mixed = claim_data["expected"] == "mixed"
                
                correct = is_mixed if expected_mixed else verdict == claim_data["expected"]
                
                return {
                    "claim": claim_data["claim"],
                    "name": claim_data["name"],
                    "expected": claim_data["expected"],
                    "verdict": verdict,
                    "confidence": confidence,
                    "correct": correct,
                    "time": elapsed,
                    "nuance_detected": result.get("nuance_analysis", {}).get("is_nuanced", False),
                    "nuance_score": result.get("nuance_analysis", {}).get("nuance_score", 0),
                    "nuance_forced": result.get("nuance_analysis", {}).get("forced_mixed", False),
                }
            else:
                return {"claim": claim_data["claim"], "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"claim": claim_data["claim"], "error": str(e)}

def main():
    print("=" * 70)
    print("QUICK NUANCE TEST - Testing 3 Previously Failed Claims")
    print("=" * 70)
    print()
    
    results = []
    for i, claim_data in enumerate(FAILED_CLAIMS, 1):
        print(f"[{i}/{len(FAILED_CLAIMS)}] Testing: {claim_data['name']}...")
        result = test_claim(claim_data)
        results.append(result)
        
        if "error" in result:
            print(f"    ❌ ERROR: {result['error']}")
        else:
            status = "✅" if result["correct"] else "❌"
            print(f"    {status} Expected: {result['expected']}, Got: {result['verdict']} ({result['confidence']*100:.1f}%)")
            print(f"       Nuance detected: {result['nuance_detected']}, Score: {result['nuance_score']}")
            if result.get("nuance_forced"):
                print(f"       🔄 MIXED verdict forced by nuance detection!")
        print()
    
    # Summary
    correct = sum(1 for r in results if r.get("correct", False))
    print("=" * 70)
    print(f"RESULTS: {correct}/{len(results)} correct ({100*correct/len(results):.0f}%)")
    print("=" * 70)
    
    if correct == len(results):
        print("🎉 ALL PREVIOUSLY FAILED CLAIMS NOW PASSING!")
    else:
        print("⚠️  Some claims still failing - further tuning needed")

if __name__ == "__main__":
    main()
