"""Simple triage helper for NH-003 using `python-tools/regression_results.json`.

This script prints provider verdict breakdown, confidence, and top sources for NH-003
to assist debugging and prompt/template adjustments.
"""
import json
import sys

PATH = 'regression_results.json'

def main():
    try:
        with open(PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('regression_results.json not found. Run regression_runner.py first.')
        sys.exit(1)

    nh = None
    for r in data.get('runs', []):
        if r.get('id') == 'NH-003':
            nh = r
            break

    if not nh:
        print('NH-003 not found in regression_results.json')
        sys.exit(1)

    resp = nh.get('response', {})
    print('\nNH-003 TRIAGE\n----------')
    print('Claim preview:', nh.get('claim_preview'))
    print('API verdict:', resp.get('verdict'), 'confidence:', resp.get('confidence'))

    print('\nProvider breakdown:')
    cv = resp.get('cross_validation', {})
    for p in cv.get('verdict_breakdown', []):
        print('-', p.get('provider'), '->', p.get('verdict'), f"(conf {p.get('confidence')})")

    print('\nTop sources:')
    for s in resp.get('sources', [])[:8]:
        print('-', s.get('title'), '-', s.get('url'))

    print('\nSuggested quick fixes:')
    print('- Add higher-weighted authoritative sources (WHO, major meta-analyses).')
    print('- If provider disagreement stems from model versions, reduce weight of low-agreement providers.')
    print('- Improve prompt templates for health claims to require citation of meta-analyses and RCTs.')

if __name__ == '__main__':
    main()
