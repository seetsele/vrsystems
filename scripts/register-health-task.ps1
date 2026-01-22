param(
  [string]$TaskName = 'VerityApiHealthCheck',
  [string]$ScriptPath = "$(Resolve-Path "$PSScriptRoot\ensure_apis_up.ps1").Path",
  [int]$IntervalMinutes = 5
)

Write-Output "Registering scheduled task '$TaskName' to run health-check every $IntervalMinutes minutes"

$action = "PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

# create a trigger to run at logon and repeat
$xml = @"
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>PowerShell.exe</Command>
      <Arguments>-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`"</Arguments>
    </Exec>
  </Actions>
</Task>
"@

$tmp = [IO.Path]::GetTempFileName()
Set-Content -Path $tmp -Value $xml -Encoding UTF8

try {
  schtasks /Create /TN $TaskName /XML $tmp /F | Out-Null
  Write-Output "Scheduled task created: $TaskName"
} catch {
  Write-Error "Failed to create scheduled task: $_"
} finally {
  Remove-Item $tmp -ErrorAction SilentlyContinue
}
