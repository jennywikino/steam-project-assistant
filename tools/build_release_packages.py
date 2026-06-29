from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


VERSION = "v0.9.2"

LIGHT_ROOT_NAME = "Steam独立游戏发行选品助手_轻量版_需Python环境"
PORTABLE_ROOT_NAME = "Steam独立游戏发行选品助手_免安装Python版"

LIGHT_ZIP_NAME = f"Steam独立游戏发行选品助手_{VERSION}_轻量版_需Python环境.zip"
PORTABLE_ZIP_NAME = f"Steam独立游戏发行选品助手_{VERSION}_免安装Python版.zip"

ROOT_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT_DIR / "tools"
DIST_DIR = ROOT_DIR / "dist"
BUILD_ROOT = DIST_DIR / "_release_build"
LIGHT_ROOT = BUILD_ROOT / LIGHT_ROOT_NAME
PORTABLE_ROOT = BUILD_ROOT / PORTABLE_ROOT_NAME
TEMPLATE_DIR = TOOLS_DIR / "portable_templates"
RUNTIME_ZIP = TOOLS_DIR / "runtime" / "python-embed-amd64.zip"
GET_PIP = TOOLS_DIR / "runtime" / "get-pip.py"

APP_FILES = [
    "app.py",
    "requirements.txt",
    "README.md",
    "SETUP.md",
    "CHANGELOG.md",
]

APP_DIRS = [
    "modules",
    "templates",
    "docs",
]

PORTABLE_PACKAGES = [
    "streamlit",
    "pandas",
    "openpyxl",
    "playwright",
]

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "data",
    "cache",
    "exports",
    "reports",
    "debug",
    "logs",
    "dist",
    "dist_test",
    "tools",
    ".rollback_backup",
}

EXCLUDED_FILE_SUFFIXES = (".pyc", ".pyo")


LIGHT_README_TEXT = """Steam 项目初筛助手 - 启动说明

这是轻量版：
- 体积小
- 需要电脑已有 Python 3.10+
- 第一次使用先运行【1_首次使用_安装运行依赖.bat】
- 日常启动运行【2_启动工具.bat】

如果要使用 Steam 页面采集：
- 再双击【3_可选_安装Steam页面采集环境.bat】
- 这一步会安装 Playwright / Chromium，可能需要 5-15 分钟

退出工具：
- 关闭【2_启动工具.bat】打开的黑色窗口，或在窗口里按 Ctrl+C。
- 只关闭浏览器网页不会一定停止后台服务。
- 如果 8501 端口被占用，双击【9_可选_强制停止工具.bat】。

不要移动 app/ 文件夹。
不要直接点击 app.py。
"""


PORTABLE_README_TEXT = """Steam 项目初筛助手 - 启动说明

这是免安装 Python 版：
- 体积较大
- 自带 Python runtime
- 不需要自己安装 Python
- 解压后直接运行【1_启动工具.bat】

如果要使用 Steam 页面采集：
- 双击【2_可选_安装Steam页面采集环境.bat】
- 这一步会安装 Playwright / Chromium，可能需要 5-15 分钟

退出工具：
- 关闭【1_启动工具.bat】打开的黑色窗口，或在窗口里按 Ctrl+C。
- 只关闭浏览器网页不会一定停止后台服务。
- 如果 8501 端口被占用，双击【9_可选_强制停止工具.bat】。

不要移动 app/ 或 runtime/ 文件夹。
不要直接点击 app.py。
不要删除 runtime/。
"""


LIGHT_INSTALL_DEPS_BAT = r"""@echo off
setlocal

cd /d "%~dp0"

if not exist "app\logs" mkdir "app\logs"
set "LOG_FILE=app\logs\install_deps.log"

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

if not exist "app\requirements.txt" (
    echo app\requirements.txt was not found.
    echo Please download the release package again.
    echo.
    pause
    exit /b 1
)

echo Steam Project Assistant - dependency setup
echo Python command: %PY_CMD%
echo Log file: %LOG_FILE%
echo.

echo [%date% %time%] Start dependency setup > "%LOG_FILE%"
echo Python command: %PY_CMD% >> "%LOG_FILE%"

cd app

echo Upgrading pip...
%PY_CMD% -m pip install --upgrade pip >> "logs\install_deps.log" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to upgrade pip.
    echo Please check app\logs\install_deps.log
    echo.
    pause
    exit /b 1
)

echo Installing project dependencies...
%PY_CMD% -m pip install -r requirements.txt >> "logs\install_deps.log" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install project dependencies.
    echo Please check app\logs\install_deps.log
    echo.
    pause
    exit /b 1
)

echo Installing Playwright Python package...
%PY_CMD% -m pip install playwright >> "logs\install_deps.log" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install Playwright Python package.
    echo Please check app\logs\install_deps.log
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies are installed.
echo You can now run the start script.
echo.
pause
exit /b 0
"""


