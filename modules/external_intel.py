from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
import re
from uuid import uuid4

import pandas as pd


EXTERNAL_INTEL_COLUMNS = [
    "record_id",
    "created_at",
    "appid",
    "game_name",
    "platform",
    "source_url",
    "title",
    "author_or_channel",
    "published_at",
    "views",
    "comments",
    "likes",
    "followers_or_members",
    "evidence_type",
    "sentiment",
    "relevance",
    "key_takeaway",
    "note",
]

EXTERNAL_INTEL_FIELD_LABELS = {
    "record_id": "记录 ID",
    "created_at": "创建时间",
    "appid": "AppID",
    "game_name": "游戏名",
    "platform": "平台",
    "source_url": "来源链接",
    "title": "标题",
    "author_or_channel": "作者/频道",
    "published_at": "发布时间",
    "views": "播放/阅读量",
    "comments": "评论数",
    "likes": "点赞数",
    "followers_or_members": "粉丝/成员数",
    "evidence_type": "证据类型",
    "sentiment": "情绪",
    "relevance": "相关度",
    "key_takeaway": "关键结论",
    "note": "备注",
}

EXTERNAL_INTEL_FIELD_DESCRIPTIONS = {
    "platform": "手动记录的外部来源平台，不自动抓取结果。",
    "source_url": "用户手动粘贴的证据链接。",
    "views": "用户手动录入的播放量或阅读量。",
    "key_takeaway": "人工总结的一句话结论。",
}

PLATFORM_OPTIONS = [
    "YouTube",
    "Bilibili",
    "X/Twitter",
    "Bluesky",
    "Reddit",
    "Discord",
    "Steam社区",
    "小黑盒",
    "NGA",
    "贴吧",
    "巴哈姆特",
    "官网",
    "Presskit",
    "媒体文章",
    "其他",
]

EVIDENCE_TYPE_OPTIONS = [
    "视频",
    "帖子",
    "文章",
    "官网",
    "社群",
    "开发者资料",
    "Presskit",
    "其他",
]

SENTIMENT_OPTIONS = ["正面", "中性", "负面", "未判断"]
RELEVANCE_OPTIONS = ["高", "中", "低"]
CHINESE_PLATFORMS = {"Bilibili", "小黑盒", "NGA", "贴吧", "巴哈姆特"}
EDITABLE_EXTERNAL_INTEL_COLUMNS = [
    "platform",
    "title",
    "author_or_channel",
    "published_at",
    "views",
    "comments",
    "likes",
    "followers_or_members",
    "evidence_type",
    "sentiment",
    "relevance",
    "key_takeaway",
    "note",
]


