from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


APPREVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"
CACHE_TTL_HOURS = 12
REQUEST_TIMEOUT_SECONDS = 10
MIN_REQUEST_INTERVAL_SECONDS = 0.8
_last_request_at = 0.0


@dataclass
class SteamReviewStatsResult:
    appid: str
    success: bool
    data: dict
    used_cache: bool = False
    used_stale_cache: bool = False
    message: str = ""


def get_cached_review_stats(appid: str, cache_path: Path, force_refresh: bool = False) -> dict:
    """Return one-page Steam appreviews stats with a 12 hour cache.

    On fetch failure the old cached entry is preserved and returned if present.
    """
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return _empty_stats(clean_appid, "AppID 无效")

    cache = _load_cache(cache_path)
    entry = cache.get(clean_appid, {})
    if entry and not force_refresh and _entry_is_fresh(entry):
        result = dict(entry)
        result["cache_status"] = "cache_hit"
        result.setdefault("review_stats_status", "已获取")
        return result

    fetched = _fetch_review_stats(clean_appid)
    if fetched.get("success"):
        fetched["cache_status"] = "refetched" if force_refresh else "fetched"
        cache[clean_appid] = fetched
        _save_cache(cache_path, cache)
        return fetched

    if entry:
        stale = dict(entry)
        stale["cache_status"] = "stale_cache_after_fetch_failed"
        stale["review_stats_status"] = "评价刷新失败，显示旧缓存"
        stale["last_error"] = fetched.get("review_stats_status", "")
        return stale

    fetched["cache_status"] = "fetch_failed"
    return fetched


def load_cached_review_stats(cache_path: Path) -> dict[str, dict]:
    cache = _load_cache(cache_path)
    return {str(appid): row for appid, row in cache.items() if isinstance(row, dict)}


def _fetch_review_stats(appid: str) -> dict:
    fetched_at = datetime.now().isoformat(timespec="seconds")
    try:
        payload = _request_appreviews(appid, "summary")
        summary = payload.get("query_summary") or {}
        if not payload.get("reviews") and _to_int(summary.get("total_reviews")) > 0:
            fallback = _request_appreviews(appid, "recent")
            if fallback.get("reviews"):
                payload["reviews"] = fallback.get("reviews")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return _empty_stats(appid, f"评价未获取：{exc}", fetched_at=fetched_at)
    return _stats_from_payload(appid, payload, fetched_at)


def _request_appreviews(appid: str, review_filter: str) -> dict:
    global _last_request_at
    elapsed = time.time() - _last_request_at
    if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
    params = {
        "json": "1",
        "language": "all",
        "purchase_type": "all",
        "num_per_page": "100",
        "cursor": "*",
        "filter": review_filter,
    }
    request = Request(
        APPREVIEWS_URL.format(appid=appid) + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.6.0 (+cached-appreviews-summary)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        _last_request_at = time.time()
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _stats_from_payload(appid: str, payload: dict, fetched_at: str) -> dict:
    summary = payload.get("query_summary") or {}
    reviews = payload.get("reviews") or []
    total_positive = _to_int(summary.get("total_positive"))
    total_negative = _to_int(summary.get("total_negative"))
    total_reviews = _to_int(summary.get("total_reviews") or (total_positive + total_negative))
    positive_rate = round(total_positive / total_reviews, 4) if total_reviews > 0 else None

    playtime_forever = []
    playtime_at_review = []
    voted_up_count = 0
    for review in reviews if isinstance(reviews, list) else []:
        if not isinstance(review, dict):
            continue
        if review.get("voted_up") is True:
            voted_up_count += 1
        author = review.get("author") or {}
        forever_minutes = _to_int(author.get("playtime_forever"))
        at_review_minutes = _to_int(author.get("playtime_at_review"))
        if forever_minutes > 0:
            playtime_forever.append(forever_minutes / 60)
        if at_review_minutes > 0:
            playtime_at_review.append(at_review_minutes / 60)

    status = "已获取"
    if total_reviews <= 0:
        status = "暂无评测"
    elif total_reviews < 10:
        status = "样本不足"

    return {
        "appid": appid,
        "success": True,
        "fetched_at": fetched_at,
        "cache_schema": "0.6.0",
        "review_total": total_reviews,
        "review_positive": total_positive,
        "review_negative": total_negative,
        "positive_rate": positive_rate,
        "review_score_desc": str(summary.get("review_score_desc", "") or ""),
        "review_score": summary.get("review_score", ""),
        "sample_review_count": len(reviews) if isinstance(reviews, list) else 0,
        "sample_voted_up_count": voted_up_count,
        "avg_playtime_hours": _mean(playtime_forever),
        "median_playtime_hours": _median(playtime_forever),
        "avg_playtime_at_review_hours": _mean(playtime_at_review),
        "median_playtime_at_review_hours": _median(playtime_at_review),
        "review_stats_status": status,
        "cache_status": "fetched",
    }


def _empty_stats(appid: str, status: str, fetched_at: str = "") -> dict:
    return {
        "appid": str(appid or ""),
        "success": False,
        "fetched_at": fetched_at or datetime.now().isoformat(timespec="seconds"),
        "cache_schema": "0.6.0",
        "review_total": 0,
        "review_positive": 0,
        "review_negative": 0,
        "positive_rate": None,
        "review_score_desc": "",
        "review_score": "",
        "sample_review_count": 0,
        "sample_voted_up_count": 0,
        "avg_playtime_hours": None,
        "median_playtime_hours": None,
        "avg_playtime_at_review_hours": None,
        "median_playtime_at_review_hours": None,
        "review_stats_status": status,
        "cache_status": "none",
    }


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(statistics.median(values)), 2)


def _to_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


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
    fetched_at = str(entry.get("fetched_at", "") or "")
    try:
        fetched_time = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    return datetime.now() - fetched_time <= timedelta(hours=CACHE_TTL_HOURS)
