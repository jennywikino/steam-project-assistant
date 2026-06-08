from dataclasses import asdict, dataclass, field
from datetime import datetime
from html import unescape
from pathlib import Path
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CACHE_TTL_MINUTES = 30
REQUEST_TIMEOUT_SECONDS = 10
SEARCH_RESULTS_URL = "https://store.steampowered.com/search/results/"

STEAM_HOME_FEED_GROUPS = [
    ("即将推出", ["popularcomingsoon", "comingsoon", "upcoming"]),
    ("近期上架", ["popularnew"]),
    ("热销参考", ["topsellers", "popular", "hot"]),
]

SOURCE_GROUP_ALIASES = {
    "Steam 新品趋势": "近期上架",
    "Steam 即将推出": "即将推出",
    "Steam 热销趋势": "热销参考",
    "Steam 折扣热点": "热销参考",
    "热销 / 热门趋势": "热销参考",
    "新品趋势": "近期上架",
}


@dataclass
class SteamStoreFeedItem:
    fetched_at: str = ""
    source_group: str = ""
    source_filter: str = ""
    appid: str = ""
    game_name: str = ""
    steam_url: str = ""
    image_url: str = ""
    price: str = ""
    release_date: str = ""
    review_summary: str = ""
    has_demo: str = ""
    has_simplified_chinese: str = ""


