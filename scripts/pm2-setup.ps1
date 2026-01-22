param(
  [string]$EcosystemPath = "$(Resolve-Path "$PSScriptRoot\..\desktop-app\ecosystem.config.js").Path"
)

Write-Output "Setting up PM2 to run desktop-app ecosystem from: $EcosystemPath"

# install pm2 globally if missing
try {
  npm ls -g pm2 --depth=0 > $null 2>&1
} catch {
  Write-Output "Installing pm2 globally..."
  npm i -g pm2
}

pm2 start $EcosystemPath
pm2 save
Write-Output "PM2 started and saved. Use 'pm2 status' to view processes."
