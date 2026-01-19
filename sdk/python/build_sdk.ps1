Write-Output "Building Python SDK wheel in sdk/python..."
Set-Location sdk\python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Output 'python not found in PATH'; exit 1 }
python -m pip install --user --upgrade build
if ($LASTEXITCODE -ne 0) { Write-Output 'could not install build' }
python -m build
if ($LASTEXITCODE -ne 0) { Write-Output 'build failed' }
Write-Output "Python SDK build complete. Artifacts in sdk/python/dist/"
