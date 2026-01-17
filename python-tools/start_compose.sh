#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="../docker-compose.yml"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found. Install Docker and re-run."
  exit 1
fi

echo "Starting compose from $COMPOSE_FILE..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for services (timeout 120s)..."
deadline=$((SECONDS+120))
wait_url(){
  url="$1"
  while [ $SECONDS -lt $deadline ]; do
    if curl -sSf --max-time 5 "$url" >/dev/null 2>&1; then
      echo "$url OK"
      return 0
    fi
    sleep 3
  done
  echo "WARN: $url did not respond in time" >&2
  return 1
}

wait_url "http://127.0.0.1:8010/prometheus" || true
wait_url "http://127.0.0.1:3001/tests/runner.html" || true
wait_url "http://127.0.0.1:9090" || true
wait_url "http://127.0.0.1:3000" || true

echo "Compose started — Grafana: http://localhost:3000 (admin/admin)"
