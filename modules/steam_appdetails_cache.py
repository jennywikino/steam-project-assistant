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
STORE_PAGE_URL = "https://store.steampowered.com/app/{appid}/"
APPDETAILS_CACHE_TTL_DAYS = 7
REQUEST_TIMEOUT_SECONDS = 10
APPDETAILS_REGIONS = [
    ("default", {"cc": "cn", "l": "schinese"}),
    ("us", {"cc": "us", "l": "english"}),
    ("jp", {"cc": "jp", "l": "schinese"}),
    ("hk", {"cc": "hk", "l": "schinese"}),
    ("tw", {"cc": "tw", "l": "tchinese"}),
]
HTML_FALLBACK_REGIONS = APPDETAILS_REGIONS[1:]


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
    if entry and not refreshed.get("success"):
        stale = dict(entry)
        stale["cache_status"] = "stale_cache_after_fetch_failed"
        stale["detail_fetch_status"] = refreshed.get("detail_fetch_status", "刷新失败，显示旧缓存")
        return stale
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
        raw = _fetch_appdetails(clean_appid, APPDETAILS_REGIONS[0][1])
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
    combined = _empty_summary(appid, "未获取：Steam appdetails 未返回有效数据", checked_at=checked_at)
    attempted_regions = []
    last_error = ""
    for region_name, params in APPDETAILS_REGIONS:
        attempted_regions.append(region_name)
        try:
            raw = _fetch_appdetails(appid, params)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            continue
        summary = _summary_from_raw_appdetails(appid, raw, checked_at, region_name)
        if summary.get("success") and _summary_has_identity_or_media(summary):
            combined = _merge_appdetails_summaries(combined, summary)
            combined["success"] = True
            combined["appdetails_region_used"] = region_name
            combined["appdetails_regions_attempted"] = " / ".join(attempted_regions)
            if region_name != "default":
                combined["detail_fetch_status"] = "fallback_region"
            else:
                combined["detail_fetch_status"] = "已获取"
            if not _summary_missing_store_core(combined):
                break
    if combined.get("success"):
        if _summary_missing_store_core(combined):
            html_summary = _fetch_html_fallback_summary(appid, checked_at)
            if html_summary.get("success"):
                combined = _merge_appdetails_summaries(combined, html_summary)
                combined["detail_fetch_status"] = "html_fallback" if not combined.get("appdetails_region_used") else combined.get("detail_fetch_status", "fallback_region")
                combined["html_fallback_status"] = "已获取"
        combined["suspected_region_restricted"] = "是" if combined.get("appdetails_region_used") not in {"", "default"} or combined.get("html_fallback_status") == "已获取" else "否"
        combined["steam_data_status"] = build_steam_data_status(combined)
        return combined

    html_summary = _fetch_html_fallback_summary(appid, checked_at)
    if html_summary.get("success"):
        html_summary["detail_fetch_status"] = "html_fallback"
        html_summary["appdetails_regions_attempted"] = " / ".join(attempted_regions)
        html_summary["suspected_region_restricted"] = "是"
        html_summary["steam_data_status"] = build_steam_data_status(html_summary)
        return html_summary

    status = f"获取失败：{last_error}" if last_error else "未获取：Steam appdetails 多地区 fallback 和 HTML fallback 均未返回有效数据"
    failed = _empty_summary(appid, status, checked_at=checked_at)
    failed["appdetails_regions_attempted"] = " / ".join(attempted_regions)
    failed["html_fallback_status"] = "未获取"
    failed["suspected_region_restricted"] = "是"
    failed["steam_data_status"] = build_steam_data_status(failed)
    return failed


