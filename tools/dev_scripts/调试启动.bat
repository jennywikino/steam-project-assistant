@echo off
setlocal

cd /d "%~dp0"

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

echo Starting Steam Project Assistant in debug mode...
echo.
%PY_CMD% -m streamlit run app.py --server.port 8501 --server.headless false --logger.level debug

echo.
echo Streamlit has stopped.
pause
exit /b 0
