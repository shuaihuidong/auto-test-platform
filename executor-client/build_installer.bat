@echo off
echo ========================================
echo   Build AutoTest Executor Installer
echo ========================================
echo.

REM 检查 Inno Setup 是否安装
set "INNO_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    set "INNO_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not exist "%INNO_PATH%" (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup first:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup at: %INNO_PATH%
echo.
echo Building installer...
echo.

REM 编译安装程序
"%INNO_PATH%" installer.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Build Complete!
    echo ========================================
    echo.
    echo Installer created: dist\AutoTestExecutor_Setup.exe
    echo.
) else (
    echo.
    echo ========================================
    echo   Build Failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
