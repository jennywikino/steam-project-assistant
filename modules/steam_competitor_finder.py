import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from modules.genre_signal_extractor import LOW_WEIGHT_TAGS, extract_genre_signals


STEAM_SEARCH_URL = "https://store.steampowered.com/search/"
CACHE_TTL_HOURS = 24
REQUEST_TIMEOUT_SECONDS = 12
MAX_KEYWORDS = 5
MAX_RESULTS_PER_KEYWORD = 10
MAX_TOTAL_CANDIDATES = 30


@dataclass
class SteamCompetitorCandidate:
    target_appid: str = ""
    target_game_name: str = ""
    candidate_name: str = ""
    candidate_steam_url: str = ""
    candidate_appid: str = ""
    source_keyword: str = ""
    source_type: str = "Steam搜索"
    candidate_price: str = ""
    candidate_release_date: str = ""
    candidate_review_summary: str = ""
    candidate_tags: str = ""
    match_score: int = 0
    match_level: str = "低"
    match_reason: str = ""
    user_decision: str = "待确认"
    notes: str = ""


@dataclass
class SteamCompetitorFindResult:
    success: bool
    message: str
    keywords: list[str] = field(default_factory=list)
    candidates: list[SteamCompetitorCandidate] = field(default_factory=list)
    used_cache: bool = False


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


def find_steam_competitor_candidates(
    game_info: dict,
    cache_path: Path,
    user_keywords: str = "",
    external_title_clues: str = "",
    ignore_cache: bool = False,
    include_low_weight_tags: bool = False,
) -> SteamCompetitorFindResult:
    """Find conservative Steam competitor candidates from keyword search results."""
    target_appid = str(game_info.get("appid", "") or "").strip()
    target_game_name = str(game_info.get("name", "") or game_info.get("game_name", "") or "").strip()
    signals = extract_genre_signals(
        short_description=str(game_info.get("short_description", "") or ""),
        about_the_game=str(game_info.get("about_the_game", "") or ""),
        genres=game_info.get("genres"),
        tags=game_info.get("tags"),
        user_keywords=user_keywords,
        external_title_clues=external_title_clues,
    )
    keywords = build_competitor_search_keywords(
        game_info,
        user_keywords,
        external_title_clues=external_title_clues,
        include_low_weight_tags=include_low_weight_tags,
    )
    if not keywords:
        return SteamCompetitorFindResult(False, "竞品候选抓取失败，可使用搜索中心手动查找。", [])

    all_candidates: list[SteamCompetitorCandidate] = []
    seen_appids = {target_appid} if target_appid else set()
    used_cache = False

    for keyword in keywords:
        cache_key = _cache_key(target_appid, keyword)
        cached_results = None if ignore_cache else _read_cached_results(cache_path, cache_key)
        if cached_results is not None:
            used_cache = True
            raw_results = cached_results
        else:
            try:
                raw_results = _fetch_search_results(keyword)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                if all_candidates:
                    break
                return SteamCompetitorFindResult(
                    False,
                    f"竞品候选抓取失败，可使用搜索中心手动查找。原因：{exc}",
                    keywords,
                    [],
                    used_cache,
                )
            _write_cached_results(cache_path, cache_key, keyword, raw_results)

        for raw in raw_results:
            candidate_appid = str(raw.get("candidate_appid", "") or "").strip()
            if not candidate_appid or candidate_appid in seen_appids:
                continue
            seen_appids.add(candidate_appid)
            all_candidates.append(
                _build_candidate(raw, game_info, target_appid, target_game_name, keyword, signals)
            )
            if len(all_candidates) >= MAX_TOTAL_CANDIDATES:
                break
        if len(all_candidates) >= MAX_TOTAL_CANDIDATES:
            break

    if not all_candidates:
        return SteamCompetitorFindResult(
            False,
            "未找到可用 Steam 竞品候选，可使用搜索中心手动查找。",
            keywords,
            [],
            used_cache,
        )

    sorted_candidates = sorted(
        all_candidates,
        key=lambda item: (item.match_score, bool(item.candidate_review_summary), item.candidate_release_date),
        reverse=True,
    )

    return SteamCompetitorFindResult(
        True,
        f"已找到 {len(sorted_candidates)} 个 Steam 竞品候选。",
        keywords,
        sorted_candidates,
        used_cache,
    )


