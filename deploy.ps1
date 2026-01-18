# ============================================================================
# VERITY SYSTEMS - DEPLOYMENT SCRIPT
# ============================================================================
# Run this script to deploy everything locally for testing
# Usage: .\deploy.ps1 [-Production] [-SkipAPI] [-SkipWeb]

param(
    [switch]$Production,
    [switch]$SkipAPI,
    [switch]$SkipWeb,
    [switch]$Deploy
)

$ErrorActionPreference = "Stop"
$ROOT = $PSScriptRoot
if (-not $ROOT) { $ROOT = (Get-Location).Path }

# Colors
function Write-Success { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "  [INFO] $msg" -ForegroundColor Yellow }
function Write-Step { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   VERITY SYSTEMS - DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# CHECK PREREQUISITES
# ============================================================================
Write-Step "Checking Prerequisites"

# Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python: $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.10+"
    exit 1
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Success "Node.js: $nodeVersion"
} catch {
    Write-Error "Node.js not found. Please install Node.js 18+"
    exit 1
}

# ============================================================================
# KILL EXISTING PROCESSES
# ============================================================================
Write-Step "Cleaning Up Existing Processes"

# Kill Python processes on our ports
$ports = @(8081, 3000, 8085)
    foreach ($port in $ports) {
    $process = netstat -ano | Select-String ":$port " | Select-Object -First 1
    if ($process) {
        $foundPid = ($process -split '\s+')[-1]
        if ($foundPid -match '^\d+$') {
            try {
                Stop-Process -Id $foundPid -Force -ErrorAction SilentlyContinue
                Write-Info "Killed process on port $port (PID: $foundPid)"
            } catch {}
        }
    }
}

Start-Sleep -Seconds 2

# ============================================================================
# START API SERVER
# ============================================================================
if (-not $SkipAPI) {
    Write-Step "Starting API Server"
    
    $envFile = if ($Production) { ".env.production" } else { ".env" }
    Write-Info "Using environment: $envFile"
    
    Push-Location "$ROOT\python-tools"
    
    # Copy production env if exists
    if ($Production -and (Test-Path ".env.production")) {
        Copy-Item ".env.production" ".env" -Force
        Write-Info "Loaded production environment"
    }
    
    # Start API in background
    $apiProcess = Start-Process python -ArgumentList "api_server_production.py" -PassThru -WindowStyle Hidden
    Write-Success "API Server starting (PID: $($apiProcess.Id))"
    
    Pop-Location
    
    # Wait for API to be ready
    Write-Info "Waiting for API to be ready..."
    $maxAttempts = 30
    $attempt = 0
    $apiReady = $false
    
    while ($attempt -lt $maxAttempts -and -not $apiReady) {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8081/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.status -eq "healthy") {
                $apiReady = $true
            }
        } catch {}
        $attempt++
    }
    
    if ($apiReady) {
        Write-Success "API Server ready at http://localhost:8081"
    } else {
        Write-Error "API Server failed to start"
    }
}

# ============================================================================
# START WEB SERVER
# ============================================================================
if (-not $SkipWeb) {
    Write-Step "Starting Web Server"
    
    Push-Location "$ROOT\public"
    
    # Start web server in background
    $webProcess = Start-Process python -ArgumentList "-m http.server 3000" -PassThru -WindowStyle Hidden
    Write-Success "Web Server starting (PID: $($webProcess.Id))"
    
    Pop-Location
    
    Start-Sleep -Seconds 2
    Write-Success "Web Server ready at http://localhost:3000"
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "         DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

if (-not $SkipAPI) {
    Write-Host "  API Server:     http://localhost:8081" -ForegroundColor White
    Write-Host "  API Docs:       http://localhost:8081/docs" -ForegroundColor White
}
if (-not $SkipWeb) {
    Write-Host "  Website:        http://localhost:3000" -ForegroundColor White
    Write-Host "  Verify Page:    http://localhost:3000/verify.html" -ForegroundColor White
}

Write-Host ""
Write-Host "  Production API Keys:" -ForegroundColor Yellow
Write-Host "    - PiLl66YdclgQCwEQFwp7rB5Diw3xDpvJi2cR709TNkA" -ForegroundColor DarkGray
Write-Host "    - TTIyLVvtam6Wq6WbSXfdMFxaBDQI6jSNLQsu0BzCzoY" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  Quick Test:" -ForegroundColor Yellow
Write-Host "    curl http://localhost:8081/health" -ForegroundColor DarkGray
Write-Host ""

# ============================================================================
# OPEN BROWSER (optional)
# ============================================================================
if (-not $SkipWeb) {
    Start-Process "http://localhost:3000"
    Start-Process "http://localhost:8081/docs"
}

# ============================================================================
# CLOUD DEPLOYMENT INFO
# ============================================================================
Write-Host ""
Write-Host "  PRODUCTION DEPLOYMENT:" -ForegroundColor Cyan
Write-Host "  ----------------------" -ForegroundColor Cyan
Write-Host "  1. Deploy API: railway up (in python-tools folder)" -ForegroundColor White
Write-Host "  2. Point DNS: api.verity.systems -> Railway URL" -ForegroundColor White
Write-Host "  3. Deploy Web: vercel (in root folder)" -ForegroundColor White
Write-Host "  4. SSL: Auto-provisioned by Railway/Vercel" -ForegroundColor White
Write-Host ""
Write-Host "  See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow
Write-Host ""