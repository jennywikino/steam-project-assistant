from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
import re

import pandas as pd


COMPANY_DOSSIER_COLUMNS = [
    "dossier_id",
    "created_at",
    "updated_at",
    "appid",
    "game_name",
    "company_name",
    "company_role",
    "country_or_region",
    "team_size",
    "founded_year",
    "known_games",
    "official_site",
    "steam_creator_url",
    "presskit_url",
    "discord_url",
    "x_url",
    "youtube_url",
    "bilibili_url",
    "contact_email",
    "contact_discord",
    "publisher_history",
    "self_publish_status",
    "evidence_summary",
    "risk_note",
    "next_action",
    "confidence",
    "source_urls",
]

COMPANY_ROLE_OPTIONS = ["developer", "publisher", "developer_and_publisher", "unknown"]
SELF_PUBLISH_STATUS_OPTIONS = ["自发行", "有发行商", "曾有发行合作", "未确认"]
COMPANY_CONFIDENCE_OPTIONS = ["高", "中", "低", "未确认"]

COMPANY_ROLE_LABELS = {
    "developer": "开发商",
    "publisher": "发行商",
    "developer_and_publisher": "两者都是",
    "unknown": "未确认",
}

COMPANY_ROLE_BY_LABEL = {value: key for key, value in COMPANY_ROLE_LABELS.items()}

COMPANY_DOSSIER_FIELD_LABELS = {
    "dossier_id": "档案 ID",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "appid": "AppID",
    "game_name": "游戏名",
    "company_name": "公司/团队名",
    "company_role": "角色",
    "country_or_region": "国家/地区",
    "team_size": "团队人数",
    "founded_year": "成立年份",
    "known_games": "已知作品",
    "official_site": "官网",
    "steam_creator_url": "Steam Creator / Developer 页面",
    "presskit_url": "Presskit",
    "discord_url": "Discord",
    "x_url": "X/Twitter",
    "youtube_url": "YouTube",
    "bilibili_url": "B站",
    "contact_email": "联系邮箱",
    "contact_discord": "Discord 联系方式",
    "publisher_history": "发行合作史",
    "self_publish_status": "自发行状态",
    "evidence_summary": "证据摘要",
    "risk_note": "风险备注",
    "next_action": "下一步动作",
    "confidence": "可信度",
    "source_urls": "其他来源链接",
}


