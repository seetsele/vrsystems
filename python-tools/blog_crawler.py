#!/usr/bin/env python3
"""
Simple blog crawler to check internal blog pages for broken links.
"""
import os
import sys
import requests
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PUBLIC = os.path.join(ROOT, 'public')
BLOG_DIR = os.path.join(PUBLIC, 'blog')

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for k,v in attrs:
                if k.lower() == 'href' and v:
                    self.links.append(v)


def check_page(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    parser = LinkParser()
    parser.feed(html)
    problems = []
    for link in parser.links:
        parsed = urlparse(link)
        if parsed.scheme in ('http','https'):
            # external: try request
            try:
                r = requests.head(link, allow_redirects=True, timeout=6)
                if r.status_code >= 400:
                    problems.append((link, r.status_code))
            except Exception as e:
                problems.append((link, str(e)))
        else:
            # Internal link: resolve against public directory
            # handle anchors and relative paths
            cleaned = link.split('#')[0].split('?')[0]
            if cleaned == '' or cleaned.startswith('mailto:') or cleaned.startswith('tel:'):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), cleaned))
            if not os.path.exists(target):
                # also try root-relative
                root_target = os.path.normpath(os.path.join(PUBLIC, cleaned.lstrip('/')))
                if not os.path.exists(root_target):
                    problems.append((link, 'missing'))
    return problems


def main():
    if not os.path.isdir(BLOG_DIR):
        print('Blog directory not found:', BLOG_DIR)
        sys.exit(1)
    all_problems = {}
    for fn in os.listdir(BLOG_DIR):
        if not fn.endswith('.html'):
            continue
        path = os.path.join(BLOG_DIR, fn)
        probs = check_page(path)
        if probs:
            all_problems[path] = probs
    if not all_problems:
        print('No broken links found in public/blog/')
        return 0
    print('Broken links found:')
    for page, probs in all_problems.items():
        print('\nPage:', os.path.relpath(page, ROOT))
        for link, reason in probs:
            print('  ', link, '->', reason)
    return 2

if __name__ == '__main__':
    code = main()
    sys.exit(code)
