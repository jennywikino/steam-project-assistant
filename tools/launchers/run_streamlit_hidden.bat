@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

set "PORT=8501"
set "APP_URL=http://localhost:%PORT%"

cd /d "%~dp0\..\.."

if not exist "logs" mkdir "logs"
set "LOG_FILE=%cd%\logs\streamlit.log"

echo.>> "%LOG_FILE%"
echo ==================================================>> "%LOG_FILE%"
echo [%date% %time%] 启动项目初筛助手后台服务>> "%LOG_FILE%"
echo 工作目录：%cd%>> "%LOG_FILE%"

if not exist "app.py" (
    echo [%date% %time%] [ERROR] app.py not found.>> "%LOG_FILE%"
    exit /b 1
)

echo [%date% %time%] 检查 %PORT% 端口...>> "%LOG_FILE%"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    echo [%date% %time%] 检测到旧服务 PID=%%p，正在关闭...>> "%LOG_FILE%"
    taskkill /PID %%p /F >> "%LOG_FILE%" 2>&1
)

timeout /t 2 /nobreak >nul

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    echo [%date% %time%] [ERROR] %PORT% 端口仍被占用，PID=%%p。>> "%LOG_FILE%"
    exit /b 1
)

echo [%date% %time%] 启动 Streamlit：%APP_URL%>> "%LOG_FILE%"
py -3 -m streamlit run app.py --server.port %PORT% --server.headless true >> "%LOG_FILE%" 2>&1
echo [%date% %time%] Streamlit 进程退出，退出码：%ERRORLEVEL%>> "%LOG_FILE%"
exit /b %ERRORLEVEL%
