Write-Output 'Starting local infra via docker-compose (Redis, Qdrant, Postgres, MinIO)'
Set-Location "$PSScriptRoot\..\python-tools\infra"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose up -d
} else {
    Write-Output 'Docker not installed or not in PATH. Please install Docker to start infra.'
}
