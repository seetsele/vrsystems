#!/usr/bin/env python3
"""Generate static HTML pages for pytest test files.

Scans `tests/` and `python-tools/tests/` for .py files and creates
`public/tests/index.html` plus one HTML file per test source file.
"""
from pathlib import Path
import html
import re
import json


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'public' / 'tests'
TEST_DIRS = [ROOT / 'tests', ROOT / 'python-tools' / 'tests']


def find_test_files():
    files = []
    for d in TEST_DIRS:
        if d.exists():
            for p in sorted(d.rglob('*.py')):
                files.append(p)
    return files


def extract_test_items(text):
    # Find top-level test functions and test classes
    funcs = re.findall(r"^def\s+(test_[A-Za-z0-9_]+)\s*\(", text, re.M)
    classes = re.findall(r"^class\s+([A-Za-z0-9_]*Test[A-Za-z0-9_]*)\s*\(:", text, re.M)
    return funcs, classes


def extract_markers_and_types(text):
    # Find pytest.mark.<name> usages and file-level TYPE: comments
    markers = re.findall(r"@pytest\.mark\.([A-Za-z0-9_]+)", text)
    # TYPE: e2e,integration,unit
    types = []
    for m in re.findall(r"^#\s*TYPE:\s*([A-Za-z0-9_,\-\s]+)$", text, re.M):
        for t in [x.strip() for x in m.split(',') if x.strip()]:
            types.append(t)
    # infer common types from markers and file-level hints
    common = ['unit','integration','e2e','smoke','performance','perf','regression','security','flaky','acceptance']
    for c in common:
        if c in markers and c not in types:
            types.append(c)
    # also look for keywords in the file for simple inference
    lower = text.lower()
    if 'integration' in lower and 'integration' not in types:
        types.append('integration')
    if 'e2e' in lower and 'e2e' not in types:
        types.append('e2e')
    if 'smoke' in lower and 'smoke' not in types:
        types.append('smoke')
    # normalize unique
    markers = sorted(set(markers))
    types = sorted(set(types))
    return markers, types


def render_file_page(src_path: Path, rel_to_root: Path):
    text = src_path.read_text(encoding='utf-8')
    escaped = html.escape(text)
    funcs, classes = extract_test_items(text)
    markers, types = extract_markers_and_types(text)
    out_name = (rel_to_root.as_posix()).replace('/', '_')
    out_file = OUT_DIR / (out_name + '.html')

    title = f"Tests: {rel_to_root}"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open('w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title>")
        f.write("<link rel=\"stylesheet\" href=\"tests.css\">")
        f.write(f"</head><body><div class=\"wrap\">")
        f.write(f"<h1>{html.escape(title)}</h1>")
        f.write(f"<p><a href=\"index.html\">Back to tests index</a></p>")
        if classes or funcs:
            f.write('<div class="items">')
            if classes:
                f.write('<h2>Test classes</h2><ul>')
                for c in classes:
                    f.write(f'<li>{html.escape(c)}</li>')
                f.write('</ul>')
            if funcs:
                f.write('<h2>Test functions</h2><ul>')
                for fn in funcs:
                    f.write(f'<li>{html.escape(fn)}</li>')
                f.write('</ul>')
            if markers or types:
                f.write('<h3>Markers / Types</h3><ul>')
                for m in markers:
                    f.write(f'<li>marker: {html.escape(m)}</li>')
                for t in types:
                    f.write(f'<li>type: {html.escape(t)}</li>')
                f.write('</ul>')
            f.write('</div>')

        f.write('<h2>Source</h2>')
        f.write('<pre class="source">')
        f.write(escaped)
        f.write('</pre>')
        f.write('</div></body></html>')

    return out_file


def render_index(pages):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx = OUT_DIR / 'index.html'
    with idx.open('w', encoding='utf-8') as f:
        f.write('<!doctype html><html><head><meta charset="utf-8"><title>Test files</title>')
        f.write('<link rel="stylesheet" href="tests.css">')
        f.write('</head><body><div class="wrap"><h1>Repository Tests</h1>')
        f.write('<p>Auto-generated listing of pytest test files.</p>')
        f.write('<ul>')
        for rel, page in pages:
            fname = page.name
            f.write(f'<li><a href="{fname}">{html.escape(rel.as_posix())}</a></li>')
        f.write('</ul>')
        f.write('</div></body></html>')


def write_index_json(pages):
    # pages is list of tuples (rel, page_path)
    data = []
    for rel, page in pages:
        src = (ROOT / rel).read_text(encoding='utf-8') if (ROOT / rel).exists() else ''
        funcs, classes = extract_test_items(src)
        markers, types = extract_markers_and_types(src)
        node = {
            'path': rel.as_posix(),
            'html': page.name,
            'functions': funcs,
            'classes': classes,
            'markers': markers,
            'types': types,
        }
        data.append(node)
    out = OUT_DIR / 'tests.json'
    out.write_text(json.dumps(data, indent=2), encoding='utf-8')


def write_css():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    css = OUT_DIR / 'tests.css'
    css.write_text('''
body{font-family:Inter,system-ui,Arial,Helvetica,sans-serif;background:#0f1720;color:#e6eef8}
.wrap{max-width:1100px;margin:40px auto;padding:24px;background:#0b1220;border-radius:10px;border:1px solid rgba(255,255,255,0.03)}
h1,h2{color:#fff}
pre.source{background:#07101a;color:#bfe0ff;padding:16px;border-radius:8px;overflow:auto}
.items ul{list-style:none;padding-left:0}
.items li{padding:4px 0}
a{color:#7dd3fc}
''', encoding='utf-8')


def main():
    files = find_test_files()
    pages = []
    for p in files:
        try:
            rel = p.relative_to(ROOT)
        except Exception:
            rel = p
        page = render_file_page(p, rel)
        pages.append((rel, page))

    render_index(pages)
    write_css()
    # write machine-readable index for the browser runner
    try:
        write_index_json(pages)
        print('Wrote tests.json')
    except Exception as e:
        print('Failed to write tests.json:', e)
    print('Generated', len(pages), 'test pages in', OUT_DIR)


if __name__ == '__main__':
    main()
