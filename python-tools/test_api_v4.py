"""
Test script for API Server v4
Starts server, runs tests, then shuts down
"""

import asyncio
import aiohttp
import time
import sys
import multiprocessing
import pytest

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def run_server():
    """Run the API server in a subprocess"""
    import os
    os.environ['PORT'] = '8890'
    import uvicorn
    
    # Suppress log output for cleaner test output
    import logging
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    from api_server_v4 import app
    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


@pytest.mark.asyncio
async def test_endpoints():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:8890"
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Wait for server to be ready
        print(f"\n{CYAN}Waiting for server to start...{RESET}")
        for i in range(30):
            try:
                async with session.get(f"{base_url}/") as resp:
                    if resp.status == 200:
                        print(f"{GREEN}Server ready!{RESET}\n")
                        break
            except:
                pass
            await asyncio.sleep(0.5)
        else:
            print(f"{RED}Server failed to start!{RESET}")
            return []
        
        # Test 1: Root endpoint
        print(f"{CYAN}Testing endpoints...{RESET}\n")
        try:
            async with session.get(f"{base_url}/") as resp:
                data = await resp.json()
                success = resp.status == 200 and "Verity API" in data.get("message", "")
                results.append(("GET /", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} GET / - {resp.status}")
        except Exception as e:
            results.append(("GET /", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} GET / - {e}")
        
        # Test 2: Health check
        try:
            async with session.get(f"{base_url}/health") as resp:
                data = await resp.json()
                success = resp.status == 200 and data.get("status") == "healthy"
                results.append(("GET /health", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} GET /health - {resp.status}")
                if success:
                    print(f"      Version: {data.get('version')}")
                    print(f"      Uptime: {data.get('uptime_seconds', 0):.1f}s")
        except Exception as e:
            results.append(("GET /health", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} GET /health - {e}")
        
        # Test 3: Detailed health
        try:
            async with session.get(f"{base_url}/health/detailed") as resp:
                data = await resp.json()
                success = resp.status == 200
                results.append(("GET /health/detailed", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} GET /health/detailed - {resp.status}")
                if success and "providers" in data:
                    print(f"      Providers: {len(data.get('providers', []))}")
        except Exception as e:
            results.append(("GET /health/detailed", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} GET /health/detailed - {e}")
        
        # Test 4: Metrics
        try:
            async with session.get(f"{base_url}/metrics") as resp:
                text = await resp.text()
                success = resp.status == 200 and "verity_requests_total" in text
                results.append(("GET /metrics", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} GET /metrics - {resp.status}")
        except Exception as e:
            results.append(("GET /metrics", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} GET /metrics - {e}")
        
        # Test 5: Status
        try:
            async with session.get(f"{base_url}/status") as resp:
                data = await resp.json()
                success = resp.status == 200
                results.append(("GET /status", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} GET /status - {resp.status}")
        except Exception as e:
            results.append(("GET /status", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} GET /status - {e}")
        
        # Test 6: Verify endpoint (validation - too short claim)
        try:
            async with session.post(f"{base_url}/api/v4/verify", 
                                   json={"claim": "short"}) as resp:
                success = resp.status == 422  # Validation error expected
                results.append(("POST /api/v4/verify (validation)", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} POST /api/v4/verify (validation) - {resp.status}")
        except Exception as e:
            results.append(("POST /api/v4/verify (validation)", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} POST /api/v4/verify (validation) - {e}")
        
        # Test 7: Verify endpoint (real request)
        print(f"\n{CYAN}Testing verification (this may take a moment)...{RESET}")
        try:
            start = time.time()
            async with session.post(
                f"{base_url}/api/v4/verify",
                json={"claim": "The Earth is approximately 4.5 billion years old"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                success = resp.status == 200 and "verdict" in data
                results.append(("POST /api/v4/verify (real)", success, resp.status))
                print(f"  {'[PASS]' if success else '[FAIL]'} POST /api/v4/verify - {resp.status} ({duration:.1f}s)")
                if success:
                    print(f"      Verdict: {data.get('verdict')}")
                    print(f"      Confidence: {data.get('confidence', 0):.2f}")
                    print(f"      Sources: {data.get('source_count', 0)}")
        except asyncio.TimeoutError:
            results.append(("POST /api/v4/verify (real)", False, "timeout"))
            print(f"  {YELLOW}[WARN]{RESET} POST /api/v4/verify - Timeout (60s)")
        except Exception as e:
            results.append(("POST /api/v4/verify (real)", False, str(e)))
            print(f"  {RED}[FAIL]{RESET} POST /api/v4/verify - {e}")
    
    return results


def main():
    print(f"\n{'='*60}")
    print(f"{CYAN}  VERITY API v4 TEST SUITE{RESET}")
    print(f"{'='*60}")
    
    # Start server in subprocess
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    
    try:
        # Run tests
        results = asyncio.run(test_endpoints())
        
        # Summary
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
        # Shutdown server
        print(f"{CYAN}Shutting down test server...{RESET}")
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.kill()
        print(f"{GREEN}Done!{RESET}\n")


if __name__ == "__main__":
    sys.exit(main())
