@echo off
setlocal

cd /d "%~dp0"

if not exist "logs" mkdir "logs"
set "LOG_FILE=logs\install_deps.log"

echo Steam Project Assistant - dependency setup
echo.
echo Working directory: %CD%
echo Log file: %LOG_FILE%
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PY_CMD=python"
    ) else (
        echo Python was not found.
        echo Please install Python 3.10+ and try again.
        echo.
        pause
        exit /b 1
    )
)

if not exist "requirements.txt" (
    echo requirements.txt was not found.
    echo Please run this script from the project folder.
    echo.
    pause
    exit /b 1
)

echo Python command: %PY_CMD%
echo.

echo [%date% %time%] Start dependency setup > "%LOG_FILE%"
echo Python command: %PY_CMD% >> "%LOG_FILE%"

echo Upgrading pip...
%PY_CMD% -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to upgrade pip.
    echo Please check %LOG_FILE%
    echo.
    pause
    exit /b 1
)

echo Installing project dependencies...
%PY_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install project dependencies.
    echo Please check %LOG_FILE%
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies are installed.
echo You can now run the start script.
echo.
pause
exit /b 0
