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

echo Running local smoke test...
%PY_CMD% tools\smoke_test_streamlit.py

echo.
pause
exit /b 0
