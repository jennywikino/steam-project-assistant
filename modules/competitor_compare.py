from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd


COMPETITOR_COLUMNS = [
    "created_at",
    "target_appid",
    "target_game_name",
    "competitor_name",
    "competitor_steam_url",
    "competitor_appid",
    "competitor_developer",
    "competitor_publisher",
    "competitor_release_status",
    "competitor_price",
    "competitor_review_count",
    "competitor_positive_rate",
    "competitor_has_demo",
    "competitor_has_simplified_chinese",
    "competitor_tags",
    "competitor_core_loop",
    "competitor_selling_points",
    "competitor_weaknesses",
    "comparison_notes",
]


COMPETITOR_FIELD_LABELS = {
    "created_at": "创建时间",
    "target_appid": "目标游戏 AppID",
    "target_game_name": "目标游戏",
    "competitor_name": "竞品游戏",
    "competitor_steam_url": "竞品 Steam 链接",
    "competitor_appid": "竞品 AppID",
    "competitor_developer": "竞品开发商",
    "competitor_publisher": "竞品发行商",
    "competitor_release_status": "竞品发售状态",
    "competitor_price": "价格",
    "competitor_review_count": "评测数",
    "competitor_positive_rate": "好评率",
    "competitor_has_demo": "是否有 Demo",
    "competitor_has_simplified_chinese": "是否支持简体中文",
    "competitor_tags": "标签",
    "competitor_core_loop": "核心玩法",
    "competitor_selling_points": "主要卖点",
    "competitor_weaknesses": "主要弱点",
    "comparison_notes": "参考意义",
}


COMPETITOR_FIELD_DESCRIPTIONS = {
    "created_at": "竞品记录创建时间。",
    "target_appid": "对应目标游戏的 Steam AppID。",
    "target_game_name": "对应目标游戏名称。",
    "competitor_name": "竞品游戏名称。",
    "competitor_steam_url": "竞品 Steam 商店页链接。",
    "competitor_appid": "竞品 Steam AppID。",
    "competitor_developer": "竞品开发商。",
    "competitor_publisher": "竞品发行商。",
    "competitor_release_status": "竞品当前发售状态。",
    "competitor_price": "手动记录的竞品价格。",
    "competitor_review_count": "手动记录的竞品评测数。",
    "competitor_positive_rate": "手动记录的竞品好评率。",
    "competitor_has_demo": "竞品是否有 Demo。",
    "competitor_has_simplified_chinese": "竞品是否支持简体中文。",
    "competitor_tags": "竞品类型、题材或商店标签。",
    "competitor_core_loop": "竞品核心玩法概述。",
    "competitor_selling_points": "竞品主要卖点。",
    "competitor_weaknesses": "竞品主要弱点。",
    "comparison_notes": "该竞品对目标项目的参考意义。",
}


COMPETITOR_HISTORY_COLUMNS = [
    "target_game_name",
    "competitor_name",
    "competitor_price",
    "competitor_review_count",
    "competitor_positive_rate",
    "competitor_has_demo",
    "competitor_has_simplified_chinese",
    "competitor_tags",
    "competitor_core_loop",
    "competitor_selling_points",
    "competitor_weaknesses",
    "comparison_notes",
]


COMPACT_COMPETITOR_HISTORY_COLUMNS = [
    "target_game_name",
    "competitor_name",
    "competitor_appid",
    "competitor_release_status",
    "competitor_price",
    "competitor_review_count",
    "competitor_positive_rate",
    "competitor_has_demo",
    "competitor_has_simplified_chinese",
]


