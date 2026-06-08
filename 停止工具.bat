@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

set "PORT=8501"
set "FOUND=0"
set "FAILED=0"

echo ========================================
echo 停止项目初筛助手
echo ========================================
echo.

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    set "FOUND=1"
    echo 找到 8501 端口上的项目初筛助手后台服务，PID=%%p
    taskkill /PID %%p /F
    if errorlevel 1 (
        set "FAILED=1"
    )
)

if "%FOUND%"=="0" (
    echo 未发现 8501 端口上的项目初筛助手进程。
) else if "%FAILED%"=="1" (
    echo.
    echo 已找到 8501 端口进程，但关闭失败。请以管理员权限运行本脚本，或手动结束上方 PID。
) else (
    echo.
    echo 已关闭项目初筛助手后台服务。
)

echo.
pause
