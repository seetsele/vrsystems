"""Complete-ish AI models registry

This file implements provider wrappers that use real SDKs when available
and fall back to a simple dummy provider when SDKs are missing. It uses
the `BaseAIProvider` and `VerificationResult` from `providers.base_provider`.
"""
from __future__ import annotations
import os
import time
import asyncio
from typing import Optional, Dict, Any, List

from providers.base_provider import BaseAIProvider, VerificationResult

# By default enable real provider SDKs. To force dummy-only mode, set
# `USE_REAL_PROVIDERS=0` or `USE_REAL_PROVIDERS=false` in the environment.
USE_REAL_PROVIDERS = not (os.getenv('USE_REAL_PROVIDERS', '1') in ('0', 'false', 'False'))


class DummyProvider(BaseAIProvider):
    """Fallback provider used when SDK is not installed or not configured."""

    def __init__(self, name: str, api_key: Optional[str] = None):
        super().__init__(name, api_key=api_key)

    async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        # Accept optional sources passed by orchestrator
        sources = kwargs.get("sources") or kwargs.get("source_urls") or []

        # Very simple heuristic: if claim contains numbers or known keywords mark as UNVERIFIABLE
        verdict = "UNVERIFIABLE"
        confidence = 40
        reasoning = "Fallback provider — real SDK not available or not configured."
        # quick check for obvious true claims (demo only)
        lower = claim.lower()
        if any(x in lower for x in ["water boils", "2+2=4", "pi is"]):
            verdict = "TRUE"
            confidence = 95
            reasoning = "Simple rule-based heuristic matched a well-known fact."
        # Append sources info to reasoning for transparency
        if sources:
            src_text = ", ".join(sources[:5])
            reasoning = f"{reasoning} Sources: {src_text}"

        return VerificationResult(
            provider=self.name,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            cost=0.0,
            response_time=time.time() - start,
            raw_response=None,
            sources=sources,
        )


# Helper factory to create provider classes that gracefully degrade
def _make_openai_provider_class() -> Any:
    try:
        import openai
        ENABLE_OPENAI = os.getenv('ENABLE_OPENAI', '1') not in ('0', 'false', 'False')
        OPENAI_KEY = os.getenv('OPENAI_API_KEY')
        if not ENABLE_OPENAI or not OPENAI_KEY:
            raise Exception('OpenAI disabled or API key missing')

        class OpenAIProvider(BaseAIProvider):
            def __init__(self, api_key: Optional[str] = None):
                super().__init__("openai", api_key=api_key or os.getenv("OPENAI_API_KEY"))
                # Use openai ChatCompletion sync client for portability
                openai.api_key = self.api_key

            async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
                start = time.time()
                prompt = (
                    "You are a fact-checking expert. Respond EXACTLY in this format:\n"
                    "VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE]\n"
                    "CONFIDENCE: [0-100]\n"
                    "REASONING: [brief explanation]\n\n"
                    f"Claim: {claim}\n"
                )
                # call in thread to avoid blocking event loop
                def _call():
                    resp = openai.ChatCompletion.create(
                        model=kwargs.get("model", "gpt-3.5-turbo"),
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                        max_tokens=512,
                    )
                    return resp

                resp = await asyncio.to_thread(_call)
                text = ""
                try:
                    text = resp.choices[0].message.content if hasattr(resp.choices[0], "message") else resp.choices[0].text
                except Exception:
                    text = str(resp)

                parsed = self._parse_response(text)
                # best-effort usage/cost extraction
                cost = 0.0
                return VerificationResult(
                    provider=self.name,
                    verdict=parsed.get("verdict", "UNVERIFIABLE"),
                    confidence=parsed.get("confidence", 0),
                    reasoning=parsed.get("reasoning", text),
                    cost=cost,
                    response_time=time.time() - start,
                    raw_response=text,
                )

        return OpenAIProvider
    except Exception:
        return lambda api_key=None: DummyProvider("openai_dummy", api_key=api_key)


