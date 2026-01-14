# Launch all apps locally: Desktop (Electron), PWA (http-server), Mobile (Expo), open Chrome Extensions
param(
    [switch]$OpenChromeExtensions
)

# Start PWA server
Write-Output "Starting PWA server on port 3001..."
if (Get-Command pwsh -ErrorAction SilentlyContinue) { $psExec = 'pwsh' } else { $psExec = 'powershell' }
$publicPath = (Resolve-Path (Join-Path $PSScriptRoot '..\public')).Path
Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$publicPath'; npx http-server -p 3001") -WindowStyle Hidden

# Start Electron (desktop app)
Write-Output "Starting Verity desktop (Electron)..."
$desktopPath = (Resolve-Path (Join-Path $PSScriptRoot '..\desktop-app')).Path
Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$desktopPath'; npx electron .") -WindowStyle Hidden

# Start Expo (mobile)
Write-Output "Starting Expo dev server for mobile app..."
$mobilePath = (Resolve-Path (Join-Path $PSScriptRoot '..\verity-mobile')).Path
Start-Process -FilePath $psExec -ArgumentList @("-NoProfile","-Command","cd '$mobilePath'; npx expo start --tunnel") -WindowStyle Hidden

if ($OpenChromeExtensions) {
    Write-Output "Opening Chrome extensions page (please load unpacked extension from browser-extension/chrome)..."
    # Try to find Chrome executable and open the extensions page, fallback to opening the page in default browser
    $possible = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe")
    $chrome = $possible | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($chrome) {
        Start-Process -FilePath $chrome -ArgumentList "--new-window","chrome://extensions/"
    } else {
        Write-Output "Chrome not found; opening default browser to the extensions URL."
        Start-Process "https://www.google.com/chrome/" # direct users to install Chrome
    }
}

Write-Output "Launch commands initiated. Check terminals for logs and press CTRL+C in the terminal windows to stop servers."