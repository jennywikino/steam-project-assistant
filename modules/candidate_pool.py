from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
import re
from uuid import uuid4

import pandas as pd

from modules.publishing_rules import evaluate_publishing_candidate


STAGE_OPTIONS = [
    "新发现",
    "待补资料",
    "待试玩",
    "待社媒确认",
    "待开发商调查",
    "值得联系",
    "已联系",
    "暂缓",
    "放弃",
]

PRIORITY_OPTIONS = ["高", "中", "低", "未定"]

CANDIDATE_POOL_COLUMNS = [
    "candidate_id",
    "created_at",
    "updated_at",
    "appid",
    "game_name",
    "steam_url",
    "steamdb_url",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "price",
    "review_score",
    "review_count",
    "median_playtime",
    "avg_playtime",
    "source",
    "source_url",
    "priority",
    "stage",
    "next_action",
    "owner_note",
    "reject_reason",
    "auto_suggestion",
    "auto_reason",
    "data_completeness",
    "missing_items",
    "market_data_source",
    "market_data_date",
    "steamdb_rank",
    "steamdb_followers",
    "steamdb_peak_ccu",
    "peak_ccu",
    "source_notes",
    "vgi_units",
    "gamalytic_owners",
    "latest_news_date",
    "is_archived",
]

CANDIDATE_POOL_FIELD_LABELS = {
    "candidate_id": "候选 ID",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "appid": "AppID",
    "game_name": "游戏名",
    "steam_url": "Steam 链接",
    "steamdb_url": "SteamDB 链接",
    "developer": "开发商",
    "publisher": "发行商",
    "release_status": "发售状态",
    "release_date": "发售日期",
    "has_demo": "Demo",
    "supports_schinese": "简中",
    "genres_tags": "类型",
    "price": "价格",
    "review_score": "评分",
    "review_count": "评论数",
    "median_playtime": "中位游玩",
    "avg_playtime": "平均游玩",
    "source": "来源",
    "source_url": "来源链接",
    "priority": "优先级",
    "stage": "当前阶段",
    "next_action": "下一步动作",
    "owner_note": "备注",
    "reject_reason": "放弃原因",
    "auto_suggestion": "自动建议",
    "auto_reason": "建议理由",
    "data_completeness": "数据完整度",
    "missing_items": "缺失项",
    "market_data_source": "第三方市场来源",
    "market_data_date": "第三方市场记录日期",
    "steamdb_rank": "SteamDB rank",
    "steamdb_followers": "SteamDB followers",
    "steamdb_peak_ccu": "SteamDB peak CCU",
    "peak_ccu": "Peak CCU",
    "source_notes": "来源备注",
    "vgi_units": "VGI units",
    "gamalytic_owners": "Gamalytic owners",
    "latest_news_date": "latest_news_date",
    "is_archived": "已归档",
}

POOL_TABLE_COLUMNS = [
    "game_name",
    "appid",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "supports_schinese",
    "review_score",
    "review_count",
    "stage",
    "priority",
    "auto_suggestion",
    "data_completeness",
    "missing_items",
    "next_action",
    "updated_at",
]

POOL_FULL_TABLE_COLUMNS = [
    "candidate_id",
    "created_at",
    "updated_at",
    "appid",
    "game_name",
    "steam_url",
    "steamdb_url",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "price",
    "review_score",
    "review_count",
    "median_playtime",
    "avg_playtime",
    "source",
    "source_url",
    "priority",
    "stage",
    "auto_suggestion",
    "auto_reason",
    "data_completeness",
    "missing_items",
    "market_data_source",
    "market_data_date",
    "steamdb_rank",
    "steamdb_followers",
    "steamdb_peak_ccu",
    "peak_ccu",
    "vgi_units",
    "gamalytic_owners",
    "latest_news_date",
    "source_notes",
    "next_action",
    "owner_note",
    "reject_reason",
    "is_archived",
]

