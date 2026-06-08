from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font

from modules.competitor_candidate import (
    CANDIDATE_COLUMNS,
    CANDIDATE_FIELD_DESCRIPTIONS,
    CANDIDATE_FIELD_LABELS,
    load_candidates,
)
from modules.competitor_compare import (
    COMPETITOR_COLUMNS,
    COMPETITOR_FIELD_DESCRIPTIONS,
    COMPETITOR_FIELD_LABELS,
    load_competitors,
)
from modules.daily_watch import DAILY_WATCH_FIELD_LABELS, load_daily_watch_notes
from modules.home_snapshots import (
    HOME_SNAPSHOT_EXPORT_COLUMNS,
    HOME_SNAPSHOT_FIELD_LABELS,
    load_home_snapshots,
)
from modules.project_card import CSV_COLUMNS, FIELD_DESCRIPTIONS, FIELD_LABELS, load_projects
from modules.steamdb_discovery import (
    TEMPLATE_FIELD_LABELS,
    WATCH_NOTE_FIELD_LABELS,
    load_templates,
    load_watch_notes,
)
from modules.steam_store_feed_fetcher import load_steam_store_feed_export_rows
from modules.steam_appdetails_cache import load_cached_appdetails_summaries
from modules.steam_review_stats import load_cached_review_stats


STEAM_HOME_FEED_EXPORT_COLUMNS = [
    "source_group",
    "search_source_filter",
    "appid",
    "game_name",
    "developer",
    "publisher",
    "release_date",
    "genres",
    "categories",
    "price",
    "supports_schinese",
    "has_demo",
    "review_summary",
    "review_total",
    "review_positive",
    "review_negative",
    "positive_rate",
    "review_score_desc",
    "sample_review_count",
    "median_playtime_hours",
    "avg_playtime_hours",
    "review_stats_status",
    "image_url",
    "appdetails_status",
    "cache_status",
    "steam_url",
    "fetched_at",
    "steam_page_date",
    "tags",
    "detail_fetch_status",
]

STEAM_HOME_FEED_FIELD_LABELS = {
    "source_group": "来源分组",
    "search_source_filter": "搜索源 filter",
    "appid": "AppID",
    "game_name": "游戏名",
    "developer": "开发商",
    "publisher": "发行商",
    "release_date": "发售日期",
    "genres": "类型",
    "categories": "分类",
    "price": "价格",
    "supports_schinese": "是否支持简中",
    "has_demo": "是否有 Demo",
    "review_summary": "评价摘要",
    "review_total": "评测数",
    "review_positive": "正评数",
    "review_negative": "差评数",
    "positive_rate": "好评率",
    "review_score_desc": "Steam 评测摘要",
    "sample_review_count": "评测样本数",
    "median_playtime_hours": "中位游玩时间（评测样本）",
    "avg_playtime_hours": "平均游玩时间（评测样本）",
    "review_stats_status": "评价数据状态",
    "image_url": "图片 URL",
    "appdetails_status": "Appdetails 状态",
    "cache_status": "缓存状态",
    "steam_url": "Steam 链接",
    "fetched_at": "获取时间",
    "steam_page_date": "Steam 上架日期 / 页面创建日期",
    "tags": "标签",
    "detail_fetch_status": "详情获取状态",
}


def build_field_description_data() -> pd.DataFrame:
    """生成字段说明 sheet 的数据。"""
    rows = []
    rows.extend(_build_description_rows("projects.csv", CSV_COLUMNS, FIELD_LABELS, FIELD_DESCRIPTIONS))
    rows.extend(
        _build_description_rows(
            "competitors.csv",
            COMPETITOR_COLUMNS,
            COMPETITOR_FIELD_LABELS,
            COMPETITOR_FIELD_DESCRIPTIONS,
        )
    )
    rows.extend(
        _build_description_rows(
            "competitor_candidates.csv",
            CANDIDATE_COLUMNS,
            CANDIDATE_FIELD_LABELS,
            CANDIDATE_FIELD_DESCRIPTIONS,
        )
    )
    rows.extend(_build_description_rows("home_snapshots.csv", HOME_SNAPSHOT_EXPORT_COLUMNS, HOME_SNAPSHOT_FIELD_LABELS, {}))
    rows.extend(_build_description_rows("steam_home_feed_cache.json", STEAM_HOME_FEED_EXPORT_COLUMNS, STEAM_HOME_FEED_FIELD_LABELS, {}))
    return pd.DataFrame(rows)


