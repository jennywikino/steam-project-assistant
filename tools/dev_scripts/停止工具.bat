@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "PORT=8501"
set "FOUND=0"
set "FAILED=0"

echo Stop Steam Project Assistant
echo.

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    set "FOUND=1"
    echo Found process on port %PORT%. PID=%%p
    taskkill /PID %%p /F
    if errorlevel 1 (
        set "FAILED=1"
    )
)

if "%FOUND%"=="0" (
    echo No process was found on port %PORT%.
) else if "%FAILED%"=="1" (
    echo.
    echo A process was found, but stopping it failed.
    echo Please run this script as administrator or stop the PID manually.
) else (
    echo.
    echo The process was stopped.
)

echo.
pause
exit /b 0
