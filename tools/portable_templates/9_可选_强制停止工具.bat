@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "PORT=8501"
set "FOUND=0"
set "FAILED=0"

echo Steam Project Assistant - optional stop tool
echo.
echo This will stop the process using port 8501.
echo Use this only when the Streamlit window is closed or the port is stuck.
echo.

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    set "FOUND=1"
    echo Found process using port %PORT%. PID=%%p
    taskkill /PID %%p /F
    if errorlevel 1 (
        set "FAILED=1"
    )
)

if "%FOUND%"=="0" (
    echo No process is using port 8501.
) else if "%FAILED%"=="1" (
    echo.
    echo Failed to stop one or more processes.
    echo Please run this script as administrator if needed.
) else (
    echo.
    echo Port 8501 has been released.
)

echo.
pause
exit /b 0
