#!/usr/bin/env python3
"""Focused unused defs scanner for application code.

Excludes `node_modules`, `build`, and common vendor folders. Writes a
CSV report to `tools/unused_app.csv` and prints a short summary.

Run: `python tools/find_unused_defs_app.py`
"""
import ast
import glob
import os
import re
import csv
from pathlib import Path

EXCLUDE_DIRS = ['node_modules', 'build', '.venv', 'venv', '__pycache__']
ROOTS = ['python-tools', 'tests', 'scripts', 'public']


def iter_py_files():
    repo = Path(os.getcwd())
    for root in ROOTS:
        base = repo / root
        if not base.exists():
            continue
        for p in base.rglob('*.py'):
            parts = set(p.parts)
            if any(x in parts for x in EXCLUDE_DIRS):
                continue
            yield str(p)


def collect_defs(files):
    defs = {}
    for py in files:
        try:
            src = open(py, 'r', encoding='utf-8').read()
        except Exception:
            continue
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                if node.name.startswith('__'):
                    continue
                defs.setdefault(node.name, set()).add(py)
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith('__'):
                    continue
                defs.setdefault(node.name, set()).add(py)
    return defs


def search_usage(name, files):
    pattern = re.compile(r'\b' + re.escape(name) + r'\b')
    found = []
    for f in files:
        try:
            txt = open(f, 'r', encoding='utf-8').read()
        except Exception:
            continue
        if pattern.search(txt):
            found.append(f)
    return found


def main():
    files = list(iter_py_files())
    defs = collect_defs(files)

    candidates = []
    for name, origins in sorted(defs.items()):
        usages = search_usage(name, files)
        usages_set = set(usages)
        origin_files = set(origins)
        if usages_set <= origin_files:
            candidates.append((name, ';'.join(sorted(origins))))

    out_csv = Path('tools') / 'unused_app.csv'
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['name', 'defined_in'])
        for row in candidates:
            writer.writerow(row)

    print(f'Wrote {out_csv} with {len(candidates)} candidate unused defs.')
    if len(candidates) > 0:
        for name, origins in candidates[:25]:
            print(f'- {name} in {origins}')


if __name__ == '__main__':
    main()
