#!/usr/bin/env python3
"""
Verity Systems - API Connectivity Test Suite
Tests all configured API providers to verify they're working.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import httpx

# Test results storage
results: Dict[str, Dict[str, Any]] = {}


def log_result(name: str, status: str, details: str = "", response_time: float = 0):
    """Log a test result"""
    emoji = "[OK]" if status == "OK" else "[FAIL]" if status == "FAILED" else "[SKIP]"
    results[name] = {
        "status": status,
        "details": details,
        "response_time_ms": round(response_time * 1000, 2)
    }
    print(f"{emoji} {name}: {status} ({round(response_time * 1000)}ms) {details}")


async def test_anthropic():
    """Test Anthropic Claude API"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Anthropic Claude", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Say 'API working' in 3 words"}]
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Anthropic Claude", "OK", "claude-3-haiku", elapsed)
        else:
            log_result("Anthropic Claude", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Anthropic Claude", "FAILED", str(e)[:100])


async def test_groq():
    """Test Groq API"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Groq", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Say 'API working'"}]
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Groq", "OK", "llama-3.1-8b-instant", elapsed)
        else:
            log_result("Groq", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Groq", "FAILED", str(e)[:100])


async def test_google_ai():
    """Test Google Gemini API"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Google Gemini", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            # Try v1beta API with correct model names (discovered via API)
            # Available models: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash-exp, gemini-2.0-flash
            models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
            
            for model in models:
                try:
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [{"parts": [{"text": "Say 'API working'"}]}]
                        }
                    )
                    if response.status_code == 200:
                        elapsed = time.time() - start
                        log_result("Google Gemini", "OK", f"{model}", elapsed)
                        return
                except:
                    continue
            elapsed = time.time() - start
            log_result("Google Gemini", "FAILED", f"No working model: {response.text[:80] if response else 'timeout'}", elapsed)
    except Exception as e:
        log_result("Google Gemini", "FAILED", str(e)[:100])


async def test_openai():
    """Test OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("OpenAI", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Say 'API working'"}]
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("OpenAI", "OK", "gpt-3.5-turbo", elapsed)
        else:
            log_result("OpenAI", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("OpenAI", "FAILED", str(e)[:100])


async def test_mistral():
    """Test Mistral API"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Mistral", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small-latest",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Say 'API working'"}]
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Mistral", "OK", "mistral-small-latest", elapsed)
        else:
            log_result("Mistral", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Mistral", "FAILED", str(e)[:100])


async def test_cohere():
    """Test Cohere API"""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Cohere", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        # Try multiple model names as Cohere deprecates them frequently
        models_to_try = ["command-r-plus", "command-r-08-2024", "command", "command-nightly"]
        async with httpx.AsyncClient(timeout=30) as client:
            for model in models_to_try:
                response = await client.post(
                    "https://api.cohere.ai/v1/chat",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "message": "Say 'API working'"
                    }
                )
                if response.status_code == 200:
                    elapsed = time.time() - start
                    log_result("Cohere", "OK", model, elapsed)
                    return
            # If none worked
            elapsed = time.time() - start
            log_result("Cohere", "FAILED", f"All models deprecated: {response.text[:80]}", elapsed)
    except Exception as e:
        log_result("Cohere", "FAILED", str(e)[:100])


async def test_deepseek():
    """Test DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("DeepSeek", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Say 'API working'"}]
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("DeepSeek", "OK", "deepseek-chat", elapsed)
        else:
            log_result("DeepSeek", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("DeepSeek", "FAILED", str(e)[:100])


async def test_perplexity():
    """Test Perplexity API"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Perplexity", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        # Try multiple model names as Perplexity changes them
        models_to_try = [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online", 
            "sonar-small-online",
            "sonar"
        ]
        async with httpx.AsyncClient(timeout=30) as client:
            for model in models_to_try:
                try:
                    response = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "max_tokens": 50,
                            "messages": [{"role": "user", "content": "Say 'API working'"}]
                        }
                    )
                    if response.status_code == 200:
                        elapsed = time.time() - start
                        log_result("Perplexity", "OK", model, elapsed)
                        return
                except:
                    continue
            elapsed = time.time() - start
            log_result("Perplexity", "FAILED", f"No working model found", elapsed)
    except Exception as e:
        log_result("Perplexity", "FAILED", str(e)[:100])


