#!/usr/bin/env python3
"""Simple provider monitoring script
Polls /providers/health and /health endpoints and logs status. Intended as a lightweight local monitor.
"""

import time
import requests
import logging
from pathlib import Path

API_BASE = "http://localhost:8000"
LOG_FILE = Path(__file__).parent / "provider_health.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def poll_once():
    try:
        r = requests.get(f"{API_BASE}/providers/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            in_cooldown = data.get('health', {}).get('in_cooldown', [])
            failures = data.get('health', {}).get('failures', {})
            logging.info(f"Providers in cooldown: {in_cooldown} failures={failures}")
            return True, data
        else:
            logging.warning(f"Providers health returned {r.status_code}")
            return False, None
    except Exception as e:
        logging.error(f"Exception fetching provider health: {e}")
        return False, None


if __name__ == '__main__':
    print("Starting provider monitor. Will poll every 60s. Ctrl-C to stop.")
    while True:
        ok, data = poll_once()
        if not ok:
            print("Provider health check failed. See log for details.")
        else:
            in_cd = data.get('health', {}).get('in_cooldown', [])
            if in_cd:
                print(f"Warning: Providers in cooldown: {in_cd}")
            else:
                print("All providers healthy")
        time.sleep(60)
