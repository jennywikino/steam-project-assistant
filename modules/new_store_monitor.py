from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from modules.steam_app_enricher import enrich_appids_basic


STEAMDB_HOME_URL = "https://steamdb.info/"
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_SLEEP_SECONDS = 0.5
USER_AGENT = "steam-project-assistant/0.7.3 (+new-store-monitor)"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36 steam-project-assistant/0.7.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
    "Cache-Control": "no-cache",
    "Referer": "https://steamdb.info/",
}

NEW_STORE_EVENT_COLUMNS = [
    "appid",
    "name",
    "event_text",
    "app_type",
    "event_time_text",
    "steamdb_url",
    "steam_url",
    "image_url",
    "first_seen_at",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "short_desc",
    "header_image",
    "is_self_published",
    "is_unreleased_or_tba",
    "has_schinese",
    "monitor_suggestion",
    "monitor_reason",
]

DISPLAY_COLUMNS = [
    "selected",
    "name",
    "appid",
    "event_text",
    "event_time_text",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "monitor_suggestion",
    "monitor_reason",
    "steam_url",
    "steamdb_url",
]

FIELD_LABELS = {
    "selected": "是否选择",
    "name": "游戏名",
    "appid": "AppID",
    "event_text": "事件",
    "event_time_text": "事件时间",
    "developer": "开发商",
    "publisher": "发行商",
    "release_status": "发售状态",
    "has_demo": "Demo",
    "supports_schinese": "简中",
    "genres_tags": "类型",
    "monitor_suggestion": "初筛建议",
    "monitor_reason": "建议理由",
    "steam_url": "Steam",
    "steamdb_url": "SteamDB",
}

EXCLUDED_TYPE_KEYWORDS = ["demo", "dlc", "beta", "tool", "soundtrack"]
EXCLUDED_EVENT_KEYWORDS = ["removal", "removed", "delete"]
UNRELEASED_MARKERS = ["coming soon", "tba", "即将推出", "待定"]


@dataclass
class NewStoreFetchResult:
    success: bool
    message: str
    rows: list[dict]


class _SteamDBRecentEventsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict] = []
        self._current_row: dict | None = None
        self._current_cell: dict | None = None
        self._current_link: str = ""
        self._current_image: str = ""
        self._in_table = False
        self._table_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "table":
            classes = attr.get("class", "")
            if "table" in classes:
                self._in_table = True
                self._table_depth = 1
            elif self._in_table:
                self._table_depth += 1
            return
        if not self._in_table:
            return
        if tag == "tr":
            self._current_row = {"cells": [], "links": [], "images": []}
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = {"text": "", "links": [], "images": []}
        elif tag == "a" and self._current_cell is not None:
            href = attr.get("href", "")
            if href:
                self._current_link = href
                self._current_cell["links"].append(href)
                self._current_row["links"].append(href)
        elif tag == "img" and self._current_cell is not None:
            src = attr.get("src", "") or attr.get("data-src", "")
            if src:
                self._current_image = src
                self._current_cell["images"].append(src)
                self._current_row["images"].append(src)

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._in_table:
            self._table_depth -= 1
            if self._table_depth <= 0:
                self._in_table = False
            return
        if not self._in_table:
            return
        if tag == "a":
            self._current_link = ""
        elif tag == "img":
            self._current_image = ""
        elif tag in {"td", "th"} and self._current_row is not None and self._current_cell is not None:
            cell = self._current_cell
            cell["text"] = _normalize_space(cell.get("text", ""))
            self._current_row["cells"].append(cell)
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_row.get("cells"):
                self.rows.append(self._current_row)
            self._current_row = None

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell["text"] += data


def fetch_recent_new_store_games() -> NewStoreFetchResult:
    try:
        html = _fetch_steamdb_home()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return NewStoreFetchResult(False, f"SteamDB Recent App Events 获取失败：{exc}", [])
    if _looks_like_anti_bot_page(html):
        return NewStoreFetchResult(False, "SteamDB 返回浏览器验证页，本次无法自动抓取；请稍后在浏览器中人工查看 Recent App Events。", [])
    rows = parse_recent_new_store_games(html)
    return NewStoreFetchResult(True, f"已抓取最近新上架 Game：{len(rows)} 条。", rows)


