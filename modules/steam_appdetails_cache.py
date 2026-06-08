from datetime import datetime, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


STORE_API_URL = "https://store.steampowered.com/api/appdetails"
APPDETAILS_CACHE_TTL_DAYS = 7
REQUEST_TIMEOUT_SECONDS = 10


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        clean = data.strip()
        if clean:
            self.parts.append(clean)

    def text(self) -> str:
        return " ".join(self.parts)


def get_cached_appdetails_summary(appid: str, cache_path: Path, force_refresh: bool = False) -> dict:
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return _empty_summary(clean_appid, "未获取：AppID 无效")

    cache = _load_cache(cache_path)
    entry = cache.get(clean_appid, {})
    if entry and not force_refresh and _entry_is_fresh(entry) and not _entry_missing_required_fields(entry):
        entry = dict(entry)
        entry["cache_status"] = "cache_hit"
        return entry

    refreshed = _fetch_appdetails_summary(clean_appid)
    if entry and not force_refresh and _entry_missing_required_fields(entry):
        refreshed["detail_fetch_status"] = "cache_missing_fields_refetched" if refreshed.get("success") else refreshed.get("detail_fetch_status", "")
    refreshed["cache_status"] = "refetched" if force_refresh else "fetched"
    cache[clean_appid] = refreshed
    _save_cache(cache_path, cache)
    return refreshed


def debug_appdetails_summary(appid: str, cache_path: Path, debug_dir: Path) -> dict:
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return _empty_summary(clean_appid, "未获取：AppID 无效")

    checked_at = datetime.now().isoformat(timespec="seconds")
    try:
        raw = _fetch_appdetails(clean_appid)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        summary = _empty_summary(clean_appid, f"获取失败：{exc}", checked_at=checked_at)
        summary["cache_status"] = "debug_fetch_failed"
        return summary

    _save_debug_raw_appdetails(debug_dir, clean_appid, raw)
    summary = _summary_from_raw_appdetails(clean_appid, raw, checked_at)
    summary["cache_status"] = "debug_refetched"

    cache = _load_cache(cache_path)
    cache[clean_appid] = summary
    _save_cache(cache_path, cache)
    return summary


def load_cached_appdetails_summaries(cache_path: Path) -> dict[str, dict]:
    cache = _load_cache(cache_path)
    return {str(appid): detail for appid, detail in cache.items() if isinstance(detail, dict)}


def clear_invalid_appdetails_cache(cache_path: Path) -> int:
    cache = _load_cache(cache_path)
    if not cache:
        return 0
    cleaned = {}
    removed = 0
    for appid, entry in cache.items():
        if _entry_missing_required_fields(entry):
            removed += 1
            continue
        cleaned[appid] = entry
    if removed:
        _save_cache(cache_path, cleaned)
    return removed


def count_missing_field_cache_entries(cache_path: Path) -> int:
    cache = _load_cache(cache_path)
    return sum(1 for entry in cache.values() if _entry_missing_required_fields(entry))


def _fetch_appdetails_summary(appid: str) -> dict:
    checked_at = datetime.now().isoformat(timespec="seconds")
    try:
        raw = _fetch_appdetails(appid)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return _empty_summary(appid, f"获取失败：{exc}", checked_at=checked_at)

    return _summary_from_raw_appdetails(appid, raw, checked_at)


def _summary_from_raw_appdetails(appid: str, raw: dict, checked_at: str) -> dict:
    app_entry = raw.get(appid, {})
    details = app_entry.get("data") or {}
    if not app_entry.get("success") or not details:
        return _empty_summary(appid, "未获取：Steam appdetails 未返回有效数据", checked_at=checked_at)

    developers = _as_text_list(details.get("developers"))
    publishers = _as_text_list(details.get("publishers"))
    genres = [str(item.get("description", "")).strip() for item in details.get("genres", []) if item.get("description")]
    categories = [
        str(item.get("description", "")).strip()
        for item in details.get("categories", [])
        if item.get("description")
    ]
    release_date = details.get("release_date") or {}
    price = details.get("price_overview") or {}
    demos = details.get("demos") or []
    supported_languages = _html_to_text(details.get("supported_languages", ""))
    screenshots = details.get("screenshots") or []
    movies = details.get("movies") or []

    is_free = bool(details.get("is_free"))
    price_text = str(price.get("final_formatted") or price.get("initial_formatted") or "")
    if is_free and not price_text:
        price_text = "免费/Free"
    has_demo = "未确认"
    if demos:
        has_demo = "是"
    elif "demos" in details:
        has_demo = "否"

    return {
        "appid": appid,
        "checked_at": checked_at,
        "success": True,
        "name": str(details.get("name", "") or ""),
        "cache_schema": "0.6.0",
        "detail_fetch_status": "已获取",
        "cache_status": "fetched",
        "developer": " / ".join(developers) if developers else "未获取",
        "publisher": " / ".join(publishers) if publishers else "未获取",
        "developers": developers,
        "publishers": publishers,
        "genres": genres,
        "genres_text": ", ".join(genres),
        "categories": categories,
        "categories_text": ", ".join(categories),
        "tags": [],
        "tags_text": "未获取",
        "short_description": _html_to_text(details.get("short_description", "")),
        "about_the_game": _html_to_text(details.get("about_the_game", "")),
        "release_date": str(release_date.get("date", "") or ""),
        "release_date_raw": release_date,
        "steam_page_date": "未获取",
        "steam_page_date_status": "后续通过 SteamDB History 或人工摘录补充",
        "price": price_text,
        "price_overview": price,
        "discount_percent": str(price.get("discount_percent", "") or ""),
        "supported_languages": supported_languages,
        "supported_languages_summary": _summarize_supported_languages(supported_languages),
        "supports_schinese": _detect_simplified_chinese(supported_languages),
        "header_image": str(details.get("header_image", "") or ""),
        "capsule_image": str(details.get("capsule_image", "") or ""),
        "screenshots_count": len(screenshots) if isinstance(screenshots, list) else 0,
        "movies_count": len(movies) if isinstance(movies, list) else 0,
        "packages_count": len(details.get("packages") or []) if isinstance(details.get("packages"), list) else 0,
        "has_demo": has_demo,
    }