def _summary_from_raw_appdetails(appid: str, raw: dict, checked_at: str, region_name: str = "default") -> dict:
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
        "app_type": str(details.get("type", "") or ""),
        "checked_at": checked_at,
        "success": True,
        "name": str(details.get("name", "") or ""),
        "cache_schema": "0.8.5-p2",
        "detail_fetch_status": "已获取",
        "cache_status": "fetched",
        "appdetails_region_used": region_name,
        "appdetails_regions_attempted": region_name,
        "html_fallback_status": "未触发",
        "suspected_region_restricted": "否",
        "steam_data_status": "",
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
        "supports_tchinese": _detect_traditional_chinese(supported_languages),
        "header_image": str(details.get("header_image", "") or ""),
        "capsule_image": str(details.get("capsule_image", "") or ""),
        "screenshots": _normalize_screenshots(screenshots),
        "movies": _normalize_movies(movies),
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


def _fetch_appdetails(appid: str, region_params: dict | None = None) -> dict:
    params = {"appids": appid, **(region_params or {"cc": "cn", "l": "schinese"})}
    request = Request(
        STORE_API_URL + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.6.0 (+cached-appdetails)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _fetch_html_fallback_summary(appid: str, checked_at: str) -> dict:
    attempted = []
    for region_name, params in HTML_FALLBACK_REGIONS:
        attempted.append(region_name)
        url = STORE_PAGE_URL.format(appid=appid) + "?" + urlencode(params)
        try:
            html = _fetch_store_html(url)
        except (HTTPError, URLError, TimeoutError, OSError):
            continue
        summary = _summary_from_store_html(appid, html, checked_at, region_name)
        if summary.get("success"):
            summary["html_fallback_status"] = "已获取"
            summary["html_fallback_region_used"] = region_name
            summary["html_fallback_regions_attempted"] = " / ".join(attempted)
            return summary
    failed = _empty_summary(appid, "商店页 HTML fallback 未获取", checked_at=checked_at)
    failed["html_fallback_status"] = "未获取"
    failed["html_fallback_regions_attempted"] = " / ".join(attempted)
    return failed


def _fetch_store_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "steam-project-assistant/0.6.11c (+single-app-html-fallback)",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _summary_from_store_html(appid: str, html: str, checked_at: str, region_name: str) -> dict:
    json_ld = _parse_json_ld(html)
    og_title = _meta_content(html, "og:title")
    og_desc = _meta_content(html, "og:description")
    og_image = _meta_content(html, "og:image")
    name = _clean_title(json_ld.get("name") or og_title or _match_text(html, r'<div[^>]+class="apphub_AppName"[^>]*>(.*?)</div>'))
    developers = _html_entity_list(json_ld.get("author") or _extract_labeled_links(html, "Developer"))
    publishers = _html_entity_list(json_ld.get("publisher") or _extract_labeled_links(html, "Publisher"))
    release_date = _clean_html_text(json_ld.get("datePublished") or _match_text(html, r'<div[^>]+class="date"[^>]*>(.*?)</div>'))
    short_description = _clean_html_text(json_ld.get("description") or og_desc)
    header_image = str(json_ld.get("image") or og_image or "").strip()
    screenshots = _extract_screenshots(html, appid)
    movies = _extract_movies(html)
    genres = _extract_app_tags(html)
    useful = any([name, header_image, developers, publishers, short_description, screenshots])
    if not useful:
        return _empty_summary(appid, "商店页 HTML fallback 未获取", checked_at=checked_at)
    summary = _empty_summary(appid, "html_fallback", checked_at=checked_at)
    summary.update(
        {
            "success": True,
            "name": name,
            "cache_schema": "0.8.5-p2",
            "detail_fetch_status": "html_fallback",
            "cache_status": "fetched",
            "appdetails_region_used": "",
            "html_fallback_status": "已获取",
            "html_fallback_region_used": region_name,
            "suspected_region_restricted": "是",
            "developer": " / ".join(developers) if developers else "未获取",
            "publisher": " / ".join(publishers) if publishers else "未获取",
            "developers": developers,
            "publishers": publishers,
            "genres": genres,
            "genres_text": ", ".join(genres) if genres else "未获取",
            "short_description": short_description,
            "about_the_game": short_description,
            "release_date": release_date,
            "header_image": header_image,
            "capsule_image": header_image,
            "screenshots": screenshots,
            "movies": movies,
            "screenshots_count": len(screenshots),
            "movies_count": len(movies),
        }
    )
    summary["steam_data_status"] = build_steam_data_status(summary)
    return summary


def _merge_appdetails_summaries(base: dict, incoming: dict) -> dict:
    merged = dict(base or {})
    for key, value in (incoming or {}).items():
        if key in {"checked_at", "cache_status", "detail_fetch_status"}:
            merged[key] = value or merged.get(key, "")
            continue
        if _has_value(value) and not _has_value(merged.get(key)):
            merged[key] = value
        elif key in {"screenshots", "movies", "developers", "publishers", "genres", "categories"}:
            if isinstance(value, list) and value and not merged.get(key):
                merged[key] = value
    return merged


def _summary_has_identity_or_media(summary: dict) -> bool:
    return any(
        _has_value(summary.get(key))
        for key in ["name", "header_image", "developer", "publisher"]
    ) or bool(summary.get("developers") or summary.get("publishers"))


def _summary_missing_store_core(summary: dict) -> bool:
    return any(
        not _has_value(summary.get(key))
        for key in ["name", "header_image", "developer", "publisher"]
    )


def _has_value(value) -> bool:
    if isinstance(value, list):
        return bool(value)
    text = str(value or "").strip()
    return bool(text) and text not in {"未获取", "未确认", "[]", "None", "nan"}


def build_steam_data_status(summary: dict) -> str:
    region = summary.get("appdetails_region_used") or "未获取"
    regions_attempted = summary.get("appdetails_regions_attempted") or "default"
    html_status = summary.get("html_fallback_status") or "未触发"
    restricted = summary.get("suspected_region_restricted") or "否"
    detail_status = "默认地区成功"
    if region not in {"", "default", "未获取"}:
        detail_status = "默认地区失败，已尝试多地区 fallback"
    elif "us" in str(regions_attempted) and region in {"", "未获取"}:
        detail_status = "默认地区失败，已尝试多地区 fallback"
    elif not summary.get("success"):
        detail_status = "商店详情未获取"
    media_status = "HTML fallback 已获取" if html_status == "已获取" else "HTML fallback 未获取" if html_status == "未获取" else "HTML fallback 未触发"
    return (
        f"商店详情：{detail_status}；"
        f"商店图文：{media_status}；"
        f"地区限制：{'疑似存在，需人工复核' if restricted == '是' else '未发现明显限制'}"
    )


def _parse_json_ld(html: str) -> dict:
    for match in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html or "", flags=re.I | re.S):
        try:
            payload = json.loads(unescape(match.strip()))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            payload = next((item for item in payload if isinstance(item, dict)), {})
        if isinstance(payload, dict):
            return payload
    return {}


