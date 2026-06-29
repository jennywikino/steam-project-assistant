@echo off
setlocal

cd /d "%~dp0"

echo Steam Project Assistant - local cache cleanup
echo.
echo This script only removes files inside the current tool folder.
echo It will not remove %%LOCALAPPDATA%%\ms-playwright or other global user folders.
echo.
echo Cleanup targets:
echo - app\logs
echo - app\data\cache
echo - app\ms-playwright
echo.

if exist "app\logs" (
    echo Removing app\logs ...
    rmdir /s /q "app\logs"
) else (
    echo app\logs not found.
)

if exist "app\data\cache" (
    echo Removing app\data\cache ...
    rmdir /s /q "app\data\cache"
) else (
    echo app\data\cache not found.
)

if exist "app\ms-playwright" (
    echo Removing app\ms-playwright ...
    rmdir /s /q "app\ms-playwright"
) else (
    echo app\ms-playwright not found.
)

echo.
echo Cleanup finished.
echo.
pause
exit /b 0
