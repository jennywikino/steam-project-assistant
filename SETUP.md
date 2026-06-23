# 安装说明

## Recommended package for normal users

Download:

```text
SteamProjectAssistant-v0.9.2-portable.zip
```

The portable zip includes its own Python runtime. Normal users do not need to install Python.

The GitHub Source code zip is for developers and requires local dependency setup.

To stop the portable app, close the black terminal window opened by `1_启动工具.bat`, or press `Ctrl+C` in that window. Closing only the browser tab may leave Streamlit running on port 8501. If the port is stuck, use `9_可选_强制停止工具.bat` in the portable package.

## Windows Release first-time setup

Recommended order after downloading the GitHub Release zip:

1. Unzip the release package.
2. Double-click `1_首次使用_安装运行依赖.bat`.
3. Double-click `2_启动工具.bat`.
4. Optional: usually do not run `3_可选_安装Steam页面采集环境.bat` first. Run it only if the Steam page collection page says local Edge is unavailable, or if you need a fully portable Playwright Chromium.

The project root contains program files. Normal users only need to focus on `0_先看这里_启动说明.txt`, `1_首次使用_安装运行依赖.bat`, `2_启动工具.bat`, and `3_可选_安装Steam页面采集环境.bat`.

Windows may show an unknown publisher warning for `.bat` or `.vbs` files. Use the scripts from the official GitHub Release only.

VBS launchers, debug startup scripts, stop scripts, and local validation scripts are not recommended for normal users.

## Script logs

- Dependency setup: `logs\install_deps.log`
- Playwright / Chromium setup: `logs\install_playwright.log`

Steam page collection tries local Microsoft Edge first, then falls back to Playwright Chromium in `app/ms-playwright`.

Playwright Chromium setup may take 5-15 minutes depending on your network and is optional for most Windows users.

## 基础启动

安装 Python 依赖后，在项目根目录启动 Streamlit 应用。

## Steam 页面采集环境

Steam 页面采集会优先使用本机 Microsoft Edge。通常不用先运行安装脚本；只有页面提示 Edge 不可用，或需要完全便携 Chromium 时，再安装 Playwright Chromium。首次安装可能需要 5–15 分钟，取决于网络环境。

可在项目根目录运行：

```powershell
python -m pip install playwright
python -m playwright install chromium
```

也可以双击：

```text
3_可选_安装Steam页面采集环境.bat
```

脚本不会假设 `.venv` 已存在，会优先使用 `py -3`，找不到时回退到 `python`。安装过程会写入：

```text
logs/install_playwright.log
```

如果安装失败，请先查看该日志，再重新运行脚本或手动执行上述命令。

## 首页 Feed 数据来源

首页项目发现 Feed 是本地工作台视图，不同电脑会因为本机数据不同而显示不同内容。

默认 Feed 来自 Steam 页面采集、候选池、手动观察和 Steam 图文源。“查查 / 项目画像 / 补资料”产生的 appdetails cache 不默认进入发现流。

首页按钮“重新读取本地数据”只会重新读取本机 `data/` 和 `cache/` 中已有记录，不等于强制抓取最新 Steam 项目。如需重新请求 Steam 图文源，请使用首页“高级刷新 / 缓存维护”中的“强制刷新 Steam 图文源”。
