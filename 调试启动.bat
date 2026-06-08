@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "PORT=8501"

echo ========================================
echo 调试启动项目初筛助手
echo ========================================
echo.

cd /d "%~dp0"

if not exist "app.py" (
    echo [ERROR] 未找到 app.py，请确认本脚本位于项目根目录。
    echo.
    pause
    exit /b 1
)

echo 工作目录：%cd%
echo 启动地址：http://localhost:%PORT%
echo.

py -3 -m streamlit run app.py --server.port %PORT%

echo.
echo Streamlit 已退出或启动失败。
pause
