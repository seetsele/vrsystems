param(
    [string]$ComposeFile = 'docker-compose.postgres.yml'
)

Write-Output "Starting staging Postgres via $ComposeFile..."
docker compose -f $ComposeFile up -d

Write-Output "Waiting for Postgres to become available..."
for ($i = 0; $i -lt 30; $i++) {
    $res = docker run --rm --network host postgres:15 pg_isready -h localhost -p 5432 -U verity 2>&1
    if ($res -like '*accepting connections*') { Write-Output 'Postgres ready'; break }
    Start-Sleep -Seconds 2
}

Write-Output "Applying Alembic migrations against DATABASE_URL in .env.staging or environment"
python -m alembic -c python-tools/alembic.ini upgrade head

Write-Output "Staging Postgres setup complete."
