#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def timestamp():
    return datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')

def ensure_dir(p: Path):
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

def main():
    vault = Path(__file__).resolve().parent.parent / 'test-vault'
    ensure_dir(vault)
    out_xml = Path(__file__).resolve().parent.parent / f'test-results/pytest-{timestamp()}.xml'
    ensure_dir(out_xml.parent)

    args = [sys.executable, '-m', 'pytest', '--junitxml', str(out_xml)] + sys.argv[1:]
    print('Running:', ' '.join(args))
    proc = subprocess.run(args)
    if proc.returncode != 0:
        print('Pytest exited with code', proc.returncode)
    # Move the xml to vault with timestamp
    dest = vault / f'pytest-{timestamp()}.xml'
    out_xml.rename(dest)
    print('Recorded pytest results to', dest)
    return proc.returncode

if __name__ == '__main__':
    sys.exit(main())