def _save_debug_raw_appdetails(debug_dir: Path, appid: str, raw: dict) -> None:
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / f"appdetails_{appid}.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return


def _fetch_appdetails(appid: str) -> dict:
    params = {"appids": appid, "cc": "cn", "l": "schinese"}
    request = Request(
        STORE_API_URL + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.6.0 (+cached-appdetails)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _empty_summary(appid: str, status: str, checked_at: str = "") -> dict:
    return {
        "appid": str(appid or ""),
        "checked_at": checked_at or datetime.now().isoformat(timespec="seconds"),
        "success": False,
        "name": "",
        "cache_schema": "0.6.0",
        "detail_fetch_status": status,
        "cache_status": "none",
        "developer": "未获取",
        "publisher": "未获取",
        "developers": [],
        "publishers": [],
        "genres": [],
        "genres_text": "未获取",
        "categories": [],
        "categories_text": "未获取",
        "tags": [],
        "tags_text": "未获取",
        "short_description": "",
        "about_the_game": "",
        "release_date": "",
        "release_date_raw": {},
        "steam_page_date": "未获取",
        "steam_page_date_status": "后续通过 SteamDB History 或人工摘录补充",
        "price": "",
        "price_overview": {},
        "discount_percent": "",
        "supported_languages": "",
        "supported_languages_summary": "未获取",
        "supports_schinese": "未确认",
        "header_image": "",
        "capsule_image": "",
        "screenshots_count": 0,
        "movies_count": 0,
        "packages_count": 0,
        "has_demo": "未确认",
    }


def _as_text_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [str(value).strip()]
    return []


def _html_to_text(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(unescape(str(value or "")))
    return re.sub(r"\s+", " ", parser.text()).strip()


def _summarize_supported_languages(value: str) -> str:
    clean = str(value or "").strip()
    if not clean:
        return "未获取"
    return clean[:180]


def _detect_simplified_chinese(value: str) -> str:
    text = str(value or "").casefold()
    if "简体中文" in str(value or "") or "simplified chinese" in text:
        return "是"
    if value.strip():
        return "否"
    return "未确认"


def _load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _entry_is_fresh(entry: dict) -> bool:
    checked_at = str(entry.get("checked_at", "") or "")
    try:
        checked_time = datetime.fromisoformat(checked_at)
    except ValueError:
        return False
    return datetime.now() - checked_time <= timedelta(days=APPDETAILS_CACHE_TTL_DAYS)


def _entry_missing_required_fields(entry: dict) -> bool:
    if not isinstance(entry, dict):
        return True
    required_keys = ["developers", "publishers", "genres", "categories", "release_date", "header_image"]
    if any(key not in entry for key in required_keys):
        return True
    if entry.get("cache_schema") != "0.6.0":
        return True
    if entry.get("success") and (
        "developer" not in entry
        or "publisher" not in entry
        or "genres_text" not in entry
        or "supports_schinese" not in entry
    ):
        return True
    empty_markers = {"", "未获取", "None", "nan", "[]"}
    core_values = [
        str(entry.get("developer", "") or "").strip(),
        str(entry.get("publisher", "") or "").strip(),
        str(entry.get("genres_text", "") or "").strip(),
        str(entry.get("release_date", "") or "").strip(),
        str(entry.get("price", "") or "").strip(),
    ]
    if all(value in empty_markers for value in core_values):
        return True
    return False
