from __future__ import annotations


def normalize_steam_game_data(
    *,
    appid: str = "",
    search_item: dict | None = None,
    appdetails: dict | None = None,
    review_stats: dict | None = None,
) -> dict:
    """Merge Steam search, appdetails and appreviews data into one UI shape."""
    search_item = search_item or {}
    appdetails = appdetails or {}
    review_stats = review_stats or {}
    clean_appid = _first(appid, search_item.get("appid"), appdetails.get("appid"), review_stats.get("appid"))
    steam_url = _first(
        search_item.get("steam_url"),
        f"https://store.steampowered.com/app/{clean_appid}/" if clean_appid else "",
    )
    developer = _first(appdetails.get("developer"), _join_list(appdetails.get("developers")), search_item.get("developer"))
    publisher = _first(appdetails.get("publisher"), _join_list(appdetails.get("publishers")), search_item.get("publisher"))
    genres = _first(appdetails.get("genres_text"), _join_list(appdetails.get("genres")), search_item.get("genres"))
    categories = _first(appdetails.get("categories_text"), _join_list(appdetails.get("categories")), search_item.get("categories"))
    price = _first(appdetails.get("price"), search_item.get("price"))
    release_date = _first(appdetails.get("release_date"), search_item.get("release_date"))

    return {
        "appid": clean_appid,
        "game_name": _first(appdetails.get("name"), search_item.get("game_name"), search_item.get("title")),
        "steam_url": steam_url,
        "image_url": _first(appdetails.get("header_image"), search_item.get("image_url")),
        "developer": developer or "未获取",
        "publisher": publisher or "未获取",
        "release_date": release_date or "未获取",
        "genres": genres or "未获取",
        "categories": categories or "未获取",
        "price": price or "未获取",
        "supports_schinese": _first(
            appdetails.get("supports_schinese"),
            search_item.get("supports_schinese"),
            search_item.get("has_simplified_chinese"),
        )
        or "未确认",
        "has_demo": _first(appdetails.get("has_demo"), search_item.get("has_demo")) or "未确认",
        "review_total": review_stats.get("review_total", 0),
        "review_positive": review_stats.get("review_positive", 0),
        "review_negative": review_stats.get("review_negative", 0),
        "positive_rate": review_stats.get("positive_rate"),
        "review_score_desc": review_stats.get("review_score_desc", ""),
        "sample_review_count": review_stats.get("sample_review_count", 0),
        "median_playtime_hours": review_stats.get("median_playtime_hours"),
        "avg_playtime_hours": review_stats.get("avg_playtime_hours"),
        "median_playtime_at_review_hours": review_stats.get("median_playtime_at_review_hours"),
        "avg_playtime_at_review_hours": review_stats.get("avg_playtime_at_review_hours"),
        "review_stats_status": review_stats.get("review_stats_status", "评价未获取"),
        "data_status": _data_status(appdetails, review_stats),
    }


def _first(*values) -> str:
    for value in values:
        text = str(value or "").strip()
        if text and text not in {"未获取", "未确认", "[]", "None", "nan"}:
            return text
    return ""


def _join_list(value) -> str:
    if isinstance(value, list):
        return " / ".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def _data_status(appdetails: dict, review_stats: dict) -> str:
    parts = []
    if appdetails:
        parts.append(f"appdetails:{appdetails.get('detail_fetch_status') or appdetails.get('cache_status') or '已读取'}")
    if review_stats:
        parts.append(f"reviews:{review_stats.get('review_stats_status') or review_stats.get('cache_status') or '已读取'}")
    return " / ".join(parts) if parts else "未获取"