def _make_anthropic_provider_class() -> Any:
    try:
        import anthropic
        ENABLE_ANTHROPIC = os.getenv('ENABLE_ANTHROPIC', '1') not in ('0', 'false', 'False')
        ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
        if not ENABLE_ANTHROPIC or not ANTHROPIC_KEY:
            raise Exception('Anthropic disabled or API key missing')

        class AnthropicProvider(BaseAIProvider):
            def __init__(self, api_key: Optional[str] = None):
                super().__init__("anthropic", api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
                self.client = anthropic.Client(api_key=self.api_key)

            async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
                start = time.time()
                prompt = (
                    "VERDICT: \nCONFIDENCE: \nREASONING: \n\n" + claim
                )

                def _call():
                    return self.client.completions.create(model=kwargs.get("model", "claude-2.1"), prompt=prompt, max_tokens=512)

                resp = await asyncio.to_thread(_call)
                text = getattr(resp, "completion", str(resp))
                parsed = self._parse_response(text)
                return VerificationResult(
                    provider=self.name,
                    verdict=parsed.get("verdict", "UNVERIFIABLE"),
                    confidence=parsed.get("confidence", 0),
                    reasoning=parsed.get("reasoning", text),
                    cost=0.0,
                    response_time=time.time() - start,
                    raw_response=text,
                )

        return AnthropicProvider
    except Exception:
        return lambda api_key=None: DummyProvider("anthropic_dummy", api_key=api_key)


def _make_ollama_provider_class() -> Any:
    # Ollama typically runs locally; we implement a small HTTP client
    import json
    try:
        import aiohttp

        class OllamaProvider(BaseAIProvider):
            def __init__(self, model_name: str, api_key: Optional[str] = None):
                super().__init__(f"ollama_{model_name.replace(':', '_')}", api_key=api_key)
                self.model_name = model_name
                self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

            async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
                start = time.time()
                prompt = (
                    "VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE]\n"
                    "CONFIDENCE: [0-100]\n"
                    "REASONING: [brief explanation]\n"
                    f"CLAIM: {claim}"
                )
                url = f"{self.base_url}/api/generate"
                async with aiohttp.ClientSession() as session:
                    payload = {"model": self.model_name, "prompt": prompt, "stream": False}
                    async with session.post(url, json=payload, timeout=60) as resp:
                        data = await resp.json()
                text = data.get("response") or data.get("output") or str(data)
                parsed = self._parse_response(text)
                return VerificationResult(
                    provider=self.name,
                    verdict=parsed.get("verdict", "UNVERIFIABLE"),
                    confidence=parsed.get("confidence", 0),
                    reasoning=parsed.get("reasoning", text),
                    cost=0.0,
                    response_time=time.time() - start,
                    raw_response=text,
                )

        return OllamaProvider
    except Exception:
        return lambda model_name, api_key=None: DummyProvider(f"ollama_{model_name}", api_key=api_key)


def _make_hf_provider_class() -> Any:
    try:
        from huggingface_hub import InferenceClient
        ENABLE_HF = os.getenv('ENABLE_HF', '1') not in ('0', 'false', 'False')
        HF_KEY = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_API_KEY')
        if not ENABLE_HF or not HF_KEY:
            raise Exception('Hugging Face disabled or API key missing')

        class HFProvider(BaseAIProvider):
            def __init__(self, model_name: str, api_key: Optional[str] = None):
                super().__init__(f"hf_{model_name.split('/')[-1]}", api_key=api_key or os.getenv("HF_TOKEN"))
                self.model_name = model_name
                self.client = InferenceClient(token=self.api_key)

            async def verify_claim(self, claim: str, **kwargs) -> VerificationResult:
                start = time.time()
                prompt = "VERDICT:\nCONFIDENCE:\nREASONING:\n\n" + claim

                def _call():
                    return self.client.text_generation(model=self.model_name, inputs=prompt, max_new_tokens=512)

                resp = await asyncio.to_thread(_call)
                text = resp[0]["generated_text"] if isinstance(resp, list) and resp else str(resp)
                parsed = self._parse_response(text)
                return VerificationResult(
                    provider=self.name,
                    verdict=parsed.get("verdict", "UNVERIFIABLE"),
                    confidence=parsed.get("confidence", 0),
                    reasoning=parsed.get("reasoning", text),
                    cost=0.0,
                    response_time=time.time() - start,
                    raw_response=text,
                )

        return HFProvider
    except Exception:
        return lambda model_name, api_key=None: DummyProvider(f"hf_{model_name}", api_key=api_key)


# Helper to create a dummy factory that preserves provider name
def _dummy_factory(name: str):
    return lambda api_key=None, **kwargs: DummyProvider(name, api_key=api_key)


# Build provider classes (or fallbacks)
if USE_REAL_PROVIDERS:
    OpenAIProvider = _make_openai_provider_class()
    AnthropicProvider = _make_anthropic_provider_class()
    OllamaProvider = _make_ollama_provider_class()
    HFProvider = _make_hf_provider_class()
else:
    # Use dummy fallbacks to keep local runs fast/safe
    OpenAIProvider = lambda api_key=None: DummyProvider("openai_dummy", api_key=api_key)
    AnthropicProvider = lambda api_key=None: DummyProvider("anthropic_dummy", api_key=api_key)
    OllamaProvider = lambda model_name, api_key=None: DummyProvider(f"ollama_{model_name}", api_key=api_key)
    HFProvider = lambda model_name, api_key=None: DummyProvider(f"hf_{model_name}", api_key=api_key)


# Register many model keys — most map to either a concrete class or a Dummy fallback
ALL_AI_MODELS: Dict[str, Any] = {
    # OpenAI
    "openai_gpt4o": OpenAIProvider,
    "openai_gpt4o_mini": OpenAIProvider,
    "openai_gpt35_turbo": OpenAIProvider,

    # Anthropic
    "anthropic_claude_opus_4": AnthropicProvider,
    "anthropic_claude_sonnet_4": AnthropicProvider,
    "anthropic_claude_haiku_4": AnthropicProvider,

    # Google / HF (map to HFProvider where appropriate)
    "google_gemini_pro": HFProvider,
    "google_gemini_flash": HFProvider,

    # Groq (map to dummy or hf)
    "groq_llama33_70b": _dummy_factory("groq_llama33_70b"),
    "groq_llama31_8b": _dummy_factory("groq_llama31_8b"),
    "groq_mixtral_8x7b": _dummy_factory("groq_mixtral_8x7b"),
    "groq_gemma2_9b": _dummy_factory("groq_gemma2_9b"),
    "groq_deepseek_r1": _dummy_factory("groq_deepseek_r1"),

    # Ollama (local models)
    "ollama_llama33_70b": lambda api_key=None: OllamaProvider("llama3.3:70b", api_key=api_key),
    "ollama_llama33_8b": lambda api_key=None: OllamaProvider("llama3.3:8b", api_key=api_key),
    "ollama_llama31_405b": lambda api_key=None: OllamaProvider("llama3.1:405b", api_key=api_key),
    "ollama_llama31_70b": lambda api_key=None: OllamaProvider("llama3.1:70b", api_key=api_key),
    "ollama_llama31_8b": lambda api_key=None: OllamaProvider("llama3.1:8b", api_key=api_key),

    # Together / Cohere / Perplexity
    "together_llama3_70b": _dummy_factory("together_llama3_70b"),
    "together_mixtral_8x22b": _dummy_factory("together_mixtral_8x22b"),
    "together_qwen2_72b": _dummy_factory("together_qwen2_72b"),

    "cohere_command_r_plus": _dummy_factory("cohere_command_r_plus"),
    "cohere_command": _dummy_factory("cohere_command"),

    "perplexity_sonar": _dummy_factory("perplexity_sonar"),

    # Hugging Face examples
    "hf_llama31_405b": lambda api_key=None: HFProvider("meta-llama/Meta-Llama-3.1-405B-Instruct"),
    "hf_mixtral_8x22b": lambda api_key=None: HFProvider("mistralai/Mixtral-8x22B-Instruct-v0.1"),
    "hf_qwen25_72b": lambda api_key=None: HFProvider("Qwen/Qwen2.5-72B-Instruct"),
    "hf_command_r_plus": lambda api_key=None: HFProvider("CohereForAI/c4ai-command-r-plus"),
    "hf_phi3_medium": lambda api_key=None: HFProvider("microsoft/Phi-3-medium-128k-instruct"),
}


def create_provider(name: str, api_key: Optional[str] = None, **kwargs) -> BaseAIProvider:
    """Factory to create a provider instance from `ALL_AI_MODELS` registry.

    - If the registry value is a class, instantiate it with `api_key` or other kwargs.
    - If it's a callable factory, call it.
    - Otherwise, return a DummyProvider.
    """
    # If test/CI requests provider mocks, return deterministic mock provider
    if os.getenv('USE_PROVIDER_MOCKS', '0') in ('1', 'true', 'True'):
        try:
            from providers.mock_providers import MockProvider

            return MockProvider(name)
        except Exception:
            pass

    entry = ALL_AI_MODELS.get(name)
    if entry is None:
        return DummyProvider(name, api_key=api_key)

    # Try a few common constructor/factory signatures robustly
    try:
        # If it's a class type, attempt various common constructor shapes
        if isinstance(entry, type):
            # 1) try keyword api_key
            try:
                return entry(api_key=api_key, **kwargs)
            except TypeError:
                pass

            # 2) try single positional api_key
            try:
                return entry(api_key)
            except TypeError:
                pass

            # 3) try no-arg constructor
            try:
                return entry()
            except Exception:
                return DummyProvider(name, api_key=api_key)

        # If it's a callable factory (lambda or function), try common call shapes
        if callable(entry):
            for attempt_args in (
                (api_key,),
                (name,),
                (),
            ):
                try:
                    return entry(*attempt_args, **kwargs)
                except TypeError:
                    continue
                except Exception:
                    continue

        # As a last resort, return a dummy provider
        return DummyProvider(name, api_key=api_key)
    except Exception:
        return DummyProvider(name, api_key=api_key)


if __name__ == "__main__":
    # quick smoke test
    prov = create_provider("openai_gpt35_turbo")
    import asyncio

    async def _run():
        res = await prov.verify_claim("Water boils at 100 degrees Celsius at sea level")
        print(res)

    asyncio.run(_run())
"""Adapter registry exposing ALL_AI_MODELS mapping model keys to adapter classes.

Each adapter exposes an async `verify_claim_with_retry(claim)` returning a
`providers.base_provider.VerificationResult` instance. Adapters wrap existing
sync provider implementations and normalize their outputs.
"""
import asyncio
import time
from typing import Dict

from providers.base_provider import VerificationResult

# Import available provider implementations
from providers.ollama_provider import OllamaProvider
from providers.groq_provider import GroqProvider
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.perplexity_provider import PerplexityProvider
try:
    from providers.cohere_provider import CohereProvider
except Exception:
    CohereProvider = None
from providers.together_provider import TogetherProvider
from providers.google_provider import GoogleProvider


class BaseAdapter:
    def _to_result(self, raw, elapsed: float) -> VerificationResult:
        """Normalize either a dict-like raw response or an existing VerificationResult.

        If `raw` is already a `VerificationResult`, update its response_time and return it.
        Otherwise treat it as a dict and construct a `VerificationResult`.
        """
        # Accept already-normalized results
        if isinstance(raw, VerificationResult):
            raw.response_time = elapsed
            # normalize fields
            raw.verdict = (raw.verdict or 'UNVERIFIABLE').upper()
            raw.confidence = float(getattr(raw, 'confidence', 0) or 0)
            raw.cost = float(getattr(raw, 'cost', 0.0) or 0.0)
            return raw

        # Try to treat raw as a mapping or object; be permissive about shapes
        provider = 'unknown'
        verdict = 'UNVERIFIABLE'
        confidence = 0.0
        reasoning = ''
        cost = 0.0
        raw_response = None

        try:
            if isinstance(raw, dict):
                provider = raw.get('provider', raw.get('name', 'unknown'))
                verdict = (raw.get('verdict') or 'UNVERIFIABLE').upper()
                confidence = float(raw.get('confidence', 0) or 0)
                reasoning = str(raw.get('reasoning', raw.get('reason', '')))
                cost = float(raw.get('cost', 0.0) or 0.0)
                raw_response = raw.get('raw_response') or raw.get('response') or raw.get('output') or raw.get('results') or None
            else:
                provider = getattr(raw, 'provider', getattr(raw, 'name', 'unknown'))
                verdict = (getattr(raw, 'verdict', 'UNVERIFIABLE') or 'UNVERIFIABLE').upper()
                confidence = float(getattr(raw, 'confidence', 0) or 0)
                reasoning = str(getattr(raw, 'reasoning', getattr(raw, 'reason', '')))
                cost = float(getattr(raw, 'cost', 0.0) or 0.0)
                raw_response = getattr(raw, 'raw_response', None) or getattr(raw, 'response', None)
        except Exception:
            # best-effort fallback
            try:
                provider = str(raw)
            except Exception:
                provider = 'unknown'

        # Clamp/normalize values
        try:
            confidence = max(0.0, min(100.0, float(confidence)))
        except Exception:
            confidence = 0.0

        try:
            cost = float(cost or 0.0)
        except Exception:
            cost = 0.0

        return VerificationResult(
            provider=str(provider),
            verdict=str(verdict),
            confidence=confidence,
            reasoning=str(reasoning),
            cost=cost,
            response_time=elapsed,
            raw_response=raw_response,
        )


class OllamaLlama33Adapter(BaseAdapter):
    def __init__(self):
        self.provider = OllamaProvider()
        self.model = "llama3.3:70b"

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class OllamaQwen25Adapter(BaseAdapter):
    def __init__(self):
        self.provider = OllamaProvider()
        self.model = "qwen25:72b"

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class GroqLlama33Adapter(BaseAdapter):
    def __init__(self):
        self.provider = GroqProvider()
        self.model = "llama-3.3-70b-versatile"

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class GroqDefaultAdapter(BaseAdapter):
    def __init__(self):
        self.provider = GroqProvider()

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider='groq', verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class OpenAIAdapter(BaseAdapter):
    def __init__(self, model: str = "gpt-4o"):
        self.provider = OpenAIProvider()
        self.model = model

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class AnthropicAdapter(BaseAdapter):
    def __init__(self, model: str = "claude-opus-4-20250514"):
        self.provider = AnthropicProvider()
        self.model = model

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class PerplexityAdapter(BaseAdapter):
    def __init__(self):
        self.provider = PerplexityProvider()

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider='perplexity', verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class CohereAdapter(BaseAdapter):
    def __init__(self, model: str = "command-r"):
        self.provider = CohereProvider()
        self.model = model

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            # Cohere provider may accept (claim, model, **kwargs) or (claim, **kwargs)
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    try:
                        return self.provider.verify_claim(claim, **kwargs)
                    except TypeError:
                        return self.provider.verify_claim(claim)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class TogetherAdapter(BaseAdapter):
    def __init__(self, model: str = "meta-llama/Llama-3-70b-chat-hf"):
        self.provider = TogetherProvider()
        self.model = model

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            def _call():
                try:
                    return self.provider.verify_claim(claim, self.model, **kwargs)
                except TypeError:
                    return self.provider.verify_claim(claim, **kwargs)

            raw = await asyncio.to_thread(_call)
            return self._to_result(raw, time.time() - start)
        except Exception as e:
            return VerificationResult(provider=self.model, verdict="ERROR", confidence=0.0, reasoning=str(e), cost=0.0, response_time=time.time()-start, raw_response=None)


class GoogleAdapter(BaseAdapter):
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        self.provider = GoogleProvider()
        self.model = model

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        def _call():
            try:
                return self.provider.verify_claim(claim, self.model, **kwargs)
            except TypeError:
                return self.provider.verify_claim(claim, **kwargs)

        raw = await asyncio.to_thread(_call)
        return self._to_result(raw, time.time() - start)


class DummyAdapter(BaseAdapter):
    def __init__(self, name: str = "dummy"):
        self.name = name

    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        await asyncio.sleep(0.01)
        return VerificationResult(
            provider=self.name,
            verdict='UNVERIFIABLE',
            confidence=50.0,
            reasoning='Fallback dummy provider - no model available locally',
            cost=0.0,
            response_time=0.01,
            raw_response=None
        )


# ============================================================
# SPECIALIZED DOMAIN MODEL ADAPTERS
# ============================================================
# Import specialized models with fallback
try:
    from providers.ai_models.specialized_models import (
        BioGPTProvider, PubMedBERTProvider, BioBERTProvider, NutritionBERTProvider,
        LegalBERTProvider, CaseLawBERTProvider, FinBERTProvider, FinGPTProvider, EconBERTProvider,
        SciBERTProvider, GalacticaProvider, ClimateBERTProvider, PoliBERTProvider, VoteBERTProvider,
        SportsBERTProvider, GeoBERTProvider, HistoryBERTProvider, TechBERTProvider, SecurityBERTProvider
    )
    SPECIALIZED_MODELS_AVAILABLE = True
except ImportError:
    SPECIALIZED_MODELS_AVAILABLE = False


class SpecializedModelAdapter(BaseAdapter):
    """Base adapter for specialized domain models"""
    
    def __init__(self, model_class, model_name: str):
        self.model_name = model_name
        self._model = None
        self._model_class = model_class
    
    def _get_model(self):
        if self._model is None:
            self._model = self._model_class()
        return self._model
    
    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            model = self._get_model()
            result = await model.verify_claim(claim, **kwargs)
            return self._to_result(result, time.time() - start)
        except Exception as e:
            return VerificationResult(
                provider=self.model_name,
                verdict="ERROR",
                confidence=0.0,
                reasoning=f"Specialized model error: {str(e)}",
                cost=0.0,
                response_time=time.time() - start,
                raw_response=None
            )


# Create specialized model adapters
if SPECIALIZED_MODELS_AVAILABLE:
    class BioGPTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(BioGPTProvider, "biogpt")
    
    class PubMedBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(PubMedBERTProvider, "pubmedbert")
    
    class BioBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(BioBERTProvider, "biobert")
    
    class NutritionBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(NutritionBERTProvider, "nutritionbert")
    
    class LegalBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(LegalBERTProvider, "legalbert")
    
    class CaseLawBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(CaseLawBERTProvider, "caselawbert")
    
    class FinBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(FinBERTProvider, "finbert")
    
    class FinGPTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(FinGPTProvider, "fingpt")
    
    class EconBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(EconBERTProvider, "econbert")
    
    class SciBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(SciBERTProvider, "scibert")
    
    class GalacticaAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(GalacticaProvider, "galactica")
    
    class ClimateBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(ClimateBERTProvider, "climatebert")
    
    class PoliBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(PoliBERTProvider, "polibert")
    
    class VoteBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(VoteBERTProvider, "votebert")
    
    class SportsBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(SportsBERTProvider, "sportsbert")
    
    class GeoBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(GeoBERTProvider, "geobert")
    
    class HistoryBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(HistoryBERTProvider, "historybert")
    
    class TechBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(TechBERTProvider, "techbert")
    
    class SecurityBERTAdapter(SpecializedModelAdapter):
        def __init__(self):
            super().__init__(SecurityBERTProvider, "securitybert")
else:
    # Fallback adapters when specialized models not available
    BioGPTAdapter = lambda: DummyAdapter("biogpt")
    PubMedBERTAdapter = lambda: DummyAdapter("pubmedbert")
    BioBERTAdapter = lambda: DummyAdapter("biobert")
    NutritionBERTAdapter = lambda: DummyAdapter("nutritionbert")
    LegalBERTAdapter = lambda: DummyAdapter("legalbert")
    CaseLawBERTAdapter = lambda: DummyAdapter("caselawbert")
    FinBERTAdapter = lambda: DummyAdapter("finbert")
    FinGPTAdapter = lambda: DummyAdapter("fingpt")
    EconBERTAdapter = lambda: DummyAdapter("econbert")
    SciBERTAdapter = lambda: DummyAdapter("scibert")
    GalacticaAdapter = lambda: DummyAdapter("galactica")
    ClimateBERTAdapter = lambda: DummyAdapter("climatebert")
    PoliBERTAdapter = lambda: DummyAdapter("polibert")
    VoteBERTAdapter = lambda: DummyAdapter("votebert")
    SportsBERTAdapter = lambda: DummyAdapter("sportsbert")
    GeoBERTAdapter = lambda: DummyAdapter("geobert")
    HistoryBERTAdapter = lambda: DummyAdapter("historybert")
    TechBERTAdapter = lambda: DummyAdapter("techbert")
    SecurityBERTAdapter = lambda: DummyAdapter("securitybert")


# ============================================================
# FREE PROVIDER ADAPTERS
# ============================================================
# Import free providers with fallback
try:
    from python_tools.free_provider_config import FreeProviderManager, FREE_PROVIDERS
    FREE_PROVIDERS_AVAILABLE = True
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python-tools"))
        from free_provider_config import FreeProviderManager, FREE_PROVIDERS
        FREE_PROVIDERS_AVAILABLE = True
    except ImportError:
        FREE_PROVIDERS_AVAILABLE = False
        FREE_PROVIDERS = {}


class FreeProviderAdapter(BaseAdapter):
    """Adapter that uses all free providers for comprehensive search"""
    
    def __init__(self):
        self._manager = None
    
    def _get_manager(self):
        if self._manager is None and FREE_PROVIDERS_AVAILABLE:
            self._manager = FreeProviderManager()
        return self._manager
    
    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            manager = self._get_manager()
            if not manager:
                return VerificationResult(
                    provider="free_providers",
                    verdict="ERROR",
                    confidence=0.0,
                    reasoning="Free providers not available",
                    cost=0.0,
                    response_time=time.time() - start,
                    raw_response=None
                )
            
            result = await manager.verify_claim(claim)
            return self._to_result(result, time.time() - start)
        except Exception as e:
            return VerificationResult(
                provider="free_providers",
                verdict="ERROR",
                confidence=0.0,
                reasoning=f"Free provider error: {str(e)}",
                cost=0.0,
                response_time=time.time() - start,
                raw_response=None
            )


class WikipediaAdapter(BaseAdapter):
    """Adapter for Wikipedia search"""
    
    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": claim,
                    "format": "json",
                    "utf8": 1,
                    "srlimit": 5
                }
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    results = data.get("query", {}).get("search", [])
                    
                    if results:
                        return VerificationResult(
                            provider="wikipedia",
                            verdict="NEEDS_REVIEW",
                            confidence=60.0,
                            reasoning=f"Found {len(results)} Wikipedia articles. Top: {results[0].get('title', 'Unknown')}",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=results
                        )
                    else:
                        return VerificationResult(
                            provider="wikipedia",
                            verdict="UNVERIFIABLE",
                            confidence=30.0,
                            reasoning="No Wikipedia articles found for this claim",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=None
                        )
        except Exception as e:
            return VerificationResult(
                provider="wikipedia",
                verdict="ERROR",
                confidence=0.0,
                reasoning=str(e),
                cost=0.0,
                response_time=time.time() - start,
                raw_response=None
            )


