import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pandas as pd


COMPETITOR_SEARCH_COLUMNS = [
    "created_at",
    "game_name",
    "steam_url",
    "关键词",
    "搜索意图",
    "Steam 搜索链接",
    "Google 链接",
    "百度链接",
    "Google Steam 链接",
    "IGDB 链接",
    "SteamDB 链接",
    "小黑盒站内搜索",
    "游民星空站内搜索",
    "游侠站内搜索",
    "人工备注",
    "是否已检查",
]


COMPETITOR_SEARCH_DISPLAY_COLUMNS = [
    "关键词",
    "搜索意图",
    "Steam 搜索链接",
    "Google 链接",
    "百度链接",
    "Google Steam 链接",
    "IGDB 链接",
    "SteamDB 链接",
    "小黑盒站内搜索",
    "游民星空站内搜索",
    "游侠站内搜索",
    "人工备注",
    "是否已检查",
]


PLATFORM_PRESENCE_COLUMNS = [
    "created_at",
    "game_name",
    "steam_url",
    "关键词",
    "百度链接",
    "YouTube 链接",
    "B站链接",
    "Reddit 链接",
    "itch 链接",
    "Google 链接",
    "Steam 搜索链接",
    "SteamDB 链接",
    "IGDB 链接",
    "小黑盒站内搜索",
    "游民星空站内搜索",
    "游侠站内搜索",
    "Top 结果标题",
    "播放量 / 浏览量 / 互动量",
    "是否官方内容",
    "是否媒体 / KOL 内容",
    "人工判断",
    "是否已检查",
]


PLATFORM_PRESENCE_DISPLAY_COLUMNS = [
    "关键词",
    "百度链接",
    "YouTube 链接",
    "B站链接",
    "Reddit 链接",
    "itch 链接",
    "Google 链接",
    "Steam 搜索链接",
    "SteamDB 链接",
    "IGDB 链接",
    "小黑盒站内搜索",
    "游民星空站内搜索",
    "游侠站内搜索",
    "Top 结果标题",
    "播放量 / 浏览量 / 互动量",
    "是否官方内容",
    "是否媒体 / KOL 内容",
    "人工判断",
    "是否已检查",
]


SEARCH_INTENT_OPTIONS = [
    "玩法竞品",
    "商业竞品",
    "题材竞品",
    "发行商核查",
    "开发商核查",
    "声量核查",
]


PRESENCE_JUDGMENT_OPTIONS = [
    "无声量",
    "弱声量",
    "有少量自然传播",
    "明显有传播",
    "异常数据",
]


DOMESTIC_LINK_LABELS = [
    "百度",
    "B站",
    "小黑盒",
    "游民星空",
    "游侠",
]


OVERSEAS_LINK_LABELS = [
    "Google",
    "Steam",
    "SteamDB",
    "YouTube",
    "Reddit",
    "itch",
    "IGDB",
]


LINK_LABEL_TO_COLUMN = {
    "Google": "Google 链接",
    "百度": "百度链接",
    "Steam": "Steam 搜索链接",
    "SteamDB": "SteamDB 链接",
    "YouTube": "YouTube 链接",
    "B站": "B站链接",
    "Reddit": "Reddit 链接",
    "itch": "itch 链接",
    "IGDB": "IGDB 链接",
    "小黑盒": "小黑盒站内搜索",
    "游民星空": "游民星空站内搜索",
    "游侠": "游侠站内搜索",
}


