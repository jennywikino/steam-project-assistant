@echo off
setlocal

cd /d "%~dp0"

if not exist "logs" mkdir "logs"
if not exist "app" mkdir "app"
set "LOG_FILE=logs\install_playwright.log"
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0app\ms-playwright"

echo Steam Project Assistant - Playwright setup
echo.
echo Working directory: %CD%
echo Log file: %LOG_FILE%
echo Browser install path: %PLAYWRIGHT_BROWSERS_PATH%
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

echo Python command: %PY_CMD%
echo.

echo [%date% %time%] Start Playwright setup > "%LOG_FILE%"
echo Python command: %PY_CMD% >> "%LOG_FILE%"
echo PLAYWRIGHT_BROWSERS_PATH=%PLAYWRIGHT_BROWSERS_PATH% >> "%LOG_FILE%"

echo Installing Playwright Python package...
%PY_CMD% -m pip install playwright >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install Playwright Python package.
    echo Please check %LOG_FILE%
    echo.
    pause
    exit /b 1
)

echo Installing Chromium browser...
echo This may take 5-15 minutes depending on your network.
echo Chromium will be installed inside app\ms-playwright.
%PY_CMD% -m playwright install chromium >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install Chromium browser.
    echo Please check %LOG_FILE%
    echo.
    pause
    exit /b 1
)

echo.
echo Playwright and Chromium are installed.
echo Please restart the Streamlit app or refresh the Steam page collector.
echo.
pause
exit /b 0
