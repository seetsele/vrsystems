import os
import json
import httpx
import time

GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')  # or use basic auth
RETRY_SECONDS = int(os.getenv('GRAFANA_IMPORT_RETRY_SECONDS', '5'))
MAX_RETRIES = int(os.getenv('GRAFANA_IMPORT_MAX_RETRIES', '12'))


def _post_dashboard(payload, headers):
    api = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/db"
    r = httpx.post(api, json={"dashboard": payload, "overwrite": True}, headers=headers, timeout=10.0)
    r.raise_for_status()
    return r.json()


def import_dashboard(json_path: str, wait_for_grafana: bool = True):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    headers = {'Content-Type': 'application/json'}
    if GRAFANA_API_KEY:
        headers['Authorization'] = f'Bearer {GRAFANA_API_KEY}'

    retries = 0
    last_err = None
    while True:
        try:
            return _post_dashboard(payload, headers)
        except Exception as e:
            last_err = e
            if not wait_for_grafana or retries >= MAX_RETRIES:
                raise
            retries += 1
            time.sleep(RETRY_SECONDS)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('file', help='path to grafana dashboard json')
    p.add_argument('--no-wait', action='store_true', help='Do not retry if Grafana is unavailable')
    args = p.parse_args()
    print(import_dashboard(args.file, wait_for_grafana=not args.no_wait))
