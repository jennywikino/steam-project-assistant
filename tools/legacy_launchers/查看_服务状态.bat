@echo off
chcp 65001 >nul
setlocal

set "PORT=8501"

echo ========================================
echo Steam Project Assistant Service Status
echo ========================================
echo.

set "FOUND=0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    set "FOUND=1"
    echo 项目初筛助手正在运行。
    echo 端口：%PORT%
    echo PID：%%p
)

if "%FOUND%"=="0" (
    echo 项目初筛助手未运行。
)

echo.
pause
