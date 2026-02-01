"""
VERITY TIERED INTEGRATION TESTS
===============================
Tests tiered verification across all platforms
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any

API_BASE = "http://localhost:8000"

# Test results storage
results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_result(name: str, passed: bool, details: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   Details: {details}")
    results["passed" if passed else "failed"] += 1
    results["tests"].append({"name": name, "passed": passed, "details": details})


async def test_health():
    """Test health endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/health") as resp:
                data = await resp.json()
                log_result(
                    "Health Endpoint",
                    resp.status == 200 and data.get("status") == "healthy",
                    f"Status: {data.get('status')}, Providers: {data.get('providers_available')}"
                )
        except Exception as e:
            log_result("Health Endpoint", False, str(e))


async def test_tiers_endpoint():
    """Test /tiers endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/tiers") as resp:
                data = await resp.json()
                expected_tiers = ["free", "starter", "pro", "professional", "agency", "business", "enterprise"]
                has_all_tiers = all(t in data.get("available_tiers", []) for t in expected_tiers)
                log_result(
                    "Tiers Endpoint",
                    resp.status == 200 and has_all_tiers,
                    f"Found {len(data.get('available_tiers', []))} tiers"
                )
        except Exception as e:
            log_result("Tiers Endpoint", False, str(e))


async def test_tier_details():
    """Test /tiers/{tier_name} endpoint"""
    async with aiohttp.ClientSession() as session:
        for tier in ["free", "pro", "enterprise"]:
            try:
                async with session.get(f"{API_BASE}/tiers/{tier}") as resp:
                    data = await resp.json()
                    has_required = all(k in data for k in ["name", "max_models", "features"])
                    log_result(
                        f"Tier Details - {tier}",
                        resp.status == 200 and has_required,
                        f"Max models: {data.get('max_models')}"
                    )
            except Exception as e:
                log_result(f"Tier Details - {tier}", False, str(e))


async def test_tiered_verification():
    """Test /tiered-verify endpoint for each tier"""
    claim = "The Earth is approximately 4.5 billion years old."
    async with aiohttp.ClientSession() as session:
        for tier in ["free", "pro", "enterprise"]:
            try:
                payload = {
                    "claim": claim,
                    "tier": tier,
                    "platform": "web",
                    "context": "",
                    "include_free_providers": True
                }
                async with session.post(f"{API_BASE}/tiered-verify", json=payload) as resp:
                    data = await resp.json()
                    has_verdict = "verdict" in data
                    correct_tier = data.get("tier") == tier
                    log_result(
                        f"Tiered Verify - {tier}",
                        resp.status == 200 and has_verdict,
                        f"Verdict: {data.get('verdict')}, Models: {len(data.get('models_used', []))}"
                    )
            except Exception as e:
                log_result(f"Tiered Verify - {tier}", False, str(e))


async def test_platform_endpoints():
    """Test platform-specific endpoints"""
    claim = "Water boils at 100°C at sea level."
    platforms = [
        ("web", "/platform/web/verify"),
        ("desktop", "/platform/desktop/verify"),
        ("mobile", "/platform/mobile/verify"),
        ("browser_extension", "/platform/browser-extension/verify"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for platform, endpoint in platforms:
            try:
                payload = {"claim": claim, "tier": "pro"}
                async with session.post(f"{API_BASE}{endpoint}", json=payload) as resp:
                    data = await resp.json()
                    log_result(
                        f"Platform - {platform}",
                        resp.status == 200 and "verdict" in data,
                        f"Verdict: {data.get('verdict', 'N/A')}"
                    )
            except Exception as e:
                log_result(f"Platform - {platform}", False, str(e))


async def test_specialized_models():
    """Test specialized models endpoints"""
    async with aiohttp.ClientSession() as session:
        # List models
        try:
            async with session.get(f"{API_BASE}/specialized-models") as resp:
                data = await resp.json()
                log_result(
                    "Specialized Models List",
                    resp.status == 200,
                    f"Available: {data.get('available')}, Count: {data.get('total_models', 0)}"
                )
        except Exception as e:
            log_result("Specialized Models List", False, str(e))


async def test_free_providers():
    """Test free providers endpoints"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/free-providers") as resp:
                data = await resp.json()
                log_result(
                    "Free Providers List",
                    resp.status == 200,
                    f"Available: {data.get('available', False)}"
                )
        except Exception as e:
            log_result("Free Providers List", False, str(e))


async def test_unified_verify():
    """Test unified verification endpoint"""
    claim = "Photosynthesis converts sunlight into chemical energy."
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "claim": claim,
                "mode": "standard",
                "use_specialized": True,
                "use_free_providers": True,
                "use_commercial": True
            }
            async with session.post(f"{API_BASE}/unified-verify", json=payload) as resp:
                data = await resp.json()
                log_result(
                    "Unified Verify",
                    resp.status == 200 and "verdict" in data,
                    f"Verdict: {data.get('verdict')}, Model count: {data.get('model_count', 0)}"
                )
        except Exception as e:
            log_result("Unified Verify", False, str(e))


async def test_all_ai_models():
    """Test all AI models listing"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/all-ai-models") as resp:
                data = await resp.json()
                log_result(
                    "All AI Models",
                    resp.status == 200,
                    f"Total: {data.get('total_models', 0)}, Categories: {list(data.get('models', {}).keys())[:3]}"
                )
        except Exception as e:
            log_result("All AI Models", False, str(e))


async def test_api_batch_verify():
    """Test batch verification (Professional+ only)"""
    claims = [
        "The sun is a star.",
        "Water is H2O.",
        "Gravity pulls objects downward."
    ]
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "claims": claims,
                "tier": "professional",
                "api_key": "test-key"
            }
            async with session.post(f"{API_BASE}/platform/api/batch-verify", json=payload) as resp:
                data = await resp.json()
                log_result(
                    "Batch Verify (Professional)",
                    resp.status == 200 and data.get("total_claims") == 3,
                    f"Total claims: {data.get('total_claims')}, Results: {len(data.get('results', []))}"
                )
        except Exception as e:
            log_result("Batch Verify (Professional)", False, str(e))


async def test_tier_access_control():
    """Test that free tier cannot access API endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "claim": "Test claim",
                "tier": "free",
                "api_key": "test-key"
            }
            async with session.post(f"{API_BASE}/platform/api/verify", json=payload) as resp:
                # Should return 403 for free tier
                log_result(
                    "Tier Access Control",
                    resp.status == 403,
                    f"Status: {resp.status} (expected 403 for free tier API access)"
                )
        except Exception as e:
            log_result("Tier Access Control", False, str(e))


async def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("VERITY TIERED INTEGRATION TESTS")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print()
    
    start = time.time()
    
    await test_health()
    await test_tiers_endpoint()
    await test_tier_details()
    await test_tiered_verification()
    await test_platform_endpoints()
    await test_specialized_models()
    await test_free_providers()
    await test_unified_verify()
    await test_all_ai_models()
    await test_api_batch_verify()
    await test_tier_access_control()
    
    elapsed = time.time() - start
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Total: {results['passed'] + results['failed']}")
    print(f"Time: {elapsed:.2f}s")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
