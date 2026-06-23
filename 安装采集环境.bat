@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist logs mkdir logs
set "LOG_FILE=%CD%\logs\install_playwright.log"

echo Steam 页面采集环境安装
echo 当前目录：%CD%
echo 日志文件：%LOG_FILE%
echo.
echo Steam 页面采集需要安装 Playwright Python 包和 Chromium 浏览器。
echo 首次安装可能需要 5-15 分钟，取决于网络环境。
echo.

> "%LOG_FILE%" echo Steam 页面采集环境安装
>> "%LOG_FILE%" echo 当前目录：%CD%
>> "%LOG_FILE%" echo 开始时间：%DATE% %TIME%
>> "%LOG_FILE%" echo.

set "PYTHON_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if "%PYTHON_CMD%"=="" (
  python --version >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
  echo 未找到 py -3 或 python。请先安装 Python 3。
  >> "%LOG_FILE%" echo 未找到 py -3 或 python。
  echo.
  echo 安装失败，请查看 logs\install_playwright.log。
  pause
  exit /b 1
)

echo 使用 Python 命令：%PYTHON_CMD%
>> "%LOG_FILE%" echo 使用 Python 命令：%PYTHON_CMD%
echo.

echo [1/2] 正在安装 Playwright Python 包...
echo 命令：%PYTHON_CMD% -m pip install playwright
>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo [1/2] %PYTHON_CMD% -m pip install playwright
%PYTHON_CMD% -m pip install playwright >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo.
  echo Playwright Python 包安装失败。
  echo 请查看 logs\install_playwright.log。
  pause
  exit /b 1
)

echo [1/2] 完成。
echo.

echo [2/2] 正在下载 Chromium 浏览器...
echo 命令：%PYTHON_CMD% -m playwright install chromium
>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo [2/2] %PYTHON_CMD% -m playwright install chromium
%PYTHON_CMD% -m playwright install chromium >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo.
  echo Chromium 浏览器安装失败。
  echo 请查看 logs\install_playwright.log。
  pause
  exit /b 1
)

echo [2/2] 完成。
echo.
echo 安装完成。请重新启动 Steam Project Assistant。
>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo 安装完成：%DATE% %TIME%
echo.
pause
