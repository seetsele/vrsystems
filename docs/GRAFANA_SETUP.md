# Grafana & Prometheus Setup

This guide explains how to run Prometheus + Grafana locally and import the Verity Provider dashboard.

Prerequisites:
- Docker and docker-compose installed

Steps:
1. Start services

   cd docker/prometheus
   docker-compose up -d

2. Visit Grafana: http://localhost:3000
   - Default credentials: admin / admin (change on first login)
   - The Prometheus datasource is configured via provisioning under `docker/prometheus/provisioning`.

3. Dashboards
   - The `public/grafana_provider_dashboard.json` file is mounted into Grafana during startup and provisioned into the Dashboards folder.
   - If not automatically imported, go to Dashboards → Import → Upload `public/grafana_provider_dashboard.json`.

4. Useful queries
   - Provider failures: `verity_provider_failures`
   - Provider in cooldown: `verity_provider_in_cooldown`
   - Cache hits/misses: `verity_cache_hits`, `verity_cache_misses`

5. Notes
   - When running on remote servers, update `docker/prometheus/prometheus.yml` to point to the correct API host/port for scraping `/metrics`.
   - For production deployments, secure Grafana with a password, and restrict access to the provisioning files.
