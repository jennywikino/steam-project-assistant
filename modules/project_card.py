from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd


CSV_COLUMNS = [
    "record_id",
    "is_deleted",
    "created_at",
    "game_name",
    "steam_url",
    "appid",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "has_simplified_chinese",
    "genre_tags",
    "core_loop",
    "first_impression",
    "china_publishing_opportunity",
    "risks",
    "next_action",
    "demo_played",
    "playtime_minutes",
    "first_5min_experience",
    "first_15min_experience",
    "first_30min_experience",
    "core_loop_clarity",
    "tutorial_issue",
    "control_issue",
    "combat_or_system_issue",
    "localization_issue",
    "performance_issue",
    "content_depth",
    "video_hook",
    "china_player_reaction",
    "demo_conclusion",
]


FIELD_LABELS = {
    "record_id": "记录 ID",
    "is_deleted": "是否已删除",
    "created_at": "创建时间",
    "game_name": "游戏名",
    "steam_url": "Steam 链接",
    "appid": "Steam AppID",
    "developer": "开发商",
    "publisher": "发行商",
    "release_status": "发售状态",
    "has_demo": "是否有 Demo",
    "has_simplified_chinese": "是否支持简体中文",
    "genre_tags": "类型/标签",
    "core_loop": "核心玩法一句话",
    "first_impression": "第一印象",
    "china_publishing_opportunity": "中国区发行机会",
    "risks": "主要风险",
    "next_action": "下一步动作",
    "demo_played": "是否已试玩 Demo",
    "playtime_minutes": "试玩时长分钟",
    "first_5min_experience": "0-5分钟体验",
    "first_15min_experience": "5-15分钟体验",
    "first_30min_experience": "15-30分钟体验",
    "core_loop_clarity": "核心循环是否清晰",
    "tutorial_issue": "新手引导问题",
    "control_issue": "操作/手感问题",
    "combat_or_system_issue": "战斗/系统/经营问题",
    "localization_issue": "本地化问题",
    "performance_issue": "性能/稳定性问题",
    "content_depth": "内容深度判断",
    "video_hook": "视频传播点",
    "china_player_reaction": "中国玩家可能反馈",
    "demo_conclusion": "Demo 试玩结论",
}


FIELD_DESCRIPTIONS = {
    "record_id": "项目记录唯一 ID，用于软删除和恢复。",
    "is_deleted": "软删除标记，True 表示默认隐藏。",
    "created_at": "项目记录创建时间。",
    "game_name": "Steam 项目或游戏名称。",
    "steam_url": "Steam 商店页链接。",
    "appid": "Steam AppID，便于后续检索。",
    "developer": "游戏开发商。",
    "publisher": "游戏发行商。",
    "release_status": "当前发售状态。",
    "has_demo": "商店页是否提供 Demo。",
    "has_simplified_chinese": "是否支持简体中文。",
    "genre_tags": "手动记录的类型、标签或题材关键词。",
    "core_loop": "一句话概括核心玩法循环。",
    "first_impression": "商店页、截图、视频或题材带来的第一印象。",
    "china_publishing_opportunity": "对中国区发行机会的初步判断。",
    "risks": "当前能识别的主要风险。",
    "next_action": "下一步要做的动作。",
    "demo_played": "是否已经试玩 Demo。",
    "playtime_minutes": "Demo 试玩时长，单位为分钟。",
    "first_5min_experience": "试玩 0-5 分钟阶段体验。",
    "first_15min_experience": "试玩 5-15 分钟阶段体验。",
    "first_30min_experience": "试玩 15-30 分钟阶段体验。",
    "core_loop_clarity": "试玩后判断核心循环是否清晰。",
    "tutorial_issue": "新手引导相关问题。",
    "control_issue": "操作、反馈、手感相关问题。",
    "combat_or_system_issue": "战斗、系统、经营或核心机制问题。",
    "localization_issue": "本地化、文本、中文体验问题。",
    "performance_issue": "性能、稳定性、Bug 或兼容问题。",
    "content_depth": "试玩后对内容深度的判断。",
    "video_hook": "是否具备视频传播点或可展示亮点。",
    "china_player_reaction": "中国玩家可能的正负反馈。",
    "demo_conclusion": "Demo 试玩后的初步结论。",
}


COMPACT_HISTORY_COLUMNS = [
    "record_id",
    "created_at",
    "game_name",
    "appid",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "has_simplified_chinese",
    "next_action",
    "demo_conclusion",
]


HISTORY_COLUMNS = [
    "record_id",
    "is_deleted",
    "created_at",
    "game_name",
    "steam_url",
    "appid",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "has_simplified_chinese",
    "genre_tags",
    "core_loop",
    "first_impression",
    "china_publishing_opportunity",
    "risks",
    "next_action",
    "demo_played",
    "playtime_minutes",
    "first_5min_experience",
    "first_15min_experience",
    "first_30min_experience",
    "core_loop_clarity",
    "tutorial_issue",
    "control_issue",
    "combat_or_system_issue",
    "localization_issue",
    "performance_issue",
    "content_depth",
    "video_hook",
    "china_player_reaction",
    "demo_conclusion",
]


