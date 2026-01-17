import os
import sys
import json
import time
from pathlib import Path

try:
    import requests
except Exception:
    print('requests library not installed')
    sys.exit(2)


def _load_api_key():
    api_key = os.environ.get('FIREWORKS_API_KEY')
    if api_key:
        return api_key
    env_path = Path(__file__).resolve().parents[2] / 'python-tools' / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith('FIREWORKS_API_KEY'):
                _, val = line.split('=', 1)
                return val.strip()
    return None


def run_probe(attempts=3, model='accounts/fireworks/models/llama-v3p3-70b-instruct'):
    api_key = _load_api_key()
    if not api_key:
        print('No FIREWORKS_API_KEY found in environment or python-tools/.env')
        return 3

    url = 'https://api.fireworks.ai/inference/v1/chat/completions'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    results = []
    for i in range(attempts):
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': f'Ping #{i+1}: are you active?'}],
            'max_tokens': 16
        }
        start = time.time()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            latency = time.time() - start
            entry = {
                'attempt': i + 1,
                'status_code': resp.status_code,
                'latency_s': round(latency, 3),
                'headers': dict(resp.headers),
                'body_snippet': resp.text[:1000]
            }
        except Exception as e:
            entry = {'attempt': i + 1, 'error': str(e)}
        results.append(entry)

    # write artifact
    ts = int(time.time())
    vault_dir = os.path.join(os.getcwd(), 'test-vault')
    os.makedirs(vault_dir, exist_ok=True)
    out = os.path.join(vault_dir, f'fireworks-run-{ts}.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'timestamp': ts, 'results': results}, fh, indent=2)

    # summary
    oks = [r for r in results if r.get('status_code') == 200]

    # parse any quota/credit related headers from the first OK response
    quota_info = None
    for r in results:
        if r.get('status_code') == 200:
            hdrs = r.get('headers', {}) or {}
            # common header keys
            keys = {k.lower(): v for k, v in hdrs.items()}
            qi = {}
            # rate limit style headers
            for k in ('x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset'):
                if k in keys:
                    qi[k] = keys[k]
            # credits or quota
            for k in ('x-credits-remaining', 'x-credits', 'x-quota-remaining', 'x-quota'):
                if k in keys:
                    qi[k] = keys[k]
            # provider-specific
            for k in ('x-fireworks-credits', 'x-fw-credits'):
                if k in keys:
                    qi[k] = keys[k]
            # if body contains simple quota info, attempt to parse
            body = r.get('body_snippet', '')
            try:
                jb = json.loads(body)
                # common fields
                for fld in ('credits', 'quota', 'remaining_credits', 'remaining'):
                    if fld in jb:
                        qi[fld] = jb.get(fld)
            except Exception:
                pass
            if qi:
                quota_info = qi
                break

    summary_record = {'artifact': out, 'ok_count': len(oks), 'total': len(results), 'quota': quota_info}
    with open(os.path.join(vault_dir, f'fireworks-summary-{ts}.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary_record, fh, indent=2)

    if oks:
        print(f'Fireworks probe: {len(oks)}/{len(results)} OK; artifact: {out}')
        if quota_info:
            print('Quota info found:', quota_info)
        return 0
    else:
        print(f'Fireworks probe: 0/{len(results)} OK; artifact: {out}')
        return 6


if __name__ == '__main__':
    code = run_probe(attempts=int(os.environ.get('FIREWORKS_PROBES', '3')))
    sys.exit(code)