@dataclass
class CompetitorRecord:
    """保存一条手动录入的竞品对照记录。"""

    target_appid: str = ""
    target_game_name: str = ""
    competitor_name: str = ""
    competitor_steam_url: str = ""
    competitor_appid: str = ""
    competitor_developer: str = ""
    competitor_publisher: str = ""
    competitor_release_status: str = ""
    competitor_price: str = ""
    competitor_review_count: str = ""
    competitor_positive_rate: str = ""
    competitor_has_demo: str = ""
    competitor_has_simplified_chinese: str = ""
    competitor_tags: str = ""
    competitor_core_loop: str = ""
    competitor_selling_points: str = ""
    competitor_weaknesses: str = ""
    comparison_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def competitor_to_dict(record: CompetitorRecord) -> dict:
    """把竞品记录转换为按 CSV 字段排序的字典。"""
    raw_data = asdict(record)
    return {column: raw_data.get(column, "") for column in COMPETITOR_COLUMNS}


def ensure_competitor_csv_exists(csv_path: Path) -> None:
    """确保竞品 CSV 存在，并为旧文件自动补齐字段。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=COMPETITOR_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing_data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=COMPETITOR_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    missing_columns = [column for column in COMPETITOR_COLUMNS if column not in existing_data.columns]
    if not missing_columns:
        return

    for column in missing_columns:
        existing_data[column] = ""

    extra_columns = [column for column in existing_data.columns if column not in COMPETITOR_COLUMNS]
    ordered_columns = COMPETITOR_COLUMNS + extra_columns
    existing_data.to_csv(csv_path, columns=ordered_columns, index=False, encoding="utf-8-sig")


def load_competitors(csv_path: Path) -> pd.DataFrame:
    """读取竞品 CSV，并兼容旧数据缺列。"""
    ensure_competitor_csv_exists(csv_path)
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COMPETITOR_COLUMNS)


def save_competitor_to_csv(record: CompetitorRecord, csv_path: Path) -> Path:
    """把竞品记录追加保存到 CSV 文件。"""
    ensure_competitor_csv_exists(csv_path)
    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    record_data = competitor_to_dict(record)
    row_data = {column: record_data.get(column, "") for column in existing_columns}
    row = pd.DataFrame([row_data], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def filter_competitors(
    competitors: pd.DataFrame,
    target_appid: str = "",
    target_game_name: str = "",
) -> pd.DataFrame:
    """按目标 AppID 或目标游戏名筛选竞品记录。"""
    if competitors.empty:
        return competitors.copy()

    appid = str(target_appid).strip()
    game_name = str(target_game_name).strip()
    mask = pd.Series(False, index=competitors.index)

    if appid:
        mask = mask | (competitors["target_appid"].astype(str).str.strip() == appid)
    if game_name:
        mask = mask | (
            competitors["target_game_name"].astype(str).str.strip().str.casefold()
            == game_name.casefold()
        )

    return competitors.loc[mask].copy()


def get_competitor_display_data(
    csv_path: Path,
    target_appid: str = "",
    target_game_name: str = "",
    show_full: bool = False,
) -> pd.DataFrame:
    """生成页面展示用的中文竞品记录表。"""
    competitors = filter_competitors(load_competitors(csv_path), target_appid, target_game_name)
    history_columns = COMPETITOR_HISTORY_COLUMNS if show_full else COMPACT_COMPETITOR_HISTORY_COLUMNS
    display_columns = [column for column in history_columns if column in competitors.columns]
    display_data = competitors.loc[:, display_columns].copy()
    return display_data.rename(columns=COMPETITOR_FIELD_LABELS)


def markdown_table_for_competitors(competitors: pd.DataFrame) -> str:
    """把竞品记录转换为 Markdown 表格。"""
    if competitors.empty:
        return "暂无记录"

    display_columns = [column for column in COMPETITOR_HISTORY_COLUMNS if column in competitors.columns]
    table_data = competitors.loc[:, display_columns].rename(columns=COMPETITOR_FIELD_LABELS)
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


def summarize_competitor_compare(project_data: dict) -> str:
    """返回竞品对照的简单占位摘要。"""
    return project_data.get("comparison_notes", "") or "暂无竞品对照摘要。"
