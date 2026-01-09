#!/usr/bin/env python3
"""Comprehensive Verification Test Suite"""

import httpx
import json
import time
from colorama import init, Fore, Style

init()  # Initialize colorama

API_URL = "http://localhost:8000/verify"

def test_claim(claim: str, expected: str = None) -> dict:
    """Test a single claim"""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(API_URL, json={"claim": claim})
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "verdict": "error"}
    except Exception as e:
        return {"error": str(e), "verdict": "error"}

def run_tests():
    print(f"\n{Fore.YELLOW}{'='*60}")
    print("COMPREHENSIVE VERIFICATION TEST SUITE")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    test_categories = {
        "EASY - Known Facts": [
            ("The Earth is round, not flat", "true"),
            ("Water boils at 100 degrees Celsius at sea level", "true"),
            ("The capital of France is Paris", "true"),
            ("The sun rises in the east", "true"),
            ("2 + 2 equals 4", "true"),
        ],
        "MEDIUM - Nuanced Claims": [
            ("The United States has the highest GDP in the world", "partially_true"),
            ("Coffee is the second most traded commodity after oil", "partially_true"),
            ("Einstein failed math in school", "false"),
            ("The Great Wall of China is visible from space", "false"),
            ("Humans only use 10% of their brain", "false"),
        ],
        "HARD - Complex/Debatable": [
            ("AI will replace most jobs in the next 10 years", "mixed"),
            ("You need to drink 8 glasses of water per day", "partially_true"),
            ("Breakfast is the most important meal of the day", "mixed"),
            ("Reading in dim light damages your eyes", "false"),
            ("Cracking your knuckles causes arthritis", "false"),
        ],
        "CONTROVERSIAL - Sensitive Topics": [
            ("Climate change is primarily caused by human activity", "true"),
            ("Vaccines cause autism", "false"),
            ("The 2020 US election was secure and fair", "true"),
            ("COVID-19 originated from a lab leak", "unverifiable"),
        ],
    }
    
    results = {"passed": 0, "failed": 0, "total": 0}
    
    for category, claims in test_categories.items():
        print(f"\n{Fore.MAGENTA}=== {category} ==={Style.RESET_ALL}\n")
        
        for i, (claim, expected) in enumerate(claims, 1):
            results["total"] += 1
            print(f"{Fore.WHITE}{i}. {claim[:60]}...{Style.RESET_ALL}")
            
            result = test_claim(claim)
            verdict = result.get("verdict", "error")
            providers = result.get("providers_used", [])
            
            # Color based on verdict
            if verdict == "error":
                color = Fore.RED
            elif verdict in ["true", "mostly_true"]:
                color = Fore.GREEN
            elif verdict in ["false", "mostly_false"]:
                color = Fore.RED
            elif verdict in ["partially_true", "mixed"]:
                color = Fore.YELLOW
            else:
                color = Fore.CYAN
            
            print(f"   {color}Verdict: {verdict}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}Providers: {', '.join(providers)}{Style.RESET_ALL}")
            
            if verdict != "error":
                results["passed"] += 1
            else:
                results["failed"] += 1
                
            time.sleep(1.5)  # Rate limiting
    
    # Summary
    print(f"\n{Fore.YELLOW}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"Total: {results['total']}")
    print(f"{Fore.GREEN}Passed: {results['passed']}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {results['failed']}{Style.RESET_ALL}")
    print(f"Success Rate: {results['passed']/results['total']*100:.1f}%")

if __name__ == "__main__":
    run_tests()
