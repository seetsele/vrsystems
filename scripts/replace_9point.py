#!/usr/bin/env python3
"""Safe replacer: replace textual references to '21-Point' with '21-Point' across the repo.

Usage:
  python scripts/replace_21-Point.py         # dry-run, prints files that would change
  python scripts/replace_21-Point.py --apply # apply changes and write .bak backups

This tool only edits text files (html, md, js, css, json, txt, py, ts, jsx, svg) and
makes a .bak backup for each file changed. It avoids renaming files to keep links intact.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_EXT = {'.html', '.htm', '.md', '.js', '.ts', '.jsx', '.tsx', '.css', '.json', '.py', '.txt', '.svg'}
PATTERNS = [
    (re.compile(r'9[-\u2011\u2010]?\s*point', re.IGNORECASE), '21-Point'),
    (re.compile(r'9\s*point', re.IGNORECASE), '21-Point'),
    (re.compile(r'\b21-Point-system\b', re.IGNORECASE), '21-point-system'),
]


def scan_files() -> List[Path]:
    files = []
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix.lower() in INCLUDE_EXT:
            files.append(p)
    return files


def process_file(p: Path, apply: bool = False) -> bool:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        return False

    new = text
    for pat, repl in PATTERNS:
        new = pat.sub(repl, new)

    if new != text:
        print(f"Will change: {p.relative_to(ROOT)}")
        if apply:
            bak = p.with_suffix(p.suffix + '.bak')
            try:
                p.rename(bak)
            except Exception:
                # fallback to writing backup
                bak.write_text(text, encoding='utf-8')
            p.write_text(new, encoding='utf-8')
            print(f"Applied changes, backup at {bak.relative_to(ROOT)}")
        return True
    return False


def main(argv: List[str]):
    apply = '--apply' in argv
    files = scan_files()
    changed = 0
    for f in files:
        try:
            if process_file(f, apply=apply):
                changed += 1
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if apply:
        print(f"Applied changes to {changed} files.")
    else:
        print(f"Dry-run: {changed} files would be changed. Use --apply to apply.)")


if __name__ == '__main__':
    main(sys.argv[1:])