@dataclass
class SteamStoreFeedResult:
    fetched_at: str = ""
    from_cache: bool = False
    used_stale_cache: bool = False
    success: bool = False
    message: str = ""
    groups: dict[str, list[SteamStoreFeedItem]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class SteamStoreSearchResult:
    query: str = ""
    status_filter: str = "全部"
    fetched_at: str = ""
    from_cache: bool = False
    used_stale_cache: bool = False
    success: bool = False
    message: str = ""
    items: list[SteamStoreFeedItem] = field(default_factory=list)
    error: str = ""


def load_steam_store_home_feed(cache_path: Path, force_refresh: bool = False) -> SteamStoreFeedResult:
    cache = _load_cache(cache_path)
    if cache and not force_refresh and _cache_is_fresh(cache):
        return _result_from_cache(cache, from_cache=True, used_stale_cache=False, message="当前显示缓存数据。")
    if cache and not force_refresh:
        return _result_from_cache(cache, from_cache=True, used_stale_cache=True, message="当前显示缓存数据。")

    try:
        result = _fetch_steam_store_home_feed()
    except Exception as exc:
        if cache:
            return _result_from_cache(
                cache,
                from_cache=True,
                used_stale_cache=True,
                message=f"Steam 图文源刷新失败，继续显示缓存：{exc}",
            )
        return SteamStoreFeedResult(
            fetched_at="",
            from_cache=False,
            used_stale_cache=False,
            success=False,
            message=f"Steam 图文源获取失败：{exc}",
            groups=_empty_groups(),
            errors=[str(exc)],
        )

    _save_cache(cache_path, result)
    return result


def search_steam_store_items(
    query: str,
    cache_path: Path,
    status_filter: str = "全部",
    force_refresh: bool = False,
    count: int = 12,
) -> SteamStoreSearchResult:
    clean_query = " ".join(str(query or "").split())
    clean_status = str(status_filter or "全部").strip() or "全部"
    if not clean_query:
        return SteamStoreSearchResult(query=clean_query, status_filter=clean_status, success=False, message="请输入搜索关键词。")

    cache = _load_cache(cache_path)
    cache_key = _search_cache_key(clean_query, clean_status)
    entry = cache.get("queries", {}).get(cache_key, {}) if isinstance(cache.get("queries"), dict) else {}
    if entry and not force_refresh and _cache_is_fresh(entry):
        return _search_result_from_cache_entry(clean_query, clean_status, entry, from_cache=True, used_stale_cache=False, message="搜索结果来自缓存。")

    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        payload = _fetch_search_results("", count=count, term=clean_query)
        items = _parse_search_payload(payload, "Steam 搜索", "search", fetched_at)[:count]
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        if entry:
            return _search_result_from_cache_entry(
                clean_query,
                clean_status,
                entry,
                from_cache=True,
                used_stale_cache=True,
                message=f"Steam 搜索失败，显示旧缓存：{exc}",
                error=str(exc),
            )
        return SteamStoreSearchResult(
            query=clean_query,
            status_filter=clean_status,
            fetched_at="",
            success=False,
            message=f"Steam 搜索失败：{exc}",
            error=str(exc),
        )

    result = SteamStoreSearchResult(
        query=clean_query,
        status_filter=clean_status,
        fetched_at=fetched_at,
        from_cache=False,
        used_stale_cache=False,
        success=bool(items),
        message="Steam 搜索完成。" if items else "Steam 搜索未返回结果。",
        items=items,
    )
    _save_search_cache_entry(cache_path, cache, cache_key, result)
    return result


def load_steam_store_feed_export_rows(cache_path: Path) -> list[dict]:
    cache = _load_cache(cache_path)
    if not cache:
        return []
    result = _result_from_cache(cache, from_cache=True, used_stale_cache=False, message="")
    rows = []
    for group_items in result.groups.values():
        for item in group_items:
            rows.append(
                {
                    "fetched_at": item.fetched_at,
                    "source_group": item.source_group,
                    "search_source_filter": item.source_filter,
                    "appid": item.appid,
                    "game_name": item.game_name,
                    "steam_url": item.steam_url,
                    "image_url": item.image_url,
                    "price": item.price,
                    "release_date": item.release_date,
                    "review_summary": item.review_summary,
                }
            )
    return rows


def _fetch_steam_store_home_feed() -> SteamStoreFeedResult:
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groups = _empty_groups()
    errors = []
    for source_group, filters in STEAM_HOME_FEED_GROUPS:
        items = []
        for search_filter in filters:
            try:
                payload = _fetch_search_results(search_filter, count=12)
                items = _parse_search_payload(payload, source_group, search_filter, fetched_at)
            except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{source_group}/{search_filter}: {exc}")
                items = []
            if items:
                break
        groups[source_group] = items[:12]

    success = any(groups.values())
    message = "Steam 图文源已刷新。" if success else "Steam 图文源未取得项目，首页会显示缓存或入口卡。"
    return SteamStoreFeedResult(
        fetched_at=fetched_at,
        from_cache=False,
        used_stale_cache=False,
        success=success,
        message=message,
        groups=groups,
        errors=errors,
    )


def _fetch_search_results(search_filter: str, count: int, term: str = "") -> dict:
    params = {
        "json": "1",
        "count": str(count),
        "start": "0",
        "category1": "998",
        "l": "schinese",
        "cc": "CN",
    }
    if search_filter:
        params["filter"] = search_filter
    if term:
        params["term"] = term
    request = Request(
        SEARCH_RESULTS_URL + "?" + urlencode(params),
        headers={
            "User-Agent": "steam-project-assistant/0.5.7 (+steam-search-results)",
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _parse_search_payload(payload: dict, source_group: str, source_filter: str, fetched_at: str) -> list[SteamStoreFeedItem]:
    raw_items = payload.get("items")
    if isinstance(raw_items, list):
        items = _parse_structured_items(raw_items, source_group, source_filter, fetched_at)
        if items:
            return items

    html = str(payload.get("results_html", "") or "")
    if html:
        items = _parse_results_html(html, source_group, source_filter, fetched_at)
        if items:
            return items
    return []


def _parse_structured_items(raw_items: list, source_group: str, source_filter: str, fetched_at: str) -> list[SteamStoreFeedItem]:
    items = []
    seen = set()
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        image_url = str(raw.get("img") or raw.get("image") or raw.get("capsule") or raw.get("logo") or "")
        appid = str(raw.get("id") or raw.get("appid") or "").strip()
        if not appid:
            app_match = re.search(r"/apps/(\d+)/", image_url)
            if app_match:
                appid = app_match.group(1)
        if not appid or appid in seen:
            continue
        seen.add(appid)
        name = str(raw.get("name") or raw.get("title") or "").strip()
        items.append(
            SteamStoreFeedItem(
                fetched_at=fetched_at,
                source_group=source_group,
                source_filter=source_filter,
                appid=appid,
                game_name=name,
                steam_url=f"https://store.steampowered.com/app/{appid}/",
                image_url=_clean_url(image_url),
                price=str(raw.get("price") or raw.get("final_price") or ""),
                release_date=str(raw.get("release_date") or raw.get("released") or ""),
                review_summary=str(raw.get("review_summary") or raw.get("reviews") or ""),
            )
        )
    return items


def _parse_results_html(html: str, source_group: str, source_filter: str, fetched_at: str) -> list[SteamStoreFeedItem]:
    rows = re.findall(r'<a\b[^>]*href="https://store\.steampowered\.com/app/(\d+)/[^"]*"[^>]*>(.*?)</a>', html, flags=re.I | re.S)
    items = []
    seen = set()
    for appid, block in rows:
        if appid in seen:
            continue
        seen.add(appid)
        name = _first_text(block, r'class="title"[^>]*>(.*?)</span>') or _strip_tags(block)
        image_url = _first_attr(block, r'<img\b[^>]*\bsrc="([^"]+)"')
        release_date = _first_text(block, r'class="[^"]*search_released[^"]*"[^>]*>(.*?)</div>')
        price = _first_text(block, r'class="[^"]*search_price[^"]*"[^>]*>(.*?)</div>')
        review_summary = _first_attr(block, r'class="[^"]*search_review_summary[^"]*"[^>]*data-tooltip-html="([^"]+)"')
        if not review_summary:
            review_summary = _first_text(block, r'class="[^"]*search_review_summary[^"]*"[^>]*>(.*?)</span>')
        items.append(
            SteamStoreFeedItem(
                fetched_at=fetched_at,
                source_group=source_group,
                source_filter=source_filter,
                appid=appid,
                game_name=_clean_text(name),
                steam_url=f"https://store.steampowered.com/app/{appid}/",
                image_url=_clean_url(image_url),
                price=_clean_text(price),
                release_date=_clean_text(release_date),
                review_summary=_clean_text(review_summary),
            )
        )
    return [item for item in items if item.appid and item.game_name]


def _first_text(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.I | re.S)
    if not match:
        return ""
    return _strip_tags(match.group(1))


def _first_attr(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.I | re.S)
    if not match:
        return ""
    return unescape(match.group(1)).strip()


def _strip_tags(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return _clean_text(text)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(str(text or ""))).strip()


def _clean_url(url: str) -> str:
    return unescape(str(url or "")).replace("\\/", "/").strip()


def _empty_groups() -> dict[str, list[SteamStoreFeedItem]]:
    return {source_group: [] for source_group, _ in STEAM_HOME_FEED_GROUPS}


def _load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_cache(cache_path: Path, result: SteamStoreFeedResult) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cached_at": datetime.now().isoformat(timespec="seconds"),
        "fetched_at": result.fetched_at,
        "success": result.success,
        "message": result.message,
        "errors": result.errors,
        "groups": {
            key: [asdict(item) for item in value]
            for key, value in result.groups.items()
        },
    }
    try:
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _save_search_cache_entry(cache_path: Path, cache: dict, cache_key: str, result: SteamStoreSearchResult) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(cache) if isinstance(cache, dict) else {}
    queries = payload.get("queries") if isinstance(payload.get("queries"), dict) else {}
    queries[cache_key] = {
        "cached_at": datetime.now().isoformat(timespec="seconds"),
        "fetched_at": result.fetched_at,
        "query": result.query,
        "status_filter": result.status_filter,
        "success": result.success,
        "message": result.message,
        "error": result.error,
        "items": [asdict(item) for item in result.items],
    }
    payload["queries"] = queries
    try:
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _cache_is_fresh(cache: dict) -> bool:
    age = _cache_age_seconds(cache)
    return 0 <= age <= CACHE_TTL_MINUTES * 60


def _cache_age_seconds(cache: dict) -> float:
    cached_at = str(cache.get("cached_at", "") or "")
    try:
        cached_time = datetime.fromisoformat(cached_at)
    except ValueError:
        return -1
    return (datetime.now() - cached_time).total_seconds()


def _search_cache_key(query: str, status_filter: str) -> str:
    return f"{query.casefold()}|{status_filter}"


def _search_result_from_cache_entry(
    query: str,
    status_filter: str,
    entry: dict,
    *,
    from_cache: bool,
    used_stale_cache: bool,
    message: str,
    error: str = "",
) -> SteamStoreSearchResult:
    rows = []
    for row in entry.get("items", []) if isinstance(entry.get("items"), list) else []:
        if isinstance(row, dict):
            rows.append(SteamStoreFeedItem(**row))
    return SteamStoreSearchResult(
        query=query,
        status_filter=status_filter,
        fetched_at=str(entry.get("fetched_at", "") or ""),
        from_cache=from_cache,
        used_stale_cache=used_stale_cache,
        success=bool(entry.get("success") or rows),
        message=message,
        items=rows,
        error=error or str(entry.get("error", "") or ""),
    )


def _result_from_cache(cache: dict, from_cache: bool, used_stale_cache: bool, message: str) -> SteamStoreFeedResult:
    groups = _empty_groups()
    for key, rows in (cache.get("groups") or {}).items():
        normalized_key = _normalize_source_group(key)
        if isinstance(rows, list):
            normalized_rows = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                row = dict(row)
                row["source_group"] = _normalize_source_group(row.get("source_group") or key)
                normalized_rows.append(SteamStoreFeedItem(**row))
            groups.setdefault(normalized_key, [])
            groups[normalized_key].extend(normalized_rows)
    return SteamStoreFeedResult(
        fetched_at=str(cache.get("fetched_at", "") or ""),
        from_cache=from_cache,
        used_stale_cache=used_stale_cache,
        success=bool(cache.get("success") or any(groups.values())),
        message=message,
        groups=groups,
        errors=[str(error) for error in cache.get("errors", [])],
    )


def _normalize_source_group(group_name: str) -> str:
    raw = str(group_name or "").strip()
    return SOURCE_GROUP_ALIASES.get(raw, raw)
