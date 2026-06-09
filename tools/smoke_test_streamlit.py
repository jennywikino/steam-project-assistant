from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
DEBUG_DIR = ROOT_DIR / "debug"
HOME_URL = "http://localhost:8501/"
HTML_PATH = DEBUG_DIR / "smoke_home.html"
SCREENSHOT_PATH = DEBUG_DIR / "smoke_home.png"
TIMEOUT_SECONDS = 8
LOCAL_BROWSER_CANDIDATES = [
    ("本机 Chrome", {"channel": "chrome"}),
    ("本机 Edge", {"channel": "msedge"}),
    ("本机 Chrome", {"executable_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe"}),
    ("本机 Chrome", {"executable_path": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"}),
    ("本机 Edge", {"executable_path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"}),
    ("本机 Edge", {"executable_path": r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"}),
]


def main() -> int:
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    status_code, html = fetch_home_html()
    if status_code <= 0:
        print("[FAIL] localhost 不可访问")
        print("Streamlit 未启动或端口不可访问")
        print("请先运行 启动工具.vbs 或 调试启动.bat")
        return 1

    print(f"[OK] localhost 可访问，HTTP 状态：{status_code}")
    save_html(html)
    run_playwright_check()
    return 0


def fetch_home_html() -> tuple[int, str]:
    request = Request(HOME_URL, headers={"User-Agent": "steam-project-assistant-smoke/0.6.7a"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            return int(response.status), raw.decode(encoding, errors="replace")
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        print(f"[FAIL] HTTP 请求失败：{exc.code} {exc.reason}")
        return int(exc.code), body
    except URLError as exc:
        print(f"[FAIL] 连接失败：{exc.reason}")
        return 0, ""
    except TimeoutError:
        print(f"[FAIL] 请求超时：{TIMEOUT_SECONDS}s")
        return 0, ""
    except OSError as exc:
        print(f"[FAIL] 本地请求异常：{exc}")
        return 0, ""


def save_html(html: str) -> None:
    try:
        HTML_PATH.write_text(html or "", encoding="utf-8")
        print(f"[OK] HTML 已保存：{HTML_PATH}")
    except OSError as exc:
        print(f"[WARN] HTML 保存失败：{exc}")


def run_playwright_check() -> None:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[SKIP] Playwright 未安装")
        print("未安装 playwright，已跳过浏览器截图，只做 HTTP 检查。")
        print("可选安装：")
        print("pip install playwright")
        return

    try:
        with sync_playwright() as playwright:
            browser, browser_label = launch_local_browser(playwright)
            if browser is None:
                print("[SKIP] 未找到可用 Chrome/Edge，已跳过浏览器截图，只做 HTTP 检查。")
                return
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
            print(f"[OK] 使用{browser_label} 截图已保存：{SCREENSHOT_PATH}")
            check_page_text(page)
            browser.close()
    except PlaywrightError as exc:
        print(f"[WARN] Playwright 浏览器检查失败：{short_error(exc)}")
    except Exception as exc:
        print(f"[WARN] Playwright 截图步骤失败：{short_error(exc)}")


def launch_local_browser(playwright) -> tuple[object | None, str]:
    for label, options in LOCAL_BROWSER_CANDIDATES:
        executable_path = options.get("executable_path")
        if executable_path and not Path(executable_path).exists():
            continue
        try:
            browser = playwright.chromium.launch(headless=True, **options)
            return browser, label
        except Exception:
            continue
    return None, ""


def check_page_text(page) -> None:
    expected = ["Steam 项目初筛助手", "首页", "一键项目画像"]
    try:
        body_text = page.locator("body").inner_text(timeout=8000)
    except Exception as exc:
        print(f"[WARN] 页面文本读取失败：{short_error(exc)}")
        return

    missing = [text for text in expected if text not in body_text]
    if not missing:
        print("[OK] 页面关键文本检查通过")
    else:
        print("[WARN] 页面关键文本缺失：" + " / ".join(missing))


def short_error(exc: Exception) -> str:
    return str(exc).splitlines()[0][:220]


if __name__ == "__main__":
    sys.exit(main())