LIGHT_START_BAT = r"""@echo off
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

if not exist "app\app.py" (
    echo app\app.py was not found.
    echo Please download the release package again.
    echo.
    pause
    exit /b 1
)

cd app

%PY_CMD% -m streamlit --version >nul 2>nul
if errorlevel 1 (
    echo Streamlit was not found.
    echo Please run 1_ first-time dependency setup first.
    echo.
    pause
    exit /b 1
)

echo Starting Steam Project Assistant...
echo Open http://localhost:8501 if the browser does not open automatically.
echo.
%PY_CMD% -m streamlit run app.py --server.port 8501 --server.headless false

echo.
echo Streamlit has stopped.
pause
exit /b 0
"""


LIGHT_INSTALL_COLLECTOR_BAT = r"""@echo off
setlocal

cd /d "%~dp0"

if not exist "app\logs" mkdir "app\logs"
set "LOG_FILE=app\logs\install_playwright.log"

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

echo Steam Project Assistant - Steam page collector setup
echo This may take 5-15 minutes depending on your network.
echo Log file: %LOG_FILE%
echo.

echo [%date% %time%] Start Playwright setup > "%LOG_FILE%"

cd app

echo Installing Playwright Python package...
%PY_CMD% -m pip install playwright >> "logs\install_playwright.log" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install Playwright Python package.
    echo Please check app\logs\install_playwright.log
    echo.
    pause
    exit /b 1
)

echo Installing Chromium browser...
%PY_CMD% -m playwright install chromium >> "logs\install_playwright.log" 2>&1
if errorlevel 1 (
    echo.
    echo Failed to install Chromium browser.
    echo Please check app\logs\install_playwright.log
    echo.
    pause
    exit /b 1
)

echo.
echo Playwright and Chromium are installed.
echo Please restart the Streamlit app or refresh the Steam page collector.
echo.
pause
exit /b 0
"""


def run(command: list[str], cwd: Path | None = None) -> None:
    print("> " + " ".join(command))
    subprocess.run(command, cwd=str(cwd or ROOT_DIR), check=True)


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / 1024 / 1024


def reset_build_dir() -> None:
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    LIGHT_ROOT.mkdir(parents=True)
    PORTABLE_ROOT.mkdir(parents=True)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def ignore_app_tree(dir_path: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDED_DIR_NAMES:
            ignored.add(name)
        if name.endswith(EXCLUDED_FILE_SUFFIXES):
            ignored.add(name)
    return ignored


def copy_app_files(package_root: Path) -> None:
    app_dir = package_root / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    for relative in APP_FILES:
        src = ROOT_DIR / relative
        if src.exists():
            copy_file(src, app_dir / relative)
        else:
            print(f"Warning: missing optional file: {relative}")

    for relative in APP_DIRS:
        src = ROOT_DIR / relative
        if src.exists():
            shutil.copytree(src, app_dir / relative, ignore=ignore_app_tree)
        else:
            print(f"Warning: missing optional directory: {relative}")

    data_dir = app_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "README.md").write_text(
        "# Data directory\n\n"
        "This release package intentionally starts with an empty data directory.\n"
        "Runtime CSV files and local caches will be created here when you use the app.\n",
        encoding="utf-8",
    )

    (app_dir / "logs").mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def copy_stop_script(package_root: Path) -> None:
    src = TEMPLATE_DIR / "9_可选_强制停止工具.bat"
    if not src.exists():
        raise SystemExit(f"Missing stop script template: {src}")
    copy_file(src, package_root / "9_可选_强制停止工具.bat")


