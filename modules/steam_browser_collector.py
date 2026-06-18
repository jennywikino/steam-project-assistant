from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import socket
import subprocess
import urllib.error
import urllib.request

import pandas as pd

from modules.steam_app_enricher import enrich_appids_basic


DEFAULT_STEAM_URL = "https://store.steampowered.com/?l=schinese"
DEFAULT_DEBUG_PORT = 9222
CDP_CONNECT_ERROR_MESSAGE = "未检测到受控 Steam 浏览器，请先点击打开 Steam 浏览器。"
STEAM_BROWSER_COLLECTED_COLUMNS = [
    "appid",
    "game_name",
    "steam_url",
    "source_page_url",
    "source_page_title",
    "collected_at",
    "collect_method",
    "selected",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "review_score",
    "review_count",
    "import_suggestion",
    "import_reason",
]

APP_URL_RE = re.compile(r"https?://store\.steampowered\.com/app/(\d+)(?:/|$)", re.IGNORECASE)


def playwright_available() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
    except Exception:
        return False
    return True


def find_browser_executable() -> str:
    configured_path = os.environ.get("STEAM_BROWSER_PATH", "").strip()
    if configured_path and Path(configured_path).exists():
        return configured_path

    try:
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        try:
            executable = playwright.chromium.executable_path
        finally:
            playwright.stop()
        if executable and Path(executable).exists():
            return str(executable)
    except Exception:
        pass

    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ""


def launch_browser(user_data_dir: Path, start_url: str = DEFAULT_STEAM_URL, debug_port: int = DEFAULT_DEBUG_PORT) -> dict:
    if not playwright_available():
        return {
            "success": False,
            "message": "当前环境未安装 Playwright。请先运行：pip install playwright；playwright install chromium",
            "browser_running": False,
            "debug_port": debug_port,
        }

    if browser_is_open(debug_port):
        return {
            "success": True,
            "message": "浏览器状态：已打开。",
            "browser_running": True,
            "debug_port": debug_port,
        }

    executable = find_browser_executable()
    if not executable:
        return {
            "success": False,
            "message": "未找到浏览器，请确认 Playwright Chromium 已安装，或配置本地 Chrome 路径。",
            "browser_running": False,
            "debug_port": debug_port,
        }

    try:
        user_data_dir.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(
            [
                executable,
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={user_data_dir}",
                "--new-window",
                start_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception as exc:
        return {
            "success": False,
            "message": f"Steam 浏览器启动失败：{exc}",
            "browser_running": False,
            "debug_port": debug_port,
        }

    return {
        "success": True,
        "message": "Steam 浏览器已打开。",
        "browser_running": True,
        "debug_port": debug_port,
    }


def browser_is_open(debug_port: int = DEFAULT_DEBUG_PORT) -> bool:
    return _cdp_available(debug_port)


def collect_current_page_appids(csv_path: Path | None = None, debug_port: int = DEFAULT_DEBUG_PORT) -> dict:
    try:
        page_info = _read_active_page(debug_port)
    except Exception as exc:
        return {"success": False, "message": _format_cdp_error(exc), "rows": []}

    appids = extract_appids_from_links([page_info["url"], *page_info["links"]])
    if not appids:
        return {
            "success": False,
            "message": "当前页面未发现 Steam app 链接，请滚动或打开具体游戏页后再试。",
            "rows": [],
        }
    rows = build_collected_rows(appids, page_info["url"], page_info["title"], "current_page")
    stats = save_collected_rows(csv_path, rows) if csv_path else {}
    return {
        "success": True,
        "message": f"当前页面发现 {len(appids)} 个 Steam AppID。",
        "rows": rows,
        "save_stats": stats,
    }


def collect_current_app(csv_path: Path | None = None, debug_port: int = DEFAULT_DEBUG_PORT) -> dict:
    try:
        page_info = _read_active_page(debug_port)
    except Exception as exc:
        return {"success": False, "message": _format_cdp_error(exc), "rows": []}

    appids = extract_appids_from_links([page_info["url"]])
    if not appids:
        return {"success": False, "message": "当前页不是 Steam App 页面。", "rows": []}
    rows = build_collected_rows([appids[0]], page_info["url"], page_info["title"], "current_app")
    stats = save_collected_rows(csv_path, rows) if csv_path else {}
    return {
        "success": True,
        "message": f"已提取当前游戏 AppID：{appids[0]}。",
        "rows": rows,
        "save_stats": stats,
    }


def extract_appids_from_links(links: list[str]) -> list[str]:
    seen: set[str] = set()
    appids: list[str] = []
    for link in links:
        for match in APP_URL_RE.finditer(str(link or "")):
            appid = match.group(1).strip()
            if appid and appid.isdigit() and appid not in seen:
                seen.add(appid)
                appids.append(appid)
    return appids


def build_collected_rows(appids: list[str], source_page_url: str, source_page_title: str, collect_method: str) -> list[dict]:
    collected_at = _now_text()
    rows = []
    for appid in appids:
        rows.append(
            {
                "appid": appid,
                "game_name": "",
                "steam_url": steam_url_from_appid(appid),
                "source_page_url": source_page_url,
                "source_page_title": source_page_title,
                "collected_at": collected_at,
                "collect_method": collect_method,
                "developer": "",
                "publisher": "",
                "release_status": "",
                "release_date": "",
                "has_demo": "",
                "supports_schinese": "",
                "genres_tags": "",
                "review_score": "",
                "review_count": "",
                "import_suggestion": "待补资料",
                "import_reason": "仅从 Steam 页面链接识别到 AppID，尚未补全基础信息。",
            }
        )
    return rows


def load_collected(csv_path: Path) -> pd.DataFrame:
    ensure_collected_csv(csv_path)
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=STEAM_BROWSER_COLLECTED_COLUMNS)
    for column in STEAM_BROWSER_COLLECTED_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, STEAM_BROWSER_COLLECTED_COLUMNS].copy()


