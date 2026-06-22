from __future__ import annotations

from datetime import datetime, timedelta
from html import unescape
from pathlib import Path
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


APPREVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"
CACHE_TTL_HOURS = 6
REQUEST_TIMEOUT_SECONDS = 10
MIN_REQUEST_INTERVAL_SECONDS = 0.8
REVIEW_BUCKETS = {
    "recent": {"filter_name": "recent", "review_type": "all"},
    "helpful": {"filter_name": "all", "review_type": "all"},
    "negative": {"filter_name": "recent", "review_type": "negative"},
}
_last_request_at = 0.0


def get_steam_review_preview(
    appid: str,
    cache_dir: Path,
    language: str = "schinese",
    num_per_group: int = 3,
    force_refresh: bool = False,
) -> dict:
    clean_appid = str(appid or "").strip()
    clean_language = _safe_cache_token(language or "schinese")
    clean_num = max(1, min(int(num_per_group or 3), 5))
    if not clean_appid.isdigit():
        return _empty_result(clean_appid, "获取失败", "AppID 无效")

    bucket_results: dict[str, dict] = {}
    errors: list[str] = []
    any_fresh_fetch = False
    any_stale_cache = False
    any_cache = False
    helpful_sort_limited = False

    for bucket, params in REVIEW_BUCKETS.items():
        cache_path = _bucket_cache_path(cache_dir, clean_appid, clean_language, bucket)
        cached = _load_cache(cache_path)
        cache_fresh = bool(cached and _cache_is_fresh(cached))
        if cached and not force_refresh and cache_fresh:
            bucket_result = _normalize_bucket_result(cached, clean_appid, bucket)
            bucket_result["status"] = "使用缓存"
            any_cache = True
        else:
            try:
                bucket_result = _fetch_review_bucket(
                    clean_appid,
                    language=clean_language,
                    bucket=bucket,
                    filter_name=params["filter_name"],
                    review_type=params["review_type"],
                    num_per_group=clean_num,
                )
                _save_cache(cache_path, bucket_result)
                any_fresh_fetch = True
            except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
                if cached:
                    bucket_result = _normalize_bucket_result(cached, clean_appid, bucket)
                    bucket_result["status"] = "使用旧缓存"
                    bucket_result["error_message"] = f"{bucket} 获取失败，使用旧缓存：{exc}"
                    any_stale_cache = True
                    errors.append(bucket_result["error_message"])
                else:
                    bucket_result = _empty_bucket_result(clean_appid, bucket, "获取失败", f"{bucket} 获取失败：{exc}")
                    errors.append(bucket_result["error_message"])
        if bucket == "helpful" and bucket_result.get("helpful_sort_limited"):
            helpful_sort_limited = True
        bucket_results[bucket] = bucket_result

    recent_reviews = bucket_results.get("recent", {}).get("reviews", [])[:clean_num]
    helpful_reviews = bucket_results.get("helpful", {}).get("reviews", [])[:clean_num]
    negative_reviews = [
        row for row in bucket_results.get("negative", {}).get("reviews", [])
        if row.get("voted_up") is False
    ][:clean_num]
    summary = _first_summary(bucket_results, ["recent", "helpful", "negative"])
    if any_fresh_fetch:
        status = "已获取"
    elif any_cache:
        status = "使用缓存"
    elif any_stale_cache:
        status = "使用旧缓存"
    else:
        status = "获取失败" if errors else "暂无"
    if status != "获取失败" and not any([recent_reviews, helpful_reviews, negative_reviews]):
        status = "暂无"

    return _normalize_result(
        {
            "appid": clean_appid,
            "status": status,
            "fetched_at": _now(),
            "summary": summary,
            "recent_reviews": recent_reviews,
            "helpful_reviews": helpful_reviews,
            "negative_reviews": negative_reviews,
            "error_message": "；".join(item for item in errors if item),
            "review_bucket_cache_keys": {
                bucket: f"{clean_appid}_{clean_language}_{bucket}" for bucket in REVIEW_BUCKETS
            },
            "bucket_status": {
                bucket: bucket_results.get(bucket, {}).get("status", "暂无") for bucket in REVIEW_BUCKETS
            },
            "helpful_sort_limited": helpful_sort_limited,
        }
    )


def build_steam_review_preview_markdown_section(review_result: dict | None) -> str:
    result = _normalize_result(review_result or {})
    groups = [
        ("最近评论", result.get("recent_reviews", [])),
        ("高赞 / 高价值评论", result.get("helpful_reviews", [])),
        ("差评样本", result.get("negative_reviews", [])),
    ]
    if not any(items for _, items in groups):
        return "## Steam 评论预览\n\n未抓到中文评论正文；评分与评论数仍可参考，可打开 Steam 评论页人工查看。\n"

    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    lines = ["## Steam 评论预览", ""]
    lines.append(
        "- 评测摘要："
        f"{_display(summary.get('review_score_desc'))} / "
        f"好评率 {_format_percent(summary.get('positive_rate'))} / "
        f"总评测数 {_display(summary.get('review_total'))}"
    )
    for title, items in groups:
        lines.extend(["", f"### {title}"])
        if not items:
            lines.append("- 暂无")
            continue
        for item in items:
            vote = "推荐" if item.get("voted_up") else "不推荐"
            lines.append(
                f"- {vote} · {item.get('created_at') or '未获取'} · "
                f"游玩 {format_playtime(item.get('author_playtime_at_review') or item.get('author_playtime_forever'))}"
            )
            lines.append(f"  - 点赞：{_display(item.get('votes_up'))}")
            lines.append(f"  - 正文：{_display(item.get('review_preview') or item.get('review'))[:200]}")
            url = str(item.get("review_url", "") or "").strip()
            if url:
                lines.append(f"  - 链接：{url}")
    lines.append("")
    return "\n".join(lines)