def parse_recent_new_store_games(html: str) -> list[dict]:
    parser = _SteamDBRecentEventsParser()
    parser.feed(html)
    results: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for raw_row in parser.rows:
        parsed = _parse_recent_event_row(raw_row)
        if not parsed:
            continue
        key = (parsed["appid"], parsed["event_text"])
        if key in seen:
            continue
        seen.add(key)
        results.append(parsed)
    if not results:
        for parsed in _parse_recent_event_fallback(html):
            key = (parsed["appid"], parsed["event_text"])
            if key in seen:
                continue
            seen.add(key)
            results.append(parsed)
    return results


def load_new_store_events(csv_path: Path) -> pd.DataFrame:
    ensure_new_store_events_csv(csv_path)
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=NEW_STORE_EVENT_COLUMNS)
    for column in NEW_STORE_EVENT_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, NEW_STORE_EVENT_COLUMNS].copy()


def save_new_store_events(csv_path: Path, rows: list[dict]) -> dict:
    ensure_new_store_events_csv(csv_path)
    data = load_new_store_events(csv_path)
    now = _now_text()
    existing_keys = set(zip(data["appid"].astype(str), data["event_text"].astype(str)))
    new_rows = []
    for row in rows:
        normalized = _normalize_event_record(row)
        key = (normalized["appid"], normalized["event_text"])
        if not normalized["appid"] or not normalized["event_text"] or key in existing_keys:
            continue
        normalized["first_seen_at"] = normalized.get("first_seen_at") or now
        new_rows.append(normalized)
        existing_keys.add(key)
    if new_rows:
        data = pd.concat([data, pd.DataFrame(new_rows)], ignore_index=True)
        data = apply_monitor_suggestions(data)
        data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"created": len(new_rows), "total": len(data)}


def enrich_new_store_events_basic_info(csv_path: Path, appids: list[str] | None = None) -> dict:
    data = load_new_store_events(csv_path)
    if data.empty:
        return {"requested": 0, "updated": 0, "failed": 0}
    target_appids = [str(appid or "").strip() for appid in (appids or data["appid"].tolist())]
    target_appids = [appid for appid in dict.fromkeys(target_appids) if appid]
    results = enrich_appids_basic(target_appids)
    updated = 0
    failed = 0
    for index, row in data.iterrows():
        appid = str(row.get("appid", "") or "").strip()
        if appid not in results:
            continue
        result = results[appid]
        if result.get("success"):
            updated += 1
        else:
            failed += 1
        _fill_if_available(data, index, "name", result.get("game_name"))
        _fill_if_available(data, index, "developer", result.get("developer"))
        _fill_if_available(data, index, "publisher", result.get("publisher"))
        _fill_if_available(data, index, "release_status", result.get("release_status"))
        _fill_if_available(data, index, "release_date", result.get("release_date"))
        _fill_if_available(data, index, "has_demo", result.get("has_demo"))
        _fill_if_available(data, index, "supports_schinese", result.get("supports_schinese"))
        _fill_if_available(data, index, "genres_tags", result.get("genres_tags"))
        _fill_if_available(data, index, "short_desc", result.get("short_desc"))
        _fill_if_available(data, index, "header_image", result.get("header_image"))
    data = apply_monitor_suggestions(data)
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"requested": len(target_appids), "updated": updated, "failed": failed}


