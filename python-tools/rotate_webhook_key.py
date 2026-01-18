#!/usr/bin/env python3
"""Rotate or set a webhook secret by `id` or `url`.

Usage:
  python rotate_webhook_key.py --id <webhook_id> --secret <new_secret>
  python rotate_webhook_key.py --url <webhook_url> --secret <new_secret>

This updates the `webhooks` table secret column (encrypted with the same KMS/fallback used by the runner).
"""
import argparse
import sqlite3
import os
import sys
from simple_test_api import encrypt_secret, DB_PATH


def rotate_by_id(wid, new_secret):
    enc = encrypt_secret(new_secret)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('UPDATE webhooks SET secret=? WHERE id=?', (enc, wid))
    conn.commit()
    conn.close()


def rotate_by_url(url, new_secret):
    enc = encrypt_secret(new_secret)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute('UPDATE webhooks SET secret=? WHERE url=?', (enc, url))
    conn.commit()
    conn.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', help='webhook id')
    p.add_argument('--url', help='webhook url')
    p.add_argument('--secret', required=True, help='new secret value')
    args = p.parse_args()
    if not args.id and not args.url:
        print('Specify --id or --url', file=sys.stderr); sys.exit(2)
    if args.id:
        rotate_by_id(args.id, args.secret)
        print('Rotated secret for id', args.id)
    else:
        rotate_by_url(args.url, args.secret)
        print('Rotated secret for url', args.url)


if __name__ == '__main__':
    main()
