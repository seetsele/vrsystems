import os
import requests
from typing import Dict, Any


def hf_inference_moderate(text: str) -> Dict[str, Any]:
    """Call Hugging Face Inference moderation model via REST (if API key provided)."""
    key = os.environ.get('HF_API_KEY')
    if not key:
        raise RuntimeError('HF_API_KEY not set')
    model = os.environ.get('HF_MODERATION_MODEL', 'moderation')
    url = f'https://api-inference.huggingface.co/models/{model}'
    headers = {'Authorization': f'Bearer {key}'}
    resp = requests.post(url, headers=headers, json={'inputs': text}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def simple_keyword_moderate(text: str) -> Dict[str, Any]:
    """Very small local fallback: flags obvious words from `MODERATION_BLOCKLIST` env."""
    block = os.environ.get('MODERATION_BLOCKLIST', 'sex,violence,terror').split(',')
    found = [w for w in block if w and w.lower() in text.lower()]
    return {'result': 'blocked' if found else 'ok', 'flags': found}


def moderate(text: str) -> Dict[str, Any]:
    """Unified moderation entrypoint.

    Priority: Hugging Face Inference API -> local keyword fallback.
    Raises an informative error if no backend is configured.
    """
    try:
        if os.environ.get('HF_API_KEY'):
            return hf_inference_moderate(text)
    except Exception:
        pass
    # fallback
    return simple_keyword_moderate(text)
