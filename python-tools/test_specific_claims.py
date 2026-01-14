#!/usr/bin/env python3
"""Test specific claims that are failing."""

import requests
import json

API_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": "demo-key-12345", "Content-Type": "application/json"}

def test_claim(name, claim, expected):
    """Test a single claim."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Expected: {expected}")
    print(f"Claim: {claim[:80]}...")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/verify",
            headers=HEADERS,
            json={"claim": claim},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            verdict = result.get("verdict", "unknown")
            nuance = result.get("nuance_analysis", {})
            
            print(f"\nResult:")
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {result.get('confidence', 0)}")
            print(f"\nNuance Analysis:")
            print(f"  Is Nuanced: {nuance.get('is_nuanced', False)}")
            print(f"  Nuance Score: {nuance.get('nuance_score', 0)}")
            print(f"  Has Academic Hedging: {nuance.get('has_academic_hedging', False)}")
            print(f"  Is Balanced Claim: {nuance.get('is_balanced_claim', False)}")
            print(f"  Override Applied: {nuance.get('override_applied', False)}")
            print(f"  Override Reason: {nuance.get('override_reason', 'N/A')}")
            
            passed = verdict == expected
            print(f"\n  {'✓ PASS' if passed else '✗ FAIL'}")
            return passed
        else:
            print(f"  Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TARGETED NUANCE DETECTION TEST")
    print("="*60)
    
    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            print(f"API Status: healthy")
        else:
            print(f"API Status: unhealthy ({health.status_code})")
            exit(1)
    except:
        print("API not responding!")
        exit(1)
    
    tests = [
        ("NH-001 Coffee Health", 
         """According to recent systematic reviews, moderate coffee consumption (3-4 cups per day) 
         has been associated with reduced risk of cardiovascular disease, type 2 diabetes, and certain 
         neurodegenerative conditions. However, excessive consumption exceeding 6 cups daily may lead to 
         anxiety, sleep disturbances, and potential cardiovascular stress in susceptible individuals.""",
         "mixed"),
        
        ("NH-002 Intermittent Fasting",
         """Intermittent fasting protocols including 16:8 time-restricted eating have demonstrated 
         metabolic benefits in randomized controlled trials, showing improvements in insulin sensitivity and 
         reduction in inflammatory markers. However, the long-term effects on muscle mass preservation and 
         hormonal balance remain subjects of ongoing research with conflicting evidence.""",
         "mixed"),
         
        ("EDGE-003 Renewable Energy",
         """Renewable energy sources such as solar, wind, and hydroelectric power have significant 
         advantages in terms of environmental impact and long-term sustainability, but they also face challenges 
         including intermittency, storage limitations, land use requirements, and initial infrastructure costs 
         that require careful planning and complementary technologies to address effectively.""",
         "mixed"),
    ]
    
    passed = 0
    for name, claim, expected in tests:
        if test_claim(name, claim, expected):
            passed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed ({100*passed/len(tests):.1f}%)")
    print("="*60)
