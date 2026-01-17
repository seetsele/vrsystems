$out = 'C:\Users\lawm\Desktop\verity-systems\python-tools\v10_test_report.json'
$elapsed = 0
$timeout = 600  # 10 minutes
while ($elapsed -lt $timeout -and -not (Test-Path $out)) {
  Write-Output ("waiting for report... ${elapsed}s")
  Start-Sleep -Seconds 10
  $elapsed += 10
}
if (Test-Path $out) {
  Write-Output 'REPORT_FOUND'
  Get-Content -Path $out -Raw
} else {
  Write-Output 'REPORT_TIMEOUT'
}
