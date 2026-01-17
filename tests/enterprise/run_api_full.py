#!/usr/bin/env python3
import os
import json
import time
import requests
import sys

BASE = os.environ.get('TEST_URL', 'http://localhost:8000')

ENDPOINTS = [
    ("GET", "/"),
    ("POST", "/verify", {"claim": "test claim"}),
    ("GET", "/api/docs"),
    ("GET", "/health"),
    ("GET", "/status"),
    ("GET", "/tools"),
    ("GET", "/settings"),
    ("GET", "/provider-setup"),
    ("GET", "/dashboard"),
]


def sanitize_path(p: str) -> str:
    return p.strip('/').replace('/', '_') or 'root'


def run():
    ts = int(time.time())
    vault_dir = os.path.join(os.getcwd(), 'test-vault')
    os.makedirs(vault_dir, exist_ok=True)
    summary = {
        'base': BASE,
        'timestamp': ts,
        'results': []
    }

    for method, path, *rest in ENDPOINTS:
        payload = rest[0] if rest else None
        url = BASE.rstrip('/') + path
        record = {'method': method, 'path': path, 'url': url}
        try:
            if method == 'GET':
                resp = requests.get(url, timeout=12)
            else:
                resp = requests.post(url, json=payload or {}, timeout=12)
            record['status_code'] = resp.status_code
            record['ok'] = 200 <= resp.status_code < 400
            record['body_snippet'] = resp.text[:1000]
            record['headers'] = dict(resp.headers)
        except requests.RequestException as e:
            record['status_code'] = None
            record['ok'] = False
            record['error'] = str(e)

        summary['results'].append(record)

        fname = f"api-{method}-{sanitize_path(path)}.json"
        with open(os.path.join(vault_dir, f"{ts}-{fname}"), 'w', encoding='utf-8') as fh:
            json.dump(record, fh, indent=2)

    # aggregate
    passed = sum(1 for r in summary['results'] if r.get('ok'))
    failed = len(summary['results']) - passed
    summary['passed'] = passed
    summary['failed'] = failed

    out_file = os.path.join(vault_dir, f'api-run-{ts}.json')
    with open(out_file, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2)

    print(f"API run complete — passed: {passed}, failed: {failed}. Artifacts: {vault_dir}")
    # Fireworks probe: if FIREWORKS_API_KEY is present, do an additional probe
    fw_key = os.environ.get('FIREWORKS_API_KEY')
    if not fw_key:
        # attempt to read from python-tools/.env
        env_path = os.path.join(os.getcwd(), 'python-tools', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as fh:
                for line in fh:
                    if line.strip().startswith('FIREWORKS_API_KEY'):
                        _, val = line.split('=', 1)
                        fw_key = val.strip()
                        break

    if fw_key:
        try:
            fw_url = 'https://api.fireworks.ai/inference/v1/chat/completions'
            payload = {
                'model': 'accounts/fireworks/models/llama-v3p3-70b-instruct',
                'messages': [{'role': 'user', 'content': 'Probe: are you active?'}],
                'max_tokens': 16
            }
            resp = requests.post(fw_url, headers={'Authorization': f'Bearer {fw_key}'}, json=payload, timeout=15)
            fw_record = {
                'status_code': resp.status_code,
                'headers': dict(resp.headers),
                'body_snippet': resp.text[:1000]
            }
        except Exception as e:
            fw_record = {'error': str(e)}
        summary['fireworks'] = fw_record
        # write per-fireworks artifact
        with open(os.path.join(vault_dir, f'{ts}-fireworks-probe.json'), 'w', encoding='utf-8') as fh:
            json.dump(fw_record, fh, indent=2)
        # update an enterprise summary file that aggregates runs
        summary_file = os.path.join(vault_dir, 'enterprise-summary.json')
        agg = {}
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as sf:
                    agg = json.load(sf)
            except Exception:
                agg = {}
        run_entry = {
            'timestamp': ts,
            'base': BASE,
            'passed': passed,
            'failed': failed,
            'fireworks_probe': fw_record
        }
        agg.setdefault('runs', []).append(run_entry)
        agg['last_run'] = run_entry
        with open(summary_file, 'w', encoding='utf-8') as sf:
            json.dump(agg, sf, indent=2)
    strict = os.environ.get('STRICT_TESTS')
    if strict and failed > 0:
        print('STRICT_TESTS set and failures present — exiting non-zero')
        return 1
    return 0


if __name__ == '__main__':
    code = run()
    sys.exit(code)