class ArXivAdapter(BaseAdapter):
    """Adapter for arXiv scientific papers"""
    
    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "http://export.arxiv.org/api/query"
                params = {"search_query": f"all:{claim}", "max_results": 5}
                async with session.get(url, params=params) as resp:
                    text = await resp.text()
                    # Count entries in XML response
                    entry_count = text.count("<entry>")
                    
                    if entry_count > 0:
                        return VerificationResult(
                            provider="arxiv",
                            verdict="NEEDS_REVIEW",
                            confidence=65.0,
                            reasoning=f"Found {entry_count} scientific papers on arXiv related to this claim",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=text[:1000]
                        )
                    else:
                        return VerificationResult(
                            provider="arxiv",
                            verdict="UNVERIFIABLE",
                            confidence=30.0,
                            reasoning="No arXiv papers found for this claim",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=None
                        )
        except Exception as e:
            return VerificationResult(
                provider="arxiv",
                verdict="ERROR",
                confidence=0.0,
                reasoning=str(e),
                cost=0.0,
                response_time=time.time() - start,
                raw_response=None
            )


class PubMedAdapter(BaseAdapter):
    """Adapter for PubMed medical literature"""
    
    async def verify_claim_with_retry(self, claim: str, **kwargs) -> VerificationResult:
        start = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                params = {"db": "pubmed", "term": claim, "retmode": "json", "retmax": 5}
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    id_list = data.get("esearchresult", {}).get("idlist", [])
                    
                    if id_list:
                        return VerificationResult(
                            provider="pubmed",
                            verdict="NEEDS_REVIEW",
                            confidence=70.0,
                            reasoning=f"Found {len(id_list)} PubMed articles. IDs: {', '.join(id_list[:3])}",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=id_list
                        )
                    else:
                        return VerificationResult(
                            provider="pubmed",
                            verdict="UNVERIFIABLE",
                            confidence=30.0,
                            reasoning="No PubMed articles found for this claim",
                            cost=0.0,
                            response_time=time.time() - start,
                            raw_response=None
                        )
        except Exception as e:
            return VerificationResult(
                provider="pubmed",
                verdict="ERROR",
                confidence=0.0,
                reasoning=str(e),
                cost=0.0,
                response_time=time.time() - start,
                raw_response=None
            )


