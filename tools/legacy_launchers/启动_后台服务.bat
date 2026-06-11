@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

set "PORT=8501"
set "APP_URL=http://localhost:%PORT%"

cd /d "%~dp0"

if not exist "logs" mkdir "logs"
set "LOG_FILE=%~dp0logs\streamlit.log"

echo.>> "%LOG_FILE%"
echo ==================================================>> "%LOG_FILE%"
echo [%date% %time%] 启动项目初筛助手后台服务>> "%LOG_FILE%"
echo 工作目录：%cd%>> "%LOG_FILE%"

if not exist "app.py" (
    echo [%date% %time%] [ERROR] app.py not found.>> "%LOG_FILE%"
    exit /b 1
)

call :resolve_python
if errorlevel 1 (
    echo [%date% %time%] [ERROR] 未找到可用 Python。>> "%LOG_FILE%"
    exit /b 1
)

echo [%date% %time%] Python 命令：%PYTHON_CMD%>> "%LOG_FILE%"

echo [%date% %time%] 检查 %PORT% 端口...>> "%LOG_FILE%"
set "FOUND_OLD=0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    set "FOUND_OLD=1"
    echo [%date% %time%] 检测到旧服务 PID=%%p，正在关闭...>> "%LOG_FILE%"
    taskkill /PID %%p /F >> "%LOG_FILE%" 2>&1
)

timeout /t 2 /nobreak >nul

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo [%date% %time%] [ERROR] %PORT% 端口仍被占用，PID=%%p。>> "%LOG_FILE%"
    exit /b 1
)

if "%FOUND_OLD%"=="1" (
    echo [%date% %time%] 旧的 %PORT% 端口进程已清理。>> "%LOG_FILE%"
)

echo [%date% %time%] 启动 Streamlit：%APP_URL%>> "%LOG_FILE%"
%PYTHON_CMD% -m streamlit run app.py --server.port %PORT% --server.headless true >> "%LOG_FILE%" 2>&1
echo [%date% %time%] Streamlit 进程退出，退出码：%ERRORLEVEL%>> "%LOG_FILE%"
exit /b %ERRORLEVEL%

:resolve_python
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    exit /b 0
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    exit /b 0
)

if exist "%LocalAppData%\Python\bin\python.exe" (
    set "PYTHON_CMD="%LocalAppData%\Python\bin\python.exe""
    exit /b 0
)

exit /b 1
