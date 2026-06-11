@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

set "PORT=8501"
set "FOUND=0"

echo ========================================
echo 项目初筛助手状态
echo ========================================
echo.

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
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