# Registry mapping keys used by the orchestrator to adapter classes
ALL_AI_MODELS: Dict[str, type] = {
    # ============================================================
    # COMMERCIAL AI PROVIDERS
    # ============================================================
    # Ollama variants (local)
    "ollama_llama33_70b": OllamaLlama33Adapter,
    "ollama_qwen25_72b": OllamaQwen25Adapter,
    "ollama_mistral_large": DummyAdapter,

    # Groq variants (fast inference)
    "groq_llama33_70b": GroqLlama33Adapter,
    "groq_mixtral_8x7b": GroqDefaultAdapter,
    "groq_deepseek_r1": GroqDefaultAdapter,

    # OpenAI
    "openai_gpt4o": lambda: OpenAIAdapter("gpt-4o"),
    "openai_gpt4o_mini": lambda: OpenAIAdapter("gpt-4o-mini"),
    "openai_gpt35_turbo": lambda: OpenAIAdapter("gpt-3.5-turbo"),
    "openai_o1": lambda: OpenAIAdapter("o1"),
    "openai_o1_mini": lambda: OpenAIAdapter("o1-mini"),

    # Anthropic
    "anthropic_claude_opus_4": lambda: AnthropicAdapter("claude-opus-4-20250514"),
    "anthropic_claude_sonnet_4": lambda: AnthropicAdapter("claude-sonnet-4-20250514"),
    "anthropic_claude_haiku": lambda: AnthropicAdapter("claude-3-5-haiku-20241022"),

    # Perplexity
    "perplexity_sonar": PerplexityAdapter,
    "perplexity_sonar_pro": PerplexityAdapter,

    # Cohere
    "cohere_command_r_plus": CohereAdapter,
    "cohere_command": CohereAdapter,
    "cohere_command_r": lambda: CohereAdapter("command-r"),

    # Together AI
    "together_llama3_70b": TogetherAdapter,
    "together_default": TogetherAdapter,
    "together_mixtral": lambda: TogetherAdapter("mistralai/Mixtral-8x22B-Instruct-v0.1"),

    # Google
    "google_gemini_pro": lambda: GoogleAdapter("gemini-1.5-pro"),
    "google_gemini_flash": lambda: GoogleAdapter("gemini-2.0-flash-exp"),
    "google_gemini_ultra": lambda: GoogleAdapter("gemini-ultra"),

    # ============================================================
    # SPECIALIZED DOMAIN MODELS (18 models)
    # ============================================================
    # Medical & Healthcare
    "biogpt": BioGPTAdapter,
    "pubmedbert": PubMedBERTAdapter,
    "biobert": BioBERTAdapter,
    "nutritionbert": NutritionBERTAdapter,

    # Legal
    "legalbert": LegalBERTAdapter,
    "caselawbert": CaseLawBERTAdapter,

    # Financial
    "finbert": FinBERTAdapter,
    "fingpt": FinGPTAdapter,
    "econbert": EconBERTAdapter,

    # Scientific
    "scibert": SciBERTAdapter,
    "galactica": GalacticaAdapter,
    "climatebert": ClimateBERTAdapter,

    # Political & Social
    "polibert": PoliBERTAdapter,
    "votebert": VoteBERTAdapter,
    "sportsbert": SportsBERTAdapter,

    # Other Specialized
    "geobert": GeoBERTAdapter,
    "historybert": HistoryBERTAdapter,
    "techbert": TechBERTAdapter,
    "securitybert": SecurityBERTAdapter,

    # ============================================================
    # FREE DATA PROVIDERS (no API key required)
    # ============================================================
    "free_providers": FreeProviderAdapter,
    "wikipedia": WikipediaAdapter,
    "arxiv": ArXivAdapter,
    "pubmed": PubMedAdapter,
}


