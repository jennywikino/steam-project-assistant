from dataclasses import asdict, dataclass, field
from datetime import datetime
from html import unescape
from pathlib import Path
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CACHE_TTL_MINUTES = 30
REQUEST_TIMEOUT_SECONDS = 10

STEAMDB_CHARTS_URL = "https://steamdb.info/charts/"
STEAMDB_TRENDING_FOLLOWERS_URL = "https://steamdb.info/stats/trendingfollowers/"
STEAMDB_WISHLIST_ACTIVITY_URL = "https://steamdb.info/stats/wishlistactivity/"
STEAMDB_MOST_WISHLISTED_URL = "https://steamdb.info/stats/mostwished/"
STEAM_STATS_FALLBACK_URL = "https://store.steampowered.com/charts/mostplayed"
STEAM_NEWS_FEED_URL = "https://store.steampowered.com/feeds/news.xml"


@dataclass
class HomeFeedItem:
    game_name: str = ""
    appid: str = ""
    source: str = ""
    source_url: str = ""
    steamdb_url: str = ""
    steam_url: str = ""
    metric: str = ""
    current_players: str = ""
    peak_24h: str = ""
    release_or_wishlist: str = ""
    note: str = ""


@dataclass
class HomeNewsItem:
    title: str = ""
    url: str = ""
    source: str = "Steam News"


@dataclass
class HomeFeedResult:
    refreshed_at: str = ""
    from_cache: bool = False
    used_stale_cache: bool = False
    message: str = ""
    sections: dict[str, list[HomeFeedItem]] = field(default_factory=dict)
    news: list[HomeNewsItem] = field(default_factory=list)


def load_home_feed(cache_path: Path, force_refresh: bool = False) -> HomeFeedResult:
    cache = _load_cache(cache_path)
    if cache and not force_refresh:
        stale = not _cache_is_fresh(cache)
        message = "当前显示缓存数据。" if not stale else "当前显示缓存数据；点击刷新可更新今日信息流。"
        return _result_from_cache(cache, from_cache=True, used_stale_cache=stale, message=message)
    if cache and force_refresh and _cache_age_seconds(cache) < 60:
        return _result_from_cache(cache, from_cache=True, used_stale_cache=False, message="刚刷新过，已避免重复请求。")

    try:
        result = _fetch_home_feed()
    except Exception as exc:
        if cache:
            return _result_from_cache(
                cache,
                from_cache=True,
                used_stale_cache=True,
                message=f"刷新失败，当前显示缓存数据：{exc}",
            )
        result = HomeFeedResult(
            refreshed_at="",
            message="获取失败，可手动打开入口。",
            sections=_empty_sections(),
            news=[],
        )
        _save_cache(cache_path, result)
        return result

    _save_cache(cache_path, result)
    return result


