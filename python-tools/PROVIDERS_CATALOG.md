Open-source and low-cost providers, runtimes, and tools to integrate with Verity

This catalog lists practical free / open / heavily-discounted options for each capability
your system needs. Use the adapters in `python-tools/integrations` to wire these in.

Moderation
- Hugging Face Inference (free tier) — many moderation/classification models
- OpenModeration (community datasets/models)
- Perspective API (limited free use via Google)

Embeddings / Vector DB
- sentence-transformers (local models)
- Hugging Face Embeddings API (free tier)
- Qdrant (open-source, Docker image)
- FAISS (local, CPU/GPU)
- Milvus (open-source)

LLM / Research Assistant
- gpt4all (local models)
- Mistral, Llama 2, MPT, Bloom via Hugging Face Hub (check licensing)
- Hugging Face Inference / Replicate (hosted inference)
- Ollama (local model manager, paid/OSS hybrid)

Streaming & Ingest
- Mastodon API (public instances)
- Reddit RSS / API (streaming or polling)
- Twitter/X (limited, paid) — consider scraping with legal review
- Webhooks, RSS, PubSub architectures; Kafka/Redis Streams for durable ingestion

Maps / Geocoding
- Nominatim (OpenStreetMap) for geocoding
- OSM tile servers; self-host or use providers friendly to small usage

Search / Vector similarity
- Qdrant + pgvector for production vector storage
- Weaviate (open-source) with vector indexes and semantic search

Observability & infra
- Prometheus + Grafana (OSS)
- Loki (logs) + Tempo (traces) if needed

Training / Fine-tuning
- Hugging Face Transformers + PEFT/LoRA for parameter-efficient finetuning
- LangChain for pipelines and retrieval-augmented generation
- Use small base models (Llama 2 / Mistral / MPT) and LoRA to keep costs low

Notes
- Always verify licenses for model use in production.
- Use environment variables to switch providers (`HF_API_KEY`, `QDRANT_URL`, etc.).
