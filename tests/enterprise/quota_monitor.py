#!/usr/bin/env python3
"""Read the most recent Fireworks probe artifact and alert if credits/rate-limit below threshold."""
import os
import glob
import json
import time
import sys

VAULT = os.path.join(os.getcwd(), 'test-vault')


def latest_fireworks_summary():
    pattern = os.path.join(VAULT, 'fireworks-summary-*.json')
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    with open(latest, 'r', encoding='utf-8') as fh:
        return json.load(fh), latest


def parse_numeric(v):
    try:
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return None


def run(threshold=100):
    data, path = latest_fireworks_summary() or (None, None)
    if not data:
        print('No fireworks summary artifact found')
        return 2

    quota = data.get('quota') or {}
    # try common header keys
    candidates = ['x-credits-remaining', 'x-credits', 'x-quota-remaining', 'x-quota', 'x-ratelimit-remaining', 'remaining_credits', 'credits', 'remaining']
    found = None
    for k in candidates:
        if k in quota:
            found = quota[k]
            break

    if found is None:
        print('No explicit credits/quota header found in summary; printing summary for inspection')
        print(json.dumps(data, indent=2))
        return 3

    num = parse_numeric(found)
    if num is None:
        print('Could not parse quota value:', found)
        return 3

    print(f'Latest fireworks summary: {path}')
    print('Quota numeric value:', num)
    if num < threshold:
        out = {'alert': True, 'value': num, 'threshold': threshold, 'summary': path}
        ts = int(time.time())
        out_path = os.path.join(VAULT, f'fireworks-quota-alert-{ts}.json')
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, indent=2)
        print('Quota below threshold — alert written to', out_path)
        return 1
    else:
        print('Quota OK:', num)
        return 0


if __name__ == '__main__':
    thr = int(os.environ.get('FW_QUOTA_THRESHOLD', '100'))
    code = run(threshold=thr)
    sys.exit(code)
