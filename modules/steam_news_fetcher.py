from __future__ import annotations

from datetime import datetime, timedelta
from html import unescape
from pathlib import Path
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


STEAM_NEWS_API_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
REQUEST_TIMEOUT_SECONDS = 10
CACHE_TTL_HOURS = 6
MAJOR_UPDATE_KEYWORDS = [
    "update",
    "version",
    "patch",
    "major",
    "anniversary",
    "new content",
    "release",
    "launch",
    "demo",
    "playtest",
]


def get_steam_news_for_app(
    appid: str,
    cache_dir: Path,
    count: int = 5,
    maxlength: int = 500,
    force_refresh: bool = False,
) -> dict:
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return _empty_result(clean_appid, "invalid", "AppID 无效")

    cache_path = cache_dir / f"{clean_appid}.json"
    cached = _load_cache(cache_path)
    if cached and not force_refresh and _cache_is_fresh(cached):
        cached = _normalize_result(cached)
        cached["status"] = "cache"
        cached["error_message"] = ""
        return cached

    try:
        result = _fetch_steam_news(clean_appid, count=count, maxlength=maxlength)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        if cached:
            cached = _normalize_result(cached)
            cached["status"] = "stale_cache"
            cached["error_message"] = f"获取失败，使用旧缓存：{exc}"
            return cached
        return _empty_result(clean_appid, "error", f"获取失败：{exc}")

    _save_cache(cache_path, result)
    return result


def build_steam_news_markdown_section(news_result: dict | None) -> str:
    result = _normalize_result(news_result or {})
    items = result.get("items", [])
    if not items:
        return "## Steam 动态 / 公告\n\n暂无 Steam 动态记录，可能是接口无返回或项目未发布公告。\n"

    lines = ["## Steam 近期动态", ""]
    for item in items[:3]:
        title = _display(item.get("title"))
        date = _display(item.get("readable_date") or item.get("date"))
        source = _display(item.get("feedlabel") or item.get("feedname"))
        summary = _display(item.get("clean_summary") or item.get("summary") or item.get("contents"))
        url = str(item.get("url", "") or "").strip()
        major_label = "重大更新候选" if item.get("is_major_update_candidate") else "普通动态"
        lines.append(f"- {title}")
        lines.append(f"  - 日期：{date}")
        lines.append(f"  - 类型 / feedname：{source}")
        lines.append(f"  - 标记：{major_label}")
        lines.append(f"  - 摘要：{_truncate(summary, 200)}")
        if url:
            lines.append(f"  - 链接：{url}")
    lines.append("")
    return "\n".join(lines)


def steam_news_status_label(news_result: dict | None) -> str:
    status = str((news_result or {}).get("status", "") or "").strip()
    items = (news_result or {}).get("items", [])
    if status == "cache":
        return "使用缓存"
    if status == "stale_cache":
        return "使用旧缓存"
    if status == "success" and items:
        return "已获取"
    if status in {"success", "empty"}:
        return "暂无"
    if status in {"error", "invalid"}:
        return "获取失败"
    return "暂无"


def _fetch_steam_news(appid: str, count: int, maxlength: int) -> dict:
    params = {
        "appid": appid,
        "count": str(max(1, min(int(count or 5), 20))),
        "maxlength": str(max(100, min(int(maxlength or 500), 1000))),
        "format": "json",
    }
    request = Request(
        STEAM_NEWS_API_URL + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.6.12 (+steam-news)",
            "Accept": "application/json,text/plain;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8", errors="replace"))

    appnews = payload.get("appnews") if isinstance(payload, dict) else {}
    raw_items = appnews.get("newsitems") if isinstance(appnews, dict) else []
    items = [_normalize_news_item(item, maxlength=500) for item in raw_items if isinstance(item, dict)]
    result = {
        "appid": appid,
        "status": "success" if items else "empty",
        "items": items,
        "fetched_at": _now(),
        "error_message": "",
    }
    return _normalize_result(result)


def _normalize_news_item(item: dict, maxlength: int = 500) -> dict:
    timestamp = item.get("date")
    date_text = ""
    try:
        date_text = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, OSError):
        date_text = str(timestamp or "")
    raw_contents = str(item.get("contents") or "")
    clean_summary = clean_steam_news_text(raw_contents, max_length=350)
    is_major = is_major_update_candidate(item.get("title"), raw_contents)
    return {
        "gid": str(item.get("gid", "") or ""),
        "title": _clean_text(item.get("title"), 180),
        "url": str(item.get("url", "") or "").strip(),
        "is_external_url": bool(item.get("is_external_url", False)),
        "author": _clean_text(item.get("author"), 80),
        "contents": clean_steam_news_text(raw_contents, max_length=maxlength),
        "clean_summary": clean_summary,
        "is_major_update_candidate": is_major,
        "raw_contents": raw_contents[:2000],
        "feedlabel": _clean_text(item.get("feedlabel"), 80),
        "date": date_text,
        "readable_date": date_text,
        "feedname": _clean_text(item.get("feedname"), 80),
    }