def _meta_content(html: str, name: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\'](.*?)["\']',
        rf'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']{re.escape(name)}["\']',
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\'](.*?)["\']',
    ]
    for pattern in patterns:
        value = _match_text(html, pattern)
        if value:
            return _clean_html_text(value)
    return ""


def _match_text(html: str, pattern: str) -> str:
    match = re.search(pattern, html or "", flags=re.I | re.S)
    return _clean_html_text(match.group(1)) if match else ""


def _clean_title(value: str) -> str:
    text = _clean_html_text(value)
    return re.sub(r"\s+on Steam$", "", text, flags=re.I).strip()


def _clean_html_text(value) -> str:
    return _html_to_text(str(value or ""))


def _html_entity_list(value) -> list[str]:
    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, dict):
        raw_items = [value.get("name", "")]
    else:
        raw_items = [value]
    items = []
    for item in raw_items:
        if isinstance(item, dict):
            item = item.get("name", "")
        text = _clean_html_text(item)
        if text and text not in items:
            items.append(text)
    return items


def _extract_labeled_links(html: str, label: str) -> list[str]:
    pattern = rf'{label}:</b>\s*(.*?)</div>'
    block = _match_raw(html, pattern)
    if not block:
        return []
    return [_clean_html_text(item) for item in re.findall(r"<a[^>]*>(.*?)</a>", block, flags=re.I | re.S) if _clean_html_text(item)]


