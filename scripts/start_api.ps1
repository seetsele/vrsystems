# Start the Verity API v10 (ensures python-tools on PYTHONPATH)
$env:PYTHONPATH = Join-Path $PSScriptRoot '..\python-tools'
Push-Location -Path (Join-Path $PSScriptRoot '..\python-tools')
Write-Output "Starting uvicorn with PYTHONPATH=$env:PYTHONPATH"
# Start uvicorn as a detached process so it keeps running after this script exits
$uvicornArgs = '-m uvicorn api_server_v10:app --host 127.0.0.1 --port 8001 --log-level info'
Start-Process -FilePath (Get-Command python).Source -ArgumentList $uvicornArgs -WorkingDirectory $env:PYTHONPATH -NoNewWindow -PassThru | Out-Null
Write-Output 'Uvicorn started (detached).'
Pop-Location
