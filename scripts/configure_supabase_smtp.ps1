# Supabase SMTP configuration helper (PowerShell template)
# This file is a safe, non-destructive template. Fill env vars and uncomment
# the command blocks you intend to use.

Write-Output "Supabase SMTP configuration helper (template)."
Write-Output "Ensure you have the service key and project ref before proceeding."

Write-Output "Examples (commented):"

# Using supabase CLI (recommended):
# supabase login
# supabase projects env set SMTP_HOST $env:SMTP_HOST --project $env:SUPABASE_PROJECT_REF
# supabase projects env set SMTP_PORT $env:SMTP_PORT --project $env:SUPABASE_PROJECT_REF
# supabase projects env set SMTP_USER $env:SMTP_USER --project $env:SUPABASE_PROJECT_REF
# supabase projects env set SMTP_PASS $env:SMTP_PASS --project $env:SUPABASE_PROJECT_REF
# supabase projects env set SMTP_FROM $env:SMTP_FROM --project $env:SUPABASE_PROJECT_REF

# Using a management API via Invoke-RestMethod (replace endpoint as needed):
# $body = @{ smtp_host = $env:SMTP_HOST; smtp_port = [int]$env:SMTP_PORT; smtp_user = $env:SMTP_USER; smtp_pass = $env:SMTP_PASS; smtp_from = $env:SMTP_FROM } | ConvertTo-Json
# Invoke-RestMethod -Method Patch -Uri "https://api.supabase.com/v1/projects/$($env:SUPABASE_PROJECT_REF)/settings/email" -Headers @{Authorization = "Bearer $($env:SUPABASE_SERVICE_KEY)"; 'Content-Type' = 'application/json'} -Body $body

Write-Output "Template created. Edit and uncomment the command you want to use."
