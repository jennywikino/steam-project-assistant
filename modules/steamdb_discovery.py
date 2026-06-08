from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
import re
from uuid import uuid4

import pandas as pd


TEMPLATE_COLUMNS = [
    "record_id",
    "created_at",
    "template_name",
    "category",
    "steamdb_url",
    "note",
    "is_favorite",
]

WATCH_NOTE_COLUMNS = [
    "record_id",
    "created_at",
    "source_page",
    "source_url",
    "game_name",
    "appid",
    "steam_url",
    "steamdb_url",
    "rank_text",
    "release_date",
    "followers",
    "reviews",
    "rating",
    "peak_players",
    "price",
    "note",
    "next_action",
]

TEMPLATE_FIELD_LABELS = {
    "record_id": "记录 ID",
    "created_at": "创建时间",
    "template_name": "模板名称",
    "category": "分类",
    "steamdb_url": "SteamDB 链接",
    "note": "备注",
    "is_favorite": "收藏",
}

WATCH_NOTE_FIELD_LABELS = {
    "record_id": "记录 ID",
    "created_at": "创建时间",
    "source_page": "来源页面",
    "source_url": "来源链接",
    "game_name": "游戏名",
    "appid": "AppID",
    "steam_url": "Steam 链接",
    "steamdb_url": "SteamDB 链接",
    "rank_text": "排名/位置",
    "release_date": "发售日期",
    "followers": "Followers",
    "reviews": "Reviews",
    "rating": "Rating",
    "peak_players": "Peak",
    "price": "价格",
    "note": "备注",
    "next_action": "下一步动作",
}

PRESET_STEAMDB_TEMPLATES = [
    {
        "template_name": "2026 新作高评分观察",
        "category": "新作发现",
        "steamdb_url": "https://steamdb.info/stats/gameratings/2026/",
        "note": "Top Rated Steam Releases 2026",
        "is_favorite": "True",
    },
    {
        "template_name": "2027 新作高评分观察",
        "category": "新作发现",
        "steamdb_url": "https://steamdb.info/stats/gameratings/2027/",
        "note": "Top Rated Steam Releases 2027",
        "is_favorite": "True",
    },
    {
        "template_name": "即将发售观察",
        "category": "新作发现",
        "steamdb_url": "https://steamdb.info/upcoming/",
        "note": "Upcoming Releases",
        "is_favorite": "True",
    },
    {
        "template_name": "发售日历",
        "category": "新作发现",
        "steamdb_url": "https://steamdb.info/calendar/",
        "note": "Release Calendar",
        "is_favorite": "True",
    },
    {
        "template_name": "Followers 增长榜",
        "category": "热度观察",
        "steamdb_url": "https://steamdb.info/stats/trendingfollowers/",
        "note": "Trending Followers",
        "is_favorite": "True",
    },
    {
        "template_name": "Wishlist Activity",
        "category": "热度观察",
        "steamdb_url": "https://steamdb.info/stats/wishlistactivity/",
        "note": "Upcoming wishlist movement",
        "is_favorite": "True",
    },
    {
        "template_name": "Most Wishlisted",
        "category": "热度观察",
        "steamdb_url": "https://steamdb.info/stats/mostwished/",
        "note": "Most wishlisted upcoming games",
        "is_favorite": "True",
    },
    {
        "template_name": "实时在线榜",
        "category": "热度观察",
        "steamdb_url": "https://steamdb.info/charts/",
        "note": "Live Player Charts",
        "is_favorite": "True",
    },
]


@dataclass
class SteamDBTemplate:
    template_name: str = ""
    category: str = ""
    steamdb_url: str = ""
    note: str = ""
    is_favorite: str = "False"
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class SteamDBWatchNote:
    source_page: str = ""
    source_url: str = ""
    game_name: str = ""
    appid: str = ""
    steam_url: str = ""
    steamdb_url: str = ""
    rank_text: str = ""
    release_date: str = ""
    followers: str = ""
    reviews: str = ""
    rating: str = ""
    peak_players: str = ""
    price: str = ""
    note: str = ""
    next_action: str = ""
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def parse_steamdb_appid(raw_input: str) -> str:
    """Parse a Steam AppID from plain digits, SteamDB app URLs, or Steam store URLs."""
    text = str(raw_input or "").strip()
    if not text:
        return ""
    if text.isdigit():
        return text

    steamdb_match = re.search(r"steamdb\.info/app/(\d+)", text, re.IGNORECASE)
    if steamdb_match:
        return steamdb_match.group(1)

    steam_match = re.search(r"store\.steampowered\.com/app/(\d+)", text, re.IGNORECASE)
    if steam_match:
        return steam_match.group(1)

    loose_match = re.search(r"\b(\d{3,10})\b", text)
    return loose_match.group(1) if loose_match else ""


