"""
Test script for Advanced Analysis Endpoints in API Server v4
Tests all the new NLP, Similarity, Source Credibility, and Monte Carlo endpoints
"""

import asyncio
import aiohttp
import time
import sys
import multiprocessing

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def run_server():
    """Run the API server in a subprocess"""
    import os
    os.environ['PORT'] = '8891'
    import uvicorn
    import logging
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    from api_server_v4 import app
    uvicorn.run(app, host="127.0.0.1", port=8891, log_level="warning")


async def test_advanced_endpoints():
    """Test all advanced analysis endpoints"""
    base_url = "http://127.0.0.1:8891"
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Wait for server
        print(f"\n{CYAN}Waiting for server...{RESET}")
        for _ in range(30):
            try:
                async with session.get(f"{base_url}/health") as resp:
                    if resp.status == 200:
                        print(f"{GREEN}Server ready!{RESET}\n")
                        break
            except:
                pass
            await asyncio.sleep(0.5)
        
        print(f"{CYAN}Testing Advanced Analysis Endpoints...{RESET}\n")
        
        # Test 1: List modules
        print(f"  Testing GET /api/v4/modules...")
        try:
            async with session.get(f"{base_url}/api/v4/modules") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    active = data.get("active_modules", 0)
                    total = data.get("total_modules", 0)
                    results.append(("GET /api/v4/modules", True, f"Active: {active}/{total}"))
                    print(f"  {GREEN}[PASS]{RESET} Modules endpoint - {active}/{total} modules active")
                else:
                    results.append(("GET /api/v4/modules", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("GET /api/v4/modules", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 2: NLP Analysis
        print(f"  Testing POST /api/v4/analyze/nlp...")
        try:
            test_claim = "The COVID vaccine is 100% safe and has never harmed anyone according to all scientists."
            async with session.post(
                f"{base_url}/api/v4/analyze/nlp",
                json={"claim": test_claim}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    analysis = data.get("analysis", {})
                    fallacies = len(analysis.get("fallacies", []))
                    propaganda = len(analysis.get("propaganda", []))
                    results.append(("POST /api/v4/analyze/nlp", True, f"Detected: {fallacies} fallacies, {propaganda} propaganda"))
                    print(f"  {GREEN}[PASS]{RESET} NLP Analysis - {fallacies} fallacies, {propaganda} propaganda detected")
                else:
                    results.append(("POST /api/v4/analyze/nlp", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("POST /api/v4/analyze/nlp", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 3: Source Credibility
        print(f"  Testing POST /api/v4/analyze/sources...")
        try:
            async with session.post(
                f"{base_url}/api/v4/analyze/sources",
                json={"domains": ["nature.com", "cdc.gov", "infowars.com", "nytimes.com"]}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    found = data.get("sources_found", 0)
                    results.append(("POST /api/v4/analyze/sources", True, f"Found: {found} sources"))
                    print(f"  {GREEN}[PASS]{RESET} Source Credibility - {found}/4 sources found")
                    
                    # Show some ratings
                    for domain, info in data.get("results", {}).items():
                        score = info.get("credibility_score", 0)
                        tier = info.get("credibility_tier", "?")
                        print(f"      {domain}: {score}/100 (Tier {tier})")
                else:
                    results.append(("POST /api/v4/analyze/sources", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("POST /api/v4/analyze/sources", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 4: Monte Carlo Confidence
        print(f"  Testing POST /api/v4/analyze/confidence...")
        try:
            evidence = [
                {"source_name": "Wikipedia", "verdict": "true", "confidence": 0.85, "credibility": 0.9},
                {"source_name": "News Source", "verdict": "true", "confidence": 0.7, "credibility": 0.7},
                {"source_name": "Science Journal", "verdict": "true", "confidence": 0.95, "credibility": 0.98},
                {"source_name": "Social Media", "verdict": "false", "confidence": 0.5, "credibility": 0.3},
            ]
            async with session.post(
                f"{base_url}/api/v4/analyze/confidence",
                json={"evidence": evidence}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get("result", {})
                    verdict = result.get("verdict", "?")
                    conf = result.get("mean_confidence", 0)
                    ci = result.get("confidence_interval", {})
                    results.append(("POST /api/v4/analyze/confidence", True, f"Verdict: {verdict}, Confidence: {conf:.2f}"))
                    print(f"  {GREEN}[PASS]{RESET} Monte Carlo - Verdict: {verdict}, Confidence: {conf:.2f}")
                    print(f"      95% CI: [{ci.get('lower', 0):.2f}, {ci.get('upper', 0):.2f}]")
                else:
                    results.append(("POST /api/v4/analyze/confidence", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("POST /api/v4/analyze/confidence", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 5: Numerical Analysis
        print(f"  Testing POST /api/v4/analyze/numerical...")
        try:
            async with session.post(
                f"{base_url}/api/v4/analyze/numerical",
                json={"claim": "The company grew by 500% in the last quarter, adding $2.5 billion in revenue."}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    analysis = data.get("analysis", {})
                    has_claims = analysis.get("has_numerical_claims", False)
                    results.append(("POST /api/v4/analyze/numerical", True, f"Has numerical claims: {has_claims}"))
                    print(f"  {GREEN}[PASS]{RESET} Numerical Analysis - Claims detected: {has_claims}")
                else:
                    text = await resp.text()
                    results.append(("POST /api/v4/analyze/numerical", False, f"Status {resp.status}"))
                    print(f"  {YELLOW}[SKIP]{RESET} Module may not be fully configured ({resp.status})")
        except Exception as e:
            results.append(("POST /api/v4/analyze/numerical", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 6: V3 Compatibility - verify
        print(f"\n{CYAN}Testing V3 Compatibility Endpoints...{RESET}\n")
        print(f"  Testing POST /v3/verify...")
        try:
            async with session.post(
                f"{base_url}/v3/verify",
                json={"claim": "Water boils at 100 degrees Celsius at sea level."}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    success = data.get("success", False)
                    verdict = data.get("result", {}).get("verdict", "?")
                    results.append(("POST /v3/verify", True, f"Success: {success}, Verdict: {verdict}"))
                    print(f"  {GREEN}[PASS]{RESET} V3 Verify - Success: {success}")
                else:
                    results.append(("POST /v3/verify", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("POST /v3/verify", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 7: V3 Compatibility - providers
        print(f"  Testing GET /v3/providers...")
        try:
            async with session.get(f"{base_url}/v3/providers") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    total = data.get("total_providers", 0)
                    results.append(("GET /v3/providers", True, f"Total providers: {total}"))
                    print(f"  {GREEN}[PASS]{RESET} V3 Providers - {total} total")
                else:
                    results.append(("GET /v3/providers", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("GET /v3/providers", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
        
        # Test 8: Comprehensive Analysis
        print(f"\n{CYAN}Testing Comprehensive Analysis...{RESET}\n")
        print(f"  Testing POST /api/v4/analyze/comprehensive...")
        try:
            async with session.post(
                f"{base_url}/api/v4/analyze/comprehensive",
                json={
                    "claim": "NASA confirmed that the Moon landing in 1969 was filmed on a Hollywood set, with 73% of Americans believing this conspiracy.",
                    "sources_used": ["nasa.gov", "snopes.com"]
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    modules_used = data.get("metadata", {}).get("modules_used", [])
                    processing_time = data.get("metadata", {}).get("processing_time_ms", 0)
                    results.append(("POST /api/v4/analyze/comprehensive", True, f"Used {len(modules_used)} modules"))
                    print(f"  {GREEN}[PASS]{RESET} Comprehensive - {len(modules_used)} modules, {processing_time:.0f}ms")
                    print(f"      Modules used: {', '.join(modules_used)}")
                    
                    # Show some insights
                    if data.get("nlp", {}).get("fallacies"):
                        print(f"      Fallacies: {data['nlp']['fallacies']}")
                    if data.get("nlp", {}).get("propaganda"):
                        print(f"      Propaganda: {[p.get('technique') for p in data['nlp']['analysis'].get('propaganda', [])]}")
                else:
                    results.append(("POST /api/v4/analyze/comprehensive", False, f"Status {resp.status}"))
                    print(f"  {RED}[FAIL]{RESET} Status {resp.status}")
        except Exception as e:
            results.append(("POST /api/v4/analyze/comprehensive", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} {e}")
    
    return results


def main():
    print(f"\n{'='*60}")
    print(f"{CYAN}  VERITY API v4 - ADVANCED ANALYSIS TEST SUITE{RESET}")
    print(f"{'='*60}")
    
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    
    try:
        results = asyncio.run(test_advanced_endpoints())
        
        passed = sum(1 for r in results if r[1])
        failed = len(results) - passed
        
        print(f"\n{'='*60}")
        print(f"{CYAN}  TEST SUMMARY{RESET}")
        print(f"{'='*60}")
        print(f"  Passed: {GREEN}{passed}{RESET}")
        print(f"  Failed: {RED}{failed}{RESET}")
        print(f"  Total:  {len(results)}")
        print(f"{'='*60}\n")
        
        return 0 if failed == 0 else 1
        
    finally:
        print(f"{CYAN}Shutting down...{RESET}")
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.kill()
        print(f"{GREEN}Done!{RESET}\n")


if __name__ == "__main__":
    sys.exit(main())
