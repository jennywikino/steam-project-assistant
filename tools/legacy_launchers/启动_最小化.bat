@echo off
chcp 65001 >nul
setlocal

set PORT=8501

echo ========================================
echo Steam Project Assistant Minimized Launcher
echo ========================================

cd /d "%~dp0"

if not exist "app.py" (
    echo [ERROR] app.py not found in current directory.
    echo Please make sure this bat file is in the same folder as app.py.
    echo.
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

echo Starting Streamlit on http://localhost:%PORT% ...
start "Steam Project Assistant" /min cmd /k "cd /d ""%~dp0"" && py -3 -m streamlit run app.py --server.port %PORT%"

echo.
echo Streamlit is running in a minimized cmd window.
echo Open http://localhost:%PORT% in your browser.
echo 关闭浏览器标签页不会关闭后台服务。
echo 正常退出请关闭启动窗口，或双击 停止_项目初筛助手.bat。
pause