def _build_description_rows(file_name: str, columns: list[str], labels: dict, descriptions: dict) -> list[dict]:
    """生成单个数据文件的字段说明行。"""
    return [
        {
            "数据文件": file_name,
            "英文列名": field_name,
            "中文列名": labels.get(field_name, field_name),
            "用途说明": descriptions.get(field_name, ""),
        }
        for field_name in columns
    ]


def apply_sheet_style(worksheet) -> None:
    """设置首行、冻结窗格、自动换行和列宽。"""
    worksheet.freeze_panes = "A2"

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")

    created_at_columns = set()
    for cell in worksheet[1]:
        if str(cell.value).strip() in {"created_at", "创建时间"}:
            created_at_columns.add(cell.column_letter)

    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if cell.column_letter in created_at_columns and cell.row > 1:
                cell.number_format = "@"
                cell.value = "" if cell.value is None else str(cell.value)

    for column_cells in worksheet.columns:
        column_letter = column_cells[0].column_letter
        max_length = 0
        for cell in column_cells:
            cell_value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(cell_value))

        min_width = 20 if column_letter in created_at_columns else 12
        worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, min_width), 40)


def _as_readable_projects(projects: pd.DataFrame) -> pd.DataFrame:
    """把项目数据转换为 Excel 可读列名和文本时间。"""
    readable = projects.copy()
    if "created_at" in readable.columns:
        readable["created_at"] = readable["created_at"].astype(str)
    return readable.rename(columns=FIELD_LABELS)


