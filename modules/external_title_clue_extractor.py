import re
import time
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from modules.genre_signal_extractor import extract_genre_signals


REQUEST_TIMEOUT_SECONDS = 8
MAX_TITLES_PER_SOURCE = 5
MAX_TOTAL_REQUESTS = 5


@dataclass
class ExternalTitleClues:
    raw_titles: list[str] = field(default_factory=list)
    extracted_terms: list[str] = field(default_factory=list)
    genre_terms: list[str] = field(default_factory=list)
    reference_games: list[str] = field(default_factory=list)
    source_message: str = ""


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.titles: list[str] = []
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if tag.lower() == "title" or attrs_dict.get("class", "").find("title") >= 0:
            self.in_title = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            clean = data.strip()
            if clean:
                self._parts.append(clean)

    def handle_endtag(self, tag: str) -> None:
        if self.in_title and tag.lower() in {"title", "a", "h3", "div", "span"}:
            title = " ".join(self._parts).strip()
            if title:
                self.titles.append(title)
            self.in_title = False
            self._parts = []


def extract_external_title_clues(pasted_titles: str) -> ExternalTitleClues:
    titles = [line.strip() for line in str(pasted_titles or "").splitlines() if line.strip()]
    text = "\n".join(titles)
    signals = extract_genre_signals(external_title_clues=text)
    terms = _extract_terms(text)
    extracted = _dedupe(terms + signals.external_title_terms + signals.reference_games)
    return ExternalTitleClues(
        raw_titles=titles,
        extracted_terms=extracted,
        genre_terms=signals.high_confidence_phrases,
        reference_games=signals.reference_games,
        source_message=f"已从 {len(titles)} 条标题提取线索。" if titles else "未提供外部标题线索。",
    )


def fetch_external_title_clues(game_name: str, english_name: str = "", appid: str = "") -> ExternalTitleClues:
    queries = _build_queries(game_name, english_name, appid)
    if not queries:
        return ExternalTitleClues(source_message="自动抓取失败，请手动粘贴标题。")

    titles = []
    for source_name, url in queries[:MAX_TOTAL_REQUESTS]:
        try:
            html = _http_get(url)
        except (HTTPError, URLError, TimeoutError, OSError):
            continue
        source_titles = _extract_titles_from_html(html)
        for title in source_titles[:MAX_TITLES_PER_SOURCE]:
            clean = _clean_title(title)
            if clean and clean.casefold() not in {item.casefold() for item in titles}:
                titles.append(f"{source_name}: {clean}")
        time.sleep(0.8)

    if not titles:
        return ExternalTitleClues(source_message="自动抓取失败，请手动粘贴标题。")
    clues = extract_external_title_clues("\n".join(titles))
    clues.source_message = f"自动抓取到 {len(titles)} 条标题线索。"
    return clues


def _build_queries(game_name: str, english_name: str, appid: str) -> list[tuple[str, str]]:
    name = (game_name or english_name or "").strip()
    if not name and appid:
        name = str(appid).strip()
    if not name:
        return []
    encoded = quote(name, safe="")
    encoded_trial = quote(f"{name} 试玩", safe="")
    encoded_gameplay = quote(f"{name} gameplay", safe="")
    return [
        ("B站", f"https://search.bilibili.com/all?keyword={encoded}"),
        ("B站试玩", f"https://search.bilibili.com/all?keyword={encoded_trial}"),
        ("百度试玩", f"https://www.baidu.com/s?wd={encoded_trial}"),
        ("Google gameplay", f"https://www.google.com/search?q={encoded_gameplay}"),
        ("YouTube gameplay", f"https://www.youtube.com/results?search_query={encoded_gameplay}"),
    ]


def _http_get(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "steam-project-assistant/0.4.2 (+title-clues)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _extract_titles_from_html(html: str) -> list[str]:
    titles = []
    for pattern in [
        r'<h3[^>]*>(.*?)</h3>',
        r'<a[^>]+title="([^"]+)"',
        r'"title"\s*:\s*"([^"]{4,120})"',
        r'<title[^>]*>(.*?)</title>',
    ]:
        for raw in re.findall(pattern, html, flags=re.S | re.I):
            clean = _clean_title(raw)
            if clean and clean.casefold() not in {item.casefold() for item in titles}:
                titles.append(clean)
    if titles:
        return titles[:30]
    parser = _TitleParser()
    parser.feed(html)
    return [_clean_title(title) for title in parser.titles if _clean_title(title)][:30]


def _extract_terms(text: str) -> list[str]:
    terms = []
    patterns = [
        "放置卡牌战斗",
        "卡牌战斗",
        "卡牌肉鸽",
        "卡组构筑",
        "牌组构筑",
        "回合制战术",
        "类炉石",
        "炉石",
        "类杀戮尖塔",
        "杀戮尖塔",
        "类小丑牌",
        "小丑牌",
        "steam新品节",
        "试玩推荐",
        "Slay the Spire",
        "Balatro",
        "Monster Train",
        "Hearthstone",
    ]
    lower_text = str(text or "").casefold()
    for pattern in patterns:
        if pattern.casefold() in lower_text:
            terms.append(pattern)
    for name in re.findall(r"[A-Z][A-Za-z0-9: '&-]{2,40}", str(text or "")):
        clean = _clean_title(name).strip(" -|")
        if clean and clean.casefold() not in {"steam", "youtube", "google"}:
            terms.append(clean)
    return _dedupe(terms)


def _clean_title(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(str(value or "")))
    text = text.replace("\\u0026", "&")
    text = text.replace("\\/", "/")
    return re.sub(r"\s+", " ", text).strip()


def _dedupe(values: list[str]) -> list[str]:
    output = []
    seen = set()
    for value in values:
        clean = str(value).strip()
        marker = clean.casefold()
        if clean and marker not in seen:
            seen.add(marker)
            output.append(clean)
    return output