OPEN_LINK_DISPLAY_COLUMNS = [
    "打开",
    "分组",
    "平台",
    "关键词",
    "链接",
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


SEARCH_CENTER_SECTION_ORDER = [
    "Steam / 商业竞品搜索",
    "全平台声量搜索",
    "国内社区与资讯搜索",
    "海外社区与社媒搜索",
    "站内搜索兜底",
]


BATCH_CATEGORY_OPTIONS = {
    "Steam/商业": ["Steam / 商业竞品搜索"],
    "国内声量": ["全平台声量搜索", "国内社区与资讯搜索"],
    "海外声量": ["全平台声量搜索", "海外社区与社媒搜索"],
    "站内搜索兜底": ["站内搜索兜底"],
}


SEARCH_NAVIGATION_COLUMNS = [
    "打开",
    "分区",
    "平台名",
    "搜索词",
    "搜索类型",
    "按钮文案",
    "链接",
    "说明",
]


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
    """Generate deduplicated keyword records with default search intent."""
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

    for keyword in split_terms(search_input.core_keywords):
        add(keyword, "玩法竞品")

    for keyword in split_terms(search_input.theme_keywords):
        add(keyword, "题材竞品")

    for keyword in split_terms(search_input.english_keywords):
        add(keyword, "玩法竞品")

    for reference_game in split_terms(search_input.reference_games):
        add(f"{reference_game} similar games", "玩法竞品")
        add(f"{reference_game} like", "玩法竞品")
        add(f"{reference_game} roguelike", "玩法竞品")

    for tag in split_terms(search_input.tags):
        add(f"{tag} indie game", "题材竞品")
        add(f"{tag} Steam game", "商业竞品")

    if search_input.developer.strip():
        add(search_input.developer.strip(), "开发商核查")
    if search_input.publisher.strip():
        add(search_input.publisher.strip(), "发行商核查")

    return [{key: value for key, value in item.items() if key != "normalized"} for item in items[:limit]]


def load_search_platforms(config_path: Path) -> list[dict]:
    """读取搜索平台字典。"""
    with config_path.open("r", encoding="utf-8") as file:
        platforms = json.load(file)
    return [platform for platform in platforms if platform.get("enabled", False)]


def build_button_label(platform: dict) -> str:
    """按搜索类型生成不误导用户的按钮文案。"""
    platform_name = platform.get("platform_name_cn", "")
    search_type = platform.get("search_type", "")
    if search_type == "baidu_site":
        return f"百度站内搜：{platform_name}"
    if search_type == "google_site":
        return f"Google 站内搜：{platform_name}"
    if search_type == "manual":
        return f"手动检查：{platform_name}"
    return f"打开 {platform_name} 搜索"


def build_search_url(platform: dict, keyword: str) -> str:
    """根据平台模板生成 URL。"""
    template = str(platform.get("url_template", ""))
    if not template:
        return ""
    return template.format(query=quote(keyword, safe=""))


def build_platform_navigation(
    search_input: SearchCenterInput,
    platforms: list[dict],
    limit: int = 20,
) -> pd.DataFrame:
    """生成平台搜索导航行，不抓取任何平台内容。"""
    keyword_items = generate_keyword_items(search_input, limit=limit)
    rows = []
    for item in keyword_items:
        keyword = item["关键词"]
        for platform in platforms:
            rows.append(
                {
                    "打开": False,
                    "分区": platform.get("category", ""),
                    "平台名": platform.get("platform_name_cn", ""),
                    "搜索词": keyword,
                    "搜索类型": platform.get("search_type", ""),
                    "按钮文案": build_button_label(platform),
                    "链接": build_search_url(platform, keyword),
                    "说明": platform.get("note", ""),
                }
            )
    return pd.DataFrame(rows, columns=SEARCH_NAVIGATION_COLUMNS)


def filter_navigation_by_batch_groups(navigation: pd.DataFrame, selected_groups: list[str]) -> pd.DataFrame:
    """按批量打开分组筛选导航链接。"""
    categories = []
    for group in selected_groups:
        categories.extend(BATCH_CATEGORY_OPTIONS.get(group, []))
    if not categories:
        return navigation.iloc[0:0].copy()
    return navigation.loc[navigation["分区"].isin(categories)].copy()


def build_links(keyword: str) -> dict:
    """Build encoded search links for one keyword."""
    encoded_keyword = quote(keyword, safe="")
    return {
        "Steam 搜索链接": f"https://store.steampowered.com/search/?term={encoded_keyword}",
        "Google 链接": f"https://www.google.com/search?q={encoded_keyword}",
        "百度链接": f"https://www.baidu.com/s?wd={encoded_keyword}",
        "Google Steam 链接": (
            f"https://www.google.com/search?q=site%3Astore.steampowered.com+{encoded_keyword}"
        ),
        "Google YouTube 链接": f"https://www.google.com/search?q=site%3Ayoutube.com+{encoded_keyword}",
        "YouTube 链接": f"https://www.youtube.com/results?search_query={encoded_keyword}",
        "B站链接": f"https://search.bilibili.com/all?keyword={encoded_keyword}",
        "Reddit 链接": f"https://www.reddit.com/search/?q={encoded_keyword}",
        "itch 链接": f"https://itch.io/search?q={encoded_keyword}",
        "IGDB 链接": f"https://www.igdb.com/search?type=1&q={encoded_keyword}",
        "SteamDB 链接": f"https://steamdb.info/search/?a=app&q={encoded_keyword}",
        "小黑盒站内搜索": f"https://www.baidu.com/s?wd=site%3Awww.xiaoheihe.cn+{encoded_keyword}",
        "游民星空站内搜索": f"https://www.baidu.com/s?wd=site%3Agamersky.com+{encoded_keyword}",
        "游侠站内搜索": f"https://www.baidu.com/s?wd=site%3Aali213.net+{encoded_keyword}",
    }


def build_search_tables(search_input: SearchCenterInput, limit: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build editable search tables without crawling any platform."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    keyword_items = generate_keyword_items(search_input, limit=limit)

    competitor_rows = []
    presence_rows = []
    for item in keyword_items:
        keyword = item["关键词"]
        links = build_links(keyword)
        base = {
            "created_at": created_at,
            "game_name": search_input.game_name.strip(),
            "steam_url": search_input.steam_url.strip(),
            "关键词": keyword,
        }
        competitor_rows.append(
            {
                **base,
                "搜索意图": item["搜索意图"],
                "Steam 搜索链接": links["Steam 搜索链接"],
                "Google 链接": links["Google 链接"],
                "百度链接": links["百度链接"],
                "Google Steam 链接": links["Google Steam 链接"],
                "IGDB 链接": links["IGDB 链接"],
                "SteamDB 链接": links["SteamDB 链接"],
                "小黑盒站内搜索": links["小黑盒站内搜索"],
                "游民星空站内搜索": links["游民星空站内搜索"],
                "游侠站内搜索": links["游侠站内搜索"],
                "人工备注": "",
                "是否已检查": False,
            }
        )
        presence_rows.append(
            {
                **base,
                "百度链接": links["百度链接"],
                "YouTube 链接": links["YouTube 链接"],
                "B站链接": links["B站链接"],
                "Reddit 链接": links["Reddit 链接"],
                "itch 链接": links["itch 链接"],
                "Google 链接": links["Google 链接"],
                "Steam 搜索链接": links["Steam 搜索链接"],
                "SteamDB 链接": links["SteamDB 链接"],
                "IGDB 链接": links["IGDB 链接"],
                "小黑盒站内搜索": links["小黑盒站内搜索"],
                "游民星空站内搜索": links["游民星空站内搜索"],
                "游侠站内搜索": links["游侠站内搜索"],
                "Top 结果标题": "",
                "播放量 / 浏览量 / 互动量": "",
                "是否官方内容": False,
                "是否媒体 / KOL 内容": False,
                "人工判断": "弱声量",
                "是否已检查": False,
            }
        )

    return pd.DataFrame(competitor_rows), pd.DataFrame(presence_rows)


def build_open_link_table(keywords: list[str]) -> pd.DataFrame:
    """Build one selectable row for each keyword/platform link."""
    rows = []
    for keyword in keywords:
        links = build_links(keyword)
        for label in DOMESTIC_LINK_LABELS:
            rows.append(
                {
                    "打开": False,
                    "分组": "国内搜索优先",
                    "平台": label,
                    "关键词": keyword,
                    "链接": links[LINK_LABEL_TO_COLUMN[label]],
                }
            )
        for label in OVERSEAS_LINK_LABELS:
            rows.append(
                {
                    "打开": False,
                    "分组": "海外搜索优先",
                    "平台": label,
                    "关键词": keyword,
                    "链接": links[LINK_LABEL_TO_COLUMN[label]],
                }
            )
    return pd.DataFrame(rows)


def save_search_tables(
    competitor_table: pd.DataFrame,
    presence_table: pd.DataFrame,
    export_dir: Path,
) -> tuple[Path, Path]:
    """Append generated search center tables to UTF-8-SIG CSV exports."""
    export_dir.mkdir(parents=True, exist_ok=True)
    competitor_path = export_dir / "competitor_search_links.csv"
    presence_path = export_dir / "platform_presence_search_links.csv"

    _append_csv(competitor_table, competitor_path, COMPETITOR_SEARCH_COLUMNS)
    _append_csv(presence_table, presence_path, PLATFORM_PRESENCE_COLUMNS)
    return competitor_path, presence_path


def _append_csv(data: pd.DataFrame, csv_path: Path, columns: list[str]) -> None:
    """Append a table with stable columns to a UTF-8-SIG CSV."""
    if csv_path.exists():
        try:
            existing_data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        except pd.errors.EmptyDataError:
            existing_data = pd.DataFrame(columns=columns)
        changed = False
        for column in columns:
            if column not in existing_data.columns:
                existing_data[column] = ""
                changed = True
        if changed:
            extra_columns = [column for column in existing_data.columns if column not in columns]
            existing_data.to_csv(
                csv_path,
                columns=columns + extra_columns,
                index=False,
                encoding="utf-8-sig",
            )

    output = data.copy()
    for column in columns:
        if column not in output.columns:
            output[column] = ""
    output = output.loc[:, columns]
    output.to_csv(
        csv_path,
        mode="a",
        header=not csv_path.exists(),
        index=False,
        encoding="utf-8-sig",
    )
