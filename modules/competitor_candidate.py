import itertools
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd


CANDIDATE_COLUMNS = [
    "created_at",
    "target_game_name",
    "target_appid",
    "candidate_name",
    "candidate_steam_url",
    "candidate_appid",
    "source_keyword",
    "source_type",
    "candidate_price",
    "candidate_release_date",
    "candidate_review_summary",
    "candidate_tags",
    "match_score",
    "match_level",
    "match_reason",
    "user_decision",
    "notes",
]


CANDIDATE_FIELD_LABELS = {
    "created_at": "创建时间",
    "target_game_name": "目标游戏",
    "target_appid": "目标 AppID",
    "candidate_name": "候选游戏",
    "candidate_steam_url": "候选 Steam 链接",
    "candidate_appid": "候选 AppID",
    "source_keyword": "来源关键词",
    "source_type": "来源类型",
    "candidate_price": "候选价格",
    "candidate_release_date": "候选发售日",
    "candidate_review_summary": "候选评价摘要",
    "candidate_tags": "候选标签",
    "match_score": "匹配分数",
    "match_level": "匹配等级",
    "match_reason": "匹配理由",
    "user_decision": "用户决策",
    "notes": "备注",
}


CANDIDATE_FIELD_DESCRIPTIONS = {
    "created_at": "候选记录创建时间。",
    "target_game_name": "候选对应的目标游戏名称。",
    "target_appid": "候选对应的目标游戏 AppID。",
    "candidate_name": "候选竞品游戏名称。",
    "candidate_steam_url": "候选游戏 Steam 商店页链接。",
    "candidate_appid": "候选游戏 Steam AppID。",
    "source_keyword": "自动发现候选时使用的 Steam 搜索关键词。",
    "source_type": "候选来源，例如标签搜索、关键词搜索或用户手动添加。",
    "candidate_price": "Steam 搜索页展示的候选价格，可能为空。",
    "candidate_release_date": "Steam 搜索页展示的候选发售日，可能为空。",
    "candidate_review_summary": "Steam 搜索页展示的候选评价摘要，可能为空。",
    "candidate_tags": "Steam 搜索页展示的候选标签，可能为空。",
    "match_score": "自动候选评分，0-100，仅用于排序和人工筛选。",
    "match_level": "自动候选等级：高、中、低。",
    "match_reason": "为什么这个游戏可能是竞品。",
    "user_decision": "用户对候选的处理状态：待确认、采纳或排除。",
    "notes": "候选相关备注。",
}


CANDIDATE_HISTORY_COLUMNS = [
    "target_game_name",
    "candidate_name",
    "candidate_steam_url",
    "candidate_appid",
    "source_keyword",
    "source_type",
    "candidate_price",
    "candidate_release_date",
    "candidate_review_summary",
    "candidate_tags",
    "match_score",
    "match_level",
    "match_reason",
    "user_decision",
    "notes",
]


COMPACT_CANDIDATE_HISTORY_COLUMNS = [
    "target_game_name",
    "candidate_name",
    "candidate_appid",
    "source_type",
    "user_decision",
]


@dataclass
class CompetitorCandidate:
    """保存一条竞品候选记录。"""

    target_game_name: str = ""
    target_appid: str = ""
    candidate_name: str = ""
    candidate_steam_url: str = ""
    candidate_appid: str = ""
    source_keyword: str = ""
    source_type: str = "用户手动添加"
    candidate_price: str = ""
    candidate_release_date: str = ""
    candidate_review_summary: str = ""
    candidate_tags: str = ""
    match_score: str = ""
    match_level: str = ""
    match_reason: str = ""
    user_decision: str = "待确认"
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def candidate_to_dict(candidate: CompetitorCandidate) -> dict:
    """把候选记录转换为按 CSV 字段排序的字典。"""
    raw_data = asdict(candidate)
    return {column: raw_data.get(column, "") for column in CANDIDATE_COLUMNS}


