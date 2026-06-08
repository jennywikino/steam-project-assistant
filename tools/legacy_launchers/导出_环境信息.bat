@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

if not exist "docs" (
    mkdir docs
)

echo ========================================
echo Export Environment Information
echo ========================================
echo.

echo Python version:
py -3 --version
if errorlevel 1 (
    echo [ERROR] Python 3 not found.
    echo.
    pause
    exit /b 1
)

echo.
echo pip version:
py -3 -m pip --version
if errorlevel 1 (
    echo [ERROR] pip not available.
    echo.
    pause
    exit /b 1
)

echo.
echo Writing dependency snapshot to docs\environment_freeze.txt ...
py -3 -m pip freeze > docs\environment_freeze.txt
if errorlevel 1 (
    echo [ERROR] Failed to export dependency snapshot.
    echo.
    pause
    exit /b 1
)

echo Writing project tree to docs\project_tree.txt ...
tree /F > docs\project_tree.txt
if errorlevel 1 (
    echo [ERROR] Failed to export project tree.
    echo.
    pause
    exit /b 1
)

echo.
echo Done. Do not upload sensitive files, company templates, or private data.
pause
