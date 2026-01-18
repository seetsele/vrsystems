import os
import json
import httpx

GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')  # or use basic auth


def import_dashboard(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    headers = {'Content-Type': 'application/json'}
    if GRAFANA_API_KEY:
        headers['Authorization'] = f'Bearer {GRAFANA_API_KEY}'

    api = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/db"
    r = httpx.post(api, json={"dashboard": payload, "overwrite": True}, headers=headers, timeout=10.0)
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('file', help='path to grafana dashboard json')
    args = p.parse_args()
    print(import_dashboard(args.file))
