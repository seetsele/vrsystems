cd 'C:\Users\lawm\Desktop\verity-systems\python-tools'
$proc = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*v10_test_suite.py*' }
if ($proc) {
  Write-Output ("v10_test_suite already running: " + ($proc.ProcessId))
} else {
  Start-Process -FilePath pwsh -ArgumentList '-NoProfile','-Command','cd "C:\\Users\\lawm\\Desktop\\verity-systems\\python-tools"; python v10_test_suite.py > v10_test.log 2>&1' -WindowStyle Hidden
  Start-Sleep -Seconds 1
  Write-Output 'v10_test_suite started'
}
Get-ChildItem -Path v10_test.log -ErrorAction SilentlyContinue | Select-Object Name,Length
