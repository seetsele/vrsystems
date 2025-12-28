"""
Verity Systems - Unified LLM Gateway
Integrates LiteLLM, Ollama, and multiple AI providers through a single interface.

This module provides:
- LiteLLM integration for 100+ cloud models
- Ollama integration for local models
- Automatic fallback between providers
- Cost tracking and optimization
- Connection pooling and retries

Author: Verity Systems
License: MIT
"""

import os
import asyncio
import aiohttp
import logging
import json
import hashlib
import time
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
from enum import Enum
import traceback

logger = logging.getLogger('VerityUnifiedLLM')

# ============================================================
# CONFIGURATION
# ============================================================

class ModelTier(Enum):
    """Model tiers by cost and capability"""
    FREE = "free"           # Completely free models
    CHEAP = "cheap"         # < $1/M tokens
    STANDARD = "standard"   # $1-10/M tokens
    PREMIUM = "premium"     # > $10/M tokens
    LOCAL = "local"         # Local models (Ollama)


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: str
    tier: ModelTier
    context_window: int
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_streaming: bool = True
    supports_function_calling: bool = False
    max_output_tokens: int = 4096
    
    
# Model catalog with pricing and capabilities
MODEL_CATALOG: Dict[str, ModelConfig] = {
    # ========== FREE TIER ==========
    "groq/llama-3.1-70b-versatile": ModelConfig(
        name="Llama 3.1 70B", provider="groq", tier=ModelTier.FREE,
        context_window=131072, cost_per_1k_input=0.0, cost_per_1k_output=0.0,
        supports_function_calling=True
    ),
    "groq/llama-3.1-8b-instant": ModelConfig(
        name="Llama 3.1 8B", provider="groq", tier=ModelTier.FREE,
        context_window=131072, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "groq/gemma2-9b-it": ModelConfig(
        name="Gemma 2 9B", provider="groq", tier=ModelTier.FREE,
        context_window=8192, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "groq/mixtral-8x7b-32768": ModelConfig(
        name="Mixtral 8x7B", provider="groq", tier=ModelTier.FREE,
        context_window=32768, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    
    # OpenRouter free models
    "openrouter/google/gemma-2-9b-it:free": ModelConfig(
        name="Gemma 2 9B (OpenRouter)", provider="openrouter", tier=ModelTier.FREE,
        context_window=8192, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "openrouter/mistralai/mistral-7b-instruct:free": ModelConfig(
        name="Mistral 7B (OpenRouter)", provider="openrouter", tier=ModelTier.FREE,
        context_window=32768, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "openrouter/meta-llama/llama-3.1-8b-instruct:free": ModelConfig(
        name="Llama 3.1 8B (OpenRouter)", provider="openrouter", tier=ModelTier.FREE,
        context_window=131072, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    
    # ========== LOCAL (OLLAMA) ==========
    "ollama/llama3.1": ModelConfig(
        name="Llama 3.1 (Local)", provider="ollama", tier=ModelTier.LOCAL,
        context_window=131072, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "ollama/mistral": ModelConfig(
        name="Mistral (Local)", provider="ollama", tier=ModelTier.LOCAL,
        context_window=32768, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "ollama/gemma2": ModelConfig(
        name="Gemma 2 (Local)", provider="ollama", tier=ModelTier.LOCAL,
        context_window=8192, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "ollama/phi3": ModelConfig(
        name="Phi-3 (Local)", provider="ollama", tier=ModelTier.LOCAL,
        context_window=128000, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    "ollama/qwen2.5": ModelConfig(
        name="Qwen 2.5 (Local)", provider="ollama", tier=ModelTier.LOCAL,
        context_window=32768, cost_per_1k_input=0.0, cost_per_1k_output=0.0
    ),
    
    # ========== CHEAP TIER ==========
    "together_ai/meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": ModelConfig(
        name="Llama 3.2 90B Vision", provider="together_ai", tier=ModelTier.CHEAP,
        context_window=131072, cost_per_1k_input=0.00088, cost_per_1k_output=0.00088
    ),
    "together_ai/mistralai/Mixtral-8x22B-Instruct-v0.1": ModelConfig(
        name="Mixtral 8x22B", provider="together_ai", tier=ModelTier.CHEAP,
        context_window=65536, cost_per_1k_input=0.0009, cost_per_1k_output=0.0009
    ),
    "deepseek/deepseek-chat": ModelConfig(
        name="DeepSeek Chat", provider="deepseek", tier=ModelTier.CHEAP,
        context_window=64000, cost_per_1k_input=0.00014, cost_per_1k_output=0.00028,
        supports_function_calling=True
    ),
    "deepseek/deepseek-reasoner": ModelConfig(
        name="DeepSeek R1", provider="deepseek", tier=ModelTier.CHEAP,
        context_window=64000, cost_per_1k_input=0.00055, cost_per_1k_output=0.00219
    ),
    
    # ========== STANDARD TIER ==========
    "anthropic/claude-3-5-sonnet-20241022": ModelConfig(
        name="Claude 3.5 Sonnet", provider="anthropic", tier=ModelTier.STANDARD,
        context_window=200000, cost_per_1k_input=0.003, cost_per_1k_output=0.015,
        supports_function_calling=True
    ),
    "anthropic/claude-3-5-haiku-20241022": ModelConfig(
        name="Claude 3.5 Haiku", provider="anthropic", tier=ModelTier.STANDARD,
        context_window=200000, cost_per_1k_input=0.001, cost_per_1k_output=0.005,
        supports_function_calling=True
    ),
    "openai/gpt-4o-mini": ModelConfig(
        name="GPT-4o Mini", provider="openai", tier=ModelTier.STANDARD,
        context_window=128000, cost_per_1k_input=0.00015, cost_per_1k_output=0.0006,
        supports_function_calling=True
    ),
    "google/gemini-1.5-flash": ModelConfig(
        name="Gemini 1.5 Flash", provider="google", tier=ModelTier.STANDARD,
        context_window=1000000, cost_per_1k_input=0.000075, cost_per_1k_output=0.0003,
        supports_function_calling=True
    ),
    "google/gemini-1.5-pro": ModelConfig(
        name="Gemini 1.5 Pro", provider="google", tier=ModelTier.STANDARD,
        context_window=2000000, cost_per_1k_input=0.00125, cost_per_1k_output=0.005,
        supports_function_calling=True
    ),
    
    # ========== PREMIUM TIER ==========
    "openai/gpt-4o": ModelConfig(
        name="GPT-4o", provider="openai", tier=ModelTier.PREMIUM,
        context_window=128000, cost_per_1k_input=0.0025, cost_per_1k_output=0.01,
        supports_function_calling=True
    ),
    "anthropic/claude-3-opus-20240229": ModelConfig(
        name="Claude 3 Opus", provider="anthropic", tier=ModelTier.PREMIUM,
        context_window=200000, cost_per_1k_input=0.015, cost_per_1k_output=0.075,
        supports_function_calling=True
    ),
    "openai/o1": ModelConfig(
        name="OpenAI o1", provider="openai", tier=ModelTier.PREMIUM,
        context_window=200000, cost_per_1k_input=0.015, cost_per_1k_output=0.06,
        supports_function_calling=False
    ),
}


# ============================================================
# CONNECTION POOL & SESSION MANAGEMENT
# ============================================================

class ConnectionPool:
    """Manages HTTP connection pools for all providers"""
    
    _instance = None
    _session: Optional[aiohttp.ClientSession] = None
    _ollama_session: Optional[aiohttp.ClientSession] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create the main HTTP session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=120, connect=10, sock_read=60)
            connector = aiohttp.TCPConnector(
                limit=100,  # Max 100 connections
                limit_per_host=20,  # Max 20 per host
                ttl_dns_cache=300,  # DNS cache for 5 min
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": "VeritySystemsLLM/1.0"}
            )
        return self._session
    
    async def get_ollama_session(self) -> aiohttp.ClientSession:
        """Get or create Ollama-specific session (longer timeouts for local)"""
        if self._ollama_session is None or self._ollama_session.closed:
            timeout = aiohttp.ClientTimeout(total=300, connect=5, sock_read=180)
            self._ollama_session = aiohttp.ClientSession(timeout=timeout)
        return self._ollama_session
    
    async def close(self):
        """Close all sessions"""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._ollama_session and not self._ollama_session.closed:
            await self._ollama_session.close()


# ============================================================
# RETRY & CIRCUIT BREAKER
# ============================================================

@dataclass
class CircuitState:
    """Track circuit breaker state per provider"""
    failures: int = 0
    last_failure: Optional[datetime] = None
    state: str = "closed"  # closed, open, half-open
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = datetime.utcnow()
        if self.failures >= 3:
            self.state = "open"
            
    def record_success(self):
        self.failures = 0
        self.state = "closed"
        
    def can_attempt(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open" and self.last_failure:
            # Try again after 60 seconds
            if datetime.utcnow() - self.last_failure > timedelta(seconds=60):
                self.state = "half-open"
                return True
        return self.state == "half-open"


class RetryHandler:
    """Handles retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.circuits: Dict[str, CircuitState] = {}
        
    def get_circuit(self, provider: str) -> CircuitState:
        if provider not in self.circuits:
            self.circuits[provider] = CircuitState()
        return self.circuits[provider]
    
    async def execute_with_retry(
        self, 
        provider: str,
        func,
        *args, 
        **kwargs
    ) -> Any:
        """Execute function with retry logic and circuit breaker"""
        circuit = self.get_circuit(provider)
        
        if not circuit.can_attempt():
            raise Exception(f"Circuit breaker open for {provider}")
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                circuit.record_success()
                return result
            except aiohttp.ClientError as e:
                last_exception = e
                circuit.record_failure()
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt+1}/{self.max_retries} for {provider} after {delay}s: {e}")
                    await asyncio.sleep(delay)
            except Exception as e:
                last_exception = e
                circuit.record_failure()
                logger.error(f"Error in {provider}: {e}")
                break
                
        raise last_exception or Exception(f"All retries failed for {provider}")


# ============================================================
# PROVIDER IMPLEMENTATIONS
# ============================================================

class BaseProvider:
    """Base class for LLM providers"""
    
    def __init__(self):
        self.pool = ConnectionPool()
        self.retry_handler = RetryHandler()
        
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        raise NotImplementedError


class LiteLLMProvider(BaseProvider):
    """
    LiteLLM integration - unified interface for 100+ models
    https://github.com/BerriAI/litellm
    """
    
    def __init__(self):
        super().__init__()
        self._litellm = None
        self._available = None
        
    def _check_litellm(self) -> bool:
        """Check if litellm is installed and import it"""
        if self._available is not None:
            return self._available
        try:
            import litellm
            litellm.set_verbose = False  # Reduce logging
            self._litellm = litellm
            self._available = True
            logger.info("LiteLLM available")
        except ImportError:
            self._available = False
            logger.warning("LiteLLM not installed. Run: pip install litellm")
        return self._available
    
    @property
    def is_available(self) -> bool:
        return self._check_litellm()
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using LiteLLM"""
        if not self.is_available:
            raise Exception("LiteLLM not available")
        
        async def _call():
            # LiteLLM supports both sync and async
            response = await self._litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "provider": "litellm",
                "finish_reason": response.choices[0].finish_reason
            }
        
        provider = model.split("/")[0] if "/" in model else "unknown"
        return await self.retry_handler.execute_with_retry(provider, _call)


class OllamaProvider(BaseProvider):
    """
    Ollama integration - run models locally
    https://ollama.com
    """
    
    def __init__(self, base_url: str = None):
        super().__init__()
        self.base_url = base_url or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self._available = None
        self._models: List[str] = []
        
    async def check_availability(self) -> bool:
        """Check if Ollama is running"""
        try:
            session = await self.pool.get_ollama_session()
            async with session.get(f"{self.base_url}/api/tags", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._models = [m['name'] for m in data.get('models', [])]
                    self._available = True
                    logger.info(f"Ollama available with models: {self._models}")
                    return True
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        self._available = False
        return False
    
    @property
    def is_available(self) -> bool:
        if self._available is None:
            # Run sync check
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return False  # Can't check synchronously
            return loop.run_until_complete(self.check_availability())
        return self._available
    
    @property
    def available_models(self) -> List[str]:
        return self._models
    
    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama library"""
        try:
            session = await self.pool.get_ollama_session()
            async with session.post(
                f"{self.base_url}/api/pull",
                json={"name": model}
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Successfully pulled Ollama model: {model}")
                    return True
        except Exception as e:
            logger.error(f"Failed to pull Ollama model {model}: {e}")
        return False
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using local Ollama model"""
        
        # Strip ollama/ prefix if present
        if model.startswith("ollama/"):
            model = model[7:]
        
        async def _call():
            session = await self.pool.get_ollama_session()
            async with session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Ollama error: {resp.status} - {text}")
                data = await resp.json()
                return {
                    "content": data.get("message", {}).get("content", ""),
                    "model": model,
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    },
                    "provider": "ollama",
                    "finish_reason": "stop"
                }
        
        return await self.retry_handler.execute_with_retry("ollama", _call)


class GroqProvider(BaseProvider):
    """Direct Groq API integration for ultra-fast inference"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using Groq's ultra-fast inference"""
        
        if model.startswith("groq/"):
            model = model[5:]
        
        async def _call():
            session = await self.pool.get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Groq error: {resp.status} - {text}")
                data = await resp.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "usage": data.get("usage", {}),
                    "provider": "groq",
                    "finish_reason": data["choices"][0].get("finish_reason", "stop")
                }
        
        return await self.retry_handler.execute_with_retry("groq", _call)


class OpenRouterProvider(BaseProvider):
    """OpenRouter - access 500+ models through one API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using OpenRouter"""
        
        if model.startswith("openrouter/"):
            model = model[11:]
        
        async def _call():
            session = await self.pool.get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://verity-systems.com",
                    "X-Title": "Verity Systems Fact Checker"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"OpenRouter error: {resp.status} - {text}")
                data = await resp.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "usage": data.get("usage", {}),
                    "provider": "openrouter",
                    "finish_reason": data["choices"][0].get("finish_reason", "stop")
                }
        
        return await self.retry_handler.execute_with_retry("openrouter", _call)


class DeepSeekProvider(BaseProvider):
    """DeepSeek - ultra cheap and capable models"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using DeepSeek"""
        
        if model.startswith("deepseek/"):
            model = model[9:]
        
        async def _call():
            session = await self.pool.get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"DeepSeek error: {resp.status} - {text}")
                data = await resp.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "usage": data.get("usage", {}),
                    "provider": "deepseek",
                    "finish_reason": data["choices"][0].get("finish_reason", "stop")
                }
        
        return await self.retry_handler.execute_with_retry("deepseek", _call)


class TogetherAIProvider(BaseProvider):
    """Together AI - fast inference with free credits"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('TOGETHER_API_KEY') or os.getenv('TOGETHER_AI_KEY')
        self.base_url = "https://api.together.xyz/v1"
        
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using Together AI"""
        
        if model.startswith("together_ai/"):
            model = model[12:]
        
        async def _call():
            session = await self.pool.get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Together AI error: {resp.status} - {text}")
                data = await resp.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "usage": data.get("usage", {}),
                    "provider": "together_ai",
                    "finish_reason": data["choices"][0].get("finish_reason", "stop")
                }
        
        return await self.retry_handler.execute_with_retry("together_ai", _call)


# ============================================================
# UNIFIED LLM GATEWAY
# ============================================================

class UnifiedLLMGateway:
    """
    Main gateway for accessing all LLM providers.
    
    Features:
    - Automatic fallback between providers
    - Cost optimization routing
    - Local model support via Ollama
    - LiteLLM for 100+ cloud models
    - Connection pooling and retries
    
    Usage:
        gateway = UnifiedLLMGateway()
        result = await gateway.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="auto",  # Auto-select best available
            prefer_free=True
        )
    """
    
    def __init__(self):
        self.litellm = LiteLLMProvider()
        self.ollama = OllamaProvider()
        self.groq = GroqProvider()
        self.openrouter = OpenRouterProvider()
        self.deepseek = DeepSeekProvider()
        self.together = TogetherAIProvider()
        
        self.usage_tracker: Dict[str, Dict[str, float]] = {}
        self.pool = ConnectionPool()
        
        # Provider priority for fallback
        self.fallback_order = [
            ("groq", self.groq),
            ("ollama", self.ollama),
            ("openrouter", self.openrouter),
            ("deepseek", self.deepseek),
            ("together_ai", self.together),
            ("litellm", self.litellm),
        ]
        
    async def initialize(self):
        """Initialize all providers and check availability"""
        logger.info("Initializing UnifiedLLMGateway...")
        
        # Check Ollama
        await self.ollama.check_availability()
        
        available = []
        if self.groq.is_available:
            available.append("Groq")
        if self.ollama.is_available:
            available.append(f"Ollama ({len(self.ollama.available_models)} models)")
        if self.openrouter.is_available:
            available.append("OpenRouter")
        if self.deepseek.is_available:
            available.append("DeepSeek")
        if self.together.is_available:
            available.append("Together AI")
        if self.litellm.is_available:
            available.append("LiteLLM")
            
        logger.info(f"Available providers: {', '.join(available) or 'None'}")
        return available
        
    async def close(self):
        """Close all connections"""
        await self.pool.close()
        
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        if self.groq.is_available:
            available.append("groq")
        if self.ollama.is_available:
            available.append("ollama")
        if self.openrouter.is_available:
            available.append("openrouter")
        if self.deepseek.is_available:
            available.append("deepseek")
        if self.together.is_available:
            available.append("together_ai")
        if self.litellm.is_available:
            available.append("litellm")
        return available
    
    def select_model(
        self,
        prefer_free: bool = True,
        prefer_local: bool = False,
        min_context: int = 4096,
        require_function_calling: bool = False
    ) -> Optional[str]:
        """
        Auto-select the best available model based on preferences.
        
        Args:
            prefer_free: Prefer free tier models
            prefer_local: Prefer local Ollama models
            min_context: Minimum context window required
            require_function_calling: Must support function calling
            
        Returns:
            Model identifier string or None if no suitable model
        """
        candidates = []
        
        for model_id, config in MODEL_CATALOG.items():
            # Check context window
            if config.context_window < min_context:
                continue
                
            # Check function calling
            if require_function_calling and not config.supports_function_calling:
                continue
                
            # Check provider availability
            provider = config.provider
            if provider == "groq" and not self.groq.is_available:
                continue
            elif provider == "ollama" and not self.ollama.is_available:
                continue
            elif provider == "openrouter" and not self.openrouter.is_available:
                continue
            elif provider == "deepseek" and not self.deepseek.is_available:
                continue
            elif provider == "together_ai" and not self.together.is_available:
                continue
                
            candidates.append((model_id, config))
        
        if not candidates:
            return None
            
        # Sort by preference
        def sort_key(item):
            model_id, config = item
            score = 0
            
            if prefer_local and config.tier == ModelTier.LOCAL:
                score -= 1000
            if prefer_free and config.tier == ModelTier.FREE:
                score -= 500
            
            # Prefer larger context windows
            score -= config.context_window / 10000
            
            # Prefer cheaper models
            score += (config.cost_per_1k_input + config.cost_per_1k_output) * 100
            
            return score
            
        candidates.sort(key=sort_key)
        return candidates[0][0]
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        prefer_free: bool = True,
        prefer_local: bool = False,
        fallback: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete a chat with automatic model selection and fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier or "auto" for auto-selection
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            prefer_free: When auto-selecting, prefer free models
            prefer_local: When auto-selecting, prefer local Ollama models
            fallback: If primary model fails, try alternatives
            
        Returns:
            Dict with 'content', 'model', 'usage', 'provider', 'finish_reason'
        """
        # Auto-select model if needed
        if model == "auto":
            model = self.select_model(prefer_free=prefer_free, prefer_local=prefer_local)
            if not model:
                raise Exception("No available models found")
            logger.info(f"Auto-selected model: {model}")
        
        # Determine provider from model string
        provider = None
        if model.startswith("groq/"):
            provider = self.groq
        elif model.startswith("ollama/"):
            provider = self.ollama
        elif model.startswith("openrouter/"):
            provider = self.openrouter
        elif model.startswith("deepseek/"):
            provider = self.deepseek
        elif model.startswith("together_ai/"):
            provider = self.together
        else:
            # Try LiteLLM as default
            provider = self.litellm
        
        # Try primary provider
        try:
            result = await provider.complete(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            self._track_usage(result)
            return result
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}")
            if not fallback:
                raise
        
        # Fallback to other providers
        errors = [str(e)]
        for name, fallback_provider in self.fallback_order:
            if fallback_provider == provider:
                continue
            if not getattr(fallback_provider, 'is_available', False):
                continue
                
            try:
                # Select appropriate model for this provider
                fallback_model = self._get_fallback_model(name)
                if not fallback_model:
                    continue
                    
                logger.info(f"Falling back to {name} with model {fallback_model}")
                result = await fallback_provider.complete(
                    messages=messages,
                    model=fallback_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                self._track_usage(result)
                return result
            except Exception as e:
                errors.append(f"{name}: {e}")
                continue
        
        raise Exception(f"All providers failed: {'; '.join(errors)}")
    
    def _get_fallback_model(self, provider: str) -> Optional[str]:
        """Get the default model for a provider"""
        defaults = {
            "groq": "groq/llama-3.1-70b-versatile",
            "ollama": "ollama/llama3.1" if "llama3.1" in self.ollama.available_models else (
                self.ollama.available_models[0] if self.ollama.available_models else None
            ),
            "openrouter": "openrouter/meta-llama/llama-3.1-8b-instruct:free",
            "deepseek": "deepseek/deepseek-chat",
            "together_ai": "together_ai/meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        }
        return defaults.get(provider)
    
    def _track_usage(self, result: Dict[str, Any]):
        """Track token usage for cost monitoring"""
        provider = result.get("provider", "unknown")
        model = result.get("model", "unknown")
        usage = result.get("usage", {})
        
        if provider not in self.usage_tracker:
            self.usage_tracker[provider] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
                "estimated_cost": 0.0
            }
        
        tracker = self.usage_tracker[provider]
        tracker["prompt_tokens"] += usage.get("prompt_tokens", 0)
        tracker["completion_tokens"] += usage.get("completion_tokens", 0)
        tracker["total_tokens"] += usage.get("total_tokens", 0)
        tracker["requests"] += 1
        
        # Estimate cost if model is in catalog
        for model_id, config in MODEL_CATALOG.items():
            if model in model_id or model_id.endswith(model):
                cost = (
                    usage.get("prompt_tokens", 0) * config.cost_per_1k_input / 1000 +
                    usage.get("completion_tokens", 0) * config.cost_per_1k_output / 1000
                )
                tracker["estimated_cost"] += cost
                break
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_cost = sum(p["estimated_cost"] for p in self.usage_tracker.values())
        total_tokens = sum(p["total_tokens"] for p in self.usage_tracker.values())
        total_requests = sum(p["requests"] for p in self.usage_tracker.values())
        
        return {
            "by_provider": self.usage_tracker,
            "totals": {
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "estimated_cost_usd": round(total_cost, 4)
            }
        }


# ============================================================
# FACT CHECKING INTEGRATION
# ============================================================

class LLMFactChecker:
    """
    Specialized fact-checking using LLMs with multi-model consensus.
    """
    
    FACT_CHECK_PROMPT = """You are a fact-checking AI assistant. Analyze the following claim and determine its accuracy.

CLAIM: {claim}

Provide your analysis in the following JSON format:
{{
    "verdict": "TRUE" | "FALSE" | "PARTIALLY_TRUE" | "UNVERIFIABLE" | "MISLEADING",
    "confidence": 0.0-1.0,
    "explanation": "Your detailed explanation",
    "key_facts": ["Fact 1", "Fact 2", ...],
    "sources_needed": ["Type of source that would help verify this"],
    "potential_biases": ["Any biases to consider"]
}}

Be objective and thorough in your analysis. If you cannot verify the claim, say so."""

    def __init__(self, gateway: UnifiedLLMGateway = None):
        self.gateway = gateway or UnifiedLLMGateway()
        
    async def verify_claim(
        self,
        claim: str,
        context: Optional[str] = None,
        use_consensus: bool = True,
        num_models: int = 3
    ) -> Dict[str, Any]:
        """
        Verify a claim using LLM analysis.
        
        Args:
            claim: The claim to verify
            context: Optional additional context
            use_consensus: Use multiple models and aggregate results
            num_models: Number of models to use for consensus
            
        Returns:
            Verification result with verdict, confidence, explanation
        """
        prompt = self.FACT_CHECK_PROMPT.format(claim=claim)
        if context:
            prompt += f"\n\nADDITIONAL CONTEXT: {context}"
        
        messages = [{"role": "user", "content": prompt}]
        
        if not use_consensus:
            # Single model verification
            result = await self.gateway.complete(
                messages=messages,
                model="auto",
                temperature=0.3,  # Lower temperature for factual accuracy
                max_tokens=1024
            )
            return self._parse_result(result["content"], result["model"])
        
        # Multi-model consensus
        models = self._select_consensus_models(num_models)
        results = []
        
        for model in models:
            try:
                result = await self.gateway.complete(
                    messages=messages,
                    model=model,
                    temperature=0.3,
                    max_tokens=1024,
                    fallback=False  # Don't fallback for consensus
                )
                parsed = self._parse_result(result["content"], result["model"])
                results.append(parsed)
            except Exception as e:
                logger.warning(f"Model {model} failed in consensus: {e}")
                continue
        
        if not results:
            raise Exception("All models failed for consensus verification")
        
        return self._aggregate_results(results)
    
    def _select_consensus_models(self, num_models: int) -> List[str]:
        """Select diverse models for consensus"""
        available = []
        
        # Prioritize diverse providers for better consensus
        if self.gateway.groq.is_available:
            available.append("groq/llama-3.1-70b-versatile")
        if self.gateway.ollama.is_available and self.gateway.ollama.available_models:
            available.append(f"ollama/{self.gateway.ollama.available_models[0]}")
        if self.gateway.openrouter.is_available:
            available.append("openrouter/google/gemma-2-9b-it:free")
        if self.gateway.deepseek.is_available:
            available.append("deepseek/deepseek-chat")
        if self.gateway.together.is_available:
            available.append("together_ai/meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo")
            
        return available[:num_models]
    
    def _parse_result(self, content: str, model: str) -> Dict[str, Any]:
        """Parse LLM response into structured result"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                data["model"] = model
                return data
        except:
            pass
        
        # Fallback parsing
        verdict = "UNVERIFIABLE"
        if "TRUE" in content.upper() and "FALSE" not in content.upper():
            verdict = "TRUE"
        elif "FALSE" in content.upper():
            verdict = "FALSE"
        elif "PARTIALLY" in content.upper():
            verdict = "PARTIALLY_TRUE"
        elif "MISLEADING" in content.upper():
            verdict = "MISLEADING"
            
        return {
            "verdict": verdict,
            "confidence": 0.5,
            "explanation": content[:500],
            "model": model,
            "key_facts": [],
            "sources_needed": [],
            "potential_biases": []
        }
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple model results into consensus"""
        if not results:
            return {"verdict": "UNVERIFIABLE", "confidence": 0.0}
        
        # Count verdicts
        verdict_counts = {}
        confidences = []
        all_facts = []
        explanations = []
        
        for result in results:
            verdict = result.get("verdict", "UNVERIFIABLE")
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            confidences.append(result.get("confidence", 0.5))
            all_facts.extend(result.get("key_facts", []))
            explanations.append(result.get("explanation", ""))
        
        # Determine consensus verdict
        consensus_verdict = max(verdict_counts, key=verdict_counts.get)
        agreement = verdict_counts[consensus_verdict] / len(results)
        
        # Calculate consensus confidence
        avg_confidence = sum(confidences) / len(confidences)
        consensus_confidence = avg_confidence * agreement
        
        return {
            "verdict": consensus_verdict,
            "confidence": round(consensus_confidence, 3),
            "agreement": round(agreement, 3),
            "models_used": [r.get("model") for r in results],
            "explanation": explanations[0] if explanations else "",
            "key_facts": list(set(all_facts))[:10],
            "individual_results": results
        }


# ============================================================
# MAIN / TESTING
# ============================================================

async def main():
    """Test the unified LLM gateway"""
    gateway = UnifiedLLMGateway()
    
    try:
        # Initialize and check providers
        available = await gateway.initialize()
        print(f"\nAvailable providers: {available}")
        
        if not available:
            print("No providers available! Please configure API keys or install Ollama.")
            return
        
        # Test completion
        print("\n--- Testing Completion ---")
        result = await gateway.complete(
            messages=[{"role": "user", "content": "What is the capital of France?"}],
            model="auto",
            prefer_free=True
        )
        print(f"Model: {result['model']}")
        print(f"Provider: {result['provider']}")
        print(f"Response: {result['content'][:200]}...")
        print(f"Usage: {result['usage']}")
        
        # Test fact checking
        print("\n--- Testing Fact Checker ---")
        checker = LLMFactChecker(gateway)
        verification = await checker.verify_claim(
            "The Eiffel Tower is located in London.",
            use_consensus=False
        )
        print(f"Verdict: {verification['verdict']}")
        print(f"Confidence: {verification['confidence']}")
        print(f"Explanation: {verification.get('explanation', '')[:200]}...")
        
        # Usage report
        print("\n--- Usage Report ---")
        report = gateway.get_usage_report()
        print(json.dumps(report, indent=2))
        
    finally:
        await gateway.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
