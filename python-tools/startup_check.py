"""
Verity Systems - Startup Validation & Health Check
Validates all dependencies, API keys, and services before server start.

Run this before starting the server to ensure everything is configured:
    python startup_check.py

Author: Verity Systems
"""

import os
import sys
import asyncio
import importlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


@dataclass
class CheckResult:
    name: str
    status: str  # 'ok', 'warning', 'error'
    message: str
    details: Optional[str] = None


def print_header():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║            VERITY SYSTEMS - STARTUP VALIDATION v5.0              ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}
""")


def print_section(title: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ {title}{Colors.END}")
    print("─" * 50)


def print_result(result: CheckResult):
    if result.status == 'ok':
        icon = f"{Colors.GREEN}✓{Colors.END}"
    elif result.status == 'warning':
        icon = f"{Colors.YELLOW}⚠{Colors.END}"
    else:
        icon = f"{Colors.RED}✗{Colors.END}"
    
    print(f"  {icon} {result.name}: {result.message}")
    if result.details:
        print(f"      {Colors.CYAN}→ {result.details}{Colors.END}")


# ============================================================
# DEPENDENCY CHECKS
# ============================================================

def check_python_version() -> CheckResult:
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        return CheckResult(
            name="Python Version",
            status="ok",
            message=f"Python {version.major}.{version.minor}.{version.micro}"
        )
    elif version.major >= 3 and version.minor >= 8:
        return CheckResult(
            name="Python Version",
            status="warning",
            message=f"Python {version.major}.{version.minor} (3.10+ recommended)"
        )
    else:
        return CheckResult(
            name="Python Version",
            status="error",
            message=f"Python {version.major}.{version.minor} (3.10+ required)"
        )


def check_required_packages() -> List[CheckResult]:
    """Check if required packages are installed"""
    results = []
    
    # Format: package_import_name: (display_name, min_version, pip_install_name)
    required_packages = {
        # Core
        "fastapi": ("FastAPI", "0.109.0", "fastapi"),
        "uvicorn": ("Uvicorn", "0.25.0", "uvicorn"),
        "aiohttp": ("aiohttp", "3.9.0", "aiohttp"),
        "pydantic": ("Pydantic", "2.0.0", "pydantic"),
        
        # AI/ML
        "anthropic": ("Anthropic SDK", "0.40.0", "anthropic"),
        "openai": ("OpenAI SDK", "1.0.0", "openai"),
        
        # Security
        "cryptography": ("Cryptography", "41.0.0", "cryptography"),
        "jwt": ("PyJWT", "2.8.0", "pyjwt"),  # Import is 'jwt', pip is 'pyjwt'
        
        # Optional but recommended
        "litellm": ("LiteLLM", "1.0.0", "litellm"),
        "redis": ("Redis", "5.0.0", "redis"),
    }
    
    optional_packages = ["litellm", "redis", "groq", "ollama"]
    
    for import_name, (display_name, min_version, pip_name) in required_packages.items():
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", "unknown")
            
            is_optional = import_name in optional_packages
            
            results.append(CheckResult(
                name=display_name,
                status="ok",
                message=f"v{version} installed"
            ))
        except ImportError:
            is_optional = import_name in optional_packages
            results.append(CheckResult(
                name=display_name,
                status="warning" if is_optional else "error",
                message="Not installed" if is_optional else "MISSING - Required!",
                details=f"pip install {pip_name}" if not is_optional else f"Optional: pip install {pip_name}"
            ))
    
    return results


# ============================================================
# API KEY CHECKS
# ============================================================

def check_api_keys() -> List[CheckResult]:
    """Check for required and optional API keys"""
    results = []
    
    api_keys = {
        # Provider: (env_var, required, description)
        "Anthropic Claude": ("ANTHROPIC_API_KEY", False, "Claude AI - $25 free from GitHub Education"),
        "OpenAI": ("OPENAI_API_KEY", False, "GPT-4 - via Azure credits"),
        "Google Fact Check": ("GOOGLE_FACTCHECK_API_KEY", False, "10,000 free requests/day"),
        "Groq": ("GROQ_API_KEY", False, "Free Llama 3.1 70B inference"),
        "OpenRouter": ("OPENROUTER_API_KEY", False, "500+ models, free tier available"),
        "Together AI": ("TOGETHER_API_KEY", False, "$25 free credits"),
        "DeepSeek": ("DEEPSEEK_API_KEY", False, "Ultra-cheap inference"),
        "NewsAPI": ("NEWS_API_KEY", False, "100 free requests/day"),
        "Supabase": ("SUPABASE_URL", False, "Database backend"),
        "Redis": ("REDIS_URL", False, "Distributed caching"),
    }
    
    for provider, (env_var, required, description) in api_keys.items():
        value = os.getenv(env_var)
        
        if value:
            # Mask the key for display
            masked = value[:4] + "..." + value[-4:] if len(value) > 10 else "****"
            results.append(CheckResult(
                name=provider,
                status="ok",
                message=f"Configured ({masked})",
                details=description
            ))
        else:
            results.append(CheckResult(
                name=provider,
                status="error" if required else "warning",
                message="Not configured",
                details=f"Set {env_var} - {description}"
            ))
    
    return results


# ============================================================
# SERVICE CHECKS
# ============================================================

async def check_services() -> List[CheckResult]:
    """Check connectivity to external services"""
    import aiohttp
    
    results = []
    
    services = [
        ("Groq API", "https://api.groq.com/openai/v1/models", "GROQ_API_KEY"),
        ("OpenRouter", "https://openrouter.ai/api/v1/models", "OPENROUTER_API_KEY"),
        ("Google Fact Check", "https://factchecktools.googleapis.com/v1alpha1/claims:search?query=test", "GOOGLE_FACTCHECK_API_KEY"),
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for name, url, api_key_env in services:
            api_key = os.getenv(api_key_env)
            
            if not api_key:
                results.append(CheckResult(
                    name=name,
                    status="warning",
                    message="Skipped (no API key)"
                ))
                continue
            
            try:
                headers = {}
                if "groq" in url.lower():
                    headers["Authorization"] = f"Bearer {api_key}"
                elif "openrouter" in url.lower():
                    headers["Authorization"] = f"Bearer {api_key}"
                elif "google" in url.lower():
                    url = f"{url}&key={api_key}"
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        results.append(CheckResult(
                            name=name,
                            status="ok",
                            message="Connected successfully"
                        ))
                    else:
                        results.append(CheckResult(
                            name=name,
                            status="warning",
                            message=f"HTTP {resp.status}",
                            details="Check API key or service status"
                        ))
            except asyncio.TimeoutError:
                results.append(CheckResult(
                    name=name,
                    status="warning",
                    message="Timeout",
                    details="Service might be slow or unavailable"
                ))
            except Exception as e:
                results.append(CheckResult(
                    name=name,
                    status="error",
                    message=str(e)[:50]
                ))
    
    # Check Redis if configured
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url, socket_connect_timeout=3)
            r.ping()
            results.append(CheckResult(
                name="Redis",
                status="ok",
                message="Connected successfully"
            ))
        except Exception as e:
            results.append(CheckResult(
                name="Redis",
                status="warning",
                message=f"Cannot connect: {str(e)[:40]}",
                details="In-memory cache will be used instead"
            ))
    else:
        results.append(CheckResult(
            name="Redis",
            status="warning",
            message="Not configured",
            details="Using in-memory cache (OK for development)"
        ))
    
    # Check Ollama (local)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get("http://localhost:11434/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    results.append(CheckResult(
                        name="Ollama (Local)",
                        status="ok",
                        message=f"{len(models)} models available",
                        details=", ".join(models[:3]) if models else "No models pulled"
                    ))
                else:
                    results.append(CheckResult(
                        name="Ollama (Local)",
                        status="warning",
                        message="Running but returned error"
                    ))
    except:
        results.append(CheckResult(
            name="Ollama (Local)",
            status="warning",
            message="Not running",
            details="Optional: Install from ollama.com for local models"
        ))
    
    return results


# ============================================================
# VERITY MODULES CHECK
# ============================================================

def check_verity_modules() -> List[CheckResult]:
    """Check if all Verity modules can be imported"""
    results = []
    
    modules = [
        ("verity_supermodel", "Core Super Model"),
        ("verity_engine", "Verification Engine"),
        ("verity_unified_llm", "Unified LLM Gateway"),
        ("verity_resilience", "Resilience Layer"),
        ("verity_cache", "Caching Layer"),
        ("verity_data_sources", "Extended Data Sources"),
        ("verity_enhanced_orchestrator", "Enhanced Orchestrator"),
        ("api_server_v4", "API Server v4"),
        ("security_utils", "Security Utilities"),
        ("enhanced_providers", "Enhanced Providers"),
    ]
    
    for module_name, display_name in modules:
        try:
            importlib.import_module(module_name)
            results.append(CheckResult(
                name=display_name,
                status="ok",
                message="Loaded successfully"
            ))
        except ImportError as e:
            results.append(CheckResult(
                name=display_name,
                status="error",
                message=f"Import failed",
                details=str(e)[:60]
            ))
        except Exception as e:
            results.append(CheckResult(
                name=display_name,
                status="warning",
                message=f"Loaded with warnings",
                details=str(e)[:60]
            ))
    
    return results


# ============================================================
# SUMMARY
# ============================================================

def print_summary(all_results: List[CheckResult]):
    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.END}")
    print(f"{Colors.BOLD}SUMMARY{Colors.END}")
    print(f"{'═' * 50}")
    
    ok_count = sum(1 for r in all_results if r.status == 'ok')
    warning_count = sum(1 for r in all_results if r.status == 'warning')
    error_count = sum(1 for r in all_results if r.status == 'error')
    
    print(f"\n  {Colors.GREEN}✓ Passed:{Colors.END} {ok_count}")
    print(f"  {Colors.YELLOW}⚠ Warnings:{Colors.END} {warning_count}")
    print(f"  {Colors.RED}✗ Errors:{Colors.END} {error_count}")
    
    if error_count == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ System is ready to start!{Colors.END}")
        print(f"\n  Run: {Colors.CYAN}python api_server_v4.py{Colors.END}")
        print(f"  Or:  {Colors.CYAN}uvicorn api_server_v4:app --reload{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Fix errors before starting the server{Colors.END}")
        
        print(f"\n{Colors.YELLOW}Errors to fix:{Colors.END}")
        for r in all_results:
            if r.status == 'error':
                print(f"  • {r.name}: {r.message}")
                if r.details:
                    print(f"    {Colors.CYAN}{r.details}{Colors.END}")
    
    # API Key setup tips
    if warning_count > 0:
        print(f"\n{Colors.YELLOW}Tips to improve functionality:{Colors.END}")
        
        key_warnings = [r for r in all_results if r.status == 'warning' and 'Not configured' in r.message]
        if key_warnings:
            print(f"\n  📋 Free API keys you can add:")
            for r in key_warnings[:5]:
                if r.details:
                    print(f"    • {r.name}: {r.details}")
    
    print()


# ============================================================
# MAIN
# ============================================================

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    print_header()
    all_results = []
    
    # Python version
    print_section("Python Environment")
    result = check_python_version()
    print_result(result)
    all_results.append(result)
    
    # Required packages
    print_section("Required Packages")
    results = check_required_packages()
    for r in results:
        print_result(r)
    all_results.extend(results)
    
    # Verity modules
    print_section("Verity Modules")
    results = check_verity_modules()
    for r in results:
        print_result(r)
    all_results.extend(results)
    
    # API keys
    print_section("API Keys")
    results = check_api_keys()
    for r in results:
        print_result(r)
    all_results.extend(results)
    
    # Services connectivity
    print_section("Service Connectivity")
    results = await check_services()
    for r in results:
        print_result(r)
    all_results.extend(results)
    
    # Summary
    print_summary(all_results)
    
    # Return exit code
    error_count = sum(1 for r in all_results if r.status == 'error')
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
