param(
    [string]$ComposeFile = "docker-compose.yml",
    [int]$MaxAttempts = 4
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

for ($attempt=1; $attempt -le $MaxAttempts; $attempt++) {
    Write-Output "Attempt $attempt of ${MaxAttempts}: starting compose (pull missing images)..."
    try {
        docker compose -f $composePath up -d --pull=missing
        if ($LASTEXITCODE -eq 0) { Write-Output "docker compose succeeded"; break }
    } catch {
        Write-Warning "docker compose attempt $attempt failed: $_"
    }
    if ($attempt -lt $MaxAttempts) {
        $wait = [math]::Min(30, [math]::Pow(2, $attempt) * 2)
        Write-Output "Waiting $wait seconds before retrying..."
        Start-Sleep -Seconds $wait
    }
}

if ($attempt -gt $MaxAttempts) {
    Write-Error "docker compose failed after ${MaxAttempts} attempts"
    Pop-Location; exit 2
}

Write-Output "Compose started; delegating to existing start_compose.ps1 for healthchecks."
& (Join-Path $root 'python-tools\start_compose.ps1') -ComposeFile $ComposeFile
Pop-Location