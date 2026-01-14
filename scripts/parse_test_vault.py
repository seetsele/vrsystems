#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import csv

vault = Path(__file__).resolve().parent.parent / 'test-vault'
out = Path(__file__).resolve().parent.parent / 'test-results' / 'test-vault-summary.csv'
if not vault.exists():
    print('No test-vault/ found. Run tests to populate it.')
    sys.exit(1)

rows = []
for p in sorted(vault.iterdir()):
    if p.suffix == '.json':
        try:
            data = json.loads(p.read_text())
            suite = data.get('meta', {}).get('suite', 'jest')
            recorded = data.get('meta', {}).get('recordedAt')
            stats = data.get('results', {}).get('numTotalTests') if data.get('results') else None
            passed = data.get('results', {}).get('numPassedTests') if data.get('results') else None
            failed = data.get('results', {}).get('numFailedTests') if data.get('results') else None
            rows.append({'file': p.name, 'suite': suite, 'recordedAt': recorded, 'total': stats, 'passed': passed, 'failed': failed})
        except Exception as e:
            print('Failed to parse', p, e)
    elif p.suffix in ('.xml',):
        try:
            tree = ET.parse(p)
            root = tree.getroot()
            total = int(root.attrib.get('tests', 0))
            failures = int(root.attrib.get('failures', 0))
            errors = int(root.attrib.get('errors', 0))
            time = root.attrib.get('time')
            rows.append({'file': p.name, 'suite': 'pytest-junit', 'recordedAt': '', 'total': total, 'passed': total - failures - errors, 'failed': failures + errors})
        except Exception as e:
            print('Failed to parse xml', p, e)

out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=['file','suite','recordedAt','total','passed','failed'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print('Wrote summary to', out)