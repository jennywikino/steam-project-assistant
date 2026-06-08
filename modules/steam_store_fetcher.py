import json
import re
import time
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


STORE_API_URL = "https://store.steampowered.com/api/appdetails"
STORE_PAGE_URL = "https://store.steampowered.com/app/{appid}/"
REQUEST_TIMEOUT_SECONDS = 10
MIN_REQUEST_INTERVAL_SECONDS = 1.0

_last_request_at = 0.0


@dataclass
class SteamStoreFetchResult:
    success: bool
    message: str
    data: dict = field(default_factory=dict)


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


def parse_appid(raw_input: str) -> str:
    """Extract a Steam AppID from a raw AppID or a Steam store URL."""
    text = str(raw_input or "").strip()
    if not text:
        return ""
    if text.isdigit():
        return text

    parsed = urlparse(text)
    path = parsed.path if parsed.scheme else text
    match = re.search(r"/app/(\d+)(?:/|$)", path)
    if match:
        return match.group(1)

    fallback = re.search(r"\b(\d{3,10})\b", text)
    return fallback.group(1) if fallback else ""


def build_store_url(appid: str) -> str:
    return STORE_PAGE_URL.format(appid=str(appid).strip())


def fetch_steam_store_info(appid: str) -> SteamStoreFetchResult:
    """Fetch public Steam store metadata without login, API keys, or aggressive crawling."""
    clean_appid = parse_appid(appid)
    if not clean_appid:
        return SteamStoreFetchResult(False, "未能解析 Steam AppID。", _empty_store_data(""))

    data = _empty_store_data(clean_appid)
    try:
        api_payload = _fetch_appdetails(clean_appid)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return SteamStoreFetchResult(
            False,
            f"自动获取失败，请手动补充。原因：{exc}",
            data,
        )

    app_entry = api_payload.get(clean_appid, {})
    if not app_entry.get("success"):
        return SteamStoreFetchResult(False, "自动获取失败，请手动补充。Steam 未返回有效公开信息。", data)

    details = app_entry.get("data") or {}
    data.update(_normalize_appdetails(clean_appid, details))

    page_tags, page_demo = _fetch_page_tags_and_demo_flag(clean_appid)
    if page_tags:
        data["tags"] = page_tags
    if page_demo is not None and not data.get("has_demo"):
        data["has_demo"] = page_demo

    return SteamStoreFetchResult(True, "已获取 Steam 商店公开信息。", data)


def _empty_store_data(appid: str) -> dict:
    return {
        "appid": str(appid or ""),
        "name": "",
        "steam_url": build_store_url(appid) if appid else "",
        "developers": [],
        "publishers": [],
        "developer": "",
        "publisher": "",
        "release_date": "",
        "release_status": "",
        "price": "",
        "supported_languages": "",
        "has_simplified_chinese": "",
        "genres": [],
        "categories": [],
        "tags": [],
        "short_description": "",
        "about_the_game": "",
        "header_image": "",
        "screenshots_count": 0,
        "movies_count": 0,
        "has_demo": "",
        "mature_content": "",
    }


def _fetch_appdetails(appid: str) -> dict:
    query = f"?appids={appid}&cc=cn&l=schinese&filters=basic,price_overview,genres,categories,platforms,release_date,screenshots,movies,demos,content_descriptors"
    raw = _http_get(STORE_API_URL + query)
    return json.loads(raw)


def _http_get(url: str) -> str:
    global _last_request_at
    elapsed = time.time() - _last_request_at
    if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)

    request = Request(
        url,
        headers={
            "User-Agent": "steam-project-assistant/0.4 (+public-store-metadata)",
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        _last_request_at = time.time()
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _normalize_appdetails(appid: str, details: dict) -> dict:
    data = _empty_store_data(appid)
    developers = _as_text_list(details.get("developers"))
    publishers = _as_text_list(details.get("publishers"))
    release_date = details.get("release_date") or {}
    price = details.get("price_overview") or {}
    supported_languages = _html_to_text(details.get("supported_languages", ""))
    genres = [item.get("description", "") for item in details.get("genres", []) if item.get("description")]
    categories = [item.get("description", "") for item in details.get("categories", []) if item.get("description")]
    screenshots = details.get("screenshots") or []
    movies = details.get("movies") or []
    demos = details.get("demos") or []
    content_descriptors = details.get("content_descriptors") or {}

    data.update(
        {
            "name": str(details.get("name", "") or ""),
            "steam_url": build_store_url(appid),
            "developers": developers,
            "publishers": publishers,
            "developer": ", ".join(developers),
            "publisher": ", ".join(publishers),
            "release_date": str(release_date.get("date", "") or ""),
            "release_status": _normalize_release_status(release_date),
            "price": str(price.get("final_formatted") or price.get("initial_formatted") or ""),
            "supported_languages": supported_languages,
            "has_simplified_chinese": _detect_simplified_chinese(supported_languages),
            "genres": genres,
            "categories": categories,
            "short_description": _clean_text(details.get("short_description", "")),
            "about_the_game": _html_to_text(details.get("about_the_game", "")),
            "header_image": str(details.get("header_image", "") or ""),
            "screenshots_count": len(screenshots) if isinstance(screenshots, list) else 0,
            "movies_count": len(movies) if isinstance(movies, list) else 0,
            "has_demo": "是" if demos else "",
            "mature_content": _mature_content_text(content_descriptors),
        }
    )
    return data


def _fetch_page_tags_and_demo_flag(appid: str) -> tuple[list[str], str | None]:
    try:
        html = _http_get(build_store_url(appid) + "?l=schinese")
    except (HTTPError, URLError, TimeoutError, OSError):
        return [], None

    tags = []
    for match in re.findall(r'<a[^>]+class="[^"]*app_tag[^"]*"[^>]*>(.*?)</a>', html, flags=re.S):
        tag = _html_to_text(match).strip()
        if tag and tag not in tags:
            tags.append(tag)
    if not tags:
        raw_tags = re.findall(r'"tag_name"\s*:\s*"([^"]+)"', html)
        for raw_tag in raw_tags:
            tag = unescape(raw_tag).strip()
            if tag and tag not in tags:
                tags.append(tag)

    demo_flag = None
    lowered = html.casefold()
    if "download demo" in lowered or "试玩" in html or "demo" in lowered:
        demo_flag = "是"

    return tags[:20], demo_flag


def _as_text_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [str(value).strip()]
    return []


def _html_to_text(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(unescape(str(value or "")))
    return _clean_text(parser.text())


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def _normalize_release_status(release_date: dict) -> str:
    if release_date.get("coming_soon"):
        return "未发售 / Coming Soon"
    date_text = str(release_date.get("date", "") or "").strip()
    return date_text or ""


def _detect_simplified_chinese(supported_languages: str) -> str:
    text = supported_languages.casefold()
    if "简体中文" in supported_languages or "simplified chinese" in text:
        return "是"
    if supported_languages.strip():
        return "否"
    return ""


def _mature_content_text(content_descriptors: dict) -> str:
    notes = content_descriptors.get("notes")
    if isinstance(notes, str):
        return _html_to_text(notes)
    ids = content_descriptors.get("ids")
    if ids:
        return ", ".join(str(item) for item in ids)
    return ""