def ensure_candidate_csv_exists(csv_path: Path) -> None:
    """确保候选 CSV 存在，并为旧文件自动补齐字段。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=CANDIDATE_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing_data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=CANDIDATE_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    missing_columns = [column for column in CANDIDATE_COLUMNS if column not in existing_data.columns]
    if not missing_columns:
        return

    for column in missing_columns:
        existing_data[column] = ""

    extra_columns = [column for column in existing_data.columns if column not in CANDIDATE_COLUMNS]
    ordered_columns = CANDIDATE_COLUMNS + extra_columns
    existing_data.to_csv(csv_path, columns=ordered_columns, index=False, encoding="utf-8-sig")


def load_candidates(csv_path: Path) -> pd.DataFrame:
    """读取候选 CSV，并兼容旧数据缺列。"""
    ensure_candidate_csv_exists(csv_path)
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=CANDIDATE_COLUMNS)


def save_candidate_to_csv(candidate: CompetitorCandidate, csv_path: Path) -> Path:
    """把候选记录追加保存到 CSV。"""
    ensure_candidate_csv_exists(csv_path)
    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    candidate_data = candidate_to_dict(candidate)
    row_data = {column: candidate_data.get(column, "") for column in existing_columns}
    row = pd.DataFrame([row_data], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def filter_candidates(
    candidates: pd.DataFrame,
    target_appid: str = "",
    target_game_name: str = "",
    user_decision: str = "全部",
) -> pd.DataFrame:
    """按目标项目和用户决策筛选候选记录。"""
    if candidates.empty:
        return candidates.copy()

    appid = str(target_appid).strip()
    game_name = str(target_game_name).strip()
    mask = pd.Series(False, index=candidates.index)

    if appid:
        mask = mask | (candidates["target_appid"].astype(str).str.strip() == appid)
    if game_name:
        mask = mask | (
            candidates["target_game_name"].astype(str).str.strip().str.casefold()
            == game_name.casefold()
        )
    if not appid and not game_name:
        mask = pd.Series(True, index=candidates.index)

    if user_decision != "全部":
        mask = mask & (candidates["user_decision"].astype(str).str.strip() == user_decision)

    return candidates.loc[mask].copy()


def get_candidate_display_data(
    csv_path: Path,
    target_appid: str = "",
    target_game_name: str = "",
    user_decision: str = "全部",
    show_full: bool = False,
) -> pd.DataFrame:
    """生成页面展示用的中文候选记录表。"""
    candidates = filter_candidates(load_candidates(csv_path), target_appid, target_game_name, user_decision)
    history_columns = CANDIDATE_HISTORY_COLUMNS if show_full else COMPACT_CANDIDATE_HISTORY_COLUMNS
    display_columns = [column for column in history_columns if column in candidates.columns]
    display_data = candidates.loc[:, display_columns].copy()
    return display_data.rename(columns=CANDIDATE_FIELD_LABELS)


def markdown_table_for_candidates(candidates: pd.DataFrame) -> str:
    """把候选记录转换为 Markdown 表格。"""
    if candidates.empty:
        return "暂无记录"

    display_columns = [column for column in CANDIDATE_HISTORY_COLUMNS if column in candidates.columns]
    table_data = candidates.loc[:, display_columns].rename(columns=CANDIDATE_FIELD_LABELS)
    headers = list(table_data.columns)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]

    for _, row in table_data.iterrows():
        values = [_clean_markdown_cell(row.get(header, "")) for header in headers]
        rows.append("| " + " | ".join(values) + " |")

    return "\n".join(rows)


def _clean_markdown_cell(value: str) -> str:
    """清理 Markdown 表格单元格中的换行和竖线。"""
    text = str(value).replace("\n", " ").replace("\r", " ").replace("|", "/").strip()
    return text if text else "未填写"


def update_candidate_decision(csv_path: Path, row_index: int, decision: str) -> Path:
    """更新候选记录的用户决策，不删除原始记录。"""
    candidates = load_candidates(csv_path)
    if row_index not in candidates.index:
        raise IndexError("候选记录不存在。")
    candidates.loc[row_index, "user_decision"] = decision
    candidates.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def build_candidate_options(candidates: pd.DataFrame) -> list[dict]:
    """把候选记录转换为下拉选择项。"""
    options = []
    for row_index, row in candidates.iterrows():
        name = str(row.get("candidate_name", "")).strip() or "未命名候选"
        appid = str(row.get("candidate_appid", "")).strip()
        decision = str(row.get("user_decision", "")).strip() or "待确认"
        label = f"{row_index} | {name} | {appid} | {decision}"
        options.append({"label": label, "row_index": row_index, "row": row})
    return options


def generate_steam_search_links(
    target_game_name: str,
    primary_tags: str,
    gameplay_keywords: str,
    reference_games: str,
    english_keywords: str = "",
) -> list[dict]:
    """根据手动输入生成 Steam 搜索链接。"""
    links = []
    target_name = str(target_game_name).strip()

    tag_terms = clean_search_terms(primary_tags, target_name, split_spaces=True)
    gameplay_terms = clean_search_terms(gameplay_keywords, target_name, split_spaces=True)
    english_terms = clean_search_terms(english_keywords, target_name, split_spaces=False)
    reference_terms = clean_search_terms(reference_games, target_name, remove_target=False, split_spaces=False)

    for term in tag_terms:
        links.append(_build_link("按单关键词搜索", term))
    for term in gameplay_terms:
        links.append(_build_link("按单关键词搜索", term))

    for first, second in itertools.islice(itertools.combinations(tag_terms + gameplay_terms, 2), 5):
        links.append(_build_link("按双关键词组合搜索", f"{first} {second}", f"{first} + {second}"))

    for term in english_terms:
        links.append(_build_link("按英文关键词搜索", term))

    for term in reference_terms:
        links.append(_build_link("按参考游戏搜索", term))

    return links


def clean_search_terms(
    raw_text: str,
    target_game_name: str = "",
    remove_target: bool = True,
    split_spaces: bool = True,
) -> list[str]:
    """清洗搜索词：拆分、去空、去重，并可去掉目标游戏名。"""
    target = str(target_game_name).strip().casefold()
    pattern = r"[\s,，、\n\r]+" if split_spaces else r"[,，、\n\r]+"
    parts = re.split(pattern, str(raw_text))
    cleaned_terms = []
    seen = set()

    for part in parts:
        term = part.strip()
        if not term:
            continue
        normalized = term.casefold()
        if remove_target and target and normalized == target:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned_terms.append(term)

    return cleaned_terms


def _build_link(source_type: str, term: str, display_term: str | None = None) -> dict:
    """生成单条 Steam 搜索链接。"""
    return {
        "source_type": source_type,
        "term": display_term or term,
        "url": f"https://store.steampowered.com/search/?term={quote_plus(term)}",
    }
