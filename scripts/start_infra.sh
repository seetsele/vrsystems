#!/usr/bin/env bash
set -euo pipefail
echo "Starting local infra via docker-compose (Redis, Qdrant, Postgres, MinIO)"
cd "$(dirname "$0")/../python-tools/infra"
if command -v docker >/dev/null 2>&1; then
  docker compose up -d
else
  echo "Docker not installed or not in PATH. Please install Docker to start infra."
fi