def _match_raw(html: str, pattern: str) -> str:
    match = re.search(pattern, html or "", flags=re.I | re.S)
    return match.group(1) if match else ""


def _extract_screenshots(html: str, appid: str) -> list[dict]:
    urls = []
    for url in re.findall(r'https?://[^"\']+/steam/apps/' + re.escape(appid) + r'/ss_[^"\']+?\.jpg', html or "", flags=re.I):
        full = url.replace("\\/", "/")
        if full not in urls:
            urls.append(full)
    rows = []
    for index, url in enumerate(urls[:12]):
        rows.append({"id": str(index), "path_thumbnail": url, "path_full": url.replace(".600x338", "")})
    return rows


def _extract_movies(html: str) -> list[dict]:
    movies = []
    thumbs = re.findall(r'data-poster=["\'](https?://[^"\']+)["\']', html or "", flags=re.I)
    for index, thumb in enumerate(thumbs[:6]):
        movies.append({"id": str(index), "name": f"Trailer {index + 1}", "thumbnail": thumb.replace("\\/", "/"), "webm": "", "mp4": ""})
    return movies


def _extract_app_tags(html: str) -> list[str]:
    tags = []
    for match in re.findall(r'<a[^>]+class=["\'][^"\']*app_tag[^"\']*["\'][^>]*>(.*?)</a>', html or "", flags=re.I | re.S):
        tag = _clean_html_text(match)
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:20]


def _empty_summary(appid: str, status: str, checked_at: str = "") -> dict:
    return {
        "appid": str(appid or ""),
        "app_type": "",
        "checked_at": checked_at or datetime.now().isoformat(timespec="seconds"),
        "success": False,
        "name": "",
        "cache_schema": "0.8.5-p2",
        "detail_fetch_status": status,
        "cache_status": "none",
        "appdetails_region_used": "",
        "appdetails_regions_attempted": "",
        "html_fallback_status": "未获取",
        "html_fallback_region_used": "",
        "html_fallback_regions_attempted": "",
        "suspected_region_restricted": "否",
        "steam_data_status": "",
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
        "supports_tchinese": "未确认",
        "header_image": "",
        "capsule_image": "",
        "screenshots": [],
        "movies": [],
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


def _normalize_screenshots(screenshots) -> list[dict]:
    if not isinstance(screenshots, list):
        return []
    rows = []
    for item in screenshots:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "id": str(item.get("id", "") or ""),
                "path_thumbnail": str(item.get("path_thumbnail", "") or ""),
                "path_full": str(item.get("path_full", "") or ""),
            }
        )
    return rows


def _normalize_movies(movies) -> list[dict]:
    if not isinstance(movies, list):
        return []
    rows = []
    for item in movies:
        if not isinstance(item, dict):
            continue
        webm = item.get("webm") if isinstance(item.get("webm"), dict) else {}
        mp4 = item.get("mp4") if isinstance(item.get("mp4"), dict) else {}
        rows.append(
            {
                "id": str(item.get("id", "") or ""),
                "name": str(item.get("name", "") or ""),
                "thumbnail": str(item.get("thumbnail", "") or ""),
                "webm": str(webm.get("max") or webm.get("480") or ""),
                "mp4": str(mp4.get("max") or mp4.get("480") or ""),
            }
        )
    return rows


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


def _detect_traditional_chinese(value: str) -> str:
    text = str(value or "").casefold()
    if "繁体中文" in str(value or "") or "traditional chinese" in text:
        return "是"
    if str(value or "").strip():
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
    required_keys = ["developers", "publishers", "genres", "categories", "release_date", "header_image", "screenshots", "movies"]
    if any(key not in entry for key in required_keys):
        return True
    if entry.get("cache_schema") != "0.8.5-p2":
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
    identity_values = core_values[:3]
    if all(value in empty_markers for value in identity_values):
        return True
    if all(value in empty_markers for value in core_values):
        return True
    return False