# ============================================================
# DOMAIN-TO-MODEL MAPPING
# ============================================================
DOMAIN_MODEL_MAPPING = {
    "medical": ["biogpt", "pubmedbert", "biobert", "nutritionbert", "pubmed"],
    "legal": ["legalbert", "caselawbert"],
    "financial": ["finbert", "fingpt", "econbert"],
    "scientific": ["scibert", "galactica", "arxiv"],
    "climate": ["climatebert"],
    "political": ["polibert", "votebert"],
    "sports": ["sportsbert"],
    "geography": ["geobert", "wikipedia"],
    "history": ["historybert", "wikipedia"],
    "technology": ["techbert", "securitybert"],
    "general": ["wikipedia", "free_providers"],
}


def get_models_for_domain(domain: str) -> list:
    """Get recommended models for a specific domain"""
    return DOMAIN_MODEL_MAPPING.get(domain.lower(), ["free_providers", "wikipedia"])


def get_all_model_names() -> list:
    """Get all available model names"""
    return list(ALL_AI_MODELS.keys())


def get_specialized_model_names() -> list:
    """Get only specialized domain model names"""
    specialized = [
        "biogpt", "pubmedbert", "biobert", "nutritionbert",
        "legalbert", "caselawbert", "finbert", "fingpt", "econbert",
        "scibert", "galactica", "climatebert", "polibert", "votebert",
        "sportsbert", "geobert", "historybert", "techbert", "securitybert"
    ]
    return [m for m in specialized if m in ALL_AI_MODELS]


def get_commercial_model_names() -> list:
    """Get commercial AI provider model names"""
    commercial_prefixes = ["openai", "anthropic", "groq", "ollama", "cohere", "together", "google", "perplexity"]
    return [name for name in ALL_AI_MODELS.keys() if any(name.startswith(p) for p in commercial_prefixes)]


def get_free_model_names() -> list:
    """Get free provider model names (no API key needed)"""
    return ["free_providers", "wikipedia", "arxiv", "pubmed"]
