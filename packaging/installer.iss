; Inno Setup script for the Windows installer.
; Build after PyInstaller, from the repo root:
;   iscc /DAppVersion=1.1.0 packaging\installer.iss

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F0D6C52-7B1E-4C6A-9A57-2B5B6E3B8C41}
AppName=Body Metrics
AppVersion={#AppVersion}
AppPublisher=slipx06
AppPublisherURL=https://github.com/slipx06/garmin-body-metrics
DefaultDirName={localappdata}\Programs\Body Metrics
DefaultGroupName=Body Metrics
DisableProgramGroupPage=yes
; Per-user install: no admin prompt.
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=BodyMetrics-Setup-{#AppVersion}
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\Body Metrics.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Close a running copy before upgrading.
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\Body Metrics\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Body Metrics"; Filename: "{app}\Body Metrics.exe"
Name: "{userdesktop}\Body Metrics"; Filename: "{app}\Body Metrics.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Body Metrics.exe"; Description: "Open Body Metrics now"; Flags: nowait postinstall skipifsilent
