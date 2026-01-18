"""Collect candidate training data from local sources and configured providers.

This script provides helper functions to assemble a dataset for fine-tuning or retrieval.
It is intentionally minimal — adapt to your data sources and privacy requirements.
"""
import os
import json
from typing import Iterable, Dict


def collect_from_folder(folder: str) -> Iterable[Dict]:
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith('.json'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        yield json.load(fh)
                except Exception:
                    continue


def collect_samples(out_path: str, sources: Iterable[str]):
    out = []
    for s in sources:
        out.extend(list(collect_from_folder(s)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=2)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--folders', nargs='+', required=True)
    p.add_argument('--out', default='python-tools/training/samples.json')
    args = p.parse_args()
    collect_samples(args.out, args.folders)
