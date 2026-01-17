Write-Output "Code signing / notarization placeholder script"
Write-Output "This script is a template. Fill in code-signing identity and key details before using."

if (-not (Test-Path -Path .\build)) {
    Write-Output "No build directory found. Run your build process first."
    exit 1
}

Write-Output "Signing artifacts in .\build... (placeholder)"
Write-Output "Use `codesign` on macOS and signtool on Windows in CI with secured secrets."
