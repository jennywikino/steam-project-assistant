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
_last_request_at = 0.0


def get_steam_review_preview(
    appid: str,
    cache_dir: Path,
    language: str = "schinese",
    num_per_group: int = 3,
    force_refresh: bool = False,
) -> dict:
    clean_appid = str(appid or "").strip()
    if not clean_appid.isdigit():
        return _empty_result(clean_appid, "获取失败", "AppID 无效")

    cache_path = cache_dir / f"{clean_appid}.json"
    cached = _load_cache(cache_path)
    if cached and not force_refresh and _cache_is_fresh(cached):
        cached = _normalize_result(cached)
        cached["status"] = "使用缓存"
        cached["error_message"] = ""
        return cached

    try:
        result = _fetch_review_preview(clean_appid, language=language, num_per_group=num_per_group)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        if cached:
            cached = _normalize_result(cached)
            cached["status"] = "使用旧缓存"
            cached["error_message"] = f"获取失败，使用旧缓存：{exc}"
            return cached
        return _empty_result(clean_appid, "获取失败", f"获取失败：{exc}")

    _save_cache(cache_path, result)
    return result


def build_steam_review_preview_markdown_section(review_result: dict | None) -> str:
    result = _normalize_result(review_result or {})
    groups = [
        ("最近评论", result.get("recent_reviews", [])),
        ("有价值评论", result.get("helpful_reviews", [])),
        ("最近差评", result.get("negative_reviews", [])),
    ]
    if not any(items for _, items in groups):
        return "## Steam 评论预览\n\n暂无评论预览，可能是接口无返回或项目暂无公开评论。\n"

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
            lines.append(f"- {vote} · {item.get('created_at') or '未获取'} · 游玩 {format_playtime(item.get('author_playtime_at_review') or item.get('author_playtime_forever'))}")
            lines.append(f"  - 点赞：{_display(item.get('votes_up'))}")
            lines.append(f"  - 正文：{_display(item.get('review_preview') or item.get('review'))}")
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


def _fetch_review_preview(appid: str, language: str, num_per_group: int) -> dict:
    clean_num = max(1, min(int(num_per_group or 3), 5))
    recent_payload = _request_appreviews(appid, filter_name="recent", language=language, review_type="all", num_per_page=max(20, clean_num * 4))
    helpful_payload = _request_appreviews(appid, filter_name="all", language=language, review_type="all", num_per_page=max(20, clean_num * 4))
    negative_payload = _request_appreviews(appid, filter_name="recent", language=language, review_type="negative", num_per_page=max(20, clean_num * 4))

    recent_reviews = [_normalize_review(item, appid) for item in _review_rows(recent_payload)]
    helpful_reviews = [_normalize_review(item, appid) for item in _review_rows(helpful_payload)]
    negative_reviews = [_normalize_review(item, appid) for item in _review_rows(negative_payload)]
    helpful_reviews = sorted(
        helpful_reviews,
        key=lambda row: (float(row.get("weighted_vote_score") or 0), int(row.get("votes_up") or 0)),
        reverse=True,
    )

    summary = _summary_from_payload(recent_payload or helpful_payload or negative_payload)
    result = {
        "appid": appid,
        "status": "已获取",
        "fetched_at": _now(),
        "summary": summary,
        "recent_reviews": recent_reviews[:clean_num],
        "helpful_reviews": helpful_reviews[:clean_num],
        "negative_reviews": negative_reviews[:clean_num],
        "error_message": "",
    }
    if not any([result["recent_reviews"], result["helpful_reviews"], result["negative_reviews"]]):
        result["status"] = "暂无"
    return _normalize_result(result)


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
            "User-Agent": "steam-project-assistant/0.6.13 (+review-preview)",
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
        "negative_reviews": [_normalize_review(row, appid) for row in result.get("negative_reviews", []) if isinstance(row, dict)],
        "error_message": str(result.get("error_message", "") or ""),
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
    }


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
