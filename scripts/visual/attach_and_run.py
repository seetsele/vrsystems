#!/usr/bin/env python3
"""
Attach a target screenshot (local path or URL) to tests/visual/targets/desktop-target.png
and run the Playwright comparison test. Writes diffs to tests/visual/target-diffs/ and prints
summary to stdout.

Usage:
  python scripts/visual/attach_and_run.py --file /path/to/screenshot.png
  python scripts/visual/attach_and_run.py --url https://example.com/desktop-target.png

"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import urllib.request

ROOT = Path(__file__).resolve().parents[2]
TARGET_DIR = ROOT / 'tests' / 'visual' / 'targets'
TARGET_FILE = TARGET_DIR / 'desktop-target.png'
DIFF_DIR = ROOT / 'tests' / 'visual' / 'target-diffs'


def download(url, dest: Path):
    print(f"Downloading {url} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dest, 'wb') as f:
        shutil.copyfileobj(r, f)


def copy_file(path, dest: Path):
    print(f"Copying {path} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, dest)


def run_playwright():
    if os.name == 'nt':
        cmd = ['npx.cmd', 'playwright', 'test', 'tests/visual/compare-to-target.spec.ts', '--reporter=list']
    else:
        cmd = ['npx', 'playwright', 'test', 'tests/visual/compare-to-target.spec.ts', '--reporter=list']
    print('Running:', ' '.join(cmd))
    p = subprocess.run(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    return p.returncode


def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--file', help='Local path to image file to use as target')
    g.add_argument('--url', help='URL to download target image from')
    args = parser.parse_args()

    if args.url:
        download(args.url, TARGET_FILE)
    else:
        src = Path(args.file)
        if not src.exists():
            print('ERROR: file not found:', src)
            sys.exit(2)
        copy_file(src, TARGET_FILE)

    DIFF_DIR.mkdir(parents=True, exist_ok=True)

    rc = run_playwright()

    # Report diffs
    diffs = list(DIFF_DIR.glob('diff-*.png'))
    if diffs:
        print('Diff images written:')
        for d in diffs:
            print(' -', d)
    else:
        print('No diff images produced.')

    if rc == 0:
        print('\nOK: Screenshot matched within tolerance.')
    else:
        print('\nFAILED: Visual comparison failed. See diffs above for debugging.')
    sys.exit(rc)


if __name__ == '__main__':
    main()