EXPORT_COLUMNS = [
    "game_name",
    "steam_url",
    "steamdb_url",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "review_score",
    "review_count",
    "stage",
    "priority",
    "auto_suggestion",
    "data_completeness",
    "missing_items",
    "market_data_source",
    "market_data_date",
    "next_action",
    "owner_note",
    "reject_reason",
    "updated_at",
]


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class CandidatePoolRecord:
    appid: str = ""
    game_name: str = ""
    steam_url: str = ""
    steamdb_url: str = ""
    developer: str = ""
    publisher: str = ""
    release_status: str = ""
    release_date: str = ""
    has_demo: str = ""
    supports_schinese: str = ""
    genres_tags: str = ""
    price: str = ""
    review_score: str = ""
    review_count: str = ""
    median_playtime: str = ""
    avg_playtime: str = ""
    source: str = ""
    source_url: str = ""
    priority: str = "未定"
    stage: str = "新发现"
    next_action: str = ""
    owner_note: str = ""
    reject_reason: str = ""
    auto_suggestion: str = ""
    auto_reason: str = ""
    data_completeness: str = ""
    missing_items: str = ""
    market_data_source: str = ""
    market_data_date: str = ""
    steamdb_rank: str = ""
    steamdb_followers: str = ""
    steamdb_peak_ccu: str = ""
    peak_ccu: str = ""
    source_notes: str = ""
    vgi_units: str = ""
    gamalytic_owners: str = ""
    latest_news_date: str = ""
    is_archived: str = "False"
    candidate_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now_text)
    updated_at: str = field(default_factory=_now_text)


def ensure_candidate_pool_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=CANDIDATE_POOL_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=CANDIDATE_POOL_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in CANDIDATE_POOL_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True
    if "candidate_id" in existing.columns:
        missing_id = existing["candidate_id"].astype(str).str.strip() == ""
        if missing_id.any():
            existing.loc[missing_id, "candidate_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
            changed = True
    for column, default in {"priority": "未定", "stage": "新发现", "is_archived": "False"}.items():
        missing = existing[column].astype(str).str.strip() == ""
        if missing.any():
            existing.loc[missing, column] = default
            changed = True
    if changed:
        extra_columns = [column for column in existing.columns if column not in CANDIDATE_POOL_COLUMNS]
        existing.to_csv(csv_path, columns=CANDIDATE_POOL_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_candidate_pool(csv_path: Path) -> pd.DataFrame:
    ensure_candidate_pool_csv_exists(csv_path)
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=CANDIDATE_POOL_COLUMNS)
    for column in CANDIDATE_POOL_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, CANDIDATE_POOL_COLUMNS].copy()


def candidate_pool_record_to_dict(record: CandidatePoolRecord) -> dict:
    raw = asdict(record)
    output = {column: str(raw.get(column, "") or "").strip() for column in CANDIDATE_POOL_COLUMNS}
    output["priority"] = output["priority"] if output["priority"] in PRIORITY_OPTIONS else "未定"
    output["stage"] = output["stage"] if output["stage"] in STAGE_OPTIONS else "新发现"
    output["is_archived"] = output["is_archived"] or "False"
    return output


def upsert_candidate_pool_record(record: CandidatePoolRecord, csv_path: Path) -> tuple[Path, str]:
    ensure_candidate_pool_csv_exists(csv_path)
    data = load_candidate_pool(csv_path)
    row = candidate_pool_record_to_dict(record)
    now = _now_text()
    appid = row.get("appid", "")

    match_mask = pd.Series(False, index=data.index)
    if appid:
        match_mask = data["appid"].astype(str).str.strip().eq(appid)

    if match_mask.any():
        index = data.loc[match_mask].index[0]
        data.loc[index, "updated_at"] = now
        for column in [
            "game_name",
            "steam_url",
            "steamdb_url",
            "developer",
            "publisher",
            "release_status",
            "release_date",
            "has_demo",
            "supports_schinese",
            "genres_tags",
            "price",
            "review_score",
            "review_count",
            "median_playtime",
            "avg_playtime",
            "auto_suggestion",
            "auto_reason",
            "data_completeness",
            "missing_items",
            "market_data_source",
            "market_data_date",
            "steamdb_rank",
            "steamdb_followers",
            "steamdb_peak_ccu",
            "peak_ccu",
            "source_notes",
            "vgi_units",
            "gamalytic_owners",
            "latest_news_date",
            "source",
            "source_url",
        ]:
            if row.get(column):
                data.loc[index, column] = row[column]
        data.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return csv_path, "updated"

    if not appid and not row.get("stage"):
        row["stage"] = "待补资料"
    if not appid:
        row["stage"] = "待补资料"
        row["next_action"] = row.get("next_action") or "资料不足：补 AppID / Steam 链接"
    row["created_at"] = now
    row["updated_at"] = now
    data = pd.concat([data, pd.DataFrame([row], columns=CANDIDATE_POOL_COLUMNS)], ignore_index=True)
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, "created"


