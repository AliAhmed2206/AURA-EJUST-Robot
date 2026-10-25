$swPath = "C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"
$p = Start-Process -FilePath $swPath -PassThru
Start-Sleep -Seconds 5
Write-Output "PID: $($p.Id), HasExited: $($p.HasExited), ExitCode: $($p.ExitCode)"
