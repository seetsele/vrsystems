# Create a Windows Scheduled Task to run the provider monitor every 5 minutes
# Usage (run in an elevated PowerShell if necessary):
#   .\create_windows_task.ps1 -PathToScript 'C:\Users\lawm\Desktop\verity-systems\python-tools\monitor_providers.py'
param(
    [string]$PathToScript = "C:\Users\lawm\Desktop\verity-systems\python-tools\monitor_providers.py",
    [string]$TaskName = "VerityProviderMonitor"
)

# Build a properly escaped command string for schtasks. Use single-quoted PowerShell literal
# so we can include inner double-quotes for the command to run.
$action = 'powershell -NoProfile -WindowStyle Hidden -Command "python ''{0}''"' -f $PathToScript
schtasks /Create /SC MINUTE /MO 5 /TN $TaskName /TR $action /F | Out-Null
Write-Output "Scheduled task '$TaskName' created to run $PathToScript every 5 minutes."