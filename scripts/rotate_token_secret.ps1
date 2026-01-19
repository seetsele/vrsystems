param(
    [string]$EnvFile = '.env.staging',
    [int]$SecretBytes = 32
)

Write-Output "Generating new TOKEN_SECRET..."
$rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
$bytes = New-Object byte[] $SecretBytes
$rng.GetBytes($bytes)
$rnd = [System.Convert]::ToBase64String($bytes)
Write-Output "New secret (base64): [REDACTED]"

if (Test-Path $EnvFile) {
    (Get-Content $EnvFile) -replace 'TOKEN_SECRET=.*', "TOKEN_SECRET=$rnd" | Set-Content $EnvFile
    Write-Output "Updated $EnvFile with new TOKEN_SECRET (do NOT commit this file)."
} else {
    Write-Output "Creating $EnvFile with new TOKEN_SECRET (do NOT commit this file)."
    "TOKEN_SECRET=$rnd" | Out-File -FilePath $EnvFile -Encoding utf8
}

Write-Output "Next steps: deploy the new secret to staging instances and run the overlap acceptance period. See docs/TOKEN_ROTATION.md for details."