def save_collected_rows(csv_path: Path, rows: list[dict]) -> dict:
    ensure_collected_csv(csv_path)
    data = load_collected(csv_path)
    stats = {"created": 0, "updated": 0, "total": 0}
    for raw in rows:
        row = _normalize_row(raw)
        appid = row.get("appid", "")
        if not appid:
            continue
        mask = data["appid"].astype(str).str.strip().eq(appid)
        if mask.any():
            index = data.loc[mask].index[0]
            for column in ["collected_at", "source_page_url", "source_page_title", "collect_method"]:
                data.loc[index, column] = row.get(column, "")
            for column in STEAM_BROWSER_COLLECTED_COLUMNS:
                if column in {"appid", "collected_at", "source_page_url", "source_page_title", "collect_method"}:
                    continue
                if not str(data.loc[index, column] or "").strip() and row.get(column):
                    data.loc[index, column] = row[column]
            stats["updated"] += 1
        else:
            data = pd.concat([data, pd.DataFrame([row], columns=STEAM_BROWSER_COLLECTED_COLUMNS)], ignore_index=True)
            stats["created"] += 1
    data = data.drop_duplicates(subset=["appid"], keep="last")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    stats["total"] = len(data)
    return stats


def backup_collected_csv(csv_path: Path) -> Path:
    ensure_collected_csv(csv_path)
    backup_path = csv_path.with_name(f"{csv_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{csv_path.suffix}")
    shutil.copy2(csv_path, backup_path)
    return backup_path


def clear_collected_csv(csv_path: Path) -> dict:
    backup_path = backup_collected_csv(csv_path)
    before = len(load_collected(csv_path))
    pd.DataFrame(columns=STEAM_BROWSER_COLLECTED_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"before": before, "after": 0, "removed": before, "backup_path": str(backup_path)}


def dedupe_collected_by_appid(csv_path: Path) -> dict:
    backup_path = backup_collected_csv(csv_path)
    data = load_collected(csv_path)
    before = len(data)
    if data.empty:
        data.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return {"before": before, "after": 0, "removed": 0, "backup_path": str(backup_path)}

    data = data.copy()
    data["_row_order"] = range(len(data))
    if "collected_at" in data.columns:
        data["_collected_sort"] = pd.to_datetime(data["collected_at"], errors="coerce")
        data = data.sort_values(["appid", "_collected_sort", "_row_order"], na_position="first")
    else:
        data = data.sort_values(["appid", "_row_order"])
    data = data.drop_duplicates(subset=["appid"], keep="last")
    data = data.sort_values("_row_order").drop(columns=[column for column in ["_row_order", "_collected_sort"] if column in data.columns])
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    after = len(data)
    return {"before": before, "after": after, "removed": before - after, "backup_path": str(backup_path)}


