from pathlib import Path
from datetime import datetime
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
DEBUG_DIR = ROOT_DIR / "debug"
HOME_URL = "http://localhost:8501/"
HTML_PATH = DEBUG_DIR / "smoke_home.html"
SCREENSHOT_PATH = DEBUG_DIR / "smoke_home.png"
REPORT_PATH = DEBUG_DIR / "smoke_report.txt"
TIMEOUT_SECONDS = 8
ERROR_KEYWORDS = [
    "ImportError",
    "ModuleNotFoundError",
    "Traceback",
    "cannot import name",
    "NameError",
    "KeyError",
    "AttributeError",
    "SyntaxError",
    "StreamlitAPIException",
    "FileNotFoundError",
    "PermissionError",
]
CORE_TEXTS = ["Steam", "项目", "首页", "一键项目画像"]
OPTIONAL_TEXTS = ["外部情报", "数据健康检查", "今日新游雷达", "Steam 直查"]
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
    result = {
        "tested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": HOME_URL,
        "http_status": "",
        "html_path": str(HTML_PATH),
        "screenshot_path": str(SCREENSHOT_PATH),
        "browser_source": "HTTP only",
        "screenshot_saved": False,
        "screenshot_warning": "",
        "error_hits": [],
        "core_hits": [],
        "optional_hits": [],
        "optional_missing": [],
        "final_result": "FAIL",
    }
    status_code, html = fetch_home_html()
    result["http_status"] = str(status_code) if status_code > 0 else "不可访问"
    if status_code <= 0:
        print("[FAIL] localhost 不可访问")
        print("Streamlit 未启动或端口不可访问")
        print("请先运行 启动工具.vbs 或 调试启动.bat")
        result["final_result"] = "FAIL"
        write_report(result)
        return 1

    print(f"[OK] localhost 可访问，HTTP 状态：{status_code}")
    save_html(html)
    browser_result = run_playwright_check()
    result.update(browser_result)

    combined_text = "\n".join([html or "", browser_result.get("page_text", "")])
    result["error_hits"] = find_keywords(combined_text, ERROR_KEYWORDS)
    result["core_hits"] = find_keywords(combined_text, CORE_TEXTS)
    result["optional_hits"] = find_keywords(combined_text, OPTIONAL_TEXTS)
    result["optional_missing"] = [text for text in OPTIONAL_TEXTS if text not in result["optional_hits"]]

    failed = False
    if result["error_hits"]:
        print("[FAIL] 页面包含错误文本：" + ", ".join(result["error_hits"]))
        failed = True
    else:
        print("[OK] 未发现错误关键词")

    if len(result["core_hits"]) >= 2:
        print("[OK] 核心文本命中：" + ", ".join(result["core_hits"]))
    else:
        print("[FAIL] 核心文本命中不足：" + (", ".join(result["core_hits"]) if result["core_hits"] else "无"))
        failed = True

    if result["optional_missing"]:
        print("[WARN] 可选文本未命中：" + ", ".join(result["optional_missing"]))
    else:
        print("[OK] 可选文本全部命中")

    result["final_result"] = "FAIL" if failed else "PASS"
    write_report(result)
    if failed:
        print(f"[FAIL] 本地冒烟验收失败，详情见 {REPORT_PATH}")
        return 1
    print("[PASS] 本地冒烟验收通过")
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


def run_playwright_check() -> dict:
    result = {
        "browser_source": "HTTP only",
        "screenshot_saved": False,
        "screenshot_warning": "",
        "page_text": "",
    }
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[SKIP] Playwright 未安装")
        print("未安装 playwright，已跳过浏览器截图，只做 HTTP 检查。")
        print("可选安装：")
        print("pip install playwright")
        return result

    try:
        with sync_playwright() as playwright:
            browser, browser_label = launch_local_browser(playwright)
            if browser is None:
                print("[SKIP] 未找到可用 Chrome/Edge，已跳过浏览器截图，只做 HTTP 检查。")
                return result
            result["browser_source"] = browser_label
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
            result["screenshot_saved"] = True
            print(f"[OK] 截图已保存：{SCREENSHOT_PATH}")
            size_warning = check_screenshot_file()
            if size_warning:
                result["screenshot_warning"] = size_warning
                print(f"[WARN] {size_warning}")
            result["page_text"] = read_page_text(page)
            browser.close()
    except PlaywrightError as exc:
        print(f"[WARN] Playwright 浏览器检查失败：{short_error(exc)}")
        result["screenshot_warning"] = f"Playwright 浏览器检查失败：{short_error(exc)}"
    except Exception as exc:
        print(f"[WARN] Playwright 截图步骤失败：{short_error(exc)}")
        result["screenshot_warning"] = f"Playwright 截图步骤失败：{short_error(exc)}"
    return result


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


def read_page_text(page) -> str:
    try:
        return page.locator("body").inner_text(timeout=8000)
    except Exception as exc:
        print(f"[WARN] 页面文本读取失败：{short_error(exc)}")
        return ""


def check_screenshot_file() -> str:
    try:
        if not SCREENSHOT_PATH.exists():
            return "截图文件未生成。"
        if SCREENSHOT_PATH.stat().st_size <= 10 * 1024:
            return "截图文件过小，可能页面未完整渲染。"
    except OSError as exc:
        return f"截图文件检查失败：{exc}"
    return ""


def find_keywords(text: str, keywords: list[str]) -> list[str]:
    haystack = text or ""
    return [keyword for keyword in keywords if keyword in haystack]


def write_report(result: dict) -> None:
    lines = [
        f"测试时间：{result.get('tested_at', '')}",
        f"URL：{result.get('url', HOME_URL)}",
        f"HTTP 状态：{result.get('http_status', '')}",
        f"HTML 文件路径：{result.get('html_path', HTML_PATH)}",
        f"截图文件路径：{result.get('screenshot_path', SCREENSHOT_PATH)}",
        f"浏览器来源：{result.get('browser_source', 'HTTP only')}",
        f"截图状态：{'已保存' if result.get('screenshot_saved') else '未保存'}",
        f"截图警告：{result.get('screenshot_warning') or '无'}",
        f"错误关键词命中：{', '.join(result.get('error_hits') or []) or '无'}",
        f"核心文本命中：{', '.join(result.get('core_hits') or []) or '无'}",
        f"可选文本命中：{', '.join(result.get('optional_hits') or []) or '无'}",
        f"可选文本未命中：{', '.join(result.get('optional_missing') or []) or '无'}",
        f"最终结果：{result.get('final_result', 'FAIL')}",
    ]
    try:
        REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"[WARN] smoke_report.txt 写入失败：{exc}")


def short_error(exc: Exception) -> str:
    return str(exc).splitlines()[0][:220]


if __name__ == "__main__":
    sys.exit(main())
