"""Simple Discord webhook sender (bot stub)."""
import os
import httpx

WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')


def send(content: str) -> bool:
    if not WEBHOOK:
        return False
    try:
        resp = httpx.post(WEBHOOK, json={"content": content}, timeout=10)
        return resp.status_code in (200, 204)
    except Exception:
        return False


if __name__ == '__main__':
    print('Test send:', send('Hello from Verity Discord bot'))
