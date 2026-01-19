param(
    [string]$ComposeFile = 'docker-compose.postgres.yml'
)

Write-Output "Starting staging Postgres via $ComposeFile..."
$envFile = Join-Path (Get-Location) '.env.staging'
if (Test-Path $envFile) {
    Write-Output "Loading environment from .env.staging"
    Get-Content $envFile | ForEach-Object {
        $_ = $_.Trim()
        if ([string]::IsNullOrWhiteSpace($_) -or $_.StartsWith('#')) { return }
        $parts = $_ -split '=', 2
        if ($parts.Count -ne 2) { return }
        $key = $parts[0].Trim()
        $val = $parts[1].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $val, 'Process')
    }
    # If DATABASE_URL not provided in .env.staging, set a sensible default
    if (-not [string]::IsNullOrWhiteSpace($env:DATABASE_URL) -and $env:DATABASE_URL -ne 'None') {
        Write-Output "Using DATABASE_URL from .env.staging"
    } else {
        Write-Output "No DATABASE_URL found in .env.staging - setting default for local Postgres"
        $default = 'postgresql://verity:veritypass@localhost:5432/verity_test'
        $env:DATABASE_URL = $default
    }
} 

docker compose -f $ComposeFile up -d

Write-Output "Waiting for Postgres to become available..."
for ($i = 0; $i -lt 30; $i++) {
    $res = docker run --rm --network host postgres:15 pg_isready -h localhost -p 5432 -U verity 2>&1
    if ($res -like '*accepting connections*') { Write-Output 'Postgres ready'; break }
    Start-Sleep -Seconds 2
}

Write-Output "Applying Alembic migrations against DATABASE_URL in .env.staging or environment"
python -c 'import os,sys; print("DATABASE_URL=" + str(os.environ.get("DATABASE_URL"))); sys.exit(0)'
python -m alembic -c python-tools/alembic.ini upgrade head

Write-Output "Staging Postgres setup complete."
