<#
Install common development prerequisites on Windows using `winget`.
Usage: .\install_prereqs.ps1 [-InstallDocker]
This script will attempt to install (if not present):
 - Node.js (LTS)
 - Python 3
 - Google Chrome
 - Visual Studio Code
 - GitHub CLI
 - PowerShell (pwsh)
 - (optionally) Docker Desktop

It only uses `winget` and will prompt if `winget` is missing.
#>
param(
    [switch]$InstallDocker
)

function Check-Command($name) { return (Get-Command $name -ErrorAction SilentlyContinue) -ne $null }

if (-not (Check-Command winget)) {
    Write-Error "winget not found. Please install App Installer from the Microsoft Store or use another package manager."
    exit 1
}

$toInstall = @(
    @{id='OpenJS.NodeJS.LTS'; name='Node.js LTS'},
    @{id='Python.Python.3'; name='Python 3'},
    @{id='Google.Chrome'; name='Google Chrome'},
    @{id='Microsoft.VisualStudioCode'; name='Visual Studio Code'},
    @{id='GitHub.cli'; name='GitHub CLI'},
    @{id='Microsoft.PowerShell'; name='PowerShell (pwsh)'}
)

if ($InstallDocker) {
    $toInstall += @{id='Docker.DockerDesktop'; name='Docker Desktop'}
}

foreach ($pkg in $toInstall) {
    $id = $pkg.id
    $name = $pkg.name
    Write-Output "Checking $name..."
    $found = winget list --id $id 2>$null | Select-String $id
    if ($found) {
        Write-Output "  $name already installed (skipping)."
        continue
    }
    Write-Output "  Installing $name (winget id: $id)..."
    winget install --id $id -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { Write-Warning "  winget install returned non-zero for $name" }
}

Write-Output "Installation attempts complete. Please restart your terminal to pick up new PATH entries if any."