import os
from typing import Sequence


def sentence_transformers_embed(texts: Sequence[str]):
    """Try to embed using `sentence-transformers` locally (if installed)."""
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError('sentence-transformers not installed') from e
    model_name = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    model = SentenceTransformer(model_name)
    return model.encode(list(texts)).tolist()


def hf_embeddings_api(texts: Sequence[str]):
    import requests
    key = os.environ.get('HF_API_KEY')
    if not key:
        raise RuntimeError('HF_API_KEY not set')
    model = os.environ.get('HF_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    url = f'https://api-inference.huggingface.co/embeddings/{model}'
    headers = {'Authorization': f'Bearer {key}'}
    resp = requests.post(url, headers=headers, json={'inputs': texts}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def embed(texts: Sequence[str]):
    """Unified embeddings entrypoint.

    Priority: local sentence-transformers -> HF embeddings API -> simple TF-IDF
    """
    try:
        return sentence_transformers_embed(texts)
    except Exception:
        pass
    try:
        return hf_embeddings_api(texts)
    except Exception:
        pass
    # last-resort: TF-IDF vectors (dense float lists)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except Exception:
        raise RuntimeError('No embedding backend available; install sentence-transformers or set HF_API_KEY')
    vec = TfidfVectorizer(max_features=512)
    m = vec.fit_transform(texts).toarray()
    return m.tolist()
