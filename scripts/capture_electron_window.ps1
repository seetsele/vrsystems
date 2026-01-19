Add-Type @"
using System;
using System.Runtime.InteropServices;
public class User32 {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
}
"@

function Get-ElectronWindowHandle {
    $proc = Get-Process | Where-Object { ($_.ProcessName -like 'electron*' -or $_.ProcessName -eq 'electron') -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($proc) { return $proc.MainWindowHandle }
    # fallback: try any process with a visible window title mentioning Verity
    $proc = Get-Process | Where-Object { $_.MainWindowTitle -match 'Verity' } | Select-Object -First 1
    if ($proc) { return $proc.MainWindowHandle }
    return [IntPtr]::Zero
}

$hwnd = Get-ElectronWindowHandle
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Output "no_electron_window_found"
    exit 1
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$userRect = New-Object User32+RECT
[User32]::GetWindowRect($hwnd, [ref]$userRect) | Out-Null
$left = $userRect.Left
$top = $userRect.Top
$width = $userRect.Right - $userRect.Left
$height = $userRect.Bottom - $userRect.Top

if ($width -le 0 -or $height -le 0) {
    Write-Output "invalid_window_rect"
    exit 1
}

$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen([System.Drawing.Point]::new($left, $top), [System.Drawing.Point]::Empty, [System.Drawing.Size]::new($width, $height))

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$path = "C:\Users\lawm\Desktop\verity-systems\screenshots\verify_window_$timestamp.png"
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Output "screenshot_saved: $path"
