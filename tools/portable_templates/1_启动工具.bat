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

if not exist "app\app.py" (
    echo app\app.py was not found.
    echo Please download the portable release package again.
    echo.
    pause
    exit /b 1
)

cd app
echo Starting Steam Project Assistant...
echo Open http://localhost:8501 if the browser does not open automatically.
echo.
..\runtime\python\python.exe -m streamlit run app.py --server.port 8501

echo.
echo Streamlit has stopped.
pause
exit /b 0
