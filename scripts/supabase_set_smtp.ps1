Write-Output "Supabase SMTP setter (PowerShell template)."

if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
    Write-Error "supabase CLI not found. Install it: https://supabase.com/docs/guides/cli"
    exit 1
}

if (Test-Path -Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -and -not $_.StartsWith('#')) {
            $parts = $_ -split '='; Set-Item -Path Env:$($parts[0]) -Value ($parts[1] -join '=')
        }
    }
}

if (-not $env:SUPABASE_PROJECT_REF) { Write-Error 'Please set SUPABASE_PROJECT_REF in .env or environment'; exit 1 }
if (-not $env:SMTP_HOST) { Write-Error 'Please set SMTP_HOST'; exit 1 }
if (-not $env:SMTP_PORT) { Write-Error 'Please set SMTP_PORT'; exit 1 }
if (-not $env:SMTP_USER) { Write-Error 'Please set SMTP_USER'; exit 1 }
if (-not $env:SMTP_PASS) { Write-Error 'Please set SMTP_PASS'; exit 1 }
if (-not $env:SMTP_FROM) { Write-Error 'Please set SMTP_FROM'; exit 1 }

Write-Output "About to set SMTP env vars for Supabase project: $env:SUPABASE_PROJECT_REF"
$c = Read-Host 'Continue? (y/N)'
if ($c -ne 'y' -and $c -ne 'Y') { Write-Output 'Aborting.'; exit 0 }

supabase projects env set SMTP_HOST $env:SMTP_HOST --project $env:SUPABASE_PROJECT_REF
supabase projects env set SMTP_PORT $env:SMTP_PORT --project $env:SUPABASE_PROJECT_REF
supabase projects env set SMTP_USER $env:SMTP_USER --project $env:SUPABASE_PROJECT_REF
supabase projects env set SMTP_PASS $env:SMTP_PASS --project $env:SUPABASE_PROJECT_REF
supabase projects env set SMTP_FROM $env:SMTP_FROM --project $env:SUPABASE_PROJECT_REF

Write-Output "Done. Verify settings in Supabase dashboard and run signup smoke tests."
