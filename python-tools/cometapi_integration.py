"""
Verity Systems - CometAPI Integration
Access 500+ AI models through a single OpenAI-compatible API

CometAPI provides:
- GPT-4, GPT-5.1, Claude 4.5, Gemini 3 Pro, and more
- Image generation (Flux, DALL-E, etc.)
- Video generation (Sora 2, Veo 3.1, Kling 2.5)
- Music generation (Suno API)
- Pay-as-you-go pricing with up to 20% savings

Website: https://cometapi.com
Docs: https://apidoc.cometapi.com
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger('VerityCometAPI')

# Configuration
COMETAPI_BASE_URL = os.getenv('COMETAPI_BASE_URL', 'https://api.cometapi.com/v1')
COMETAPI_API_KEY = os.getenv('COMETAPI_API_KEY', '')

# Available models on CometAPI (subset - they have 500+)
COMETAPI_MODELS = {
    # Latest LLMs
    'gpt-4': 'gpt-4',
    'gpt-4-turbo': 'gpt-4-turbo',
    'gpt-4o': 'gpt-4o',
    'gpt-4o-mini': 'gpt-4o-mini',
    'gpt-5.1': 'gpt-5.1',  # Latest GPT
    'claude-3-opus': 'claude-3-opus-20240229',
    'claude-3-sonnet': 'claude-3-sonnet-20240229',
    'claude-3-haiku': 'claude-3-haiku-20240307',
    'claude-3.5-sonnet': 'claude-3-5-sonnet-20241022',
    'claude-4.5': 'claude-4.5',  # Latest Claude
    'gemini-pro': 'gemini-pro',
    'gemini-3-pro': 'gemini-3-pro-preview-thinking',
    'llama-3-70b': 'llama-3-70b',
    'llama-3.1-405b': 'llama-3.1-405b',
    'mistral-large': 'mistral-large-latest',
    'mixtral-8x22b': 'mixtral-8x22b-instruct',
    
    # Specialized models
    'deepseek-v3': 'deepseek-chat',
    'qwen-72b': 'qwen-72b-chat',
    'yi-large': 'yi-large',
}

# Image generation models
COMETAPI_IMAGE_MODELS = {
    'dall-e-3': 'dall-e-3',
    'flux-pro': 'flux-pro',
    'flux-2': 'flux-2',
    'nano-banana-pro': 'nano-banana-pro',
    'stable-diffusion-xl': 'stable-diffusion-xl',
}


class CometAPIClient:
    """
    Client for CometAPI - unified access to 500+ AI models.
    Uses OpenAI-compatible API format.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or COMETAPI_API_KEY
        self.base_url = base_url or COMETAPI_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("CometAPI key not configured. Set COMETAPI_API_KEY environment variable.")
            logger.info("Get your free API key at: https://cometapi.com/console/")
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=120)
            )
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = 'gpt-4o',
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using any supported model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model ID (see COMETAPI_MODELS)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            **kwargs: Additional OpenAI-compatible parameters
        
        Returns:
            OpenAI-compatible response dict
        """
        if not self.is_configured:
            return {'error': 'CometAPI not configured', 'choices': []}
        
        session = await self._get_session()
        
        payload = {
            'model': COMETAPI_MODELS.get(model, model),
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': stream,
            **kwargs
        }
        
        try:
            async with session.post(
                f'{self.base_url}/chat/completions',
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"CometAPI response from {model}: {result.get('usage', {})}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"CometAPI error ({response.status}): {error_text}")
                    return {
                        'error': f'API error: {response.status}',
                        'details': error_text,
                        'choices': []
                    }
        except asyncio.TimeoutError:
            logger.error(f"CometAPI timeout for model {model}")
            return {'error': 'Request timeout', 'choices': []}
        except Exception as e:
            logger.error(f"CometAPI request failed: {e}")
            return {'error': str(e), 'choices': []}
    
    async def verify_claim(
        self,
        claim: str,
        model: str = 'gpt-4o',
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a claim using a specified AI model.
        
        Args:
            claim: The claim to verify
            model: Model to use for verification
            context: Additional context for verification
        
        Returns:
            Verification result with verdict, confidence, explanation
        """
        system_prompt = """You are an expert fact-checker. Analyze the given claim and provide:
1. VERDICT: TRUE, FALSE, MIXED, MISLEADING, or UNVERIFIED
2. CONFIDENCE: A score from 0-100
3. EXPLANATION: Brief explanation of your verdict
4. SOURCES: List any sources or reasoning used

Respond in JSON format:
{
    "verdict": "TRUE|FALSE|MIXED|MISLEADING|UNVERIFIED",
    "confidence": 85,
    "explanation": "Brief explanation...",
    "key_points": ["point1", "point2"],
    "sources_needed": ["source type needed for full verification"]
}"""
        
        user_message = f"Verify this claim: {claim}"
        if context:
            user_message += f"\n\nAdditional context: {context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=0.3,  # Lower temperature for factual tasks
            max_tokens=1000
        )
        
        if 'error' in response:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 0,
                'explanation': f"Verification failed: {response['error']}",
                'model': model,
                'provider': 'cometapi'
            }
        
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    'verdict': 'UNVERIFIED',
                    'confidence': 50,
                    'explanation': content
                }
            
            result['model'] = model
            result['provider'] = 'cometapi'
            result['usage'] = response.get('usage', {})
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse verification response: {e}")
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 0,
                'explanation': f"Parse error: {e}",
                'model': model,
                'provider': 'cometapi'
            }
    
    async def multi_model_verify(
        self,
        claim: str,
        models: List[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a claim using multiple models for consensus.
        
        Args:
            claim: The claim to verify
            models: List of models to use (defaults to diverse set)
            context: Additional context
        
        Returns:
            Combined verification result with consensus
        """
        if models is None:
            models = ['gpt-4o', 'claude-3.5-sonnet', 'gemini-pro']
        
        # Run verifications in parallel
        tasks = [
            self.verify_claim(claim, model=model, context=context)
            for model in models
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        valid_results = []
        model_results = {}
        
        for model, result in zip(models, results):
            if isinstance(result, Exception):
                model_results[model] = {
                    'verdict': 'ERROR',
                    'error': str(result)
                }
            else:
                model_results[model] = result
                if result.get('verdict') not in ['UNVERIFIED', 'ERROR']:
                    valid_results.append(result)
        
        # Calculate consensus
        if valid_results:
            verdicts = [r['verdict'] for r in valid_results]
            confidences = [r.get('confidence', 50) for r in valid_results]
            
            # Find most common verdict
            from collections import Counter
            verdict_counts = Counter(verdicts)
            consensus_verdict = verdict_counts.most_common(1)[0][0]
            
            # Calculate agreement percentage
            agreement = verdict_counts[consensus_verdict] / len(verdicts) * 100
            
            # Average confidence
            avg_confidence = sum(confidences) / len(confidences)
            
            # Adjust confidence based on agreement
            final_confidence = avg_confidence * (agreement / 100)
        else:
            consensus_verdict = 'UNVERIFIED'
            agreement = 0
            final_confidence = 0
        
        return {
            'claim': claim,
            'verdict': consensus_verdict,
            'confidence': round(final_confidence, 1),
            'agreement': round(agreement, 1),
            'models_used': models,
            'model_results': model_results,
            'provider': 'cometapi',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def generate_image(
        self,
        prompt: str,
        model: str = 'dall-e-3',
        size: str = '1024x1024',
        quality: str = 'standard',
        n: int = 1
    ) -> Dict[str, Any]:
        """
        Generate an image using CometAPI's image models.
        
        Args:
            prompt: Image description
            model: Image model to use
            size: Image size
            quality: 'standard' or 'hd'
            n: Number of images
        
        Returns:
            Response with image URLs
        """
        if not self.is_configured:
            return {'error': 'CometAPI not configured'}
        
        session = await self._get_session()
        
        payload = {
            'model': COMETAPI_IMAGE_MODELS.get(model, model),
            'prompt': prompt,
            'size': size,
            'quality': quality,
            'n': n
        }
        
        try:
            async with session.post(
                f'{self.base_url}/images/generations',
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {'error': f'API error: {response.status}', 'details': error_text}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from CometAPI."""
        if not self.is_configured:
            return []
        
        session = await self._get_session()
        
        try:
            async with session.get(f'{self.base_url}/models') as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# Convenience function for OpenAI-compatible usage
def get_openai_client(api_key: Optional[str] = None):
    """
    Get an OpenAI client configured for CometAPI.
    
    Usage:
        from cometapi_integration import get_openai_client
        
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    try:
        import openai
        
        return openai.OpenAI(
            api_key=api_key or COMETAPI_API_KEY,
            base_url=COMETAPI_BASE_URL
        )
    except ImportError:
        logger.error("OpenAI package not installed. Run: pip install openai")
        return None


# Global client instance
_client: Optional[CometAPIClient] = None


def get_cometapi_client() -> CometAPIClient:
    """Get or create the global CometAPI client."""
    global _client
    if _client is None:
        _client = CometAPIClient()
    return _client


# ============================================================
# PROVIDER WRAPPER FOR VERITY SYSTEMS
# ============================================================

class CometAPIProvider:
    """
    CometAPI provider for Verity's verification engine.
    Integrates with the existing provider system.
    """
    
    name = "cometapi"
    display_name = "CometAPI (500+ Models)"
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = CometAPIClient(api_key=api_key)
        self.available_models = list(COMETAPI_MODELS.keys())
    
    @property
    def is_available(self) -> bool:
        return self.client.is_configured
    
    async def verify(
        self,
        claim: str,
        model: str = 'gpt-4o',
        **kwargs
    ) -> Dict[str, Any]:
        """Verify a claim using CometAPI."""
        return await self.client.verify_claim(claim, model=model, **kwargs)
    
    async def verify_multi(
        self,
        claim: str,
        models: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Verify using multiple models for consensus."""
        return await self.client.multi_model_verify(claim, models=models, **kwargs)
    
    async def close(self):
        await self.client.close()


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    async def test_cometapi():
        print("\n" + "="*60)
        print("🚀 Testing CometAPI Integration")
        print("="*60 + "\n")
        
        client = CometAPIClient()
        
        if not client.is_configured:
            print("❌ CometAPI not configured!")
            print("   Set COMETAPI_API_KEY environment variable")
            print("   Get your free key at: https://cometapi.com/console/")
            return
        
        print("✅ CometAPI configured")
        
        # Test chat completion
        print("\n📝 Testing chat completion...")
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "What is 2+2? Reply briefly."}],
            model='gpt-4o-mini',
            max_tokens=50
        )
        
        if 'error' not in response:
            content = response['choices'][0]['message']['content']
            print(f"   Response: {content}")
            print(f"   Tokens: {response.get('usage', {})}")
        else:
            print(f"   Error: {response['error']}")
        
        # Test claim verification
        print("\n🔍 Testing claim verification...")
        result = await client.verify_claim(
            "The Earth is approximately 4.5 billion years old",
            model='gpt-4o'
        )
        
        print(f"   Verdict: {result.get('verdict')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Model: {result.get('model')}")
        
        # Test multi-model verification
        print("\n🔬 Testing multi-model verification...")
        multi_result = await client.multi_model_verify(
            "Water boils at 100°C at sea level",
            models=['gpt-4o-mini', 'claude-3-haiku']
        )
        
        print(f"   Consensus: {multi_result.get('verdict')}")
        print(f"   Confidence: {multi_result.get('confidence')}%")
        print(f"   Agreement: {multi_result.get('agreement')}%")
        
        await client.close()
        
        print("\n✅ CometAPI integration test complete!")
    
    asyncio.run(test_cometapi())
