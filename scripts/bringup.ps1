Param(
    [switch]$withDocker
)

# Bringup helper for local development (PowerShell)
Set-StrictMode -Version Latest
# Determine repository root (one level above the scripts directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$root = Resolve-Path (Join-Path $scriptDir '..') | Select-Object -ExpandProperty Path
Set-Location $root

# Resolve python-tools path early so multiple functions can use it
if (Test-Path (Join-Path $root 'python-tools')) {
    $pythonToolsDir = (Resolve-Path (Join-Path $root 'python-tools')).Path
} else {
    $pythonToolsDir = $null
}

function Start-Static {
    Write-Output "Starting static server on port 3001..."
    $publicDir = (Resolve-Path (Join-Path $root 'public') -ErrorAction SilentlyContinue)
    if ($publicDir) {
        $publicPath = $publicDir.Path
        Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m http.server 3001" -WorkingDirectory $publicPath
    } else {
        Write-Output "public directory not found; skipping static server start."
    }
}

function Start-Fallback {
    Write-Output "Starting fallback runner..."
    if (-not $pythonToolsDir) { Write-Output "python-tools folder not found; skipping fallback runner."; return }
    $fallbackScript = Join-Path $pythonToolsDir 'simple_test_api.py'
    if (Test-Path $fallbackScript) {
        Start-Process -NoNewWindow -FilePath "python" -ArgumentList "$fallbackScript" -WorkingDirectory $pythonToolsDir
    } else {
        Write-Output "Fallback script not found: $fallbackScript"
    }
}

function Start-FastAPI {
    Write-Output "Starting FastAPI runner on 8011..."
    if (-not $pythonToolsDir) { Write-Output "python-tools folder not found; skipping FastAPI runner."; return }
    $fastApiModule = Join-Path $pythonToolsDir 'test_runner_server.py'
    if (Test-Path $fastApiModule) {
        Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn test_runner_server:app --host 127.0.0.1 --port 8011" -WorkingDirectory $pythonToolsDir
    } else {
        Write-Output "FastAPI module not found in python-tools; skipping FastAPI start."
    }
}

if ($withDocker) {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Output "Docker detected. Starting compose stack..."
        Set-Location (Join-Path $root 'python-tools')
        & .\start_compose.ps1
        return
    } else {
        Write-Output "Docker not found; falling back to local services."
    }
}

Start-Static
Start-Fallback
Start-FastAPI
Write-Output "Bringup complete. Static: http://127.0.0.1:3001, FastAPI: http://127.0.0.1:8011"
