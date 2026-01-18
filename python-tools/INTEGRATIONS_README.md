Integration adapters and recommended free/open services

Overview
--------
This folder contains lightweight adapters that let the system use free or open services
for moderation, embeddings, LLMs, streaming ingest, and maps. They are intentionally
permissive: adapters will try a preferred provider if configured via environment variables,
and fall back to local/simple implementations where possible.

Recommended providers / tools
-----------------------------
- Embeddings: `sentence-transformers` locally, or Hugging Face Embeddings API (free tier)
- Moderation: Hugging Face Inference moderation models, or local keyword filters / classifiers
- LLM / Research Assistant: `gpt4all` (local), or Hugging Face text generation API (free tier)
- Vector DB: Qdrant (open-source, runs in Docker), Milvus, or local FAISS/annoy (no Docker)
- Streaming ingestion: Mastodon (public), Reddit (RSS/polling), RSS feeds, and webhooks
- Maps / Geocoding: OpenStreetMap / Nominatim + OSM tile servers

How to use
----------
Each adapter exposes a simple function (for example `integrations.moderation.moderate(text)`)
and will raise a clear error if no backend is available. Configure via environment variables:

- `HF_API_KEY` — use Hugging Face APIs for moderation/embeddings/LLM
- `EMBEDDING_MODEL`, `HF_EMBEDDING_MODEL` — model names
- `GPT4ALL_MODEL` — path to local gpt4all model
- `MASTODON_TOKEN` — token for Mastodon connectors
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` — for Reddit/PRAW connectors

Next steps
----------
1. Install any optional Python packages you intend to use (e.g. `sentence-transformers`, `gpt4all`, `mastodon.py`).
2. Set environment variables for the services you prefer.
3. Wire the frontend/UI to call these adapters via the existing API endpoints.
