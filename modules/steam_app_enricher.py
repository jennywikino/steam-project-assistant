from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import shutil
import time

from modules.steam_appdetails_cache import get_cached_appdetails_summary


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_appdetails_cache.json"
STORE_URL_TEMPLATE = "https://store.steampowered.com/app/{appid}/"
REQUEST_INTERVAL_SECONDS = 0.25

EMPTY_VALUES = {
    "",
    "None",
    "nan",
    "[]",
    "未获取",
    "未确认",
    "未填写",
}


def enrich_appids_basic(appids: list[str], force_refresh: bool = False) -> dict[str, dict]:
    cache_path = DEFAULT_CACHE_PATH
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cached_entries, cache_warning = _load_cache_with_repair(cache_path)
    results: dict[str, dict] = {}
    seen: set[str] = set()

    for raw_appid in appids:
        appid = str(raw_appid or "").strip()
        if not appid or appid in seen:
            continue
        seen.add(appid)
        if not appid.isdigit():
            results[appid] = _failed_result(appid, "AppID 无效", cache_warning)
            continue

        cache_hit = appid in cached_entries and not force_refresh
        try:
            detail = dict(cached_entries[appid]) if cache_hit else get_cached_appdetails_summary(appid, cache_path, force_refresh=force_refresh)
        except Exception as exc:
            results[appid] = _failed_result(appid, f"Steam 基础信息补全失败：{exc}", cache_warning)
            continue

        result = _basic_result_from_appdetails(appid, detail, cache_hit=cache_hit, cache_warning=cache_warning)
        results[appid] = result
        if not cache_hit:
            time.sleep(REQUEST_INTERVAL_SECONDS)

    return results


def _basic_result_from_appdetails(appid: str, detail: dict, *, cache_hit: bool, cache_warning: str = "") -> dict:
    success = bool(detail.get("success")) and bool(_clean(detail.get("name")))
    release_date = _clean(detail.get("release_date"))
    release_status = _release_status(detail, release_date)
    result = {
        "appid": appid,
        "game_name": _clean(detail.get("name")),
        "steam_url": STORE_URL_TEMPLATE.format(appid=appid),
        "developer": _clean(detail.get("developer")) or _join_list(detail.get("developers")),
        "publisher": _clean(detail.get("publisher")) or _join_list(detail.get("publishers")),
        "release_date": release_date,
        "release_status": release_status,
        "price": _clean(detail.get("price")),
        "review_score": "",
        "review_count": "",
        "positive_rate": "",
        "review_score_desc": "",
        "app_type": _clean(detail.get("app_type") or detail.get("type")),
        "has_demo": _clean(detail.get("has_demo")),
        "supports_schinese": _clean(detail.get("supports_schinese")),
        "supports_tchinese": _clean(detail.get("supports_tchinese")) or _detect_traditional_chinese(detail.get("supported_languages")),
        "supported_languages": _clean(detail.get("supported_languages")),
        "genres_tags": _clean(detail.get("genres_text")) or _join_list(detail.get("genres")),
        "short_desc": _clean(detail.get("short_description")),
        "header_image": _clean(detail.get("header_image")),
        "source_notes": "Steam basic info enriched",
        "success": success,
        "cache_hit": cache_hit,
        "error": "",
    }
    if cache_warning:
        result["cache_warning"] = cache_warning
    if not success:
        result["error"] = _clean(detail.get("detail_fetch_status")) or "Steam 基础信息补全失败 / 需人工复核"
        result["source_notes"] = "Steam basic info enriched; Steam 基础信息补全失败 / 需人工复核"
    return result


def _failed_result(appid: str, error: str, cache_warning: str = "") -> dict:
    result = {
        "appid": appid,
        "game_name": "",
        "steam_url": STORE_URL_TEMPLATE.format(appid=appid) if appid.isdigit() else "",
        "developer": "",
        "publisher": "",
        "release_date": "",
        "release_status": "",
        "price": "",
        "review_score": "",
        "review_count": "",
        "positive_rate": "",
        "review_score_desc": "",
        "app_type": "",
        "has_demo": "",
        "supports_schinese": "",
        "supports_tchinese": "",
        "supported_languages": "",
        "genres_tags": "",
        "short_desc": "",
        "header_image": "",
        "source_notes": "Steam basic info enriched; Steam 基础信息补全失败 / 需人工复核",
        "success": False,
        "cache_hit": False,
        "error": error,
    }
    if cache_warning:
        result["cache_warning"] = cache_warning
    return result


def _load_cache_with_repair(cache_path: Path) -> tuple[dict[str, dict], str]:
    if not cache_path.exists():
        return {}, ""
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        backup_path = cache_path.with_name(
            f"{cache_path.stem}.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}{cache_path.suffix}.bak"
        )
        try:
            shutil.copy2(cache_path, backup_path)
            warning = f"缓存损坏，已备份到 {backup_path.name} 并重建。"
        except OSError:
            warning = "缓存损坏，已忽略并重建。"
        return {}, warning + f" 原因：{exc}"
    if not isinstance(data, dict):
        return {}, "缓存格式不是对象，已忽略并重建。"
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}, ""


def _release_status(detail: dict, release_date: str) -> str:
    raw = detail.get("release_date_raw")
    if isinstance(raw, dict) and raw.get("coming_soon") is True:
        return "Coming Soon"
    return release_date


def _join_list(value) -> str:
    if isinstance(value, list):
        return " / ".join(_clean(item) for item in value if _clean(item))
    return _clean(value)


def _clean(value) -> str:
    text = str(value or "").strip()
    if text in EMPTY_VALUES:
        return ""
    return text


def _detect_traditional_chinese(value) -> str:
    text = str(value or "")
    folded = text.casefold()
    if "繁体中文" in text or "traditional chinese" in folded:
        return "是"
    if text.strip():
        return "否"
    return "未确认"
