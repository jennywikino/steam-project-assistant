import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import pandas as pd


SEARCH_CENTER_SECTION_ORDER = [
    "Steam / 商业竞品搜索",
    "国内社区与资讯搜索",
    "海外社区与社媒搜索",
    "港澳台社区搜索",
    "站内搜索兜底",
]


BATCH_CATEGORY_OPTIONS = {
    "Steam/商业": ["Steam / 商业竞品搜索"],
    "国内声量": ["国内社区与资讯搜索"],
    "海外声量": ["海外社区与社媒搜索"],
    "港澳台": ["港澳台社区搜索"],
    "站内搜索兜底": ["站内搜索兜底"],
}


REGION_LABELS = {
    "mainland_cn": "国内",
    "hk_tw": "港澳台",
    "global": "海外/全球",
    "japan": "日本",
    "korea": "韩国",
    "other": "其他",
}


ENGINE_LABELS = {
    "native": "原生",
    "baidu": "百度",
    "google": "Google",
}


SEARCH_NAVIGATION_COLUMNS = [
    "打开",
    "分区",
    "平台名",
    "区域",
    "搜索词",
    "搜索意图",
    "搜索类型",
    "推荐搜索",
    "备用搜索",
    "推荐链接",
    "备用链接",
    "说明",
]


EXAMPLE_INPUT = {
    "game_name": "We Need An Army",
    "steam_url": "https://store.steampowered.com/app/3671320/We_Need_An_Army/",
    "short_description": (
        "tactical slots based roguelike battler, collect units, relics, mini games, army builder"
    ),
    "tags": "Roguelike, Strategy, Pixel Graphics, Auto Battler",
    "core_keywords": "slots based roguelike, grid tactics, army builder, roguelike battler",
    "theme_keywords": "",
    "english_keywords": "tactical roguelike, auto battler, pixel strategy",
    "reference_games": "Luck be a Landlord, Peglin, Backpack Hero",
    "developer": "",
    "publisher": "",
}


@dataclass
class SearchCenterInput:
    game_name: str
    steam_url: str = ""
    short_description: str = ""
    tags: str = ""
    core_keywords: str = ""
    theme_keywords: str = ""
    english_keywords: str = ""
    reference_games: str = ""
    developer: str = ""
    publisher: str = ""


def split_terms(raw_text: str) -> list[str]:
    """Split comma-separated user input into unique non-empty terms."""
    terms = []
    seen = set()
    for part in str(raw_text).replace("，", ",").split(","):
        term = part.strip()
        normalized = term.casefold()
        if not term or normalized in seen:
            continue
        seen.add(normalized)
        terms.append(term)
    return terms


def generate_keyword_items(search_input: SearchCenterInput, limit: int = 20) -> list[dict]:
    """Generate deduplicated keyword records."""
    game_name = search_input.game_name.strip()
    items = []

    def add(keyword: str, intent: str) -> None:
        clean_keyword = " ".join(str(keyword).split())
        if not clean_keyword:
            return
        normalized = clean_keyword.casefold()
        if normalized in {item["normalized"] for item in items}:
            return
        items.append({"关键词": clean_keyword, "搜索意图": intent, "normalized": normalized})

    if game_name:
        add(game_name, "商业竞品")
        add(f"{game_name} Steam", "商业竞品")
        add(f"{game_name} demo", "声量核查")
        add(f"{game_name} review", "声量核查")
        add(f"{game_name} gameplay", "声量核查")
        add(f"{game_name} trailer", "声量核查")
        add(f"{game_name} 中文评测", "声量核查")
        add(f"{game_name} 攻略", "声量核查")
        add(f"{game_name} 试玩", "声量核查")
        add(f"{game_name} 实况", "声量核查")
        add(f"{game_name} 愿望单", "声量核查")
        add(f"{game_name} publisher", "发行商核查")
        add(f"{game_name} presskit", "发行商核查")

    if search_input.developer.strip():
        add(search_input.developer.strip(), "开发商核查")
    if search_input.publisher.strip():
        add(search_input.publisher.strip(), "发行商核查")

    for keyword in split_terms(search_input.tags):
        add(keyword, "题材竞品")
    for keyword in split_terms(search_input.core_keywords):
        add(keyword, "玩法竞品")
    for keyword in split_terms(search_input.theme_keywords):
        add(keyword, "题材竞品")
    for keyword in split_terms(search_input.english_keywords):
        add(keyword, "玩法竞品")
    for keyword in split_terms(search_input.short_description):
        add(keyword, "玩法竞品")

    for reference_game in split_terms(search_input.reference_games):
        add(f"{reference_game} similar games", "玩法竞品")
        add(f"{reference_game} like", "玩法竞品")
        add(f"{reference_game} roguelike", "玩法竞品")

    return [{key: value for key, value in item.items() if key != "normalized"} for item in items[:limit]]


def generate_nga_keyword_items(search_input: SearchCenterInput) -> list[dict]:
    """Generate the narrower NGA keyword set requested for forum checks."""
    game_name = search_input.game_name.strip()
    developer = search_input.developer.strip()
    keywords = []

    def add(keyword: str, intent: str) -> None:
        clean_keyword = " ".join(str(keyword).split())
        if not clean_keyword:
            return
        normalized = clean_keyword.casefold()
        if normalized in {item["normalized"] for item in keywords}:
            return
        keywords.append({"关键词": clean_keyword, "搜索意图": intent, "normalized": normalized})

    if game_name:
        add(game_name, "声量核查")
        add(f"{game_name} 试玩", "声量核查")
        add(f"{game_name} 评测", "声量核查")
        add(f"{game_name} 攻略", "声量核查")
        add(f"{game_name} steam", "声量核查")
        add(f"{game_name} demo", "声量核查")
    if developer:
        add(developer, "开发商核查")

    return [{key: value for key, value in item.items() if key != "normalized"} for item in keywords]