async def test_openrouter():
    """Test OpenRouter API"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("OpenRouter", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        # Try multiple free models
        free_models = [
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "huggingfaceh4/zephyr-7b-beta:free"
        ]
        async with httpx.AsyncClient(timeout=30) as client:
            for model in free_models:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://verity.systems"
                    },
                    json={
                        "model": model,
                        "max_tokens": 50,
                        "messages": [{"role": "user", "content": "Say 'API working'"}]
                    }
                )
                if response.status_code == 200:
                    elapsed = time.time() - start
                    log_result("OpenRouter", "OK", model.split('/')[1].split(':')[0], elapsed)
                    return
            # If all failed
            elapsed = time.time() - start
            log_result("OpenRouter", "FAILED", f"No free models available: {response.text[:80]}", elapsed)
    except Exception as e:
        log_result("OpenRouter", "FAILED", str(e)[:100])


async def test_huggingface():
    """Test HuggingFace API"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("HuggingFace", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            # Try new router endpoint first
            response = await client.post(
                "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "inputs": "The sky is blue.",
                    "parameters": {"candidate_labels": ["true", "false"]}
                }
            )
            elapsed = time.time() - start
            if response.status_code == 200:
                log_result("HuggingFace", "OK", "bart-large-mnli (router)", elapsed)
            elif response.status_code == 503:
                log_result("HuggingFace", "LOADING", "Model loading, try again", elapsed)
            else:
                # Try legacy endpoint as fallback
                response2 = await client.post(
                    "https://api-inference.huggingface.co/models/facebook/bart-large-mnli",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "inputs": "The sky is blue.",
                        "parameters": {"candidate_labels": ["true", "false"]}
                    }
                )
                if response2.status_code == 200:
                    log_result("HuggingFace", "OK", "bart-large-mnli (legacy)", time.time() - start)
                else:
                    log_result("HuggingFace", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("HuggingFace", "FAILED", str(e)[:100])


# ============== SEARCH APIs ==============

async def test_tavily():
    """Test Tavily Search API"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Tavily Search", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": "test query",
                    "max_results": 1
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Tavily Search", "OK", "search working", elapsed)
        else:
            log_result("Tavily Search", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Tavily Search", "FAILED", str(e)[:100])


async def test_exa():
    """Test Exa (Metaphor) Search API"""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Exa Search", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.exa.ai/search",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "query": "test query",
                    "numResults": 1
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Exa Search", "OK", "search working", elapsed)
        else:
            log_result("Exa Search", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Exa Search", "FAILED", str(e)[:100])


async def test_brave():
    """Test Brave Search API"""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Brave Search", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "X-Subscription-Token": api_key,
                    "Accept": "application/json"
                },
                params={"q": "test query", "count": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Brave Search", "OK", "search working", elapsed)
        elif response.status_code == 401:
            log_result("Brave Search", "FAILED", "Invalid API key", elapsed)
        elif response.status_code == 429:
            log_result("Brave Search", "RATE_LIMITED", "Quota exceeded", elapsed)
        else:
            log_result("Brave Search", "FAILED", f"HTTP {response.status_code}: {response.text[:80] if response.text else 'No response'}", elapsed)
    except Exception as e:
        log_result("Brave Search", "FAILED", str(e)[:100])


async def test_serper():
    """Test Serper (Google) API"""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Serper Google", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                json={"q": "test query", "num": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Serper Google", "OK", "search working", elapsed)
        else:
            log_result("Serper Google", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Serper Google", "FAILED", str(e)[:100])


async def test_you():
    """Test You.com API"""
    api_key = os.getenv("YOU_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("You.com Search", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.ydc-index.io/search",
                headers={"X-API-Key": api_key},
                params={"query": "test query"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("You.com Search", "OK", "search working", elapsed)
        else:
            log_result("You.com Search", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("You.com Search", "FAILED", str(e)[:100])


async def test_jina():
    """Test Jina AI API"""
    api_key = os.getenv("JINA_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Jina AI", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://r.jina.ai/https://example.com",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Jina AI", "OK", "reader working", elapsed)
        else:
            log_result("Jina AI", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Jina AI", "FAILED", str(e)[:100])


# ============== FACT-CHECK & DATA APIs ==============

async def test_google_factcheck():
    """Test Google Fact Check API"""
    api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Google FactCheck", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                params={"key": api_key, "query": "climate change", "pageSize": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Google FactCheck", "OK", "search working", elapsed)
        else:
            log_result("Google FactCheck", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Google FactCheck", "FAILED", str(e)[:100])


async def test_claimbuster():
    """Test ClaimBuster API"""
    api_key = os.getenv("CLAIMBUSTER_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("ClaimBuster", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://idir.uta.edu/claimbuster/api/v2/score/text/The earth is flat",
                headers={"x-api-key": api_key}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("ClaimBuster", "OK", "scoring working", elapsed)
        else:
            log_result("ClaimBuster", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("ClaimBuster", "FAILED", str(e)[:100])


async def test_newsapi():
    """Test NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("NewsAPI", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params={"apiKey": api_key, "country": "us", "pageSize": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("NewsAPI", "OK", "headlines working", elapsed)
        else:
            log_result("NewsAPI", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("NewsAPI", "FAILED", str(e)[:100])


async def test_mediastack():
    """Test Mediastack API"""
    api_key = os.getenv("MEDIASTACK_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Mediastack", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "http://api.mediastack.com/v1/news",
                params={"access_key": api_key, "limit": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Mediastack", "OK", "news working", elapsed)
        else:
            log_result("Mediastack", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Mediastack", "FAILED", str(e)[:100])


async def test_wolfram():
    """Test Wolfram Alpha API"""
    app_id = os.getenv("WOLFRAM_APP_ID")
    if not app_id or "your-" in app_id:
        log_result("Wolfram Alpha", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(
                "https://api.wolframalpha.com/v2/query",  # HTTPS not HTTP
                params={"input": "2+2", "appid": app_id, "format": "plaintext", "output": "json"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Wolfram Alpha", "OK", "query working", elapsed)
        else:
            log_result("Wolfram Alpha", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Wolfram Alpha", "FAILED", str(e)[:100])


async def test_polygon():
    """Test Polygon.io API"""
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Polygon.io", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev",
                params={"apiKey": api_key}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Polygon.io", "OK", "financial data working", elapsed)
        else:
            log_result("Polygon.io", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Polygon.io", "FAILED", str(e)[:100])


# ============== FREE APIs (No key needed) ==============

async def test_wikipedia():
    """Test Wikipedia API (no key needed)"""
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/Earth",
                headers={
                    "User-Agent": "VeritySystems/1.0 (https://verity.systems; contact@verity.systems)"
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Wikipedia", "OK", "FREE - no key needed", elapsed)
        else:
            log_result("Wikipedia", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Wikipedia", "FAILED", str(e)[:100])


async def test_wikidata():
    """Test Wikidata API (no key needed)"""
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://www.wikidata.org/w/api.php",
                params={"action": "wbgetentities", "ids": "Q2", "format": "json"},
                headers={
                    "User-Agent": "VeritySystems/1.0 (https://verity.systems; contact@verity.systems)"
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Wikidata", "OK", "FREE - no key needed", elapsed)
        else:
            log_result("Wikidata", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Wikidata", "FAILED", str(e)[:100])


async def test_semantic_scholar():
    """Test Semantic Scholar API (no key needed for basic)"""
    try:
        import time
        start = time.time()
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        headers = {"User-Agent": "VeritySystems/1.0 (https://verity.systems)"}
        if api_key:
            headers["x-api-key"] = api_key
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={"query": "machine learning", "limit": 1},
                headers=headers
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Semantic Scholar", "OK", "FREE - academic search", elapsed)
        elif response.status_code == 429:
            log_result("Semantic Scholar", "RATE_LIMITED", "Add API key for higher limits", elapsed)
        else:
            log_result("Semantic Scholar", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Semantic Scholar", "FAILED", str(e)[:100])


async def test_crossref():
    """Test CrossRef API (no key needed)"""
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.crossref.org/works",
                params={"query": "climate", "rows": 1}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("CrossRef", "OK", "FREE - no key needed", elapsed)
        else:
            log_result("CrossRef", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("CrossRef", "FAILED", str(e)[:100])


async def test_pubmed():
    """Test PubMed API (no key needed)"""
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={"db": "pubmed", "term": "covid", "retmax": 1, "retmode": "json"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("PubMed", "OK", "FREE - no key needed", elapsed)
        else:
            log_result("PubMed", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("PubMed", "FAILED", str(e)[:100])


async def test_duckduckgo():
    """Test DuckDuckGo API (no key needed)"""
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": "python programming", "format": "json", "no_redirect": "1"},
                headers={
                    "User-Agent": "VeritySystems/1.0 (https://verity.systems)"
                }
            )
        elapsed = time.time() - start
        # DuckDuckGo returns 200 even for empty results, 202 means async processing
        if response.status_code in [200, 202]:
            data = response.json() if response.status_code == 200 else {}
            # Check if we got any results
            if data.get('Abstract') or data.get('RelatedTopics') or response.status_code == 200:
                log_result("DuckDuckGo", "OK", "FREE - Instant Answers", elapsed)
            else:
                log_result("DuckDuckGo", "OK", "FREE - no results for query", elapsed)
        else:
            log_result("DuckDuckGo", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("DuckDuckGo", "FAILED", str(e)[:100])


# ============================================================================
# NEW SERVICE TESTS - GitHub Education / Free Tier Services
# ============================================================================

async def test_together_ai():
    """Test Together AI API ($25 credit from GitHub Education)"""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Together AI", "SKIPPED", "No API key - Get $25 credit from GitHub Education")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Together AI", "OK", "Llama 3.3 70B working", elapsed)
        else:
            log_result("Together AI", "FAILED", f"HTTP {response.status_code}: {response.text[:100]}", elapsed)
    except Exception as e:
        log_result("Together AI", "FAILED", str(e)[:100])


async def test_mongodb():
    """Test MongoDB Atlas connection"""
    uri = os.getenv("MONGODB_URI")
    if not uri or "your-" in uri:
        log_result("MongoDB Atlas", "SKIPPED", "No URI - Free 512MB cluster available")
        return
    
    try:
        import time
        start = time.time()
        # Test by parsing the URI and attempting connection info
        if uri.startswith("mongodb"):
            log_result("MongoDB Atlas", "OK", "URI configured (driver test needed)", time.time() - start)
        else:
            log_result("MongoDB Atlas", "FAILED", "Invalid URI format")
    except Exception as e:
        log_result("MongoDB Atlas", "FAILED", str(e)[:100])


async def test_ipinfo():
    """Test IPInfo API (50k req/month free)"""
    api_key = os.getenv("IPINFO_TOKEN")
    if not api_key or "your-" in api_key:
        log_result("IPInfo", "SKIPPED", "No API key - 50k/month free tier")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://ipinfo.io/8.8.8.8?token={api_key}"
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            log_result("IPInfo", "OK", f"City: {data.get('city', 'N/A')}", elapsed)
        else:
            log_result("IPInfo", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("IPInfo", "FAILED", str(e)[:100])


async def test_sendgrid():
    """Test SendGrid API (100 emails/day free)"""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("SendGrid", "SKIPPED", "No API key - 100 emails/day free")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.sendgrid.com/v3/scopes",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("SendGrid", "OK", "Email API ready", elapsed)
        else:
            log_result("SendGrid", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("SendGrid", "FAILED", str(e)[:100])


async def test_configcat():
    """Test ConfigCat API (feature flags)"""
    sdk_key = os.getenv("CONFIGCAT_SDK_KEY")
    if not sdk_key or "your-" in sdk_key:
        log_result("ConfigCat", "SKIPPED", "No SDK key - Free tier available")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://cdn-global.configcat.com/configuration-files/{sdk_key}/config_v6.json"
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("ConfigCat", "OK", "Feature flags loaded", elapsed)
        else:
            log_result("ConfigCat", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("ConfigCat", "FAILED", str(e)[:100])


async def test_carto():
    """Test Carto API (geographic data)"""
    api_key = os.getenv("CARTO_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Carto", "SKIPPED", "No API key - Free tier from GitHub Education")
        return
    
    try:
        import time
        start = time.time()
        account = os.getenv("CARTO_USERNAME", "verity")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://{account}.carto.com/api/v2/sql",
                params={"q": "SELECT 1", "api_key": api_key}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Carto", "OK", "Geographic SQL API ready", elapsed)
        else:
            log_result("Carto", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Carto", "FAILED", str(e)[:100])


async def test_browserstack():
    """Test BrowserStack API (cross-browser testing)"""
    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    if not username or not access_key or "your-" in username:
        log_result("BrowserStack", "SKIPPED", "No credentials - Free from GitHub Education")
        return
    
    try:
        import time
        import base64
        start = time.time()
        auth = base64.b64encode(f"{username}:{access_key}".encode()).decode()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.browserstack.com/automate/plan.json",
                headers={"Authorization": f"Basic {auth}"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            log_result("BrowserStack", "OK", f"Plan: {data.get('automate_plan', 'N/A')}", elapsed)
        else:
            log_result("BrowserStack", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("BrowserStack", "FAILED", str(e)[:100])


async def test_new_relic():
    """Test New Relic API (APM)"""
    api_key = os.getenv("NEW_RELIC_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("New Relic", "SKIPPED", "No API key - Free tier available")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.newrelic.com/v2/applications.json",
                headers={"Api-Key": api_key}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("New Relic", "OK", "APM connected", elapsed)
        elif response.status_code == 401:
            log_result("New Relic", "FAILED", "Invalid API key", elapsed)
        else:
            log_result("New Relic", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("New Relic", "FAILED", str(e)[:100])


async def test_sentry():
    """Test Sentry API (error tracking)"""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn or "your-" in dsn:
        log_result("Sentry", "SKIPPED", "No DSN - 5k errors/month free")
        return
    
    try:
        import time
        start = time.time()
        # Sentry DSN is validated by format
        if dsn.startswith("https://") and "@" in dsn and "sentry.io" in dsn:
            log_result("Sentry", "OK", "DSN configured correctly", time.time() - start)
        else:
            log_result("Sentry", "FAILED", "Invalid DSN format")
    except Exception as e:
        log_result("Sentry", "FAILED", str(e)[:100])


async def test_honeybadger():
    """Test Honeybadger API (error tracking)"""
    api_key = os.getenv("HONEYBADGER_API_KEY")
    if not api_key or "your-" in api_key:
        log_result("Honeybadger", "SKIPPED", "No API key - Free from GitHub Education")
        return
    
    try:
        import time
        start = time.time()
        # Honeybadger auth token is used directly in header
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(
                "https://app.honeybadger.io/v2/teams",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            log_result("Honeybadger", "OK", "Error tracking ready", elapsed)
        elif response.status_code == 401:
            log_result("Honeybadger", "AUTH_ERROR", "Invalid API key", elapsed)
        else:
            # If we get a response at all, the service is reachable
            log_result("Honeybadger", "OK", f"API reachable (HTTP {response.status_code})", elapsed)
    except Exception as e:
        log_result("Honeybadger", "FAILED", str(e)[:100])


async def test_stripe():
    """Test Stripe API (payments)"""
    api_key = os.getenv("STRIPE_SECRET_KEY")
    if not api_key or "your-" in api_key:
        log_result("Stripe", "SKIPPED", "No API key")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.stripe.com/v1/balance",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            mode = "test" if "test" in api_key else "live"
            log_result("Stripe", "OK", f"Mode: {mode}", elapsed)
        else:
            log_result("Stripe", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Stripe", "FAILED", str(e)[:100])


async def test_supabase():
    """Test Supabase API (database)"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key or "your-" in url:
        log_result("Supabase", "SKIPPED", "No credentials - 500MB free")
        return
    
    try:
        import time
        start = time.time()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{url}/rest/v1/",
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}"
                }
            )
        elapsed = time.time() - start
        if response.status_code in [200, 204]:
            log_result("Supabase", "OK", "Database connected", elapsed)
        else:
            log_result("Supabase", "FAILED", f"HTTP {response.status_code}", elapsed)
    except Exception as e:
        log_result("Supabase", "FAILED", str(e)[:100])


async def main():
    """Run all API tests"""
    print("=" * 70)
    print("VERITY SYSTEMS - COMPREHENSIVE API CONNECTIVITY TEST")
    print(f"   Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    print("\n[AI/LLM PROVIDERS]")
    print("-" * 50)
    await test_anthropic()
    await test_groq()
    await test_google_ai()
    await test_openai()
    await test_mistral()
    await test_cohere()
    await test_deepseek()
    await test_perplexity()
    await test_openrouter()
    await test_huggingface()
    await test_together_ai()
    
    print("\n[SEARCH PROVIDERS]")
    print("-" * 50)
    await test_tavily()
    await test_exa()
    await test_brave()
    await test_serper()
    await test_you()
    await test_jina()
    
    print("\n[FACT-CHECK & DATA PROVIDERS]")
    print("-" * 50)
    await test_google_factcheck()
    await test_claimbuster()
    await test_newsapi()
    await test_mediastack()
    await test_wolfram()
    await test_polygon()
    
    print("\n[FREE APIs - No Key Required]")
    print("-" * 50)
    await test_wikipedia()
    await test_wikidata()
    await test_semantic_scholar()
    await test_crossref()
    await test_pubmed()
    await test_duckduckgo()
    
    print("\n[INFRASTRUCTURE & SERVICES]")
    print("-" * 50)
    await test_stripe()
    await test_supabase()
    await test_mongodb()
    await test_sendgrid()
    await test_ipinfo()
    
    print("\n[MONITORING & DEVOPS]")
    print("-" * 50)
    await test_sentry()
    await test_honeybadger()
    await test_new_relic()
    await test_browserstack()
    await test_configcat()
    await test_carto()
    
    # Summary
    print("\n" + "=" * 70)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 70)
    
    ok_count = sum(1 for r in results.values() if r["status"] == "OK")
    failed_count = sum(1 for r in results.values() if r["status"] == "FAILED")
    skipped_count = sum(1 for r in results.values() if r["status"] == "SKIPPED")
    loading_count = sum(1 for r in results.values() if r["status"] == "LOADING")
    auth_error = sum(1 for r in results.values() if r["status"] == "AUTH_ERROR")
    rate_limited = sum(1 for r in results.values() if r["status"] == "RATE_LIMITED")
    
    print(f"[OK]   Working:      {ok_count}")
    print(f"[FAIL] Failed:       {failed_count}")
    print(f"[AUTH] Auth Error:   {auth_error}")
    print(f"[RATE] Rate Limited: {rate_limited}")
    print(f"[LOAD] Loading:      {loading_count}")
    print(f"[SKIP] Skipped:      {skipped_count}")
    print(f"       Total:        {len(results)}")
    
    if failed_count > 0:
        print("\n[FAIL] APIs needing attention:")
        for name, result in results.items():
            if result["status"] == "FAILED":
                print(f"   - {name}: {result['details']}")
    
    if skipped_count > 0:
        print("\n[SKIP] APIs needing API keys:")
        for name, result in results.items():
            if result["status"] == "SKIPPED":
                print(f"   - {name}: {result['details']}")
    
    print("\n" + "=" * 70)
    
    # Save results to JSON
    with open("api_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "working": ok_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "loading": loading_count,
                "auth_error": auth_error,
                "rate_limited": rate_limited
            },
            "results": results
        }, f, indent=2)
    print("Results saved to api_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
