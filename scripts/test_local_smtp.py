"""Test local SMTP helper.

Usage:
  python scripts/test_local_smtp.py

This attempts to send a test email via the local SMTP server configured by
`LOCAL_SMTP_HOST`/`LOCAL_SMTP_PORT` (defaults to localhost:1025 for MailHog).
"""
import os
import sys
import asyncio
from pathlib import Path

# Add python-tools to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python-tools'))
import email_service as es_mod


async def run():
    # Respect environment variables
    svc = es_mod.EmailService()
    if not svc.is_configured:
        print('EmailService not configured. Set LOCAL_SMTP_HOST or SENDGRID_API_KEY in environment.')
        return
    print('Attempting test email via configured transport...')
    res = await svc.send_email('test@example.com', 'Test from Verity local SMTP', '<p>Test</p>')
    print('Result:', res)


if __name__ == '__main__':
    asyncio.run(run())
