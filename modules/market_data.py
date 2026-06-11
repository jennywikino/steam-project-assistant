from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import pandas as pd


MARKET_DATA_COLUMNS = [
    "market_data_id",
    "created_at",
    "updated_at",
    "appid",
    "game_name",
    "source",
    "source_url",
    "data_date",
    "reviews",
    "review_score",
    "followers",
    "wishlists",
    "wishlist_activity_rank",
    "current_players",
    "peak_24h",
    "avg_daily_ccu",
    "all_time_peak",
    "estimated_owners_low",
    "estimated_owners_mid",
    "estimated_owners_high",
    "estimated_sales",
    "estimated_downloads",
    "estimated_gross_revenue",
    "avg_playtime_hours",
    "median_playtime_hours",
    "country_top1",
    "country_top1_share",
    "country_top2",
    "country_top2_share",
    "country_top3",
    "country_top3_share",
    "notes",
    "confidence",
    "is_estimated",
]

MARKET_SOURCE_OPTIONS = ["VGI", "Gamalytic", "SteamDB", "SteamSpy", "Steam官方", "手动估算", "其他"]
MARKET_CONFIDENCE_OPTIONS = ["高", "中", "低", "未确认"]
MARKET_ESTIMATED_OPTIONS = ["True", "False"]

MARKET_DATA_FIELD_LABELS = {
    "source": "来源",
    "source_url": "来源链接",
    "data_date": "日期",
    "reviews": "reviews",
    "review_score": "review score",
    "followers": "followers",
    "current_players": "current players",
    "avg_daily_ccu": "avg daily CCU",
    "estimated_combo": "estimated owners / sales / downloads",
    "estimated_gross_revenue": "gross revenue",
    "avg_playtime_hours": "avg playtime",
    "median_playtime_hours": "median playtime",
    "confidence": "confidence",
}

MARKET_SUMMARY_FIELDS = [
    "reviews",
    "review_score",
    "followers",
    "current_players",
    "peak_24h",
    "estimated_sales",
    "estimated_downloads",
    "estimated_gross_revenue",
    "avg_playtime_hours",
    "median_playtime_hours",
]


