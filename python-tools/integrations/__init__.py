"""Integration adapters for optional external services.

Each adapter attempts to use a preferred free/open provider (via env vars),
and falls back to a local, lightweight implementation when possible.

Adapters included:
- moderation: uses HuggingFace Inference API (HF_API_KEY) or local transformers model
- embeddings: uses sentence-transformers (local) or HF embeddings API
- llm: uses local gpt4all (if installed) or HF text-generation API
- streaming: connectors for Mastodon and Reddit polling (optional deps)
- maps: Nominatim geocoding + OSM tiles

These modules are deliberately permissive about optional dependencies so the
repo can run without all services installed; production usage should set the
appropriate environment variables and install needed packages.
"""

from . import moderation, embeddings, llm, streaming, maps

__all__ = ["moderation", "embeddings", "llm", "streaming", "maps"]
