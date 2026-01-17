Local runner compose (static + runner + prometheus + grafana)

Quick start:

```sh
docker compose up -d
```

Services:
- `static` serves `./public` on port `3001`
- `runner` runs the FastAPI runner on port `8010` (use the compose command which runs uvicorn)
- `prometheus` on port `9090` (scrapes runner at `/prometheus`)
- `grafana` on port `3000` (admin password: `admin`)

Notes:
- The compose file mounts the repository into containers; this is intended for local development only.
- To import the Grafana dashboard, open `http://localhost:3000` and import `python-tools/grafana/test_runner_dashboard.json`.
- If you prefer the fallback `simple_test_api.py` instead of the FastAPI runner, update the `runner` service `command` to run that script and change binding host to `0.0.0.0` inside the script.