def update_collected_selection(csv_path: Path, visible_appids: list[str], selected_appids: list[str]) -> dict:
    data = load_collected(csv_path)
    if data.empty:
        return {"visible": 0, "selected": 0}

    visible_set = {str(appid or "").strip() for appid in visible_appids if str(appid or "").strip()}
    selected_set = {str(appid or "").strip() for appid in selected_appids if str(appid or "").strip()}
    if not visible_set:
        return {"visible": 0, "selected": int(_selected_mask(data).sum())}

    appids = data["appid"].astype(str).str.strip()
    visible_mask = appids.isin(visible_set)
    data.loc[visible_mask, "selected"] = appids.loc[visible_mask].isin(selected_set).map(lambda value: "True" if value else "False")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"visible": int(visible_mask.sum()), "selected": int(_selected_mask(data).sum())}


def bulk_update_collected_selection(csv_path: Path, filtered: pd.DataFrame, mode: str) -> dict:
    data = load_collected(csv_path)
    if data.empty or filtered.empty:
        return {"visible": 0, "selected": 0}

    visible_appids = {
        str(appid or "").strip()
        for appid in filtered.get("appid", pd.Series(dtype=str)).astype(str).tolist()
        if str(appid or "").strip()
    }
    if not visible_appids:
        return {"visible": 0, "selected": int(_selected_mask(data).sum())}

    current_selected = set(data.loc[_selected_mask(data), "appid"].astype(str).str.strip().tolist())
    if mode == "select_visible":
        next_selected = current_selected | visible_appids
    elif mode == "select_demo":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")))
    elif mode == "select_demo_self":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")) and _is_self_published(row))
    elif mode == "select_unreleased_demo":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")) and _is_unreleased_v074(row))
    elif mode == "clear_visible":
        next_selected = current_selected - visible_appids
    elif mode == "invert_visible":
        next_selected = set(current_selected)
        for appid in visible_appids:
            if appid in next_selected:
                next_selected.remove(appid)
            else:
                next_selected.add(appid)
    else:
        next_selected = current_selected

    appids = data["appid"].astype(str).str.strip()
    visible_mask = appids.isin(visible_appids)
    data.loc[visible_mask, "selected"] = appids.loc[visible_mask].isin(next_selected).map(lambda value: "True" if value else "False")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"visible": len(visible_appids), "selected": int(_selected_mask(data).sum())}


def enrich_collected_basic_info(csv_path: Path, appids: list[str] | None = None) -> dict:
    data = load_collected(csv_path)
    if data.empty:
        return {"requested": 0, "updated": 0, "failed": 0, "cache_hit": 0}

    target_appids = _target_appids(data, appids)
    results = enrich_appids_basic(target_appids)
    stats = {"requested": len(target_appids), "updated": 0, "failed": 0, "cache_hit": 0}
    for appid, info in results.items():
        if info.get("cache_hit"):
            stats["cache_hit"] += 1
        mask = data["appid"].astype(str).str.strip().eq(str(appid))
        if not mask.any():
            continue
        if not info.get("success"):
            stats["failed"] += 1
            continue
        index = data.loc[mask].index[0]
        for source_field, target_field in [
            ("game_name", "game_name"),
            ("steam_url", "steam_url"),
            ("developer", "developer"),
            ("publisher", "publisher"),
            ("release_status", "release_status"),
            ("release_date", "release_date"),
            ("has_demo", "has_demo"),
            ("supports_schinese", "supports_schinese"),
            ("genres_tags", "genres_tags"),
            ("review_score", "review_score"),
            ("review_count", "review_count"),
        ]:
            value = _clean(info.get(source_field))
            if value:
                data.loc[index, target_field] = value
        suggestion, reason = suggest_import(data.loc[index].to_dict())
        data.loc[index, "import_suggestion"] = suggestion
        data.loc[index, "import_reason"] = reason
        stats["updated"] += 1
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return stats


