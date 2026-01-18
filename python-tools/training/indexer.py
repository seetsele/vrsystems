"""Embed text and push vectors to Qdrant (or local FAISS) using `integrations.embeddings`.
"""
import os
import json
from python_tools.integrations import embeddings


def index_json(input_file: str, collection: str = 'verity'):
    with open(input_file, 'r', encoding='utf-8') as fh:
        docs = json.load(fh)
    texts = [d.get('text') or d.get('content') or '' for d in docs]
    vecs = embeddings.embed(texts)
    # attempt Qdrant
    qdrant_url = os.environ.get('QDRANT_URL', 'http://127.0.0.1:6333')
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=qdrant_url)
        payload = []
        for i, v in enumerate(vecs):
            payload.append({'id': i, 'vector': v, 'payload': docs[i]})
        client.recreate_collection(collection_name=collection, vector_size=len(vecs[0]))
        client.upsert(collection_name=collection, points=payload)
        print('Indexed to Qdrant:', collection)
        return
    except Exception:
        pass
    # fallback: write vectors to disk
    out = input_file + '.vectors.json'
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'texts': texts, 'vectors': vecs}, fh)
    print('Wrote vectors to', out)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('--collection', default='verity')
    args = p.parse_args()
    index_json(args.input, args.collection)