def load_search_platforms(config_path: Path) -> list[dict]:
    """Load enabled platform definitions."""
    with config_path.open("r", encoding="utf-8") as file:
        platforms = json.load(file)
    return [platform for platform in platforms if platform.get("enabled", False)]


def build_engine_url(platform: dict, keyword: str, engine: str) -> str:
    """Build a native or search-engine site-search URL."""
    encoded_keyword = quote(keyword, safe="")
    if engine == "native":
        template = str(platform.get("url_template") or "")
        return template.format(query=encoded_keyword) if template else ""

    site_domain = str(platform.get("site_domain", "")).strip()
    if engine == "baidu":
        query = f"site:{site_domain} {keyword}" if site_domain else keyword
        return f"https://www.baidu.com/s?wd={quote(query, safe='')}"
    if engine == "google":
        query = f"site:{site_domain} {keyword}" if site_domain else keyword
        return f"https://www.google.com/search?q={quote(query, safe='')}"
    return ""


def build_engine_links(platform: dict, keyword: str, engines: list[str]) -> list[dict]:
    """Build deduplicated engine link records for one platform keyword row."""
    links = []
    seen = set()
    for engine in engines:
        if engine in seen:
            continue
        seen.add(engine)
        url = build_engine_url(platform, keyword, engine)
        if not url:
            continue
        links.append(
            {
                "engine": engine,
                "label": ENGINE_LABELS.get(engine, engine),
                "url": url,
            }
        )
    return links


def build_search_type_label(platform: dict) -> str:
    """Convert platform strategy to a compact user-facing search type."""
    search_type = platform.get("search_type", "")
    site_domain = str(platform.get("site_domain", "")).strip()
    if search_type == "native":
        return "原生搜索"
    if search_type == "manual":
        return "手动平台"
    if site_domain:
        return "站内搜索"
    return "搜索引擎"


def serialize_links_for_csv(links: list[dict]) -> str:
    """Flatten link records for CSV export."""
    return " | ".join(f"{link['label']}: {link['url']}" for link in links)


def build_platform_navigation(
    search_input: SearchCenterInput,
    platforms: list[dict],
    limit: int = 20,
) -> pd.DataFrame:
    """Build merged platform+keyword navigation rows without crawling any site."""
    rows = []
    default_keyword_items = generate_keyword_items(search_input, limit=limit)
    for platform in platforms:
        keyword_items = (
            generate_nga_keyword_items(search_input)
            if platform.get("keyword_profile") == "nga"
            else default_keyword_items
        )
        preferred_engines = list(platform.get("preferred_engines") or [])
        fallback_engines = list(platform.get("fallback_engines") or [])
        for item in keyword_items:
            keyword = item["关键词"]
            recommended_links = build_engine_links(platform, keyword, preferred_engines)
            fallback_links = build_engine_links(platform, keyword, fallback_engines)
            rows.append(
                {
                    "打开": False,
                    "分区": platform.get("category", ""),
                    "平台名": platform.get("platform_name_cn", ""),
                    "区域": REGION_LABELS.get(platform.get("region", ""), platform.get("region", "")),
                    "搜索词": keyword,
                    "搜索意图": item.get("搜索意图", ""),
                    "搜索类型": build_search_type_label(platform),
                    "推荐搜索": ", ".join(link["label"] for link in recommended_links),
                    "备用搜索": ", ".join(link["label"] for link in fallback_links),
                    "推荐链接": recommended_links,
                    "备用链接": fallback_links,
                    "说明": platform.get("note", ""),
                }
            )
    return pd.DataFrame(rows, columns=SEARCH_NAVIGATION_COLUMNS)


def filter_navigation_by_batch_groups(navigation: pd.DataFrame, selected_groups: list[str]) -> pd.DataFrame:
    """Filter navigation rows by batch-open group labels."""
    categories = []
    for group in selected_groups:
        categories.extend(BATCH_CATEGORY_OPTIONS.get(group, []))
    if not categories:
        return navigation.iloc[0:0].copy()
    return navigation.loc[navigation["分区"].isin(categories)].copy()


def expand_links_for_display(navigation: pd.DataFrame, include_fallback: bool = True) -> pd.DataFrame:
    """Expand merged link columns into a flat table for URL inspection and export."""
    rows = []
    for _, row in navigation.iterrows():
        link_groups = [("推荐搜索", row.get("推荐链接", []))]
        if include_fallback:
            link_groups.append(("备用搜索", row.get("备用链接", [])))
        for group_name, links in link_groups:
            if not isinstance(links, list):
                continue
            for link in links:
                rows.append(
                    {
                        "分区": row.get("分区", ""),
                        "平台名": row.get("平台名", ""),
                        "区域": row.get("区域", ""),
                        "搜索词": row.get("搜索词", ""),
                        "搜索类型": row.get("搜索类型", ""),
                        "链接组": group_name,
                        "搜索引擎": link.get("label", ""),
                        "链接": link.get("url", ""),
                        "说明": row.get("说明", ""),
                    }
                )
    return pd.DataFrame(rows)


def prepare_navigation_for_csv(navigation: pd.DataFrame) -> pd.DataFrame:
    """Convert object link columns to text before CSV export."""
    output = navigation.copy()
    output["推荐链接"] = output["推荐链接"].apply(
        lambda links: serialize_links_for_csv(links) if isinstance(links, list) else ""
    )
    output["备用链接"] = output["备用链接"].apply(
        lambda links: serialize_links_for_csv(links) if isinstance(links, list) else ""
    )
    return output
