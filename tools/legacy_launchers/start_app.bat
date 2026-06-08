@echo off
chcp 65001 >nul
setlocal

set PORT=8501

echo ========================================
echo Steam Project Assistant Launcher
echo ========================================

cd /d "%~dp0"

echo Current directory:
echo %cd%
echo.

if not exist "app.py" (
    echo [ERROR] app.py not found in current directory.
    echo Please make sure this bat file is in the same folder as app.py.
    echo.
    echo Files in current directory:
    dir
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found.
    echo.
    pause
    exit /b 1
)

echo Checking Python...
py -3 --version
if errorlevel 1 (
    echo [ERROR] Python 3 not found. Please install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    echo.
    pause
    exit /b 1
)

echo.
echo Checking port %PORT%...
set FOUND_OLD=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    set FOUND_OLD=1
    echo 检测到旧的项目初筛助手仍在运行，正在尝试关闭旧进程...
    echo Found old process on port %PORT%, PID=%%p
    taskkill /PID %%p /F
)

timeout /t 2 /nobreak >nul
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo [ERROR] 8501 端口仍被占用，自动清理失败。
    echo 请运行：停止_项目初筛助手.bat
    echo.
    pause
    exit /b 1
)

if "%FOUND_OLD%"=="1" (
    echo 旧的 8501 端口进程已清理。
)

echo.
echo Starting Streamlit app on http://localhost:%PORT% ...
py -3 -m streamlit run app.py --server.port %PORT%

echo.
echo Streamlit closed or failed.
pause
