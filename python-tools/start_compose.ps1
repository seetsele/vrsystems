param(
    [string]$ComposeFile = "docker-compose.yml"
)

function Check-Command($name){
    return (Get-Command $name -ErrorAction SilentlyContinue) -ne $null
}

if (-not (Check-Command docker)){
    Write-Error "Docker is not available. Install Docker Desktop and try again."
    exit 1
}

$root = (Resolve-Path "$(Join-Path $PSScriptRoot '..')").Path
Push-Location $root

# Resolve compose file path relative to repo root
$composePath = Join-Path $root $ComposeFile
if (-not (Test-Path $composePath)) {
    Write-Warning "Compose file not found at $composePath; falling back to provided path: $ComposeFile"
    $composePath = $ComposeFile
}

Write-Output "Starting compose from $composePath..."
docker compose -f $composePath up -d

Write-Output "Waiting for services to become healthy (timeout 120s)..."
$deadline = (Get-Date).AddSeconds(120)

function Wait-Url($url){
    while ((Get-Date) -lt $deadline) {
        try{
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400){ Write-Output "$url OK"; return $true }
        }catch{}
        Start-Sleep -Seconds 3
    }
    Write-Warning "$url did not respond in time"
    return $false
}

$ok = $true
$ok = Wait-Url 'http://127.0.0.1:8010/prometheus' -and $ok
$ok = Wait-Url 'http://127.0.0.1:3001/tests/runner.html' -and $ok
$ok = Wait-Url 'http://127.0.0.1:9090/-/ready' -or Wait-Url 'http://127.0.0.1:9090' -and $ok
$ok = Wait-Url 'http://127.0.0.1:3000' -and $ok

if ($ok){
    Write-Output 'Compose stack appears up. Grafana: http://localhost:3000 (admin/admin)'
    # Attempt to import Grafana dashboard automatically if present
    $grafanaDash = Join-Path $root 'python-tools\grafana\test_runner_dashboard.json'
    if (Test-Path $grafanaDash) {
        try{
            Write-Output 'Importing Grafana dashboard...'
            python "$root\python-tools\grafana\import_dashboard.py" $grafanaDash
            Write-Output 'Grafana dashboard import attempted.'
        } catch {
            Write-Warning "Grafana import failed: $_"
        }
    }
    Pop-Location; exit 0
}
Write-Warning 'One or more services failed to respond; check `docker compose ps` and logs.'
Pop-Location
exit 2
