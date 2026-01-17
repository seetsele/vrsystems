#!/usr/bin/env python3
"""
CI Smoke Tests Runner
Runs existing local smoke tests and the blog crawler.
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(__file__)

def run(cmd, cwd=None):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd or ROOT)
    return res.returncode


def main():
    rc = 0
    # 1) local smoke tests
    rc1 = run('python local_smoke_tests.py', cwd=ROOT)
    if rc1 != 0:
        print('local_smoke_tests.py failed')
        rc = rc1
    else:
        print('local_smoke_tests.py passed')

    # 2) blog crawler
    rc2 = run('python blog_crawler.py', cwd=ROOT)
    if rc2 != 0:
        print('blog_crawler.py found issues')
        rc = rc2
    else:
        print('blog_crawler.py passed')

    if rc == 0:
        print('\nSMOKE TESTS OK')
    else:
        print('\nSMOKE TESTS FAILED')
    sys.exit(rc)

if __name__ == '__main__':
    main()