def steam_review_preview_status_label(review_result: dict | None) -> str:
    status = str((review_result or {}).get("status", "") or "").strip()
    if status in {"已获取", "使用缓存", "使用旧缓存", "暂无", "获取失败"}:
        return status
    if any((review_result or {}).get(key) for key in ["recent_reviews", "helpful_reviews", "negative_reviews"]):
        return "已获取"
    return "暂无"


def clean_review_text(value: str, max_length: int = 300) -> str:
    text = unescape(str(value or ""))
    text = text.replace("\r", "\n")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "暂无评论正文"
    if len(text) > max_length:
        return text[: max(0, max_length - 1)].rstrip() + "..."
    return text


def format_playtime(minutes) -> str:
    try:
        value = int(minutes or 0)
    except (TypeError, ValueError):
        value = 0
    if value <= 0:
        return "未获取"
    return f"{round(value / 60, 1)} 小时"


def _fetch_review_bucket(
    appid: str,
    *,
    language: str,
    bucket: str,
    filter_name: str,
    review_type: str,
    num_per_group: int,
) -> dict:
    clean_num = max(1, min(int(num_per_group or 3), 5))
    payload = _request_appreviews(
        appid,
        filter_name=filter_name,
        language=language,
        review_type=review_type,
        num_per_page=max(20, clean_num * 4),
    )
    reviews = [_normalize_review(item, appid) for item in _review_rows(payload)]
    helpful_sort_limited = False
    if bucket == "recent":
        reviews = sorted(reviews, key=lambda row: _to_int(row.get("timestamp_created")), reverse=True)
    elif bucket == "helpful":
        has_usefulness_fields = any(
            _to_float(row.get("weighted_vote_score")) > 0 or _to_int(row.get("votes_up")) > 0
            for row in reviews
        )
        helpful_sort_limited = not has_usefulness_fields
        if has_usefulness_fields:
            reviews = sorted(
                reviews,
                key=lambda row: (_to_float(row.get("weighted_vote_score")), _to_int(row.get("votes_up"))),
                reverse=True,
            )
    elif bucket == "negative":
        reviews = [row for row in reviews if row.get("voted_up") is False]
        reviews = sorted(reviews, key=lambda row: _to_int(row.get("timestamp_created")), reverse=True)

    result = {
        "appid": appid,
        "bucket": bucket,
        "status": "已获取" if reviews else "暂无",
        "fetched_at": _now(),
        "summary": _summary_from_payload(payload),
        "reviews": reviews[:clean_num],
        "error_message": "",
        "helpful_sort_limited": helpful_sort_limited,
    }
    return _normalize_bucket_result(result, appid, bucket)