def _normalize_result(result: dict) -> dict:
    appid = str(result.get("appid", "") or "")
    items = result.get("items", [])
    normalized_items = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                raw_contents = str(item.get("raw_contents") or item.get("contents") or item.get("clean_summary") or item.get("summary") or "")
                clean_summary = clean_steam_news_text(raw_contents, max_length=350)
                normalized_items.append(
                    {
                        "gid": str(item.get("gid", "") or ""),
                        "title": _clean_text(item.get("title"), 180),
                        "url": str(item.get("url", "") or "").strip(),
                        "is_external_url": bool(item.get("is_external_url", False)),
                        "author": _clean_text(item.get("author"), 80),
                        "contents": clean_steam_news_text(raw_contents, max_length=500),
                        "clean_summary": clean_summary,
                        "raw_contents": raw_contents[:2000],
                        "is_major_update_candidate": bool(item.get("is_major_update_candidate")) or is_major_update_candidate(item.get("title"), raw_contents),
                        "feedlabel": _clean_text(item.get("feedlabel"), 80),
                        "date": _clean_text(item.get("date"), 40),
                        "readable_date": _clean_text(item.get("readable_date") or item.get("date"), 40),
                        "feedname": _clean_text(item.get("feedname"), 80),
                    }
                )
    status = str(result.get("status", "") or ("success" if normalized_items else "empty"))
    return {
        "appid": appid,
        "status": status,
        "items": normalized_items,
        "fetched_at": str(result.get("fetched_at", "") or ""),
        "error_message": str(result.get("error_message", "") or ""),
    }


def _empty_result(appid: str, status: str, error_message: str = "") -> dict:
    return {
        "appid": str(appid or ""),
        "status": status,
        "items": [],
        "fetched_at": _now(),
        "error_message": error_message,
    }


def clean_steam_news_text(text: str, max_length: int = 500) -> str:
    clean = _unescape_entities(str(text or ""))
    clean = clean.replace("\\r", "\n").replace("\\n", "\n").replace("\r", "\n")
    clean = re.sub(r"(?is)<(script|style|iframe)\b.*?</\1>", " ", clean)
    clean = re.sub(r"(?is)<img\b[^>]*>", " ", clean)
    clean = re.sub(r"(?i)<\s*(br|/p|/div|/li)\s*/?>", "\n", clean)
    clean = re.sub(r"(?is)<a\b[^>]*>(.*?)</a>", r"\1", clean)
    clean = re.sub(r"<[^>]+>", " ", clean)

    clean = re.sub(r"(?is)\[img\].*?\[/img\]", " ", clean)
    clean = re.sub(r"(?is)\[url=[^\]]+\](.*?)\[/url\]", r"\1", clean)
    clean = re.sub(r"(?is)\[url\]https?://[^\[]+\[/url\]", " ", clean)
    clean = re.sub(r"(?i)\[\*\]", "\n- ", clean)
    clean = re.sub(r"(?i)\[/?(?:b|i|u|h\d|list|olist|quote|code|previewyoutube|table|tr|td|th|strike|spoiler)[^\]]*\]", " ", clean)
    clean = re.sub(r"\[[^\]]{1,40}\]", " ", clean)

    clean = re.sub(r"https?://\S+", " ", clean)
    clean = re.sub(r"www\.\S+", " ", clean)
    clean = re.sub(r"(?m)^\s*[\\]+\s*", "", clean)
    clean = re.sub(r"(?<=\s)\\+(?=\s|$)", " ", clean)
    clean = clean.replace("\\", "")
    clean = re.sub(r"[ \t\u00a0]+", " ", clean)
    clean = re.sub(r"\n\s*\n+", "\n", clean)
    clean = re.sub(r"\s*\n\s*", " ", clean)
    clean = clean.strip(" \t\n-")
    if not clean:
        return "暂无摘要"
    if len(clean) > max_length:
        return clean[: max(0, max_length - 1)].rstrip() + "..."
    return clean


def is_major_update_candidate(title, content) -> bool:
    text = f"{title or ''} {content or ''}".casefold()
    return any(keyword in text for keyword in MAJOR_UPDATE_KEYWORDS)


def _truncate(value: str, max_length: int) -> str:
    text = str(value or "").strip()
    if len(text) <= max_length:
        return text
    return text[: max(0, max_length - 1)].rstrip() + "..."


def _clean_text(value, maxlength: int) -> str:
    text = re.sub(r"\s+", " ", _unescape_entities(str(value or ""))).strip()
    if len(text) > maxlength:
        return text[: max(0, maxlength - 1)].rstrip() + "..."
    return text


def _unescape_entities(value: str) -> str:
    text = str(value or "")
    for _ in range(3):
        next_text = unescape(text)
        if next_text == text:
            break
        text = next_text
    return text.replace("\xa0", " ")


def _display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未记录"


def _load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_cache(cache_path: Path, result: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        cache_path.write_text(json.dumps(_normalize_result(result), ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _cache_is_fresh(cache: dict) -> bool:
    fetched_at = str(cache.get("fetched_at", "") or "")
    try:
        fetched_time = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    return datetime.now() - fetched_time <= timedelta(hours=CACHE_TTL_HOURS)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
