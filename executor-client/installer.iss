; 自动化测试执行机 安装程序
; AutoTest Executor Installer

#define AppName "自动化测试执行机"
#define AppNameEn "AutoTest Executor"
#define AppVersion "1.0.0"
#define AppPublisher "AutoTest Platform"
#define AppExeName "AutoTestExecutor.exe"

[Setup]
; 安装程序基本信息
AppId={{A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\AutoTestExecutor
DefaultGroupName={#AppName}
AllowNoIcons=yes
; 输出文件名
OutputDir=dist
OutputBaseFilename=AutoTestExecutor_Setup
; 压缩设置
Compression=lzma2
SolidCompression=yes
; 安装程序外观
WizardStyle=modern
; 权限要求
PrivilegesRequired=admin
; 卸载程序
UninstallDisplayIcon={app}\{#AppExeName}

; 不使用多语言，使用默认
; [Languages]
; Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
; Name: "english"; MessagesFile: "compiler:Languages\English.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked

[Files]
; 主程序和所有文件
Source: "dist\AutoTestExecutor\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\AutoTestExecutor\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\AutoTestExecutor\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\卸载"; Filename: "{uninstallexe}"
; 桌面快捷方式
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; 安装完成后运行程序
Filename: "{app}\{#AppExeName}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent

[Messages]
; 自定义中文消息
WelcomeLabel1=欢迎使用 [name] 安装向导
WelcomeLabel2=这将安装 [name/ver] 到您的电脑中。
SelectDirLabel3=安装程序将把 [name] 安装到以下目录。
SelectDirBrowseLabel=继续，请按"下一步"。如果您想选择其他目录，请按"浏览"。
BeveledLabel=正在准备安装...
WizardSelectProgramGroupDescription=在 Windows 开始菜单的以下程序组中创建 [name] 的快捷方式。
WizardSelectProgramGroupLabel3=安装程序将创建 [name] 的快捷方式。
FinishedLabel=[name] 已成功安装到您的电脑中。
ClickFinish=点击"完成"按钮退出安装向导。
FinishedHeadingLabel=安装完成
FinishedLabelNoIcons=[name] 已成功安装到您的电脑中。
CreatingDesktopIconLabel=创建桌面快捷方式:
CreateDesktopIconText=创建桌面快捷方式

[CustomMessages]
CreateDesktopIcon=创建桌面快捷方式
LaunchProgram=启动程序
AdditionalIcons=附加图标:

[Code]
// 检查进程是否正在运行（使用更可靠的方法）
function IsAppRunning: Boolean;
var
  ResultCode: Integer;
  strOutput: AnsiString;
begin
  Result := False;
  // 使用 taskkill 的 /nolog 开关来检查，不会真的关闭
  if Exec('tasklist.exe', '/FI "IMAGENAME eq AutoTestExecutor.exe" /FI "STATUS eq running" /FO CSV /NH', '', SW_HIDE,
     ewWaitUntilTerminated, ResultCode) then
  begin
    // 如果 tasklist 成功执行，检查输出中是否包含进程名
    // 这里简化处理，直接尝试终止进程
    Result := True;
  end;
end;

// 强制终止进程
function KillApp: Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('taskkill.exe', '/F /IM AutoTestExecutor.exe', '', SW_HIDE,
     ewWaitUntilTerminated, ResultCode) then
  begin
    // 等待进程结束
    Sleep(1000);
    Result := True;
  end;
end;

// 安装前检查
function InitializeSetup(): Boolean;
begin
  Result := True;
  // 尝试终止可能存在的进程（静默处理）
  KillApp;
  // 等待一下确保文件释放
  Sleep(500);
end;

// 卸载前检查
function InitializeUninstall(): Boolean;
begin
  Result := True;
  // 强制关闭进程（静默处理）
  KillApp;
  Sleep(500);
end;