def find_candidate_by_appid(csv_path: Path, appid: str) -> dict:
    clean_appid = str(appid or "").strip()
    if not clean_appid:
        return {}
    data = load_candidate_pool(csv_path)
    matches = data.loc[data["appid"].astype(str).str.strip().eq(clean_appid)]
    if matches.empty:
        return {}
    return matches.iloc[0].to_dict()


def update_candidate_pool_fields(csv_path: Path, candidate_id: str = "", appid: str = "", updates: dict | None = None) -> Path:
    data = load_candidate_pool(csv_path)
    updates = updates or {}
    mask = pd.Series(False, index=data.index)
    if candidate_id:
        mask = mask | data["candidate_id"].astype(str).str.strip().eq(str(candidate_id).strip())
    if appid:
        mask = mask | data["appid"].astype(str).str.strip().eq(str(appid).strip())
    if not mask.any():
        raise ValueError("未找到候选记录。")
    for column, value in updates.items():
        if column in data.columns:
            data.loc[mask, column] = str(value)
    data.loc[mask, "updated_at"] = _now_text()
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def filter_candidate_pool(
    data: pd.DataFrame,
    stage: str = "全部",
    priority: str = "全部",
    has_demo: str = "全部",
    supports_schinese: str = "全部",
    archived: str = "未归档",
) -> pd.DataFrame:
    filtered = data.copy()
    if stage != "全部":
        filtered = filtered.loc[filtered["stage"].astype(str).str.strip().eq(stage)]
    if priority != "全部":
        filtered = filtered.loc[filtered["priority"].astype(str).str.strip().eq(priority)]
    if has_demo != "全部":
        filtered = filtered.loc[filtered["has_demo"].astype(str).str.strip().eq(has_demo)]
    if supports_schinese != "全部":
        filtered = filtered.loc[filtered["supports_schinese"].astype(str).str.strip().eq(supports_schinese)]
    if archived == "未归档":
        filtered = filtered.loc[~filtered["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})]
    elif archived == "已归档":
        filtered = filtered.loc[filtered["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})]
    return filtered.copy()


def candidate_pool_summary(data: pd.DataFrame) -> dict:
    if data.empty:
        return {
            "today_new": 0,
            "pending": 0,
            "high_priority": 0,
            "demo": 0,
            "contact": 0,
            "rejected": 0,
            "insufficient": 0,
        }
    active = data.loc[~data["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})].copy()
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    pending_stages = {"新发现", "待补资料", "待社媒确认", "待开发商调查", "暂缓"}
    suggestions = apply_auto_suggestions(data)
    return {
        "today_new": int(data["created_at"].astype(str).str.startswith(today_prefix).sum()),
        "pending": int(active["stage"].astype(str).isin(pending_stages).sum()),
        "high_priority": int(active["priority"].astype(str).eq("高").sum()),
        "demo": int(active["stage"].astype(str).eq("待试玩").sum()),
        "contact": int(active["stage"].astype(str).eq("值得联系").sum()),
        "rejected": int(data["stage"].astype(str).eq("放弃").sum()),
        "insufficient": int(suggestions["auto_suggestion"].astype(str).eq("资料不足").sum()) if "auto_suggestion" in suggestions.columns else 0,
    }


def parse_candidate_import_lines(text: str) -> list[dict]:
    rows = []
    for line_number, raw_line in enumerate(str(text or "").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        appid = parse_appid_from_text(line)
        if not appid:
            rows.append({"line_number": line_number, "raw_line": line, "appid": "", "error": "未解析到 AppID"})
            continue
        rows.append({"line_number": line_number, "raw_line": line, "appid": appid, "error": ""})
    return rows


def parse_appid_from_text(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    if value.isdigit():
        return value
    steam_match = re.search(r"store\.steampowered\.com/app/(\d+)", value, flags=re.IGNORECASE)
    if steam_match:
        return steam_match.group(1)
    steamdb_match = re.search(r"steamdb\.info/app/(\d+)", value, flags=re.IGNORECASE)
    if steamdb_match:
        return steamdb_match.group(1)
    if re.search(r"\bappid\b", value, flags=re.IGNORECASE):
        appid_match = re.search(r"\bappid\b\s*[:：=#-]?\s*(\d{3,10})\b", value, flags=re.IGNORECASE)
        return appid_match.group(1) if appid_match else ""
    return ""


def apply_auto_suggestions(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    if output.empty:
        for column in ["auto_suggestion", "auto_reason", "next_action"]:
            if column not in output.columns:
                output[column] = ""
        return output
    for column in CANDIDATE_POOL_COLUMNS:
        if column not in output.columns:
            output[column] = ""
    suggestions = []
    reasons = []
    next_actions = []
    for _, row in output.iterrows():
        rule_result = evaluate_publishing_candidate(row.to_dict())
        suggestions.append(str(rule_result.get("auto_suggestion", "") or ""))
        reasons.append(str(rule_result.get("auto_reason", "") or ""))
        current_next_action = str(row.get("next_action", "") or "").strip()
        next_actions.append(current_next_action or str(rule_result.get("next_action", "") or ""))
    output["auto_suggestion"] = suggestions
    output["auto_reason"] = reasons
    output["next_action"] = next_actions
    return output


def build_auto_suggestion(row: dict) -> tuple[str, str]:
    result = evaluate_publishing_candidate(row)
    return str(result.get("auto_suggestion", "") or ""), str(result.get("auto_reason", "") or "")

    developer = _clean_rule_value(row.get("developer"))
    publisher = _clean_rule_value(row.get("publisher"))
    genres = _clean_rule_value(row.get("genres_tags"))
    release_text = _clean_rule_value(row.get("release_status") or row.get("release_date"))
    has_demo = _clean_rule_value(row.get("has_demo"))
    supports_schinese = _clean_rule_value(row.get("supports_schinese"))
    review_count = _parse_int(row.get("review_count"))

    reason_parts = []
    if not developer or not genres:
        suggestion = "资料不足"
        reason_parts.append("基础字段缺失，需要补项目画像")
    elif has_demo == "是" and supports_schinese == "是" and not publisher:
        suggestion = "可优先查看"
        reason_parts.append("具备试玩与中文区验证条件")
    elif not publisher:
        suggestion = "资料不足"
        reason_parts.append("基础字段缺失，需要补项目画像")
    elif is_released_candidate(release_text) and review_count >= 500:
        suggestion = "已上线项目"
        reason_parts.append("评论数较高且已发售，更适合作竞品参考，不作为发行候选")
    elif publisher and developer and publisher.casefold() != developer.casefold():
        suggestion = "已有发行"
        reason_parts.append("Steam 显示已有发行商")
    elif has_demo == "否" and not is_released_candidate(release_text):
        suggestion = "观望"
        reason_parts.append("暂无 Demo，无法验证试玩转化")
    elif has_demo == "是" and supports_schinese == "是":
        suggestion = "可优先查看"
        reason_parts.append("具备试玩与中文区验证条件")
    else:
        suggestion = "人工复核"
        reason_parts.append("字段不足以自动判断，需人工复核")

    if supports_schinese == "是":
        reason_parts.append("已显示支持简中，可检查中文区反馈")
    return suggestion, "；".join(reason_parts)


def apply_suggestion_to_stage(suggestion: str) -> dict:
    mapping = {
        "待补资料": {"stage": "待补资料", "priority": "未定", "next_action": "补项目画像"},
        "暂缓": {"stage": "暂缓", "priority": "低", "next_action": "作为竞品参考"},
        "竞品参考": {"stage": "待开发商调查", "priority": "低", "next_action": "查发行合作空间"},
        "值得联系": {"stage": "值得联系", "priority": "高", "next_action": "查联系方式 / 准备外联"},
        "待试玩": {"stage": "待试玩", "priority": "中", "next_action": "试玩 Demo"},
        "待开发商调查": {"stage": "待开发商调查", "priority": "未定", "next_action": "查开发商背景"},
        "资料不足": {"stage": "待补资料", "priority": "未定", "next_action": "补项目画像"},
        "观望": {"stage": "暂缓", "priority": "低", "next_action": "等待 Demo / 新资料"},
        "可优先查看": {"stage": "待试玩", "priority": "高", "next_action": "试玩 Demo / 补中文区反馈"},
        "已有发行": {"stage": "待开发商调查", "priority": "低", "next_action": "确认发行商关系"},
        "已上线项目": {"stage": "暂缓", "priority": "低", "next_action": "作为竞品参考"},
        "人工复核": {"stage": "待补资料", "priority": "未定", "next_action": "人工复核"},
    }
    return mapping.get(str(suggestion or "").strip(), mapping["人工复核"]).copy()


def is_insufficient_candidate(row: dict) -> bool:
    suggestion, _ = build_auto_suggestion(row)
    return suggestion in {"待补资料", "资料不足"}


def is_released_candidate(value: str) -> bool:
    text = str(value or "").casefold()
    if not text:
        return False
    unreleased_markers = ["即将", "未发售", "coming soon", "tba", "待定", "upcoming"]
    if any(marker in text for marker in unreleased_markers):
        return False
    return any(marker in text for marker in ["已发售", "released", "年", "202", "201", "抢先体验", "early access"])


def _clean_rule_value(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"未获取", "未确认", "暂无", "资料不足", "None", "nan", "[]"} else text


def _parse_int(value) -> int:
    text = str(value or "").replace(",", "").strip()
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return 0


def candidate_pool_display_data(data: pd.DataFrame, show_full: bool = False) -> pd.DataFrame:
    if data.empty:
        base_columns = POOL_FULL_TABLE_COLUMNS if show_full else POOL_TABLE_COLUMNS
        return pd.DataFrame(columns=[CANDIDATE_POOL_FIELD_LABELS.get(column, column) for column in base_columns])
    suggested = apply_candidate_data_status(apply_auto_suggestions(data))
    base_columns = POOL_FULL_TABLE_COLUMNS if show_full else POOL_TABLE_COLUMNS
    columns = [column for column in base_columns if column in suggested.columns]
    display = suggested.loc[:, columns].copy()
    display_source = suggested.reset_index(drop=True)
    if "game_name" in display.columns:
        display["game_name"] = [
            _display_game_name_or_appid(row.to_dict(), value)
            for value, (_, row) in zip(display["game_name"], display_source.iterrows())
        ]
    for column in ["developer", "publisher", "release_status", "has_demo", "supports_schinese"]:
        if column in display.columns:
            display[column] = display[column].map(_display_or_insufficient)
    if "next_action" in display.columns:
        display["next_action"] = [
            _display_next_action(row.to_dict(), value)
            for value, (_, row) in zip(display["next_action"], display_source.iterrows())
        ]
    display = display.fillna("").astype(str)
    return display.rename(columns=CANDIDATE_POOL_FIELD_LABELS)


def apply_candidate_data_status(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    if output.empty:
        for column in ["data_completeness", "missing_items"]:
            if column not in output.columns:
                output[column] = ""
        return output
    for column in CANDIDATE_POOL_COLUMNS:
        if column not in output.columns:
            output[column] = ""
    completeness = []
    missing_items = []
    for _, row in output.iterrows():
        status = build_candidate_data_status(row.to_dict())
        completeness.append(status["data_completeness"])
        missing_items.append(status["missing_items"])
    output["data_completeness"] = completeness
    output["missing_items"] = missing_items
    return output


def build_candidate_data_status(row: dict) -> dict:
    missing = []
    if is_appid_placeholder_record(row):
        missing.extend(["基础信息", "开发商/发行商", "发售状态"])
    else:
        for label, key in [
            ("开发商", "developer"),
            ("发行商", "publisher"),
            ("发售状态", "release_status"),
            ("标签", "genres_tags"),
            ("简中", "supports_schinese"),
        ]:
            if not _clean_rule_value(row.get(key)):
                missing.append(label)
    if not _clean_rule_value(row.get("has_demo")):
        missing.append("Demo 状态")
    if _parse_int(row.get("review_count")) <= 0:
        missing.append("评论")
    if not _clean_rule_value(row.get("latest_news_date")):
        missing.append("公告")
    if not (_clean_rule_value(row.get("market_data_source")) or _clean_rule_value(row.get("market_data_date"))):
        missing.append("第三方市场")

    core_missing = {item for item in missing if item in {"基础信息", "开发商/发行商", "开发商", "发行商", "发售状态", "标签", "简中"}}
    if not core_missing and len(missing) <= 2:
        completeness = "高"
    elif len(core_missing) <= 2 and not is_appid_placeholder_record(row):
        completeness = "中"
    else:
        completeness = "低"
    return {
        "data_completeness": completeness,
        "missing_items": "、".join(dict.fromkeys(missing)) if missing else "无明显缺失",
    }


def is_appid_placeholder_record(row: dict) -> bool:
    appid = str(row.get("appid", "") or "").strip()
    game_name = str(row.get("game_name", "") or "").strip()
    developer = _clean_rule_value(row.get("developer"))
    publisher = _clean_rule_value(row.get("publisher"))
    release_status = _clean_rule_value(row.get("release_status") or row.get("release_date"))
    name_is_placeholder = not game_name or bool(re.fullmatch(r"AppID\s+\d+", game_name, flags=re.IGNORECASE))
    return bool(appid and name_is_placeholder and not developer and not publisher and not release_status)


def _display_game_name_or_appid(row: dict, value) -> str:
    text = str(value or "").strip()
    appid = str(row.get("appid", "") or "").strip()
    if (not text or re.fullmatch(r"AppID\s+\d+", text, flags=re.IGNORECASE)) and appid:
        return f"AppID {appid}"
    return text or "资料不足"


def _display_next_action(row: dict, value) -> str:
    text = str(value or "").strip()
    if is_appid_placeholder_record(row):
        return "补项目画像"
    return text or "补项目画像"


def _display_or_insufficient(value) -> str:
    text = str(value or "").strip()
    if not text or text in {"未获取", "未确认", "None", "nan", "[]"}:
        return "资料不足"
    return text


def candidate_pool_options(data: pd.DataFrame) -> list[dict]:
    options = []
    for _, row in data.iterrows():
        name = str(row.get("game_name", "") or "").strip() or "未命名候选"
        appid = str(row.get("appid", "") or "").strip() or "无 AppID"
        stage = str(row.get("stage", "") or "新发现").strip()
        priority = str(row.get("priority", "") or "未定").strip()
        candidate_id = str(row.get("candidate_id", "") or "").strip()
        label = f"{name} | {appid} | {stage} | {priority}"
        options.append({"label": label, "candidate_id": candidate_id, "row": row})
    return options


def export_candidate_pool_to_excel(csv_path: Path, export_dir: Path) -> Path:
    data = apply_candidate_data_status(load_candidate_pool(csv_path))
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / f"candidate_pool_{datetime.now().strftime('%Y%m%d')}.xlsx"

    def readable(frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            frame = pd.DataFrame(columns=EXPORT_COLUMNS)
        columns = [column for column in EXPORT_COLUMNS if column in frame.columns]
        return frame.loc[:, columns].rename(columns=CANDIDATE_POOL_FIELD_LABELS)

    sheets = {
        "全部候选": data,
        "高优先级": data.loc[data["priority"].astype(str).eq("高")],
        "待试玩": data.loc[data["stage"].astype(str).eq("待试玩")],
        "值得联系": data.loc[data["stage"].astype(str).eq("值得联系")],
        "已放弃": data.loc[data["stage"].astype(str).eq("放弃")],
    }
    with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
        for sheet_name, frame in sheets.items():
            readable(frame).to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.book[sheet_name]
            worksheet.freeze_panes = "A2"
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 36)
    return export_path


def export_daily_candidate_report(csv_path: Path, export_dir: Path, market_data_csv_path: Path | None = None) -> Path:
    data = apply_candidate_data_status(_attach_market_data_summary(apply_auto_suggestions(load_candidate_pool(csv_path)), market_data_csv_path))
    export_dir.mkdir(parents=True, exist_ok=True)
    today_text = datetime.now().strftime("%Y%m%d")
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    export_path = export_dir / f"daily_candidate_report_{today_text}.xlsx"

    stage = data["stage"].astype(str) if "stage" in data.columns else pd.Series([], dtype=str)
    priority = data["priority"].astype(str) if "priority" in data.columns else pd.Series([], dtype=str)
    has_demo = data["has_demo"].astype(str) if "has_demo" in data.columns else pd.Series([], dtype=str)
    created_at = data["created_at"].astype(str) if "created_at" in data.columns else pd.Series([], dtype=str)

    sheets = {
        "今日新增": data.loc[created_at.str.startswith(today_prefix)] if not data.empty else data,
        "待处理": data.loc[stage.isin(["新发现", "待补资料", "待开发商调查"])] if not data.empty else data,
        "待试玩": data.loc[stage.eq("待试玩") | has_demo.eq("是")] if not data.empty else data,
        "值得联系": data.loc[stage.eq("值得联系") | priority.eq("高")] if not data.empty else data,
        "放弃_暂缓": data.loc[stage.isin(["放弃", "暂缓"])] if not data.empty else data,
        "全部候选": data,
    }
    with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
        for sheet_name, frame in sheets.items():
            _daily_report_readable(frame).to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.book[sheet_name]
            worksheet.freeze_panes = "A2"
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 40)
    return export_path


def _daily_report_readable(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        frame = pd.DataFrame(columns=EXPORT_COLUMNS)
    columns = [column for column in EXPORT_COLUMNS if column in frame.columns]
    readable = frame.loc[:, columns].copy()
    for column in ["developer", "publisher", "release_status", "has_demo", "supports_schinese"]:
        if column in readable.columns:
            readable[column] = readable[column].map(_display_or_insufficient)
    return readable.rename(columns=CANDIDATE_POOL_FIELD_LABELS)


def _attach_market_data_summary(data: pd.DataFrame, market_data_csv_path: Path | None) -> pd.DataFrame:
    output = data.copy()
    if market_data_csv_path is None or output.empty or not market_data_csv_path.exists():
        return output
    try:
        market = pd.read_csv(market_data_csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except (OSError, pd.errors.EmptyDataError):
        return output
    if market.empty or "appid" not in market.columns:
        return output
    for column in ["data_date", "updated_at"]:
        if column not in market.columns:
            market[column] = ""
    market = market.sort_values(["data_date", "updated_at"], ascending=False)
    latest = market.drop_duplicates(subset=["appid"], keep="first").set_index("appid")
    for index, row in output.iterrows():
        appid = str(row.get("appid", "") or "").strip()
        if not appid or appid not in latest.index:
            continue
        item = latest.loc[appid]
        output.loc[index, "market_data_source"] = item.get("source", "")
        output.loc[index, "market_data_date"] = item.get("data_date", "")
        output.loc[index, "steamdb_followers"] = item.get("followers", "")
        output.loc[index, "steamdb_peak_ccu"] = item.get("peak_24h", "") or item.get("all_time_peak", "")
        output.loc[index, "peak_ccu"] = item.get("peak_24h", "") or item.get("all_time_peak", "")
        output.loc[index, "vgi_units"] = item.get("estimated_sales", "")
        output.loc[index, "gamalytic_owners"] = item.get("estimated_owners_mid", "") or item.get("estimated_owners_low", "")
    return output