def build_competitor_search_keywords(
    game_info: dict,
    user_keywords: str = "",
    external_title_clues: str = "",
    include_low_weight_tags: bool = False,
) -> list[str]:
    terms = []

    def add(value: str) -> None:
        clean = " ".join(str(value or "").split()).strip()
        if not clean:
            return
        normalized = clean.casefold()
        if normalized not in {item.casefold() for item in terms}:
            terms.append(clean)

    signals = extract_genre_signals(
        short_description=str(game_info.get("short_description", "") or ""),
        about_the_game=str(game_info.get("about_the_game", "") or ""),
        genres=game_info.get("genres"),
        tags=game_info.get("tags"),
        user_keywords=user_keywords,
        external_title_clues=external_title_clues,
    )

    primary_terms = signals.search_keywords[:3] if signals.reference_games else signals.search_keywords
    for term in primary_terms:
        add(term)
    external_references = _extract_reference_games_from_text(external_title_clues)
    for reference in _dedupe(signals.reference_games + external_references):
        add(reference)

    tags = _split_terms(game_info.get("tags"))
    genres = _split_terms(game_info.get("genres"))
    strong_tags = [tag for tag in tags + genres if _normalize(tag) not in LOW_WEIGHT_TAGS]
    if len(strong_tags) >= 2:
        add(f"{strong_tags[0]} {strong_tags[1]}")
    if len(strong_tags) >= 3:
        add(f"{strong_tags[0]} {strong_tags[2]}")

    if include_low_weight_tags and not terms:
        for term in tags + genres:
            add(term)

    return terms[:MAX_KEYWORDS]


def candidate_to_dict(candidate: SteamCompetitorCandidate) -> dict:
    return asdict(candidate)


def _fetch_search_results(keyword: str) -> list[dict]:
    url = (
        f"{STEAM_SEARCH_URL}?term={quote(keyword, safe='')}"
        "&category1=998&ndl=1&supportedlang=schinese"
    )
    html = _http_get(url)
    return _parse_search_results(html, keyword)[:MAX_RESULTS_PER_KEYWORD]


