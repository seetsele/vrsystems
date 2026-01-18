"""Simple Slack webhook sender (bot stub)."""
import os
import httpx

WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')


def send(text: str) -> bool:
    if not WEBHOOK:
        return False
    try:
        resp = httpx.post(WEBHOOK, json={"text": text}, timeout=10)
        return resp.status_code in (200, 201)
    except Exception:
        return False


if __name__ == '__main__':
    print('Test send:', send('Hello from Verity bot'))