@dataclass
class ProjectCard:
    """保存单个 Steam 项目的基础初筛信息和 Demo 试玩记录。"""

    game_name: str = ""
    steam_url: str = ""
    appid: str = ""
    developer: str = ""
    publisher: str = ""
    release_status: str = ""
    has_demo: str = ""
    has_simplified_chinese: str = ""
    genre_tags: str = ""
    core_loop: str = ""
    first_impression: str = ""
    china_publishing_opportunity: str = ""
    risks: str = ""
    next_action: str = ""
    demo_played: str = ""
    playtime_minutes: int = 0
    first_5min_experience: str = ""
    first_15min_experience: str = ""
    first_30min_experience: str = ""
    core_loop_clarity: str = ""
    tutorial_issue: str = ""
    control_issue: str = ""
    combat_or_system_issue: str = ""
    localization_issue: str = ""
    performance_issue: str = ""
    content_depth: str = ""
    video_hook: str = ""
    china_player_reaction: str = ""
    demo_conclusion: str = ""
    record_id: str = field(default_factory=lambda: str(uuid4()))
    is_deleted: str = "False"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def project_to_dict(project: ProjectCard) -> dict:
    """把项目卡片转换为按 CSV 字段排序的字典。"""
    raw_data = asdict(project)
    return {column: raw_data.get(column, "") for column in CSV_COLUMNS}


def ensure_csv_exists(csv_path: Path) -> None:
    """确保 CSV 文件存在，并为旧 CSV 自动补齐新字段。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=CSV_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing_data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=CSV_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in CSV_COLUMNS:
        if column not in existing_data.columns:
            existing_data[column] = ""
            changed = True

    if "record_id" in existing_data.columns:
        empty_ids = existing_data["record_id"].astype(str).str.strip() == ""
        if empty_ids.any():
            existing_data.loc[empty_ids, "record_id"] = [str(uuid4()) for _ in range(int(empty_ids.sum()))]
            changed = True

    if "is_deleted" in existing_data.columns:
        empty_deleted = existing_data["is_deleted"].astype(str).str.strip() == ""
        if empty_deleted.any():
            existing_data.loc[empty_deleted, "is_deleted"] = "False"
            changed = True

    if changed:
        extra_columns = [column for column in existing_data.columns if column not in CSV_COLUMNS]
        ordered_columns = CSV_COLUMNS + extra_columns
        existing_data.to_csv(csv_path, columns=ordered_columns, index=False, encoding="utf-8-sig")


def load_projects(csv_path: Path, include_deleted: bool = False) -> pd.DataFrame:
    """读取项目 CSV，并默认忽略软删除记录。"""
    ensure_csv_exists(csv_path)
    try:
        projects = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        projects = pd.DataFrame(columns=CSV_COLUMNS)

    if include_deleted:
        return projects
    return projects.loc[projects["is_deleted"].astype(str).str.casefold() != "true"].copy()


def filter_projects(
    projects: pd.DataFrame,
    game_name_query: str = "",
    appid_query: str = "",
    release_status: str = "全部",
) -> pd.DataFrame:
    """按游戏名、AppID 和发售状态筛选项目记录。"""
    filtered = projects.copy()
    if game_name_query.strip():
        filtered = filtered[
            filtered["game_name"].astype(str).str.contains(game_name_query.strip(), case=False, na=False)
        ]
    if appid_query.strip():
        filtered = filtered[filtered["appid"].astype(str).str.contains(appid_query.strip(), case=False, na=False)]
    if release_status != "全部":
        filtered = filtered[filtered["release_status"].astype(str) == release_status]
    return filtered


def get_history_display_data(projects: pd.DataFrame, show_full: bool = False) -> pd.DataFrame:
    """生成网页历史记录表格使用的中文列名数据。"""
    display_columns = HISTORY_COLUMNS if show_full else COMPACT_HISTORY_COLUMNS
    display_columns = [column for column in display_columns if column in projects.columns]
    history_data = projects.loc[:, display_columns].copy()
    return history_data.rename(columns=FIELD_LABELS)


def update_project_deleted(csv_path: Path, record_id: str, is_deleted: bool) -> Path:
    """更新项目软删除状态。"""
    projects = load_projects(csv_path, include_deleted=True)
    mask = projects["record_id"].astype(str) == str(record_id)
    if not mask.any():
        raise ValueError("未找到对应项目记录。")
    projects.loc[mask, "is_deleted"] = "True" if is_deleted else "False"
    projects.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def update_project_fields(csv_path: Path, record_id: str, updates: dict) -> Path:
    """按记录 ID 更新项目字段，保持 CSV 字段结构不变。"""
    projects = load_projects(csv_path, include_deleted=True)
    mask = projects["record_id"].astype(str) == str(record_id)
    if not mask.any():
        raise ValueError("未找到对应项目记录。")

    for column, value in updates.items():
        if column in projects.columns:
            projects.loc[mask, column] = value

    projects.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def build_project_action_options(projects: pd.DataFrame) -> list[dict]:
    """把项目记录转换为删除/恢复下拉选项。"""
    options = []
    for _, row in projects.iterrows():
        record_id = str(row.get("record_id", "")).strip()
        game_name = str(row.get("game_name", "")).strip() or "未命名项目"
        appid = str(row.get("appid", "")).strip()
        deleted = str(row.get("is_deleted", "")).strip()
        label = f"{game_name} | {appid} | {deleted} | {record_id}"
        options.append({"label": label, "record_id": record_id})
    return options


def save_project_to_csv(project: ProjectCard, csv_path: Path) -> Path:
    """把项目数据追加保存到 CSV 文件。"""
    ensure_csv_exists(csv_path)

    existing_columns = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns)
    project_data = project_to_dict(project)
    row_data = {column: project_data.get(column, "") for column in existing_columns}
    row = pd.DataFrame([row_data], columns=existing_columns)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path