def export_projects_to_excel(
    csv_path: Path,
    excel_path: Path,
    competitor_csv_path: Path | None = None,
    candidate_csv_path: Path | None = None,
    steamdb_watch_csv_path: Path | None = None,
    steamdb_template_csv_path: Path | None = None,
    daily_watch_csv_path: Path | None = None,
    home_snapshot_csv_path: Path | None = None,
    steam_home_feed_cache_path: Path | None = None,
    steam_appdetails_cache_path: Path | None = None,
    steam_review_stats_cache_path: Path | None = None,
) -> Path:
    """把原始 CSV 导出为中文可读 Excel。"""
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    active_projects = load_projects(csv_path, include_deleted=False)
    deleted_projects = load_projects(csv_path, include_deleted=True)
    deleted_projects = deleted_projects.loc[
        deleted_projects["is_deleted"].astype(str).str.casefold() == "true"
    ].copy()

    readable_projects = _as_readable_projects(active_projects)
    readable_deleted_projects = _as_readable_projects(deleted_projects)

    if competitor_csv_path is None:
        competitors = pd.DataFrame(columns=COMPETITOR_COLUMNS)
    else:
        competitors = load_competitors(competitor_csv_path)
    readable_competitors = competitors.rename(columns=COMPETITOR_FIELD_LABELS)

    if candidate_csv_path is None:
        candidates = pd.DataFrame(columns=CANDIDATE_COLUMNS)
    else:
        candidates = load_candidates(candidate_csv_path)
    readable_candidates = candidates.rename(columns=CANDIDATE_FIELD_LABELS)

    if steamdb_watch_csv_path is None:
        steamdb_watch_notes = pd.DataFrame(columns=WATCH_NOTE_FIELD_LABELS.keys())
    else:
        steamdb_watch_notes = load_watch_notes(steamdb_watch_csv_path)
    readable_steamdb_watch_notes = steamdb_watch_notes.rename(columns=WATCH_NOTE_FIELD_LABELS)

    if steamdb_template_csv_path is None:
        steamdb_templates = pd.DataFrame(columns=TEMPLATE_FIELD_LABELS.keys())
    else:
        steamdb_templates = load_templates(steamdb_template_csv_path)
    readable_steamdb_templates = steamdb_templates.rename(columns=TEMPLATE_FIELD_LABELS)

    if daily_watch_csv_path is None:
        daily_watch_notes = pd.DataFrame(columns=DAILY_WATCH_FIELD_LABELS.keys())
    else:
        daily_watch_notes = load_daily_watch_notes(daily_watch_csv_path)
    readable_daily_watch_notes = daily_watch_notes.rename(columns=DAILY_WATCH_FIELD_LABELS)

    if home_snapshot_csv_path is None:
        home_snapshots = pd.DataFrame(columns=HOME_SNAPSHOT_EXPORT_COLUMNS)
    else:
        home_snapshots = load_home_snapshots(home_snapshot_csv_path)
        home_snapshots = home_snapshots.loc[
            :,
            [column for column in HOME_SNAPSHOT_EXPORT_COLUMNS if column in home_snapshots.columns],
        ].copy()
    readable_home_snapshots = home_snapshots.rename(columns=HOME_SNAPSHOT_FIELD_LABELS)

    if steam_home_feed_cache_path is None:
        steam_home_feed = pd.DataFrame(columns=STEAM_HOME_FEED_EXPORT_COLUMNS)
    else:
        steam_home_feed = pd.DataFrame(load_steam_store_feed_export_rows(steam_home_feed_cache_path))
        if steam_appdetails_cache_path is not None:
            details = load_cached_appdetails_summaries(steam_appdetails_cache_path)
            if not steam_home_feed.empty and "appid" in steam_home_feed.columns:
                for index, row in steam_home_feed.iterrows():
                    detail = details.get(str(row.get("appid", "")).strip(), {})
                    steam_home_feed.loc[index, "developer"] = detail.get("developer", "")
                    steam_home_feed.loc[index, "publisher"] = detail.get("publisher", "")
                    steam_home_feed.loc[index, "release_date"] = detail.get("release_date") or row.get("release_date", "")
                    steam_home_feed.loc[index, "steam_page_date"] = detail.get("steam_page_date", "未获取")
                    steam_home_feed.loc[index, "genres"] = detail.get("genres_text", "")
                    steam_home_feed.loc[index, "categories"] = detail.get("categories_text", "")
                    steam_home_feed.loc[index, "tags"] = detail.get("tags_text", "未获取")
                    steam_home_feed.loc[index, "price"] = detail.get("price") or row.get("price", "")
                    steam_home_feed.loc[index, "has_demo"] = detail.get("has_demo", "")
                    steam_home_feed.loc[index, "supports_schinese"] = detail.get("supports_schinese", "")
                    steam_home_feed.loc[index, "detail_fetch_status"] = detail.get("detail_fetch_status", "")
                    steam_home_feed.loc[index, "appdetails_status"] = detail.get("detail_fetch_status", "")
                    steam_home_feed.loc[index, "cache_status"] = detail.get("cache_status", "")
        if steam_review_stats_cache_path is not None:
            review_stats = load_cached_review_stats(steam_review_stats_cache_path)
            if not steam_home_feed.empty and "appid" in steam_home_feed.columns:
                for index, row in steam_home_feed.iterrows():
                    reviews = review_stats.get(str(row.get("appid", "")).strip(), {})
                    for column in [
                        "review_total",
                        "review_positive",
                        "review_negative",
                        "positive_rate",
                        "review_score_desc",
                        "sample_review_count",
                        "median_playtime_hours",
                        "avg_playtime_hours",
                        "review_stats_status",
                    ]:
                        steam_home_feed.loc[index, column] = reviews.get(column, "")
        for column in STEAM_HOME_FEED_EXPORT_COLUMNS:
            if column not in steam_home_feed.columns:
                steam_home_feed[column] = ""
        steam_home_feed = steam_home_feed.loc[:, STEAM_HOME_FEED_EXPORT_COLUMNS].copy()
    readable_steam_home_feed = steam_home_feed.rename(columns=STEAM_HOME_FEED_FIELD_LABELS)

    field_descriptions = build_field_description_data()

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        readable_projects.to_excel(writer, sheet_name="项目总表", index=False)
        readable_deleted_projects.to_excel(writer, sheet_name="已删除项目", index=False)
        readable_competitors.to_excel(writer, sheet_name="竞品对照", index=False)
        readable_candidates.to_excel(writer, sheet_name="竞品候选池", index=False)
        readable_steamdb_watch_notes.to_excel(writer, sheet_name="SteamDB观察", index=False)
        readable_steamdb_templates.to_excel(writer, sheet_name="SteamDB模板", index=False)
        readable_daily_watch_notes.to_excel(writer, sheet_name="今日观察", index=False)
        readable_home_snapshots.to_excel(writer, sheet_name="首页快照", index=False)
        readable_steam_home_feed.to_excel(writer, sheet_name="首页Steam图文源", index=False)
        field_descriptions.to_excel(writer, sheet_name="字段说明", index=False)

        for sheet_name in [
            "项目总表",
            "已删除项目",
            "竞品对照",
            "竞品候选池",
            "SteamDB观察",
            "SteamDB模板",
            "今日观察",
            "首页快照",
            "首页Steam图文源",
            "字段说明",
        ]:
            apply_sheet_style(writer.book[sheet_name])

    return excel_path