def _http_get(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "steam-project-assistant/0.4.1 (+steam-search-candidates)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _parse_search_results(html: str, keyword: str) -> list[dict]:
    rows = re.findall(
        r'<a[^>]+class="[^"]*search_result_row[^"]*"[^>]*>.*?</a>',
        html,
        flags=re.S | re.I,
    )
    results = []
    for row_html in rows:
        appid = _attr(row_html, "data-ds-appid") or _appid_from_href(_attr(row_html, "href"))
        if not appid:
            continue
        name = _text_from_class(row_html, "title")
        if not name:
            continue
        href = _attr(row_html, "href") or f"https://store.steampowered.com/app/{appid}/"
        if "/app/" not in href:
            continue
        results.append(
            {
                "candidate_name": name,
                "candidate_steam_url": _clean_store_url(href, appid),
                "candidate_appid": appid,
                "candidate_price": _text_from_class(row_html, "search_price"),
                "candidate_release_date": _text_from_class(row_html, "search_released"),
                "candidate_review_summary": _review_summary(row_html),
                "candidate_tags": _search_tags(row_html),
                "source_keyword": keyword,
            }
        )
    return results


def _build_candidate(
    raw: dict,
    game_info: dict,
    target_appid: str,
    target_game_name: str,
    keyword: str,
    signals,
) -> SteamCompetitorCandidate:
    target_tags = _split_terms(game_info.get("genres")) + _split_terms(game_info.get("tags"))
    candidate_tags = _split_terms(raw.get("candidate_tags"))
    score, level, reason = _score_candidate(raw, keyword, target_tags, signals, str(game_info.get("release_status", "")))
    return SteamCompetitorCandidate(
        target_appid=target_appid,
        target_game_name=target_game_name,
        candidate_name=raw.get("candidate_name", ""),
        candidate_steam_url=raw.get("candidate_steam_url", ""),
        candidate_appid=raw.get("candidate_appid", ""),
        source_keyword=keyword,
        candidate_price=raw.get("candidate_price", ""),
        candidate_release_date=raw.get("candidate_release_date", ""),
        candidate_review_summary=raw.get("candidate_review_summary", ""),
        candidate_tags=", ".join(candidate_tags),
        match_score=score,
        match_level=level,
        match_reason=reason,
        notes="由 V0.4.2 Steam 搜索自动发现，需人工确认。",
    )


def _build_match_reason(keyword: str, target_tags: list[str], candidate_tags: list[str]) -> str:
    shared = [
        tag for tag in candidate_tags
        if tag.casefold() in {target_tag.casefold() for target_tag in target_tags}
    ]
    if shared:
        return f"共享 {', '.join(shared[:3])} 标签。"
    if keyword:
        return f"同一玩法关键词“{keyword}”下出现。"
    return "搜索相关，匹配度待人工确认。"


def _score_candidate(raw: dict, keyword: str, target_tags: list[str], signals, release_status: str) -> tuple[int, str, str]:
    name = str(raw.get("candidate_name", "") or "")
    tags = _split_terms(raw.get("candidate_tags"))
    candidate_haystack = _normalize(" ".join([name, raw.get("candidate_tags", "")]))
    keyword_haystack = _normalize(keyword)
    haystack = _normalize(" ".join([candidate_haystack, keyword_haystack]))
    score = 0
    reasons = []

    if any(term in candidate_haystack for term in ["deckbuilder", "deck builder", "deck-building", "card battler", "card game", "card", "卡牌", "卡组", "牌组"]):
        score += 40
        reasons.append("卡牌/构筑信号")
    elif any(term in keyword_haystack for term in ["deckbuilder", "card battler", "card game", "卡牌", "卡组"]):
        score += 15
        reasons.append("来源为卡牌构筑搜索")

    if any(term in candidate_haystack for term in ["roguelite", "roguelike", "肉鸽", "类 rogue", "轻度 rogue"]):
        score += 30
        reasons.append("肉鸽信号")
    elif any(term in keyword_haystack for term in ["roguelite", "roguelike", "肉鸽"]):
        score += 10
    reference_hit = False
    for reference in signals.reference_games:
        if _normalize(reference) in haystack or _normalize(reference) in _normalize(keyword):
            reference_hit = True
            score += 35
            reasons.append(f"{reference} 类比")
            break

    shared_high_tags = [
        tag for tag in tags
        if _normalize(tag) in {_normalize(target_tag) for target_tag in target_tags}
        and _normalize(tag) not in LOW_WEIGHT_TAGS
    ]
    if len(shared_high_tags) >= 2:
        score += 20
        reasons.append("共享高价值标签")
    if release_status and raw.get("candidate_release_date"):
        score += 10

    generic_terms = {"strategy", "turn-based tactics", "turn based tactics", "策略", "回合制战术"}
    if _normalize(keyword) in generic_terms and score < 40:
        score -= 30
        reasons.append("仅命中泛策略词")

    if "卡牌肉鸽" in signals.primary_type:
        if _is_large_strategy_ip(name, tags):
            score -= 40
            reasons.append("大型策略/IP偏离")
        if not reference_hit and not any(term in candidate_haystack for term in ["card", "deck", "roguelite", "roguelike", "卡牌", "卡组", "肉鸽", "类 rogue", "轻度 rogue"]):
            score -= 20

    if _is_non_game_or_dlc(name, tags):
        score -= 50
        reasons.append("疑似 DLC/非游戏")

    score = max(0, min(100, score))
    level = "高" if score >= 70 else "中" if score >= 40 else "低"
    if reasons:
        reason = "；".join(reasons[:2]) + "。"
    else:
        reason = _build_match_reason(keyword, target_tags, tags)
    return score, level, reason


def _extract_reference_games_from_text(text: str) -> list[str]:
    normalized = _normalize(text)
    refs = []
    checks = {
        "Slay the Spire": ["slay the spire", "杀戮尖塔"],
        "Balatro": ["balatro", "小丑牌"],
        "Monster Train": ["monster train", "怪物火车"],
        "Hearthstone": ["hearthstone", "炉石", "炉石传说"],
    }
    for name, aliases in checks.items():
        if any(alias in normalized for alias in aliases):
            refs.append(name)
    return refs


def _is_large_strategy_ip(name: str, tags: list[str]) -> bool:
    text = _normalize(" ".join([name, " ".join(tags)]))
    patterns = [
        "heroes of might and magic",
        "warhammer 40",
        "total war",
        "civilization",
        "age of wonders",
        "4x",
        "grand strategy",
        "大战略",
        "大型ip",
        "传统战棋",
    ]
    return any(pattern in text for pattern in patterns)


def _is_non_game_or_dlc(name: str, tags: list[str]) -> bool:
    text = _normalize(" ".join([name, " ".join(tags)]))
    return any(term in text for term in ["soundtrack", "ost", "dlc", "demo", "tool", "software", "原声", "壁纸"])


def _read_cached_results(cache_path: Path, cache_key: str) -> list[dict] | None:
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    entry = cache.get(cache_key)
    if not isinstance(entry, dict):
        return None
    queried_at = _parse_datetime(entry.get("queried_at", ""))
    if not queried_at:
        return None
    if datetime.now() - queried_at > timedelta(hours=CACHE_TTL_HOURS):
        return None
    results = entry.get("results")
    return results if isinstance(results, list) else None


def _write_cached_results(cache_path: Path, cache_key: str, keyword: str, results: list[dict]) -> None:
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}
        cache[cache_key] = {
            "queried_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "keyword": keyword,
            "results": results,
        }
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def _cache_key(appid: str, keyword: str) -> str:
    return f"{appid or 'no_appid'}::{keyword.casefold()}"


