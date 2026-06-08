from datetime import datetime, timedelta
from pathlib import Path
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STORE_API_URL = "https://store.steampowered.com/api/appdetails"
IMAGE_CACHE_TTL_DAYS = 7
REQUEST_TIMEOUT_SECONDS = 8


def get_cached_steam_image(appid: str, cache_path: Path) -> dict:
    """Return cached Steam image metadata, refreshing from appdetails when stale."""
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return {}

    cache = _load_cache(cache_path)
    entry = cache.get(clean_appid, {})
    if entry and _entry_is_fresh(entry):
        return entry

    refreshed = _fetch_steam_image_entry(clean_appid)
    cache[clean_appid] = refreshed
    _save_cache(cache_path, cache)
    return refreshed


def _fetch_steam_image_entry(appid: str) -> dict:
    checked_at = datetime.now().isoformat(timespec="seconds")
    try:
        details = _fetch_appdetails(appid)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "appid": appid,
            "checked_at": checked_at,
            "success": False,
            "message": str(exc),
            "header_image": "",
            "capsule_image": "",
            "name": "",
        }

    app_entry = details.get(appid, {})
    data = app_entry.get("data") or {}
    if not app_entry.get("success") or not data:
        return {
            "appid": appid,
            "checked_at": checked_at,
            "success": False,
            "message": "Steam appdetails 未返回有效图片信息",
            "header_image": "",
            "capsule_image": "",
            "name": "",
        }

    return {
        "appid": appid,
        "checked_at": checked_at,
        "success": True,
        "message": "ok",
        "header_image": str(data.get("header_image", "") or ""),
        "capsule_image": str(data.get("capsule_image", "") or ""),
        "name": str(data.get("name", "") or ""),
    }


def _fetch_appdetails(appid: str) -> dict:
    query = f"?appids={appid}&cc=cn&l=schinese&filters=basic"
    request = Request(
        STORE_API_URL + query,
        headers={
            "User-Agent": "steam-project-assistant/0.5.4 (+public-store-images)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


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
    return datetime.now() - checked_time <= timedelta(days=IMAGE_CACHE_TTL_DAYS)
