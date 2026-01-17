#!/usr/bin/env python3
"""Scan repository for Zyte (formerly Scrapinghub) usage and references.

Looks for `ZYTE_API_KEY` in env files and for imports/usages of `zyte`,
`scrapinghub`, or `scrapy` in python files. Prints a concise report.

Run: `python tests/enterprise/check_zyte_usage.py`
"""
import glob
import os
import re
from pathlib import Path


def find_env_keys(root):
    keys = []
    for f in glob.glob(os.path.join(root, '**', '*.env*'), recursive=True):
        try:
            txt = open(f, 'r', encoding='utf-8').read()
        except Exception:
            continue
        if 'ZYTE_API_KEY' in txt or 'ZYTE' in txt.upper():
            keys.append(f)
    return keys


def find_imports(root):
    matches = []
    pattern = re.compile(r'\b(zyte|scrapinghub|scrapy)\b', re.I)
    for f in glob.glob(os.path.join(root, '**', '*.py'), recursive=True):
        try:
            txt = open(f, 'r', encoding='utf-8').read()
        except Exception:
            continue
        if pattern.search(txt):
            matches.append(f)
    return matches


def main():
    repo = Path(os.getcwd())
    roots = [str(repo)]
    env_files = find_env_keys('.')
    import_files = find_imports('.')

    print('Zyte env key files:')
    if env_files:
        for e in env_files:
            print(' -', e)
    else:
        print(' - none found')

    print('\nFiles importing or referencing zyte/scrapy/scrapinghub:')
    if import_files:
        for f in import_files:
            print(' -', f)
    else:
        print(' - none found')

    if env_files and not import_files:
        print('\nNote: Zyte API key(s) present but no code import references found.')


if __name__ == '__main__':
    main()
