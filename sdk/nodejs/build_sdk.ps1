Write-Output "Packing Node SDK in sdk/nodejs..."
Set-Location sdk\nodejs
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Write-Output 'npm not found in PATH'; exit 1 }
npm install --no-audit --no-fund
npm pack
Write-Output "Node SDK pack complete. Tarball in sdk/nodejs/"