def _fetch_home_feed() -> HomeFeedResult:
    sections = _empty_sections()
    messages = []

    charts_items = []
    try:
        charts_items = _parse_steamdb_table(
            _http_get(STEAMDB_CHARTS_URL),
            source="SteamDB 热门在线",
            source_url=STEAMDB_CHARTS_URL,
            limit=5,
            metric_mode="charts",
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        messages.append(f"SteamDB Charts 获取失败：{exc}")
        try:
            charts_items = _parse_steam_charts_fallback(_http_get(STEAM_STATS_FALLBACK_URL), limit=5)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as fallback_exc:
            messages.append(f"Steam 官方 Stats 备用也失败：{fallback_exc}")
    sections["charts"] = charts_items[:5]

    try:
        sections["trending_followers"] = _parse_steamdb_table(
            _http_get(STEAMDB_TRENDING_FOLLOWERS_URL),
            source="Trending Followers",
            source_url=STEAMDB_TRENDING_FOLLOWERS_URL,
            limit=5,
            metric_mode="generic",
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        messages.append(f"Trending Followers 获取失败：{exc}")

    wishlist_items = []
    try:
        wishlist_items = _parse_steamdb_table(
            _http_get(STEAMDB_WISHLIST_ACTIVITY_URL),
            source="Wishlist Activity",
            source_url=STEAMDB_WISHLIST_ACTIVITY_URL,
            limit=5,
            metric_mode="wishlist",
        )
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        messages.append(f"Wishlist Activity 获取失败：{exc}")
        try:
            wishlist_items = _parse_steamdb_table(
                _http_get(STEAMDB_MOST_WISHLISTED_URL),
                source="Most Wishlisted",
                source_url=STEAMDB_MOST_WISHLISTED_URL,
                limit=5,
                metric_mode="wishlist",
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as fallback_exc:
            messages.append(f"Most Wishlisted 获取失败：{fallback_exc}")
    sections["wishlist"] = wishlist_items[:5]

    news = []
    try:
        news = _parse_steam_news_feed(_http_get(STEAM_NEWS_FEED_URL), limit=3)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        messages.append(f"Steam News 获取失败：{exc}")

    return HomeFeedResult(
        refreshed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_cache=False,
        used_stale_cache=False,
        message="；".join(messages) if messages else "今日信息流已刷新。",
        sections=sections,
        news=news,
    )


def _http_get(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SteamProjectAssistant/0.5.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8", errors="ignore")


def _parse_steamdb_table(
    html: str,
    source: str,
    source_url: str,
    limit: int,
    metric_mode: str,
) -> list[HomeFeedItem]:
    rows = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, flags=re.IGNORECASE | re.DOTALL)
    items = []
    seen = set()
    for row in rows:
        app_match = re.search(r'href="/app/(\d+)/(?:[^"]*)"', row, flags=re.IGNORECASE)
        if not app_match:
            continue
        appid = app_match.group(1)
        if appid in seen:
            continue
        seen.add(appid)
        name = _extract_app_name(row, appid)
        if not name:
            continue
        cells = _extract_cells(row)
        metric = _compact_metric(cells)
        current_players = ""
        peak_24h = ""
        release_or_wishlist = ""
        if metric_mode == "charts":
            current_players = cells[1] if len(cells) > 1 else ""
            peak_24h = cells[2] if len(cells) > 2 else ""
            metric = " / ".join(part for part in [f"当前 {current_players}" if current_players else "", f"24h {peak_24h}" if peak_24h else ""] if part)
        elif metric_mode == "wishlist":
            release_or_wishlist = metric
        items.append(
            HomeFeedItem(
                game_name=name,
                appid=appid,
                source=source,
                source_url=source_url,
                steamdb_url=f"https://steamdb.info/app/{appid}/",
                steam_url=f"https://store.steampowered.com/app/{appid}/",
                metric=metric,
                current_players=current_players,
                peak_24h=peak_24h,
                release_or_wishlist=release_or_wishlist,
            )
        )
        if len(items) >= limit:
            break
    if not items:
        raise ValueError("未解析到榜单项目")
    return items


def _parse_steam_charts_fallback(html: str, limit: int) -> list[HomeFeedItem]:
    app_blocks = re.findall(r'href="https://store\.steampowered\.com/app/(\d+)/[^"]*"[^>]*>(.*?)</a>', html, flags=re.IGNORECASE | re.DOTALL)
    items = []
    seen = set()
    for appid, block in app_blocks:
        if appid in seen:
            continue
        seen.add(appid)
        name = _strip_tags(block)
        if not name:
            continue
        items.append(
            HomeFeedItem(
                game_name=name,
                appid=appid,
                source="Steam 官方 Stats",
                source_url=STEAM_STATS_FALLBACK_URL,
                steamdb_url=f"https://steamdb.info/app/{appid}/",
                steam_url=f"https://store.steampowered.com/app/{appid}/",
                metric="Steam most played",
            )
        )
        if len(items) >= limit:
            break
    if not items:
        raise ValueError("未解析到 Steam 官方榜单项目")
    return items


def _parse_steam_news_feed(xml: str, limit: int) -> list[HomeNewsItem]:
    item_blocks = re.findall(r"<item\b[^>]*>(.*?)</item>", xml, flags=re.IGNORECASE | re.DOTALL)
    news = []
    for block in item_blocks:
        title = _first_xml_text(block, "title")
        link = _first_xml_text(block, "link")
        if title:
            news.append(HomeNewsItem(title=title, url=link or "https://store.steampowered.com/news/"))
        if len(news) >= limit:
            break
    if not news:
        raise ValueError("未解析到 Steam 新闻")
    return news


def _extract_app_name(row: str, appid: str) -> str:
    match = re.search(rf'href="/app/{appid}/[^"]*"[^>]*>(.*?)</a>', row, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    name = _strip_tags(match.group(1))
    return re.sub(r"\s+", " ", name).strip()


def _extract_cells(row: str) -> list[str]:
    cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row, flags=re.IGNORECASE | re.DOTALL)
    return [_strip_tags(cell) for cell in cells if _strip_tags(cell)]


def _compact_metric(cells: list[str]) -> str:
    parts = [cell for cell in cells[1:5] if cell and cell not in {"-", "—"}]
    return " / ".join(parts[:3])


def _first_xml_text(block: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", block, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return _strip_tags(match.group(1))


def _strip_tags(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _empty_sections() -> dict[str, list[HomeFeedItem]]:
    return {"charts": [], "trending_followers": [], "wishlist": []}


def _load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(cache_path: Path, result: HomeFeedResult) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cached_at": datetime.now().isoformat(timespec="seconds"),
        "refreshed_at": result.refreshed_at,
        "message": result.message,
        "sections": {
            key: [asdict(item) for item in value]
            for key, value in result.sections.items()
        },
        "news": [asdict(item) for item in result.news],
    }
    try:
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _cache_is_fresh(cache: dict) -> bool:
    age = _cache_age_seconds(cache)
    if age < 0:
        return False
    return age <= CACHE_TTL_MINUTES * 60


def _cache_age_seconds(cache: dict) -> float:
    cached_at = cache.get("cached_at", "")
    try:
        cached_time = datetime.fromisoformat(cached_at)
    except ValueError:
        return -1
    return (datetime.now() - cached_time).total_seconds()


def _result_from_cache(cache: dict, from_cache: bool, used_stale_cache: bool, message: str) -> HomeFeedResult:
    sections = {}
    for key, rows in cache.get("sections", {}).items():
        sections[key] = [HomeFeedItem(**row) for row in rows]
    for key in _empty_sections():
        sections.setdefault(key, [])
    news = [HomeNewsItem(**row) for row in cache.get("news", [])]
    return HomeFeedResult(
        refreshed_at=cache.get("refreshed_at", ""),
        from_cache=from_cache,
        used_stale_cache=used_stale_cache,
        message=message,
        sections=sections,
        news=news,
    )
