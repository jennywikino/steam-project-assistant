@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=runtime\python\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Portable Python runtime was not found.
    echo Please download the portable release package again.
    echo.
    pause
    exit /b 1
)

if not exist "app\logs" mkdir "app\logs"
set "LOG_FILE=app\logs\install_playwright.log"
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0app\ms-playwright"

cd app

echo Steam Project Assistant - Steam page collector setup
echo This may take 5-15 minutes depending on your network.
echo Log file: logs\install_playwright.log
echo Browser install path: %PLAYWRIGHT_BROWSERS_PATH%
echo Chromium will be installed inside app\ms-playwright.
echo.

echo [%date% %time%] Start Playwright Chromium setup > "logs\install_playwright.log"
echo PLAYWRIGHT_BROWSERS_PATH=%PLAYWRIGHT_BROWSERS_PATH% >> "logs\install_playwright.log"
..\runtime\python\python.exe -m playwright install chromium >> "logs\install_playwright.log" 2>&1
if errorlevel 1 (
    echo.
    echo Installation failed.
    echo Please check %LOG_FILE%
    echo.
    pause
    exit /b 1
)

echo.
echo Playwright Chromium browser is installed.
echo Please restart the Streamlit app or refresh the Steam page collector.
echo.
pause
exit /b 0