@dataclass
class CompanyDossierRecord:
    appid: str = ""
    game_name: str = ""
    company_name: str = ""
    company_role: str = "unknown"
    country_or_region: str = ""
    team_size: str = ""
    founded_year: str = ""
    known_games: str = ""
    official_site: str = ""
    steam_creator_url: str = ""
    presskit_url: str = ""
    discord_url: str = ""
    x_url: str = ""
    youtube_url: str = ""
    bilibili_url: str = ""
    contact_email: str = ""
    contact_discord: str = ""
    publisher_history: str = ""
    self_publish_status: str = "未确认"
    evidence_summary: str = ""
    risk_note: str = ""
    next_action: str = ""
    confidence: str = "未确认"
    source_urls: str = ""
    dossier_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_company_dossier_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=COMPANY_DOSSIER_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=COMPANY_DOSSIER_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in COMPANY_DOSSIER_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "dossier_id" in existing.columns:
        missing_id = existing["dossier_id"].astype(str).str.strip() == ""
        if missing_id.any():
            existing.loc[missing_id, "dossier_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
            changed = True
    for time_column in ["created_at", "updated_at"]:
        missing_time = existing[time_column].astype(str).str.strip() == ""
        if missing_time.any():
            existing.loc[missing_time, time_column] = now
            changed = True

    normalized = _normalize_company_dossier_frame(existing)
    if not normalized.equals(existing.loc[:, normalized.columns]):
        existing = normalized
        changed = True

    if changed:
        extra_columns = [column for column in existing.columns if column not in COMPANY_DOSSIER_COLUMNS]
        existing.to_csv(csv_path, columns=COMPANY_DOSSIER_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_company_dossiers(csv_path: Path) -> pd.DataFrame:
    ensure_company_dossier_csv_exists(csv_path)
    try:
        records = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        records = pd.DataFrame(columns=COMPANY_DOSSIER_COLUMNS)
    return _normalize_company_dossier_frame(records)


def save_company_dossier_to_csv(record: CompanyDossierRecord, csv_path: Path) -> Path:
    ensure_company_dossier_csv_exists(csv_path)
    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    record_data = sanitize_company_dossier_record(company_dossier_to_dict(record))
    row = pd.DataFrame([{column: record_data.get(column, "") for column in existing_columns}], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def update_company_dossier_record(csv_path: Path, dossier_id: str, updates: dict) -> bool:
    records = load_company_dossiers(csv_path)
    clean_id = str(dossier_id or "").strip()
    if not clean_id:
        return False
    mask = records["dossier_id"].astype(str).str.strip().eq(clean_id)
    if not mask.any():
        return False

    allowed = set(COMPANY_DOSSIER_COLUMNS) - {"dossier_id", "created_at"}
    clean_updates = sanitize_company_dossier_record({**records.loc[mask].iloc[0].to_dict(), **(updates or {})})
    clean_updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for column, value in clean_updates.items():
        if column in allowed:
            records.loc[mask, column] = value
    save_company_dossier_frame(records, csv_path)
    return True


def delete_company_dossier_records(csv_path: Path, dossier_ids: list[str]) -> int:
    records = load_company_dossiers(csv_path)
    clean_ids = {str(dossier_id or "").strip() for dossier_id in dossier_ids if str(dossier_id or "").strip()}
    if not clean_ids:
        return 0
    before_count = len(records)
    records = records.loc[~records["dossier_id"].astype(str).str.strip().isin(clean_ids)].copy()
    save_company_dossier_frame(records, csv_path)
    return before_count - len(records)


def save_company_dossier_frame(records: pd.DataFrame, csv_path: Path) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _normalize_company_dossier_frame(records)
    normalized.to_csv(csv_path, columns=COMPANY_DOSSIER_COLUMNS, index=False, encoding="utf-8-sig")
    return csv_path


def company_dossier_to_dict(record: CompanyDossierRecord) -> dict:
    raw = asdict(record)
    return {column: raw.get(column, "") for column in COMPANY_DOSSIER_COLUMNS}


def sanitize_company_dossier_record(record: dict) -> dict:
    clean = {}
    for column in COMPANY_DOSSIER_COLUMNS:
        clean[column] = _clean_text(record.get(column, ""))
    if not clean["dossier_id"]:
        clean["dossier_id"] = str(uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not clean["created_at"]:
        clean["created_at"] = now
    if not clean["updated_at"]:
        clean["updated_at"] = clean["created_at"] or now
    if clean["company_role"] not in COMPANY_ROLE_OPTIONS:
        clean["company_role"] = "unknown"
    if clean["self_publish_status"] not in SELF_PUBLISH_STATUS_OPTIONS:
        clean["self_publish_status"] = "未确认"
    if clean["confidence"] not in COMPANY_CONFIDENCE_OPTIONS:
        clean["confidence"] = "未确认"
    return clean


def filter_company_dossiers(
    records: pd.DataFrame,
    appid: str = "",
    game_name: str = "",
    company_name: str = "",
    company_role: str = "全部",
    confidence: str = "全部",
) -> pd.DataFrame:
    filtered = _ensure_company_columns(records)
    clean_appid = str(appid or "").strip()
    clean_game_name = _normalize_lookup_text(game_name)
    clean_company_name = _normalize_lookup_text(company_name)

    if clean_appid:
        filtered = filtered.loc[filtered["appid"].astype(str).str.strip().str.contains(re.escape(clean_appid), case=False, na=False)]
    if clean_game_name:
        names = filtered["game_name"].astype(str).map(_normalize_lookup_text)
        filtered = filtered.loc[names.str.contains(re.escape(clean_game_name), na=False)]
    if clean_company_name:
        companies = filtered["company_name"].astype(str).map(_normalize_lookup_text)
        filtered = filtered.loc[companies.str.contains(re.escape(clean_company_name), na=False)]
    if company_role and company_role != "全部":
        role_value = COMPANY_ROLE_BY_LABEL.get(company_role, company_role)
        filtered = filtered.loc[filtered["company_role"].astype(str).str.strip() == role_value]
    if confidence and confidence != "全部":
        filtered = filtered.loc[filtered["confidence"].astype(str).str.strip() == confidence]
    return sort_company_dossiers(filtered)


def filter_company_dossiers_for_project(records: pd.DataFrame, appid: str = "", game_name: str = "") -> pd.DataFrame:
    records = _ensure_company_columns(records)
    clean_appid = str(appid or "").strip()
    clean_name = _normalize_lookup_text(game_name)
    if clean_appid:
        return sort_company_dossiers(records.loc[records["appid"].astype(str).str.strip().eq(clean_appid)])
    if not clean_name:
        return records.iloc[0:0].loc[:, COMPANY_DOSSIER_COLUMNS].copy()
    names = records["game_name"].astype(str).map(_normalize_lookup_text)
    mask = names.eq(clean_name) | names.str.contains(re.escape(clean_name), na=False)
    return sort_company_dossiers(records.loc[mask])


def latest_company_dossier(records: pd.DataFrame) -> dict:
    records = sort_company_dossiers(records)
    if records.empty:
        return {}
    return records.iloc[0].to_dict()


def sort_company_dossiers(records: pd.DataFrame) -> pd.DataFrame:
    records = _ensure_company_columns(records)
    if records.empty:
        return records
    sorted_records = records.copy()
    sorted_records["_updated_at_sort"] = pd.to_datetime(sorted_records["updated_at"], errors="coerce")
    sorted_records = sorted_records.sort_values(
        by=["_updated_at_sort", "updated_at", "created_at"],
        ascending=[False, False, False],
        na_position="last",
    )
    return sorted_records.drop(columns=["_updated_at_sort"]).loc[:, COMPANY_DOSSIER_COLUMNS].copy()


def parse_company_names(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        raw_items = []
        for item in value:
            raw_items.extend(parse_company_names(item))
    else:
        text = str(value or "").strip()
        if not text:
            return []
        raw_items = re.split(r"\s*(?:/|,|;|、|，|；)\s*", text)

    names = []
    seen = set()
    for item in raw_items:
        clean = str(item or "").strip()
        if not clean:
            continue
        key = clean.casefold()
        if key in seen:
            continue
        seen.add(key)
        names.append(clean)
    return names


def build_company_search_links(company_name: str, include_steam: bool = True) -> list[tuple[str, str]]:
    name = str(company_name or "").strip()
    if not name:
        return []
    links = []
    if include_steam:
        links.extend(
            [
                ("Steam 开发者搜索", f"https://store.steampowered.com/search/?developer={quote(name)}"),
                ("Steam 发行商搜索", f"https://store.steampowered.com/search/?publisher={quote(name)}"),
            ]
        )
    links.extend([
        ("Google developer", f"https://www.google.com/search?q={quote(name + ' game developer')}"),
        ("Google presskit", f"https://www.google.com/search?q={quote(name + ' presskit')}"),
        ("Google contact", f"https://www.google.com/search?q={quote(name + ' contact')}"),
        ("YouTube", f"https://www.youtube.com/results?search_query={quote(name + ' game')}"),
        ("B站", f"https://search.bilibili.com/all?keyword={quote(name + ' 游戏')}"),
        ("X/Twitter", f"https://twitter.com/search?q={quote(name)}&src=typed_query"),
        ("Bluesky", f"https://bsky.app/search?q={quote(name)}"),
        ("LinkedIn", f"https://www.linkedin.com/search/results/all/?keywords={quote(name + ' game studio')}"),
        ("Discord", f"https://www.google.com/search?q={quote(name + ' game discord')}"),
    ])
    return links


def build_company_dossier_markdown_section(
    records: pd.DataFrame | None = None,
    associated_companies: list[tuple[str, str]] | None = None,
) -> str:
    records = _ensure_company_columns(records)
    lines = ["## 开发商本体调查", ""]
    if associated_companies:
        lines.append("关联公司：")
        for role, name in associated_companies:
            clean_name = str(name or "").strip()
            if clean_name:
                lines.append(f"- {display_company_role(role)}：{clean_name}")
        lines.append("")
    if records.empty:
        lines.append("暂无开发商本体调查记录。")
        lines.append("")
        return "\n".join(lines)

    row = latest_company_dossier(records)
    contact = _join_non_empty(
        [
            row.get("contact_email"),
            row.get("contact_discord"),
            row.get("official_site"),
            row.get("discord_url"),
            row.get("x_url"),
            row.get("youtube_url"),
            row.get("bilibili_url"),
        ]
    )
    lines.extend([
        f"- 公司/团队：{_display(row.get('company_name'))}",
        f"- 角色：{display_company_role(row.get('company_role'))}",
        f"- 国家/地区：{_display(row.get('country_or_region'))}",
        f"- 团队规模：{_display(row.get('team_size'))}",
        f"- 已知作品：{_display(row.get('known_games'))}",
        f"- 自发行状态：{_display(row.get('self_publish_status'))}",
        f"- 发行合作史：{_display(row.get('publisher_history'))}",
        f"- 联系方式：{_display(contact)}",
        f"- 证据摘要：{_display(row.get('evidence_summary'))}",
        f"- 风险备注：{_display(row.get('risk_note'))}",
        f"- 下一步动作：{_display(row.get('next_action'))}",
        f"- 可信度：{_display(row.get('confidence'))}",
        "",
    ])
    return "\n".join(lines)


def display_company_role(value) -> str:
    return COMPANY_ROLE_LABELS.get(str(value or "").strip(), "未确认")


def _normalize_company_dossier_frame(records: pd.DataFrame) -> pd.DataFrame:
    output = records.copy() if records is not None else pd.DataFrame(columns=COMPANY_DOSSIER_COLUMNS)
    for column in COMPANY_DOSSIER_COLUMNS:
        if column not in output.columns:
            output[column] = ""
        output[column] = output[column].astype(str).map(_clean_text)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    missing_id = output["dossier_id"].astype(str).str.strip() == ""
    if missing_id.any():
        output.loc[missing_id, "dossier_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
    missing_created_at = output["created_at"].astype(str).str.strip() == ""
    if missing_created_at.any():
        output.loc[missing_created_at, "created_at"] = now
    missing_updated_at = output["updated_at"].astype(str).str.strip() == ""
    if missing_updated_at.any():
        output.loc[missing_updated_at, "updated_at"] = output.loc[missing_updated_at, "created_at"]

    output["company_role"] = output["company_role"].map(lambda value: value if value in COMPANY_ROLE_OPTIONS else "unknown")
    output["self_publish_status"] = output["self_publish_status"].map(
        lambda value: value if value in SELF_PUBLISH_STATUS_OPTIONS else "未确认"
    )
    output["confidence"] = output["confidence"].map(lambda value: value if value in COMPANY_CONFIDENCE_OPTIONS else "未确认")
    return output.loc[:, COMPANY_DOSSIER_COLUMNS].copy()


def _ensure_company_columns(records: pd.DataFrame | None) -> pd.DataFrame:
    return _normalize_company_dossier_frame(records)


def _clean_text(value) -> str:
    return " ".join(str(value or "").split())


def _normalize_lookup_text(value) -> str:
    return " ".join(str(value or "").split()).casefold()


def _display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未确认"


def _join_non_empty(values: list[object]) -> str:
    items = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in items:
            items.append(text)
    return " / ".join(items)
