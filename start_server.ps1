# Verity API Server Startup Script
$ErrorActionPreference = "Continue"

Write-Host "Starting Verity API Server..." -ForegroundColor Green

# Set environment
$env:PYTHONPATH = "c:\Users\lawm\Desktop\verity-systems;c:\Users\lawm\Desktop\verity-systems\python-tools"

# Change to project root
Set-Location c:\Users\lawm\Desktop\verity-systems

# Start server
& "c:\Users\lawm\Desktop\verity-systems\.venv311\Scripts\python.exe" -m uvicorn python-tools.api_server_v10:app --host 0.0.0.0 --port 8000

Write-Host "Server stopped." -ForegroundColor Yellow
