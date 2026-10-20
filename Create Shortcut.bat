@echo off
rem Creates a "Body Metrics" shortcut on the desktop that starts the app.
set "DIR=%~dp0"
set "DIR=%DIR:~0,-1%"
powershell -NoProfile -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$lnk = Join-Path $desktop 'Body Metrics.lnk';" ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk);" ^
  "$s.TargetPath = '%DIR%\Body Metrics.bat';" ^
  "$s.WorkingDirectory = '%DIR%';" ^
  "$s.WindowStyle = 7;" ^
  "$s.IconLocation = '%DIR%\icon.ico,0';" ^
  "$s.Description = 'Enter body metrics into Garmin Connect';" ^
  "$s.Save();" ^
  "Write-Host ('Shortcut created: ' + $lnk)"
pause