def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _attr(html: str, attr_name: str) -> str:
    match = re.search(rf'{re.escape(attr_name)}="([^"]*)"', html, flags=re.I)
    return unescape(match.group(1)).strip() if match else ""


def _appid_from_href(href: str) -> str:
    match = re.search(r"/app/(\d+)", str(href or ""))
    return match.group(1) if match else ""


def _clean_store_url(href: str, appid: str) -> str:
    if appid:
        return f"https://store.steampowered.com/app/{appid}/"
    return str(href or "").split("?")[0]


def _text_from_class(html: str, class_name: str) -> str:
    match = re.search(
        rf'<[^>]+class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>(.*?)</[^>]+>',
        html,
        flags=re.S | re.I,
    )
    return _html_to_text(match.group(1)) if match else ""


def _review_summary(html: str) -> str:
    match = re.search(r'<span[^>]+class="[^"]*search_review_summary[^"]*"[^>]*data-tooltip-html="([^"]*)"', html, flags=re.S | re.I)
    if match:
        return _html_to_text(match.group(1))
    return _text_from_class(html, "search_review_summary")


def _search_tags(html: str) -> str:
    tags = []
    for raw in re.findall(r'<span[^>]+class="[^"]*top_tag[^"]*"[^>]*>(.*?)</span>', html, flags=re.S | re.I):
        tag = _html_to_text(raw)
        if tag and tag not in tags:
            tags.append(tag)
    return ", ".join(tags)


def _html_to_text(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(unescape(str(value or "")))
    return re.sub(r"\s+", " ", parser.text()).strip()


def _split_terms(value) -> list[str]:
    if isinstance(value, list):
        parts = value
    else:
        parts = re.split(r"[,，、;/\n\r]+", str(value or ""))
    output = []
    seen = set()
    for part in parts:
        clean = str(part).strip()
        marker = clean.casefold()
        if clean and marker not in seen:
            seen.add(marker)
            output.append(clean)
    return output


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


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


def _keywords_from_description(description: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z -]{2,24}", description)
    stop = {"the", "and", "with", "you", "your", "game", "from", "into", "this", "that"}
    output = []
    for word in words:
        clean = " ".join(word.split()).strip(" -")
        if clean.casefold() in stop or len(clean) < 4:
            continue
        if clean.casefold() not in {item.casefold() for item in output}:
            output.append(clean)
    return output
