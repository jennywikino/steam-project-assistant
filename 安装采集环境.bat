@echo off
chcp 65001 >nul
cd /d %~dp0
echo 正在安装 Steam 页面采集环境...
echo.
.\.venv\Scripts\python.exe -m pip install playwright
if errorlevel 1 (
  echo.
  echo Playwright Python 包安装失败。
  pause
  exit /b 1
)
echo.
.\.venv\Scripts\python.exe -m playwright install chromium
if errorlevel 1 (
  echo.
  echo Chromium 浏览器安装失败。
  pause
  exit /b 1
)
echo.
echo 安装完成。请重新启动 Steam 项目初筛助手。
pause
