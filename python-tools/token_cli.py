"""CLI helper to issue scoped JWT tokens using `python-tools/token_service.py`.

Usage:
  python token_cli.py --subject user@example.com --scopes verify,moderate --expires 3600

Reads `TOKEN_SECRET` from environment; prints the token to stdout.
"""
import os
import argparse
from token_service import TokenService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', required=True)
    parser.add_argument('--scopes', default='')
    parser.add_argument('--secret', default=None, help='Optional raw secret to sign with (overrides env)')
    parser.add_argument('--expires', type=int, default=3600)
    args = parser.parse_args()
    secret = args.secret or os.environ.get('TOKEN_SECRET')
    if not secret:
        raise SystemExit('TOKEN_SECRET not set in environment and --secret not provided')

    svc = TokenService(secret=secret)
    scopes = [s.strip() for s in args.scopes.split(',') if s.strip()]
    token = svc.create_token(args.subject, scopes, expires_in=args.expires)
    print(token)


if __name__ == '__main__':
    main()