@dataclass
class ExternalIntelRecord:
    appid: str = ""
    game_name: str = ""
    platform: str = ""
    source_url: str = ""
    title: str = ""
    author_or_channel: str = ""
    published_at: str = ""
    views: str = ""
    comments: str = ""
    likes: str = ""
    followers_or_members: str = ""
    evidence_type: str = ""
    sentiment: str = "未判断"
    relevance: str = "中"
    key_takeaway: str = ""
    note: str = ""
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_external_intel_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in EXTERNAL_INTEL_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True

    if "record_id" in existing.columns:
        missing_id = existing["record_id"].astype(str).str.strip() == ""
        if missing_id.any():
            existing.loc[missing_id, "record_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
            changed = True
    if "created_at" in existing.columns:
        missing_created_at = existing["created_at"].astype(str).str.strip() == ""
        if missing_created_at.any():
            existing.loc[missing_created_at, "created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changed = True

    normalized = _normalize_external_intel_frame(existing)
    if not normalized.equals(existing.loc[:, normalized.columns]):
        existing = normalized
        changed = True

    if changed:
        extra_columns = [column for column in existing.columns if column not in EXTERNAL_INTEL_COLUMNS]
        existing.to_csv(csv_path, columns=EXTERNAL_INTEL_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_external_intel(csv_path: Path) -> pd.DataFrame:
    ensure_external_intel_csv_exists(csv_path)
    try:
        records = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        records = pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS)
    for column in EXTERNAL_INTEL_COLUMNS:
        if column not in records.columns:
            records[column] = ""
    return _normalize_external_intel_frame(records.loc[:, EXTERNAL_INTEL_COLUMNS].copy())


def save_external_intel_to_csv(record: ExternalIntelRecord, csv_path: Path) -> Path:
    ensure_external_intel_csv_exists(csv_path)
    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    record_data = external_intel_to_dict(record)
    record_data = sanitize_external_intel_record(record_data)
    row = pd.DataFrame([{column: record_data.get(column, "") for column in existing_columns}], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def external_intel_to_dict(record: ExternalIntelRecord) -> dict:
    raw = asdict(record)
    return {column: raw.get(column, "") for column in EXTERNAL_INTEL_COLUMNS}


def sanitize_external_intel_record(record: dict) -> dict:
    clean = {}
    for column in EXTERNAL_INTEL_COLUMNS:
        clean[column] = " ".join(str(record.get(column, "") or "").split())
    if not clean["record_id"]:
        clean["record_id"] = str(uuid4())
    if not clean["created_at"]:
        clean["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if clean["platform"] not in PLATFORM_OPTIONS:
        clean["platform"] = clean["platform"] or "其他"
    if clean["evidence_type"] not in EVIDENCE_TYPE_OPTIONS:
        clean["evidence_type"] = clean["evidence_type"] or "其他"
    if clean["sentiment"] not in SENTIMENT_OPTIONS:
        clean["sentiment"] = clean["sentiment"] or "未判断"
    if clean["relevance"] not in RELEVANCE_OPTIONS:
        clean["relevance"] = clean["relevance"] or "中"
    return clean


def filter_external_intel(records: pd.DataFrame, appid: str = "", game_name: str = "") -> pd.DataFrame:
    records = _ensure_columns(records)
    if records.empty:
        return records.loc[:, EXTERNAL_INTEL_COLUMNS].copy()
    clean_appid = str(appid or "").strip()
    clean_name = " ".join(str(game_name or "").split()).casefold()
    if clean_appid:
        mask = records["appid"].astype(str).str.strip().eq(clean_appid)
        return records.loc[mask, EXTERNAL_INTEL_COLUMNS].copy()
    if not clean_name:
        return records.iloc[0:0].loc[:, EXTERNAL_INTEL_COLUMNS].copy()

    normalized_names = records["game_name"].astype(str).map(lambda value: " ".join(value.split()).casefold())
    mask = normalized_names.eq(clean_name) | normalized_names.str.contains(re.escape(clean_name), na=False)
    if not mask.any():
        mask = normalized_names.map(lambda value: bool(value and value in clean_name))
    return records.loc[mask, EXTERNAL_INTEL_COLUMNS].copy()


def filter_external_intel_library(
    records: pd.DataFrame,
    appid: str = "",
    game_name: str = "",
    platform: str = "全部",
    relevance: str = "全部",
    sentiment: str = "全部",
    evidence_type: str = "全部",
) -> pd.DataFrame:
    filtered = _ensure_columns(records)
    clean_appid = str(appid or "").strip()
    clean_name = " ".join(str(game_name or "").split()).casefold()
    if clean_appid:
        filtered = filtered.loc[filtered["appid"].astype(str).str.strip().str.contains(re.escape(clean_appid), case=False, na=False)]
    if clean_name:
        names = filtered["game_name"].astype(str).map(lambda value: " ".join(value.split()).casefold())
        filtered = filtered.loc[names.str.contains(re.escape(clean_name), na=False)]
    if platform and platform != "全部":
        filtered = filtered.loc[filtered["platform"].astype(str).str.strip() == platform]
    if relevance and relevance != "全部":
        filtered = filtered.loc[filtered["relevance"].astype(str).str.strip() == relevance]
    if sentiment and sentiment != "全部":
        filtered = filtered.loc[filtered["sentiment"].astype(str).str.strip() == sentiment]
    if evidence_type and evidence_type != "全部":
        filtered = filtered.loc[filtered["evidence_type"].astype(str).str.strip() == evidence_type]
    return filtered.loc[:, EXTERNAL_INTEL_COLUMNS].copy()


def update_external_intel_record(csv_path: Path, record_id: str, updates: dict) -> bool:
    records = load_external_intel(csv_path)
    clean_id = str(record_id or "").strip()
    if not clean_id:
        return False
    mask = records["record_id"].astype(str).str.strip().eq(clean_id)
    if not mask.any():
        return False

    clean_updates = {
        column: " ".join(str(value or "").split())
        for column, value in (updates or {}).items()
        if column in EDITABLE_EXTERNAL_INTEL_COLUMNS
    }
    for column, value in clean_updates.items():
        records.loc[mask, column] = value
    save_external_intel_frame(records, csv_path)
    return True


def delete_external_intel_records(csv_path: Path, record_ids: list[str]) -> int:
    records = load_external_intel(csv_path)
    clean_ids = {str(record_id or "").strip() for record_id in record_ids if str(record_id or "").strip()}
    if not clean_ids:
        return 0
    before_count = len(records)
    records = records.loc[~records["record_id"].astype(str).str.strip().isin(clean_ids)].copy()
    save_external_intel_frame(records, csv_path)
    return before_count - len(records)


def save_external_intel_frame(records: pd.DataFrame, csv_path: Path) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _normalize_external_intel_frame(records)
    normalized.to_csv(csv_path, columns=EXTERNAL_INTEL_COLUMNS, index=False, encoding="utf-8-sig")
    return csv_path


def find_duplicate_external_intel(records: pd.DataFrame) -> pd.DataFrame:
    records = _ensure_columns(records)
    if records.empty:
        return pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS + ["duplicate_rule", "duplicate_key", "keep_record_id"])

    duplicate_rows = []
    seen_row_keys = set()
    duplicate_specs = [
        ("同一 appid + source_url", "appid"),
        ("同一 game_name + source_url", "game_name"),
    ]
    for rule_name, field_name in duplicate_specs:
        candidates = records.copy()
        candidates["_source_key"] = candidates["source_url"].astype(str).str.strip().str.casefold()
        candidates["_field_key"] = candidates[field_name].astype(str).str.strip().str.casefold()
        candidates = candidates.loc[(candidates["_source_key"] != "") & (candidates["_field_key"] != "")].copy()
        if candidates.empty:
            continue
        candidates["_duplicate_key"] = candidates["_field_key"] + "|" + candidates["_source_key"]
        duplicate_keys = candidates["_duplicate_key"].value_counts()
        duplicate_keys = set(duplicate_keys[duplicate_keys > 1].index.tolist())
        if not duplicate_keys:
            continue
        for duplicate_key in sorted(duplicate_keys):
            group = candidates.loc[candidates["_duplicate_key"] == duplicate_key].copy()
            group = group.sort_values(["created_at", "record_id"], ascending=True)
            keep_record_id = str(group.iloc[0].get("record_id", "") or "").strip()
            for _, row in group.iterrows():
                row_key = (rule_name, str(row.get("record_id", "") or "").strip())
                if row_key in seen_row_keys:
                    continue
                seen_row_keys.add(row_key)
                item = {column: row.get(column, "") for column in EXTERNAL_INTEL_COLUMNS}
                item["duplicate_rule"] = rule_name
                item["duplicate_key"] = duplicate_key
                item["keep_record_id"] = keep_record_id
                duplicate_rows.append(item)
    return pd.DataFrame(duplicate_rows, columns=EXTERNAL_INTEL_COLUMNS + ["duplicate_rule", "duplicate_key", "keep_record_id"])


def duplicate_record_ids_to_delete(duplicates: pd.DataFrame) -> list[str]:
    if duplicates.empty or "keep_record_id" not in duplicates.columns:
        return []
    delete_ids = []
    for _, row in duplicates.iterrows():
        record_id = str(row.get("record_id", "") or "").strip()
        keep_record_id = str(row.get("keep_record_id", "") or "").strip()
        if record_id and record_id != keep_record_id and record_id not in delete_ids:
            delete_ids.append(record_id)
    return delete_ids


def summarize_external_intel(records: pd.DataFrame) -> dict:
    records = _ensure_columns(records)
    if records.empty:
        return {
            "record_count": 0,
            "high_relevance_count": 0,
            "youtube_max_views": "",
            "bilibili_max_views": "",
            "max_traffic": "",
            "main_platforms": [],
            "has_chinese_content": False,
            "has_official_or_presskit": False,
            "has_community": False,
            "key_takeaways": [],
            "rule_notes": ["外部声量：暂未发现明显覆盖"],
        }

    records = records.copy()
    records["_views_num"] = records["views"].map(parse_count)
    platform_counts = records["platform"].astype(str).str.strip()
    evidence_counts = records["evidence_type"].astype(str).str.strip()
    high_records = records.loc[records["relevance"].astype(str).str.strip() == "高"].copy()

    youtube_records = records.loc[platform_counts == "YouTube"]
    bilibili_records = records.loc[platform_counts == "Bilibili"]
    media_records = records.loc[(platform_counts == "媒体文章") | (evidence_counts == "文章")]
    has_chinese_content = bool(platform_counts.isin(CHINESE_PLATFORMS).any())
    has_official_or_presskit = bool(platform_counts.isin({"官网", "Presskit"}).any() or evidence_counts.isin({"官网", "Presskit"}).any())
    has_community = bool(platform_counts.isin({"Discord", "Reddit", "Steam社区"}).any() or evidence_counts.eq("社群").any())

    rule_notes = []
    if has_chinese_content:
        rule_notes.append("中文声量：已有中文侧内容")
    if not youtube_records.empty and youtube_records["_views_num"].max() >= 10000:
        rule_notes.append("海外视频声量：有一定视频传播")
    if youtube_records.empty and bilibili_records.empty and media_records.empty:
        rule_notes.append("外部声量：暂未发现明显覆盖")
    if has_official_or_presskit or has_community:
        rule_notes.append("基础资料：资料入口较完整")

    top_key_records = pd.concat([high_records, records], ignore_index=True)
    key_takeaways = []
    for takeaway in top_key_records["key_takeaway"].astype(str).tolist():
        clean = takeaway.strip()
        if clean and clean not in key_takeaways:
            key_takeaways.append(clean)
        if len(key_takeaways) >= 3:
            break

    return {
        "record_count": int(len(records)),
        "high_relevance_count": int(len(high_records)),
        "youtube_max_views": format_count(youtube_records["_views_num"].max()) if not youtube_records.empty else "",
        "bilibili_max_views": format_count(bilibili_records["_views_num"].max()) if not bilibili_records.empty else "",
        "max_traffic": _max_traffic_label(records),
        "main_platforms": _main_platforms(platform_counts),
        "has_chinese_content": has_chinese_content,
        "has_official_or_presskit": has_official_or_presskit,
        "has_community": has_community,
        "key_takeaways": key_takeaways,
        "rule_notes": rule_notes,
    }


def build_external_intel_markdown_section(records: pd.DataFrame) -> str:
    summary = summarize_external_intel(records)
    if summary["record_count"] <= 0:
        return "## 4. 外部声量与资料\n- 暂无外部情报记录。\n"
    lines = [
        "## 4. 外部声量与资料",
        f"- 记录数：{summary['record_count']}",
        f"- 高相关记录：{summary['high_relevance_count']}",
    ]
    if summary["main_platforms"]:
        lines.append(f"- 主要平台：{', '.join(summary['main_platforms'])}")
    if summary["max_traffic"]:
        lines.append(f"- 最高播放/阅读：{summary['max_traffic']}")
    if summary["has_chinese_content"]:
        lines.append("- 中文侧内容：已有中文侧内容")
    if summary["has_official_or_presskit"]:
        lines.append("- 官网/Presskit：已有")
    if summary["key_takeaways"]:
        lines.append("- 关键结论：")
        lines.extend([f"  - {item}" for item in summary["key_takeaways"]])
    lines.append("")
    return "\n".join(lines)


def parse_count(value) -> int:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return 0
    multiplier = 1
    if "万" in text:
        multiplier = 10000
    elif re.search(r"\bk\b", text, flags=re.I):
        multiplier = 1000
    elif re.search(r"\bm\b", text, flags=re.I):
        multiplier = 1000000
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return 0
    return int(float(match.group(0)) * multiplier)


def format_count(value) -> str:
    try:
        number = int(float(value or 0))
    except (TypeError, ValueError):
        number = 0
    return f"{number:,}" if number > 0 else ""


def _ensure_columns(records: pd.DataFrame) -> pd.DataFrame:
    if records is None:
        return pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS)
    output = records.copy()
    for column in EXTERNAL_INTEL_COLUMNS:
        if column not in output.columns:
            output[column] = ""
    return output.loc[:, EXTERNAL_INTEL_COLUMNS].copy()


def _normalize_external_intel_frame(records: pd.DataFrame) -> pd.DataFrame:
    output = records.copy() if records is not None else pd.DataFrame(columns=EXTERNAL_INTEL_COLUMNS)
    for column in EXTERNAL_INTEL_COLUMNS:
        if column not in output.columns:
            output[column] = ""
        output[column] = output[column].astype(str).map(lambda value: " ".join(str(value or "").split()))

    missing_id = output["record_id"].astype(str).str.strip() == ""
    if missing_id.any():
        output.loc[missing_id, "record_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
    missing_created_at = output["created_at"].astype(str).str.strip() == ""
    if missing_created_at.any():
        output.loc[missing_created_at, "created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return output.loc[:, EXTERNAL_INTEL_COLUMNS].copy()


def _main_platforms(platforms: pd.Series) -> list[str]:
    counts = platforms[platforms.astype(str).str.strip() != ""].value_counts()
    return counts.head(5).index.tolist()


def _max_traffic_label(records: pd.DataFrame) -> str:
    if records.empty or "_views_num" not in records.columns:
        return ""
    sorted_records = records.sort_values("_views_num", ascending=False)
    for _, row in sorted_records.iterrows():
        views = int(row.get("_views_num") or 0)
        if views <= 0:
            continue
        platform = str(row.get("platform", "") or "外部记录").strip()
        title = str(row.get("title", "") or "").strip()
        label = f"{platform} {format_count(views)}"
        return f"{label}（{title}）" if title else label
    return ""
