#!/usr/bin/env python3
"""Find likely-unused function and class definitions in the repo.

This is a conservative heuristic scanner: it collects top-level `def` and `class`
names from .py files under specified roots and then searches for their usages
by simple name occurrences across the repo. If a name is only declared but
never referenced elsewhere (except its defining file), it's reported as
potentially unused.

Run: `python tools/find_unused_defs.py` from repo root.
"""
import ast
import os
import glob
import re
from pathlib import Path

ROOTS = [
    'python-tools',
    'tests',
    '.',
]


def collect_defs(root):
    defs = {}
    for py in glob.glob(os.path.join(root, '**', '*.py'), recursive=True):
        try:
            src = open(py, 'r', encoding='utf-8').read()
        except Exception:
            continue
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # skip dunder
                if node.name.startswith('__'):
                    continue
                defs.setdefault(node.name, set()).add(py)
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith('__'):
                    continue
                defs.setdefault(node.name, set()).add(py)
    return defs


def search_usage(name, roots):
    pattern = re.compile(r'\b' + re.escape(name) + r'\b')
    found = []
    for root in roots:
        for f in glob.glob(os.path.join(root, '**', '*.py'), recursive=True):
            try:
                txt = open(f, 'r', encoding='utf-8').read()
            except Exception:
                continue
            if pattern.search(txt):
                found.append(f)
    return found


def main():
    repo_root = Path(os.getcwd())
    roots = [str(repo_root / r) for r in ROOTS if os.path.exists(repo_root / r)]
    defs = {}
    for r in roots:
        d = collect_defs(r)
        for k, v in d.items():
            defs.setdefault(k, set()).update(v)

    candidates = []
    for name, origins in sorted(defs.items()):
        usages = search_usage(name, roots)
        # if usages only in origin files, likely unused elsewhere
        usages_set = set(usages)
        origin_files = set(origins)
        # exclude obvious file where defined
        if usages_set <= origin_files:
            candidates.append((name, list(origins)))

    print('\nPotentially unused definitions (heuristic):')
    for name, files in candidates:
        print(f'- {name} defined in:')
        for f in files:
            print(f'    {f}')
    print(f'\nTotal potentially unused: {len(candidates)}')


if __name__ == '__main__':
    main()
