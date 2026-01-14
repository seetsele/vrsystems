# Stop local servers started by launch_local.ps1
param()

$names = @('electron','node','http-server','expo','ngrok','python')
foreach ($n in $names) {
    Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Output "Stopping process $($_.ProcessName) Id=$($_.Id)"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}
Write-Output "Stop commands issued. Verify with Get-Process."