def write_light_entrypoints() -> None:
    write_text(LIGHT_ROOT / "0_先看这里_启动说明.txt", LIGHT_README_TEXT)
    write_text(LIGHT_ROOT / "1_首次使用_安装运行依赖.bat", LIGHT_INSTALL_DEPS_BAT)
    write_text(LIGHT_ROOT / "2_启动工具.bat", LIGHT_START_BAT)
    write_text(LIGHT_ROOT / "3_可选_安装Steam页面采集环境.bat", LIGHT_INSTALL_COLLECTOR_BAT)
    copy_stop_script(LIGHT_ROOT)


def write_portable_entrypoints() -> None:
    write_text(PORTABLE_ROOT / "0_先看这里_启动说明.txt", PORTABLE_README_TEXT)
    for name in [
        "1_启动工具.bat",
        "2_可选_安装Steam页面采集环境.bat",
    ]:
        src = TEMPLATE_DIR / name
        if not src.exists():
            raise SystemExit(f"Missing portable template: {src}")
        copy_file(src, PORTABLE_ROOT / name)
    copy_stop_script(PORTABLE_ROOT)


def require_runtime_zip() -> None:
    if RUNTIME_ZIP.exists():
        return
    raise SystemExit(
        "\nPortable Python runtime was not found.\n\n"
        f"Expected file: {RUNTIME_ZIP}\n\n"
        "Download the Windows embeddable Python package from:\n"
        "https://www.python.org/downloads/windows/\n\n"
        "Use the 64-bit embeddable package, rename it to:\n"
        "python-embed-amd64.zip\n\n"
        "Then place it in:\n"
        f"{TOOLS_DIR / 'runtime'}\n"
    )


def extract_runtime() -> Path:
    runtime_dir = PORTABLE_ROOT / "runtime" / "python"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting Python runtime: {RUNTIME_ZIP}")
    with zipfile.ZipFile(RUNTIME_ZIP, "r") as archive:
        archive.extractall(runtime_dir)
    return runtime_dir


def enable_embedded_python_site_packages(runtime_dir: Path) -> None:
    pth_files = list(runtime_dir.glob("python*._pth"))
    if not pth_files:
        print("Warning: python*._pth was not found; skipping embedded site setup.")
        return
    for pth in pth_files:
        lines = pth.read_text(encoding="utf-8").splitlines()
        output: list[str] = []
        found_import_site = False
        for line in lines:
            if line.strip() == "#import site":
                output.append("import site")
                found_import_site = True
            else:
                output.append(line)
                if line.strip() == "import site":
                    found_import_site = True
        if not found_import_site:
            output.append("import site")
        pth.write_text("\n".join(output) + "\n", encoding="utf-8")


def runtime_python(runtime_dir: Path) -> Path:
    python_exe = runtime_dir / "python.exe"
    if not python_exe.exists():
        raise SystemExit(f"python.exe was not found after extraction: {python_exe}")
    return python_exe


def ensure_pip(python_exe: Path) -> None:
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "--version"],
        cwd=str(PORTABLE_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode == 0:
        print(result.stdout.strip())
        return

    if not GET_PIP.exists():
        raise SystemExit(
            "\npip is not available in the embedded Python runtime.\n\n"
            f"Expected bootstrap file: {GET_PIP}\n\n"
            "Download get-pip.py from:\n"
            "https://bootstrap.pypa.io/get-pip.py\n\n"
            "Then place it in tools/runtime/ and run this build script again.\n"
        )

    run([str(python_exe), str(GET_PIP)], cwd=PORTABLE_ROOT)


def install_portable_dependencies(python_exe: Path) -> None:
    run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], cwd=PORTABLE_ROOT)
    run([str(python_exe), "-m", "pip", "install", *PORTABLE_PACKAGES], cwd=PORTABLE_ROOT)


