#!/usr/bin/env python3
import csv
from pathlib import Path

SRC = Path('tools') / 'unused_app.csv'
OUT = Path('tools') / 'unused_filtered_top50.csv'

if not SRC.exists():
    print('source missing', SRC)
    raise SystemExit(1)

rows = []
with SRC.open(encoding='utf-8') as fh:
    r = csv.DictReader(fh)
    for row in r:
        name = row['name']
        files = row['defined_in']
        score = files.count(';') + 1
        low = files.lower()
        is_vendor = 'node_modules' in low or 'dmg-builder' in low or 'node-gyp' in low
        rows.append((score, is_vendor, name, files))

rows.sort(key=lambda x: (x[0], x[1]))

filtered = []
for score, is_vendor, name, files in rows:
    if is_vendor:
        continue
    # exclude pure test-only definitions
    if '\\tests\\' in files.lower() or '/tests/' in files.lower():
        continue
    filtered.append((name, files))
    if len(filtered) >= 50:
        break

with OUT.open('w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['name', 'defined_in'])
    for name, files in filtered:
        w.writerow([name, files])

print('WROTE', OUT, 'ROWS', len(filtered))
for name, files in filtered[:20]:
    print('-', name, 'in', files)
