#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

with_docker=false
if [ "${1:-}" = "--with-docker" ]; then
  with_docker=true
fi

if $with_docker && command -v docker >/dev/null 2>&1; then
  echo "Docker detected — starting compose stack"
  (cd "$ROOT/python-tools" && ./start_compose.sh)
  exit 0
fi

echo "Starting static server on port 3001"
cd "$ROOT/public"
python -m http.server 3001 &
cd "$ROOT"

echo "Starting fallback runner"
python python-tools/simple_test_api.py &

echo "Starting FastAPI runner on 8011"
cd "$ROOT/python-tools"
python -m uvicorn test_runner_server:app --host 127.0.0.1 --port 8011 &

echo "Bringup complete. Static: http://127.0.0.1:3001, FastAPI: http://127.0.0.1:8011"
