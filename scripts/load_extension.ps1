# Load Chrome with the unpacked extension (Windows)
param(
    [string]$ExtensionPath = "$(Resolve-Path "$PSScriptRoot\..\browser-extension\chrome").Path"
)

# Find Chrome executable
$possible = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe")
$chrome = $possible | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { Write-Error "Chrome not found. Open chrome://extensions and 'Load unpacked' manually."; exit 1 }

Write-Output "Launching Chrome with extension loaded from: $ExtensionPath"
Start-Process -FilePath $chrome -ArgumentList "--load-extension=$ExtensionPath" -NoNewWindow
