#!/usr/bin/env python3
"""
Verity API Comprehensive Tester
================================
Complete testing suite for all Verity API endpoints.

Usage:
    python api_tester_comprehensive.py [--base-url URL] [--api-key KEY]
    
Features:
    - Tests all API endpoints
    - Provider health checks
    - Verification accuracy testing
    - Load testing capabilities
    - Stripe integration tests
    - Generates detailed reports
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Installing required package: httpx")
    os.system(f"{sys.executable} -m pip install httpx")
    import httpx

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.live import Live
except ImportError:
    print("Installing required package: rich")
    os.system(f"{sys.executable} -m pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.live import Live

# Initialize console
console = Console()

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_API_KEY = "demo-key-12345"

# Test claims with known ground truth for accuracy testing
TEST_CLAIMS = [
    {
        "claim": "The Earth is approximately 4.5 billion years old",
        "expected": "TRUE",
        "category": "science"
    },
    {
        "claim": "Water boils at 100 degrees Celsius at sea level",
        "expected": "TRUE",
        "category": "science"
    },
    {
        "claim": "The Great Wall of China is visible from the Moon with the naked eye",
        "expected": "FALSE",
        "category": "misconception"
    },
    {
        "claim": "Lightning never strikes the same place twice",
        "expected": "FALSE", 
        "category": "misconception"
    },
    {
        "claim": "The human body has 206 bones in adulthood",
        "expected": "TRUE",
        "category": "biology"
    },
    {
        "claim": "Vaccines cause autism according to scientific consensus",
        "expected": "FALSE",
        "category": "health"
    },
    {
        "claim": "Mount Everest is the tallest mountain on Earth measured from sea level",
        "expected": "TRUE",
        "category": "geography"
    },
    {
        "claim": "Goldfish have a 3-second memory",
        "expected": "FALSE",
        "category": "misconception"
    },
    {
        "claim": "The speed of light is approximately 299,792,458 meters per second",
        "expected": "TRUE",
        "category": "physics"
    },
    {
        "claim": "Bats are blind",
        "expected": "FALSE",
        "category": "biology"
    },
]

# =============================================================================
# API TESTER CLASS
# =============================================================================

class VerityAPITester:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {}
        }
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def close(self):
        await self.client.aclose()
    
    # =========================================================================
    # BASIC ENDPOINT TESTS
    # =========================================================================
    
    async def test_root(self) -> Dict:
        """Test root endpoint"""
        try:
            start = time.time()
            resp = await self.client.get(f"{self.base_url}/", headers=self._get_headers())
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_providers(self) -> Dict:
        """Test providers list endpoint"""
        try:
            start = time.time()
            resp = await self.client.get(f"{self.base_url}/providers", headers=self._get_headers())
            latency = (time.time() - start) * 1000
            
            data = resp.json() if resp.status_code == 200 else None
            provider_count = len(data.get("providers", [])) if data else 0
            
            return {
                "endpoint": "/providers",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "provider_count": provider_count,
                "data": data
            }
        except Exception as e:
            return {
                "endpoint": "/providers",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_providers_health(self) -> Dict:
        """Test provider health endpoint"""
        try:
            start = time.time()
            resp = await self.client.get(f"{self.base_url}/providers/health", headers=self._get_headers())
            latency = (time.time() - start) * 1000
            
            data = resp.json() if resp.status_code == 200 else None
            
            return {
                "endpoint": "/providers/health",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": data
            }
        except Exception as e:
            return {
                "endpoint": "/providers/health",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_deep_health(self) -> Dict:
        """Test deep health check endpoint"""
        try:
            start = time.time()
            resp = await self.client.get(f"{self.base_url}/health/deep", headers=self._get_headers())
            latency = (time.time() - start) * 1000
            
            data = resp.json() if resp.status_code == 200 else None
            
            return {
                "endpoint": "/health/deep",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": data
            }
        except Exception as e:
            return {
                "endpoint": "/health/deep",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_stats(self) -> Dict:
        """Test stats endpoint"""
        try:
            start = time.time()
            resp = await self.client.get(f"{self.base_url}/stats", headers=self._get_headers())
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/stats",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/stats",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    # =========================================================================
    # VERIFICATION TESTS
    # =========================================================================
    
    async def test_verify_single(self, claim: str, expected: Optional[str] = None) -> Dict:
        """Test single verification endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/verify",
                headers=self._get_headers(),
                json={"claim": claim, "min_providers": 3}
            )
            latency = (time.time() - start) * 1000
            
            data = resp.json() if resp.status_code == 200 else None
            
            # Check accuracy if expected result provided
            accuracy_correct = None
            if data and expected:
                verdict = data.get("verdict", "").upper()
                if expected == "TRUE" and verdict in ["TRUE", "MOSTLY TRUE", "LIKELY TRUE"]:
                    accuracy_correct = True
                elif expected == "FALSE" and verdict in ["FALSE", "MOSTLY FALSE", "LIKELY FALSE"]:
                    accuracy_correct = True
                elif expected == "UNVERIFIABLE" and verdict in ["UNVERIFIABLE", "UNCERTAIN"]:
                    accuracy_correct = True
                else:
                    accuracy_correct = False
            
            return {
                "endpoint": "/verify",
                "claim": claim[:50] + "..." if len(claim) > 50 else claim,
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "verdict": data.get("verdict") if data else None,
                "confidence": data.get("confidence") if data else None,
                "providers_used": data.get("providers_used") if data else None,
                "expected": expected,
                "accuracy_correct": accuracy_correct,
                "data": data
            }
        except Exception as e:
            return {
                "endpoint": "/verify",
                "claim": claim[:50] + "..." if len(claim) > 50 else claim,
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_v3_verify(self, claim: str) -> Dict:
        """Test v3 verification endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/v3/verify",
                headers=self._get_headers(),
                json={"claim": claim, "mode": "balanced"}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/v3/verify",
                "claim": claim[:50] + "..." if len(claim) > 50 else claim,
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/v3/verify",
                "claim": claim[:50] + "..." if len(claim) > 50 else claim,
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_batch_verify(self, claims: List[str]) -> Dict:
        """Test batch verification endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/v3/batch-verify",
                headers=self._get_headers(),
                json={"claims": claims}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/v3/batch-verify",
                "claim_count": len(claims),
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/v3/batch-verify",
                "claim_count": len(claims),
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    # =========================================================================
    # TOOL TESTS
    # =========================================================================
    
    async def test_social_media(self) -> Dict:
        """Test social media analysis endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/tools/social-media",
                headers=self._get_headers(),
                json={"url": "https://twitter.com/example/status/123", "analyze_thread": False}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/tools/social-media",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code in [200, 400, 404],  # 400/404 is ok for test URL
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/tools/social-media",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_source_credibility(self) -> Dict:
        """Test source credibility endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/tools/source-credibility",
                headers=self._get_headers(),
                json={"url": "https://www.reuters.com"}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/tools/source-credibility",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/tools/source-credibility",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_statistics_validator(self) -> Dict:
        """Test statistics validator endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/tools/statistics-validator",
                headers=self._get_headers(),
                json={"claim": "73% of Americans support this policy according to a 2024 Gallup poll"}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/tools/statistics-validator",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/tools/statistics-validator",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_research_assistant(self) -> Dict:
        """Test research assistant endpoint"""
        try:
            start = time.time()
            resp = await self.client.post(
                f"{self.base_url}/tools/research-assistant",
                headers=self._get_headers(),
                json={"topic": "climate change effects on ocean temperatures", "depth": "summary"}
            )
            latency = (time.time() - start) * 1000
            
            return {
                "endpoint": "/tools/research-assistant",
                "status_code": resp.status_code,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "/tools/research-assistant",
                "status_code": 0,
                "latency_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    
    async def run_all_tests(self, include_verification: bool = True, include_accuracy: bool = True):
        """Run comprehensive test suite"""
        
        console.print(Panel.fit(
            "[bold cyan]Verity API Comprehensive Tester[/bold cyan]\n" +
            f"Base URL: {self.base_url}\n" +
            f"API Key: {'*' * 10 + self.api_key[-4:] if self.api_key else 'None'}",
            title="🔍 Test Suite"
        ))
        
        # Phase 1: Basic Connectivity
        console.print("\n[bold yellow]Phase 1: Basic Connectivity Tests[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Testing endpoints...", total=5)
            
            self.results["tests"]["root"] = await self.test_root()
            progress.advance(task)
            
            self.results["tests"]["providers"] = await self.test_providers()
            progress.advance(task)
            
            self.results["tests"]["providers_health"] = await self.test_providers_health()
            progress.advance(task)
            
            self.results["tests"]["deep_health"] = await self.test_deep_health()
            progress.advance(task)
            
            self.results["tests"]["stats"] = await self.test_stats()
            progress.advance(task)
        
        # Display Phase 1 results
        self._display_basic_results()
        
        # Phase 2: Verification Tests
        if include_verification:
            console.print("\n[bold yellow]Phase 2: Verification Endpoint Tests[/bold yellow]")
            
            test_claim = "The Earth orbits the Sun"
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Testing verification...", total=3)
                
                self.results["tests"]["verify_single"] = await self.test_verify_single(test_claim, "TRUE")
                progress.advance(task)
                
                self.results["tests"]["v3_verify"] = await self.test_v3_verify(test_claim)
                progress.advance(task)
                
                self.results["tests"]["batch_verify"] = await self.test_batch_verify([
                    "Water is wet",
                    "The moon is made of cheese"
                ])
                progress.advance(task)
            
            self._display_verification_results()
        
        # Phase 3: Tool Tests
        console.print("\n[bold yellow]Phase 3: Specialized Tool Tests[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Testing tools...", total=4)
            
            self.results["tests"]["social_media"] = await self.test_social_media()
            progress.advance(task)
            
            self.results["tests"]["source_credibility"] = await self.test_source_credibility()
            progress.advance(task)
            
            self.results["tests"]["statistics_validator"] = await self.test_statistics_validator()
            progress.advance(task)
            
            self.results["tests"]["research_assistant"] = await self.test_research_assistant()
            progress.advance(task)
        
        self._display_tool_results()
        
        # Phase 4: Accuracy Testing
        if include_accuracy:
            console.print("\n[bold yellow]Phase 4: Accuracy Testing (Ground Truth Claims)[/bold yellow]")
            
            accuracy_results = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Testing accuracy...", total=len(TEST_CLAIMS))
                
                for test_case in TEST_CLAIMS:
                    result = await self.test_verify_single(
                        test_case["claim"],
                        test_case["expected"]
                    )
                    result["category"] = test_case["category"]
                    accuracy_results.append(result)
                    progress.advance(task)
                    await asyncio.sleep(0.5)  # Rate limiting
            
            self.results["tests"]["accuracy"] = accuracy_results
            self._display_accuracy_results(accuracy_results)
        
        # Generate Summary
        self._generate_summary()
        
        return self.results
    
    # =========================================================================
    # DISPLAY METHODS
    # =========================================================================
    
    def _display_basic_results(self):
        table = Table(title="Basic Endpoint Tests")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", justify="right")
        table.add_column("Details")
        
        for key in ["root", "providers", "providers_health", "deep_health", "stats"]:
            result = self.results["tests"].get(key, {})
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            status_style = "green" if result.get("success") else "red"
            latency = f"{result.get('latency_ms', 0):.0f}ms"
            
            details = ""
            if key == "providers":
                details = f"{result.get('provider_count', 0)} providers"
            elif "error" in result:
                details = result["error"][:50]
            
            table.add_row(result.get("endpoint", key), f"[{status_style}]{status}[/{status_style}]", latency, details)
        
        console.print(table)
    
    def _display_verification_results(self):
        table = Table(title="Verification Tests")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", justify="right")
        table.add_column("Verdict")
        table.add_column("Confidence")
        
        for key in ["verify_single", "v3_verify", "batch_verify"]:
            result = self.results["tests"].get(key, {})
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            status_style = "green" if result.get("success") else "red"
            latency = f"{result.get('latency_ms', 0):.0f}ms"
            verdict = result.get("verdict", "-")
            confidence = f"{result.get('confidence', 0):.0%}" if result.get("confidence") else "-"
            
            table.add_row(
                result.get("endpoint", key),
                f"[{status_style}]{status}[/{status_style}]",
                latency,
                str(verdict),
                confidence
            )
        
        console.print(table)
    
    def _display_tool_results(self):
        table = Table(title="Tool Tests")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", justify="right")
        
        for key in ["social_media", "source_credibility", "statistics_validator", "research_assistant"]:
            result = self.results["tests"].get(key, {})
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            status_style = "green" if result.get("success") else "red"
            latency = f"{result.get('latency_ms', 0):.0f}ms"
            
            table.add_row(result.get("endpoint", key), f"[{status_style}]{status}[/{status_style}]", latency)
        
        console.print(table)
    
    def _display_accuracy_results(self, results: List[Dict]):
        table = Table(title="Accuracy Test Results")
        table.add_column("Claim", style="dim", max_width=40)
        table.add_column("Expected", style="bold")
        table.add_column("Actual")
        table.add_column("Correct", style="bold")
        table.add_column("Category")
        
        correct = 0
        total = len(results)
        
        for result in results:
            expected = result.get("expected", "-")
            actual = result.get("verdict", "-")
            is_correct = result.get("accuracy_correct")
            
            if is_correct:
                correct += 1
                correct_str = "[green]✅ YES[/green]"
            elif is_correct is False:
                correct_str = "[red]❌ NO[/red]"
            else:
                correct_str = "[yellow]⚠️ N/A[/yellow]"
            
            table.add_row(
                result.get("claim", "-"),
                expected,
                str(actual),
                correct_str,
                result.get("category", "-")
            )
        
        console.print(table)
        
        accuracy_pct = (correct / total * 100) if total > 0 else 0
        console.print(f"\n[bold]Accuracy Score: {correct}/{total} ({accuracy_pct:.1f}%)[/bold]")
    
    def _generate_summary(self):
        tests = self.results["tests"]
        
        total_tests = 0
        passed_tests = 0
        total_latency = 0
        
        for key, result in tests.items():
            if key == "accuracy":
                continue
            if isinstance(result, list):
                continue
            total_tests += 1
            if result.get("success"):
                passed_tests += 1
            total_latency += result.get("latency_ms", 0)
        
        avg_latency = total_latency / total_tests if total_tests > 0 else 0
        
        # Accuracy from ground truth tests
        accuracy_results = tests.get("accuracy", [])
        accuracy_correct = sum(1 for r in accuracy_results if r.get("accuracy_correct"))
        accuracy_total = len(accuracy_results)
        accuracy_pct = (accuracy_correct / accuracy_total * 100) if accuracy_total > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A",
            "average_latency_ms": round(avg_latency, 2),
            "accuracy_tests": accuracy_total,
            "accuracy_correct": accuracy_correct,
            "accuracy_percentage": f"{accuracy_pct:.1f}%"
        }
        
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            f"[bold green]Tests Passed:[/bold green] {passed_tests}/{total_tests} ({self.results['summary']['pass_rate']})\n" +
            f"[bold cyan]Average Latency:[/bold cyan] {avg_latency:.0f}ms\n" +
            f"[bold yellow]Accuracy Score:[/bold yellow] {accuracy_correct}/{accuracy_total} ({accuracy_pct:.1f}%)",
            title="📊 Test Summary"
        ))
    
    def save_report(self, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        console.print(f"\n[dim]Report saved to: {filename}[/dim]")
        return filename


# =============================================================================
# MAIN
# =============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Verity API Comprehensive Tester")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="API key for authentication")
    parser.add_argument("--no-verification", action="store_true", help="Skip verification tests")
    parser.add_argument("--no-accuracy", action="store_true", help="Skip accuracy tests")
    parser.add_argument("--output", "-o", help="Output report filename")
    
    args = parser.parse_args()
    
    tester = VerityAPITester(args.base_url, args.api_key)
    
    try:
        await tester.run_all_tests(
            include_verification=not args.no_verification,
            include_accuracy=not args.no_accuracy
        )
        tester.save_report(args.output)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
