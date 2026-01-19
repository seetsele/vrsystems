Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$rect = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($rect.Width, $rect.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rect.Location, [System.Drawing.Point]::Empty, $rect.Size)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$path1 = "C:\Users\lawm\Desktop\verity-systems\screenshots\verify_full_$timestamp.png"
$bmp.Save($path1,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Output "screenshot_saved: $path1"
