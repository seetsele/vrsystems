"""Run quick regression checks for failed tests recorded in comprehensive_test_results.json

This runner loads `python-tools/comprehensive_test_results.json`, iterates over
`analysis.failed_tests`, and posts each `claim_preview` to the local `/verify` API
to capture the current verdict and provider metadata for triage.

Usage:
  python regression_runner.py --input comprehensive_test_results.json --output regression_results.json
"""
import json
import argparse
import requests
from urllib.parse import urljoin

API_BASE = "http://localhost:8000"

def run_regressions(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    failed = data.get('analysis', {}).get('failed_tests', [])
    results = []

    for t in failed:
        claim = t.get('claim_preview') or '<no-claim-text>'
        payload = {'claim': claim}
        print(f"Running {t.get('id')} -> payload preview: {claim[:80]!r}")
        try:
            r = requests.post(urljoin(API_BASE, '/verify'), json=payload, timeout=60)
            entry = {
                'id': t.get('id'),
                'category': t.get('category'),
                'expected': t.get('expected'),
                'claim_preview': claim,
                'status_code': r.status_code,
                'response': None
            }
            try:
                entry['response'] = r.json()
            except Exception:
                entry['response'] = r.text
        except Exception as e:
            entry = {
                'id': t.get('id'),
                'category': t.get('category'),
                'expected': t.get('expected'),
                'claim_preview': claim,
                'error': str(e)
            }
        results.append(entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({'runs': results}, f, indent=2)

    print(f"Wrote regression results to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='comprehensive_test_results.json')
    parser.add_argument('--output', default='regression_results.json')
    args = parser.parse_args()
    run_regressions(args.input, args.output)