def _request_appreviews(appid: str, filter_name: str, language: str, review_type: str, num_per_page: int) -> dict:
    global _last_request_at
    elapsed = time.time() - _last_request_at
    if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
    params = {
        "json": "1",
        "language": str(language or "schinese"),
        "purchase_type": "all",
        "num_per_page": str(max(1, min(num_per_page, 100))),
        "cursor": "*",
        "filter": filter_name,
        "review_type": review_type,
    }
    request = Request(
        APPREVIEWS_URL.format(appid=appid) + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.8.5 (+review-preview)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        _last_request_at = time.time()
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _normalize_result(result: dict) -> dict:
    appid = str(result.get("appid", "") or "")
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    return {
        "appid": appid,
        "status": str(result.get("status", "") or "暂无"),
        "fetched_at": str(result.get("fetched_at", "") or ""),
        "summary": _normalize_summary(summary),
        "recent_reviews": [_normalize_review(row, appid) for row in result.get("recent_reviews", []) if isinstance(row, dict)],
        "helpful_reviews": [_normalize_review(row, appid) for row in result.get("helpful_reviews", []) if isinstance(row, dict)],
        "negative_reviews": [_normalize_review(row, appid) for row in result.get("negative_reviews", []) if isinstance(row, dict) and row.get("voted_up") is False],
        "error_message": str(result.get("error_message", "") or ""),
        "review_bucket_cache_keys": result.get("review_bucket_cache_keys", {}) if isinstance(result.get("review_bucket_cache_keys"), dict) else {},
        "bucket_status": result.get("bucket_status", {}) if isinstance(result.get("bucket_status"), dict) else {},
        "helpful_sort_limited": bool(result.get("helpful_sort_limited")),
    }


def _normalize_bucket_result(result: dict, appid: str, bucket: str) -> dict:
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    return {
        "appid": str(result.get("appid", "") or appid),
        "bucket": str(result.get("bucket", "") or bucket),
        "status": str(result.get("status", "") or "暂无"),
        "fetched_at": str(result.get("fetched_at", "") or ""),
        "summary": _normalize_summary(summary),
        "reviews": [_normalize_review(row, appid) for row in result.get("reviews", []) if isinstance(row, dict)],
        "error_message": str(result.get("error_message", "") or ""),
        "helpful_sort_limited": bool(result.get("helpful_sort_limited")),
    }


def _normalize_review(row: dict, appid: str) -> dict:
    author = row.get("author") if isinstance(row.get("author"), dict) else {}
    recommendationid = str(row.get("recommendationid", "") or "")
    created_at = _readable_timestamp(row.get("timestamp_created"))
    raw_review = str(row.get("review", "") or "")
    review_url = f"https://steamcommunity.com/app/{appid}/reviews/?browsefilter=toprated" if appid else ""
    return {
        "recommendationid": recommendationid,
        "voted_up": bool(row.get("voted_up", False)),
        "review": clean_review_text(raw_review, max_length=2000),
        "review_preview": clean_review_text(raw_review, max_length=300),
        "timestamp_created": str(row.get("timestamp_created", "") or ""),
        "created_at": created_at,
        "author_playtime_forever": _to_int(author.get("playtime_forever") if author else row.get("author_playtime_forever")),
        "author_playtime_at_review": _to_int(author.get("playtime_at_review") if author else row.get("author_playtime_at_review")),
        "votes_up": _to_int(row.get("votes_up")),
        "votes_funny": _to_int(row.get("votes_funny")),
        "weighted_vote_score": _to_float(row.get("weighted_vote_score")),
        "language": str(row.get("language", "") or ""),
        "review_url": review_url,
    }


def _summary_from_payload(payload: dict) -> dict:
    summary = payload.get("query_summary") if isinstance(payload, dict) else {}
    return _normalize_summary(summary if isinstance(summary, dict) else {})


def _normalize_summary(summary: dict) -> dict:
    total_positive = _to_int(summary.get("total_positive"))
    total_negative = _to_int(summary.get("total_negative"))
    total_reviews = _to_int(summary.get("total_reviews") or (total_positive + total_negative))
    positive_rate = round(total_positive / total_reviews, 4) if total_reviews > 0 else None
    return {
        "review_total": total_reviews,
        "review_positive": total_positive,
        "review_negative": total_negative,
        "positive_rate": positive_rate,
        "review_score_desc": str(summary.get("review_score_desc", "") or ""),
        "review_score": str(summary.get("review_score", "") or ""),
    }


def _review_rows(payload: dict) -> list[dict]:
    rows = payload.get("reviews") if isinstance(payload, dict) else []
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _first_summary(bucket_results: dict[str, dict], buckets: list[str]) -> dict:
    for bucket in buckets:
        summary = bucket_results.get(bucket, {}).get("summary", {})
        normalized = _normalize_summary(summary if isinstance(summary, dict) else {})
        if normalized.get("review_total") or normalized.get("review_score_desc"):
            return normalized
    return _normalize_summary({})


def _empty_result(appid: str, status: str, error_message: str = "") -> dict:
    return {
        "appid": str(appid or ""),
        "status": status,
        "fetched_at": _now(),
        "summary": _normalize_summary({}),
        "recent_reviews": [],
        "helpful_reviews": [],
        "negative_reviews": [],
        "error_message": error_message,
        "review_bucket_cache_keys": {},
        "bucket_status": {},
        "helpful_sort_limited": False,
    }


def _empty_bucket_result(appid: str, bucket: str, status: str, error_message: str = "") -> dict:
    return _normalize_bucket_result(
        {
            "appid": appid,
            "bucket": bucket,
            "status": status,
            "fetched_at": _now(),
            "summary": {},
            "reviews": [],
            "error_message": error_message,
            "helpful_sort_limited": False,
        },
        appid,
        bucket,
    )


def _bucket_cache_path(cache_dir: Path, appid: str, language: str, bucket: str) -> Path:
    return cache_dir / f"{appid}_{_safe_cache_token(language)}_{_safe_cache_token(bucket)}.json"


def _safe_cache_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or "").strip())
    return token or "default"


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
        cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _cache_is_fresh(cache: dict) -> bool:
    fetched_at = str(cache.get("fetched_at", "") or "")
    try:
        fetched_time = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    return datetime.now() - fetched_time <= timedelta(hours=CACHE_TTL_HOURS)


def _readable_timestamp(value) -> str:
    try:
        return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, OSError):
        return str(value or "")


def _format_percent(value) -> str:
    if value is None or value == "":
        return "未获取"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(value)


def _display(value) -> str:
    text = str(value if value is not None else "").strip()
    return text if text else "未获取"


def _to_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _to_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
