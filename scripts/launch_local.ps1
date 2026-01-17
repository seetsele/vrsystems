# Launch all apps locally: Desktop (Electron), PWA (http-server), Mobile (Expo), open Chrome Extensions
param(
    [switch]$OpenChromeExtensions,
    [string]$TestRunnerApiKey = '',
    [switch]$SkipElectron,
    [switch]$SkipExpo
)

# choose pwsh if available
if (Get-Command pwsh -ErrorAction SilentlyContinue) { $psExec = 'pwsh' } else { $psExec = 'powershell' }

Write-Output "Starting PWA static server on port 3001..."
$publicPath = (Resolve-Path (Join-Path $PSScriptRoot '..\public')).Path
Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$publicPath'; python -m http.server 3001 --bind 127.0.0.1") -WindowStyle Hidden

# Start test-runner: prefer FastAPI (`test_runner_server.py`) when port available, else fallback to simple HTTP runner
$pythonTools = (Resolve-Path (Join-Path $PSScriptRoot '..\python-tools')).Path
if (Test-Path $pythonTools) {
    # check port 8010
    $portFree = $true
    try {
        $nc = Test-NetConnection -ComputerName 127.0.0.1 -Port 8010 -WarningAction SilentlyContinue
        if ($nc -and $nc.TcpTestSucceeded) { $portFree = $false }
    } catch { $portFree = $true }

    if ($portFree) {
        Write-Output "Port 8010 appears free; attempting to start FastAPI runner (test_runner_server.py)..."
        # detect python executable
        if (Get-Command python -ErrorAction SilentlyContinue) {
            $pyCmd = 'python'
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            $pyCmd = 'py'
        } else {
            $pyCmd = 'python'
        }
        if ($TestRunnerApiKey -ne '') { $envAssign = "`$env:TEST_RUNNER_API_KEY='$TestRunnerApiKey'; " } else { $envAssign = "" }
        # set PYTHONPATH to include python-tools to avoid import issues
        $cmdFast = "cd '$pythonTools'; $envAssign `$env:PYTHONPATH='$pythonTools'; $pyCmd -m uvicorn test_runner_server:app --host 127.0.0.1 --port 8010 --log-level info *> '$pythonTools\test_runner.log' 2>&1"
        $proc = Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command",$cmdFast) -WindowStyle Hidden -PassThru
        # wait and probe /docs for up to 15 seconds
        Start-Sleep -Seconds 1
        $ready = $false
        for ($i=0; $i -lt 15; $i++){
            try {
                $r = Invoke-RestMethod -Uri 'http://127.0.0.1:8010/docs' -Method GET -TimeoutSec 2 -ErrorAction Stop
                $ready = $true; break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        if ($ready) {
            Write-Output "FastAPI runner started on port 8010. Logs: $pythonTools\test_runner.log"
        } else {
            Write-Output "FastAPI runner did not respond; falling back to simple_test_api.py. Check logs: $pythonTools\test_runner.log"
            try { $proc.Kill() } catch { }
            $portFree = $false
        }
    } else {
        Write-Output "Port 8010 already in use; will start simple_test_api.py as fallback."
    }

    if (-not $portFree) {
        Write-Output "Starting simple test runner (python-tools/simple_test_api.py) on port 8010..."
        if ($TestRunnerApiKey -ne '') { $envPart = "`$env:TEST_RUNNER_API_KEY='$TestRunnerApiKey'; " } else { $envPart = "" }
        $cmd = "cd '$pythonTools'; $envPart python simple_test_api.py"
        Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command",$cmd) -WindowStyle Hidden
        Start-Sleep -Seconds 1
    }
} else {
    Write-Output "python-tools folder not found; skipping test runner start."
}

if (-not $SkipElectron) {
    Write-Output "Starting Verity desktop (Electron)..."
    $desktopPath = (Resolve-Path (Join-Path $PSScriptRoot '..\desktop-app')).Path
    Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$desktopPath'; npx electron .") -WindowStyle Hidden
} else {
    Write-Output "Skipping Electron start (SkipElectron set)."
}

if (-not $SkipExpo) {
    Write-Output "Starting Expo dev server for mobile app..."
    $mobilePath = (Resolve-Path (Join-Path $PSScriptRoot '..\verity-mobile')).Path
    Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$mobilePath'; npx expo start --tunnel") -WindowStyle Hidden
} else {
    Write-Output "Skipping Expo start (SkipExpo set)."
}

Start-Sleep -Seconds 2

# Open runner UI (include key as query param if provided)
$runnerUrl = 'http://127.0.0.1:3001/tests/runner.html'
if ($TestRunnerApiKey -ne '') { $runnerUrl = $runnerUrl + '?key=' + [System.Uri]::EscapeDataString($TestRunnerApiKey) }
Write-Output "Opening runner UI: $runnerUrl"
Start-Process $runnerUrl

if ($OpenChromeExtensions) {
    Write-Output "Opening Chrome extensions page (please load unpacked extension from browser-extension/chrome)..."
    $possible = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe")
    $chrome = $possible | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($chrome) {
        Start-Process -FilePath $chrome -ArgumentList "--new-window","chrome://extensions/"
    } else {
        Start-Process "https://www.google.com/chrome/"
    }
}

Write-Output "Launch commands initiated. Check terminals for logs and press CTRL+C to stop servers."