cd 'C:\Users\lawm\Desktop\verity-systems\python-tools'
$proc = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*v10_test_suite.py*' }
if ($proc) {
  Write-Output ("v10_test_suite already running: " + ($proc.ProcessId))
} else {
  # Choose pwsh if available, else fall back to Windows PowerShell
  if (Get-Command pwsh -ErrorAction SilentlyContinue) { $shellPath = (Get-Command pwsh).Source; $shellArg = '-NoProfile' } 
  elseif (Get-Command powershell -ErrorAction SilentlyContinue) { $shellPath = (Get-Command powershell).Source; $shellArg = '-NoProfile' } 
  else { Write-Error 'No PowerShell executable found in PATH'; exit 1 }

  $cmd = "cd `"$PWD`"; python v10_test_suite.py > v10_test.log 2>&1"
  Start-Process -FilePath $shellPath -ArgumentList $shellArg,'-Command',$cmd -WindowStyle Hidden -PassThru | Out-Null
  Start-Sleep -Seconds 1
  Write-Output 'v10_test_suite started'
}
Get-ChildItem -Path v10_test.log -ErrorAction SilentlyContinue | Select-Object Name,Length