def apply_monitor_suggestions(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    for column in NEW_STORE_EVENT_COLUMNS:
        if column not in output.columns:
            output[column] = ""
    for index, row in output.iterrows():
        suggestion = build_monitor_suggestion(row.to_dict())
        output.loc[index, "is_self_published"] = suggestion["is_self_published"]
        output.loc[index, "is_unreleased_or_tba"] = suggestion["is_unreleased_or_tba"]
        output.loc[index, "has_schinese"] = suggestion["has_schinese"]
        output.loc[index, "monitor_suggestion"] = suggestion["monitor_suggestion"]
        output.loc[index, "monitor_reason"] = suggestion["monitor_reason"]
    return output


def build_monitor_suggestion(row: dict) -> dict:
    developer = _clean(row.get("developer"))
    publisher = _clean(row.get("publisher"))
    release_text = f"{_clean(row.get('release_status'))} {_clean(row.get('release_date'))}"
    has_demo = _clean(row.get("has_demo"))
    supports_schinese = _clean(row.get("supports_schinese"))
    is_self_published = "是" if (not publisher or (developer and publisher == developer)) else "否"
    is_unreleased = "是" if _is_unreleased_or_tba(release_text) else "否"
    has_schinese = "是" if supports_schinese == "是" else "否"

    reasons = []
    if not developer or not publisher or not release_text.strip():
        suggestion = "待补资料"
        reasons.append("开发商、发行商或发售状态资料不足")
    elif is_self_published == "否":
        suggestion = "竞品参考"
        reasons.append("已有明显发行商或发行关系，优先作为竞品参考")
    elif is_self_published == "是" and is_unreleased == "是" and (has_demo == "是" or has_schinese == "是"):
        suggestion = "候选池观察"
        reasons.append("自发行 + 未发售/TBA，且有 Demo 或支持简中")
    elif is_self_published == "是" and is_unreleased == "是":
        suggestion = "待补资料"
        reasons.append("自发行且未发售/TBA，但还需要确认 Demo、简中和项目画像")
    else:
        suggestion = "竞品参考"
        reasons.append("已发售或缺少近期发行跟进信号")

    return {
        "is_self_published": is_self_published,
        "is_unreleased_or_tba": is_unreleased,
        "has_schinese": has_schinese,
        "monitor_suggestion": suggestion,
        "monitor_reason": "；".join(reasons),
    }


def filter_new_store_events(
    data: pd.DataFrame,
    *,
    self_published_only: bool = False,
    unreleased_only: bool = False,
    demo_only: bool = False,
    schinese_only: bool = False,
    observation_only: bool = False,
) -> pd.DataFrame:
    output = apply_monitor_suggestions(data)
    if self_published_only:
        output = output.loc[output["is_self_published"].astype(str).eq("是")]
    if unreleased_only:
        output = output.loc[output["is_unreleased_or_tba"].astype(str).eq("是")]
    if demo_only:
        output = output.loc[output["has_demo"].astype(str).eq("是")]
    if schinese_only:
        output = output.loc[output["supports_schinese"].astype(str).eq("是")]
    if observation_only:
        output = output.loc[output["monitor_suggestion"].astype(str).eq("候选池观察")]
    return output.copy()


def new_store_events_display_data(data: pd.DataFrame) -> pd.DataFrame:
    output = apply_monitor_suggestions(data)
    if output.empty:
        return pd.DataFrame(columns=[FIELD_LABELS[column] for column in DISPLAY_COLUMNS])
    output = output.copy()
    output["selected"] = False
    columns = [column for column in DISPLAY_COLUMNS if column in output.columns]
    return output.loc[:, columns].fillna("").rename(columns=FIELD_LABELS)


def ensure_new_store_events_csv(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=NEW_STORE_EVENT_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")


def _fetch_steamdb_home() -> str:
    request = Request(
        STEAMDB_HOME_URL,
        headers=REQUEST_HEADERS,
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        time.sleep(REQUEST_SLEEP_SECONDS)
        return response.read().decode("utf-8", errors="replace")


def _parse_recent_event_row(raw_row: dict) -> dict | None:
    cells = raw_row.get("cells") or []
    row_text = _normalize_space(" ".join(str(cell.get("text", "")) for cell in cells))
    if "New on store:" not in row_text:
        return None
    if any(keyword.lower() in row_text.lower() for keyword in EXCLUDED_EVENT_KEYWORDS):
        return None
    appid = _first_appid(raw_row.get("links") or [])
    if not appid:
        return None
    app_type = _parse_app_type(row_text)
    if app_type.casefold() != "game":
        return None
    name = _parse_event_name(row_text, app_type)
    if not name or any(keyword in name.casefold() for keyword in EXCLUDED_TYPE_KEYWORDS):
        return None
    event_time_text = _parse_event_time(cells)
    image_url = _normalize_steamdb_url((raw_row.get("images") or [""])[0])
    return {
        "appid": appid,
        "name": name,
        "event_text": f"New on store: {name}",
        "app_type": app_type,
        "event_time_text": event_time_text,
        "steamdb_url": f"https://steamdb.info/app/{appid}/",
        "steam_url": f"https://store.steampowered.com/app/{appid}/",
        "image_url": image_url,
        "first_seen_at": _now_text(),
    }


def _parse_recent_event_fallback(html: str) -> list[dict]:
    output = []
    text = _normalize_space(re.sub(r"<[^>]+>", " ", html))
    for match in re.finditer(r"New on store:\s*(.+?)\s+Game\b", text, flags=re.IGNORECASE):
        name = _normalize_space(match.group(1).strip(" -–—"))
        if not name or any(keyword in name.casefold() for keyword in EXCLUDED_TYPE_KEYWORDS):
            continue
        start = max(match.start() - 1500, 0)
        end = min(match.end() + 1500, len(html))
        appid = _first_appid(re.findall(r"href=[\"']([^\"']+)[\"']", html[start:end]))
        if not appid:
            continue
        output.append(
            {
                "appid": appid,
                "name": name,
                "event_text": f"New on store: {name}",
                "app_type": "Game",
                "event_time_text": "",
                "steamdb_url": f"https://steamdb.info/app/{appid}/",
                "steam_url": f"https://store.steampowered.com/app/{appid}/",
                "image_url": "",
                "first_seen_at": _now_text(),
            }
        )
    return output


def _parse_event_name(row_text: str, app_type: str) -> str:
    if app_type:
        match = re.search(rf"New on store:\s*(.+)\s+{re.escape(app_type)}\b", row_text, flags=re.IGNORECASE)
    else:
        match = re.search(r"New on store:\s*(.+)$", row_text, flags=re.IGNORECASE)
    if not match:
        return ""
    return _normalize_space(match.group(1).strip(" -–—"))


def _parse_app_type(row_text: str) -> str:
    for app_type in ["Game", "Demo", "DLC", "Beta", "Tool", "Soundtrack"]:
        if re.search(rf"\b{re.escape(app_type)}\b", row_text, flags=re.IGNORECASE):
            return app_type
    return ""


def _parse_event_time(cells: list[dict]) -> str:
    for cell in cells:
        text = _normalize_space(str(cell.get("text", "")))
        if re.search(r"\b(?:ago|today|yesterday|\d{4}-\d{2}-\d{2}|\d+\s+(?:minute|hour|day)s?)\b", text, flags=re.IGNORECASE):
            return text
    return ""


def _first_appid(links: list[str]) -> str:
    for href in links:
        match = re.search(r"/app/(\d{3,10})", href)
        if match:
            return match.group(1)
    return ""


def _normalize_event_record(row: dict) -> dict:
    output = {column: _clean(row.get(column)) for column in NEW_STORE_EVENT_COLUMNS}
    appid = output.get("appid", "")
    output["steamdb_url"] = output.get("steamdb_url") or (f"https://steamdb.info/app/{appid}/" if appid else "")
    output["steam_url"] = output.get("steam_url") or (f"https://store.steampowered.com/app/{appid}/" if appid else "")
    return output


def _fill_if_available(data: pd.DataFrame, index, column: str, value) -> None:
    text = _clean(value)
    if text:
        data.loc[index, column] = text


def _is_unreleased_or_tba(text: str) -> bool:
    clean = _clean(text).casefold()
    if any(marker in clean for marker in UNRELEASED_MARKERS):
        return True
    if re.fullmatch(r"\s*(?:20\d{2})\s*", clean):
        return True
    return False


def _normalize_steamdb_url(url: str) -> str:
    value = _clean(url)
    if not value:
        return ""
    if value.startswith("//"):
        return "https:" + value
    if value.startswith("/"):
        return "https://steamdb.info" + value
    return value


def _looks_like_anti_bot_page(html: str) -> bool:
    text = html.casefold()
    return "checking your browser" in text or "cf_chl" in text or "cloudflare" in text


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(str(text or ""))).strip()


def _clean(value) -> str:
    text = str(value or "").strip()
    if text.lower() in {"none", "nan", "null"}:
        return ""
    return text


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
