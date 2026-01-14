#!/usr/bin/env python3
"""Replace CI badge placeholder in README.md with actual owner/repo.
Usage:
  GITHUB_REPO=owner/repo python scripts/update_readme_badge.py
Or:
  python scripts/update_readme_badge.py owner/repo
This script is idempotent and will only replace the placeholder template.
"""
import os
import re
import sys

REPO = os.getenv('GITHUB_REPO')
if not REPO and len(sys.argv) > 1:
    REPO = sys.argv[1]

README = os.path.join(os.path.dirname(__file__), '..', 'README.md')
PLACEHOLDER = '[![CI Status](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml)'

if not REPO:
    print('No GITHUB_REPO provided. Nothing to do.')
    sys.exit(0)

owner_repo = REPO.strip()
new_badge = f'[![CI Status](https://github.com/{owner_repo}/actions/workflows/ci.yml/badge.svg)](https://github.com/{owner_repo}/actions/workflows/ci.yml)'

with open(README, 'r', encoding='utf-8') as fh:
    text = fh.read()

if PLACEHOLDER in text:
    text = text.replace(PLACEHOLDER, new_badge)
    with open(README, 'w', encoding='utf-8') as fh:
        fh.write(text)
    print(f'Updated README badge to {owner_repo}')
else:
    # try to replace any owner/repo pattern in existing badge
    updated = re.sub(r'https://github.com/[^/]+/[^/]+/actions/workflows/ci.yml/badge.svg',
                     f'https://github.com/{owner_repo}/actions/workflows/ci.yml/badge.svg', text)
    if updated != text:
        with open(README, 'w', encoding='utf-8') as fh:
            fh.write(updated)
        print(f'Updated existing README badge to {owner_repo}')
    else:
        print('No placeholder found, and no existing badge pattern matched. No changes made.')
