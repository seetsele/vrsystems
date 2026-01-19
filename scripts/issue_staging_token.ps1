param(
    [string]$Subject = 'staging-user',
    [string]$Scopes = 'verify',
    [int]$Expires = 3600
)

if (-not (Test-Path '.env.staging')) {
    Write-Output ".env.staging not found; please copy env.staging.example -> .env.staging and set TOKEN_SECRET"
    exit 1
}

Write-Output "Loading .env.staging and issuing token..."
Get-Content .env.staging | ForEach-Object {
    if ($_ -match '^TOKEN_SECRET=(.*)') { $env:TOKEN_SECRET = $Matches[1] }
}

python python-tools/token_cli.py --subject $Subject --scopes $Scopes --expires $Expires
