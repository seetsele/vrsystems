<#
Simple health-check & auto-restart helper (PowerShell)

Usage:
  .\scripts\ensure_apis_up.ps1 -ConfigFile .\scripts\apis-to-monitor.json -IntervalSeconds 60

What it does:
  - Reads a JSON file with endpoints and optional restart commands
  - Pings each endpoint periodically
  - If an endpoint fails repeatedly, executes a configured restart command and logs the event

Notes:
  - This is a local helper for dev / small deployments. For production use, prefer a real process manager (systemd/PM2/Docker) and an external uptime monitor.
#>

param(
  [string]$ConfigFile = "scripts\apis-to-monitor.json",
  [int]$IntervalSeconds = 60,
  [int]$FailThreshold = 3
)

function Load-Json($path) {
  if (-Not (Test-Path $path)) { throw "Config file not found: $path" }
  Get-Content $path -Raw | ConvertFrom-Json
}

try {
  $cfg = Load-Json $ConfigFile
} catch {
  Write-Error "Failed to load config: $_"
  exit 2
}

Write-Output "Monitoring $($cfg.endpoints.Count) endpoints every $IntervalSeconds seconds. Press Ctrl+C to stop."

# state: dictionary of url -> consecutiveFails
$state = @{}
foreach ($e in $cfg.endpoints) { $state[$e.url] = 0 }

while ($true) {
  foreach ($e in $cfg.endpoints) {
    try {
      $r = Invoke-WebRequest -Uri $e.url -UseBasicParsing -Method GET -TimeoutSec 10 -ErrorAction Stop
      if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
        if ($state[$e.url] -ne 0) { Write-Output "OK: $($e.name) [$($e.url)] recovered" }
        $state[$e.url] = 0
        continue
      } else {
        throw "Status $($r.StatusCode)"
      }
    } catch {
      $state[$e.url] = $state[$e.url] + 1
      Write-Warning "Endpoint failure ($($state[$e.url])/$FailThreshold): $($e.name) [$($e.url)] - $_"
      if ($state[$e.url] -ge $FailThreshold) {
        Write-Error "Threshold reached for $($e.name). Executing recovery actions..."
        if ($e.restartCommand) {
          try {
            Write-Output "Running restart command: $($e.restartCommand)"
            Invoke-Expression $e.restartCommand
            Start-Sleep -Seconds 5
          } catch {
            Write-Error "Restart command failed: $_"
          }
        } else {
          Write-Warning "No restartCommand configured for $($e.name)."
        }
        # Reset counter to avoid repeated restarts
        $state[$e.url] = 0
      }
    }
  }

  Start-Sleep -Seconds $IntervalSeconds
}