def steam_url_from_appid(appid: str) -> str:
    appid = str(appid or "").strip()
    return f"https://store.steampowered.com/app/{appid}/" if appid else ""


def steamdb_app_url_from_appid(appid: str) -> str:
    appid = str(appid or "").strip()
    return f"https://steamdb.info/app/{appid}/" if appid else ""


def steamdb_quick_links(appid: str) -> list[tuple[str, str]]:
    appid = str(appid or "").strip()
    if not appid:
        return []
    base = f"https://steamdb.info/app/{appid}"
    return [
        ("Steam 商店页", steam_url_from_appid(appid)),
        ("SteamDB App 页", f"{base}/"),
        ("SteamDB Charts", f"{base}/charts/"),
        ("SteamDB History", f"{base}/history/"),
        ("SteamDB Depots", f"{base}/depots/"),
        ("SteamDB Subs / Packages", f"{base}/subs/"),
        ("SteamDB Patchnotes", f"{base}/patchnotes/"),
    ]


def ensure_template_csv_exists(csv_path: Path) -> None:
    _ensure_csv(csv_path, TEMPLATE_COLUMNS)
    templates = load_templates(csv_path)
    if templates.empty:
        preset_rows = []
        for preset in PRESET_STEAMDB_TEMPLATES:
            preset_rows.append(_template_to_dict(SteamDBTemplate(**preset)))
        pd.DataFrame(preset_rows, columns=TEMPLATE_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    existing_urls = set(templates["steamdb_url"].astype(str).str.strip())
    missing_rows = []
    for preset in PRESET_STEAMDB_TEMPLATES:
        if preset["steamdb_url"] not in existing_urls:
            missing_rows.append(_template_to_dict(SteamDBTemplate(**preset)))
    if missing_rows:
        pd.DataFrame(missing_rows, columns=TEMPLATE_COLUMNS).to_csv(
            csv_path,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig",
        )


def ensure_watch_note_csv_exists(csv_path: Path) -> None:
    _ensure_csv(csv_path, WATCH_NOTE_COLUMNS)


def load_templates(csv_path: Path) -> pd.DataFrame:
    _ensure_csv(csv_path, TEMPLATE_COLUMNS)
    return _read_csv(csv_path, TEMPLATE_COLUMNS)


def load_watch_notes(csv_path: Path) -> pd.DataFrame:
    _ensure_csv(csv_path, WATCH_NOTE_COLUMNS)
    return _read_csv(csv_path, WATCH_NOTE_COLUMNS)


def save_template_to_csv(template: SteamDBTemplate, csv_path: Path) -> Path:
    ensure_template_csv_exists(csv_path)
    row = pd.DataFrame([_template_to_dict(template)], columns=TEMPLATE_COLUMNS)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def save_watch_note_to_csv(note: SteamDBWatchNote, csv_path: Path) -> Path:
    ensure_watch_note_csv_exists(csv_path)
    row = pd.DataFrame([_watch_note_to_dict(note)], columns=WATCH_NOTE_COLUMNS)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def _ensure_csv(csv_path: Path, columns: list[str]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in columns:
        if column not in existing.columns:
            existing[column] = ""
            changed = True
    if "record_id" in existing.columns:
        missing_id = existing["record_id"].astype(str).str.strip() == ""
        if missing_id.any():
            existing.loc[missing_id, "record_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
            changed = True
    if changed:
        extra_columns = [column for column in existing.columns if column not in columns]
        existing.to_csv(csv_path, columns=columns + extra_columns, index=False, encoding="utf-8-sig")


def _read_csv(csv_path: Path, columns: list[str]) -> pd.DataFrame:
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=columns)
    for column in columns:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, columns].copy()


def _template_to_dict(template: SteamDBTemplate) -> dict:
    raw = asdict(template)
    return {column: raw.get(column, "") for column in TEMPLATE_COLUMNS}


def _watch_note_to_dict(note: SteamDBWatchNote) -> dict:
    raw = asdict(note)
    return {column: raw.get(column, "") for column in WATCH_NOTE_COLUMNS}
