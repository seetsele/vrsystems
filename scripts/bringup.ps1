Param(
    [switch]$withDocker
)

# Bringup helper for local development (PowerShell)
Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

function Start-Static {
    Write-Output "Starting static server on port 3001..."
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m http.server 3001" -WorkingDirectory (Join-Path $root 'public')
}

function Start-Fallback {
    Write-Output "Starting fallback runner..."
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "python-tools\simple_test_api.py" -WorkingDirectory $root
}

function Start-FastAPI {
    Write-Output "Starting FastAPI runner on 8011..."
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn test_runner_server:app --host 127.0.0.1 --port 8011" -WorkingDirectory (Join-Path $root 'python-tools')
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