def assert_no_real_data(package_root: Path) -> None:
    forbidden = [
        package_root / "app" / "data" / "cache",
        package_root / "app" / "cache",
        package_root / "app" / "exports",
        package_root / "app" / "reports",
        package_root / "app" / "debug",
    ]
    for path in forbidden:
        if path.exists():
            raise SystemExit(f"Forbidden runtime data path was included: {path}")

    for path in package_root.rglob("*"):
        if path.name in {"candidate_pool.csv", "steam_browser_collected.csv"}:
            raise SystemExit(f"Forbidden real data file was included: {path}")
        if path.name in {"steam_appdetails_cache.json", "steam_home_feed_cache.json"}:
            raise SystemExit(f"Forbidden cache file was included: {path}")
        if path.suffix in EXCLUDED_FILE_SUFFIXES:
            raise SystemExit(f"Forbidden bytecode file was included: {path}")
        if "__pycache__" in path.parts:
            raise SystemExit(f"Forbidden __pycache__ path was included: {path}")


def make_zip(package_root: Path, zip_name: str) -> Path:
    zip_path = DIST_DIR / zip_name
    if zip_path.exists():
        zip_path.unlink()
    print(f"Creating zip: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in package_root.rglob("*"):
            relative_path = path.relative_to(BUILD_ROOT).as_posix()
            if path.is_dir():
                archive.write(path, relative_path + "/")
            elif path.is_file():
                archive.write(path, relative_path)
    return zip_path


def package_has_forbidden_paths(zip_path: Path) -> bool:
    forbidden_fragments = [
        "/data/cache/",
        "/cache/",
        "/exports/",
        "/reports/",
        "/debug/",
        "/.git/",
        "/.venv/",
        "/dist/",
        "/dist_test/",
        "/tools/runtime/",
        "/__pycache__/",
    ]
    forbidden_names = {
        "candidate_pool.csv",
        "steam_browser_collected.csv",
        "steam_appdetails_cache.json",
        "steam_home_feed_cache.json",
    }
    with zipfile.ZipFile(zip_path, "r") as archive:
        for name in archive.namelist():
            normalized = "/" + name.replace("\\", "/")
            if any(fragment in normalized for fragment in forbidden_fragments):
                return True
            if Path(name).name in forbidden_names:
                return True
    return False


def build_light_package() -> Path:
    copy_app_files(LIGHT_ROOT)
    write_light_entrypoints()
    assert_no_real_data(LIGHT_ROOT)
    return make_zip(LIGHT_ROOT, LIGHT_ZIP_NAME)


def build_portable_package(skip_dependency_install: bool = False) -> Path:
    require_runtime_zip()
    copy_app_files(PORTABLE_ROOT)
    write_portable_entrypoints()
    runtime_dir = extract_runtime()
    enable_embedded_python_site_packages(runtime_dir)
    python_exe = runtime_python(runtime_dir)
    if skip_dependency_install:
        print("Skipping portable dependency installation by request.")
    else:
        ensure_pip(python_exe)
        install_portable_dependencies(python_exe)
    assert_no_real_data(PORTABLE_ROOT)
    return make_zip(PORTABLE_ROOT, PORTABLE_ZIP_NAME)


def build(skip_dependency_install: bool = False) -> tuple[Path, Path]:
    DIST_DIR.mkdir(exist_ok=True)
    reset_build_dir()
    light_zip = build_light_package()
    portable_zip = build_portable_package(skip_dependency_install=skip_dependency_install)
    light_forbidden = package_has_forbidden_paths(light_zip)
    portable_forbidden = package_has_forbidden_paths(portable_zip)
    portable_runtime_exists = (PORTABLE_ROOT / "runtime" / "python" / "python.exe").exists()

    print()
    print("Release packages created:")
    print(f"- Light package: {light_zip}")
    print(f"  Size: {file_size_mb(light_zip):.1f} MB")
    print(f"- No-Python-install package: {portable_zip}")
    print(f"  Size: {file_size_mb(portable_zip):.1f} MB")
    print(f"  Includes runtime/python: {'yes' if portable_runtime_exists else 'no'}")
    print(f"- Light package excludes runtime data/cache/export paths: {'no' if light_forbidden else 'yes'}")
    print(f"- No-Python-install package excludes runtime data/cache/export paths: {'no' if portable_forbidden else 'yes'}")
    print()
    print("Upload these two zip files to GitHub Release. Do not ask normal users to download Source code zip.")
    return light_zip, portable_zip


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Windows release zip packages.")
    parser.add_argument(
        "--skip-dependency-install",
        action="store_true",
        help="Create the no-Python-install package without installing Python packages into the embedded runtime.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        build(skip_dependency_install=args.skip_dependency_install)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
