; Inno Setup Installer Script for Auto Test Executor
; Auto Test Platform - Executor Client Installer

[Setup]
AppName=Auto Test Executor
AppVersion=1.0.0
AppPublisher=Auto Test Platform
DefaultDirName={commonpf}\AutoTestExecutor
DefaultGroupName=Auto Test Platform
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=AutoTestExecutor-Setup-v1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable and all dependencies from PyInstaller bundle
Source: "dist\AutoTestExecutor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ARCHITECTURE.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Auto Test Executor"; Filename: "{app}\AutoTestExecutor.exe"
Name: "{group}\Uninstall Auto Test Executor"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Auto Test Executor"; Filename: "{app}\AutoTestExecutor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AutoTestExecutor.exe"; Description: "Launch Auto Test Executor"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{userappdata}\AutoTestExecutor"
