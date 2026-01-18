import os
from typing import Optional


def hf_text_generate(prompt: str, max_new_tokens: int = 256) -> str:
    """Call Hugging Face text-generation endpoint if `HF_API_KEY` is set."""
    import requests
    key = os.environ.get('HF_API_KEY')
    if not key:
        raise RuntimeError('HF_API_KEY not set')
    model = os.environ.get('HF_LLM_MODEL', 'gpt2')
    url = f'https://api-inference.huggingface.co/models/{model}'
    headers = {'Authorization': f'Bearer {key}'}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    out = resp.json()
    if isinstance(out, list) and out:
        return out[0].get('generated_text', '')
    return str(out)


def gpt4all_local(prompt: str, model_path: Optional[str] = None) -> str:
    """Try to use local `gpt4all` if installed: lightweight local LLM option."""
    try:
        from gpt4all import GPT4All
    except Exception as e:
        raise RuntimeError('gpt4all not installed') from e
    model_path = model_path or os.environ.get('GPT4ALL_MODEL')
    g = GPT4All(model_path) if model_path else GPT4All()
    return g.generate(prompt)


def generate(prompt: str, max_new_tokens: int = 256) -> str:
    """Unified LLM entrypoint.

    Priority: local gpt4all -> Hugging Face Inference API
    """
    try:
        return gpt4all_local(prompt)
    except Exception:
        pass
    return hf_text_generate(prompt, max_new_tokens=max_new_tokens)