def apply_import_suggestions(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    if output.empty:
        return output
    for index, row in output.iterrows():
        suggestion, reason = suggest_import(row.to_dict())
        output.loc[index, "import_suggestion"] = suggestion
        output.loc[index, "import_reason"] = reason
    return output


def filter_collected(
    data: pd.DataFrame,
    *,
    demo_only: bool = False,
    unreleased_only: bool = False,
    self_published_only: bool = False,
    schinese_only: bool = False,
    observation_only: bool = False,
    exclude_reference: bool = False,
) -> pd.DataFrame:
    filtered = data.copy()
    if demo_only:
        filtered = filtered.loc[filtered["has_demo"].astype(str).str.strip().eq("是")]
    if unreleased_only:
        filtered = filtered.loc[filtered.apply(lambda row: _is_unreleased_v074(row.to_dict()), axis=1)]
    if self_published_only:
        filtered = filtered.loc[filtered.apply(lambda row: _is_self_published(row.to_dict()), axis=1)]
    if schinese_only:
        filtered = filtered.loc[filtered["supports_schinese"].astype(str).str.strip().eq("是")]
    if observation_only:
        filtered = filtered.loc[filtered["import_suggestion"].astype(str).isin({"候选池观察 / 值得联系", "待试玩"})]
    if exclude_reference:
        filtered = filtered.loc[~filtered["import_suggestion"].astype(str).eq("竞品参考")]
    return filtered.copy()


def collected_display_data(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in data.iterrows():
        rows.append(
            {
                "是否选择": False,
                "游戏名": row.get("game_name", "") or f"AppID {row.get('appid', '')}",
                "AppID": row.get("appid", ""),
                "来源页面": row.get("source_page_title", "") or row.get("source_page_url", ""),
                "开发商": row.get("developer", ""),
                "发行商": row.get("publisher", ""),
                "发售状态": row.get("release_status", "") or row.get("release_date", ""),
                "Demo": row.get("has_demo", ""),
                "简中": row.get("supports_schinese", ""),
                "类型": row.get("genres_tags", ""),
                "评测": row.get("review_score", ""),
                "评论数": row.get("review_count", ""),
                "导入建议": row.get("import_suggestion", ""),
                "建议理由": row.get("import_reason", ""),
                "Steam 链接": row.get("steam_url", ""),
            }
        )
    return pd.DataFrame(rows)


def collected_display_data_v074(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in data.iterrows():
        rows.append(
            {
                "是否选择": _truthy(row.get("selected")),
                "游戏名": row.get("game_name", "") or f"AppID {row.get('appid', '')}",
                "AppID": row.get("appid", ""),
                "来源": row.get("source_page_title", "") or row.get("source_page_url", ""),
                "开发商": row.get("developer", ""),
                "发行商": row.get("publisher", ""),
                "发售状态": row.get("release_status", "") or row.get("release_date", ""),
                "Demo": row.get("has_demo", ""),
                "简中": row.get("supports_schinese", ""),
                "类型": row.get("genres_tags", ""),
                "评测": row.get("review_score", ""),
                "评论数": row.get("review_count", ""),
                "导入建议": row.get("import_suggestion", ""),
                "建议理由": row.get("import_reason", ""),
                "Steam 链接": row.get("steam_url", ""),
            }
        )
    return pd.DataFrame(rows)


def suggest_import(row: dict) -> tuple[str, str]:
    has_demo = _clean(row.get("has_demo")) == "是"
    supports_schinese = _clean(row.get("supports_schinese")) == "是"
    developer = _clean(row.get("developer"))
    publisher = _clean(row.get("publisher"))
    review_count = _parse_int(row.get("review_count"))

    if _is_obvious_reference(row, review_count):
        return "竞品参考", "评论数较高或项目较成熟，适合作为竞品参考，不作为放弃判断。"
    if has_demo and _is_unreleased_v074(row):
        return "待试玩", "有 Demo 且仍处于未发售、Coming Soon 或 TBA 状态，适合进入试玩队列。"
    if has_demo and supports_schinese and developer and (not publisher or publisher == developer):
        return "候选池观察 / 值得联系", "有 Demo、支持简中，且看起来为开发商自发行或发行信息为空。"
    if publisher and developer and publisher != developer:
        return "竞品参考", "开发商与发行商不同，优先作为发行竞品或市场参考。"
    return "待补资料", "当前资料不足，需要补项目画像后再判断。"


def ensure_collected_csv(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=STEAM_BROWSER_COLLECTED_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")


def steam_url_from_appid(appid: str) -> str:
    return f"https://store.steampowered.com/app/{str(appid).strip()}/"


def _read_active_page(debug_port: int) -> dict:
    if not _cdp_available(debug_port):
        raise RuntimeError(CDP_CONNECT_ERROR_MESSAGE)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
        try:
            pages = []
            for context in browser.contexts:
                pages.extend([page for page in context.pages if not page.is_closed()])
            if not pages:
                raise RuntimeError("未检测到可读取的浏览器页面。")
            page = _select_page(pages)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            links = page.eval_on_selector_all(
                "a[href*='/app/']",
                "els => els.map(el => el.href)",
            )
            return {
                "url": page.url,
                "title": page.title(),
                "links": links,
            }
        finally:
            disconnect = getattr(browser, "disconnect", None)
            if callable(disconnect):
                disconnect()


def _select_page(pages: list) -> object:
    steam_pages = [page for page in pages if "store.steampowered.com" in str(page.url)]
    return (steam_pages or pages)[-1]


def _cdp_available(debug_port: int) -> bool:
    if not _port_open(debug_port):
        return False
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/version", timeout=1.5) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError, TimeoutError):
        return False


def _port_open(debug_port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", int(debug_port)), timeout=0.5):
            return True
    except OSError:
        return False


def _format_cdp_error(exc: Exception) -> str:
    text = str(exc or "").strip()
    if not text or CDP_CONNECT_ERROR_MESSAGE in text or "ECONNREFUSED" in text or "connect" in text.casefold():
        return CDP_CONNECT_ERROR_MESSAGE
    return f"读取当前页面失败：{text}"


def _normalize_row(raw: dict) -> dict:
    row = {column: _clean(raw.get(column)) for column in STEAM_BROWSER_COLLECTED_COLUMNS}
    if row["appid"] and not row["steam_url"]:
        row["steam_url"] = steam_url_from_appid(row["appid"])
    if not row["collected_at"]:
        row["collected_at"] = _now_text()
    if not row["import_suggestion"]:
        row["import_suggestion"], row["import_reason"] = suggest_import(row)
    return row


def _target_appids(data: pd.DataFrame, appids: list[str] | None) -> list[str]:
    if appids:
        candidates = [str(appid or "").strip() for appid in appids]
    else:
        candidates = data["appid"].astype(str).str.strip().tolist()
    output = []
    seen = set()
    for appid in candidates:
        if appid and appid.isdigit() and appid not in seen:
            seen.add(appid)
            output.append(appid)
    return output


def _is_unreleased(row: dict) -> bool:
    text = " ".join([_clean(row.get("release_status")), _clean(row.get("release_date"))]).casefold()
    return any(token in text for token in ["coming soon", "tba", "to be announced", "即将推出", "未发售", "待定"])


def _is_unreleased_v074(row: dict) -> bool:
    text = " ".join([_clean(row.get("release_status")), _clean(row.get("release_date"))]).casefold()
    tokens = ["coming soon", "tba", "to be announced", "即将推出", "未发售", "待定", "未来"]
    if any(token in text for token in tokens):
        return True
    parsed_date = pd.to_datetime(_clean(row.get("release_date")), errors="coerce")
    if pd.notna(parsed_date):
        return parsed_date.date() > datetime.now().date()
    return False


def _is_self_published(row: dict) -> bool:
    developer = _clean(row.get("developer"))
    publisher = _clean(row.get("publisher"))
    return bool(developer and (not publisher or publisher == developer))


def _is_obvious_reference(row: dict, review_count: int) -> bool:
    if review_count >= 50000:
        return True
    status_text = " ".join([_clean(row.get("release_status")), _clean(row.get("release_date"))]).casefold()
    if review_count >= 5000 and not _is_unreleased_v074(row):
        return True
    return any(token in status_text for token in ["2018", "2019", "2020", "2021"])


def _matching_appids(data: pd.DataFrame, predicate) -> set[str]:
    matched: set[str] = set()
    for _, row in data.iterrows():
        row_dict = row.to_dict()
        appid = _clean(row_dict.get("appid"))
        if appid and predicate(row_dict):
            matched.add(appid)
    return matched


def _selected_mask(data: pd.DataFrame) -> pd.Series:
    if "selected" not in data.columns:
        return pd.Series(False, index=data.index)
    return data["selected"].map(_truthy)


def _is_yes(value) -> bool:
    return _clean(value) in {"是", "Yes", "yes", "true", "True", "1", "有", "有 Demo"}


def _truthy(value) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "是", "有"}


def _parse_int(value) -> int:
    digits = re.sub(r"[^\d]", "", str(value or ""))
    return int(digits) if digits else 0


def _clean(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"None", "nan", "[]"} else text


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