@dataclass
class MarketDataRecord:
    appid: str = ""
    game_name: str = ""
    source: str = "其他"
    source_url: str = ""
    data_date: str = ""
    reviews: str = ""
    review_score: str = ""
    followers: str = ""
    wishlists: str = ""
    wishlist_activity_rank: str = ""
    current_players: str = ""
    peak_24h: str = ""
    avg_daily_ccu: str = ""
    all_time_peak: str = ""
    estimated_owners_low: str = ""
    estimated_owners_mid: str = ""
    estimated_owners_high: str = ""
    estimated_sales: str = ""
    estimated_downloads: str = ""
    estimated_gross_revenue: str = ""
    avg_playtime_hours: str = ""
    median_playtime_hours: str = ""
    country_top1: str = ""
    country_top1_share: str = ""
    country_top2: str = ""
    country_top2_share: str = ""
    country_top3: str = ""
    country_top3_share: str = ""
    notes: str = ""
    confidence: str = "未确认"
    is_estimated: str = "True"
    market_data_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_market_data_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=MARKET_DATA_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=MARKET_DATA_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in MARKET_DATA_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    missing_id = existing["market_data_id"].astype(str).str.strip() == ""
    if missing_id.any():
        existing.loc[missing_id, "market_data_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
        changed = True
    for time_column in ["created_at", "updated_at"]:
        missing_time = existing[time_column].astype(str).str.strip() == ""
        if missing_time.any():
            existing.loc[missing_time, time_column] = now
            changed = True

    normalized = _normalize_market_data_frame(existing)
    if not normalized.equals(existing.loc[:, normalized.columns]):
        existing = normalized
        changed = True

    if changed:
        extra_columns = [column for column in existing.columns if column not in MARKET_DATA_COLUMNS]
        existing.to_csv(csv_path, columns=MARKET_DATA_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_market_data(csv_path: Path) -> pd.DataFrame:
    ensure_market_data_csv_exists(csv_path)
    try:
        records = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        records = pd.DataFrame(columns=MARKET_DATA_COLUMNS)
    return _normalize_market_data_frame(records)


def save_market_data_to_csv(record: MarketDataRecord, csv_path: Path) -> Path:
    ensure_market_data_csv_exists(csv_path)
    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    record_data = sanitize_market_data_record(market_data_to_dict(record))
    row = pd.DataFrame([{column: record_data.get(column, "") for column in existing_columns}], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def delete_market_data_records(csv_path: Path, market_data_ids: list[str]) -> int:
    records = load_market_data(csv_path)
    clean_ids = {str(record_id or "").strip() for record_id in market_data_ids if str(record_id or "").strip()}
    if not clean_ids:
        return 0
    before_count = len(records)
    records = records.loc[~records["market_data_id"].astype(str).str.strip().isin(clean_ids)].copy()
    records.to_csv(csv_path, columns=MARKET_DATA_COLUMNS, index=False, encoding="utf-8-sig")
    return before_count - len(records)


def market_data_to_dict(record: MarketDataRecord) -> dict:
    raw = asdict(record)
    return {column: raw.get(column, "") for column in MARKET_DATA_COLUMNS}


def sanitize_market_data_record(record: dict) -> dict:
    clean = {}
    for column in MARKET_DATA_COLUMNS:
        clean[column] = _clean_text(record.get(column, ""))
    if not clean["market_data_id"]:
        clean["market_data_id"] = str(uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not clean["created_at"]:
        clean["created_at"] = now
    if not clean["updated_at"]:
        clean["updated_at"] = clean["created_at"] or now
    if clean["source"] not in MARKET_SOURCE_OPTIONS:
        clean["source"] = clean["source"] or "其他"
    if clean["confidence"] not in MARKET_CONFIDENCE_OPTIONS:
        clean["confidence"] = "未确认"
    if clean["is_estimated"] not in MARKET_ESTIMATED_OPTIONS:
        clean["is_estimated"] = "True" if str(clean["is_estimated"]).casefold() in {"1", "yes", "y", "true", "是"} else "False"
    return clean


def filter_market_data(records: pd.DataFrame, appid: str = "", game_name: str = "") -> pd.DataFrame:
    records = _ensure_market_columns(records)
    clean_appid = str(appid or "").strip()
    clean_name = _normalize_lookup_text(game_name)
    if clean_appid:
        return sort_market_data(records.loc[records["appid"].astype(str).str.strip().eq(clean_appid)])
    if not clean_name:
        return records.iloc[0:0].loc[:, MARKET_DATA_COLUMNS].copy()
    names = records["game_name"].astype(str).map(_normalize_lookup_text)
    mask = names.eq(clean_name) | names.str.contains(clean_name, regex=False, na=False)
    return sort_market_data(records.loc[mask])


def find_market_data_duplicate_note(records: pd.DataFrame, record: MarketDataRecord) -> str:
    records = _ensure_market_columns(records)
    if records.empty:
        return ""
    appid = str(record.appid or "").strip()
    source = str(record.source or "").strip()
    data_date = str(record.data_date or "").strip()
    if not appid or not source or not data_date:
        return ""
    mask = (
        records["appid"].astype(str).str.strip().eq(appid)
        & records["source"].astype(str).str.strip().eq(source)
        & records["data_date"].astype(str).str.strip().eq(data_date)
    )
    if mask.any():
        return "疑似重复：已有相同 AppID + 来源 + 数据日期的市场数据记录。"
    return ""


def summarize_market_data(records: pd.DataFrame) -> dict:
    records = sort_market_data(records)
    if records.empty:
        return {
            "record_count": 0,
            "source_count": 0,
            "sources": [],
            "latest_record": {},
            "latest_date": "",
            "conflict_note": "",
            "is_estimated": False,
        }
    latest = records.iloc[0].to_dict()
    sources = [source for source in records["source"].astype(str).str.strip().drop_duplicates().tolist() if source]
    conflict_fields = []
    for column in MARKET_SUMMARY_FIELDS:
        values = {str(value or "").strip() for value in records[column].tolist() if str(value or "").strip()}
        if len(values) > 1:
            conflict_fields.append(column)
    is_estimated = records["is_estimated"].astype(str).str.strip().str.casefold().isin({"true", "1", "yes", "y"}).any()
    return {
        "record_count": int(len(records)),
        "source_count": len(sources),
        "sources": sources,
        "latest_record": latest,
        "latest_date": latest.get("data_date", "") or latest.get("updated_at", ""),
        "conflict_note": "多来源存在差异" if conflict_fields else "",
        "is_estimated": bool(is_estimated),
    }


def build_market_data_markdown_section(records: pd.DataFrame | None = None) -> str:
    records = _ensure_market_columns(records)
    if records.empty:
        return (
            "## 第三方市场数据\n\n"
            "暂无第三方市场数据记录。\n\n"
            "- 数据限制：第三方销量、收入、下载量为估算值，不等同于官方后台数据。\n"
        )

    summary = summarize_market_data(records)
    latest = summary["latest_record"]
    estimated_sales_downloads = _join_non_empty(
        [
            _estimated_label(latest.get("estimated_sales"), latest.get("is_estimated")),
            _estimated_label(latest.get("estimated_downloads"), latest.get("is_estimated")),
        ]
    )
    countries = format_country_distribution(latest)
    lines = [
        "## 第三方市场数据",
        "",
        f"- 数据来源：{_display(' / '.join(summary['sources']))}",
        f"- 最新记录：{_display(summary['latest_date'])}",
        f"- 评测数：{_display(latest.get('reviews'))}",
        f"- 好评率：{_display(latest.get('review_score'))}",
        f"- Followers：{_display(latest.get('followers'))}",
        f"- 当前在线：{_display(latest.get('current_players'))}",
        f"- 24h Peak：{_display(latest.get('peak_24h'))}",
        f"- 估算销量 / 下载：{_display(estimated_sales_downloads)}",
        f"- 估算收入：{_display(_estimated_label(latest.get('estimated_gross_revenue'), latest.get('is_estimated')))}",
        f"- 平均游玩：{_display(latest.get('avg_playtime_hours'))}",
        f"- 中位游玩：{_display(latest.get('median_playtime_hours'))}",
        f"- 地区分布：{_display(countries)}",
    ]
    if summary["conflict_note"]:
        lines.append(f"- 多来源提示：{summary['conflict_note']}")
    lines.append("- 数据限制：第三方销量、收入、下载量为估算值，不等同于官方后台数据。")
    lines.append("")
    return "\n".join(lines)


def build_market_data_external_links(appid: str, game_name: str = "") -> list[tuple[str, str]]:
    clean_appid = str(appid or "").strip()
    clean_name = str(game_name or "").strip()
    query = quote(clean_name or clean_appid or "Steam game")
    links = []
    if clean_appid:
        links.extend(
            [
                ("打开 SteamDB", f"https://steamdb.info/app/{quote(clean_appid)}/"),
                ("打开 SteamSpy", f"https://steamspy.com/app/{quote(clean_appid)}"),
                ("打开 Steam 官方页", f"https://store.steampowered.com/app/{quote(clean_appid)}/"),
            ]
        )
    else:
        links.extend(
            [
                ("打开 SteamDB", "https://steamdb.info/"),
                ("打开 SteamSpy", "https://steamspy.com/"),
                ("打开 Steam 官方页", f"https://store.steampowered.com/search/?term={query}"),
            ]
        )
    links.extend(
        [
            ("打开 Gamalytic 首页", "https://gamalytic.com/"),
            ("打开 VGI 首页", "https://app.sensortower.com/vgi"),
        ]
    )
    return links


def sort_market_data(records: pd.DataFrame) -> pd.DataFrame:
    records = _ensure_market_columns(records)
    if records.empty:
        return records
    output = records.copy()
    output["_data_date_sort"] = pd.to_datetime(output["data_date"], errors="coerce")
    output["_updated_at_sort"] = pd.to_datetime(output["updated_at"], errors="coerce")
    output = output.sort_values(
        by=["_data_date_sort", "_updated_at_sort", "data_date", "updated_at"],
        ascending=[False, False, False, False],
        na_position="last",
    )
    return output.drop(columns=["_data_date_sort", "_updated_at_sort"]).loc[:, MARKET_DATA_COLUMNS].copy()


def latest_market_data_date(records: pd.DataFrame) -> str:
    records = sort_market_data(records)
    if records.empty:
        return ""
    row = records.iloc[0]
    return str(row.get("data_date", "") or row.get("updated_at", "") or "").strip()


def format_country_distribution(row: dict) -> str:
    countries = []
    for index in [1, 2, 3]:
        country = str(row.get(f"country_top{index}", "") or "").strip()
        share = str(row.get(f"country_top{index}_share", "") or "").strip()
        if country:
            countries.append(f"{country} {share}".strip())
    return " / ".join(countries)


def _normalize_market_data_frame(records: pd.DataFrame) -> pd.DataFrame:
    output = records.copy() if records is not None else pd.DataFrame(columns=MARKET_DATA_COLUMNS)
    for column in MARKET_DATA_COLUMNS:
        if column not in output.columns:
            output[column] = ""
        output[column] = output[column].astype(str).map(_clean_text)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    missing_id = output["market_data_id"].astype(str).str.strip() == ""
    if missing_id.any():
        output.loc[missing_id, "market_data_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
    missing_created_at = output["created_at"].astype(str).str.strip() == ""
    if missing_created_at.any():
        output.loc[missing_created_at, "created_at"] = now
    missing_updated_at = output["updated_at"].astype(str).str.strip() == ""
    if missing_updated_at.any():
        output.loc[missing_updated_at, "updated_at"] = output.loc[missing_updated_at, "created_at"]

    output["source"] = output["source"].map(lambda value: value if value in MARKET_SOURCE_OPTIONS else "其他")
    output["confidence"] = output["confidence"].map(lambda value: value if value in MARKET_CONFIDENCE_OPTIONS else "未确认")
    output["is_estimated"] = output["is_estimated"].map(lambda value: "True" if str(value).casefold() in {"true", "1", "yes", "y", "是"} else "False")
    return output.loc[:, MARKET_DATA_COLUMNS].copy()


def _ensure_market_columns(records: pd.DataFrame | None) -> pd.DataFrame:
    return _normalize_market_data_frame(records)


def _clean_text(value) -> str:
    return " ".join(str(value or "").split())


def _normalize_lookup_text(value) -> str:
    return " ".join(str(value or "").split()).casefold()


def _display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未记录"


def _estimated_label(value, is_estimated) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    estimated = str(is_estimated or "").strip().casefold() in {"true", "1", "yes", "y"}
    return f"{text}（估算）" if estimated else text


def _join_non_empty(values: list[object]) -> str:
    items = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in items:
            items.append(text)
    return " / ".join(items)
