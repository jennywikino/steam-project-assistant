from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import re
from uuid import uuid4
from urllib.parse import quote, urlparse
import webbrowser

import pandas as pd
import streamlit as st

from modules.candidate_pool import (
    PRIORITY_OPTIONS,
    STAGE_OPTIONS,
    CandidatePoolRecord,
    apply_auto_suggestions,
    apply_suggestion_to_stage,
    candidate_pool_record_to_dict,
    candidate_pool_display_data,
    candidate_pool_options,
    candidate_pool_summary,
    export_daily_candidate_report,
    export_candidate_pool_to_excel,
    export_candidate_pool_v070_to_excel,
    filter_candidate_pool,
    find_candidate_by_appid,
    ensure_candidate_pool_csv_exists,
    is_appid_placeholder_record,
    is_insufficient_candidate,
    load_candidate_pool,
    parse_candidate_import_lines,
    update_candidate_pool_fields,
    upsert_candidate_pool_record,
)
from modules.competitor_candidate import (
    CompetitorCandidate,
    build_candidate_options,
    ensure_candidate_csv_exists,
    filter_candidates,
    generate_steam_search_links,
    get_candidate_display_data,
    load_candidates,
    save_candidate_to_csv,
    update_candidate_decision,
)
from modules.competitor_compare import (
    CompetitorRecord,
    ensure_competitor_csv_exists,
    filter_competitors,
    get_competitor_display_data,
    load_competitors,
    save_competitor_to_csv,
)
from modules.company_dossier import (
    COMPANY_CONFIDENCE_OPTIONS,
    COMPANY_DOSSIER_FIELD_LABELS,
    COMPANY_ROLE_BY_LABEL,
    COMPANY_ROLE_LABELS,
    COMPANY_ROLE_OPTIONS,
    SELF_PUBLISH_STATUS_OPTIONS,
    CompanyDossierRecord,
    build_company_search_links,
    delete_company_dossier_records,
    display_company_role,
    filter_company_dossiers,
    filter_company_dossiers_for_project,
    latest_company_dossier,
    load_company_dossiers,
    parse_company_names,
    save_company_dossier_to_csv,
    update_company_dossier_record,
)
from modules.daily_watch import (
    DAILY_WATCH_COLUMNS,
    DailyWatchNote,
    ensure_daily_watch_csv_exists,
    load_daily_watch_notes,
    save_daily_watch_note_to_csv,
)
from modules.excel_exporter import export_projects_to_excel
from modules.external_intel import (
    EVIDENCE_TYPE_OPTIONS,
    EXTERNAL_INTEL_FIELD_LABELS,
    PLATFORM_OPTIONS,
    RELEVANCE_OPTIONS,
    SENTIMENT_OPTIONS,
    ExternalIntelRecord,
    delete_external_intel_records,
    duplicate_record_ids_to_delete,
    ensure_external_intel_csv_exists,
    filter_external_intel_library,
    find_duplicate_external_intel,
    filter_external_intel,
    format_count,
    load_external_intel,
    parse_count,
    save_external_intel_to_csv,
    summarize_external_intel,
    update_external_intel_record,
)
from modules.external_title_clue_extractor import (
    extract_external_title_clues,
    fetch_external_title_clues,
)
from modules.project_card import (
    ProjectCard,
    build_project_action_options,
    ensure_csv_exists,
    filter_projects,
    get_history_display_data,
    load_projects,
    save_project_to_csv,
    update_project_deleted,
    update_project_fields,
)
from modules.home_feed_fetcher import (
    HomeFeedItem,
    HomeFeedResult,
    load_home_feed,
)
from modules.new_store_monitor import (
    apply_monitor_suggestions,
    enrich_new_store_events_basic_info,
    fetch_recent_new_store_games,
    filter_new_store_events,
    load_new_store_events,
    new_store_events_display_data,
    save_new_store_events,
)
from modules.home_snapshots import (
    HomeSnapshot,
    ensure_home_snapshot_csv_exists,
    load_home_snapshots,
    save_home_snapshot_to_csv,
    update_home_snapshot_fields,
)
from modules.market_data import (
    MARKET_CONFIDENCE_OPTIONS,
    MARKET_DATA_FIELD_LABELS,
    MARKET_SOURCE_OPTIONS,
    MarketDataRecord,
    build_market_data_external_links,
    filter_market_data,
    find_market_data_duplicate_note,
    format_country_distribution,
    latest_market_data_date,
    load_market_data,
    save_market_data_to_csv,
    summarize_market_data,
)
from modules.project_profile_generator import (
    PLACEHOLDER,
    ProjectProfile,
    build_project_data_status,
    generate_project_profile,
    normalize_availability_status,
    profile_summary_for_project,
    profile_to_markdown,
    profile_to_text,
    save_profile_reports,
)
from modules.report_generator import generate_reports
from modules.search_history import (
    SearchHistoryRecord,
    clear_search_history,
    delete_search_history_record,
    ensure_search_history_csv_exists,
    filter_search_history,
    history_option_label,
    load_search_history,
    search_history_to_prefill,
    upsert_search_history,
)
from modules.search_center_v031b import (
    BATCH_CATEGORY_OPTIONS,
    EXAMPLE_INPUT,
    SEARCH_CENTER_SECTION_ORDER,
    SearchCenterInput,
    build_platform_navigation,
    expand_links_for_display,
    filter_navigation_by_batch_groups,
    load_search_platforms,
    prepare_navigation_for_csv,
)
from modules.steam_competitor_finder import (
    SteamCompetitorCandidate,
    candidate_to_dict as steam_candidate_to_dict,
    find_steam_competitor_candidates,
)
from modules.steam_image_cache import get_cached_steam_image
from modules.steam_news_fetcher import (
    get_steam_news_for_app,
    is_major_update_candidate,
    steam_news_status_label,
)
from modules.steam_review_preview import (
    format_playtime as format_review_preview_playtime,
    get_steam_review_preview,
    steam_review_preview_status_label,
)
from modules.steam_appdetails_cache import (
    clear_invalid_appdetails_cache,
    count_missing_field_cache_entries,
    debug_appdetails_summary,
    get_cached_appdetails_summary,
    load_cached_appdetails_summaries,
)
from modules.steam_app_enricher import enrich_appids_basic
from modules.steam_browser_collector import (
    DEFAULT_STEAM_URL,
    apply_import_suggestions,
    bulk_update_collected_selection,
    browser_is_open,
    clear_collected_csv,
    collect_current_app,
    collect_current_page_appids,
    collected_display_data_v074,
    dedupe_collected_by_appid,
    enrich_collected_basic_info,
    filter_collected,
    launch_browser,
    load_collected,
    playwright_available,
    save_collected_rows,
    update_collected_selection,
)
from modules.steam_search_importer import (
    apply_search_import_suggestions,
    bulk_update_search_import_selection,
    clear_search_imports,
    dedupe_search_imports_by_appid,
    enrich_search_imports_basic_info,
    fetch_steam_search_appids_with_stats,
    filter_search_imports,
    load_search_imports,
    save_search_import_rows,
    search_import_display_data,
    update_search_import_selection,
)
from modules.steam_data_normalizer import normalize_steam_game_data
from modules.steam_review_stats import get_cached_review_stats
from modules.steam_store_feed_fetcher import (
    SteamStoreFeedItem,
    SteamStoreFeedResult,
    load_steam_store_home_feed,
    search_steam_store_items,
)
from modules.steamdb_discovery import (
    SteamDBTemplate,
    SteamDBWatchNote,
    ensure_template_csv_exists,
    ensure_watch_note_csv_exists,
    load_templates,
    load_watch_notes,
    parse_steamdb_appid,
    save_template_to_csv,
    save_watch_note_to_csv,
    steam_url_from_appid,
    steamdb_app_url_from_appid,
    steamdb_quick_links,
)
from modules.steamdb_importer import parse_steamdb_paste
from modules.steam_store_fetcher import parse_appid


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "projects.csv"
COMPETITOR_CSV_PATH = BASE_DIR / "data" / "competitors.csv"
CANDIDATE_CSV_PATH = BASE_DIR / "data" / "competitor_candidates.csv"
CANDIDATE_POOL_CSV_PATH = BASE_DIR / "data" / "candidate_pool.csv"
STEAMDB_TEMPLATE_CSV_PATH = BASE_DIR / "data" / "steamdb_link_templates.csv"
STEAMDB_WATCH_NOTE_CSV_PATH = BASE_DIR / "data" / "steamdb_watch_notes.csv"
NEW_STORE_EVENTS_CSV_PATH = BASE_DIR / "data" / "new_store_events.csv"
STEAM_BROWSER_COLLECTED_CSV_PATH = BASE_DIR / "data" / "steam_browser_collected.csv"
STEAM_SEARCH_IMPORT_CSV_PATH = BASE_DIR / "data" / "steam_search_imports.csv"
STEAM_BROWSER_USER_DATA_DIR = BASE_DIR / "data" / "browser_profiles" / "steam_browser_collector"
STEAM_BROWSER_DEBUG_PORT = 9222
DAILY_WATCH_CSV_PATH = BASE_DIR / "data" / "daily_watch_notes.csv"
HOME_SNAPSHOT_CSV_PATH = BASE_DIR / "data" / "home_snapshots.csv"
EXTERNAL_INTEL_CSV_PATH = BASE_DIR / "data" / "external_intel.csv"
COMPANY_DOSSIER_CSV_PATH = BASE_DIR / "data" / "company_dossier.csv"
MARKET_DATA_CSV_PATH = BASE_DIR / "data" / "market_data.csv"
SEARCH_HISTORY_CSV_PATH = BASE_DIR / "data" / "search_history.csv"
HOME_SNAPSHOT_IMAGE_DIR = BASE_DIR / "data" / "snapshots"
HOME_FEED_CACHE_PATH = BASE_DIR / "data" / "cache" / "home_feed_cache.json"
STEAM_HOME_FEED_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_home_feed_cache.json"
STEAM_SEARCH_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_search_cache.json"
STEAM_NEWS_CACHE_DIR = BASE_DIR / "data" / "cache" / "steam_news"
STEAM_REVIEW_PREVIEW_CACHE_DIR = BASE_DIR / "data" / "cache" / "steam_reviews_preview"
STEAM_IMAGE_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_images_cache.json"
STEAM_APPDETAILS_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_appdetails_cache.json"
STEAM_REVIEW_STATS_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_review_stats_cache.json"
STEAM_COMPETITOR_CACHE_PATH = BASE_DIR / "data" / "cache" / "steam_competitor_search_cache.json"
APPDETAILS_DEBUG_DIR = BASE_DIR / "debug"
MARKDOWN_REPORT_DIR = BASE_DIR / "reports" / "markdown"
TXT_REPORT_DIR = BASE_DIR / "reports" / "txt"
PROFILE_REPORT_DIR = BASE_DIR / "reports" / "profile"
EXCEL_REPORT_PATH = BASE_DIR / "reports" / "excel" / "项目总表.xlsx"
SEARCH_EXPORT_DIR = BASE_DIR / "exports"
SEARCH_PLATFORM_CONFIG_PATH = BASE_DIR / "config" / "search_platforms.json"

SEARCH_RECOMMENDED_PLATFORMS = [
    "Steam 商店搜索",
    "SteamDB",
    "Bilibili",
    "YouTube",
    "Google",
    "百度",
    "小黑盒",
    "NGA 玩家社区",
    "TapTap",
    "巴哈姆特",
]

SEARCH_CORE_KEYWORDS = [
    "{game_name}",
    "{game_name} Steam",
    "{game_name} demo",
    "{game_name} 试玩",
    "{game_name} 中文评测",
    "{game_name} gameplay",
    "{game_name} trailer",
    "{developer}",
]

SEARCH_MODE_LIMITS = {
    "精简模式": {"per_platform": 2, "section": 30},
    "标准模式": {"per_platform": 5, "section": 20},
    "完整模式": {"per_platform": None, "section": None},
}


def clean_candidate_value(value) -> str:
    text = str(value or "").strip()
    if text in {"未获取", "未填写", "None", "nan", "[]", PLACEHOLDER}:
        return ""
    return text


def is_empty_or_placeholder_game_name(value, appid) -> bool:
    text = clean_candidate_value(value)
    clean_appid = str(appid or "").strip()
    if not text:
        return True
    return bool(clean_appid and re.fullmatch(rf"AppID\s+{re.escape(clean_appid)}", text, flags=re.IGNORECASE))


def candidate_record_from_mapping(data: dict, *, source: str = "", stage: str = "新发现", priority: str = "未定") -> CandidatePoolRecord:
    appid = clean_candidate_value(data.get("appid") or data.get("AppID"))
    game_name = clean_candidate_value(data.get("game_name") or data.get("title") or data.get("游戏名"))
    steam_url = clean_candidate_value(data.get("steam_url") or data.get("Steam 链接"))
    steamdb_url = clean_candidate_value(data.get("steamdb_url") or data.get("SteamDB 链接"))
    if appid:
        steam_url = steam_url or steam_url_from_appid(appid)
        steamdb_url = steamdb_url or steamdb_app_url_from_appid(appid)
    review_score = clean_candidate_value(
        data.get("review_score")
        or data.get("review_score_desc")
        or data.get("positive_rate")
        or data.get("rating")
    )
    return CandidatePoolRecord(
        appid=appid,
        game_name=game_name,
        steam_url=steam_url,
        steamdb_url=steamdb_url,
        developer=clean_candidate_value(data.get("developer")),
        publisher=clean_candidate_value(data.get("publisher")),
        release_status=clean_candidate_value(data.get("release_status") or data.get("release_date")),
        release_date=clean_candidate_value(data.get("release_date")),
        has_demo=clean_candidate_value(data.get("has_demo")),
        supports_schinese=clean_candidate_value(data.get("supports_schinese") or data.get("has_simplified_chinese")),
        genres_tags=clean_candidate_value(data.get("genres_tags") or data.get("genres") or data.get("tags") or data.get("genre_tags")),
        price=clean_candidate_value(data.get("price")),
        review_score=review_score,
        review_count=clean_candidate_value(data.get("review_count") or data.get("review_total") or data.get("reviews")),
        median_playtime=clean_candidate_value(data.get("median_playtime") or data.get("median_playtime_hours")),
        avg_playtime=clean_candidate_value(data.get("avg_playtime") or data.get("avg_playtime_hours")),
        source=source or clean_candidate_value(data.get("source") or data.get("source_group") or data.get("source_page")),
        source_url=clean_candidate_value(data.get("source_url") or data.get("steamdb_url") or data.get("steam_url")),
        priority=priority,
        stage=stage,
        next_action=clean_candidate_value(data.get("next_action")),
        owner_note=clean_candidate_value(data.get("owner_note") or data.get("note") or data.get("subtitle")),
        reject_reason=clean_candidate_value(data.get("reject_reason")),
        steamdb_rank=clean_candidate_value(data.get("steamdb_rank") or data.get("rank")),
        steamdb_followers=clean_candidate_value(data.get("steamdb_followers") or data.get("followers")),
        steamdb_peak_ccu=clean_candidate_value(data.get("steamdb_peak_ccu") or data.get("peak_ccu")),
        peak_ccu=clean_candidate_value(data.get("peak_ccu")),
        source_notes=clean_candidate_value(data.get("source_notes")),
        is_archived=clean_candidate_value(data.get("is_archived")) or "False",
    )


def save_mapping_to_candidate_pool(
    data: dict,
    *,
    source: str = "",
    stage: str = "新发现",
    priority: str = "未定",
    success_prefix: str = "候选池已更新",
    force_status_updates: bool = False,
) -> None:
    record = candidate_record_from_mapping(data, source=source, stage=stage, priority=priority)
    if not record.appid and not record.game_name:
        st.warning("缺少游戏名和 AppID，无法加入候选池。")
        return
    _, action = upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
    if force_status_updates and record.appid:
        update_candidate_pool_fields(
            CANDIDATE_POOL_CSV_PATH,
            appid=record.appid,
            updates={
                "stage": record.stage,
                "priority": record.priority,
                "next_action": record.next_action,
                "reject_reason": record.reject_reason,
                "is_archived": record.is_archived,
            },
        )
    action_text = "新增" if action == "created" else "更新"
    st.success(f"{success_prefix}：{action_text} {record.game_name or record.appid}")


def build_candidate_pool_record_from_appid(appid: str, source_url: str = "", source: str = "SteamDB 批量导入") -> tuple[CandidatePoolRecord, bool]:
    clean_appid = str(appid or "").strip()
    detail = {}
    review_stats = {}
    try:
        detail = get_cached_appdetails_summary(clean_appid, STEAM_APPDETAILS_CACHE_PATH)
    except Exception:
        detail = {}
    try:
        review_stats = get_cached_review_stats(clean_appid, STEAM_REVIEW_STATS_CACHE_PATH)
    except Exception:
        review_stats = {}
    normalized = normalize_steam_game_data(
        appid=clean_appid,
        search_item={"appid": clean_appid, "steam_url": steam_url_from_appid(clean_appid)},
        appdetails=detail,
        review_stats=review_stats,
    )
    game_name = clean_candidate_value(normalized.get("game_name"))
    enriched = bool(game_name and game_name != f"AppID {clean_appid}")
    if not enriched:
        game_name = f"AppID {clean_appid}"
    return (
        CandidatePoolRecord(
            appid=clean_appid,
            game_name=game_name,
            steam_url=steam_url_from_appid(clean_appid),
            steamdb_url=steamdb_app_url_from_appid(clean_appid),
            developer=clean_candidate_value(normalized.get("developer")),
            publisher=clean_candidate_value(normalized.get("publisher")),
            release_status=clean_candidate_value(normalized.get("release_date")),
            release_date=clean_candidate_value(normalized.get("release_date")),
            has_demo=clean_candidate_value(normalized.get("has_demo")),
            supports_schinese=clean_candidate_value(normalized.get("supports_schinese")),
            genres_tags=clean_candidate_value(normalized.get("genres")),
            price=clean_candidate_value(normalized.get("price")),
            review_score=clean_candidate_value(normalized.get("review_score_desc") or normalized.get("positive_rate")),
            review_count=clean_candidate_value(normalized.get("review_total")),
            median_playtime=clean_candidate_value(normalized.get("median_playtime_hours")),
            avg_playtime=clean_candidate_value(normalized.get("avg_playtime_hours")),
            source=source,
            source_url=source_url,
            priority="未定",
            stage="新发现",
            next_action="判断优先级" if enriched else "补项目画像",
        ),
        enriched,
    )


CANDIDATE_POOL_BASE_UPDATE_FIELDS = {
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
    "steamdb_rank",
    "steamdb_followers",
    "steamdb_peak_ccu",
    "peak_ccu",
    "source_notes",
}


def update_candidate_pool_basic_info_from_mapping(data: dict, source: str = "") -> tuple[bool, str]:
    record = candidate_record_from_mapping(data, source=source or str(data.get("source", "") or ""), stage="新发现", priority="未定")
    appid = str(record.appid or "").strip()
    if not appid:
        return False, "缺少 AppID，无法匹配候选池。"
    existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid)
    if not existing:
        return False, "该 AppID 尚未在候选池中。"

    record_data = candidate_pool_record_to_dict(record)
    updates = {
        field: value
        for field, value in record_data.items()
        if field in CANDIDATE_POOL_BASE_UPDATE_FIELDS and str(value or "").strip()
    }
    current_next_action = str(existing.get("next_action", "") or "").strip()
    if not current_next_action or current_next_action == "补项目画像":
        updates["next_action"] = "判断优先级"
    if not updates:
        return False, "没有可回写的基础信息。"
    update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, appid=appid, updates=updates)
    return True, f"候选池信息已更新：{record.game_name or appid}"


def upsert_steamdb_paste_candidate(row: dict) -> str:
    appid = clean_candidate_value(row.get("appid"))
    game_name = clean_candidate_value(row.get("game_name")) or (f"AppID {appid}" if appid else "")
    if not appid and not game_name:
        return "failed"

    steam_url = clean_candidate_value(row.get("steam_url")) or steam_url_from_appid(appid)
    steamdb_url = clean_candidate_value(row.get("steamdb_url")) or steamdb_app_url_from_appid(appid)
    row_source_notes = clean_candidate_value(row.get("source_notes"))
    source_notes = "来自 SteamDB 导入"
    if row_source_notes:
        source_notes = f"{source_notes}；{row_source_notes}"
    incoming = {
        "appid": appid,
        "game_name": game_name,
        "steam_url": steam_url,
        "steamdb_url": steamdb_url,
        "developer": clean_candidate_value(row.get("developer")),
        "publisher": clean_candidate_value(row.get("publisher")),
        "release_status": clean_candidate_value(row.get("release_status") or row.get("release_date")),
        "steamdb_rank": clean_candidate_value(row.get("rank") or row.get("steamdb_rank")),
        "steamdb_followers": clean_candidate_value(row.get("followers") or row.get("steamdb_followers")),
        "review_count": clean_candidate_value(row.get("reviews") or row.get("review_count")),
        "peak_ccu": clean_candidate_value(row.get("peak_ccu")),
        "steamdb_peak_ccu": clean_candidate_value(row.get("peak_ccu") or row.get("steamdb_peak_ccu")),
        "review_score": clean_candidate_value(row.get("rating") or row.get("review_score")),
        "price": clean_candidate_value(row.get("price")),
        "release_date": clean_candidate_value(row.get("release_date")),
        "has_demo": clean_candidate_value(row.get("has_demo")),
        "supports_schinese": clean_candidate_value(row.get("supports_schinese")),
        "source": "SteamDB Paste",
        "source_url": steamdb_url or steam_url,
        "next_action": "补项目画像",
        "stage": "新发现",
        "priority": "未定",
    }
    incoming["source_notes"] = source_notes

    existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid) if appid else {}
    if existing:
        updates = {}
        fill_only_fields = [
            "game_name",
            "steam_url",
            "steamdb_url",
            "developer",
            "publisher",
            "release_status",
            "release_date",
            "has_demo",
            "supports_schinese",
            "steamdb_rank",
            "steamdb_followers",
            "review_count",
            "peak_ccu",
            "steamdb_peak_ccu",
            "review_score",
            "price",
            "source",
            "source_url",
            "next_action",
        ]
        for field in fill_only_fields:
            current_value = clean_candidate_value(existing.get(field))
            new_value = incoming.get(field, "")
            if field == "game_name":
                if (
                    is_empty_or_placeholder_game_name(current_value, appid)
                    and new_value
                    and not is_empty_or_placeholder_game_name(new_value, appid)
                ):
                    updates[field] = new_value
                continue
            if not current_value and new_value:
                updates[field] = new_value
        current_notes = clean_candidate_value(existing.get("source_notes"))
        if "SteamDB 导入" not in current_notes:
            updates["source_notes"] = f"{current_notes}；来自 SteamDB 导入" if current_notes else "来自 SteamDB 导入"
        incoming_notes = clean_candidate_value(incoming.get("source_notes"))
        if incoming_notes and incoming_notes not in current_notes:
            updates["source_notes"] = append_note_text(current_notes, incoming_notes)
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, appid=appid, updates=updates)
        return "updated"

    record = CandidatePoolRecord(
        appid=appid,
        game_name=game_name,
        steam_url=steam_url,
        steamdb_url=steamdb_url,
        developer=incoming["developer"],
        publisher=incoming["publisher"],
        release_status=incoming["release_status"],
        price=incoming["price"],
        review_score=incoming["review_score"],
        review_count=incoming["review_count"],
        has_demo=incoming["has_demo"],
        supports_schinese=incoming["supports_schinese"],
        source=incoming["source"],
        source_url=incoming["source_url"],
        priority=incoming["priority"],
        stage=incoming["stage"],
        next_action=incoming["next_action"],
        steamdb_rank=incoming["steamdb_rank"],
        steamdb_followers=incoming["steamdb_followers"],
        steamdb_peak_ccu=incoming["steamdb_peak_ccu"],
        peak_ccu=incoming["peak_ccu"],
        source_notes=incoming["source_notes"],
        release_date=incoming["release_date"],
    )
    upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
    return "created"


def import_steamdb_paste_rows_to_candidate_pool(rows: list[dict]) -> dict:
    stats = {"created": 0, "updated": 0, "failed": 0, "failed_rows": []}
    for row in rows:
        try:
            action = upsert_steamdb_paste_candidate(row)
        except Exception as exc:
            action = "failed"
            stats["failed_rows"].append({"source_row": row.get("source_row", ""), "reason": str(exc)})
        if action in {"created", "updated"}:
            stats[action] += 1
        else:
            stats["failed"] += 1
            if not stats["failed_rows"] or stats["failed_rows"][-1].get("source_row") != row.get("source_row"):
                stats["failed_rows"].append({"source_row": row.get("source_row", ""), "reason": "缺少 AppID 和游戏名"})
    return stats


def candidate_pool_update_payload_from_chacha(card: dict) -> dict:
    return {
        "appid": card.get("appid"),
        "game_name": card.get("game_name") or card.get("title"),
        "steam_url": card.get("steam_url"),
        "steamdb_url": card.get("steamdb_url"),
        "developer": card.get("developer"),
        "publisher": card.get("publisher"),
        "release_status": card.get("release_status") or card.get("release_date"),
        "release_date": card.get("release_date") or card.get("release_status"),
        "has_demo": card.get("has_demo"),
        "supports_schinese": card.get("supports_schinese"),
        "genres_tags": card.get("genres_tags") or card.get("genres") or card.get("tags"),
        "price": card.get("price"),
        "review_score": card.get("review_score") or card.get("review_score_desc") or card.get("positive_rate"),
        "review_count": card.get("review_count") or card.get("review_total"),
        "median_playtime": card.get("median_playtime") or card.get("median_playtime_hours"),
        "avg_playtime": card.get("avg_playtime") or card.get("avg_playtime_hours"),
    }


DOMESTIC_LINK_LABELS = ["百度", "B站", "小黑盒", "游民星空", "游侠"]
OVERSEAS_LINK_LABELS = ["Google", "Steam", "SteamDB", "YouTube", "Reddit", "itch", "IGDB"]
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
OPEN_LINK_DISPLAY_COLUMNS = ["打开", "分组", "平台", "关键词", "链接"]


def build_project_from_form(form_values: dict) -> ProjectCard:
    """把页面表单数据整理成项目卡片。"""
    return ProjectCard(**form_values)


def build_competitor_from_form(form_values: dict) -> CompetitorRecord:
    """把竞品表单数据整理成竞品记录。"""
    return CompetitorRecord(**form_values)


def build_candidate_from_form(form_values: dict) -> CompetitorCandidate:
    """把候选表单数据整理成候选记录。"""
    return CompetitorCandidate(**form_values)


def get_project_options() -> list[dict]:
    """读取未删除项目，生成可选择的目标项目。"""
    projects = load_projects(CSV_PATH, include_deleted=False)
    options = [{"label": "手动输入目标项目", "record_id": "", "game_name": "", "appid": ""}]
    for _, row in projects.iterrows():
        record_id = str(row.get("record_id", "")).strip()
        game_name = str(row.get("game_name", "")).strip()
        appid = str(row.get("appid", "")).strip()
        if not game_name and not appid:
            continue
        label = f"{game_name} / {appid}" if appid else game_name
        options.append({"label": label, "record_id": record_id, "game_name": game_name, "appid": appid})
    return options


def get_saved_project_options() -> list[dict]:
    """读取可补充的已保存项目选项。"""
    return [option for option in get_project_options() if option["record_id"]]


def load_project_row(record_id: str):
    """按记录 ID 读取项目行。"""
    projects = load_projects(CSV_PATH, include_deleted=False)
    matched = projects.loc[projects["record_id"].astype(str) == str(record_id)]
    if matched.empty:
        return None
    return matched.iloc[0]


def project_from_row(row) -> ProjectCard:
    """把 CSV 行恢复成 ProjectCard，供报告生成使用。"""
    values = {
        field_name: row.get(field_name, "")
        for field_name in ProjectCard.__dataclass_fields__
        if field_name in row
    }
    return ProjectCard(**values)


def build_report_for_project(project: ProjectCard) -> tuple[Path, Path]:
    """为项目生成报告，并带上对应竞品和候选记录。"""
    competitors = filter_competitors(load_competitors(COMPETITOR_CSV_PATH), project.appid, project.game_name)
    candidates = filter_candidates(load_candidates(CANDIDATE_CSV_PATH), project.appid, project.game_name, "全部")
    return generate_reports(
        project,
        MARKDOWN_REPORT_DIR,
        TXT_REPORT_DIR,
        competitors,
        candidates,
    )


def render_report_result(project: ProjectCard) -> None:
    """生成报告并显示路径。"""
    markdown_path, txt_path = build_report_for_project(project)
    st.success("初筛报告已生成。")
    st.write(f"Markdown 报告路径：{markdown_path}")
    st.write(f"TXT 报告路径：{txt_path}")


def render_profile_draft_page() -> None:
    """Render the one-click project profile draft workflow."""
    st.subheader("一键项目画像")
    st.caption("输入 Steam 链接或 AppID 后，生成一页紧凑的发行初筛项目画像；只读公开商店信息和 1 页 Steam 评测样本。")

    consume_pending_profile_prefill()
    render_external_title_clue_controls()

    with st.form("project_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            steam_input = st.text_input(
                "Steam 链接或 AppID",
                key="profile_steam_input",
                placeholder="https://store.steampowered.com/app/123456/Game_Name/",
            )
            chinese_name = ""
            user_keywords = st.text_area("用户补充关键词（可选，逗号或换行分隔）", height=90, key="profile_user_keywords")
            pasted_titles = st.text_area(
                "外部标题线索，可选",
                height=110,
                key="profile_external_title_clues",
                help="可把 B站、YouTube、百度、Google、小黑盒等搜索结果标题粘进来。工具会提取类型词和竞品名，不需要全文。",
            )
        with col2:
            user_has_demo = st.selectbox("是否已有 Demo（可选）", ["未确认", "是", "否"], key="profile_user_has_demo")
            user_demo_played = st.selectbox("是否已试玩（可选）", ["未确认", "已试玩", "未试玩"], key="profile_user_demo_played")
            st.info("字段拿不到时会显示“未获取/需人工确认”，不会自动编造。")

        generate_profile = st.form_submit_button("生成项目画像草稿")

    if generate_profile:
        appid = parse_appid(steam_input)
        if not appid:
            st.error("未能从输入中解析 AppID，请输入 Steam 商店链接或纯数字 AppID。")
        else:
            prefill = st.session_state.get("profile_prefill_metadata", {})
            if not isinstance(prefill, dict) or str(prefill.get("appid", "")).strip() not in {"", appid}:
                prefill = {}
            detail = get_cached_appdetails_summary(appid, STEAM_APPDETAILS_CACHE_PATH)
            review_stats = get_cached_review_stats(appid, STEAM_REVIEW_STATS_CACHE_PATH)
            if not review_stats.get("success") and str(prefill.get("review_total", "") or "").strip():
                review_stats = {**review_stats, **prefill, "success": True, "review_stats_status": prefill.get("review_stats_status") or "来自首页预填"}
            normalized = normalize_steam_game_data(
                appid=appid,
                search_item=prefill,
                appdetails=detail,
                review_stats=review_stats,
            )
            slug_match = re.search(r"/app/\d+/([^/?#]+)", str(steam_input or ""))
            input_slug = slug_match.group(1).strip("/") if slug_match else ""
            resolved_game_name = ""
            for candidate_name in [detail.get("name"), normalized.get("game_name"), input_slug]:
                clean_name = str(candidate_name or "").strip()
                if clean_name and clean_name != PLACEHOLDER and clean_name not in {"未获取", "未确认"}:
                    resolved_game_name = clean_name
                    break
            store_info = {
                **normalized,
                "name": resolved_game_name,
                "game_name": resolved_game_name,
                "developers": detail.get("developers", []),
                "publishers": detail.get("publishers", []),
                "release_status": normalized.get("release_date", ""),
                "has_simplified_chinese": normalized.get("supports_schinese", ""),
                "tags": detail.get("tags", []),
                "header_image": detail.get("header_image", ""),
                "capsule_image": detail.get("capsule_image", ""),
                "image_url": normalized.get("image_url", ""),
                "short_description": detail.get("short_description", ""),
                "about_the_game": detail.get("about_the_game", ""),
                "screenshots": detail.get("screenshots", []),
                "movies": detail.get("movies", []),
                "screenshots_count": detail.get("screenshots_count", 0),
                "movies_count": detail.get("movies_count", 0),
                "mature_content": detail.get("mature_content", ""),
                "quick_capture_note": prefill.get("quick_capture_note") or prefill.get("note", ""),
                "source_context": prefill.get("source_context", ""),
                "appdetails_region_used": detail.get("appdetails_region_used", ""),
                "html_fallback_status": detail.get("html_fallback_status", ""),
                "suspected_region_restricted": detail.get("suspected_region_restricted", ""),
                "steam_data_status": detail.get("steam_data_status", ""),
            }
            if chinese_name.strip():
                store_info["name"] = chinese_name.strip()
                store_info["game_name"] = chinese_name.strip()
            if user_has_demo != "未确认":
                store_info["has_demo"] = user_has_demo

            profile = generate_project_profile(
                store_info,
                chinese_name=chinese_name,
                user_keywords=user_keywords,
                user_has_demo=user_has_demo,
                user_demo_played=user_demo_played,
                external_title_clues=pasted_titles,
            )
            st.session_state["project_profile_draft"] = profile
            st.session_state["project_profile_fetch_success"] = bool(detail.get("success") or prefill)
            st.session_state["project_profile_fetch_message"] = (
                f"已读取 Steam 缓存数据：{normalized.get('data_status')}"
            )
            st.session_state["profile_pending_duplicate_appid"] = ""

    profile = st.session_state.get("project_profile_draft")
    if not isinstance(profile, ProjectProfile):
        return

    fetch_message = st.session_state.get("project_profile_fetch_message", "")
    if st.session_state.get("project_profile_fetch_success"):
        st.success(fetch_message)
    elif fetch_message:
        st.warning(fetch_message)

    render_profile_draft(profile)
    render_profile_actions(profile)


def render_external_title_clue_controls() -> None:
    with st.expander("外部标题线索，可选", expanded=False):
        st.caption("可把 B站、YouTube、百度、Google、小黑盒等搜索结果标题粘进来。工具只提取标题里的类型词和竞品名。")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write("手动粘贴标题是主路径；自动抓取可能因动态加载或反爬失败。")
        with col2:
            if st.button("尝试抓取外部标题线索", key="profile_fetch_external_titles"):
                raw_input = st.session_state.get("profile_steam_input", "")
                appid = parse_appid(raw_input)
                game_name = st.session_state.get("profile_chinese_name", "") or st.session_state.get("profile_game_name", "")
                if not game_name and appid:
                    game_name = appid
                clues = fetch_external_title_clues(game_name=game_name, english_name="", appid=appid)
                if clues.raw_titles:
                    existing = st.session_state.get("profile_external_title_clues", "")
                    merged = "\n".join([part for part in [existing.strip(), "\n".join(clues.raw_titles)] if part])
                    st.session_state["profile_external_title_clues"] = merged
                    st.success(clues.source_message)
                else:
                    st.warning(clues.source_message or "自动抓取失败，请手动粘贴标题。")

        pasted = st.session_state.get("profile_external_title_clues", "")
        if pasted:
            clues = extract_external_title_clues(pasted)
            st.write("已提取线索：" + " / ".join(clues.extracted_terms[:12]))


def profile_appid(profile: ProjectProfile) -> str:
    """Return the active AppID from normalized profile fields."""
    info = profile.raw_store_info or {}
    return str(info.get("appid", "") or profile.basic_info.get("AppID", "") or "").strip()


def profile_game_name(profile: ProjectProfile) -> str:
    """Return the active game name from normalized profile fields."""
    info = profile.raw_store_info or {}
    return str(info.get("game_name", "") or profile.basic_info.get("游戏名", "") or "").strip()


def profile_party_summary(profile: ProjectProfile) -> str:
    info = profile.raw_store_info or {}
    developer = str(info.get("developer", "") or profile.basic_info.get("开发商", "") or PLACEHOLDER).strip()
    publisher = str(info.get("publisher", "") or profile.basic_info.get("发行商", "") or PLACEHOLDER).strip()
    return f"开发商：{developer or PLACEHOLDER} · 发行商：{publisher or PLACEHOLDER}"


def profile_steam_news_title(profile: ProjectProfile) -> str:
    appid = profile_appid(profile)
    result = st.session_state.get(f"profile_steam_news_result_{appid}", {}) if appid else {}
    items = result.get("items", []) if isinstance(result, dict) else []
    if items:
        latest_item = items[0] if isinstance(items[0], dict) else {}
        latest = latest_item.get("readable_date") or latest_item.get("date") or "未获取"
        return f"Steam 动态 / 公告（{len(items)} 条 · 最新 {latest}）"
    status = steam_news_status_label(result) if isinstance(result, dict) else "展开后获取"
    return f"Steam 动态 / 公告（{status}）"


def profile_review_preview_title(profile: ProjectProfile) -> str:
    info = profile.raw_store_info or {}
    positive_rate = format_positive_rate(info.get("positive_rate"))
    review_total = format_review_total(info.get("review_total"))
    return f"Steam 评论预览（好评率 {positive_rate} · 总评 {review_total}）"


def profile_market_data_title(profile: ProjectProfile) -> str:
    records = filter_market_data(
        load_market_data(MARKET_DATA_CSV_PATH),
        appid=profile_appid(profile),
        game_name=profile_game_name(profile),
    )
    return f"第三方市场数据（记录：{len(records)} 条）"


def profile_external_intel_title(profile: ProjectProfile) -> str:
    records = filter_external_intel(
        load_external_intel(EXTERNAL_INTEL_CSV_PATH),
        appid=profile_appid(profile),
        game_name=profile_game_name(profile),
    )
    return f"外部声量摘要 / 外部情报（记录：{len(records)} 条）"


def render_profile_draft(profile: ProjectProfile) -> None:
    """Display compact generated profile sections."""
    summary = profile.quick_summary or {}
    info = profile.raw_store_info or {}

    with st.expander("自动获取到的基础信息", expanded=True):
        basic_rows = [{"字段": key, "内容": value or PLACEHOLDER} for key, value in profile.basic_info.items()]
        st.dataframe(pd.DataFrame(basic_rows), use_container_width=True, hide_index=True)

    render_profile_data_overview(profile)
    render_profile_store_media_preview(profile)

    if st.checkbox(profile_steam_news_title(profile), value=False, key="profile_show_steam_news_panel"):
        render_profile_steam_news_panel(profile)
    if st.checkbox(profile_review_preview_title(profile), value=False, key="profile_show_review_preview_panel"):
        render_profile_steam_review_preview(profile)

    st.markdown("### 项目初筛卡")

    data_quality_level = str(getattr(profile, "data_quality_level", "") or "low")
    has_review_data = _profile_has_review_data(info)
    st.caption(f"数据充分性：{_data_quality_label(data_quality_level)}")

    if data_quality_level == "low":
        st.warning("数据不足，需人工验证。当前只能做项目初筛记录。")
        st.write("下一步动作：补商店截图、视频、Demo、评测或社区声量。")
    elif data_quality_level == "medium":
        type_col, selling_col = st.columns([1, 2])
        with type_col:
            st.markdown("**类型定位**")
            st.write(summary.get("游戏类型 / 赛道定位", PLACEHOLDER))
        with selling_col:
            st.markdown("**卖点一句话**")
            st.write(_first_specific_item(summary.get("主卖点", [])) or _first_specific_item(profile.selling_points) or PLACEHOLDER)
        st.info("当前信息不足以判断商业潜力。")
        st.write("**最大风险**：缺少评测/游玩时长/社区声量。")
        st.write("**下一步动作**：先看 Trailer / Demo / B站小黑盒声量。")
    else:
        type_col, selling_col = st.columns([1, 2])
        with type_col:
            st.markdown("**类型定位**")
            st.write(summary.get("游戏类型 / 赛道定位", PLACEHOLDER))
        with selling_col:
            st.markdown("**卖点一句话**")
            st.write(_first_specific_item(summary.get("主卖点", [])) or _first_specific_item(profile.selling_points) or PLACEHOLDER)

        if has_review_data:
            metric_cols = st.columns(4)
            metric_cols[0].metric("好评率", format_positive_rate(info.get("positive_rate")))
            metric_cols[1].metric("评测数", format_review_total(info.get("review_total")))
            metric_cols[2].metric("中位游玩", format_hours(info.get("median_playtime_hours")))
            metric_cols[3].metric("平均游玩", format_hours(info.get("avg_playtime_hours")))
            st.caption("游玩时间基于 Steam 评测样本，不代表全体玩家。")
        else:
            st.info("暂无 Steam 评测数据，无法判断口碑和游玩时长。")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**中国区机会**")
            st.write(_first_specific_item(profile.china_opportunities) or "需人工确认")
        with col2:
            st.markdown("**最大风险**")
            st.write(_first_specific_item(summary.get("主要风险", [])) or _first_specific_item(profile.risks) or "待人工确认")
        with col3:
            st.markdown("**下一步动作**")
            st.write(profile.next_action or PLACEHOLDER)

    review_status = str(info.get("review_stats_status", "") or "").strip()
    if review_status:
        st.caption(f"评测状态：{review_status}")
    st.caption("基于公开信息生成，需试玩复核。")

    if st.checkbox(f"开发商本体调查（{profile_party_summary(profile)}）", value=False, key="profile_show_company_dossier"):
        render_profile_company_dossier(profile)
    if st.checkbox(profile_market_data_title(profile), value=False, key="profile_show_market_data"):
        render_profile_market_data(profile)
    if st.checkbox(profile_external_intel_title(profile), value=False, key="profile_show_external_intel"):
        render_profile_external_intel(profile)

    profile_appid = str(info.get("appid", "") or profile.basic_info.get("AppID", "") or "").strip()
    steam_news_result = st.session_state.get(f"profile_steam_news_result_{profile_appid}", {}) if profile_appid else {}
    review_preview_result = st.session_state.get(f"profile_review_preview_result_{profile_appid}", {}) if profile_appid else {}
    data_source_items = [
        f"Steam AppID：{profile.basic_info.get('AppID', PLACEHOLDER)}",
        f"Steam 链接：{profile.basic_info.get('Steam 链接', PLACEHOLDER)}",
        f"数据状态：{info.get('data_status', PLACEHOLDER)}",
        f"评价状态：{info.get('review_stats_status', PLACEHOLDER)}",
        f"Steam 动态：{steam_news_status_label(steam_news_result)}",
        f"Steam 评论预览：{steam_review_preview_status_label(review_preview_result)}",
        f"appdetails_region_used：{info.get('appdetails_region_used', PLACEHOLDER)}",
        f"html_fallback_status：{info.get('html_fallback_status', PLACEHOLDER)}",
        f"suspected_region_restricted：{info.get('suspected_region_restricted', PLACEHOLDER)}",
        f"header_image 是否存在：{'是' if info.get('header_image') or info.get('image_url') else '否'}",
        f"screenshots_count：{info.get('screenshots_count', 0)}",
        f"movies_count：{info.get('movies_count', 0)}",
        f"short_description 是否存在：{'是' if str(info.get('short_description', '')).strip() else '否'}",
    ]
    if data_source_items or profile.source_limitations:
        with st.expander("数据来源 / 调试信息（仅排错时查看）", expanded=False):
            render_profile_bullet_section("来源", data_source_items)
            render_profile_bullet_section("限制", _specific_items(profile.source_limitations))

    manual_items = _specific_items(profile.manual_checklist + profile.risks)
    if manual_items:
        with st.expander("人工待确认项", expanded=False):
            render_profile_bullet_section("待确认", manual_items)


def render_profile_data_overview(profile: ProjectProfile) -> None:
    appid = profile_appid(profile)
    game_name = profile_game_name(profile)
    market_records = filter_market_data(load_market_data(MARKET_DATA_CSV_PATH), appid=appid, game_name=game_name)
    news_result = st.session_state.get(f"profile_steam_news_result_{appid}", {}) if appid else {}
    review_result = st.session_state.get(f"profile_review_preview_result_{appid}", {}) if appid else {}
    status = build_project_data_status(
        profile,
        market_data_records=market_records,
        steam_news_result=news_result,
        steam_review_preview_result=review_result,
    )
    completeness = status.get("数据完整度", "未记录")
    needs_review = status.get("需人工复核", "是")
    summary = (
        f"数据概览：完整度 {completeness}｜"
        f"基础{status.get('基础信息', '未记录')}｜"
        f"素材{status.get('商店素材', '未记录')}｜"
        f"评论{status.get('评论数据', '未记录')}｜"
        f"动态{status.get('Steam 动态', '未记录')}｜"
        f"第三方{status.get('第三方市场', '未记录')}"
    )
    if completeness == "低" or needs_review == "是":
        summary += "｜需人工复核"
    st.caption(summary)

    with st.expander("展开数据概览", expanded=False):
        overview_rows = [
            {"数据块": key, "状态": status.get(key, "未记录")}
            for key in ["基础信息", "商店素材", "评论数据", "Steam 动态", "第三方市场", "数据完整度", "最后更新时间", "缺失项"]
        ]
        st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)
        st.caption(
            f"Demo：{status.get('Demo', '未确认')} · "
            f"Playtest：{status.get('Playtest', '未确认')} · "
            f"需人工复核：{needs_review}"
        )


def render_profile_store_media_preview(profile: ProjectProfile) -> None:
    info = profile.raw_store_info or {}
    st.markdown("### 商店图文预览")

    screenshots = info.get("screenshots") if isinstance(info.get("screenshots"), list) else []
    movies = info.get("movies") if isinstance(info.get("movies"), list) else []
    header_image = (
        str(info.get("header_image", "") or "").strip()
        or str(info.get("image_url", "") or "").strip()
        or _first_screenshot_url(screenshots)
    )

    image_col, summary_col = st.columns([1.4, 1])
    with image_col:
        if header_image:
            st.image(header_image, use_container_width=True)
        else:
            st.caption("暂无商店图，建议打开 Steam / SteamDB 人工确认。")
    with summary_col:
        st.markdown(f"**{profile.basic_info.get('游戏名', PLACEHOLDER)}**")
        short_description = str(info.get("short_description", "") or "").strip()
        st.write(short_description or "短描述未获取")
        st.caption(f"开发：{compact_card_value(info.get('developer'))}")
        st.caption(f"发行：{compact_card_value(info.get('publisher'))}")
        st.caption(f"发售：{compact_card_value(info.get('release_date') or info.get('release_status'))}")
        st.caption(f"类型：{compact_card_value(info.get('genres'), max_len=80)}")
        st.caption(
            f"简中：{info.get('has_simplified_chinese') or info.get('supports_schinese') or '未确认'} · "
            f"Demo：{normalize_availability_status(info.get('has_demo'))} · "
            f"Playtest：{normalize_availability_status(info.get('has_playtest'))}"
        )
        st.caption(f"截图：{info.get('screenshots_count', len(screenshots)) or 0} · 视频：{info.get('movies_count', len(movies)) or 0}")
        steam_url = str(info.get("steam_url", "") or profile.basic_info.get("Steam 链接", "") or "").strip()
        appid = str(profile.basic_info.get("AppID", "") or info.get("appid", "") or "").strip()
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            if steam_url and steam_url != PLACEHOLDER:
                st.link_button("打开 Steam", steam_url, use_container_width=True)
        with link_col2:
            if appid and appid != PLACEHOLDER:
                st.link_button("打开 SteamDB", f"https://steamdb.info/app/{appid}/", use_container_width=True)

    render_profile_screenshot_preview(screenshots)
    render_profile_movie_preview(movies, str(info.get("steam_url", "") or profile.basic_info.get("Steam 链接", "")))
    st.caption(build_profile_visual_hint(screenshots, movies))


def render_profile_steam_news_panel(profile: ProjectProfile) -> None:
    info = profile.raw_store_info or {}
    appid = str(info.get("appid", "") or profile.basic_info.get("AppID", "") or "").strip()
    st.markdown("### Steam 动态 / 公告")
    if not appid or appid == PLACEHOLDER:
        st.info("暂无 Steam 动态：缺少 AppID。")
        st.caption("Steam 动态来自公开新闻/公告接口，仅用于辅助判断版本更新与运营活跃度，需人工复核。")
        return

    force_key = f"profile_steam_news_force_refresh_{appid}"
    force_refresh = bool(st.session_state.pop(force_key, False))
    news_result = get_steam_news_for_app(appid, STEAM_NEWS_CACHE_DIR, count=5, maxlength=500, force_refresh=force_refresh)
    st.session_state[f"profile_steam_news_result_{appid}"] = news_result
    status_label = steam_news_status_label(news_result)
    st.caption(f"Steam 动态：{status_label} · 缓存时间：{news_result.get('fetched_at') or '未记录'}")
    st.caption("接口摘要可能不是当前 Steam 页面语言；如需确认中文公告，请打开原文。")
    if news_result.get("error_message"):
        st.warning(news_result["error_message"])

    action_cols = st.columns([1, 1, 2])
    if action_cols[0].button("刷新 Steam 动态", key=f"profile_refresh_steam_news_{appid}", use_container_width=True):
        st.session_state[force_key] = True
        st.rerun()
    with action_cols[1]:
        st.link_button("打开 Steam 新闻页", f"https://store.steampowered.com/news/app/{appid}", use_container_width=True)

    items = news_result.get("items", []) if isinstance(news_result.get("items"), list) else []
    if not items:
        st.info("暂无 Steam 动态，可能是接口无返回或项目未发布公告。")
        st.caption("Steam 动态来自公开新闻/公告接口，仅用于辅助判断版本更新与运营活跃度，需人工复核。")
        return

    for index, item in enumerate(items[:5], start=1):
        title = str(item.get("title", "") or "未命名公告")
        source = str(item.get("feedlabel") or item.get("feedname") or "Steam News")
        date_text = str(item.get("date", "") or "未记录")
        summary = str(item.get("clean_summary") or item.get("contents") or "暂无摘要")
        full_clean = str(item.get("contents") or summary or "暂无摘要")
        url = str(item.get("url", "") or "").strip()
        is_major = bool(item.get("is_major_update_candidate")) or is_major_update_candidate(title, full_clean)
        st.markdown(f"**{index}. {title}**")
        st.caption(f"日期：{date_text} · 类型 / feedname：{source}")
        if is_major:
            st.warning("重大更新候选")
        st.write(str(summary)[:200] + ("..." if len(str(summary)) > 200 else ""))
        if full_clean and full_clean != summary:
            with st.expander("查看完整清洗内容", expanded=False):
                st.write(full_clean)
        link_cols = st.columns([1, 2])
        with link_cols[0]:
            if url:
                st.link_button("打开原文", url, use_container_width=True)
        with link_cols[1]:
            if url:
                st.text_input("复制新闻链接", value=url, key=f"profile_steam_news_copy_{appid}_{index}")
    st.caption("Steam 动态来自公开新闻/公告接口，仅用于辅助判断版本更新与运营活跃度，需人工复核。")


def render_profile_steam_review_preview(profile: ProjectProfile) -> None:
    info = profile.raw_store_info or {}
    appid = str(info.get("appid", "") or profile.basic_info.get("AppID", "") or "").strip()
    st.markdown("### Steam 评论预览")
    if not appid or appid == PLACEHOLDER:
        st.info("暂无评论预览：缺少 AppID。")
        return

    force_key = f"profile_review_preview_force_refresh_{appid}"
    force_refresh = bool(st.session_state.pop(force_key, False))
    review_result = get_steam_review_preview(
        appid,
        STEAM_REVIEW_PREVIEW_CACHE_DIR,
        language="schinese",
        num_per_group=3,
        force_refresh=force_refresh,
    )
    st.session_state[f"profile_review_preview_result_{appid}"] = review_result
    if review_result.get("error_message"):
        st.warning(review_result["error_message"])

    status = steam_review_preview_status_label(review_result)
    summary = review_result.get("summary", {}) if isinstance(review_result.get("summary"), dict) else {}
    st.caption(f"Steam 评论预览：{status} · 缓存时间：{review_result.get('fetched_at') or '未记录'}")
    metric_cols = st.columns(3)
    metric_cols[0].metric("好评率", format_positive_rate(summary.get("positive_rate") or info.get("positive_rate")))
    metric_cols[1].metric("总评测数", format_review_total(summary.get("review_total") or info.get("review_total")))
    metric_cols[2].metric("评价描述", str(summary.get("review_score_desc") or info.get("review_score_desc") or "未获取"))

    action_cols = st.columns([1, 1, 2])
    if action_cols[0].button("刷新评论预览", key=f"profile_refresh_review_preview_{appid}", use_container_width=True):
        st.session_state[force_key] = True
        st.rerun()
    with action_cols[1]:
        st.link_button("打开 Steam 评论页", f"https://steamcommunity.com/app/{appid}/reviews/", use_container_width=True)

    groups = [
        ("最近中文评论", review_result.get("recent_reviews", [])),
        ("高价值评论", review_result.get("helpful_reviews", [])),
        ("差评样本", review_result.get("negative_reviews", [])),
    ]
    if not any(items for _, items in groups):
        st.info("暂无中文评论样本，可打开 Steam 评论页人工查看。")
        return

    for group_title, reviews in groups:
        st.markdown(f"**{group_title}**")
        if not reviews:
            st.caption("暂无")
            continue
        for index, review in enumerate(reviews[:3], start=1):
            render_profile_review_preview_item(review, f"{appid}_{group_title}_{index}")

    st.caption("Steam 评论预览仅拉取少量公开样本，用于快速判断玩家反馈方向，不替代完整评论分析器。")


def render_profile_review_preview_item(review: dict, key_suffix: str) -> None:
    voted_label = "推荐" if review.get("voted_up") else "不推荐"
    created_at = str(review.get("created_at", "") or "未获取")
    playtime = format_review_preview_playtime(review.get("author_playtime_at_review") or review.get("author_playtime_forever"))
    votes_up = str(review.get("votes_up", 0) or 0)
    preview = str(review.get("review_preview") or review.get("review") or "暂无评论正文")
    full_text = str(review.get("review") or preview)
    review_url = str(review.get("review_url", "") or "").strip()

    st.markdown(f"- **{voted_label}** · {created_at} · 游玩 {playtime} · 点赞 {votes_up}")
    st.write(preview[:200] + ("..." if len(preview) > 200 else ""))
    if review_url:
        st.markdown(f"[打开 Steam 原评论]({review_url})")
    if full_text and full_text != preview:
        with st.expander("展开查看完整评论", expanded=False):
            st.write(full_text)


def render_profile_screenshot_preview(screenshots: list[dict]) -> None:
    st.markdown("**截图预览**")
    if not screenshots:
        st.caption("暂无截图")
        return
    visible = screenshots[:6]
    columns = st.columns(min(3, len(visible)))
    for index, item in enumerate(visible):
        with columns[index % len(columns)]:
            image_url = str(item.get("path_thumbnail") or item.get("path_full") or "").strip()
            full_url = str(item.get("path_full") or image_url).strip()
            if image_url:
                st.image(image_url, use_container_width=True)
            if full_url:
                st.markdown(f"[打开原图]({full_url})")
    if len(screenshots) > 6:
        with st.expander("查看更多截图", expanded=False):
            extra = screenshots[6:]
            extra_columns = st.columns(3)
            for index, item in enumerate(extra):
                with extra_columns[index % 3]:
                    image_url = str(item.get("path_thumbnail") or item.get("path_full") or "").strip()
                    full_url = str(item.get("path_full") or image_url).strip()
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    if full_url:
                        st.markdown(f"[打开原图]({full_url})")


def render_profile_movie_preview(movies: list[dict], steam_url: str) -> None:
    st.markdown("**视频 / Trailer**")
    if not movies:
        st.caption("暂无视频")
        return
    visible = movies[:3]
    columns = st.columns(min(3, len(visible)))
    for index, movie in enumerate(visible):
        with columns[index % len(columns)]:
            thumbnail = str(movie.get("thumbnail", "") or "").strip()
            if thumbnail:
                st.image(thumbnail, use_container_width=True)
            st.caption(str(movie.get("name", "") or f"视频 {index + 1}"))
            if steam_url:
                st.markdown(f"[打开 Steam 页面看视频]({steam_url})")
    if len(movies) > 3:
        with st.expander("查看更多视频", expanded=False):
            for index, movie in enumerate(movies[3:], start=4):
                st.write(f"{index}. {movie.get('name') or '未命名视频'}")


def build_profile_visual_hint(screenshots: list[dict], movies: list[dict]) -> str:
    if movies:
        return "视觉初判：有视频，可先看 Trailer 判断前 15 秒钩子。"
    if len(screenshots) >= 4:
        return "视觉初判：有多张截图，可快速判断战斗画面、UI 密度和美术识别度。"
    if screenshots:
        return "视觉初判：截图偏少，需要补看 Steam 页面确认玩法画面。"
    return "暂无商店图，建议打开 Steam / SteamDB 人工确认。"


def _first_screenshot_url(screenshots: list[dict]) -> str:
    for item in screenshots:
        if isinstance(item, dict):
            url = str(item.get("path_full") or item.get("path_thumbnail") or "").strip()
            if url:
                return url
    return ""


def _profile_has_review_data(info: dict) -> bool:
    try:
        return int(float(info.get("review_total") or 0)) >= 10
    except (TypeError, ValueError):
        return False


def _data_quality_label(level: str) -> str:
    labels = {
        "high": "高，可以做弱初筛",
        "medium": "中，缺少评测/游玩时长",
        "low": "低，需人工验证",
    }
    return labels.get(str(level or "").strip(), "低，需人工验证")


def render_profile_bullet_section(title: str, items: list[str]) -> None:
    st.markdown(f"**{title}**")
    if not items:
        st.write(f"- {PLACEHOLDER}")
        return
    for item in items:
        st.write(f"- {item}")


def _specific_items(items: list[str]) -> list[str]:
    generic_markers = [
        "发行沟通",
        "需要试玩确认",
        "玩法差异化",
        "待从候选池确认",
        "本地化、PR、愿望单增长",
        "核心循环是否真的成立",
        "开发商是否愿意合作",
        "中国玩家是否有兴趣",
    ]
    output = []
    for item in items or []:
        text = str(item or "").strip()
        if not text or text == PLACEHOLDER:
            continue
        if any(marker in text for marker in generic_markers):
            continue
        if text not in output:
            output.append(text)
    return output


def _first_specific_item(items: list[str]) -> str:
    values = _specific_items(items)
    return values[0] if values else ""


def render_profile_company_dossier(profile: ProjectProfile) -> None:
    appid = _company_source_value(profile.basic_info.get("AppID", ""))
    game_name = _company_source_value(profile.basic_info.get("游戏名", ""))
    developer = _company_source_value(profile.basic_info.get("开发商", ""))
    publisher = _company_source_value(profile.basic_info.get("发行商", ""))
    developer_names = get_profile_company_names(profile, "developer")
    publisher_names = get_profile_company_names(profile, "publisher")
    company_targets = build_company_target_options(developer_names, publisher_names)
    all_records = load_company_dossiers(COMPANY_DOSSIER_CSV_PATH)
    project_records = filter_company_dossiers_for_project(all_records, appid=appid, game_name=game_name)
    selected_target = resolve_selected_company_target(company_targets, project_records)
    current_record = latest_company_dossier(filter_company_records_for_target(project_records, selected_target))

    st.markdown("### 开发商本体调查")
    st.caption("开发商本体信息来自公开资料和人工记录，需人工复核。这里只记录证据，不自动判断真相。")

    meta_cols = st.columns(4)
    with meta_cols[0]:
        render_company_name_list("开发商", developer_names)
    with meta_cols[1]:
        render_company_name_list("发行商", publisher_names)
    meta_cols[2].write(f"AppID：{appid or '未确认'}")
    meta_cols[3].write(f"游戏名：{game_name or '未确认'}")

    render_company_dossier_summary(current_record)
    render_legacy_merged_company_notice(project_records)

    external_records = filter_external_intel(load_external_intel(EXTERNAL_INTEL_CSV_PATH), appid=appid, game_name=game_name)
    st.caption(f"相关外部情报记录数：{len(external_records)}")
    render_company_related_external_links(external_records)

    selected_label = selected_target.get("label", "")
    if company_targets:
        target_labels = [target["label"] for target in company_targets]
        if selected_label not in target_labels:
            selected_label = target_labels[0]
        selected_label = st.selectbox(
            "调查对象",
            target_labels,
            index=target_labels.index(selected_label),
            key="company_dossier_selected_target_label",
        )
        selected_target = next((target for target in company_targets if target["label"] == selected_label), selected_target)
        current_record = latest_company_dossier(filter_company_records_for_target(project_records, selected_target))
        st.session_state["company_dossier_selected_company_name"] = selected_target.get("name", "")
        st.session_state["company_dossier_selected_company_role"] = selected_target.get("role", "unknown")
    else:
        st.session_state["company_dossier_selected_company_name"] = ""
        st.session_state["company_dossier_selected_company_role"] = "unknown"
        st.caption("未获取开发商/发行商名称，可在表单中手动填写公司/团队名。")
    render_company_search_entry(selected_target, company_targets)

    saved = render_company_dossier_form(
        profile=profile,
        appid=appid,
        game_name=game_name,
        developer_names=developer_names,
        publisher_names=publisher_names,
        selected_target=selected_target,
        current_record=current_record,
        external_records=external_records,
    )
    if saved:
        project_records = filter_company_dossiers_for_project(
            load_company_dossiers(COMPANY_DOSSIER_CSV_PATH),
            appid=appid,
            game_name=game_name,
        )
        render_company_dossier_summary(latest_company_dossier(filter_company_records_for_target(project_records, selected_target)))

    with st.expander("公司档案库", expanded=False):
        render_company_dossier_library_manager(appid, game_name)


def get_profile_company_names(profile: ProjectProfile, role: str) -> list[str]:
    info = profile.raw_store_info or {}
    if role == "developer":
        return parse_company_names(info.get("developers")) or parse_company_names(info.get("developer")) or parse_company_names(profile.basic_info.get("开发商", ""))
    if role == "publisher":
        return parse_company_names(info.get("publishers")) or parse_company_names(info.get("publisher")) or parse_company_names(profile.basic_info.get("发行商", ""))
    return []


def build_company_target_options(developer_names: list[str], publisher_names: list[str]) -> list[dict]:
    targets = []
    publisher_keys = {name.casefold() for name in publisher_names}
    for name in developer_names:
        targets.append(
            {
                "label": f"开发商：{name}",
                "name": name,
                "role": "developer",
                "self_publish_status": "自发行" if name.casefold() in publisher_keys else "未确认",
            }
        )
    for name in publisher_names:
        targets.append({"label": f"发行商：{name}", "name": name, "role": "publisher", "self_publish_status": "未确认"})
    return targets


def resolve_selected_company_target(company_targets: list[dict], project_records: pd.DataFrame) -> dict:
    labels = [target["label"] for target in company_targets]
    selected_label = str(st.session_state.get("company_dossier_selected_target_label", "") or "").strip()
    if selected_label in labels:
        return next(target for target in company_targets if target["label"] == selected_label)
    latest_record = latest_company_dossier(project_records)
    if latest_record:
        company_name = str(latest_record.get("company_name", "") or "").strip()
        company_role = str(latest_record.get("company_role", "") or "").strip()
        for target in company_targets:
            if target["name"].casefold() == company_name.casefold() and target["role"] == company_role:
                return target
    return company_targets[0] if company_targets else {"label": "未确认", "name": "", "role": "unknown"}


def filter_company_records_for_target(records: pd.DataFrame, target: dict) -> pd.DataFrame:
    if records.empty:
        return records
    company_name = str(target.get("name", "") or "").strip()
    company_role = str(target.get("role", "") or "").strip()
    if not company_name:
        return records.iloc[0:0].copy()
    names = records["company_name"].astype(str).str.strip().str.casefold()
    mask = names.eq(company_name.casefold())
    if company_role in {"developer", "publisher", "developer_and_publisher"}:
        roles = records["company_role"].astype(str).str.strip()
        mask = mask & roles.isin({company_role, "developer_and_publisher"} if company_role in {"developer", "publisher"} else {company_role})
    return records.loc[mask].copy()


def render_company_name_list(title: str, names: list[str]) -> None:
    st.markdown(f"**{title}：**")
    if not names:
        st.write("- 未确认")
        return
    for name in names:
        st.write(f"- {name}")


def render_legacy_merged_company_notice(records: pd.DataFrame) -> None:
    if records.empty or "company_name" not in records.columns:
        return
    merged_names = []
    for value in records["company_name"].astype(str).tolist():
        names = parse_company_names(value)
        if len(names) > 1:
            merged_names.append(value)
    if merged_names:
        st.warning("检测到旧式合并公司名，建议拆分后分别保存：" + " / ".join(dict.fromkeys(merged_names)))


def render_company_dossier_summary(record: dict) -> None:
    st.markdown("**开发商本体摘要**")
    if not record:
        st.info("暂无开发商本体调查记录。")
        return
    contact = _join_company_display_values(
        [
            record.get("contact_email"),
            record.get("contact_discord"),
            record.get("official_site"),
            record.get("discord_url"),
            record.get("x_url"),
            record.get("youtube_url"),
            record.get("bilibili_url"),
        ]
    )
    rows = [
        ("公司/团队", record.get("company_name")),
        ("角色", display_company_role(record.get("company_role"))),
        ("地区", record.get("country_or_region")),
        ("团队规模", record.get("team_size")),
        ("已知作品", record.get("known_games")),
        ("自发行状态", record.get("self_publish_status")),
        ("发行合作史", record.get("publisher_history")),
        ("联系入口", contact),
        ("主要证据", record.get("evidence_summary")),
        ("风险", record.get("risk_note")),
        ("下一步", record.get("next_action")),
    ]
    cols = st.columns(2)
    for index, (label, value) in enumerate(rows):
        with cols[index % 2]:
            st.write(f"{label}：{_company_display(value)}")


def render_company_related_external_links(records: pd.DataFrame) -> None:
    links = collect_company_relevant_external_links(records)
    if not links:
        return
    with st.expander("可参考的外部情报链接", expanded=False):
        st.caption("以下仅展示已手动记录的外部情报链接，不自动复制到档案。")
        for label, url in links:
            st.markdown(f"- {label}：[打开链接]({url})")


def collect_company_relevant_external_links(records: pd.DataFrame) -> list[tuple[str, str]]:
    if records.empty or "source_url" not in records.columns:
        return []
    wanted_platforms = {"官网", "Presskit", "Discord", "X/Twitter", "YouTube", "Bilibili"}
    wanted_evidence = {"官网", "Presskit", "社群", "开发者资料"}
    links = []
    seen = set()
    for _, row in records.iterrows():
        url = str(row.get("source_url", "") or "").strip()
        if not url or url in seen:
            continue
        platform = str(row.get("platform", "") or "").strip()
        evidence_type = str(row.get("evidence_type", "") or "").strip()
        title = str(row.get("title", "") or "").strip()
        if platform in wanted_platforms or evidence_type in wanted_evidence:
            seen.add(url)
            label = " / ".join(part for part in [platform, evidence_type, title] if part) or "来源链接"
            links.append((label, url))
        if len(links) >= 12:
            break
    return links


def render_company_search_entry(selected_target: dict, company_targets: list[dict]) -> None:
    st.markdown("**外部搜索入口**")
    if company_targets:
        st.markdown("**Steam 快捷搜索**")
        steam_cols = st.columns(3)
        for index, target in enumerate(company_targets):
            name = str(target.get("name", "") or "").strip()
            role = str(target.get("role", "") or "").strip()
            if not name or role not in {"developer", "publisher"}:
                continue
            query_key = "developer" if role == "developer" else "publisher"
            label_role = "开发商" if role == "developer" else "发行商"
            url = f"https://store.steampowered.com/search/?{query_key}={quote(name)}"
            with steam_cols[index % 3]:
                st.link_button(f"Steam 搜索{label_role}：{name}", url, use_container_width=True)

    company_name = str(selected_target.get("name", "") or "").strip()
    if not company_name:
        st.caption("未获取公司/团队名，可先在表单中手动填写。")
        return
    st.caption(f"当前外部搜索对象：{display_company_role(selected_target.get('role'))}：{company_name}")
    columns = st.columns(3)
    for index, (label, url) in enumerate(build_company_search_links(company_name, include_steam=False)):
        with columns[index % 3]:
            st.link_button(label, url, use_container_width=True)


def render_company_dossier_form(
    profile: ProjectProfile,
    appid: str,
    game_name: str,
    developer_names: list[str],
    publisher_names: list[str],
    selected_target: dict,
    current_record: dict,
    external_records: pd.DataFrame,
) -> bool:
    _prepare_company_dossier_form_state(
        profile,
        appid,
        game_name,
        developer_names,
        publisher_names,
        selected_target,
        current_record,
        external_records,
    )

    with st.form("company_dossier_form"):
        st.markdown("**开发商本体摘要**")
        summary_cols = st.columns(3)
        summary_items = [
            ("当前调查对象", st.session_state.get("company_dossier_company_name")),
            ("角色", st.session_state.get("company_dossier_company_role_label")),
            ("地区", st.session_state.get("company_dossier_country_or_region")),
            ("已知作品", st.session_state.get("company_dossier_known_games")),
            ("自发行状态", st.session_state.get("company_dossier_self_publish_status")),
            ("可信度", st.session_state.get("company_dossier_confidence")),
            ("下一步动作", st.session_state.get("company_dossier_next_action")),
        ]
        for index, (label, value) in enumerate(summary_items):
            with summary_cols[index % 3]:
                st.write(f"{label}：{market_display(value)}")

        with st.expander("常用字段", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("公司/团队名", key="company_dossier_company_name")
                st.selectbox("角色", list(COMPANY_ROLE_BY_LABEL.keys()), key="company_dossier_company_role_label")
                st.text_input("国家/地区", key="company_dossier_country_or_region")
                st.text_area("已知作品", key="company_dossier_known_games", height=70)
                st.text_input("官网", key="company_dossier_official_site")
                st.text_input("Steam Creator / Developer 页面", key="company_dossier_steam_creator_url")
                if not str(st.session_state.get("company_dossier_steam_creator_url", "") or "").strip():
                    st.caption("Steam Creator 页面未获取，可手动填写。")
                st.text_input("Presskit", key="company_dossier_presskit_url")
            with col2:
                st.text_input("联系邮箱", key="company_dossier_contact_email")
                st.text_input("Discord", key="company_dossier_discord_url")
                st.text_input("Discord 联系方式", key="company_dossier_contact_discord")
                st.selectbox("自发行状态", SELF_PUBLISH_STATUS_OPTIONS, key="company_dossier_self_publish_status")
                st.text_area("发行合作史", key="company_dossier_publisher_history", height=70)
                st.selectbox("可信度", COMPANY_CONFIDENCE_OPTIONS, key="company_dossier_confidence")
            st.text_area("证据摘要", key="company_dossier_evidence_summary", height=80)
            st.text_area("下一步动作", key="company_dossier_next_action", height=60)

            action_cols = st.columns(4)
            save_record = action_cols[0].form_submit_button("保存开发商档案")
            update_record = action_cols[1].form_submit_button("更新当前档案")
            clear_form = action_cols[2].form_submit_button("清空表单")
            send_to_report = action_cols[3].form_submit_button("发送到项目画像报告")

        with st.expander("更多公司资料字段", expanded=False):
            more_col1, more_col2 = st.columns(2)
            with more_col1:
                st.text_input("团队人数", key="company_dossier_team_size")
                st.text_input("成立年份", key="company_dossier_founded_year")
                st.text_input("X/Twitter", key="company_dossier_x_url")
                st.text_input("YouTube", key="company_dossier_youtube_url")
                st.text_input("B站", key="company_dossier_bilibili_url")
            with more_col2:
                st.text_area("其他来源链接", key="company_dossier_source_urls", height=80)
                st.text_area("风险备注 / 详细备注", key="company_dossier_risk_note", height=90)

    if clear_form:
        st.session_state["company_dossier_clear_requested"] = True
        st.rerun()
    if save_record:
        return save_company_dossier_form_record(appid, game_name, update_existing=False)
    if update_record:
        return save_company_dossier_form_record(appid, game_name, update_existing=True)
    if send_to_report:
        return save_company_dossier_form_record(
            appid,
            game_name,
            update_existing=bool(st.session_state.get("company_dossier_current_id")),
            report_action=True,
        )
    return False


def _prepare_company_dossier_form_state(
    profile: ProjectProfile,
    appid: str,
    game_name: str,
    developer_names: list[str],
    publisher_names: list[str],
    selected_target: dict,
    current_record: dict,
    external_records: pd.DataFrame,
) -> None:
    selected_name = str(selected_target.get("name", "") or "").strip()
    selected_role = str(selected_target.get("role", "unknown") or "unknown").strip()
    profile_key = f"{appid}|{game_name}|{'/'.join(developer_names)}|{'/'.join(publisher_names)}|{selected_role}|{selected_name}"
    should_reset = (
        st.session_state.get("company_dossier_profile_key") != profile_key
        or st.session_state.pop("company_dossier_clear_requested", False)
    )
    if not should_reset:
        _normalize_company_form_select_values()
        return

    st.session_state["company_dossier_profile_key"] = profile_key
    st.session_state["company_dossier_appid"] = appid
    st.session_state["company_dossier_game_name"] = game_name
    st.session_state["company_dossier_current_id"] = str(current_record.get("dossier_id", "") or "").strip()
    defaults = build_company_dossier_form_defaults(profile, game_name, selected_target, current_record, external_records)
    for key, value in defaults.items():
        st.session_state[f"company_dossier_{key}"] = value
    _normalize_company_form_select_values()


def build_company_dossier_form_defaults(
    profile: ProjectProfile,
    game_name: str,
    selected_target: dict,
    current_record: dict,
    external_records: pd.DataFrame,
) -> dict:
    selected_name = str(selected_target.get("name", "") or "").strip()
    selected_role = str(selected_target.get("role", "unknown") or "unknown").strip()
    if current_record:
        role_label = display_company_role(current_record.get("company_role"))
        return {
            "company_name": str(current_record.get("company_name", "") or ""),
            "company_role_label": role_label if role_label in COMPANY_ROLE_BY_LABEL else "未确认",
            "country_or_region": str(current_record.get("country_or_region", "") or ""),
            "team_size": str(current_record.get("team_size", "") or ""),
            "founded_year": str(current_record.get("founded_year", "") or ""),
            "known_games": str(current_record.get("known_games", "") or ""),
            "official_site": str(current_record.get("official_site", "") or ""),
            "steam_creator_url": str(current_record.get("steam_creator_url", "") or ""),
            "presskit_url": str(current_record.get("presskit_url", "") or ""),
            "discord_url": str(current_record.get("discord_url", "") or ""),
            "x_url": str(current_record.get("x_url", "") or ""),
            "youtube_url": str(current_record.get("youtube_url", "") or ""),
            "bilibili_url": str(current_record.get("bilibili_url", "") or ""),
            "contact_email": str(current_record.get("contact_email", "") or ""),
            "contact_discord": str(current_record.get("contact_discord", "") or ""),
            "publisher_history": str(current_record.get("publisher_history", "") or ""),
            "self_publish_status": str(current_record.get("self_publish_status", "") or "未确认"),
            "evidence_summary": str(current_record.get("evidence_summary", "") or ""),
            "risk_note": str(current_record.get("risk_note", "") or ""),
            "next_action": str(current_record.get("next_action", "") or ""),
            "confidence": str(current_record.get("confidence", "") or "未确认"),
            "source_urls": str(current_record.get("source_urls", "") or ""),
        }

    source_links = [url for _, url in collect_company_relevant_external_links(external_records)]
    return {
        "company_name": selected_name,
        "company_role_label": display_company_role(selected_role),
        "country_or_region": "",
        "team_size": "",
        "founded_year": "",
        "known_games": game_name,
        "official_site": "",
        "steam_creator_url": infer_steam_creator_url(profile),
        "presskit_url": "",
        "discord_url": "",
        "x_url": "",
        "youtube_url": "",
        "bilibili_url": "",
        "contact_email": "",
        "contact_discord": "",
        "publisher_history": "",
        "self_publish_status": str(selected_target.get("self_publish_status", "") or "未确认"),
        "evidence_summary": "",
        "risk_note": "",
        "next_action": "需确认联系方式",
        "confidence": "未确认",
        "source_urls": "\n".join(source_links),
    }


def save_company_dossier_form_record(appid: str, game_name: str, update_existing: bool, report_action: bool = False) -> bool:
    record_data = collect_company_dossier_form_data(appid, game_name)
    if not record_data["company_name"]:
        st.warning("请先填写公司/团队名。")
        return False
    if update_existing:
        dossier_id = str(st.session_state.get("company_dossier_current_id", "") or "").strip()
        if not dossier_id:
            st.warning("当前没有可更新的公司档案，请先保存新档案。")
            return False
        if not update_company_dossier_record(COMPANY_DOSSIER_CSV_PATH, dossier_id, record_data):
            st.warning("未找到当前档案，未保存修改。")
            return False
        st.success("公司档案已更新。")
    else:
        record = CompanyDossierRecord(**record_data)
        save_company_dossier_to_csv(record, COMPANY_DOSSIER_CSV_PATH)
        st.session_state["company_dossier_current_id"] = record.dossier_id
        st.success(f"开发商档案已保存：{COMPANY_DOSSIER_CSV_PATH}")
    if report_action:
        st.success("已发送到项目画像报告：后续生成或预览 Markdown 时会读取该公司档案。")
    return True


def collect_company_dossier_form_data(appid: str, game_name: str) -> dict:
    role_label = str(st.session_state.get("company_dossier_company_role_label", "未确认") or "未确认").strip()
    company_role = COMPANY_ROLE_BY_LABEL.get(role_label, "unknown")
    return {
        "appid": _clean_company_value(st.session_state.get("company_dossier_appid") or appid),
        "game_name": _clean_company_value(st.session_state.get("company_dossier_game_name") or game_name),
        "company_name": _clean_company_value(st.session_state.get("company_dossier_company_name")),
        "company_role": company_role,
        "country_or_region": _clean_company_value(st.session_state.get("company_dossier_country_or_region")),
        "team_size": _clean_company_value(st.session_state.get("company_dossier_team_size")),
        "founded_year": _clean_company_value(st.session_state.get("company_dossier_founded_year")),
        "known_games": _clean_company_multiline(st.session_state.get("company_dossier_known_games")),
        "official_site": _clean_company_value(st.session_state.get("company_dossier_official_site")),
        "steam_creator_url": _clean_company_value(st.session_state.get("company_dossier_steam_creator_url")),
        "presskit_url": _clean_company_value(st.session_state.get("company_dossier_presskit_url")),
        "discord_url": _clean_company_value(st.session_state.get("company_dossier_discord_url")),
        "x_url": _clean_company_value(st.session_state.get("company_dossier_x_url")),
        "youtube_url": _clean_company_value(st.session_state.get("company_dossier_youtube_url")),
        "bilibili_url": _clean_company_value(st.session_state.get("company_dossier_bilibili_url")),
        "contact_email": _clean_company_value(st.session_state.get("company_dossier_contact_email")),
        "contact_discord": _clean_company_value(st.session_state.get("company_dossier_contact_discord")),
        "publisher_history": _clean_company_multiline(st.session_state.get("company_dossier_publisher_history")),
        "self_publish_status": _clean_company_value(st.session_state.get("company_dossier_self_publish_status")) or "未确认",
        "evidence_summary": _clean_company_multiline(st.session_state.get("company_dossier_evidence_summary")),
        "risk_note": _clean_company_multiline(st.session_state.get("company_dossier_risk_note")),
        "next_action": _clean_company_multiline(st.session_state.get("company_dossier_next_action")),
        "confidence": _clean_company_value(st.session_state.get("company_dossier_confidence")) or "未确认",
        "source_urls": _clean_company_multiline(st.session_state.get("company_dossier_source_urls")),
    }


def render_company_dossier_library_manager(current_appid: str, current_game_name: str) -> None:
    all_records = load_company_dossiers(COMPANY_DOSSIER_CSV_PATH)
    filtered = filter_company_dossiers(all_records, **render_company_dossier_library_filters(current_appid, current_game_name))
    st.caption(f"过滤结果：{len(filtered)} 条；默认显示最近 20 条。")
    visible = filtered.head(20)
    render_company_dossier_library_table(visible)
    render_company_dossier_delete_form(visible)


def render_company_dossier_library_filters(current_appid: str, current_game_name: str) -> dict:
    col1, col2, col3 = st.columns(3)
    with col1:
        company_name = st.text_input("按公司名搜索", key="company_library_filter_company_name")
        appid = st.text_input("按 AppID 搜索", value=current_appid, key="company_library_filter_appid")
    with col2:
        game_name = st.text_input("按游戏名搜索", value=current_game_name, key="company_library_filter_game_name")
        role = st.selectbox("按角色筛选", ["全部"] + list(COMPANY_ROLE_BY_LABEL.keys()), key="company_library_filter_role")
    with col3:
        confidence = st.selectbox("按可信度筛选", ["全部"] + COMPANY_CONFIDENCE_OPTIONS, key="company_library_filter_confidence")
    return {
        "appid": appid,
        "game_name": game_name,
        "company_name": company_name,
        "company_role": role,
        "confidence": confidence,
    }


def render_company_dossier_library_table(records: pd.DataFrame) -> None:
    if records.empty:
        st.info("暂无匹配的公司档案。")
        return
    display_columns = [
        "updated_at",
        "appid",
        "game_name",
        "company_name",
        "company_role",
        "country_or_region",
        "self_publish_status",
        "confidence",
        "next_action",
        "dossier_id",
    ]
    display = records.loc[:, [column for column in display_columns if column in records.columns]].copy()
    if "company_role" in display.columns:
        display["company_role"] = display["company_role"].map(display_company_role)
    st.dataframe(display.rename(columns=COMPANY_DOSSIER_FIELD_LABELS), use_container_width=True, hide_index=True)


def render_company_dossier_delete_form(records: pd.DataFrame) -> None:
    st.markdown("**删除档案**")
    if records.empty:
        st.caption("没有可删除档案。")
        return
    options = build_company_dossier_record_options(records)
    selected_label = st.selectbox("选择要删除的档案", list(options.keys()), key="company_library_delete_id")
    selected_id = options[selected_label]
    confirm = st.checkbox("我确认删除这条公司档案", key="company_library_delete_confirm")
    if st.button("删除选中档案", key="company_library_delete_button"):
        if not confirm:
            st.warning("请先勾选二次确认。")
            return
        deleted_count = delete_company_dossier_records(COMPANY_DOSSIER_CSV_PATH, [selected_id])
        if deleted_count:
            st.success("公司档案已删除。")
            if st.session_state.get("company_dossier_current_id") == selected_id:
                st.session_state["company_dossier_current_id"] = ""
        else:
            st.warning("未找到对应档案，未删除。")


def build_company_dossier_record_options(records: pd.DataFrame) -> dict:
    options = {}
    for _, row in records.iterrows():
        dossier_id = str(row.get("dossier_id", "") or "").strip()
        if not dossier_id:
            continue
        company_name = str(row.get("company_name", "") or "").strip() or "未确认公司"
        game_name = str(row.get("game_name", "") or "").strip() or "未确认游戏"
        updated_at = str(row.get("updated_at", "") or "").strip()
        options[f"{company_name} | {game_name} | {updated_at} | {dossier_id}"] = dossier_id
    return options


def infer_company_role(developer: str, publisher: str) -> str:
    if developer and publisher and developer.casefold() == publisher.casefold():
        return "developer_and_publisher"
    if developer:
        return "developer"
    if publisher:
        return "publisher"
    return "unknown"


def infer_self_publish_status(developer: str, publisher: str) -> str:
    if developer and publisher and developer.casefold() == publisher.casefold():
        return "自发行"
    if publisher and developer and developer.casefold() != publisher.casefold():
        return "有发行商"
    return "未确认"


def infer_steam_creator_url(profile: ProjectProfile) -> str:
    info = profile.raw_store_info or {}
    for key in ["steam_creator_url", "developer_url", "publisher_url", "steam_developer_url", "steam_publisher_url", "creator_url"]:
        value = str(info.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _normalize_company_form_select_values() -> None:
    if st.session_state.get("company_dossier_company_role_label") not in COMPANY_ROLE_BY_LABEL:
        st.session_state["company_dossier_company_role_label"] = "未确认"
    if st.session_state.get("company_dossier_self_publish_status") not in SELF_PUBLISH_STATUS_OPTIONS:
        st.session_state["company_dossier_self_publish_status"] = "未确认"
    if st.session_state.get("company_dossier_confidence") not in COMPANY_CONFIDENCE_OPTIONS:
        st.session_state["company_dossier_confidence"] = "未确认"


def _company_source_value(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"", PLACEHOLDER, "未获取", "未确认"} else text


def _company_display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未确认"


def _join_company_display_values(values: list[object]) -> str:
    items = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in items:
            items.append(text)
    return " / ".join(items)


def _clean_company_value(value) -> str:
    return " ".join(str(value or "").split())


def _clean_company_multiline(value) -> str:
    lines = [" ".join(line.split()) for line in str(value or "").splitlines()]
    return "\n".join(line for line in lines if line)


def render_profile_market_data(profile: ProjectProfile) -> None:
    appid = _external_display_source_value(profile.basic_info.get("AppID", ""))
    game_name = _external_display_source_value(profile.basic_info.get("游戏名", ""))
    all_records = load_market_data(MARKET_DATA_CSV_PATH)
    records = filter_market_data(all_records, appid=appid, game_name=game_name)
    summary = summarize_market_data(records)

    st.markdown("### 第三方市场数据")
    st.info(
        "当前为手动记录卡，不会自动抓取 VGI / Gamalytic / SteamDB 数据。"
        "请打开对应网站搜索后，将关键数据手动录入。"
        "后续 API 接入后再自动填充。"
    )
    render_market_data_summary(summary)

    with st.expander("快速录入市场数据", expanded=True):
        render_market_data_external_entry_links(appid, game_name)
        saved = render_market_data_form(appid, game_name, all_records)
        if saved:
            records = filter_market_data(load_market_data(MARKET_DATA_CSV_PATH), appid=appid, game_name=game_name)
            summary = summarize_market_data(records)
            render_market_data_summary(summary)

    render_market_data_history(records)


def render_market_data_summary(summary: dict) -> None:
    st.markdown("**市场数据摘要**")
    if summary["record_count"] <= 0:
        st.info("暂无第三方市场数据记录。")
        return

    latest = summary["latest_record"]
    countries = format_country_distribution(latest)
    if summary["conflict_note"]:
        st.warning(summary["conflict_note"])
    if summary["is_estimated"]:
        st.caption("估算类数据仅代表第三方或人工估算，不等同于官方后台数据。")

    rows = [
        ("数据来源数", summary["source_count"]),
        ("最新记录日期", summary["latest_date"]),
        ("评测数", latest.get("reviews")),
        ("好评率", latest.get("review_score")),
        ("Followers", latest.get("followers")),
        ("当前在线", latest.get("current_players")),
        ("24h Peak", latest.get("peak_24h")),
        ("估算销量", market_estimated_display(latest.get("estimated_sales"), latest.get("is_estimated"))),
        ("估算收入", market_estimated_display(latest.get("estimated_gross_revenue"), latest.get("is_estimated"))),
        ("平均游玩", latest.get("avg_playtime_hours")),
        ("中位游玩", latest.get("median_playtime_hours")),
        ("主要国家/地区", countries),
        ("数据可信度", latest.get("confidence")),
    ]
    cols = st.columns(2)
    for index, (label, value) in enumerate(rows):
        with cols[index % 2]:
            st.write(f"{label}：{market_display(value)}")


def render_market_data_external_entry_links(appid: str, game_name: str) -> None:
    st.markdown("**外部打开入口**")
    links = build_market_data_external_links(appid, game_name)
    columns = st.columns(5)
    for index, (label, url) in enumerate(links):
        with columns[index % 5]:
            st.link_button(label, url, use_container_width=True)
    st.caption("Gamalytic / VGI 仅打开首页，请复制搜索词到站内搜索；当前不会自动查询或自动估算市场数据。")
    steam_url = f"https://store.steampowered.com/app/{quote(str(appid).strip())}/" if str(appid or "").strip() else ""
    st.markdown("**复制搜索词**")
    copy_cols = st.columns(3)
    with copy_cols[0]:
        st.text_input("复制游戏名", value=str(game_name or "").strip(), key="market_data_copy_game_name")
    with copy_cols[1]:
        st.text_input("复制 AppID", value=str(appid or "").strip(), key="market_data_copy_appid")
    with copy_cols[2]:
        st.text_input("复制 Steam 链接", value=steam_url, key="market_data_copy_steam_url")


def render_market_data_form(appid: str, game_name: str, all_records: pd.DataFrame) -> bool:
    _prepare_market_data_form_state(appid, game_name)

    with st.form("market_data_form"):
        st.caption(
            f"自动带入：AppID {market_display(st.session_state.get('market_data_appid'))} / "
            f"游戏名 {market_display(st.session_state.get('market_data_game_name'))}"
        )
        st.markdown("**手动录入**")
        source_cols = st.columns([1, 2, 1, 1])
        with source_cols[0]:
            st.selectbox("本次保存来源", MARKET_SOURCE_OPTIONS, key="market_data_source")
        with source_cols[1]:
            st.text_input("来源链接 / steamdb_url / vgi_url / gamalytic_url", key="market_data_source_url")
        with source_cols[2]:
            st.text_input("记录日期", key="market_data_data_date")
        with source_cols[3]:
            st.selectbox("数据可信度", MARKET_CONFIDENCE_OPTIONS, key="market_data_confidence")

        quick_col1, quick_col2, quick_col3 = st.columns(3)
        with quick_col1:
            st.markdown("**SteamDB 手动数据**")
            st.text_input("followers", key="market_data_followers")
            st.text_input("peak_ccu / 24h peak", key="market_data_peak_24h")
            st.text_input("current_ccu", key="market_data_current_players")
            st.text_input("wishlist_rank", key="market_data_wishlist_activity_rank")
            st.text_input("top_sellers_rank / wishlists", key="market_data_wishlists")
            st.text_input("reviews", key="market_data_reviews")
            st.text_input("review score", key="market_data_review_score")
        with quick_col2:
            st.markdown("**VGI 手动数据**")
            st.text_input("units_sold", key="market_data_estimated_sales")
            st.text_input("avg_playtime", key="market_data_avg_playtime_hours")
            st.text_input("median_playtime", key="market_data_median_playtime_hours")
            st.text_input("top_country_1", key="market_data_country_top1")
            st.text_input("top_country_1_share", key="market_data_country_top1_share")
            st.text_input("top_country_2", key="market_data_country_top2")
            st.text_input("top_country_2_share", key="market_data_country_top2_share")
        with quick_col3:
            st.markdown("**Gamalytic 手动数据**")
            st.text_input("owners_low", key="market_data_estimated_owners_low")
            st.text_input("owners_mid", key="market_data_estimated_owners_mid")
            st.text_input("owners_high", key="market_data_estimated_owners_high")
            st.text_input("revenue", key="market_data_estimated_gross_revenue")
            st.text_input("estimated downloads", key="market_data_estimated_downloads")
            st.text_input("top_country_3", key="market_data_country_top3")
            st.text_input("top_country_3_share", key="market_data_country_top3_share")
            st.checkbox("is_estimated", value=st.session_state.get("market_data_is_estimated", True), key="market_data_is_estimated")
        st.text_area("notes", key="market_data_notes", height=80)

        with st.expander("高级字段", expanded=False):
            adv_col1, adv_col2, adv_col3 = st.columns(3)
            with adv_col1:
                st.text_input("avg daily CCU", key="market_data_avg_daily_ccu")
                st.text_input("all-time peak", key="market_data_all_time_peak")
            with adv_col2:
                st.caption("SteamDB / VGI / Gamalytic 主要字段已放在上方三列。")
            with adv_col3:
                st.caption("当前不自动抓取第三方市场数据，需人工复制来源和记录日期。")

        save_col, clear_col = st.columns(2)
        save_record = save_col.form_submit_button("保存市场数据")
        clear_form = clear_col.form_submit_button("清空表单")

    if clear_form:
        st.session_state["market_data_clear_requested"] = True
        st.rerun()
    if not save_record:
        return False

    record = build_market_data_record_from_state()
    duplicate_note = find_market_data_duplicate_note(all_records, record)
    if duplicate_note:
        st.warning(duplicate_note)
    try:
        save_market_data_to_csv(record, MARKET_DATA_CSV_PATH)
    except Exception as exc:
        st.session_state["market_data_last_error"] = str(exc)
        st.error(f"保存市场数据失败：{exc}")
        return False
    st.session_state["market_data_last_error"] = ""
    st.success(f"市场数据已保存：{MARKET_DATA_CSV_PATH}")
    return True


def _prepare_market_data_form_state(appid: str, game_name: str) -> None:
    profile_key = f"{appid}|{game_name}"
    should_reset = (
        st.session_state.get("market_data_profile_key") != profile_key
        or st.session_state.pop("market_data_clear_requested", False)
    )
    if not should_reset:
        if st.session_state.get("market_data_source") not in MARKET_SOURCE_OPTIONS:
            st.session_state["market_data_source"] = "其他"
        if st.session_state.get("market_data_confidence") not in MARKET_CONFIDENCE_OPTIONS:
            st.session_state["market_data_confidence"] = "未确认"
        return

    st.session_state["market_data_profile_key"] = profile_key
    defaults = {
        "appid": appid,
        "game_name": game_name,
        "source": "Gamalytic",
        "source_url": "",
        "data_date": datetime.now().strftime("%Y-%m-%d"),
        "reviews": "",
        "review_score": "",
        "followers": "",
        "wishlists": "",
        "wishlist_activity_rank": "",
        "current_players": "",
        "peak_24h": "",
        "avg_daily_ccu": "",
        "all_time_peak": "",
        "estimated_owners_low": "",
        "estimated_owners_mid": "",
        "estimated_owners_high": "",
        "estimated_sales": "",
        "estimated_downloads": "",
        "estimated_gross_revenue": "",
        "avg_playtime_hours": "",
        "median_playtime_hours": "",
        "country_top1": "",
        "country_top1_share": "",
        "country_top2": "",
        "country_top2_share": "",
        "country_top3": "",
        "country_top3_share": "",
        "notes": "",
        "confidence": "未确认",
        "is_estimated": True,
    }
    for key, value in defaults.items():
        st.session_state[f"market_data_{key}"] = value


def build_market_data_record_from_state() -> MarketDataRecord:
    return MarketDataRecord(
        appid=_clean_market_value(st.session_state.get("market_data_appid")),
        game_name=_clean_market_value(st.session_state.get("market_data_game_name")),
        source=_clean_market_value(st.session_state.get("market_data_source")) or "其他",
        source_url=_clean_market_value(st.session_state.get("market_data_source_url")),
        data_date=_clean_market_value(st.session_state.get("market_data_data_date")),
        reviews=_clean_market_value(st.session_state.get("market_data_reviews")),
        review_score=_clean_market_value(st.session_state.get("market_data_review_score")),
        followers=_clean_market_value(st.session_state.get("market_data_followers")),
        wishlists=_clean_market_value(st.session_state.get("market_data_wishlists")),
        wishlist_activity_rank=_clean_market_value(st.session_state.get("market_data_wishlist_activity_rank")),
        current_players=_clean_market_value(st.session_state.get("market_data_current_players")),
        peak_24h=_clean_market_value(st.session_state.get("market_data_peak_24h")),
        avg_daily_ccu=_clean_market_value(st.session_state.get("market_data_avg_daily_ccu")),
        all_time_peak=_clean_market_value(st.session_state.get("market_data_all_time_peak")),
        estimated_owners_low=_clean_market_value(st.session_state.get("market_data_estimated_owners_low")),
        estimated_owners_mid=_clean_market_value(st.session_state.get("market_data_estimated_owners_mid")),
        estimated_owners_high=_clean_market_value(st.session_state.get("market_data_estimated_owners_high")),
        estimated_sales=_clean_market_value(st.session_state.get("market_data_estimated_sales")),
        estimated_downloads=_clean_market_value(st.session_state.get("market_data_estimated_downloads")),
        estimated_gross_revenue=_clean_market_value(st.session_state.get("market_data_estimated_gross_revenue")),
        avg_playtime_hours=_clean_market_value(st.session_state.get("market_data_avg_playtime_hours")),
        median_playtime_hours=_clean_market_value(st.session_state.get("market_data_median_playtime_hours")),
        country_top1=_clean_market_value(st.session_state.get("market_data_country_top1")),
        country_top1_share=_clean_market_value(st.session_state.get("market_data_country_top1_share")),
        country_top2=_clean_market_value(st.session_state.get("market_data_country_top2")),
        country_top2_share=_clean_market_value(st.session_state.get("market_data_country_top2_share")),
        country_top3=_clean_market_value(st.session_state.get("market_data_country_top3")),
        country_top3_share=_clean_market_value(st.session_state.get("market_data_country_top3_share")),
        notes=_clean_market_multiline(st.session_state.get("market_data_notes")),
        confidence=_clean_market_value(st.session_state.get("market_data_confidence")) or "未确认",
        is_estimated="True" if bool(st.session_state.get("market_data_is_estimated")) else "False",
    )


def render_market_data_history(records: pd.DataFrame) -> None:
    st.markdown("**来源对比表**")
    if records.empty:
        st.info("暂无第三方市场数据记录。")
        return

    display = records.copy()
    display["estimated_combo"] = display.apply(
        lambda row: " / ".join(
            part
            for part in [
                market_display(row.get("estimated_owners_mid")),
                market_display(row.get("estimated_sales")),
                market_display(row.get("estimated_downloads")),
            ]
            if part != "未记录"
        ),
        axis=1,
    )
    columns = [
        "source",
        "data_date",
        "reviews",
        "review_score",
        "followers",
        "current_players",
        "avg_daily_ccu",
        "estimated_combo",
        "estimated_gross_revenue",
        "avg_playtime_hours",
        "median_playtime_hours",
        "confidence",
        "source_url",
    ]
    visible = display.loc[:, columns].head(30).rename(columns=MARKET_DATA_FIELD_LABELS)
    visible = visible.applymap(market_display)
    try:
        st.dataframe(
            visible,
            use_container_width=True,
            hide_index=True,
            column_config={"来源链接": st.column_config.LinkColumn("来源链接")},
        )
    except Exception:
        st.dataframe(visible, use_container_width=True, hide_index=True)


def market_display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未记录"


def market_estimated_display(value, is_estimated) -> str:
    text = market_display(value)
    if text == "未记录":
        return text
    return f"{text}（估算）" if str(is_estimated or "").casefold() in {"true", "1", "yes", "y"} else text


def _clean_market_value(value) -> str:
    return " ".join(str(value or "").split())


def _clean_market_multiline(value) -> str:
    lines = [" ".join(line.split()) for line in str(value or "").splitlines()]
    return "\n".join(line for line in lines if line)


def render_profile_external_intel(profile: ProjectProfile) -> None:
    appid = _external_display_source_value(profile.basic_info.get("AppID", ""))
    game_name = _external_display_source_value(profile.basic_info.get("游戏名", ""))
    all_records = load_external_intel(EXTERNAL_INTEL_CSV_PATH)
    records = filter_external_intel(all_records, appid=appid, game_name=game_name)
    summary = summarize_external_intel(records)

    st.markdown("### 外部声量摘要")
    if summary["record_count"] <= 0:
        st.info("暂无外部情报记录。")
    else:
        metric_cols = st.columns(4)
        metric_cols[0].metric("情报记录数", summary["record_count"])
        metric_cols[1].metric("高相关记录数", summary["high_relevance_count"])
        metric_cols[2].metric("YouTube 最高播放", summary["youtube_max_views"] or "未填写")
        metric_cols[3].metric("B站最高播放", summary["bilibili_max_views"] or "未填写")

        status_cols = st.columns(3)
        status_cols[0].write(f"中文视频/文章：{'已有中文侧内容' if summary['has_chinese_content'] else '未填写'}")
        status_cols[1].write(f"官网/Presskit：{'已有' if summary['has_official_or_presskit'] else '未填写'}")
        status_cols[2].write(f"Discord / 社群：{'已有' if summary['has_community'] else '未填写'}")

        for note in summary["rule_notes"]:
            st.caption(note)
        st.markdown("**关键结论 Top 3**")
        if summary["key_takeaways"]:
            for item in summary["key_takeaways"]:
                st.write(f"- {item}")
        else:
            st.write("- 未填写")

    with st.expander("外部情报记录", expanded=False):
        render_external_search_links(game_name)
        saved = render_external_intel_form(appid, game_name)
        if saved:
            records = filter_external_intel(load_external_intel(EXTERNAL_INTEL_CSV_PATH), appid=appid, game_name=game_name)
        render_external_intel_history(records)
        render_current_external_intel_export(records, appid, game_name)

    with st.expander("外部情报库 / 管理", expanded=False):
        render_external_intel_library_manager(all_records, appid, game_name)


def render_external_intel_form(appid: str, game_name: str) -> bool:
    _prepare_external_intel_form_state(appid, game_name)

    with st.form("external_intel_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("AppID", key="external_intel_appid")
            st.text_input("游戏名", key="external_intel_game_name")
            st.selectbox("平台", PLATFORM_OPTIONS, key="external_intel_platform")
            st.text_input("来源链接", key="external_intel_source_url")
            st.text_input("标题", key="external_intel_title")
            st.text_input("作者/频道", key="external_intel_author_or_channel")
            st.text_input("发布时间", key="external_intel_published_at")
        with col2:
            st.text_input("播放/阅读量", key="external_intel_views")
            st.text_input("评论数", key="external_intel_comments")
            st.text_input("点赞数", key="external_intel_likes")
            st.text_input("粉丝/成员数", key="external_intel_followers_or_members")
            st.selectbox("证据类型", EVIDENCE_TYPE_OPTIONS, key="external_intel_evidence_type")
            st.selectbox("情绪", SENTIMENT_OPTIONS, key="external_intel_sentiment")
            st.selectbox("相关度", RELEVANCE_OPTIONS, key="external_intel_relevance")
        st.text_area("关键结论", key="external_intel_key_takeaway", height=80)
        st.text_area("备注", key="external_intel_note", height=80)

        save_col, clear_col = st.columns(2)
        with save_col:
            save_record = st.form_submit_button("保存外部情报")
        with clear_col:
            clear_form = st.form_submit_button("清空表单")

    if clear_form:
        st.session_state["external_intel_clear_requested"] = True
        st.rerun()

    if not save_record:
        return False

    record = ExternalIntelRecord(
        appid=_clean_external_form_value(st.session_state.get("external_intel_appid")),
        game_name=_clean_external_form_value(st.session_state.get("external_intel_game_name")),
        platform=_clean_external_form_value(st.session_state.get("external_intel_platform")),
        source_url=_clean_external_form_value(st.session_state.get("external_intel_source_url")),
        title=_clean_external_form_value(st.session_state.get("external_intel_title")),
        author_or_channel=_clean_external_form_value(st.session_state.get("external_intel_author_or_channel")),
        published_at=_clean_external_form_value(st.session_state.get("external_intel_published_at")),
        views=_clean_external_form_value(st.session_state.get("external_intel_views")),
        comments=_clean_external_form_value(st.session_state.get("external_intel_comments")),
        likes=_clean_external_form_value(st.session_state.get("external_intel_likes")),
        followers_or_members=_clean_external_form_value(st.session_state.get("external_intel_followers_or_members")),
        evidence_type=_clean_external_form_value(st.session_state.get("external_intel_evidence_type")),
        sentiment=_clean_external_form_value(st.session_state.get("external_intel_sentiment")) or "未判断",
        relevance=_clean_external_form_value(st.session_state.get("external_intel_relevance")) or "中",
        key_takeaway=_clean_external_form_value(st.session_state.get("external_intel_key_takeaway")),
        note=_clean_external_form_value(st.session_state.get("external_intel_note")),
    )
    duplicate_note = find_external_intel_duplicate_note(record)
    if duplicate_note:
        st.warning(duplicate_note)
    save_external_intel_to_csv(record, EXTERNAL_INTEL_CSV_PATH)
    st.success(f"外部情报已保存：{EXTERNAL_INTEL_CSV_PATH}")
    return True


def _prepare_external_intel_form_state(appid: str, game_name: str) -> None:
    current_profile_key = f"{appid}|{game_name}"
    should_reset = (
        st.session_state.get("external_intel_profile_key") != current_profile_key
        or st.session_state.pop("external_intel_clear_requested", False)
    )
    if should_reset:
        st.session_state["external_intel_profile_key"] = current_profile_key
        st.session_state["external_intel_appid"] = appid
        st.session_state["external_intel_game_name"] = game_name
        st.session_state["external_intel_platform"] = "YouTube"
        st.session_state["external_intel_source_url"] = ""
        st.session_state["external_intel_title"] = ""
        st.session_state["external_intel_author_or_channel"] = ""
        st.session_state["external_intel_published_at"] = ""
        st.session_state["external_intel_views"] = ""
        st.session_state["external_intel_comments"] = ""
        st.session_state["external_intel_likes"] = ""
        st.session_state["external_intel_followers_or_members"] = ""
        st.session_state["external_intel_evidence_type"] = "视频"
        st.session_state["external_intel_sentiment"] = "未判断"
        st.session_state["external_intel_relevance"] = "中"
        st.session_state["external_intel_key_takeaway"] = ""
        st.session_state["external_intel_note"] = ""

    if st.session_state.get("external_intel_platform") not in PLATFORM_OPTIONS:
        st.session_state["external_intel_platform"] = "其他"
    if st.session_state.get("external_intel_evidence_type") not in EVIDENCE_TYPE_OPTIONS:
        st.session_state["external_intel_evidence_type"] = "其他"
    if st.session_state.get("external_intel_sentiment") not in SENTIMENT_OPTIONS:
        st.session_state["external_intel_sentiment"] = "未判断"
    if st.session_state.get("external_intel_relevance") not in RELEVANCE_OPTIONS:
        st.session_state["external_intel_relevance"] = "中"


def render_external_search_links(game_name: str) -> None:
    st.markdown("**外部搜索入口**")
    if not game_name:
        st.caption("未获取游戏名，暂不能生成外部搜索入口。")
        return
    links = build_external_search_links(game_name)
    columns = st.columns(3)
    for index, (label, url) in enumerate(links):
        with columns[index % 3]:
            st.link_button(label, url, use_container_width=True)


def build_external_search_links(game_name: str) -> list[tuple[str, str]]:
    name = str(game_name or "").strip()
    return [
        ("YouTube gameplay", f"https://www.youtube.com/results?search_query={quote(name + ' gameplay')}"),
        ("YouTube review", f"https://www.youtube.com/results?search_query={quote(name + ' review')}"),
        ("B站 试玩", f"https://search.bilibili.com/all?keyword={quote(name + ' 试玩')}"),
        ("B站 评测", f"https://search.bilibili.com/all?keyword={quote(name + ' 评测')}"),
        ("Google review", f"https://www.google.com/search?q={quote(name + ' review')}"),
        ("X/Twitter", f"https://twitter.com/search?q={quote(name)}&src=typed_query"),
        ("Bluesky", f"https://bsky.app/search?q={quote(name)}"),
        ("Reddit", f"https://www.reddit.com/search/?q={quote(name)}"),
        ("小黑盒", f"https://www.xiaoheihe.cn/search?keyword={quote(name)}"),
        ("NGA 站内搜索", f"https://www.baidu.com/s?wd={quote('site:ngabbs.com ' + name)}"),
        ("百度站内搜索", f"https://www.baidu.com/s?wd={quote(name)}"),
    ]


def render_external_intel_history(records: pd.DataFrame) -> None:
    st.markdown("**当前项目历史记录**")
    if records.empty:
        st.info("暂无外部情报记录。")
        return

    visible_records = records.tail(20).iloc[::-1]
    header = "| 平台 | 标题 | 播放/阅读量 | 评论数 | 相关度 | 关键结论 | 来源链接 |"
    separator = "| --- | --- | --- | --- | --- | --- | --- |"
    lines = [header, separator]
    for _, row in visible_records.iterrows():
        source_url = str(row.get("source_url", "") or "").strip()
        source_link = f"[打开]({source_url})" if source_url else "未填写"
        lines.append(
            "| "
            + " | ".join(
                [
                    _markdown_table_cell(_external_display(row.get("platform"))),
                    _markdown_table_cell(_external_display(row.get("title"))),
                    _markdown_table_cell(_external_count_display(row.get("views"))),
                    _markdown_table_cell(_external_count_display(row.get("comments"))),
                    _markdown_table_cell(_external_display(row.get("relevance"))),
                    _markdown_table_cell(_external_display(row.get("key_takeaway"))),
                    source_link,
                ]
            )
            + " |"
        )
    st.markdown("\n".join(lines))


def render_current_external_intel_export(records: pd.DataFrame, appid: str, game_name: str) -> None:
    if st.button("导出当前项目外部情报 CSV", key="export_current_external_intel"):
        if records.empty:
            st.info("当前项目暂无外部情报记录可导出。")
            return
        SEARCH_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        export_key = appid or game_name or "unknown"
        export_path = SEARCH_EXPORT_DIR / f"external_intel_{sanitize_export_filename(export_key)}.csv"
        records.to_csv(export_path, index=False, encoding="utf-8-sig")
        st.success(f"当前项目外部情报已导出：{export_path}")


def render_external_intel_library_manager(all_records: pd.DataFrame, current_appid: str, current_game_name: str) -> None:
    refresh_col, status_col = st.columns([1, 3])
    with refresh_col:
        if st.button("刷新外部情报记录", key="external_library_refresh", use_container_width=True):
            st.session_state["external_intel_last_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    with status_col:
        st.caption(f"外部情报最后读取时间：{st.session_state.get('external_intel_last_loaded_at') or st.session_state.get('home_last_loaded_at') or '未记录'}")
    all_records = load_external_intel(EXTERNAL_INTEL_CSV_PATH)
    filters = render_external_intel_library_filters(current_appid, current_game_name)
    filtered = filter_external_intel_library(all_records, **filters)
    st.caption(f"过滤结果：{len(filtered)} 条")
    render_external_intel_library_table(filtered)
    render_external_intel_links(filtered)
    render_external_intel_edit_form(filtered)
    render_external_intel_delete_form(filtered)
    render_external_intel_dedupe_tools(all_records)


def render_external_intel_library_filters(current_appid: str, current_game_name: str) -> dict:
    st.markdown("**过滤器**")
    col1, col2, col3 = st.columns(3)
    with col1:
        appid = st.text_input("AppID", value=current_appid, key="external_library_filter_appid")
        platform = st.selectbox("平台", ["全部"] + PLATFORM_OPTIONS, key="external_library_filter_platform")
    with col2:
        game_name = st.text_input("游戏名", value=current_game_name, key="external_library_filter_game_name")
        relevance = st.selectbox("相关度", ["全部"] + RELEVANCE_OPTIONS, key="external_library_filter_relevance")
    with col3:
        sentiment = st.selectbox("情绪", ["全部"] + SENTIMENT_OPTIONS, key="external_library_filter_sentiment")
        evidence_type = st.selectbox("证据类型", ["全部"] + EVIDENCE_TYPE_OPTIONS, key="external_library_filter_evidence_type")
    return {
        "appid": appid,
        "game_name": game_name,
        "platform": platform,
        "relevance": relevance,
        "sentiment": sentiment,
        "evidence_type": evidence_type,
    }


def render_external_intel_library_table(records: pd.DataFrame) -> None:
    st.markdown("**情报库记录**")
    display_columns = [
        "created_at",
        "appid",
        "game_name",
        "platform",
        "title",
        "author_or_channel",
        "views",
        "comments",
        "relevance",
        "sentiment",
        "key_takeaway",
        "source_url",
    ]
    if records.empty:
        st.info("暂无匹配的外部情报记录。")
        return
    display = records.loc[:, [column for column in display_columns if column in records.columns]].copy()
    st.dataframe(display.rename(columns=EXTERNAL_INTEL_FIELD_LABELS), use_container_width=True, hide_index=True)


def render_external_intel_links(records: pd.DataFrame) -> None:
    if records.empty:
        return
    link_records = records.loc[records["source_url"].astype(str).str.strip() != ""].tail(10).iloc[::-1]
    if link_records.empty:
        return
    st.markdown("**可点击来源链接**")
    for _, row in link_records.iterrows():
        platform = _external_display(row.get("platform"))
        title = _external_display(row.get("title"))
        source_url = str(row.get("source_url", "") or "").strip()
        st.markdown(f"- {platform} · {title}：[打开链接]({source_url})")


def render_external_intel_edit_form(records: pd.DataFrame) -> None:
    st.markdown("**编辑记录**")
    if records.empty:
        st.caption("没有可编辑记录。")
        return
    options = build_external_intel_record_options(records)
    selected_label = st.selectbox("选择 record_id", list(options.keys()), key="external_library_edit_record_id")
    selected = options[selected_label]
    record = records.loc[records["record_id"].astype(str).str.strip() == selected["record_id"]]
    if record.empty:
        st.warning("未找到选中的外部情报记录。")
        return
    row = record.iloc[0]
    with st.form("external_intel_edit_form"):
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox("平台", PLATFORM_OPTIONS, index=_option_index(PLATFORM_OPTIONS, row.get("platform"), "其他"), key="external_edit_platform")
            title = st.text_input("标题", value=str(row.get("title", "") or ""), key="external_edit_title")
            author_or_channel = st.text_input("作者/频道", value=str(row.get("author_or_channel", "") or ""), key="external_edit_author")
            published_at = st.text_input("发布时间", value=str(row.get("published_at", "") or ""), key="external_edit_published_at")
            evidence_type = st.selectbox("证据类型", EVIDENCE_TYPE_OPTIONS, index=_option_index(EVIDENCE_TYPE_OPTIONS, row.get("evidence_type"), "其他"), key="external_edit_evidence_type")
        with col2:
            views = st.text_input("播放/阅读量", value=str(row.get("views", "") or ""), key="external_edit_views")
            comments = st.text_input("评论数", value=str(row.get("comments", "") or ""), key="external_edit_comments")
            likes = st.text_input("点赞数", value=str(row.get("likes", "") or ""), key="external_edit_likes")
            followers_or_members = st.text_input("粉丝/成员数", value=str(row.get("followers_or_members", "") or ""), key="external_edit_followers")
            sentiment = st.selectbox("情绪", SENTIMENT_OPTIONS, index=_option_index(SENTIMENT_OPTIONS, row.get("sentiment"), "未判断"), key="external_edit_sentiment")
            relevance = st.selectbox("相关度", RELEVANCE_OPTIONS, index=_option_index(RELEVANCE_OPTIONS, row.get("relevance"), "中"), key="external_edit_relevance")
        key_takeaway = st.text_area("关键结论", value=str(row.get("key_takeaway", "") or ""), height=80, key="external_edit_key_takeaway")
        note = st.text_area("备注", value=str(row.get("note", "") or ""), height=80, key="external_edit_note")
        save_edit = st.form_submit_button("保存修改")

    if save_edit:
        updates = {
            "platform": platform,
            "title": title,
            "author_or_channel": author_or_channel,
            "published_at": published_at,
            "views": views,
            "comments": comments,
            "likes": likes,
            "followers_or_members": followers_or_members,
            "evidence_type": evidence_type,
            "sentiment": sentiment,
            "relevance": relevance,
            "key_takeaway": key_takeaway,
            "note": note,
        }
        try:
            success = update_external_intel_record(EXTERNAL_INTEL_CSV_PATH, selected["record_id"], updates)
        except Exception as exc:
            st.error(f"保存修改失败：{exc}")
            return
        if success:
            st.success("外部情报记录已更新。")
        else:
            st.warning("未找到对应记录，未保存修改。")


def render_external_intel_delete_form(records: pd.DataFrame) -> None:
    st.markdown("**删除记录**")
    if records.empty:
        st.caption("没有可删除记录。")
        return
    options = build_external_intel_record_options(records)
    selected_label = st.selectbox("选择要删除的 record_id", list(options.keys()), key="external_library_delete_record_id")
    selected = options[selected_label]
    confirm = st.checkbox("我确认删除这条外部情报", key="external_library_delete_confirm")
    if st.button("删除选中记录", key="external_library_delete_button"):
        if not confirm:
            st.warning("请先勾选二次确认。")
            return
        try:
            deleted_count = delete_external_intel_records(EXTERNAL_INTEL_CSV_PATH, [selected["record_id"]])
        except Exception as exc:
            st.error(f"删除失败：{exc}")
            return
        if deleted_count:
            st.success("外部情报记录已删除。")
        else:
            st.warning("未找到对应记录，未删除。")


def render_external_intel_dedupe_tools(all_records: pd.DataFrame) -> None:
    st.markdown("**去重**")
    if st.button("扫描疑似重复", key="external_library_scan_duplicates"):
        st.session_state["external_intel_duplicates"] = find_duplicate_external_intel(all_records)
    duplicates = st.session_state.get("external_intel_duplicates")
    if not isinstance(duplicates, pd.DataFrame):
        return
    if duplicates.empty:
        st.info("未发现疑似重复记录。")
        return
    display_columns = ["duplicate_rule", "created_at", "appid", "game_name", "platform", "title", "source_url", "record_id", "keep_record_id"]
    st.dataframe(duplicates.loc[:, display_columns], use_container_width=True, hide_index=True)
    delete_ids = duplicate_record_ids_to_delete(duplicates)
    st.caption(f"将删除 {len(delete_ids)} 条重复记录，只保留每组最早 created_at 的一条。")
    confirm = st.checkbox("我确认删除重复项，只保留最早记录", key="external_library_dedupe_confirm")
    if st.button("删除重复项，只保留最早 created_at 的一条", key="external_library_delete_duplicates"):
        if not confirm:
            st.warning("请先勾选二次确认。")
            return
        try:
            deleted_count = delete_external_intel_records(EXTERNAL_INTEL_CSV_PATH, delete_ids)
        except Exception as exc:
            st.error(f"删除重复项失败：{exc}")
            return
        st.success(f"已删除 {deleted_count} 条重复记录。")
        st.session_state["external_intel_duplicates"] = find_duplicate_external_intel(load_external_intel(EXTERNAL_INTEL_CSV_PATH))


def build_external_intel_record_options(records: pd.DataFrame) -> dict:
    options = {}
    for _, row in records.iterrows():
        record_id = str(row.get("record_id", "") or "").strip()
        if not record_id:
            continue
        title = str(row.get("title", "") or "").strip() or "未填写标题"
        platform = str(row.get("platform", "") or "").strip() or "未填写平台"
        label = f"{platform} | {title[:40]} | {record_id}"
        options[label] = {"record_id": record_id}
    return options


def _option_index(options: list[str], value, fallback: str) -> int:
    clean = str(value or "").strip()
    if clean in options:
        return options.index(clean)
    return options.index(fallback) if fallback in options else 0


def sanitize_export_filename(value: str) -> str:
    clean = re.sub(r'[<>:"/\\|?*\s]+', "_", str(value or "").strip())
    clean = clean.strip("._")
    return clean[:80] or "unknown"


def find_external_intel_duplicate_note(record: ExternalIntelRecord) -> str:
    source_url = str(record.source_url or "").strip().casefold()
    if not source_url:
        return ""
    records = load_external_intel(EXTERNAL_INTEL_CSV_PATH)
    if records.empty:
        return ""
    same_url = records["source_url"].astype(str).str.strip().str.casefold().eq(source_url)
    appid = str(record.appid or "").strip()
    if appid and (same_url & records["appid"].astype(str).str.strip().eq(appid)).any():
        return "疑似重复：已有相同 AppID + source_url 的外部情报记录。"
    game_name = " ".join(str(record.game_name or "").split()).casefold()
    if game_name:
        names = records["game_name"].astype(str).map(lambda value: " ".join(value.split()).casefold())
        if (same_url & names.eq(game_name)).any():
            return "疑似重复：已有相同游戏名 + source_url 的外部情报记录。"
    return ""


def _external_display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未填写"


def _external_count_display(value) -> str:
    clean = _external_display(value)
    if clean == "未填写":
        return clean
    parsed = parse_count(clean)
    return format_count(parsed) if parsed else clean


def _external_display_source_value(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"", PLACEHOLDER, "未获取", "未确认"} else text


def _clean_external_form_value(value) -> str:
    return " ".join(str(value or "").split())


def _markdown_table_cell(value: str) -> str:
    return str(value or "未填写").replace("|", "\\|").replace("\n", " ")


def render_profile_steam_competitors(profile: ProjectProfile) -> None:
    """Render Steam competitor candidate finder for the current profile."""
    st.markdown("### Steam 竞品候选")
    option_col, action_col = st.columns([2, 1])
    with option_col:
        ignore_cache = st.checkbox("忽略缓存，重新搜索", value=False, key="steam_candidate_ignore_cache")
    with action_col:
        search_candidates = st.button("自动查找 Steam 竞品候选", key="steam_candidate_search")

    if search_candidates:
        game_info = build_competitor_finder_input(profile)
        user_keywords = st.session_state.get("profile_user_keywords", "")
        result = find_steam_competitor_candidates(
            game_info,
            STEAM_COMPETITOR_CACHE_PATH,
            user_keywords=user_keywords,
            external_title_clues=st.session_state.get("profile_external_title_clues", ""),
            ignore_cache=ignore_cache,
        )
        st.session_state["steam_candidate_result_message"] = result.message
        st.session_state["steam_candidate_result_success"] = result.success
        st.session_state["steam_candidate_result_used_cache"] = result.used_cache
        st.session_state["steam_candidate_results"] = result.candidates
        st.session_state["steam_candidate_keywords"] = result.keywords

    message = st.session_state.get("steam_candidate_result_message", "")
    if message:
        if st.session_state.get("steam_candidate_result_success"):
            cache_note = "（来自缓存）" if st.session_state.get("steam_candidate_result_used_cache") else ""
            st.success(f"{message}{cache_note}")
        else:
            st.warning(message)

    keywords = st.session_state.get("steam_candidate_keywords", [])
    if keywords:
        st.caption("搜索关键词：" + " / ".join(str(keyword) for keyword in keywords))

    candidates = st.session_state.get("steam_candidate_results", [])
    if not candidates:
        return

    high_mid_candidates = [candidate for candidate in candidates if candidate.match_level in {"高", "中"}]
    low_candidates = [candidate for candidate in candidates if candidate.match_level == "低"]
    visible_candidates = high_mid_candidates[:10]
    if visible_candidates:
        st.caption("默认显示前 10 个高/中匹配候选。")
        render_steam_candidate_table(profile, visible_candidates)
    else:
        st.info("暂无高/中匹配候选，可展开查看低匹配候选。")
    with st.expander(f"显示低匹配候选（{len(low_candidates)}）", expanded=False):
        if low_candidates:
            render_steam_candidate_table(profile, low_candidates)
        else:
            st.write("暂无低匹配候选。")


def build_competitor_finder_input(profile: ProjectProfile) -> dict:
    info = dict(profile.raw_store_info or {})
    info.setdefault("appid", "" if profile.basic_info.get("AppID") == PLACEHOLDER else profile.basic_info.get("AppID", ""))
    info.setdefault("name", "" if profile.basic_info.get("游戏名") == PLACEHOLDER else profile.basic_info.get("游戏名", ""))
    info.setdefault("developer", "" if profile.basic_info.get("开发商") == PLACEHOLDER else profile.basic_info.get("开发商", ""))
    info.setdefault("publisher", "" if profile.basic_info.get("发行商") == PLACEHOLDER else profile.basic_info.get("发行商", ""))
    if not info.get("tags"):
        tags = profile.basic_info.get("类型/标签", "")
        info["tags"] = "" if tags == PLACEHOLDER else tags
    return info


def render_steam_candidate_table(profile: ProjectProfile, candidates: list[SteamCompetitorCandidate]) -> None:
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "候选游戏": candidate.candidate_name,
                "AppID": candidate.candidate_appid,
                "价格": candidate.candidate_price or PLACEHOLDER,
                "发售日": candidate.candidate_release_date or PLACEHOLDER,
                "评价": candidate.candidate_review_summary or PLACEHOLDER,
                "来源关键词": candidate.source_keyword,
                "匹配等级": candidate.match_level,
                "匹配分数": candidate.match_score,
                "匹配理由": candidate.match_reason,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for index, candidate in enumerate(candidates):
        with st.container():
            st.markdown(f"**{candidate.candidate_name}**")
            cols = st.columns([1, 1, 1, 1, 3])
            with cols[0]:
                st.link_button("打开 Steam 页面", candidate.candidate_steam_url, use_container_width=True)
            with cols[1]:
                if st.button("加入候选池", key=f"add_steam_candidate_{candidate.candidate_appid}_{index}"):
                    save_steam_candidate_to_pool(profile, candidate, "待确认")
            with cols[2]:
                if st.button("排除", key=f"exclude_steam_candidate_{candidate.candidate_appid}_{index}"):
                    save_steam_candidate_to_pool(profile, candidate, "排除")
            with cols[3]:
                st.metric("匹配", f"{candidate.match_level} {candidate.match_score}")
            with cols[4]:
                st.caption(candidate.match_reason or "匹配度待人工确认。")


def save_steam_candidate_to_pool(
    profile: ProjectProfile,
    candidate: SteamCompetitorCandidate,
    decision: str,
) -> None:
    if steam_candidate_exists(profile, candidate):
        st.info("该候选已存在于候选池，不重复写入。")
        return
    data = steam_candidate_to_dict(candidate)
    data["user_decision"] = decision
    candidate_record = build_candidate_from_form(data)
    save_candidate_to_csv(candidate_record, CANDIDATE_CSV_PATH)
    st.success(f"已写入候选池：{candidate.candidate_name}（{decision}）")


def steam_candidate_exists(profile: ProjectProfile, candidate: SteamCompetitorCandidate) -> bool:
    candidates = load_candidates(CANDIDATE_CSV_PATH)
    if candidates.empty or "candidate_appid" not in candidates.columns:
        return False
    target_appid = str(candidate.target_appid or profile.basic_info.get("AppID", "")).strip()
    target_name = str(candidate.target_game_name or profile.basic_info.get("游戏名", "")).strip()
    candidate_appid = str(candidate.candidate_appid).strip()
    if not candidate_appid:
        return False

    mask = candidates["candidate_appid"].astype(str).str.strip().eq(candidate_appid)
    if target_appid and "target_appid" in candidates.columns:
        mask = mask & candidates["target_appid"].astype(str).str.strip().eq(target_appid)
    elif target_name and "target_game_name" in candidates.columns:
        mask = mask & candidates["target_game_name"].astype(str).str.strip().str.casefold().eq(target_name.casefold())
    return bool(mask.any())


def render_profile_actions(profile: ProjectProfile) -> None:
    """Render save, export, and cross-module handoff actions."""
    st.markdown("### 操作")
    appid = profile_appid(profile)
    steam_url = str(profile.basic_info.get("Steam 链接", "") or "").strip()
    if not steam_url and appid:
        steam_url = f"https://store.steampowered.com/app/{appid}/"
    steamdb_url = f"https://steamdb.info/app/{appid}/" if appid else ""

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("保存为项目记录", key="profile_save_project"):
            save_profile_as_project(profile, allow_duplicate=False)
    with col2:
        if st.button("生成 Markdown 画像报告", key="profile_export_md"):
            markdown_path, _ = save_profile_reports(
                profile,
                PROFILE_REPORT_DIR,
                EXTERNAL_INTEL_CSV_PATH,
                COMPANY_DOSSIER_CSV_PATH,
                MARKET_DATA_CSV_PATH,
                STEAM_NEWS_CACHE_DIR,
                STEAM_REVIEW_PREVIEW_CACHE_DIR,
            )
            st.success(f"Markdown 画像报告已生成：{markdown_path}")
    with col3:
        if st.button("发送到搜索中心", key="profile_send_search"):
            send_profile_to_search_center(profile)
    with col4:
        if steam_url:
            st.link_button("打开 Steam", steam_url, use_container_width=True)
        else:
            st.button("打开 Steam", disabled=True, key="profile_open_steam_disabled")
    with col5:
        if steamdb_url:
            st.link_button("打开 SteamDB", steamdb_url, use_container_width=True)
        else:
            st.button("打开 SteamDB", disabled=True, key="profile_open_steamdb_disabled")

    render_profile_candidate_pool_actions(profile)

    duplicate_appid = st.session_state.get("profile_pending_duplicate_appid", "")
    if duplicate_appid:
        st.warning("该项目已存在，是否追加为新记录或更新旧记录？当前 V0.4 先支持追加为新记录。")
        if st.button("确认追加为新记录", key="profile_confirm_append_project"):
            save_profile_as_project(profile, allow_duplicate=True)
            st.session_state["profile_pending_duplicate_appid"] = ""

    with st.expander("更多操作", expanded=False):
        more_col1, more_col2 = st.columns(2)
        with more_col1:
            if st.button("生成 txt 画像报告", key="profile_export_txt"):
                _, txt_path = save_profile_reports(
                    profile,
                    PROFILE_REPORT_DIR,
                    EXTERNAL_INTEL_CSV_PATH,
                    COMPANY_DOSSIER_CSV_PATH,
                    MARKET_DATA_CSV_PATH,
                    STEAM_NEWS_CACHE_DIR,
                    STEAM_REVIEW_PREVIEW_CACHE_DIR,
                )
                st.success(f"TXT 画像报告已生成：{txt_path}")
        with more_col2:
            if st.button("发送到竞品候选发现器", key="profile_send_candidate"):
                send_profile_to_candidate_finder(profile)

        if st.checkbox("预览 Markdown 画像报告", value=False, key="profile_show_markdown_preview"):
            external_records = filter_external_intel(
                load_external_intel(EXTERNAL_INTEL_CSV_PATH),
                appid=profile.basic_info.get("AppID", ""),
                game_name=profile.basic_info.get("游戏名", ""),
            )
            company_records = filter_company_dossiers_for_project(
                load_company_dossiers(COMPANY_DOSSIER_CSV_PATH),
                appid=profile.basic_info.get("AppID", ""),
                game_name=profile.basic_info.get("游戏名", ""),
            )
            market_records = filter_market_data(
                load_market_data(MARKET_DATA_CSV_PATH),
                appid=profile.basic_info.get("AppID", ""),
                game_name=profile.basic_info.get("游戏名", ""),
            )
            steam_news_result = st.session_state.get(f"profile_steam_news_result_{appid}", {}) if appid else {}
            if not steam_news_result and appid:
                steam_news_result = get_steam_news_for_app(
                    appid,
                    STEAM_NEWS_CACHE_DIR,
                    count=5,
                    maxlength=500,
                    force_refresh=False,
                )
            review_preview_result = st.session_state.get(f"profile_review_preview_result_{appid}", {}) if appid else {}
            if not review_preview_result and appid:
                review_preview_result = get_steam_review_preview(
                    appid,
                    STEAM_REVIEW_PREVIEW_CACHE_DIR,
                    language="schinese",
                    num_per_group=3,
                    force_refresh=False,
                )
            st.code(
                profile_to_markdown(
                    profile,
                    external_records,
                    company_records,
                    market_records,
                    steam_news_result=steam_news_result,
                    steam_review_preview_result=review_preview_result,
                ),
                language="markdown",
            )


def profile_candidate_data(profile: ProjectProfile) -> dict:
    info = profile.raw_store_info or {}
    basic = profile.basic_info or {}
    appid = profile_appid(profile)
    steam_url = clean_candidate_value(basic.get("Steam 链接") or info.get("steam_url")) or steam_url_from_appid(appid)
    return {
        "appid": appid,
        "game_name": clean_candidate_value(basic.get("游戏名") or info.get("name") or info.get("game_name")),
        "steam_url": steam_url,
        "steamdb_url": steamdb_app_url_from_appid(appid),
        "developer": clean_candidate_value(basic.get("开发商") or info.get("developer")),
        "publisher": clean_candidate_value(basic.get("发行商") or info.get("publisher")),
        "release_status": clean_candidate_value(basic.get("发售状态") or info.get("release_date")),
        "release_date": clean_candidate_value(info.get("release_date") or basic.get("发售日期") or basic.get("发售状态")),
        "has_demo": clean_candidate_value(info.get("has_demo") or basic.get("Demo")),
        "supports_schinese": clean_candidate_value(info.get("supports_schinese") or basic.get("简中")),
        "genres_tags": clean_candidate_value(basic.get("类型/标签") or info.get("genres_text") or info.get("tags_text")),
        "price": clean_candidate_value(info.get("price") or basic.get("价格")),
        "review_score": clean_candidate_value(info.get("review_score_desc") or info.get("positive_rate")),
        "review_count": clean_candidate_value(info.get("review_total")),
        "median_playtime": clean_candidate_value(info.get("median_playtime_hours")),
        "avg_playtime": clean_candidate_value(info.get("avg_playtime_hours")),
        "source": "项目画像",
        "source_url": steam_url,
        "next_action": "判断优先级",
    }


def render_profile_candidate_pool_actions(profile: ProjectProfile) -> None:
    data = profile_candidate_data(profile)
    appid = data.get("appid", "")
    existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid) if appid else {}
    with st.container(border=True):
        st.markdown("**候选池操作**")
        if existing:
            st.caption(
                "已在候选池："
                f"{existing.get('stage') or '新发现'} / "
                f"{existing.get('priority') or '未定'} / "
                f"{existing.get('next_action') or '未填写下一步'}"
            )
        elif not appid:
            st.caption("当前画像缺少 AppID，可临时加入候选池并标记为资料不足。")
        else:
            st.caption("当前项目尚未加入候选池。")

        action_cols = st.columns(5)
        if existing:
            if action_cols[0].button("更新候选池信息", key="profile_candidate_update_basic", use_container_width=True):
                ok, message = update_candidate_pool_basic_info_from_mapping(data, source="项目画像")
                if ok:
                    st.success(message)
                else:
                    st.info(message)
        elif action_cols[0].button("加入候选池", key="profile_candidate_add", use_container_width=True):
            save_mapping_to_candidate_pool(data, source="项目画像", stage="新发现", success_prefix="已加入项目候选池")
        if action_cols[1].button("标记为值得联系", key="profile_candidate_contact", use_container_width=True):
            save_mapping_to_candidate_pool(
                {**data, "next_action": "联系开发商 / 发行方"},
                source="项目画像",
                stage="值得联系",
                priority="高",
                success_prefix="候选状态已更新",
                force_status_updates=True,
            )
        if action_cols[2].button("标记为待试玩", key="profile_candidate_demo", use_container_width=True):
            save_mapping_to_candidate_pool(
                {**data, "next_action": "补 Demo 试玩"},
                source="项目画像",
                stage="待试玩",
                success_prefix="候选状态已更新",
                force_status_updates=True,
            )
        if action_cols[3].button("标记为放弃", key="profile_candidate_reject", use_container_width=True):
            save_mapping_to_candidate_pool(
                {**data, "next_action": "放弃", "reject_reason": "项目画像人工标记放弃"},
                source="项目画像",
                stage="放弃",
                success_prefix="候选状态已更新",
                force_status_updates=True,
            )
        action_cols[4].caption("下方可更新状态")

        with st.expander("更新候选池状态", expanded=False):
            selected_stage = st.selectbox("stage", STAGE_OPTIONS, key="profile_candidate_stage")
            selected_priority = st.selectbox("priority", PRIORITY_OPTIONS, key="profile_candidate_priority")
            next_action = st.text_input("next_action", value=existing.get("next_action", "") if existing else "")
            owner_note = st.text_area("owner_note", value=existing.get("owner_note", "") if existing else "", height=80)
            reject_reason = st.text_input("reject_reason", value=existing.get("reject_reason", "") if existing else "")
            archived = st.checkbox(
                "归档",
                value=str(existing.get("is_archived", "")).casefold() in {"true", "1", "yes", "y"} if existing else False,
            )
            if st.button("保存状态", key="profile_candidate_status_save"):
                save_mapping_to_candidate_pool(
                    {
                        **data,
                        "next_action": next_action,
                        "owner_note": owner_note,
                        "reject_reason": reject_reason,
                        "is_archived": "True" if archived else "False",
                    },
                    source="项目画像",
                    stage=selected_stage,
                    priority=selected_priority,
                    success_prefix="候选状态已更新",
                    force_status_updates=True,
                )


def save_profile_as_project(profile: ProjectProfile, allow_duplicate: bool = False) -> None:
    """Append a profile draft to the existing project CSV without overwriting rows."""
    summary = profile_summary_for_project(profile)
    appid = str(summary.get("appid", "")).strip()
    if appid and not allow_duplicate and project_appid_exists(appid):
        st.session_state["profile_pending_duplicate_appid"] = appid
        st.warning("该项目已存在，是否追加为新记录或更新旧记录？当前 V0.4 先支持追加为新记录。")
        return

    project = build_project_from_form(summary)
    saved_csv_path = save_project_to_csv(project, CSV_PATH)
    upsert_candidate_pool_record(
        candidate_record_from_mapping(
            profile_candidate_data(profile),
            source="项目画像保存",
            stage="新发现",
        ),
        CANDIDATE_POOL_CSV_PATH,
    )
    st.success(f"项目画像已保存为项目记录：{saved_csv_path}")


def project_appid_exists(appid: str) -> bool:
    if not str(appid).strip():
        return False
    projects = load_projects(CSV_PATH, include_deleted=True)
    if projects.empty or "appid" not in projects.columns:
        return False
    return projects["appid"].astype(str).str.strip().eq(str(appid).strip()).any()


def send_profile_to_search_center(profile: ProjectProfile) -> None:
    """Pre-fill search center fields and generate navigation rows."""
    search_values = build_search_values_from_profile(profile)
    apply_search_center_values(search_values)
    st.session_state["search_keyword_limit"] = max(20, len(profile.search_keywords))
    try:
        platforms = load_search_platforms(SEARCH_PLATFORM_CONFIG_PATH)
        navigation_table = build_platform_navigation(
            SearchCenterInput(**search_values),
            platforms,
            limit=int(st.session_state.get("search_keyword_limit", 20)),
        )
    except Exception as exc:
        st.error(f"搜索中心生成失败，不影响画像草稿：{exc}")
        return
    st.session_state["search_navigation_table"] = navigation_table
    st.success("已发送到搜索中心并生成搜索入口，可切换到“搜索中心”Tab 查看。")


def build_search_values_from_profile(profile: ProjectProfile) -> dict:
    info = profile.raw_store_info or {}
    tags = profile.basic_info.get("类型/标签", "")
    english_keywords = ", ".join(
        keyword
        for keyword in profile.search_keywords
        if keyword and keyword.isascii() and keyword.casefold() not in {"steam", "demo", "review", "trailer"}
    )
    return {
        "game_name": profile.basic_info.get("游戏名", "") if profile.basic_info.get("游戏名") != PLACEHOLDER else "",
        "steam_url": profile.basic_info.get("Steam 链接", "") if profile.basic_info.get("Steam 链接") != PLACEHOLDER else "",
        "short_description": str(info.get("short_description", "") or profile.core_gameplay_judgment),
        "tags": "" if tags == PLACEHOLDER else tags,
        "core_keywords": ", ".join(profile.search_keywords),
        "theme_keywords": "" if tags == PLACEHOLDER else tags,
        "english_keywords": english_keywords,
        "reference_games": "",
        "developer": "" if profile.basic_info.get("开发商") == PLACEHOLDER else profile.basic_info.get("开发商", ""),
        "publisher": "" if profile.basic_info.get("发行商") == PLACEHOLDER else profile.basic_info.get("发行商", ""),
    }


def send_profile_to_candidate_finder(profile: ProjectProfile) -> None:
    """Pre-fill the competitor candidate finder inputs without creating fake competitors."""
    game_name = profile.basic_info.get("游戏名", "")
    appid = profile.basic_info.get("AppID", "")
    tags = profile.basic_info.get("类型/标签", "")
    st.session_state["competition_target_game_name"] = "" if game_name == PLACEHOLDER else game_name
    st.session_state["competition_target_appid"] = "" if appid == PLACEHOLDER else appid
    st.session_state["candidate_primary_tags"] = "" if tags == PLACEHOLDER else tags
    st.session_state["candidate_gameplay_keywords"] = profile.core_gameplay_judgment
    st.session_state["candidate_english_keywords"] = ", ".join(
        keyword for keyword in profile.search_keywords if keyword and keyword.isascii()
    )
    st.success("已发送到竞品候选发现器，可切换到“竞品与候选”Tab 继续生成候选搜索链接。")


def combine_next_action(action: str, note: str) -> str:
    """合并下一步动作选项和补充说明。"""
    clean_note = str(note).strip()
    if clean_note:
        return f"{action}：{clean_note}"
    return action


def render_quick_record_page() -> None:
    """渲染 30 秒快速记录表单。"""
    st.subheader("快速记录")
    st.caption("只填当前能确认的信息即可保存，未填写字段会保留为空。")

    with st.form("quick_record_form"):
        col1, col2 = st.columns(2)
        with col1:
            game_name = st.text_input("游戏名", key="quick_game_name")
            steam_url = st.text_input("Steam 链接", key="quick_steam_url")
            appid = st.text_input("Steam AppID", key="quick_appid")
            developer = st.text_input("开发商", key="quick_developer")
            publisher = st.text_input("发行商", key="quick_publisher")
            release_status = st.selectbox(
                "发售状态",
                ["未填写", "未发售", "抢先体验", "已发售", "即将推出"],
                key="quick_release_status",
            )
        with col2:
            has_demo = st.selectbox("是否有 Demo", ["未确认", "是", "否"], key="quick_has_demo")
            has_simplified_chinese = st.selectbox(
                "是否支持简体中文",
                ["未确认", "是", "否"],
                key="quick_has_simplified_chinese",
            )
            genre_tags = st.text_area("类型/标签", height=80, key="quick_genre_tags")
            core_loop = st.text_area(
                "核心玩法一句话",
                height=80,
                key="quick_core_loop",
                help="一句话说明玩家反复做什么",
            )
            first_impression = st.text_area(
                "第一印象",
                height=90,
                key="quick_first_impression",
                help="商店页和视频给你的第一判断",
            )

        action_col, note_col = st.columns([1, 2])
        with action_col:
            next_action_choice = st.selectbox(
                "下一步动作",
                ["未决定", "先试玩 Demo", "先查竞品", "联系开发者", "暂缓观察", "暂不跟进"],
                key="quick_next_action_choice",
                help="试玩 / 联系 / 暂缓 / 放弃 / 等版本",
            )
        with note_col:
            next_action_note = st.text_input("下一步动作补充说明", key="quick_next_action_note")

        with st.expander("展开填写更多信息", expanded=False):
            china_publishing_opportunity = st.text_area(
                "中国区发行机会",
                height=100,
                key="quick_china_publishing_opportunity",
            )
            risks = st.text_area("主要风险", height=100, key="quick_risks")

        col_save, col_report = st.columns([1, 1])
        with col_save:
            save_only = st.form_submit_button("保存快速记录")
        with col_report:
            save_and_report = st.form_submit_button("保存并生成报告")

    if save_only or save_and_report:
        project = build_project_from_form(
            {
                "game_name": game_name,
                "steam_url": steam_url,
                "appid": appid,
                "developer": developer,
                "publisher": publisher,
                "release_status": release_status,
                "has_demo": has_demo,
                "has_simplified_chinese": has_simplified_chinese,
                "genre_tags": genre_tags,
                "core_loop": core_loop,
                "first_impression": first_impression,
                "china_publishing_opportunity": china_publishing_opportunity,
                "risks": risks,
                "next_action": combine_next_action(next_action_choice, next_action_note),
            }
        )

        saved_csv_path = save_project_to_csv(project, CSV_PATH)
        st.success(f"已保存快速记录：{saved_csv_path}")
        st.info("后续可在 Demo 试玩、竞品与候选页继续补充。")

        if save_and_report:
            render_report_result(project)


def render_demo_review_page() -> None:
    """渲染默认折叠的 Demo 深度评估表单。"""
    st.subheader("Demo 试玩")
    project_options = get_saved_project_options()
    if not project_options:
        st.info("暂无已保存项目。请先在快速记录页保存一个项目。")
        return

    selected_label = st.selectbox(
        "选择要补充 Demo 试玩的项目",
        ["请选择项目后填写 Demo 试玩记录"] + [option["label"] for option in project_options],
        key="demo_project_selector",
    )
    if selected_label == "请选择项目后填写 Demo 试玩记录":
        st.info("请选择项目后填写 Demo 试玩记录。")
        return
    selected_project = next(option for option in project_options if option["label"] == selected_label)
    project_row = load_project_row(selected_project["record_id"])
    if project_row is None:
        st.warning("未找到该项目记录，请刷新后重试。")
        return

    st.markdown("### 当前项目基础摘要")
    summary_cols = st.columns(4)
    summary_cols[0].metric("游戏名", str(project_row.get("game_name", "") or PLACEHOLDER))
    summary_cols[1].metric("AppID", str(project_row.get("appid", "") or PLACEHOLDER))
    summary_cols[2].metric("开发商", str(project_row.get("developer", "") or PLACEHOLDER))
    summary_cols[3].metric("发售状态", str(project_row.get("release_status", "") or PLACEHOLDER))

    with st.form("demo_review_form"):
        with st.expander("基础试玩信息", expanded=True):
            demo_played = st.selectbox(
                "是否已试玩 Demo",
                ["未试玩", "已试玩", "无 Demo"],
                index=["未试玩", "已试玩", "无 Demo"].index(project_row.get("demo_played", "未试玩"))
                if project_row.get("demo_played", "未试玩") in ["未试玩", "已试玩", "无 Demo"]
                else 0,
                key="demo_played",
            )
            playtime_minutes = st.number_input(
                "试玩时长分钟",
                min_value=0,
                step=5,
                value=int(project_row.get("playtime_minutes", "0") or 0),
                key="playtime_minutes",
            )
            demo_conclusion = st.text_area(
                "Demo 试玩结论",
                value=str(project_row.get("demo_conclusion", "")),
                height=100,
                key="demo_conclusion",
                help="试玩后是否值得继续跟进",
            )

        with st.expander("分钟段体验", expanded=False):
            first_5min_experience = st.text_area(
                "0-5分钟体验",
                value=str(project_row.get("first_5min_experience", "")),
                height=90,
                key="first_5min_experience",
            )
            first_15min_experience = st.text_area(
                "5-15分钟体验",
                value=str(project_row.get("first_15min_experience", "")),
                height=90,
                key="first_15min_experience",
            )
            first_30min_experience = st.text_area(
                "15-30分钟体验",
                value=str(project_row.get("first_30min_experience", "")),
                height=90,
                key="first_30min_experience",
            )

        with st.expander("问题记录", expanded=False):
            tutorial_issue = st.text_area(
                "新手引导问题",
                value=str(project_row.get("tutorial_issue", "")),
                height=90,
                key="tutorial_issue",
            )
            control_issue = st.text_area(
                "操作/手感问题",
                value=str(project_row.get("control_issue", "")),
                height=90,
                key="control_issue",
            )
            combat_or_system_issue = st.text_area(
                "战斗/系统/经营问题",
                value=str(project_row.get("combat_or_system_issue", "")),
                height=90,
                key="combat_or_system_issue",
            )
            localization_issue = st.text_area(
                "本地化问题",
                value=str(project_row.get("localization_issue", "")),
                height=90,
                key="localization_issue",
            )
            performance_issue = st.text_area(
                "性能/稳定性问题",
                value=str(project_row.get("performance_issue", "")),
                height=90,
                key="performance_issue",
            )

        with st.expander("项目判断", expanded=True):
            core_loop_clarity = st.selectbox(
                "核心循环是否清晰",
                ["未判断", "清晰", "部分清晰", "不清晰"],
                index=["未判断", "清晰", "部分清晰", "不清晰"].index(
                    project_row.get("core_loop_clarity", "未判断")
                )
                if project_row.get("core_loop_clarity", "未判断") in ["未判断", "清晰", "部分清晰", "不清晰"]
                else 0,
                key="core_loop_clarity",
            )
            content_depth = st.text_area(
                "内容深度判断",
                value=str(project_row.get("content_depth", "")),
                height=90,
                key="content_depth",
            )
            video_hook = st.selectbox(
                "视频传播点",
                ["未判断", "有", "一般", "没有"],
                index=["未判断", "有", "一般", "没有"].index(project_row.get("video_hook", "未判断"))
                if project_row.get("video_hook", "未判断") in ["未判断", "有", "一般", "没有"]
                else 0,
                key="video_hook",
            )
            china_player_reaction = st.text_area(
                "中国玩家可能反馈",
                value=str(project_row.get("china_player_reaction", "")),
                height=90,
                key="china_player_reaction",
            )

        col_save, col_report = st.columns([1, 1])
        with col_save:
            save_demo = st.form_submit_button("保存 Demo 试玩记录")
        with col_report:
            save_demo_and_report = st.form_submit_button("保存并生成报告")

    if save_demo or save_demo_and_report:
        updates = {
            "demo_played": demo_played,
            "playtime_minutes": playtime_minutes,
            "demo_conclusion": demo_conclusion,
            "first_5min_experience": first_5min_experience,
            "first_15min_experience": first_15min_experience,
            "first_30min_experience": first_30min_experience,
            "tutorial_issue": tutorial_issue,
            "control_issue": control_issue,
            "combat_or_system_issue": combat_or_system_issue,
            "localization_issue": localization_issue,
            "performance_issue": performance_issue,
            "core_loop_clarity": core_loop_clarity,
            "content_depth": content_depth,
            "video_hook": video_hook,
            "china_player_reaction": china_player_reaction,
        }
        update_project_fields(CSV_PATH, selected_project["record_id"], updates)
        st.success("Demo 试玩记录已保存。")

        if save_demo_and_report:
            refreshed_row = load_project_row(selected_project["record_id"])
            render_report_result(project_from_row(refreshed_row))


def render_candidate_finder(target_game_name: str, target_appid: str) -> None:
    """渲染竞品候选发现器。"""
    with st.expander("竞品候选发现器", expanded=False):
        st.caption("这里只生成搜索链接和候选池，不会自动确认竞品。")

        search_col1, search_col2 = st.columns(2)
        with search_col1:
            primary_tags = st.text_input("核心标签，可用逗号、顿号、空格或换行分隔", key="candidate_primary_tags")
            gameplay_keywords = st.text_input("玩法关键词，可用逗号、顿号、空格或换行分隔", key="candidate_gameplay_keywords")
            english_keywords = st.text_input("英文搜索关键词，可选", key="candidate_english_keywords")
        with search_col2:
            reference_games = st.text_area("用户已知参考游戏，可选", height=110, key="candidate_reference_games")

        search_links = generate_steam_search_links(
            target_game_name,
            primary_tags,
            gameplay_keywords,
            reference_games,
            english_keywords,
        )
        if search_links:
            st.markdown("**Steam 搜索链接**")
            for link in search_links:
                st.markdown(f"- {link['source_type']}：[{link['term']}]({link['url']})")

    with st.expander("手动添加候选", expanded=False):
        with st.form("candidate_form"):
            cand_col1, cand_col2 = st.columns(2)
            with cand_col1:
                candidate_name = st.text_input("候选游戏名")
                candidate_steam_url = st.text_input("候选 Steam 链接")
                candidate_appid = st.text_input("候选 AppID")
                source_type = st.selectbox("来源类型", ["标签搜索", "关键词搜索", "用户手动添加"])
            with cand_col2:
                match_reason = st.text_area(
                    "为什么可能是竞品",
                    height=100,
                    help="这个竞品为什么对目标项目有参考价值",
                )
                notes = st.text_area("备注", height=100)
            save_candidate = st.form_submit_button("保存候选")

    if save_candidate:
        if not target_game_name.strip() and not target_appid.strip():
            st.error("请填写候选目标游戏名或目标 AppID。")
        elif not candidate_name.strip():
            st.error("请至少填写候选游戏名。")
        else:
            candidate = build_candidate_from_form(
                {
                    "target_game_name": target_game_name,
                    "target_appid": target_appid,
                    "candidate_name": candidate_name,
                    "candidate_steam_url": candidate_steam_url,
                    "candidate_appid": candidate_appid,
                    "source_type": source_type,
                    "match_reason": match_reason,
                    "user_decision": "待确认",
                    "notes": notes,
                }
            )
            candidate_csv_path = save_candidate_to_csv(candidate, CANDIDATE_CSV_PATH)
            st.success(f"候选记录已保存：{candidate_csv_path}")

    render_candidate_pool(target_appid, target_game_name)


def render_candidate_pool(target_appid: str, target_game_name: str) -> None:
    """折叠展示当前项目候选池。"""
    all_candidates = filter_candidates(load_candidates(CANDIDATE_CSV_PATH), "", target_game_name, "全部")
    with st.expander(f"竞品候选池（共 {len(all_candidates)} 条）", expanded=False):
        target_filter = st.text_input("按目标游戏筛选候选", value=target_game_name)
        decision_filter = st.selectbox("候选状态筛选", ["待确认", "采纳", "排除", "全部"])
        show_full_candidates = st.checkbox("显示完整候选字段", value=False)
        filtered_candidates = filter_candidates(
            load_candidates(CANDIDATE_CSV_PATH),
            "",
            target_filter,
            decision_filter,
        )
        display_data = get_candidate_display_data(
            CANDIDATE_CSV_PATH,
            "",
            target_filter,
            decision_filter,
            show_full=show_full_candidates,
        )
        if display_data.empty:
            st.info("暂无候选记录")
        else:
            st.dataframe(display_data, use_container_width=True)
            render_candidate_actions(filtered_candidates)


def render_candidate_actions(filtered_candidates) -> None:
    """渲染候选采纳和排除操作。"""
    candidate_options = build_candidate_options(filtered_candidates)
    if not candidate_options:
        return

    selected_candidate_label = st.selectbox(
        "选择候选进行处理",
        [option["label"] for option in candidate_options],
        key="candidate_action_selector",
    )
    selected_candidate = next(option for option in candidate_options if option["label"] == selected_candidate_label)
    candidate_row = selected_candidate["row"]
    row_index = int(selected_candidate["row_index"])

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("采纳为正式竞品"):
            competitor = CompetitorRecord(
                target_appid=str(candidate_row.get("target_appid", "")),
                target_game_name=str(candidate_row.get("target_game_name", "")),
                competitor_name=str(candidate_row.get("candidate_name", "")),
                competitor_steam_url=str(candidate_row.get("candidate_steam_url", "")),
                competitor_appid=str(candidate_row.get("candidate_appid", "")),
                comparison_notes=str(candidate_row.get("match_reason", "")),
            )
            save_competitor_to_csv(competitor, COMPETITOR_CSV_PATH)
            update_candidate_decision(CANDIDATE_CSV_PATH, row_index, "采纳")
            st.success("候选已采纳为正式竞品。")
    with action_col2:
        if st.button("标记为排除"):
            update_candidate_decision(CANDIDATE_CSV_PATH, row_index, "排除")
            st.success("候选已标记为排除。")


def render_competitor_section(target_game_name: str, target_appid: str) -> None:
    """渲染竞品录入表单和当前项目竞品记录。"""
    with st.expander("正式竞品录入", expanded=False):
        with st.form("competitor_form"):
            st.caption("竞品信息仅支持手动录入，不自动查竞品。")

            target_col1, target_col2 = st.columns(2)
            with target_col1:
                form_target_game_name = st.text_input("目标游戏名", value=target_game_name)
            with target_col2:
                form_target_appid = st.text_input("目标游戏 AppID", value=target_appid)

            col1, col2 = st.columns(2)
            with col1:
                competitor_name = st.text_input("竞品游戏名")
                competitor_steam_url = st.text_input("竞品 Steam 链接")
                competitor_appid = st.text_input("竞品 AppID")
                competitor_developer = st.text_input("竞品开发商")
                competitor_publisher = st.text_input("竞品发行商")
                competitor_release_status = st.selectbox(
                    "竞品发售状态",
                    ["未填写", "未发售", "抢先体验", "已发售", "即将推出"],
                )
                competitor_price = st.text_input("竞品价格")
                competitor_review_count = st.text_input("竞品评测数")
                competitor_positive_rate = st.text_input("竞品好评率")
            with col2:
                competitor_has_demo = st.selectbox("竞品是否有 Demo", ["未确认", "是", "否"])
                competitor_has_simplified_chinese = st.selectbox("竞品是否支持简体中文", ["未确认", "是", "否"])
                competitor_tags = st.text_area("竞品标签", height=80)
                competitor_core_loop = st.text_area("竞品核心玩法", height=90)
                competitor_selling_points = st.text_area("竞品主要卖点", height=100)
                competitor_weaknesses = st.text_area("竞品主要弱点", height=100)
                comparison_notes = st.text_area(
                    "对目标项目的参考意义",
                    height=100,
                    help="这个竞品为什么对目标项目有参考价值",
                )

            save_competitor = st.form_submit_button("保存竞品记录")

    if save_competitor:
        if not form_target_game_name.strip() and not form_target_appid.strip():
            st.error("请填写目标游戏名或目标游戏 AppID。")
        elif not competitor_name.strip():
            st.error("请至少填写竞品游戏名。")
        else:
            competitor = build_competitor_from_form(
                {
                    "target_appid": form_target_appid,
                    "target_game_name": form_target_game_name,
                    "competitor_name": competitor_name,
                    "competitor_steam_url": competitor_steam_url,
                    "competitor_appid": competitor_appid,
                    "competitor_developer": competitor_developer,
                    "competitor_publisher": competitor_publisher,
                    "competitor_release_status": competitor_release_status,
                    "competitor_price": competitor_price,
                    "competitor_review_count": competitor_review_count,
                    "competitor_positive_rate": competitor_positive_rate,
                    "competitor_has_demo": competitor_has_demo,
                    "competitor_has_simplified_chinese": competitor_has_simplified_chinese,
                    "competitor_tags": competitor_tags,
                    "competitor_core_loop": competitor_core_loop,
                    "competitor_selling_points": competitor_selling_points,
                    "competitor_weaknesses": competitor_weaknesses,
                    "comparison_notes": comparison_notes,
                }
            )
            competitor_csv_path = save_competitor_to_csv(competitor, COMPETITOR_CSV_PATH)
            st.success(f"竞品记录已保存：{competitor_csv_path}")

    st.subheader("当前项目竞品记录")
    show_full_competitors = st.checkbox("显示完整竞品字段", value=False)
    display_data = get_competitor_display_data(
        COMPETITOR_CSV_PATH,
        target_appid,
        target_game_name,
        show_full=show_full_competitors,
    )
    if display_data.empty:
        st.info("暂无竞品记录")
    else:
        st.dataframe(display_data, use_container_width=True)


WORKFLOW_ACTIVE_STAGES = ["新发现", "待补资料", "待试玩", "待开发商调查", "值得联系"]
WORKFLOW_TABLE_COLUMNS = [
    "game_name",
    "appid",
    "developer",
    "publisher",
    "release_status",
    "has_demo",
    "supports_schinese",
    "stage",
    "priority",
    "auto_suggestion",
    "next_action",
    "updated_at",
]

WORKFLOW_TABLE_LABELS = [
    "游戏名",
    "AppID",
    "开发商",
    "发行商",
    "发售状态",
    "Demo",
    "简中",
    "当前阶段",
    "优先级",
    "自动建议",
    "下一步动作",
    "更新时间",
]


def render_daily_workflow_page() -> None:
    st.subheader("今日工作流")
    st.caption("用于每天快速处理候选项目：补资料、看画像、改状态、导出日报。")
    ensure_candidate_pool_csv_exists(CANDIDATE_POOL_CSV_PATH)
    pool = apply_auto_suggestions(load_candidate_pool(CANDIDATE_POOL_CSV_PATH))
    render_daily_workflow_overview(pool)
    render_daily_workflow_candidate_queue(pool)
    render_daily_workflow_current_project(pool)
    render_daily_workflow_outputs()


def render_daily_workflow_overview(pool: pd.DataFrame) -> None:
    st.markdown("### 今日概览")
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    stage = pool["stage"].astype(str) if "stage" in pool.columns else pd.Series([], dtype=str)
    priority = pool["priority"].astype(str) if "priority" in pool.columns else pd.Series([], dtype=str)
    created_at = pool["created_at"].astype(str) if "created_at" in pool.columns else pd.Series([], dtype=str)
    cols = st.columns(7)
    cols[0].metric("今日新增候选", int(created_at.str.startswith(today_prefix).sum()) if not pool.empty else 0)
    cols[1].metric("待处理", int(stage.isin(WORKFLOW_ACTIVE_STAGES).sum()) if not pool.empty else 0)
    cols[2].metric("待补资料", int(stage.eq("待补资料").sum()) if not pool.empty else 0)
    cols[3].metric("待试玩", int(stage.eq("待试玩").sum()) if not pool.empty else 0)
    cols[4].metric("值得联系", int(stage.eq("值得联系").sum()) if not pool.empty else 0)
    cols[5].metric("高优先级", int(priority.eq("高").sum()) if not pool.empty else 0)
    cols[6].metric("已放弃 / 暂缓", int(stage.isin(["放弃", "暂缓"]).sum()) if not pool.empty else 0)


def render_daily_workflow_candidate_queue(pool: pd.DataFrame) -> None:
    st.markdown("### 待处理候选")
    if pool.empty:
        st.info("候选池暂无记录。")
        return
    filters = st.columns([2, 1, 1])
    keyword = filters[0].text_input("搜索", key="workflow_keyword_filter", placeholder="游戏名 / AppID / 开发商 / 发行商")
    stage_filter = filters[1].selectbox("stage", ["全部"] + WORKFLOW_ACTIVE_STAGES, key="workflow_stage_filter")
    priority_filter = filters[2].selectbox("priority", ["全部"] + PRIORITY_OPTIONS, key="workflow_priority_filter")

    today_only = bool(st.session_state.get("workflow_today_new_only", False))
    if today_only:
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        filtered = pool.loc[pool["created_at"].astype(str).str.startswith(today_prefix)].copy()
        notice_cols = st.columns([3, 1])
        notice_cols[0].info("当前显示：今日新增候选。")
        if notice_cols[1].button("清除今日新增筛选", key="workflow_clear_today_filter", use_container_width=True):
            st.session_state["workflow_today_new_only"] = False
            st.rerun()
    else:
        filtered = pool.loc[pool["stage"].astype(str).isin(WORKFLOW_ACTIVE_STAGES)].copy()
    if stage_filter != "全部":
        filtered = filtered.loc[filtered["stage"].astype(str).eq(stage_filter)]
    if priority_filter != "全部":
        filtered = filtered.loc[filtered["priority"].astype(str).eq(priority_filter)]
    query = str(keyword or "").strip()
    if query:
        haystack = (
            filtered["game_name"].astype(str)
            + " "
            + filtered["appid"].astype(str)
            + " "
            + filtered["developer"].astype(str)
            + " "
            + filtered["publisher"].astype(str)
        )
        filtered = filtered.loc[haystack.str.contains(query, case=False, na=False)]

    st.dataframe(
        daily_workflow_display_data(filtered),
        use_container_width=True,
        hide_index=True,
    )
    if filtered.empty:
        st.info("暂无符合条件的待处理候选。")
        return

    with st.expander("候选操作", expanded=True):
        options = candidate_pool_options(filtered)
        labels = [option["label"] for option in options]
        selected_label = st.selectbox("选择候选", labels, key="workflow_candidate_select")
        selected = next(option for option in options if option["label"] == selected_label)
        render_daily_workflow_candidate_actions(selected["row"].to_dict(), selected["candidate_id"])


def render_daily_workflow_candidate_actions(row: dict, candidate_id: str) -> None:
    appid = str(row.get("appid", "") or "").strip()
    steam_url = str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    steamdb_url = str(row.get("steamdb_url", "") or "").strip() or steamdb_app_url_from_appid(appid)
    cols = st.columns(5)
    if cols[0].button("设为当前处理项目", key=f"workflow_set_current_{candidate_id}", use_container_width=True):
        st.session_state["workflow_current_candidate_id"] = candidate_id
        st.success("已设为当前处理项目。")
    if cols[1].button("发送到查查", key=f"workflow_send_lookup_{candidate_id}", use_container_width=True):
        set_lookup_prefill_from_candidate(row, source="今日工作流")
        st.success("已发送到查查，请打开首页 / 今日看板。")
    if cols[2].button("发送到项目画像", key=f"workflow_send_profile_{candidate_id}", use_container_width=True):
        set_profile_prefill_from_mapping(row, source_context="今日工作流")
        st.session_state["pending_home_target"] = "profile"
        st.session_state["active_page"] = "一键项目画像"
        st.success("已发送到项目画像，请打开对应 Tab。")
    with cols[3]:
        if steam_url:
            st.link_button("打开 Steam", steam_url, use_container_width=True)
    with cols[4]:
        if steamdb_url:
            st.link_button("打开 SteamDB", steamdb_url, use_container_width=True)


def daily_workflow_display_data(data: pd.DataFrame) -> pd.DataFrame:
    display = candidate_pool_display_data(data, show_full=False)
    columns = [column for column in WORKFLOW_TABLE_LABELS if column in display.columns]
    return display.loc[:, columns]


def render_daily_workflow_current_project(pool: pd.DataFrame) -> None:
    st.markdown("### 当前处理项目")
    candidate_id = str(st.session_state.get("workflow_current_candidate_id", "") or "").strip()
    if not candidate_id or pool.empty:
        st.info("请从上方候选列表选择一个项目开始处理。")
        return
    matches = pool.loc[pool["candidate_id"].astype(str).str.strip().eq(candidate_id)]
    if matches.empty:
        st.warning("当前处理项目不在候选池中，请重新选择。")
        return
    row = matches.iloc[0].to_dict()
    appid = str(row.get("appid", "") or "").strip()
    steam_url = str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    summary_rows = [
        {"字段": "游戏名", "内容": row.get("game_name") or (f"AppID {appid}" if appid else "资料不足")},
        {"字段": "AppID", "内容": appid or "资料不足"},
        {"字段": "Steam 链接", "内容": steam_url or "资料不足"},
        {"字段": "开发商", "内容": row.get("developer") or "资料不足"},
        {"字段": "发行商", "内容": row.get("publisher") or "资料不足"},
        {"字段": "当前阶段", "内容": row.get("stage") or "新发现"},
        {"字段": "优先级", "内容": row.get("priority") or "未定"},
        {"字段": "下一步动作", "内容": row.get("next_action") or "补项目画像"},
        {"字段": "备注", "内容": row.get("owner_note") or "未填写"},
    ]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    render_daily_workflow_current_actions(row, candidate_id)
    render_daily_workflow_current_form(row, candidate_id)


def render_daily_workflow_current_actions(row: dict, candidate_id: str) -> None:
    cols = st.columns(7)
    if cols[0].button("补全基础信息", key=f"workflow_current_enrich_{candidate_id}", use_container_width=True):
        stats = run_candidate_pool_bulk_enrich(pd.DataFrame([row]))
        if stats["success"]:
            st.success("基础信息已补全。")
        else:
            st.info("获取失败，可稍后重试。")
    if cols[1].button("发送到项目画像", key=f"workflow_current_profile_{candidate_id}", use_container_width=True):
        set_profile_prefill_from_mapping(row, source_context="今日工作流")
        st.session_state["pending_home_target"] = "profile"
        st.session_state["active_page"] = "一键项目画像"
        st.success("已发送到项目画像，请打开对应 Tab。")
    quick_updates = [
        ("标记为待试玩", {"stage": "待试玩", "next_action": "试玩 Demo"}),
        ("标记为待开发商调查", {"stage": "待开发商调查", "next_action": "调查开发商 / 发行关系"}),
        ("标记为值得联系", {"stage": "值得联系", "priority": "高", "next_action": "联系开发商 / 发行方"}),
        ("标记为暂缓", {"stage": "暂缓", "priority": "低", "next_action": "暂缓观察"}),
        ("标记为放弃", {"stage": "放弃", "priority": "低", "next_action": "放弃"}),
    ]
    for col, (label, updates) in zip(cols[2:], quick_updates):
        if col.button(label, key=f"workflow_current_{label}_{candidate_id}", use_container_width=True):
            update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates=updates)
            st.success(f"已{label.replace('标记为', '标记为')}。")


def render_daily_workflow_current_form(row: dict, candidate_id: str) -> None:
    with st.form(f"workflow_current_form_{candidate_id}"):
        cols = st.columns([1, 1, 2])
        current_stage = row.get("stage") if row.get("stage") in STAGE_OPTIONS else "新发现"
        current_priority = row.get("priority") if row.get("priority") in PRIORITY_OPTIONS else "未定"
        stage = cols[0].selectbox("stage", STAGE_OPTIONS, index=STAGE_OPTIONS.index(current_stage))
        priority = cols[1].selectbox("priority", PRIORITY_OPTIONS, index=PRIORITY_OPTIONS.index(current_priority))
        next_action = cols[2].text_input("next_action", value=str(row.get("next_action", "") or ""))
        note_cols = st.columns(2)
        owner_note = note_cols[0].text_area("owner_note", value=str(row.get("owner_note", "") or ""), height=90)
        reject_reason = note_cols[1].text_area("reject_reason", value=str(row.get("reject_reason", "") or ""), height=90)
        submitted = st.form_submit_button("保存当前处理项目更新", use_container_width=True)
    if submitted:
        update_candidate_pool_fields(
            CANDIDATE_POOL_CSV_PATH,
            candidate_id=candidate_id,
            updates={
                "stage": stage,
                "priority": priority,
                "next_action": next_action,
                "owner_note": owner_note,
                "reject_reason": reject_reason,
            },
        )
        st.success("当前处理项目已更新。")


def render_daily_workflow_outputs() -> None:
    st.markdown("### 今日输出")
    cols = st.columns(3)
    if cols[0].button("导出今日候选日报", key="workflow_export_daily_report", use_container_width=True):
        export_path = export_daily_candidate_report(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel", MARKET_DATA_CSV_PATH)
        st.success(f"今日候选日报已导出：{export_path}")
    if cols[1].button("导出候选池 Excel", key="workflow_export_candidate_pool", use_container_width=True):
        export_path = export_candidate_pool_to_excel(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel")
        st.success(f"候选池 Excel 已导出：{export_path}")
    if cols[2].button("打开 reports/excel 目录", key="workflow_show_reports_dir", use_container_width=True):
        st.info(f"目录路径：{BASE_DIR / 'reports' / 'excel'}")
    filter_cols = st.columns(3)
    if filter_cols[0].button("查看今日新增", key="workflow_view_today_new", use_container_width=True):
        st.session_state["workflow_today_new_only"] = True
        st.session_state["workflow_stage_filter"] = "全部"
        st.rerun()
    if filter_cols[1].button("查看值得联系", key="workflow_view_contact", use_container_width=True):
        st.session_state["workflow_today_new_only"] = False
        st.session_state["workflow_stage_filter"] = "值得联系"
        st.rerun()
    if filter_cols[2].button("查看待试玩", key="workflow_view_demo", use_container_width=True):
        st.session_state["workflow_today_new_only"] = False
        st.session_state["workflow_stage_filter"] = "待试玩"
        st.rerun()


def set_lookup_prefill_from_candidate(row: dict, source: str = "") -> None:
    appid = str(row.get("appid", "") or "").strip()
    steam_url = str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    st.session_state["pending_lookup_prefill"] = {
        "lookup_input": steam_url or appid or str(row.get("game_name", "") or ""),
        "source": source,
        "candidate_id": row.get("candidate_id", ""),
    }
    st.session_state["pending_home_target"] = "home"
    st.session_state["active_page"] = "首页 / 今日看板"


def render_competitor_candidate_page() -> None:
    """渲染竞品与候选页。"""
    st.subheader("竞品与候选")
    render_project_candidate_pool_section()

    project_options = get_project_options()
    selected_label = st.selectbox(
        "选择目标项目",
        [option["label"] for option in project_options],
        key="competition_target_selector",
    )
    selected_project = next(option for option in project_options if option["label"] == selected_label)

    if not selected_project.get("record_id"):
        st.info("请选择项目或从项目画像发送到竞品候选发现器。")
        with st.expander("手动输入目标项目", expanded=False):
            manual_col1, manual_col2 = st.columns(2)
            with manual_col1:
                target_game_name = st.text_input("目标游戏名", key="competition_target_game_name")
            with manual_col2:
                target_appid = st.text_input("目标 AppID", key="competition_target_appid")
        if not str(target_game_name or target_appid).strip():
            return
    else:
        st.markdown("### 当前项目摘要")
        summary_cols = st.columns(3)
        summary_cols[0].metric("游戏名", selected_project.get("game_name", "") or PLACEHOLDER)
        summary_cols[1].metric("AppID", selected_project.get("appid", "") or PLACEHOLDER)
        summary_cols[2].metric(
            "已有竞品记录",
            len(
                filter_competitors(
                    load_competitors(COMPETITOR_CSV_PATH),
                    selected_project.get("appid", ""),
                    selected_project.get("game_name", ""),
                )
            ),
        )
        with st.expander("竞品候选发现器高级字段", expanded=False):
            manual_col1, manual_col2 = st.columns(2)
            with manual_col1:
                target_game_name = st.text_input(
                    "目标游戏名",
                    value=selected_project["game_name"],
                    key="competition_target_game_name",
                )
            with manual_col2:
                target_appid = st.text_input(
                    "目标 AppID",
                    value=selected_project["appid"],
                    key="competition_target_appid",
                )

    st.caption("竞品候选发现器只生成搜索线索和候选池记录，正式竞品仍需人工确认。")
    render_candidate_finder(target_game_name, target_appid)
    render_competitor_section(target_game_name, target_appid)


def render_project_candidate_pool_section() -> None:
    st.markdown("### 项目候选池")
    ensure_candidate_pool_csv_exists(CANDIDATE_POOL_CSV_PATH)
    pool = load_candidate_pool(CANDIDATE_POOL_CSV_PATH)
    summary = candidate_pool_summary(pool)
    metric_cols = st.columns(5)
    metric_cols[0].metric("待处理", summary["pending"])
    metric_cols[1].metric("高优先级", summary["high_priority"])
    metric_cols[2].metric("待试玩", summary["demo"])
    metric_cols[3].metric("值得联系", summary["contact"])
    metric_cols[4].metric("已放弃", summary["rejected"])
    st.caption("规则建议仅用于辅助初筛，需人工复核；不会自动改变 stage。")

    compact_filters = len(pool) <= 10
    filter_cols = st.columns([2, 1, 1])
    with filter_cols[0]:
        keyword_filter = st.text_input("搜索", key="candidate_pool_keyword_filter", placeholder="游戏名 / AppID / 开发商 / 发行商")
    with filter_cols[1]:
        current_stage = st.session_state.get("candidate_pool_stage_filter", "全部")
        stage_options = ["全部"] + STAGE_OPTIONS
        if current_stage not in stage_options:
            current_stage = "全部"
        stage_filter = st.selectbox(
            "stage",
            stage_options,
            index=stage_options.index(current_stage),
            key="candidate_pool_stage_filter",
        )
    with filter_cols[2]:
        current_priority = st.session_state.get("candidate_pool_priority_filter", "全部")
        priority_options = ["全部"] + PRIORITY_OPTIONS
        if current_priority not in priority_options:
            current_priority = "全部"
        priority_filter = st.selectbox(
            "priority",
            priority_options,
            index=priority_options.index(current_priority),
            key="candidate_pool_priority_filter",
        )

    advanced_expanded = not compact_filters and bool(st.session_state.get("candidate_pool_show_advanced_default", False))
    with st.expander("高级筛选", expanded=advanced_expanded):
        advanced_cols = st.columns(6)
        with advanced_cols[0]:
            demo_filter = st.selectbox("Demo", ["全部", "是", "否", "未确认"], key="candidate_pool_demo_filter")
        with advanced_cols[1]:
            schinese_filter = st.selectbox("简中", ["全部", "是", "否", "未确认"], key="candidate_pool_schinese_filter")
        with advanced_cols[2]:
            archived_filter = st.selectbox("归档", ["未归档", "已归档", "全部"], key="candidate_pool_archived_filter")
        with advanced_cols[3]:
            release_status_filter = st.text_input("发售状态", key="candidate_pool_release_status_filter")
        with advanced_cols[4]:
            company_filter = st.text_input("开发商/发行商", key="candidate_pool_company_filter")
        with advanced_cols[5]:
            min_review_count = st.selectbox("评论数", ["任意", "10+", "50+", "100+", "500+"], key="candidate_pool_min_review_filter")

    filtered = filter_candidate_pool(
        pool,
        stage=stage_filter,
        priority=priority_filter,
        has_demo=demo_filter,
        supports_schinese=schinese_filter,
        archived=archived_filter,
    )
    filtered = apply_candidate_pool_text_filters(
        filtered,
        keyword=keyword_filter,
        release_status=release_status_filter,
        company=company_filter,
        min_review_count=min_review_count,
    )
    render_candidate_pool_bulk_enrich(pool, filtered)

    show_full_candidate_pool = st.checkbox("显示完整字段", value=False, key="candidate_pool_show_full_fields")
    filtered_with_suggestions = apply_auto_suggestions(filtered)
    st.dataframe(
        candidate_pool_display_data(filtered_with_suggestions, show_full=show_full_candidate_pool),
        use_container_width=True,
        hide_index=True,
    )

    st.caption("导出前提醒：PUBG / Apex / Rust / CS2 / 绝区零等参考或测试项目默认不会进入正式候选。")
    if st.button("导出 V0.7.1 正式候选 Excel", key="candidate_pool_export_v070", use_container_width=True):
        try:
            export_result = export_candidate_pool_v070_to_excel(CANDIDATE_POOL_CSV_PATH)
        except Exception as exc:
            st.error(f"导出 V0.7.1 正式候选 Excel 失败：{exc}")
        else:
            st.success("已生成 Excel，可直接下载")
            result_cols = st.columns(5)
            result_cols[0].metric("全部候选", export_result["total_count"])
            result_cols[1].metric("正式候选", export_result["formal_count"])
            result_cols[2].metric("竞品参考", export_result["competitor_count"])
            result_cols[3].metric("资料不足", export_result["insufficient_count"])
            result_cols[4].metric("已放弃/暂缓", export_result["paused_rejected_count"])
            filename = str(export_result.get("filename") or "candidate_pool_v071.xlsx")
            export_bytes = export_result.get("bytes")
            st.caption(f"文件名：{filename}")
            if not export_bytes:
                st.error("本次导出的 Excel 内容为空，无法生成下载按钮。")
            else:
                st.download_button(
                    "下载本次导出的 Excel",
                    data=export_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_candidate_pool_v071_{Path(filename).stem}",
                    use_container_width=True,
                )
                st.caption("下载位置由浏览器控制，如需每次选择保存位置，请在浏览器下载设置中开启“下载前询问保存位置”。")

    action_cols = st.columns([1, 1, 1, 2])
    if action_cols[0].button("导出候选清单", key="candidate_pool_export", use_container_width=True):
        export_path = export_candidate_pool_to_excel(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel")
        st.success(f"候选清单已导出：{export_path}")
    if action_cols[1].button("导出今日候选日报", key="candidate_pool_export_daily_report", use_container_width=True):
        export_path = export_daily_candidate_report(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel", MARKET_DATA_CSV_PATH)
        st.success(f"今日候选日报已导出：{export_path}")
    action_cols[2].caption(f"当前筛选：{len(filtered)} 条")
    action_cols[3].caption(f"数据文件：{CANDIDATE_POOL_CSV_PATH}")

    if filtered.empty:
        st.info("暂无符合筛选条件的候选。")
        return

    with st.expander("处理选中候选", expanded=False):
        options = candidate_pool_options(filtered_with_suggestions)
        selected_label = st.selectbox("选择候选", [option["label"] for option in options], key="candidate_pool_action_select")
        selected = next(option for option in options if option["label"] == selected_label)
        row = selected["row"].to_dict()
        candidate_id = selected["candidate_id"]
        render_project_candidate_pool_actions(row, candidate_id)


def render_project_candidate_pool_actions(row: dict, candidate_id: str) -> None:
    appid = str(row.get("appid", "") or "").strip()
    steam_url = str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    steamdb_url = str(row.get("steamdb_url", "") or "").strip() or steamdb_app_url_from_appid(appid)
    suggestion, reason = build_candidate_pool_auto_suggestion(row)
    st.write(f"自动建议：{suggestion or '未生成'}")
    if reason:
        st.caption(f"建议理由：{reason}")
    action_cols = st.columns(4)
    if action_cols[0].button("发送到查查", key=f"candidate_pool_chacha_{candidate_id}", use_container_width=True):
        set_lookup_prefill_from_candidate(row, source="项目候选池")
        st.success("已发送到首页查查。")
    if action_cols[1].button("发送到项目画像", key=f"candidate_pool_profile_{candidate_id}", use_container_width=True):
        set_profile_prefill_from_mapping(row, source_context="项目候选池")
        st.session_state["pending_home_target"] = "profile"
        st.session_state["active_page"] = "一键项目画像"
        st.success("已发送到项目画像。")
        st.rerun()
    with action_cols[2]:
        if steam_url:
            st.link_button("打开 Steam", steam_url, use_container_width=True)
    with action_cols[3]:
        if steamdb_url:
            st.link_button("打开 SteamDB", steamdb_url, use_container_width=True)

    quick_cols = st.columns(6)
    if quick_cols[0].button("应用自动建议", key=f"candidate_pool_apply_suggestion_{candidate_id}", use_container_width=True):
        updates = apply_suggestion_to_stage(suggestion)
        updates["auto_suggestion"] = suggestion
        updates["auto_reason"] = reason
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates=updates)
        st.success("已应用自动建议，用户备注未改动。")
    if quick_cols[1].button("标记为待试玩", key=f"candidate_pool_quick_demo_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"stage": "待试玩", "priority": "高", "next_action": "试玩 Demo"})
        st.success("已标记为待试玩。")
    if quick_cols[2].button("待开发商调查", key=f"candidate_pool_quick_dev_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"stage": "待开发商调查", "next_action": "调查开发商 / 发行关系"})
        st.success("已标记为待开发商调查。")
    if quick_cols[3].button("值得联系", key=f"candidate_pool_quick_contact_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"stage": "值得联系", "priority": "高", "next_action": "联系开发商 / 发行方"})
        st.success("已标记为值得联系。")
    if quick_cols[4].button("暂缓", key=f"candidate_pool_quick_hold_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"stage": "暂缓", "priority": "低", "next_action": "暂缓观察"})
        st.success("已标记为暂缓。")
    if quick_cols[5].button("放弃", key=f"candidate_pool_quick_reject_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"stage": "放弃", "priority": "低", "next_action": "放弃"})
        st.success("已标记为放弃。")

    edit_cols = st.columns([1, 1, 2, 1])
    stage = edit_cols[0].selectbox(
        "更新 stage",
        STAGE_OPTIONS,
        index=STAGE_OPTIONS.index(row.get("stage")) if row.get("stage") in STAGE_OPTIONS else 0,
        key=f"candidate_pool_stage_edit_{candidate_id}",
    )
    priority = edit_cols[1].selectbox(
        "更新 priority",
        PRIORITY_OPTIONS,
        index=PRIORITY_OPTIONS.index(row.get("priority")) if row.get("priority") in PRIORITY_OPTIONS else 3,
        key=f"candidate_pool_priority_edit_{candidate_id}",
    )
    next_action = edit_cols[2].text_input(
        "更新 next_action",
        value=str(row.get("next_action", "") or ""),
        key=f"candidate_pool_next_action_edit_{candidate_id}",
    )
    archived = edit_cols[3].checkbox(
        "归档",
        value=str(row.get("is_archived", "")).casefold() in {"true", "1", "yes", "y"},
        key=f"candidate_pool_archive_edit_{candidate_id}",
    )
    note_cols = st.columns(2)
    owner_note = note_cols[0].text_area(
        "备注",
        value=str(row.get("owner_note", "") or ""),
        height=80,
        key=f"candidate_pool_owner_note_edit_{candidate_id}",
    )
    reject_reason = note_cols[1].text_area(
        "放弃原因",
        value=str(row.get("reject_reason", "") or ""),
        height=80,
        key=f"candidate_pool_reject_reason_edit_{candidate_id}",
    )
    if st.button("保存候选更新", key=f"candidate_pool_save_edit_{candidate_id}", use_container_width=True):
        update_candidate_pool_fields(
            CANDIDATE_POOL_CSV_PATH,
            candidate_id=candidate_id,
            updates={
                "stage": stage,
                "priority": priority,
                "next_action": next_action,
                "owner_note": owner_note,
                "reject_reason": reject_reason,
                "is_archived": "True" if archived else "False",
            },
        )
        st.success("候选状态已更新。")


def render_candidate_pool_bulk_enrich(pool: pd.DataFrame, filtered: pd.DataFrame) -> None:
    with st.expander("批量补全候选信息", expanded=False):
        st.caption("只补当前筛选结果里的资料不足或 AppID 占位记录；最多 10 条，不抓公告、评论正文、图片或第三方市场数据。")
        candidate_source = candidate_pool_light_enrich_rows(filtered)
        target_count = min(len(candidate_source), 10)
        st.write(f"预计处理数量：{target_count} / 可补全 {len(candidate_source)} 条")
        if st.button("补全当前筛选结果", key="candidate_pool_bulk_enrich_submit", use_container_width=True):
            if target_count <= 0:
                st.info("当前范围没有可补全的候选。")
                return
            stats = run_candidate_pool_bulk_enrich(candidate_source.head(10))
            st.success(
                "批量补全完成："
                f"成功补全 {stats['success']} 条，"
                f"资料不足 {stats['insufficient']} 条，"
                f"请求失败 {stats['failed']} 条，"
                f"重复跳过 {stats['duplicate']} 条。"
            )
            if stats["failures"]:
                st.info("部分项目获取失败，可稍后重试。")


def candidate_pool_light_enrich_rows(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return filtered.copy()
    suggested = apply_auto_suggestions(filtered)
    mask = suggested.apply(lambda row: is_appid_placeholder_record(row.to_dict()) or is_insufficient_candidate(row.to_dict()), axis=1)
    return suggested.loc[mask].copy()


def run_candidate_pool_bulk_enrich(candidates: pd.DataFrame) -> dict:
    stats = {"success": 0, "insufficient": 0, "failed": 0, "duplicate": 0, "failures": []}
    seen_appids: set[str] = set()
    progress = st.progress(0)
    total = len(candidates)
    for processed, (_, row) in enumerate(candidates.iterrows(), start=1):
        row_dict = row.to_dict()
        candidate_id = str(row_dict.get("candidate_id", "") or "").strip()
        appid = str(row_dict.get("appid", "") or "").strip()
        label = str(row_dict.get("game_name", "") or appid or candidate_id)
        if not appid:
            stats["failed"] += 1
            stats["failures"].append({"项目": label, "原因": "缺少 AppID"})
            if candidate_id:
                update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, updates={"next_action": "补项目画像"})
            progress.progress(processed / total)
            continue
        if appid in seen_appids:
            stats["duplicate"] += 1
            progress.progress(processed / total)
            continue
        seen_appids.add(appid)
        try:
            record, enriched = build_candidate_pool_record_from_appid(appid, source_url=str(row_dict.get("source_url", "") or ""), source="候选池批量补全")
            updates = {
                key: value
                for key, value in candidate_pool_record_to_dict(record).items()
                if key
                in {
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
                    "next_action",
                }
                and str(value or "").strip()
            }
            if str(row_dict.get("next_action", "") or "").strip():
                updates.pop("next_action", None)
            suggested_row = {**row_dict, **updates}
            suggestion, reason = build_candidate_pool_auto_suggestion(suggested_row)
            updates["auto_suggestion"] = suggestion
            updates["auto_reason"] = reason
            if not enriched and not str(row_dict.get("next_action", "") or "").strip():
                updates["next_action"] = "补项目画像"
            update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, appid=appid, updates=updates)
            if enriched:
                stats["success"] += 1
            else:
                stats["insufficient"] += 1
        except Exception as exc:
            stats["failed"] += 1
            stats["failures"].append({"项目": label, "原因": str(exc)})
            update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, candidate_id=candidate_id, appid=appid, updates={"next_action": "补项目画像"})
        progress.progress(processed / total)
    return stats


def build_candidate_pool_auto_suggestion(row: dict) -> tuple[str, str]:
    suggested = apply_auto_suggestions(pd.DataFrame([row]))
    if suggested.empty:
        return "", ""
    first = suggested.iloc[0]
    return str(first.get("auto_suggestion", "") or ""), str(first.get("auto_reason", "") or "")


def apply_candidate_pool_text_filters(
    data: pd.DataFrame,
    *,
    keyword: str = "",
    release_status: str = "",
    company: str = "",
    min_review_count: str = "任意",
) -> pd.DataFrame:
    filtered = data.copy()
    query = str(keyword or "").strip()
    if query:
        haystack = (
            filtered["game_name"].astype(str)
            + " "
            + filtered["appid"].astype(str)
            + " "
            + filtered["developer"].astype(str)
            + " "
            + filtered["publisher"].astype(str)
        )
        filtered = filtered.loc[haystack.str.contains(query, case=False, na=False)]
    release_query = str(release_status or "").strip()
    if release_query:
        filtered = filtered.loc[
            filtered["release_status"].astype(str).str.contains(release_query, case=False, na=False)
            | filtered["release_date"].astype(str).str.contains(release_query, case=False, na=False)
        ]
    company_query = str(company or "").strip()
    if company_query:
        filtered = filtered.loc[
            filtered["developer"].astype(str).str.contains(company_query, case=False, na=False)
            | filtered["publisher"].astype(str).str.contains(company_query, case=False, na=False)
        ]
    if min_review_count != "任意":
        threshold = int(min_review_count.replace("+", ""))
        counts = filtered["review_count"].astype(str).str.replace(",", "", regex=False)
        filtered = filtered.loc[pd.to_numeric(counts, errors="coerce").fillna(0) >= threshold]
    return filtered


SEARCH_FIELD_KEYS = {
    "game_name": "search_game_name",
    "steam_url": "search_steam_url",
    "short_description": "search_short_description",
    "tags": "search_tags",
    "core_keywords": "search_core_keywords",
    "theme_keywords": "search_theme_keywords",
    "english_keywords": "search_english_keywords",
    "reference_games": "search_reference_games",
    "developer": "search_developer",
    "publisher": "search_publisher",
}


def ensure_search_center_state() -> None:
    """初始化搜索中心输入状态。"""
    for field_name, state_key in SEARCH_FIELD_KEYS.items():
        st.session_state.setdefault(state_key, "")
    st.session_state.setdefault("search_keyword_limit", 20)


def apply_search_center_values(values: dict) -> None:
    """把示例或项目历史数据写入搜索中心输入状态。"""
    for field_name, state_key in SEARCH_FIELD_KEYS.items():
        st.session_state[state_key] = str(values.get(field_name, "") or "")


def build_search_input_from_state() -> SearchCenterInput:
    """从页面状态构造搜索中心输入。"""
    return SearchCenterInput(
        game_name=st.session_state.get("search_game_name", ""),
        steam_url=st.session_state.get("search_steam_url", ""),
        short_description=st.session_state.get("search_short_description", ""),
        tags=st.session_state.get("search_tags", ""),
        core_keywords=st.session_state.get("search_core_keywords", ""),
        theme_keywords=st.session_state.get("search_theme_keywords", ""),
        english_keywords=st.session_state.get("search_english_keywords", ""),
        reference_games=st.session_state.get("search_reference_games", ""),
        developer=st.session_state.get("search_developer", ""),
        publisher=st.session_state.get("search_publisher", ""),
    )


def build_links_v031a(keyword: str) -> dict:
    """生成 V0.31a 搜索链接，使用 %20 URL 编码。"""
    encoded_keyword = quote(keyword, safe="")
    return {
        "Steam 搜索链接": f"https://store.steampowered.com/search/?term={encoded_keyword}",
        "Google 链接": f"https://www.google.com/search?q={encoded_keyword}",
        "百度链接": f"https://www.baidu.com/s?wd={encoded_keyword}",
        "Google Steam 链接": (
            f"https://www.google.com/search?q=site%3Astore.steampowered.com+{encoded_keyword}"
        ),
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


def build_open_link_table(keywords: list[str]) -> pd.DataFrame:
    """为每个关键词和平台生成一行可勾选打开的链接。"""
    rows = []
    for keyword in keywords:
        links = build_links_v031a(keyword)
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


def upgrade_search_tables_v031a(competitor_table, presence_table) -> tuple[pd.DataFrame, pd.DataFrame]:
    """补齐 V0.31a 新链接列，并把链接统一为 %20 编码。"""
    upgraded_competitor = competitor_table.copy()
    upgraded_presence = presence_table.copy()

    for index, row in upgraded_competitor.iterrows():
        links = build_links_v031a(str(row.get("关键词", "")))
        for column in [
            "Steam 搜索链接",
            "Google 链接",
            "百度链接",
            "Google Steam 链接",
            "IGDB 链接",
            "SteamDB 链接",
            "小黑盒站内搜索",
            "游民星空站内搜索",
            "游侠站内搜索",
        ]:
            upgraded_competitor.loc[index, column] = links[column]

    for index, row in upgraded_presence.iterrows():
        links = build_links_v031a(str(row.get("关键词", "")))
        for column in [
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
        ]:
            upgraded_presence.loc[index, column] = links[column]

    return upgraded_competitor, upgraded_presence


def save_search_tables_v031a(
    competitor_table: pd.DataFrame,
    presence_table: pd.DataFrame,
    export_dir: Path,
) -> tuple[Path, Path]:
    """保存 V0.31a 搜索中心 CSV，并兼容旧导出文件缺列。"""
    export_dir.mkdir(parents=True, exist_ok=True)
    competitor_path = export_dir / "competitor_search_links.csv"
    presence_path = export_dir / "platform_presence_search_links.csv"
    append_csv_v031a(competitor_table, competitor_path, COMPETITOR_SEARCH_COLUMNS)
    append_csv_v031a(presence_table, presence_path, PLATFORM_PRESENCE_COLUMNS)
    return competitor_path, presence_path


def append_csv_v031a(data: pd.DataFrame, csv_path: Path, columns: list[str]) -> None:
    """追加 UTF-8-SIG CSV；旧文件缺列时先补齐。"""
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
            existing_data.to_csv(csv_path, columns=columns + extra_columns, index=False, encoding="utf-8-sig")

    output = data.copy()
    for column in columns:
        if column not in output.columns:
            output[column] = ""
    output.loc[:, columns].to_csv(
        csv_path,
        mode="a",
        header=not csv_path.exists(),
        index=False,
        encoding="utf-8-sig",
    )


def render_search_center_page() -> None:
    """渲染半自动搜索中心。"""
    ensure_search_center_state()

    st.subheader("搜索中心 / Search Center")
    st.caption(
        "本模块只生成搜索入口，不自动抓取结果。国内平台默认使用百度站内搜索，"
        "港澳台和海外平台默认使用 Google 或平台原生搜索。备用搜索引擎可手动展开。"
    )
    st.info(
        "原生搜索：直接使用平台自己的搜索链接。站内搜索：通过百度/Google 限定站点搜索，"
        "适用于没有稳定公开搜索页的平台。手动平台：暂不自动生成稳定链接，只给出检查提醒。"
    )

    st.markdown("### 从当前项目生成搜索")
    current_search_input = build_search_input_from_state()
    if current_search_input.game_name.strip():
        preview_cols = st.columns(4)
        preview_cols[0].metric("游戏名", current_search_input.game_name or PLACEHOLDER)
        preview_cols[1].metric("开发商", current_search_input.developer or PLACEHOLDER)
        preview_cols[2].metric("发行商", current_search_input.publisher or PLACEHOLDER)
        preview_cols[3].metric("Steam URL", "已填写" if current_search_input.steam_url else "未填写")
    else:
        st.info("可从项目画像或历史记录发送项目到搜索中心。")

    action_col1, action_col2 = st.columns([1, 2])
    with action_col1:
        if st.button("填入示例：We Need An Army"):
            apply_search_center_values(EXAMPLE_INPUT)
            st.rerun()
    with action_col2:
        project_options = get_saved_project_options()
        if project_options:
            selected_label = st.selectbox(
                "从已保存项目带入",
                [option["label"] for option in project_options],
                key="search_project_selector",
            )
            selected_project = next(option for option in project_options if option["label"] == selected_label)
            if st.button("生成搜索中心链接（带入当前项目）"):
                project_row = load_project_row(selected_project["record_id"])
                if project_row is not None:
                    apply_search_center_values(
                        {
                            "game_name": project_row.get("game_name", ""),
                            "steam_url": project_row.get("steam_url", ""),
                            "short_description": project_row.get("core_loop", ""),
                            "tags": project_row.get("genre_tags", ""),
                            "core_keywords": project_row.get("core_loop", ""),
                            "english_keywords": "",
                            "developer": project_row.get("developer", ""),
                            "publisher": project_row.get("publisher", ""),
                        }
                    )
                    st.rerun()
        else:
            st.info("暂无已保存项目，可先使用独立输入或示例测试。")

    with st.expander("手动填写搜索字段", expanded=False):
        with st.form("search_center_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("游戏名 game_name（必填）", key="search_game_name")
                st.text_input("Steam URL steam_url（可选）", key="search_steam_url")
                st.text_area("英文简介 short_description（可选）", height=90, key="search_short_description")
                st.text_input("Steam 标签 tags（逗号分隔）", key="search_tags")
                st.text_input("核心玩法关键词 core_keywords（逗号分隔）", key="search_core_keywords")
            with col2:
                st.text_input("题材关键词 theme_keywords（逗号分隔）", key="search_theme_keywords")
                st.text_input("英文关键词 english_keywords（逗号分隔）", key="search_english_keywords")
                st.text_input("参考游戏 reference_games（逗号分隔）", key="search_reference_games")
                st.text_input("开发商 developer（可选）", key="search_developer")
                st.text_input("发行商 publisher（可选）", key="search_publisher")
                st.number_input(
                    "keyword_set 最大保留条数",
                    min_value=1,
                    max_value=50,
                    step=1,
                    key="search_keyword_limit",
                )

            generate_tables = st.form_submit_button("生成搜索链接表")

    if generate_tables:
        search_input = build_search_input_from_state()
        if not search_input.game_name.strip():
            st.error("请至少填写游戏名 game_name。")
        else:
            try:
                platforms = load_search_platforms(SEARCH_PLATFORM_CONFIG_PATH)
                navigation_table = build_platform_navigation(
                    search_input,
                    platforms,
                    limit=int(st.session_state.get("search_keyword_limit", 20)),
                )
            except Exception as exc:
                st.error(f"搜索中心生成失败，不影响其他功能：{exc}")
            else:
                st.session_state["search_navigation_table"] = navigation_table
                keyword_count = navigation_table["搜索词"].nunique() if not navigation_table.empty else 0
                row_count = len(navigation_table)
                st.success(f"已生成 {keyword_count} 条 keyword_set，合并为 {row_count} 条平台搜索导航。")

    render_search_center_tables()


def render_search_center_tables() -> None:
    """渲染平台搜索导航。"""
    navigation_table = st.session_state.get("search_navigation_table")
    if navigation_table is None or navigation_table.empty:
        return

    recommended_rows = get_recommended_search_rows(navigation_table)
    render_search_summary(navigation_table, recommended_rows)

    show_fallback_engines = st.checkbox(
        "显示备用搜索引擎",
        value=False,
        key="search_show_fallback_engines",
        help="默认只显示推荐搜索。勾选后显示 Google/百度等备用站内搜索入口。",
    )
    search_display_mode = st.radio(
        "搜索显示模式",
        ["精简模式", "标准模式", "完整模式"],
        horizontal=True,
        key="search_display_mode",
        help="精简模式减少默认展示量；完整模式仍保留全部搜索导航，但按分区折叠。",
    )

    with st.expander(f"推荐优先搜索（{len(recommended_rows)} 条）", expanded=True):
        render_platform_navigation_section(
            recommended_rows,
            "推荐优先搜索",
            show_fallback_engines,
            group_by_platform=False,
        )

    st.divider()

    for section_name in SEARCH_CENTER_SECTION_ORDER:
        section_rows = navigation_table.loc[navigation_table["分区"] == section_name].copy()
        if section_rows.empty:
            continue
        display_rows, current_count = limit_navigation_rows_for_mode(section_rows, search_display_mode)
        with st.expander(f"{section_name}（共 {len(section_rows)} 条，当前显示 {current_count} 条）", expanded=False):
            render_platform_navigation_section(
                display_rows,
                section_name,
                show_fallback_engines,
                group_by_platform=True,
            )
            if current_count < len(section_rows):
                show_all_key = f"search_show_all_{section_name}"
                if st.checkbox("显示该分区全部", key=show_all_key):
                    render_platform_navigation_section(
                        section_rows,
                        f"{section_name} 全部",
                        show_fallback_engines,
                        group_by_platform=True,
                    )

    render_batch_open_links(navigation_table, recommended_rows, show_fallback_engines)

    with st.expander("显示完整链接", expanded=False):
        flat_links = expand_links_for_display(navigation_table, include_fallback=show_fallback_engines)
        st.dataframe(
            flat_links,
            use_container_width=True,
            hide_index=True,
        )

    if st.button("导出搜索导航 CSV"):
        try:
            SEARCH_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            export_path = SEARCH_EXPORT_DIR / "search_navigation_links.csv"
            prepare_navigation_for_csv(navigation_table).to_csv(export_path, index=False, encoding="utf-8-sig")
        except Exception as exc:
            st.error(f"搜索中心导出失败，不影响其他功能：{exc}")
        else:
            st.success(f"搜索导航 CSV 已导出：{export_path}")

    if st.button("导出推荐搜索 CSV"):
        try:
            SEARCH_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            export_path = SEARCH_EXPORT_DIR / "search_navigation_recommended.csv"
            prepare_navigation_for_csv(recommended_rows).to_csv(export_path, index=False, encoding="utf-8-sig")
        except Exception as exc:
            st.error(f"推荐搜索导出失败，不影响其他功能：{exc}")
        else:
            st.success(f"推荐搜索 CSV 已导出：{export_path}")


def render_search_summary(navigation_table: pd.DataFrame, recommended_rows: pd.DataFrame) -> None:
    """Render compact search-center summary metrics before long lists."""
    keyword_count = navigation_table["搜索词"].nunique()
    total_count = len(navigation_table)
    domestic_platform_count = navigation_table.loc[
        navigation_table["区域"].eq("国内"),
        "平台名",
    ].nunique()
    overseas_platform_count = navigation_table.loc[
        navigation_table["区域"].isin(["港澳台", "海外/全球", "日本", "韩国", "其他"]),
        "平台名",
    ].nunique()

    metric_cols = st.columns(5)
    metric_cols[0].metric("keyword_set", keyword_count)
    metric_cols[1].metric("搜索导航", total_count)
    metric_cols[2].metric("推荐入口", len(recommended_rows))
    metric_cols[3].metric("国内平台", domestic_platform_count)
    metric_cols[4].metric("港澳台/海外平台", overseas_platform_count)

    recommended_names = [
        platform for platform in SEARCH_RECOMMENDED_PLATFORMS if platform in set(recommended_rows["平台名"].tolist())
    ]
    st.info(
        f"已生成 {keyword_count} 条 keyword_set，{total_count} 条平台搜索导航。"
        f"推荐先看：{'、'.join(recommended_names)}。"
    )


def get_search_context() -> dict:
    """Read the current search form context used only for display prioritization."""
    game_name = str(st.session_state.get("search_game_name", "")).strip()
    developer = str(st.session_state.get("search_developer", "")).strip()
    core_keywords = [
        term.strip()
        for term in str(st.session_state.get("search_core_keywords", "")).replace("，", ",").split(",")
        if term.strip()
    ]
    english_keywords = [
        term.strip()
        for term in str(st.session_state.get("search_english_keywords", "")).replace("，", ",").split(",")
        if term.strip()
    ]
    return {
        "game_name": game_name,
        "developer": developer,
        "core_keywords": core_keywords,
        "english_keywords": english_keywords,
    }


def build_core_keyword_order() -> list[str]:
    """Build keyword order for display limits without changing generated keywords."""
    context = get_search_context()
    game_name = context["game_name"]
    developer = context["developer"]
    ordered_keywords = []
    for template in SEARCH_CORE_KEYWORDS:
        keyword = template.format(game_name=game_name, developer=developer).strip()
        if keyword and keyword not in ordered_keywords:
            ordered_keywords.append(keyword)
    for keyword in context["core_keywords"] + context["english_keywords"]:
        if keyword not in ordered_keywords:
            ordered_keywords.append(keyword)
    return ordered_keywords


def keyword_display_rank(keyword: str) -> int:
    """Rank core keywords before less important generated keywords."""
    ordered_keywords = build_core_keyword_order()
    normalized = str(keyword).casefold()
    for index, core_keyword in enumerate(ordered_keywords):
        if normalized == core_keyword.casefold():
            return index
    return len(ordered_keywords) + 100


def get_recommended_search_rows(navigation_table: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    """Return the default high-signal search rows."""
    platform_rank = {platform: index for index, platform in enumerate(SEARCH_RECOMMENDED_PLATFORMS)}
    candidates = navigation_table.loc[navigation_table["平台名"].isin(platform_rank)].copy()
    if candidates.empty:
        return candidates
    candidates["_platform_rank"] = candidates["平台名"].map(platform_rank)
    candidates["_keyword_rank"] = candidates["搜索词"].apply(keyword_display_rank)
    candidates = candidates.sort_values(["_platform_rank", "_keyword_rank", "搜索词"])
    candidates = candidates.drop_duplicates("平台名", keep="first").head(limit)
    return candidates.drop(columns=["_platform_rank", "_keyword_rank"], errors="ignore")


def limit_navigation_rows_for_mode(section_rows: pd.DataFrame, display_mode: str) -> tuple[pd.DataFrame, int]:
    """Limit rows for collapsed sections according to selected display mode."""
    limits = SEARCH_MODE_LIMITS.get(display_mode, SEARCH_MODE_LIMITS["精简模式"])
    per_platform_limit = limits["per_platform"]
    section_limit = limits["section"]
    if per_platform_limit is None:
        return section_rows, len(section_rows)

    ranked = section_rows.copy()
    ranked["_keyword_rank"] = ranked["搜索词"].apply(keyword_display_rank)
    ranked = ranked.sort_values(["平台名", "_keyword_rank", "搜索词"])
    limited = ranked.groupby("平台名", group_keys=False).head(per_platform_limit)
    limited = limited.sort_values(["平台名", "_keyword_rank", "搜索词"])
    if section_limit is not None:
        limited = limited.head(section_limit)
    limited = limited.drop(columns=["_keyword_rank"], errors="ignore")
    return limited, len(limited)


def render_platform_navigation_section(
    section_rows: pd.DataFrame,
    section_name: str,
    show_fallback_engines: bool,
    group_by_platform: bool = True,
) -> None:
    """以平台导航形式展示一个分区。"""
    st.caption(f"{section_name}：按平台 + 搜索词合并展示，默认只显示推荐搜索入口。")
    if group_by_platform:
        for platform_name, platform_rows in section_rows.groupby("平台名", sort=False):
            st.markdown(f"**{platform_name}（{len(platform_rows)} 条）**")
            render_navigation_rows(platform_rows, show_fallback_engines)
    else:
        render_navigation_rows(section_rows, show_fallback_engines)


def render_navigation_rows(section_rows: pd.DataFrame, show_fallback_engines: bool) -> None:
    """Render compact row list without exposing raw URLs."""
    for row_index, row in section_rows.reset_index(drop=True).iterrows():
        cols = st.columns([1.2, 0.8, 2.0, 1.0, 2.0])
        with cols[0]:
            st.write(str(row.get("平台名", "")))
        with cols[1]:
            st.caption(str(row.get("区域", "")))
        with cols[2]:
            st.write(str(row.get("搜索词", "")))
        with cols[3]:
            st.write(str(row.get("搜索类型", "")))
        with cols[4]:
            render_row_link_buttons(row, show_fallback_engines)
        note = str(row.get("说明", "")).strip()
        if note and row_index < 3:
            st.caption(note)


def render_row_link_buttons(row: pd.Series, show_fallback_engines: bool) -> None:
    """Render recommended and optional fallback link buttons for one merged row."""
    links = list(row.get("推荐链接", []) or [])
    if show_fallback_engines:
        links.extend(list(row.get("备用链接", []) or []))
    if not links:
        st.caption(str(row.get("说明", "手动检查")))
        return

    button_columns = st.columns(min(len(links), 3))
    for index, link in enumerate(links):
        with button_columns[index % len(button_columns)]:
            st.link_button(
                format_link_button_label(link),
                str(link.get("url", "")),
                use_container_width=True,
            )


def format_link_button_label(link: dict) -> str:
    """Build compact button labels for row actions."""
    engine = str(link.get("engine", ""))
    labels = {
        "native": "打开原生",
        "baidu": "打开百度",
        "google": "打开Google",
    }
    return labels.get(engine, f"打开{link.get('label', '搜索')}")


def collect_links_for_rows(rows: pd.DataFrame, include_fallback: bool) -> list[str]:
    """Collect URLs from merged navigation rows."""
    urls = []
    for _, row in rows.iterrows():
        link_groups = [row.get("推荐链接", [])]
        if include_fallback:
            link_groups.append(row.get("备用链接", []))
        for links in link_groups:
            if not isinstance(links, list):
                continue
            for link in links:
                url = str(link.get("url", "")).strip()
                if url:
                    urls.append(url)
    return urls


def render_batch_open_links(
    navigation_table: pd.DataFrame,
    recommended_rows: pd.DataFrame,
    show_fallback_engines: bool,
) -> None:
    """按分类筛选后批量打开链接。"""
    with st.expander("批量打开链接", expanded=False):
        batch_scope = st.radio(
            "选择批量打开范围",
            ["推荐优先链接", "当前分区链接", "当前平台链接", "全部链接"],
            horizontal=True,
            key="search_batch_scope",
        )
        if batch_scope == "推荐优先链接":
            filtered_links = recommended_rows.copy()
        elif batch_scope == "当前分区链接":
            selected_section = st.selectbox(
                "选择分区",
                [section for section in SEARCH_CENTER_SECTION_ORDER if section in set(navigation_table["分区"])],
                key="search_batch_section",
            )
            filtered_links = navigation_table.loc[navigation_table["分区"].eq(selected_section)].copy()
        elif batch_scope == "当前平台链接":
            selected_platform = st.selectbox(
                "选择平台",
                sorted(navigation_table["平台名"].dropna().unique().tolist()),
                key="search_batch_platform",
            )
            filtered_links = navigation_table.loc[navigation_table["平台名"].eq(selected_platform)].copy()
        else:
            st.warning("全部链接数量较多，建议只在确实需要时使用。")
            filtered_links = navigation_table.copy()

        if filtered_links.empty:
            st.info("当前范围暂无可打开链接。")
            return

        filtered_links = filtered_links.reset_index(drop=True)
        batch_columns = ["打开", "分区", "平台名", "区域", "搜索词", "搜索类型", "推荐搜索"]
        if show_fallback_engines:
            batch_columns.append("备用搜索")
        edited_open_link_table = st.data_editor(
            filtered_links.loc[:, batch_columns],
            use_container_width=True,
            hide_index=True,
            column_order=batch_columns,
            column_config={
                "打开": st.column_config.CheckboxColumn("打开"),
                "分区": st.column_config.TextColumn("分区", disabled=True),
                "平台名": st.column_config.TextColumn("平台名", disabled=True),
                "区域": st.column_config.TextColumn("区域", disabled=True),
                "搜索词": st.column_config.TextColumn("搜索词", disabled=True),
                "搜索类型": st.column_config.TextColumn("搜索类型", disabled=True),
                "推荐搜索": st.column_config.TextColumn("推荐搜索", disabled=True),
                "备用搜索": st.column_config.TextColumn("备用搜索", disabled=True),
            },
            key="search_batch_open_editor",
        )

        selected_mask = edited_open_link_table["打开"].astype(bool)
        selected_rows = filtered_links.loc[selected_mask].copy()
        selected_links = collect_links_for_rows(selected_rows, include_fallback=show_fallback_engines)

        selected_count = len(selected_links)
        confirm_over_limit = False
        if selected_count > 10:
            st.warning("你将打开超过 10 个浏览器标签页，默认只打开前 10 个。")
            confirm_over_limit = st.checkbox("确认继续打开全部选中链接")

        if st.button(f"打开选中链接（{selected_count}）"):
            if selected_count == 0:
                st.info("请先在上方表格勾选要打开的链接。")
                return

            links_to_open = selected_links if confirm_over_limit or selected_count <= 10 else selected_links[:10]
            for url in links_to_open:
                webbrowser.open_new_tab(url)
            st.success(f"已提交打开 {len(links_to_open)} 个浏览器标签页。")
            if selected_count > len(links_to_open):
                st.info("还有未打开的链接；勾选确认后可一次打开全部。")


def get_steamdb_common_link_groups() -> dict[str, list[tuple[str, str]]]:
    """Return the SteamDB discovery links shared by Home and SteamDB tabs."""
    current_year = datetime.now().year
    return {
        "新作发现": [
            (f"Top Rated Releases {current_year}", f"https://steamdb.info/stats/gameratings/{current_year}/"),
            ("Top Rated Releases 2025", "https://steamdb.info/stats/gameratings/2025/"),
            ("Top Rated Releases 2027", "https://steamdb.info/stats/gameratings/2027/"),
            ("Upcoming Releases", "https://steamdb.info/upcoming/"),
            ("Release Calendar", "https://steamdb.info/calendar/"),
        ],
        "热度观察": [
            ("Live Player Charts", "https://steamdb.info/charts/"),
            ("Trending Followers", "https://steamdb.info/stats/trendingfollowers/"),
            ("Wishlist Activity", "https://steamdb.info/stats/wishlistactivity/"),
            ("Most Wishlisted", "https://steamdb.info/stats/mostwished/"),
            ("Global Top Sellers", "https://steamdb.info/stats/globaltopsellers/"),
            ("Weekly Top Sellers", "https://steamdb.info/topsellers/"),
        ],
        "活动 / 新品节": [
            ("活动入口：Steam Release Calendar", "https://steamdb.info/calendar/"),
            ("活动入口：Upcoming Releases", "https://steamdb.info/upcoming/"),
            ("活动入口：Wishlist Activity", "https://steamdb.info/stats/wishlistactivity/"),
            ("活动入口：Trending Followers", "https://steamdb.info/stats/trendingfollowers/"),
        ],
    }


def get_steam_news_links() -> list[tuple[str, str]]:
    return [
        ("Steam 商店首页", "https://store.steampowered.com/"),
        ("Steam News Hub", "https://store.steampowered.com/news/"),
        ("Steam Specials / 折扣活动", "https://store.steampowered.com/specials"),
        ("Steam Upcoming Events", "https://partner.steamgames.com/doc/marketing/upcoming_events"),
    ]


def render_home_dashboard_page() -> None:
    """Render the daily intelligence dashboard."""
    ensure_daily_watch_csv_exists(DAILY_WATCH_CSV_PATH)
    ensure_home_snapshot_csv_exists(HOME_SNAPSHOT_CSV_PATH)
    HOME_SNAPSHOT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    ensure_template_csv_exists(STEAMDB_TEMPLATE_CSV_PATH)
    ensure_watch_note_csv_exists(STEAMDB_WATCH_NOTE_CSV_PATH)
    ensure_candidate_csv_exists(CANDIDATE_CSV_PATH)
    ensure_candidate_pool_csv_exists(CANDIDATE_POOL_CSV_PATH)
    ensure_csv_exists(CSV_PATH)
    ensure_search_history_csv_exists(SEARCH_HISTORY_CSV_PATH)

    render_pending_home_target_notice()

    projects = load_projects(CSV_PATH, include_deleted=True)
    active_projects = projects.loc[projects["is_deleted"].astype(str).str.casefold() != "true"].copy()
    snapshots = load_home_snapshots(HOME_SNAPSHOT_CSV_PATH)
    daily_notes = load_daily_watch_notes(DAILY_WATCH_CSV_PATH)
    steamdb_notes = load_watch_notes(STEAMDB_WATCH_NOTE_CSV_PATH)
    candidate_pool = load_candidate_pool(CANDIDATE_POOL_CSV_PATH)
    pending_projects = filter_pending_projects(active_projects)
    header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([2, 1, 1, 1, 1])
    loaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["home_last_loaded_at"] = loaded_at
    with header_col1:
        st.caption(f"最后读取时间：{loaded_at}")
    with header_col2:
        force_refresh = st.button("刷新 Steam 图文源", key="home_steam_feed_refresh", use_container_width=True)
    with header_col3:
        if st.button("刷新当前卡片详情", key="home_appdetails_refresh", use_container_width=True):
            st.session_state["force_refresh_visible_appdetails"] = True
    with header_col4:
        if st.button("刷新当前卡片评价数据", key="home_review_stats_refresh", use_container_width=True):
            st.session_state["force_refresh_visible_review_stats"] = True
    with header_col5:
        if st.button("清理无效详情缓存", key="home_appdetails_clear_invalid", use_container_width=True):
            removed_count = clear_invalid_appdetails_cache(STEAM_APPDETAILS_CACHE_PATH)
            st.session_state["home_appdetails_clear_message"] = f"已清理 {removed_count} 条无效 appdetails 缓存。"
            st.rerun()
    if st.session_state.get("home_appdetails_clear_message"):
        st.success(st.session_state.pop("home_appdetails_clear_message"))

    render_home_metrics(daily_notes, active_projects, pending_projects, candidate_pool)
    st.caption("用于快速浏览最近采集、导入和待处理的 Steam 项目。优先展示最新采集、未上线、有 Demo、自发行、热门参考等项目。")

    steam_feed = load_steam_store_home_feed(STEAM_HOME_FEED_CACHE_PATH, force_refresh=force_refresh)
    feed = HomeFeedResult(message="SteamDB 自动抓取入口已下线；新项目发现主流程为 Steam 浏览器采集 + SteamDB 手动粘贴导入。")
    render_home_project_discovery_feed(candidate_pool, steam_feed, snapshots, daily_notes)

    with st.expander("高级 / 低频工具", expanded=False):
        render_home_candidate_pool_summary(candidate_pool)

        render_home_common_tools_grid()

        st.subheader("旧版雷达 / 手动观察")
        st.caption("低频辅助入口；主流程优先使用上方项目发现 Feed。")
        radar_col1, radar_col2 = st.columns([1, 1])
        with radar_col1:
            radar_refresh = st.button("刷新雷达", key="home_radar_refresh", use_container_width=True)
        with radar_col2:
            if st.button("刷新当前卡片", key="home_radar_refresh_visible_cards", use_container_width=True):
                st.session_state["force_refresh_visible_appdetails"] = True
                st.session_state["force_refresh_visible_review_stats"] = True
        with st.expander("更多刷新 / 缓存操作", expanded=False):
            more_col1, more_col2, more_col3 = st.columns(3)
            if more_col1.button("刷新 Steam 图文源", key="home_radar_refresh_feed_more", use_container_width=True):
                radar_refresh = True
            if more_col2.button("刷新当前卡片评论数据", key="home_radar_refresh_reviews_more", use_container_width=True):
                st.session_state["force_refresh_visible_review_stats"] = True
            if more_col3.button("清理无效详情缓存", key="home_radar_clear_invalid_more", use_container_width=True):
                removed_count = clear_invalid_appdetails_cache(STEAM_APPDETAILS_CACHE_PATH)
                st.session_state["home_appdetails_clear_message"] = f"已清理 {removed_count} 条无效 appdetails 缓存。"
                st.rerun()
        if radar_refresh:
            steam_feed = load_steam_store_home_feed(STEAM_HOME_FEED_CACHE_PATH, force_refresh=True)
        render_home_steam_store_discovery(steam_feed, snapshots, daily_notes)
        render_home_discovery_projects(feed, snapshots, daily_notes, steamdb_notes)

        st.subheader("最近处理 / 待处理")
        project_col1, project_col2 = st.columns([1, 1])
        with project_col1:
            render_home_recent_projects(active_projects)
        with project_col2:
            render_home_pending_projects(pending_projects)

        lower_col1, lower_col2 = st.columns([1, 1])
        with lower_col1:
            render_home_quick_actions()
        with lower_col2:
            render_home_snapshot_form()
            render_home_daily_watch_form()

        render_home_snapshot_manager(snapshots)
        render_home_daily_watch_history(daily_notes)
        render_home_data_health_check(steam_feed)
        render_home_debug_expander(feed, steam_feed)


def render_pending_home_target_notice() -> None:
    target = st.session_state.get("pending_home_target", "")
    if not target:
        return
    label_map = {
        "home": "查查 / Steam 项目直查",
        "profile": "一键项目画像",
        "steamdb": "SteamDB 发现",
        "search": "搜索中心",
        "history": "历史与导出",
        "daily_watch": "今日观察记录",
        "candidate_pool": "竞品与候选 / 项目候选池",
        "daily_workflow": "今日工作流",
    }
    label = label_map.get(str(target), str(target))
    st.info(f"已发送到【{label}】，请打开对应 Tab。相关字段已预填或目标已记录。")


HOME_FEED_FILTER_OPTIONS = ["全部", "即将推出", "近期上新", "待试玩", "值得联系", "竞品参考", "手动观察"]


def render_home_project_discovery_feed(
    candidate_pool: pd.DataFrame,
    steam_feed: SteamStoreFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
) -> None:
    st.subheader("项目发现 Feed")
    feed_filter = st.radio("Feed 筛选", HOME_FEED_FILTER_OPTIONS, horizontal=True, key="home_project_feed_filter")
    previous_filter = st.session_state.get("home_project_feed_previous_filter")
    if previous_filter != feed_filter:
        st.session_state["home_project_feed_visible_count"] = 12
        st.session_state["home_project_feed_previous_filter"] = feed_filter
    visible_count = int(st.session_state.get("home_project_feed_visible_count", 12) or 12)

    cards = build_home_project_feed_cards(candidate_pool, steam_feed, snapshots, daily_notes)
    filtered_cards = [card for card in cards if home_feed_card_matches_filter(card, feed_filter)]
    if not filtered_cards:
        st.info("当前筛选暂无项目。可以先用 Steam 浏览器采集，或切换到“全部”。")
        return

    visible_cards = enrich_steam_store_cards(filtered_cards[:visible_count], limit=visible_count)
    columns = st.columns(3)
    for index, card in enumerate(visible_cards):
        with columns[index % 3]:
            render_home_project_feed_card(card, index)

    if len(filtered_cards) > visible_count:
        if st.button("加载更多 12 个", key="home_project_feed_load_more", use_container_width=True):
            st.session_state["home_project_feed_visible_count"] = visible_count + 12
            st.rerun()
    st.caption(f"当前筛选 {len(filtered_cards)} 个项目，已显示 {min(visible_count, len(filtered_cards))} 个。")


def build_home_project_feed_cards(
    candidate_pool: pd.DataFrame,
    steam_feed: SteamStoreFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
) -> list[dict]:
    cards: list[dict] = []
    cards.extend(home_cards_from_browser_collected())
    cards.extend(home_cards_from_candidate_pool(candidate_pool))
    cards.extend(home_cards_from_appdetails_cache(limit=80))
    if len(cards) < 12:
        cards.extend(collect_steam_store_cards(steam_feed))
        cards.extend(collect_manual_observation_cards(snapshots, daily_notes))
    return dedupe_and_sort_home_project_feed_cards(cards)


def home_cards_from_browser_collected() -> list[dict]:
    try:
        collected = load_collected(STEAM_BROWSER_COLLECTED_CSV_PATH)
    except Exception:
        return []
    cards = []
    for _, row in collected.iterrows():
        row_dict = row.to_dict()
        appid = str(row_dict.get("appid", "") or "").strip()
        if not appid:
            continue
        cards.append(
            {
                "card_type": "steam_browser_collected",
                "record_id": f"browser_{appid}",
                "title": clean_candidate_value(row_dict.get("game_name")) or f"AppID {appid}",
                "game_name": clean_candidate_value(row_dict.get("game_name")) or f"AppID {appid}",
                "appid": appid,
                "source": "Steam 浏览器采集",
                "source_group": "Steam 浏览器采集",
                "source_url": clean_candidate_value(row_dict.get("source_page_url")) or steam_url_from_appid(appid),
                "steam_url": clean_candidate_value(row_dict.get("steam_url")) or steam_url_from_appid(appid),
                "steamdb_url": steamdb_app_url_from_appid(appid),
                "developer": clean_candidate_value(row_dict.get("developer")),
                "publisher": clean_candidate_value(row_dict.get("publisher")),
                "release_date": clean_candidate_value(row_dict.get("release_date") or row_dict.get("release_status")),
                "has_demo": clean_candidate_value(row_dict.get("has_demo")),
                "supports_schinese": clean_candidate_value(row_dict.get("supports_schinese")),
                "genres": clean_candidate_value(row_dict.get("genres_tags")),
                "auto_suggestion": clean_candidate_value(row_dict.get("import_suggestion")),
                "auto_reason": clean_candidate_value(row_dict.get("import_reason")),
                "next_action": "试玩 Demo" if clean_candidate_value(row_dict.get("import_suggestion")) == "待试玩" else "补项目画像",
                "feed_updated_at": clean_candidate_value(row_dict.get("collected_at")),
                "feed_source_rank": 1,
                "feed_category": "手动观察",
            }
        )
    return cards


def home_cards_from_candidate_pool(candidate_pool: pd.DataFrame) -> list[dict]:
    if candidate_pool.empty:
        return []
    data = apply_auto_suggestions(candidate_pool)
    cards = []
    for _, row in data.iterrows():
        row_dict = row.to_dict()
        if is_hidden_home_feed_candidate(row_dict):
            continue
        appid = clean_candidate_value(row_dict.get("appid"))
        game_name = clean_candidate_value(row_dict.get("game_name")) or (f"AppID {appid}" if appid else "")
        if not appid and not game_name:
            continue
        cards.append(
            {
                "card_type": "candidate_pool_feed",
                "record_id": clean_candidate_value(row_dict.get("candidate_id")) or appid or game_name,
                "title": game_name,
                "game_name": game_name,
                "appid": appid,
                "source": clean_candidate_value(row_dict.get("source")) or "候选池",
                "source_group": clean_candidate_value(row_dict.get("source")) or "候选池",
                "source_url": clean_candidate_value(row_dict.get("source_url")) or clean_candidate_value(row_dict.get("steam_url")),
                "steam_url": clean_candidate_value(row_dict.get("steam_url")) or steam_url_from_appid(appid),
                "steamdb_url": clean_candidate_value(row_dict.get("steamdb_url")) or steamdb_app_url_from_appid(appid),
                "developer": clean_candidate_value(row_dict.get("developer")),
                "publisher": clean_candidate_value(row_dict.get("publisher")),
                "release_date": clean_candidate_value(row_dict.get("release_date") or row_dict.get("release_status")),
                "has_demo": clean_candidate_value(row_dict.get("has_demo")),
                "supports_schinese": clean_candidate_value(row_dict.get("supports_schinese")),
                "genres": clean_candidate_value(row_dict.get("genres_tags")),
                "auto_suggestion": clean_candidate_value(row_dict.get("auto_suggestion")),
                "auto_reason": clean_candidate_value(row_dict.get("auto_reason")),
                "next_action": clean_candidate_value(row_dict.get("next_action")),
                "stage": clean_candidate_value(row_dict.get("stage")),
                "priority": clean_candidate_value(row_dict.get("priority")),
                "feed_updated_at": clean_candidate_value(row_dict.get("updated_at") or row_dict.get("created_at")),
                "feed_source_rank": 2,
                "feed_category": "候选池",
            }
        )
    return cards


def home_cards_from_appdetails_cache(limit: int = 80) -> list[dict]:
    cards = []
    try:
        summaries = load_cached_appdetails_summaries(STEAM_APPDETAILS_CACHE_PATH)
    except Exception:
        return []
    for appid, detail in list(summaries.items())[:limit]:
        if not isinstance(detail, dict):
            continue
        game_name = clean_candidate_value(detail.get("name") or detail.get("game_name"))
        if not game_name:
            continue
        cards.append(
            {
                "card_type": "appdetails_cache_feed",
                "record_id": f"cache_{appid}",
                "title": game_name,
                "game_name": game_name,
                "appid": str(appid),
                "source": "Steam 基础信息缓存",
                "source_group": "Steam 基础信息缓存",
                "source_url": steam_url_from_appid(str(appid)),
                "steam_url": steam_url_from_appid(str(appid)),
                "steamdb_url": steamdb_app_url_from_appid(str(appid)),
                "developer": clean_candidate_value(detail.get("developer")),
                "publisher": clean_candidate_value(detail.get("publisher")),
                "release_date": clean_candidate_value(detail.get("release_date")),
                "has_demo": clean_candidate_value(detail.get("has_demo")),
                "supports_schinese": clean_candidate_value(detail.get("supports_schinese")),
                "genres": clean_candidate_value(detail.get("genres_text")),
                "image_url": clean_candidate_value(detail.get("header_image")),
                "next_action": "补项目画像",
                "feed_updated_at": clean_candidate_value(detail.get("checked_at")),
                "feed_source_rank": 3,
                "feed_category": "缓存",
            }
        )
    return cards


def dedupe_and_sort_home_project_feed_cards(cards: list[dict]) -> list[dict]:
    cards = [card for card in cards if home_card_key(card)]
    cards.sort(key=lambda card: (int(card.get("feed_source_rank", 9) or 9), -home_feed_timestamp_value(card)))
    seen = set()
    output = []
    for card in cards:
        key = home_card_key(card)
        if key in seen:
            continue
        seen.add(key)
        output.append(card)
    return output


def home_feed_timestamp(card: dict) -> pd.Timestamp:
    value = card.get("feed_updated_at") or card.get("updated_at") or card.get("collected_at") or card.get("created_at")
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.Timestamp.min
    return ts


def home_feed_timestamp_value(card: dict) -> int:
    ts = home_feed_timestamp(card)
    if ts == pd.Timestamp.min:
        return 0
    return int(ts.value)


def is_hidden_home_feed_candidate(row: dict) -> bool:
    archived = clean_candidate_value(row.get("is_archived")).casefold()
    stage = clean_candidate_value(row.get("stage"))
    reject_reason = clean_candidate_value(row.get("reject_reason"))
    return archived in {"true", "1", "yes", "y"} or "放弃" in stage or bool(reject_reason)


def home_feed_card_matches_filter(card: dict, feed_filter: str) -> bool:
    if feed_filter == "全部":
        return True
    release_text = " ".join([str(card.get("release_date", "") or ""), str(card.get("release_status", "") or "")]).casefold()
    suggestion = str(card.get("auto_suggestion", "") or "")
    source = str(card.get("source_group", "") or card.get("source", "") or "")
    next_action = str(card.get("next_action", "") or "")
    if feed_filter == "即将推出":
        return any(token in release_text for token in ["coming soon", "tba", "即将", "未发售", "待定"])
    if feed_filter == "近期上新":
        return "Steam 浏览器采集" in source or "新" in release_text or "recent" in release_text
    if feed_filter == "待试玩":
        return "待试玩" in suggestion or "试玩" in next_action or str(card.get("has_demo", "") or "") == "是"
    if feed_filter == "值得联系":
        return "值得联系" in suggestion or "候选池观察" in suggestion
    if feed_filter == "竞品参考":
        return "竞品参考" in suggestion
    if feed_filter == "手动观察":
        return "浏览器采集" in source or "手动观察" in source or card.get("card_type") in {"steam_browser_collected", "daily_watch", "snapshot"}
    return True


def render_home_project_feed_card(card: dict, index: int) -> None:
    with st.container(border=True):
        image_url = resolve_home_card_image(card)
        if image_url:
            st.image(image_url, use_container_width=True)
        title = card.get("game_name") or card.get("title") or f"AppID {card.get('appid', '')}"
        st.markdown(f"**{title}**")
        st.caption(f"{card.get('source_group') or card.get('source') or '项目发现'} · AppID：{card.get('appid') or '未获取'}")
        suggestion = str(card.get("auto_suggestion", "") or "").strip()
        if "竞品参考" in suggestion:
            st.warning("竞品参考")
        elif suggestion:
            st.info(suggestion)
        st.caption(f"发售：{compact_card_value(card.get('release_date') or card.get('release_status'))}")
        st.caption(f"Demo：{compact_card_value(card.get('has_demo'))} · 简中：{compact_card_value(card.get('supports_schinese'))}")
        st.caption(f"开发：{compact_card_value(card.get('developer'))}")
        st.caption(f"发行：{compact_card_value(card.get('publisher'))}")
        st.caption(f"类型：{compact_card_value(card.get('genres') or card.get('genres_tags'), max_len=60)}")
        st.caption(f"下一步：{compact_card_value(card.get('next_action'))}")

        action_cols = st.columns(4)
        with action_cols[0]:
            if card.get("steam_url"):
                st.link_button("打开 Steam", card["steam_url"], use_container_width=True)
        with action_cols[1]:
            if st.button("加入候选池", key=f"feed_candidate_{home_card_key(card)}_{index}", use_container_width=True):
                add_home_card_to_candidate_pool(card)
        with action_cols[2]:
            if st.button("项目画像", key=f"feed_profile_{home_card_key(card)}_{index}", use_container_width=True):
                send_home_card_to_profile(card)
        with action_cols[3]:
            if st.button("忽略", key=f"feed_ignore_{home_card_key(card)}_{index}", use_container_width=True):
                ignore_home_card_candidate(card)
                st.rerun()


HOME_FEED_FILTER_OPTIONS = [
    "全部",
    "最新采集",
    "未上线/TBA",
    "有 Demo/可试玩",
    "无发行/自发行",
    "热门/评论多",
    "潜力观察",
    "竞品参考",
]

HOME_FEED_FILTER_DESCRIPTIONS = {
    "最新采集": "最近通过浏览器采集或导入的项目",
    "未上线/TBA": "仍处于 Coming Soon / TBA / 未来发售状态",
    "有 Demo/可试玩": "可优先进入试玩验证",
    "无发行/自发行": "潜在发行机会更高",
    "热门/评论多": "适合竞品或市场参考",
    "潜力观察": "需要补资料或继续判断",
    "竞品参考": "已有发行或成熟项目，适合参考不一定适合联系",
}

BIG_PUBLISHER_KEYWORDS = [
    "electronic arts",
    "ea",
    "capcom",
    "square enix",
    "bandai namco",
    "ubisoft",
    "sega",
    "xbox",
    "playstation",
    "sony",
    "nintendo",
    "netease",
    "tencent",
    "devolver",
    "team17",
    "raw fury",
    "focus entertainment",
    "paradox",
    "2k",
    "take-two",
]


def render_home_project_discovery_feed(
    candidate_pool: pd.DataFrame,
    steam_feed: SteamStoreFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
) -> None:
    st.subheader("项目发现 Feed")
    feed_filter = st.radio("Feed 筛选", HOME_FEED_FILTER_OPTIONS, horizontal=True, key="home_project_feed_filter")
    if feed_filter in HOME_FEED_FILTER_DESCRIPTIONS:
        st.caption(f"{feed_filter}：{HOME_FEED_FILTER_DESCRIPTIONS[feed_filter]}")

    visible_by_filter = st.session_state.setdefault("home_project_feed_visible_count_by_filter", {})
    if not isinstance(visible_by_filter, dict):
        visible_by_filter = {}
        st.session_state["home_project_feed_visible_count_by_filter"] = visible_by_filter
    visible_count = int(visible_by_filter.get(feed_filter, 12) or 12)

    candidate_appids = home_feed_candidate_appids(candidate_pool)
    cards = build_home_project_feed_cards(candidate_pool, steam_feed, snapshots, daily_notes)
    filtered_cards = [card for card in cards if home_feed_card_matches_filter(card, feed_filter)]
    filtered_cards = sort_home_project_feed_cards(filtered_cards, feed_filter)
    if not filtered_cards:
        st.info("当前筛选暂无项目。可以先用 Steam 浏览器采集，或切换到“全部”。")
        return

    visible_cards = enrich_steam_store_cards(filtered_cards[:visible_count], limit=visible_count)
    columns = st.columns(3)
    for index, card in enumerate(visible_cards):
        with columns[index % 3]:
            render_home_project_feed_card(card, index, card.get("appid") in candidate_appids)

    shown_count = min(visible_count, len(filtered_cards))
    if len(filtered_cards) > visible_count:
        if st.button("加载更多 12 个", key=f"home_project_feed_load_more_{feed_filter}", use_container_width=True):
            visible_by_filter[feed_filter] = visible_count + 12
            st.session_state["home_project_feed_visible_count_by_filter"] = visible_by_filter
            st.rerun()
    else:
        st.caption("已显示全部。")
    st.caption(f"当前分类 {len(filtered_cards)} 个项目，已显示 {shown_count} 个。")


def home_feed_candidate_appids(candidate_pool: pd.DataFrame) -> set[str]:
    if candidate_pool.empty or "appid" not in candidate_pool.columns:
        return set()
    return {str(value).strip() for value in candidate_pool["appid"].fillna("").tolist() if str(value).strip()}


def dedupe_and_sort_home_project_feed_cards(cards: list[dict]) -> list[dict]:
    cards = [card for card in cards if home_card_key(card)]
    cards.sort(key=lambda card: (-home_feed_timestamp_value(card), int(card.get("feed_source_rank", 9) or 9)))
    seen = set()
    output = []
    for card in cards:
        key = home_card_key(card)
        if key in seen:
            continue
        seen.add(key)
        output.append(card)
    return output


def sort_home_project_feed_cards(cards: list[dict], feed_filter: str) -> list[dict]:
    if feed_filter == "热门/评论多":
        return sorted(cards, key=lambda card: (-home_feed_review_count(card), -home_feed_timestamp_value(card)))
    if feed_filter == "竞品参考":
        return sorted(cards, key=lambda card: (-home_feed_review_count(card), not home_feed_has_review_score(card), home_feed_is_unreleased(card), -home_feed_timestamp_value(card)))
    if feed_filter == "未上线/TBA":
        return sorted(cards, key=lambda card: (-home_feed_opportunity_score(card), -home_feed_timestamp_value(card)))
    if feed_filter == "无发行/自发行":
        return sorted(cards, key=lambda card: (-home_feed_self_published_score(card), -home_feed_timestamp_value(card)))
    if feed_filter == "潜力观察":
        return sorted(cards, key=lambda card: (-home_feed_potential_score(card), -home_feed_timestamp_value(card)))
    return sorted(cards, key=lambda card: (-home_feed_timestamp_value(card), int(card.get("feed_source_rank", 9) or 9)))


def home_feed_card_matches_filter(card: dict, feed_filter: str) -> bool:
    if feed_filter == "全部":
        return True
    if feed_filter == "最新采集":
        return card.get("card_type") in {"steam_browser_collected", "candidate_pool_feed"} and home_feed_timestamp_value(card) > 0
    if feed_filter == "未上线/TBA":
        return home_feed_is_unreleased(card)
    if feed_filter == "有 Demo/可试玩":
        return home_feed_has_demo(card)
    if feed_filter == "无发行/自发行":
        return (
            home_feed_is_self_published(card)
            and not home_feed_is_competitor_reference(card)
            and not home_feed_is_big_publisher(card)
            and not (home_feed_is_released(card) and not home_feed_has_demo(card))
        )
    if feed_filter == "热门/评论多":
        return home_feed_review_count(card) >= 500 or home_feed_has_review_score(card) or home_feed_has_hot_source(card)
    if feed_filter == "潜力观察":
        return home_feed_is_potential_watch(card)
    if feed_filter == "竞品参考":
        return home_feed_is_competitor_reference(card)
    return True


def render_home_project_feed_card(card: dict, index: int, already_in_candidate_pool: bool = False) -> None:
    with st.container(border=True):
        image_url = resolve_home_card_image(card)
        if image_url:
            st.image(image_url, use_container_width=True)
        title = card.get("game_name") or card.get("title") or f"AppID {card.get('appid', '')}"
        st.markdown(f"**{title}**")
        st.caption(f"{card.get('source_group') or card.get('source') or '项目发现'} · AppID：{card.get('appid') or '未获取'}")

        tags = home_feed_card_tags(card)
        if tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))

        suggestion = str(card.get("auto_suggestion", "") or "").strip()
        if suggestion:
            if "竞品参考" in suggestion:
                st.warning(suggestion)
            else:
                st.info(suggestion)
        st.caption(f"发售：{compact_card_value(card.get('release_date') or card.get('release_status'))}")
        st.caption(f"Demo：{compact_card_value(card.get('has_demo'))} · 简中：{compact_card_value(card.get('supports_schinese'))}")
        st.caption(f"开发：{compact_card_value(card.get('developer'))}")
        st.caption(f"发行：{compact_card_value(card.get('publisher'))}")
        st.caption(f"类型：{compact_card_value(card.get('genres') or card.get('genres_tags'), max_len=60)}")
        review_count = home_feed_review_count(card)
        if review_count:
            st.caption(f"评论数：{review_count}")
        st.caption(f"下一步：{compact_card_value(card.get('next_action'))}")

        action_cols = st.columns(4)
        with action_cols[0]:
            if card.get("steam_url"):
                st.link_button("打开 Steam", card["steam_url"], use_container_width=True)
        with action_cols[1]:
            button_label = "已在候选池 / 更新候选池" if already_in_candidate_pool else "加入候选池"
            if st.button(button_label, key=f"feed_candidate_{home_card_key(card)}_{index}", use_container_width=True):
                add_home_card_to_candidate_pool(card)
        with action_cols[2]:
            if st.button("项目画像", key=f"feed_profile_{home_card_key(card)}_{index}", use_container_width=True):
                send_home_card_to_profile(card)
        with action_cols[3]:
            if st.button("忽略", key=f"feed_ignore_{home_card_key(card)}_{index}", use_container_width=True):
                ignore_home_card_candidate(card)
                st.rerun()


def home_feed_card_tags(card: dict) -> list[str]:
    tags = []
    if card.get("card_type") == "steam_browser_collected":
        tags.append("最新采集")
    if home_feed_is_unreleased(card):
        tags.append("未上线")
    if home_feed_has_demo(card):
        tags.append("有 Demo")
    if home_feed_supports_schinese(card):
        tags.append("简中")
    if home_feed_is_self_published(card):
        tags.append("自发行")
    if home_feed_is_competitor_reference(card):
        tags.append("竞品参考")
    if home_feed_is_data_incomplete(card):
        tags.append("资料不足")
    if home_feed_review_count(card) >= 500 or home_feed_has_hot_source(card):
        tags.append("热门参考")
    return tags[:7]


def home_feed_text_blob(card: dict) -> str:
    values = [
        card.get("release_status"),
        card.get("release_date"),
        card.get("stage"),
        card.get("next_action"),
        card.get("auto_suggestion"),
        card.get("import_suggestion"),
        card.get("auto_reason"),
        card.get("import_reason"),
        card.get("source"),
        card.get("source_group"),
    ]
    return " ".join([str(value) for value in values if value is not None]).casefold()


def home_feed_release_text(card: dict) -> str:
    return " ".join([str(card.get("release_date", "") or ""), str(card.get("release_status", "") or "")]).casefold()


def home_feed_has_demo(card: dict) -> bool:
    value = str(card.get("has_demo", "") or "").strip().casefold()
    text = home_feed_text_blob(card)
    return value in {"是", "yes", "true", "1", "有", "demo"} or "demo" in text or "试玩" in text


def home_feed_supports_schinese(card: dict) -> bool:
    value = str(card.get("supports_schinese", "") or "").strip().casefold()
    return value in {"是", "yes", "true", "1", "有", "简中", "支持"}


def home_feed_is_unreleased(card: dict) -> bool:
    text = home_feed_release_text(card)
    all_text = home_feed_text_blob(card)
    if any(token in text for token in ["coming soon", "tba", "即将推出", "即将", "待定", "未发售"]):
        return True
    if "未发售" in all_text:
        return True
    date_value = pd.to_datetime(card.get("release_date"), errors="coerce")
    if not pd.isna(date_value):
        try:
            date_value = date_value.tz_localize(None) if getattr(date_value, "tzinfo", None) else date_value
            today = pd.Timestamp.now(tz=None).normalize()
            return date_value.normalize() > today
        except Exception:
            return False
    return False


def home_feed_is_released(card: dict) -> bool:
    return not home_feed_is_unreleased(card) and bool(str(card.get("release_date", "") or "").strip())


def home_feed_is_self_published(card: dict) -> bool:
    developer = str(card.get("developer", "") or "").strip().casefold()
    publisher = str(card.get("publisher", "") or "").strip().casefold()
    explicit = str(card.get("is_self_published", "") or "").strip().casefold()
    return explicit in {"是", "yes", "true", "1"} or not publisher or (developer and publisher == developer)


def home_feed_is_big_publisher(card: dict) -> bool:
    publisher = str(card.get("publisher", "") or "").strip().casefold()
    if not publisher:
        return False
    return any(keyword in publisher for keyword in BIG_PUBLISHER_KEYWORDS)


def home_feed_review_count(card: dict) -> int:
    for key in ["review_count", "reviews_count", "reviews_total", "review_total"]:
        value = card.get(key)
        if value is None or value == "":
            continue
        digits = re.sub(r"[^0-9]", "", str(value))
        if digits:
            return int(digits)
    return 0


def home_feed_has_review_score(card: dict) -> bool:
    return bool(str(card.get("review_score", "") or card.get("review_summary", "") or "").strip())


def home_feed_has_hot_source(card: dict) -> bool:
    text = home_feed_text_blob(card)
    return any(token in text for token in ["热门", "热销", "top", "popular", "trending", "爆款"])


def home_feed_is_competitor_reference(card: dict) -> bool:
    text = home_feed_text_blob(card)
    developer = str(card.get("developer", "") or "").strip()
    publisher = str(card.get("publisher", "") or "").strip()
    if "竞品参考" in text:
        return True
    if publisher and developer and publisher.casefold() != developer.casefold():
        return True
    return home_feed_review_count(card) >= 1000 and home_feed_is_released(card)


def home_feed_is_data_incomplete(card: dict) -> bool:
    text = home_feed_text_blob(card)
    required = [card.get("game_name") or card.get("title"), card.get("developer"), card.get("publisher"), card.get("release_date")]
    return "待补资料" in text or "资料不足" in text or sum(bool(str(value or "").strip()) for value in required) <= 2


def home_feed_opportunity_score(card: dict) -> int:
    return sum(
        [
            4 if home_feed_is_unreleased(card) else 0,
            3 if home_feed_has_demo(card) else 0,
            2 if home_feed_supports_schinese(card) else 0,
            2 if home_feed_is_self_published(card) else 0,
            1 if card.get("card_type") == "steam_browser_collected" else 0,
        ]
    )


def home_feed_self_published_score(card: dict) -> int:
    return sum(
        [
            4 if home_feed_is_unreleased(card) else 0,
            3 if home_feed_has_demo(card) else 0,
            2 if home_feed_supports_schinese(card) else 0,
            2 if home_feed_is_self_published(card) else 0,
            1 if not home_feed_is_data_incomplete(card) else 0,
        ]
    )


def home_feed_potential_score(card: dict) -> int:
    return sum(
        [
            5 if home_feed_is_unreleased(card) else 0,
            3 if home_feed_has_demo(card) else 0,
            2 if home_feed_supports_schinese(card) else 0,
            2 if home_feed_is_self_published(card) else 0,
            1 if home_feed_is_data_incomplete(card) else 0,
        ]
    )


def home_feed_is_potential_watch(card: dict) -> bool:
    text = home_feed_text_blob(card)
    if any(token in text for token in ["候选池观察", "待开发商调查", "待补资料", "资料不足"]):
        return True
    if home_feed_is_unreleased(card) and (home_feed_has_demo(card) or home_feed_supports_schinese(card)):
        return True
    return home_feed_is_self_published(card) and home_feed_is_data_incomplete(card) and not home_feed_is_competitor_reference(card)


def home_cards_from_browser_collected() -> list[dict]:
    try:
        collected = load_collected(STEAM_BROWSER_COLLECTED_CSV_PATH)
    except Exception:
        return []
    cards = []
    for _, row in collected.iterrows():
        row_dict = row.to_dict()
        appid = str(row_dict.get("appid", "") or "").strip()
        if not appid:
            continue
        suggestion = clean_candidate_value(row_dict.get("import_suggestion"))
        cards.append(
            {
                "card_type": "steam_browser_collected",
                "record_id": f"browser_{appid}",
                "title": clean_candidate_value(row_dict.get("game_name")) or f"AppID {appid}",
                "game_name": clean_candidate_value(row_dict.get("game_name")) or f"AppID {appid}",
                "appid": appid,
                "source": "Steam 浏览器采集",
                "source_group": "Steam 浏览器采集",
                "source_url": clean_candidate_value(row_dict.get("source_page_url")) or steam_url_from_appid(appid),
                "steam_url": clean_candidate_value(row_dict.get("steam_url")) or steam_url_from_appid(appid),
                "steamdb_url": steamdb_app_url_from_appid(appid),
                "developer": clean_candidate_value(row_dict.get("developer")),
                "publisher": clean_candidate_value(row_dict.get("publisher")),
                "release_status": clean_candidate_value(row_dict.get("release_status")),
                "release_date": clean_candidate_value(row_dict.get("release_date") or row_dict.get("release_status")),
                "has_demo": clean_candidate_value(row_dict.get("has_demo")),
                "supports_schinese": clean_candidate_value(row_dict.get("supports_schinese")),
                "genres": clean_candidate_value(row_dict.get("genres_tags")),
                "review_score": clean_candidate_value(row_dict.get("review_score")),
                "review_count": clean_candidate_value(row_dict.get("review_count")),
                "header_image": clean_candidate_value(row_dict.get("header_image")),
                "image_url": clean_candidate_value(row_dict.get("header_image")),
                "auto_suggestion": suggestion,
                "import_suggestion": suggestion,
                "auto_reason": clean_candidate_value(row_dict.get("import_reason")),
                "import_reason": clean_candidate_value(row_dict.get("import_reason")),
                "next_action": "试玩 Demo" if suggestion == "待试玩" else "补项目画像",
                "feed_updated_at": clean_candidate_value(row_dict.get("collected_at")),
                "feed_source_rank": 1,
                "feed_category": "最新采集",
            }
        )
    return cards


def home_cards_from_candidate_pool(candidate_pool: pd.DataFrame) -> list[dict]:
    if candidate_pool.empty:
        return []
    data = apply_auto_suggestions(candidate_pool)
    cards = []
    for _, row in data.iterrows():
        row_dict = row.to_dict()
        if is_hidden_home_feed_candidate(row_dict):
            continue
        appid = clean_candidate_value(row_dict.get("appid"))
        game_name = clean_candidate_value(row_dict.get("game_name")) or (f"AppID {appid}" if appid else "")
        if not appid and not game_name:
            continue
        cards.append(
            {
                "card_type": "candidate_pool_feed",
                "record_id": clean_candidate_value(row_dict.get("candidate_id")) or appid or game_name,
                "title": game_name,
                "game_name": game_name,
                "appid": appid,
                "source": clean_candidate_value(row_dict.get("source")) or "候选池",
                "source_group": clean_candidate_value(row_dict.get("source")) or "候选池",
                "source_url": clean_candidate_value(row_dict.get("source_url")) or clean_candidate_value(row_dict.get("steam_url")),
                "steam_url": clean_candidate_value(row_dict.get("steam_url")) or steam_url_from_appid(appid),
                "steamdb_url": clean_candidate_value(row_dict.get("steamdb_url")) or steamdb_app_url_from_appid(appid),
                "developer": clean_candidate_value(row_dict.get("developer")),
                "publisher": clean_candidate_value(row_dict.get("publisher")),
                "release_status": clean_candidate_value(row_dict.get("release_status")),
                "release_date": clean_candidate_value(row_dict.get("release_date") or row_dict.get("release_status")),
                "has_demo": clean_candidate_value(row_dict.get("has_demo")),
                "supports_schinese": clean_candidate_value(row_dict.get("supports_schinese")),
                "genres": clean_candidate_value(row_dict.get("genres_tags")),
                "review_score": clean_candidate_value(row_dict.get("review_score")),
                "review_count": clean_candidate_value(row_dict.get("review_count")),
                "header_image": clean_candidate_value(row_dict.get("header_image")),
                "image_url": clean_candidate_value(row_dict.get("header_image")),
                "auto_suggestion": clean_candidate_value(row_dict.get("auto_suggestion")),
                "auto_reason": clean_candidate_value(row_dict.get("auto_reason")),
                "next_action": clean_candidate_value(row_dict.get("next_action")),
                "stage": clean_candidate_value(row_dict.get("stage")),
                "priority": clean_candidate_value(row_dict.get("priority")),
                "is_self_published": clean_candidate_value(row_dict.get("is_self_published")),
                "feed_updated_at": clean_candidate_value(row_dict.get("updated_at") or row_dict.get("created_at")),
                "feed_source_rank": 2,
                "feed_category": "候选池",
            }
        )
    return cards


def home_cards_from_appdetails_cache(limit: int = 80) -> list[dict]:
    cards = []
    try:
        summaries = load_cached_appdetails_summaries(STEAM_APPDETAILS_CACHE_PATH)
    except Exception:
        return []
    for appid, detail in list(summaries.items())[:limit]:
        if not isinstance(detail, dict):
            continue
        game_name = clean_candidate_value(detail.get("name") or detail.get("game_name"))
        if not game_name:
            continue
        cards.append(
            {
                "card_type": "appdetails_cache_feed",
                "record_id": f"cache_{appid}",
                "title": game_name,
                "game_name": game_name,
                "appid": str(appid),
                "source": "Steam 基础信息缓存",
                "source_group": "Steam 基础信息缓存",
                "source_url": steam_url_from_appid(str(appid)),
                "steam_url": steam_url_from_appid(str(appid)),
                "steamdb_url": steamdb_app_url_from_appid(str(appid)),
                "developer": clean_candidate_value(detail.get("developer")),
                "publisher": clean_candidate_value(detail.get("publisher")),
                "release_status": clean_candidate_value(detail.get("release_status")),
                "release_date": clean_candidate_value(detail.get("release_date") or detail.get("release_status")),
                "has_demo": clean_candidate_value(detail.get("has_demo")),
                "supports_schinese": clean_candidate_value(detail.get("supports_schinese")),
                "genres": clean_candidate_value(detail.get("genres_text") or detail.get("genres_tags")),
                "review_score": clean_candidate_value(detail.get("review_score")),
                "review_count": clean_candidate_value(detail.get("review_count")),
                "header_image": clean_candidate_value(detail.get("header_image")),
                "image_url": clean_candidate_value(detail.get("header_image")),
                "next_action": "补项目画像",
                "feed_updated_at": clean_candidate_value(detail.get("checked_at")),
                "feed_source_rank": 3,
                "feed_category": "缓存",
            }
        )
    return cards


def render_chacha_page() -> None:
    ensure_search_history_csv_exists(SEARCH_HISTORY_CSV_PATH)
    ensure_candidate_pool_csv_exists(CANDIDATE_POOL_CSV_PATH)
    ensure_csv_exists(CSV_PATH)
    render_home_chacha_lookup()


def render_home_chacha_lookup() -> None:
    pending_lookup = st.session_state.pop("pending_lookup_prefill", {})
    pending_input = ""
    if isinstance(pending_lookup, dict):
        pending_input = str(pending_lookup.get("lookup_input", "") or "").strip()
    pending_input = pending_input or st.session_state.pop("chacha_lookup_pending_input", "")
    if pending_input:
        st.session_state["home_direct_lookup_input"] = pending_input
    if st.session_state.get("chacha_lookup_clear_requested"):
        st.session_state["home_direct_lookup_input"] = ""
        st.session_state["home_direct_lookup_result"] = {}
        st.session_state["home_direct_lookup_message"] = ""
        st.session_state["home_direct_lookup_debug"] = {}
        st.session_state["chacha_lookup_loaded_history"] = {}
        st.session_state["chacha_search_candidates"] = []
        st.session_state["chacha_search_query_text"] = ""
        st.session_state["chacha_lookup_clear_requested"] = False

    st.subheader("查查 / Steam 项目直查")
    st.caption("输入 Steam 链接、SteamDB 链接、AppID 或游戏名，快速生成项目画像。")
    input_col, submit_col, clear_col, profile_col, save_col = st.columns([4, 1, 1, 1.2, 1.2])
    with input_col:
        raw_input = st.text_area(
            "Steam 链接 / SteamDB 链接 / AppID / 游戏名 / 混合文本",
            key="home_direct_lookup_input",
            height=88,
            placeholder="https://store.steampowered.com/app/3513350/Wuthering_Waves/\n或 Wuthering Waves / 3513350",
        )
    with submit_col:
        st.write("")
        do_lookup = st.button("查询", key="home_direct_lookup_submit", use_container_width=True)
    with clear_col:
        st.write("")
        do_clear = st.button("清空", key="home_direct_lookup_clear", use_container_width=True)
    with profile_col:
        st.write("")
        send_profile = st.button("发送到项目画像", key="chacha_send_profile", use_container_width=True)
    with save_col:
        st.write("")
        save_project = st.button("保存为项目记录", key="chacha_save_project", use_container_width=True)

    if do_clear:
        st.session_state["chacha_lookup_clear_requested"] = True
        st.rerun()

    if do_lookup:
        result, debug = run_home_chacha_lookup(raw_input)
        st.session_state["home_direct_lookup_result"] = result
        st.session_state["home_direct_lookup_debug"] = debug
        st.session_state["home_direct_lookup_message"] = debug.get("message", "")
        maybe_save_chacha_history(raw_input, result, debug)

    message = st.session_state.get("home_direct_lookup_message", "")
    if message:
        if st.session_state.get("home_direct_lookup_debug", {}).get("direct_lookup_error"):
            st.warning(message)
        else:
            st.success(message)

    result = st.session_state.get("home_direct_lookup_result", {})
    if isinstance(result, dict) and result:
        render_home_chacha_result(result)

    render_chacha_search_candidates()

    if send_profile:
        if isinstance(result, dict) and result:
            send_home_direct_lookup_to_profile(result)
        else:
            st.warning("请先查询或载入一条查查历史。")
    if save_project:
        if isinstance(result, dict) and result:
            save_quick_capture_project(result)
        else:
            st.warning("请先查询或载入一条查查历史。")

    render_chacha_recent_history()


def run_home_chacha_lookup(raw_input: str) -> tuple[dict, dict]:
    clean_input = str(raw_input or "").strip()
    appid = parse_appid(clean_input)
    query_type = detect_chacha_query_type(clean_input, appid)
    debug = {
        "direct_lookup_input": clean_input,
        "direct_lookup_appid": appid,
        "direct_lookup_query_type": query_type,
        "direct_lookup_status": "pending",
        "direct_lookup_error": "",
        "direct_lookup_appdetails_status": "",
        "message": "",
    }
    if appid:
        st.session_state["chacha_search_candidates"] = []
        st.session_state["chacha_search_query_text"] = ""
        cards = build_home_quick_appid_result_cards(appid, raw_input=clean_input)
        card = cards[0] if cards else {}
        debug["direct_lookup_status"] = "success" if card else "failed"
        debug["direct_lookup_appdetails_status"] = str(card.get("appdetails_status") or card.get("detail_fetch_status") or "")
        debug["message"] = "查询完成。" if card else "未获取到 Steam 项目数据。"
        return card, debug

    search_query = extract_chacha_game_query(clean_input)
    if not search_query:
        st.session_state["chacha_search_candidates"] = []
        st.session_state["chacha_search_query_text"] = ""
        debug["direct_lookup_status"] = "failed"
        debug["direct_lookup_error"] = "query_empty"
        debug["message"] = "请输入 Steam 链接、SteamDB 链接、AppID 或游戏名。"
        return {}, debug

    candidates, search_errors = build_chacha_text_search_candidates(search_query, clean_input, query_type)
    st.session_state["chacha_search_candidates"] = candidates
    st.session_state["chacha_search_query_text"] = clean_input

    debug["direct_lookup_status"] = "candidate_selection_required"
    debug["direct_lookup_error"] = "; ".join(search_errors[:3])
    debug["message"] = "普通文本搜索已进入低信任候选模式。请先选择正确项目，不会自动写入历史。"
    return {}, debug


def build_chacha_search_candidate(item: SteamStoreFeedItem, query_text: str, query_type: str) -> dict:
    candidate = steam_store_item_to_card(item)
    candidate["query_text"] = query_text
    candidate["query_type"] = query_type
    candidate["last_result_status"] = "Steam 搜索候选，待人工确认"
    return candidate


def build_chacha_text_search_candidates(search_query: str, raw_input: str, query_type: str) -> tuple[list[dict], list[str]]:
    local_candidates = build_chacha_local_exact_candidates(search_query, raw_input, query_type)
    steam_candidates, errors = fetch_chacha_steam_search_candidates(search_query, raw_input, query_type)
    candidates = dedupe_chacha_candidates(local_candidates + steam_candidates)
    if candidates:
        candidates = enrich_steam_store_cards(candidates[:10], limit=10)
        candidates = [score_chacha_candidate(search_query, candidate) for candidate in candidates]
        candidates.sort(
            key=lambda card: (
                int(card.get("match_score", 0) or 0),
                1 if card.get("candidate_source") == "local_exact" else 0,
            ),
            reverse=True,
        )
    return candidates, errors


def build_chacha_local_exact_candidates(search_query: str, raw_input: str, query_type: str) -> list[dict]:
    normalized_query = normalize_chacha_match_text(search_query)
    if not normalized_query:
        return []
    candidates: list[dict] = []

    history = load_search_history(SEARCH_HISTORY_CSV_PATH)
    for _, row in history.iterrows():
        row_dict = row.to_dict()
        if chacha_row_matches_query(row_dict, normalized_query, ["game_name", "query_text"]):
            candidates.append(chacha_candidate_from_row(row_dict, raw_input, query_type, "local_exact", "本地查查历史精确匹配"))

    projects = load_projects(CSV_PATH, include_deleted=False)
    for _, row in projects.iterrows():
        row_dict = row.to_dict()
        if chacha_row_matches_query(row_dict, normalized_query, ["game_name"]):
            candidates.append(chacha_candidate_from_row(row_dict, raw_input, query_type, "local_exact", "已保存项目记录精确匹配"))

    for appid, detail in load_cached_appdetails_summaries(STEAM_APPDETAILS_CACHE_PATH).items():
        if not isinstance(detail, dict):
            continue
        name = detail.get("name") or detail.get("game_name")
        if normalize_chacha_match_text(name) == normalized_query:
            candidates.append(chacha_candidate_from_appdetails(str(appid), detail, raw_input, query_type))
    return candidates


def fetch_chacha_steam_search_candidates(search_query: str, raw_input: str, query_type: str) -> tuple[list[dict], list[str]]:
    regions = [
        ("us", "english"),
        ("jp", "english"),
        ("hk", "english"),
        ("tw", "tchinese"),
    ]
    candidates: list[dict] = []
    errors: list[str] = []
    for country, language in regions:
        result = search_steam_store_items(
            search_query,
            STEAM_SEARCH_CACHE_PATH,
            count=10,
            country=country,
            language=language,
        )
        if result.error:
            errors.append(f"{country}/{language}: {result.error}")
        for item in result.items[:10]:
            candidate = build_chacha_search_candidate(item, raw_input, query_type)
            candidate["candidate_source"] = f"steam_search_{country}_{language}"
            candidate["match_reason"] = f"Steam 搜索召回：{country}/{language}"
            candidates.append(candidate)
    return candidates, errors


def chacha_row_matches_query(row: dict, normalized_query: str, fields: list[str]) -> bool:
    return any(normalize_chacha_match_text(row.get(field)) == normalized_query for field in fields)


def chacha_candidate_from_row(row: dict, raw_input: str, query_type: str, source: str, reason: str) -> dict:
    appid = str(row.get("appid", "") or "").strip()
    return {
        "card_type": "steam_store",
        "record_id": appid or str(row.get("history_id") or row.get("record_id") or ""),
        "title": str(row.get("game_name", "") or row.get("title", "") or appid or "未获取"),
        "game_name": str(row.get("game_name", "") or row.get("title", "") or ""),
        "appid": appid,
        "source": reason,
        "source_group": reason,
        "source_filter": "local_exact",
        "search_source_filter": "local_exact",
        "source_url": str(row.get("steam_url", "") or steam_url_from_appid(appid)),
        "steam_url": str(row.get("steam_url", "") or steam_url_from_appid(appid)),
        "steamdb_url": str(row.get("steamdb_url", "") or steamdb_app_url_from_appid(appid)),
        "image_url": str(row.get("image_url", "") or ""),
        "developer": str(row.get("developer", "") or "未获取"),
        "publisher": str(row.get("publisher", "") or "未获取"),
        "release_date": str(row.get("release_date", "") or row.get("release_status", "") or "未获取"),
        "genres": str(row.get("genre_tags", "") or row.get("genres", "") or "未获取"),
        "short_description": str(row.get("short_description", "") or row.get("note", "") or row.get("first_impression", "") or ""),
        "query_text": raw_input,
        "query_type": query_type,
        "candidate_source": source,
        "match_reason": reason,
        "last_result_status": "本地精确匹配候选，待人工确认",
    }


def chacha_candidate_from_appdetails(appid: str, detail: dict, raw_input: str, query_type: str) -> dict:
    card = {
        "card_type": "steam_store",
        "record_id": appid,
        "title": detail.get("name") or f"AppID {appid}",
        "game_name": detail.get("name") or "",
        "appid": appid,
        "source": "appdetails 缓存精确匹配",
        "source_group": "appdetails 缓存精确匹配",
        "source_filter": "local_appdetails_cache",
        "search_source_filter": "local_appdetails_cache",
        "source_url": steam_url_from_appid(appid),
        "steam_url": steam_url_from_appid(appid),
        "steamdb_url": steamdb_app_url_from_appid(appid),
        "image_url": detail.get("header_image") or detail.get("capsule_image") or "",
        "developer": detail.get("developer") or _join_home_card_list(detail.get("developers")) or "未获取",
        "publisher": detail.get("publisher") or _join_home_card_list(detail.get("publishers")) or "未获取",
        "release_date": detail.get("release_date") or "未获取",
        "genres": detail.get("genres_text") or _join_home_card_list(detail.get("genres")) or "未获取",
        "short_description": detail.get("short_description") or "",
        "query_text": raw_input,
        "query_type": query_type,
        "candidate_source": "local_exact",
        "match_reason": "appdetails 缓存精确匹配",
        "last_result_status": "本地 appdetails 缓存精确匹配候选，待人工确认",
    }
    return merge_appdetails_into_home_card(card, detail)


def dedupe_chacha_candidates(candidates: list[dict]) -> list[dict]:
    output = []
    seen = set()
    for candidate in candidates:
        appid = str(candidate.get("appid", "") or "").strip()
        name_key = normalize_chacha_match_text(candidate.get("game_name") or candidate.get("title"))
        key = appid or name_key
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(candidate)
    return output


def score_chacha_candidate(query: str, candidate: dict) -> dict:
    output = dict(candidate)
    raw_name = str(output.get("game_name") or output.get("title") or "")
    normalized_query = normalize_chacha_match_text(query)
    normalized_name = normalize_chacha_match_text(raw_name)
    query_tokens = chacha_match_tokens(query)
    name_tokens = set(chacha_match_tokens(raw_name))
    score = 0
    reason = output.get("match_reason") or "Steam 搜索候选"

    if output.get("candidate_source") == "local_exact" and normalized_name == normalized_query:
        score = 100
        reason = output.get("match_reason") or "本地精确匹配"
    elif normalized_query and normalized_query == normalized_name:
        score = 100
        reason = "标题完全匹配"
    elif normalized_query and normalized_query in normalized_name:
        score = 80
        reason = "查询词是标题连续子串"
    elif query_tokens:
        matched_tokens = [token for token in query_tokens if token in name_tokens or token in normalized_name]
        token_ratio = len(matched_tokens) / len(query_tokens)
        if token_ratio >= 0.75:
            score = 60
            reason = "查询词 token 大部分命中标题"
        else:
            score = int(SequenceMatcher(None, normalized_query, normalized_name).ratio() * 45)
            reason = "标题相似度较低"
    else:
        score = int(SequenceMatcher(None, normalized_query, normalized_name).ratio() * 45)
        reason = "标题相似度较低"

    output["match_score"] = str(max(0, min(100, score)))
    output["match_reason"] = reason
    output["is_main_candidate"] = "是" if is_chacha_main_candidate(output) else "否"
    return output


def normalize_chacha_match_text(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(value or "").casefold())


def chacha_match_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^0-9a-z\u4e00-\u9fff]+", str(value or "").casefold()) if token]


def is_chacha_main_candidate(candidate: dict) -> bool:
    try:
        score = int(str(candidate.get("match_score", "0") or "0"))
    except ValueError:
        score = 0
    return score >= 60 or str(candidate.get("candidate_source", "") or "") == "local_exact"


def query_chacha_candidate_detail(candidate: dict, raw_input: str, query_type: str = "game_name") -> tuple[dict, dict]:
    appid = str(candidate.get("appid", "") or "").strip()
    debug = {
        "direct_lookup_input": str(raw_input or "").strip(),
        "direct_lookup_appid": appid,
        "direct_lookup_query_type": query_type,
        "direct_lookup_status": "confirmed_candidate",
        "direct_lookup_error": "",
        "direct_lookup_appdetails_status": "",
        "message": "",
    }
    if not appid:
        debug["direct_lookup_status"] = "failed"
        debug["direct_lookup_error"] = "candidate_appid_empty"
        debug["message"] = "候选缺少 AppID，无法查询详情。"
        return {}, debug

    cards = build_home_quick_appid_result_cards(appid, raw_input=raw_input)
    card = cards[0] if cards else dict(candidate)
    card["query_text"] = str(raw_input or "").strip()
    card["query_type"] = query_type
    card["last_result_status"] = "已手动确认 Steam 搜索候选"
    debug["direct_lookup_appid"] = str(card.get("appid", "") or appid)
    debug["direct_lookup_status"] = "confirmed_candidate" if card else "failed"
    debug["direct_lookup_appdetails_status"] = str(card.get("appdetails_status") or card.get("detail_fetch_status") or "")
    debug["message"] = "已按选中候选查询详情。"
    return card, debug


def render_home_chacha_result(card: dict) -> None:
    review_score = format_review_summary(card)
    rows = [
        {"字段": "游戏名", "内容": card.get("game_name") or card.get("title") or "未获取"},
        {"字段": "AppID", "内容": card.get("appid") or "未获取"},
        {"字段": "Steam 链接", "内容": card.get("steam_url") or "未获取"},
        {"字段": "开发商", "内容": compact_card_value(card.get("developer"))},
        {"字段": "发行商", "内容": compact_card_value(card.get("publisher"))},
        {"字段": "发售状态", "内容": compact_card_value(card.get("release_date") or card.get("release_status"))},
        {"字段": "好评率 / 评测数", "内容": review_score},
        {"字段": "appdetails_status", "内容": card.get("appdetails_status") or card.get("detail_fetch_status") or "未获取"},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    link_col1, link_col2 = st.columns(2)
    with link_col1:
        if card.get("steam_url"):
            st.link_button("打开 Steam", card["steam_url"], use_container_width=True)
    with link_col2:
        if card.get("steamdb_url"):
            st.link_button("打开 SteamDB", card["steamdb_url"], use_container_width=True)
    appid = str(card.get("appid", "") or "").strip()
    if appid and find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid):
        if st.button("更新候选池信息", key=f"chacha_update_candidate_pool_{appid}", use_container_width=True):
            ok, message = update_candidate_pool_basic_info_from_mapping(
                candidate_pool_update_payload_from_chacha(card),
                source="查查",
            )
            if ok:
                st.success(message)
            else:
                st.info(message)
    with st.expander("查看完整解析结果", expanded=False):
        st.json({key: value for key, value in card.items() if key not in {"screenshots", "movies"}})


def render_chacha_search_candidates() -> None:
    candidates = st.session_state.get("chacha_search_candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return

    st.markdown("**Steam 搜索候选**")
    st.caption("普通文本搜索为低信任候选模式。请点击“查询此候选”确认正确项目，候选列表本身不会写入历史。")

    main_candidates = [candidate for candidate in candidates if is_chacha_main_candidate(candidate)]
    low_candidates = [candidate for candidate in candidates if not is_chacha_main_candidate(candidate)]

    if not main_candidates:
        st.warning("未找到高相关 Steam 候选。建议粘贴 Steam 链接或 AppID。")
        st.code("https://store.steampowered.com/app/3513350/Wuthering_Waves/\nAppID: 3513350", language="text")
    else:
        for index, candidate in enumerate(main_candidates, start=1):
            render_chacha_candidate_card(candidate, f"main_{index}")

    if low_candidates:
        with st.expander("低相关候选", expanded=False):
            st.caption("以下结果相关性较低，默认不作为主候选。只有确认无误后才点击查询。")
            for index, candidate in enumerate(low_candidates, start=1):
                render_chacha_candidate_card(candidate, f"low_{index}")


def render_chacha_candidate_card(candidate: dict, key_suffix: str) -> None:
    query_text = str(st.session_state.get("chacha_search_query_text", "") or "").strip()
    appid = str(candidate.get("appid", "") or "").strip()
    name = candidate.get("game_name") or candidate.get("title") or "未获取"
    image_url = str(candidate.get("image_url") or candidate.get("header_image") or candidate.get("capsule_image") or "").strip()
    score = str(candidate.get("match_score", "") or "0")
    reason = str(candidate.get("match_reason", "") or "未记录")
    steam_url = str(candidate.get("steam_url") or steam_url_from_appid(appid) or "").strip()
    steamdb_url = str(candidate.get("steamdb_url") or steamdb_app_url_from_appid(appid) or "").strip()

    st.markdown("---")
    image_col, info_col, action_col = st.columns([1.1, 3, 1.2])
    with image_col:
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.caption("暂无商店图")
    with info_col:
        st.markdown(f"**{name}**")
        st.write(f"AppID：{appid or '未获取'}")
        st.write(f"开发商：{compact_card_value(candidate.get('developer'))}")
        st.write(f"发行商：{compact_card_value(candidate.get('publisher'))}")
        st.write(f"发售日期：{compact_card_value(candidate.get('release_date') or candidate.get('release_status'))}")
        st.write(f"类型 / 标签：{compact_card_value(candidate.get('genres') or candidate.get('tags'))}")
        description = compact_card_value(candidate.get("short_description"), max_len=180)
        if description != "未获取":
            st.caption(description)
        st.caption(f"匹配分数：{score}；匹配原因：{reason}")
    with action_col:
        if steam_url:
            st.link_button("打开 Steam", steam_url, use_container_width=True)
        if steamdb_url:
            st.link_button("打开 SteamDB", steamdb_url, use_container_width=True)
        if st.button("查询此候选", key=f"chacha_candidate_query_{key_suffix}_{appid or name}", use_container_width=True):
            card, debug = query_chacha_candidate_detail(candidate, query_text, candidate.get("query_type") or "game_name")
            st.session_state["home_direct_lookup_result"] = card
            st.session_state["home_direct_lookup_debug"] = debug
            st.session_state["home_direct_lookup_message"] = debug.get("message", "")
            maybe_save_chacha_history(query_text, card, debug)
            st.session_state["chacha_search_candidates"] = []
            st.session_state["chacha_search_query_text"] = ""
            st.rerun()


def render_chacha_recent_history() -> None:
    st.markdown("**最近查过**")
    st.caption("查查搜索历史记录所有查查过的项目，即使没有保存；历史项目记录只记录已经保存为项目记录的项目。")
    records = load_search_history(SEARCH_HISTORY_CSV_PATH)
    filter_col, select_col = st.columns([1, 2])
    with filter_col:
        keyword = st.text_input("历史过滤关键词", key="chacha_history_filter")
    filtered = filter_search_history(records, keyword=keyword, limit=30)
    if filtered.empty:
        st.info("暂无查查搜索历史。")
        return
    options = [history_option_label(row.to_dict()) for _, row in filtered.iterrows()]
    with select_col:
        selected_label = st.selectbox("历史", options, key="chacha_history_select")
    selected_index = options.index(selected_label)
    selected_row = filtered.iloc[selected_index].to_dict()
    action_cols = st.columns(6)
    if action_cols[0].button("载入历史", key="chacha_history_load", use_container_width=True):
        load_chacha_history_into_input(selected_row)
        st.success("已载入历史摘要，未重新请求网络。")
    if action_cols[1].button("重新查询", key="chacha_history_rerun", use_container_width=True):
        query = selected_row.get("steam_url") or selected_row.get("appid") or selected_row.get("game_name") or selected_row.get("query_text")
        st.session_state["pending_lookup_prefill"] = {"lookup_input": query, "source": "查查历史"}
        result, debug = run_home_chacha_lookup(query)
        st.session_state["home_direct_lookup_result"] = result
        st.session_state["home_direct_lookup_debug"] = debug
        st.session_state["home_direct_lookup_message"] = debug.get("message", "")
        maybe_save_chacha_history(query, result, debug)
        st.rerun()
    if action_cols[2].button("发送到项目画像", key="chacha_history_profile", use_container_width=True):
        send_home_direct_lookup_to_profile(search_history_to_prefill(selected_row))
    with action_cols[3]:
        if selected_row.get("steam_url"):
            st.link_button("打开 Steam", selected_row["steam_url"], use_container_width=True)
    with action_cols[4]:
        if selected_row.get("steamdb_url"):
            st.link_button("打开 SteamDB", selected_row["steamdb_url"], use_container_width=True)
    with action_cols[5]:
        st.text_input("AppID", value=selected_row.get("appid", ""), key=f"chacha_history_copy_appid_{selected_row.get('history_id', '')}")

    cleanup_cols = st.columns([1, 1, 2])
    if cleanup_cols[0].button("删除当前历史", key="chacha_history_delete_current", use_container_width=True):
        delete_search_history_record(
            SEARCH_HISTORY_CSV_PATH,
            history_id=str(selected_row.get("history_id", "") or ""),
            appid=str(selected_row.get("appid", "") or ""),
        )
        st.success("已删除当前查查历史。")
        st.rerun()
    clear_confirmed = cleanup_cols[1].checkbox(
        "我确认清空全部查查搜索历史",
        key="chacha_history_clear_confirmed",
    )
    if cleanup_cols[2].button("清空全部查查历史", key="chacha_history_clear_all", use_container_width=True):
        if clear_confirmed:
            clear_search_history(SEARCH_HISTORY_CSV_PATH)
            st.success("已清空全部查查搜索历史。")
            st.rerun()
        else:
            st.warning("请先勾选二次确认。")


def load_chacha_history_into_input(row: dict) -> None:
    query = row.get("steam_url") or row.get("appid") or row.get("game_name") or row.get("query_text") or ""
    st.session_state["pending_lookup_prefill"] = {"lookup_input": query, "source": "查查历史"}
    st.session_state["chacha_lookup_loaded_history"] = search_history_to_prefill(row)
    st.session_state["home_direct_lookup_result"] = search_history_to_prefill(row)
    st.session_state["home_direct_lookup_message"] = "已载入查查历史。点击“重新查询”才会重新请求网络。"
    st.rerun()


def maybe_save_chacha_history(raw_input: str, card: dict, debug: dict) -> None:
    if debug.get("direct_lookup_status") not in {"success", "high_confidence", "confirmed_candidate"}:
        return
    if debug.get("direct_lookup_error"):
        return
    if not isinstance(card, dict) or not card:
        return
    appid = str(card.get("appid", "") or "").strip()
    game_name = str(card.get("game_name") or card.get("title") or "").strip()
    if not appid and not game_name:
        return
    record = SearchHistoryRecord(
        query_text=str(raw_input or "").strip(),
        query_type=debug.get("direct_lookup_query_type") or detect_chacha_query_type(str(raw_input or ""), appid),
        appid=appid,
        game_name=game_name,
        steam_url=str(card.get("steam_url", "") or "").strip(),
        steamdb_url=str(card.get("steamdb_url", "") or "").strip(),
        developer=_clean_prefill_value(card.get("developer")),
        publisher=_clean_prefill_value(card.get("publisher")),
        release_date=_clean_prefill_value(card.get("release_date") or card.get("release_status")),
        review_score=str(card.get("positive_rate") or card.get("review_score_desc") or "").strip(),
        review_count=str(card.get("review_total") or "").strip(),
        last_result_status=debug.get("message") or card.get("last_result_status") or "",
        note=str(card.get("note", "") or "").strip(),
    )
    upsert_search_history(SEARCH_HISTORY_CSV_PATH, record)


def detect_chacha_query_type(raw_input: str, appid: str = "") -> str:
    text = str(raw_input or "").strip()
    lowered = text.casefold()
    if "store.steampowered.com/app/" in lowered:
        return "steam_url"
    if "steamdb.info/app/" in lowered:
        return "steamdb_url"
    if appid and text == appid:
        return "appid"
    if appid and len(text.split()) > 1:
        return "mixed_text"
    if text:
        return "game_name"
    return "unknown"


def extract_chacha_game_query(raw_input: str) -> str:
    text = str(raw_input or "").strip()
    if not text:
        return ""
    first_line = first_meaningful_capture_line(text, extract_urls(text))
    return first_line or text[:120]


def format_review_summary(card: dict) -> str:
    rate = str(card.get("positive_rate") or "").strip()
    total = str(card.get("review_total") or "").strip()
    desc = str(card.get("review_score_desc") or "").strip()
    parts = [part for part in [rate, total, desc] if part and part not in {"0", "未获取", "未确认"}]
    return " / ".join(parts) if parts else "未获取"


def render_quick_capture_entry() -> None:
    with st.expander("快速收录项目（低频补充入口）", expanded=False):
        raw_text = st.text_area(
            "粘贴 Steam / SteamDB 链接、AppID、游戏名、社媒链接或备注",
            height=150,
            key="quick_capture_input",
            placeholder="Deadly Trick\nhttps://store.steampowered.com/app/xxxx/\nYouTube 最高播放 12000\n开发商 Finalblow\n计划参加 Steam Next Fest",
        )
        action_cols = st.columns(5)
        parse_clicked = action_cols[0].button("解析", key="quick_capture_parse", use_container_width=True)
        save_project_clicked = action_cols[1].button("保存为项目记录", key="quick_capture_save_project", use_container_width=True)
        save_profile_clicked = action_cols[2].button("保存并进入项目画像", key="quick_capture_save_profile", use_container_width=True)
        save_intel_clicked = action_cols[3].button("保存为外部情报", key="quick_capture_save_external", use_container_width=True)
        clear_clicked = action_cols[4].button("清空", key="quick_capture_clear", use_container_width=True)

        if clear_clicked:
            st.session_state["quick_capture_input"] = ""
            st.session_state["quick_capture_parsed"] = {}
            st.rerun()

        should_parse = parse_clicked or save_project_clicked or save_profile_clicked or save_intel_clicked
        parsed = st.session_state.get("quick_capture_parsed", {})
        if should_parse:
            parsed = parse_quick_capture_text(raw_text)
            st.session_state["quick_capture_parsed"] = parsed
            st.session_state["quick_capture_last_parsed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["quick_capture_links_count"] = len(parsed.get("external_links", []))
            st.session_state["quick_capture_appid"] = parsed.get("appid", "")

        if isinstance(parsed, dict) and parsed:
            render_quick_capture_preview(parsed)

        if save_project_clicked:
            save_quick_capture_project(parsed)
        if save_profile_clicked:
            save_quick_capture_to_profile(parsed)
        if save_intel_clicked:
            save_quick_capture_external_intel(parsed)


def parse_quick_capture_text(raw_text: str) -> dict:
    text = str(raw_text or "").strip()
    urls = extract_urls(text)
    appid = parse_quick_capture_appid(text)
    steam_url = steam_url_from_appid(appid)
    steamdb_url = steamdb_app_url_from_appid(appid)
    steam_slug = extract_steam_url_slug(text)
    detail = get_cached_appdetails_summary(appid, STEAM_APPDETAILS_CACHE_PATH) if appid else {}
    normalized = normalize_steam_game_data(
        appid=appid,
        search_item={
            "game_name": steam_slug,
            "steam_url": steam_url,
            "steamdb_url": steamdb_url,
        },
        appdetails=detail,
        review_stats={},
    )
    first_line = first_meaningful_capture_line(text, urls)
    game_name = first_home_card_value(
        detail.get("name") if isinstance(detail, dict) else "",
        normalized.get("game_name"),
        steam_slug,
        first_line,
        fallback="未获取",
    )
    external_links = [
        {"url": url, "platform": detect_external_platform(url)}
        for url in urls
        if not is_steam_project_url(url)
    ]
    note = build_quick_capture_note(text, urls, appid, game_name)
    parsed = {
        **normalized,
        "appid": appid,
        "game_name": game_name,
        "steam_url": steam_url,
        "steamdb_url": steamdb_url,
        "image_url": normalized.get("image_url", ""),
        "developer": normalized.get("developer", ""),
        "publisher": normalized.get("publisher", ""),
        "release_date": normalized.get("release_date", ""),
        "genres": normalized.get("genres", ""),
        "categories": normalized.get("categories", ""),
        "price": normalized.get("price", ""),
        "supports_schinese": normalized.get("supports_schinese", ""),
        "has_demo": normalized.get("has_demo", ""),
        "external_links": external_links,
        "note": note,
        "source_context": "quick_capture",
        "raw_text": text,
        "appdetails_status": detail.get("detail_fetch_status", "") if isinstance(detail, dict) else "",
    }
    return parsed


def render_quick_capture_preview(parsed: dict) -> None:
    external_links = parsed.get("external_links", [])
    platforms = sorted({link.get("platform", "") for link in external_links if link.get("platform")})
    st.markdown("**解析结果**")
    preview_rows = [
        {"字段": "AppID", "内容": parsed.get("appid") or "未获取"},
        {"字段": "游戏名", "内容": parsed.get("game_name") or "未获取"},
        {"字段": "Steam 链接", "内容": parsed.get("steam_url") or "未获取"},
        {"字段": "SteamDB 链接", "内容": parsed.get("steamdb_url") or "未获取"},
        {"字段": "识别到的外部链接数量", "内容": str(len(external_links))},
        {"字段": "平台列表", "内容": ", ".join(platforms) if platforms else "未获取"},
        {"字段": "开发商", "内容": parsed.get("developer") or "未获取"},
        {"字段": "发行商", "内容": parsed.get("publisher") or "未获取"},
        {"字段": "发售日期", "内容": parsed.get("release_date") or "未获取"},
        {"字段": "类型", "内容": parsed.get("genres") or "未获取"},
        {"字段": "备注文本", "内容": parsed.get("note") or "未获取"},
    ]
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)


def save_quick_capture_project(parsed: dict) -> None:
    if not parsed:
        st.warning("请先粘贴内容并解析。")
        return
    appid = str(parsed.get("appid", "") or "").strip()
    if appid and project_appid_exists(appid):
        st.warning("已存在同 AppID 记录，默认不重复新增。")
        return
    project = ProjectCard(
        game_name=str(parsed.get("game_name", "") or "").strip(),
        steam_url=str(parsed.get("steam_url", "") or "").strip(),
        appid=appid,
        developer=str(parsed.get("developer", "") or "").strip(),
        publisher=str(parsed.get("publisher", "") or "").strip(),
        release_status=str(parsed.get("release_date", "") or "").strip(),
        has_demo=str(parsed.get("has_demo", "") or "").strip(),
        has_simplified_chinese=str(parsed.get("supports_schinese", "") or "").strip(),
        genre_tags=str(parsed.get("genres", "") or "").strip(),
        first_impression=str(parsed.get("note", "") or "").strip(),
        next_action="生成项目画像",
    )
    if not project.game_name and not project.appid:
        st.warning("未识别到游戏名或 AppID，未保存项目记录。")
        return
    save_project_to_csv(project, CSV_PATH)
    note = DailyWatchNote(
        source="quick_capture",
        source_url=project.steam_url or str(parsed.get("steamdb_url", "") or ""),
        game_name=project.game_name,
        appid=project.appid,
        note=str(parsed.get("note", "") or ""),
        next_action="生成项目画像",
        imported_to_project="True",
    )
    save_daily_watch_note_to_csv(note, DAILY_WATCH_CSV_PATH)
    st.success(f"已保存为项目记录：{project.game_name or project.appid}")


def save_quick_capture_to_profile(parsed: dict) -> None:
    if not parsed:
        st.warning("请先粘贴内容并解析。")
        return
    data = dict(parsed)
    data["source_context"] = "quick_capture"
    metadata = set_profile_prefill_from_mapping(data, source_context="quick_capture")
    metadata["quick_capture_note"] = str(parsed.get("note", "") or "")
    metadata["note"] = str(parsed.get("note", "") or "")
    pending = st.session_state.get("pending_profile_prefill", {})
    if isinstance(pending, dict):
        pending["metadata"] = metadata
        st.session_state["pending_profile_prefill"] = pending
    st.session_state["pending_home_target"] = "profile"
    st.success("已发送到一键项目画像，请打开对应 Tab。")


def save_quick_capture_external_intel(parsed: dict) -> None:
    if not parsed:
        st.warning("请先粘贴内容并解析。")
        return
    links = parsed.get("external_links", [])
    if not links:
        st.info("未识别到外部链接。")
        return
    saved_count = 0
    note = str(parsed.get("note", "") or "").strip()
    takeaway = note[:80]
    for link in links:
        record = ExternalIntelRecord(
            appid=str(parsed.get("appid", "") or "").strip(),
            game_name=str(parsed.get("game_name", "") or "").strip(),
            platform=str(link.get("platform", "") or "其他"),
            source_url=str(link.get("url", "") or "").strip(),
            title=f"{parsed.get('game_name') or '未命名项目'} {link.get('platform') or '外部链接'}",
            evidence_type="链接",
            sentiment="未判断",
            relevance="中",
            key_takeaway=takeaway,
            note=note,
        )
        duplicate_note = find_external_intel_duplicate_note(record)
        if duplicate_note:
            st.warning(f"{record.source_url}：{duplicate_note}")
        save_external_intel_to_csv(record, EXTERNAL_INTEL_CSV_PATH)
        saved_count += 1
    st.success(f"已保存 {saved_count} 条外部情报记录。")


def extract_urls(text: str) -> list[str]:
    urls = []
    for match in re.finditer(r"https?://[^\s<>\"]+", text or ""):
        url = match.group(0).rstrip("，。,.；;)")
        if url not in urls:
            urls.append(url)
    return urls


def parse_quick_capture_appid(text: str) -> str:
    raw = str(text or "")
    steam_match = re.search(r"store\.steampowered\.com/app/(\d+)", raw, flags=re.I)
    if steam_match:
        return steam_match.group(1)
    steamdb_match = re.search(r"steamdb\.info/app/(\d+)", raw, flags=re.I)
    if steamdb_match:
        return steamdb_match.group(1)
    for line in raw.splitlines():
        clean = line.strip()
        if clean.isdigit() and 3 <= len(clean) <= 10:
            return clean
    return ""


def detect_external_platform(url: str) -> str:
    host = urlparse(url).netloc.casefold()
    if "youtube.com" in host or "youtu.be" in host:
        return "YouTube"
    if "bilibili.com" in host or "b23.tv" in host:
        return "Bilibili"
    if "x.com" in host or "twitter.com" in host:
        return "X/Twitter"
    if "bsky.app" in host:
        return "Bluesky"
    if "reddit.com" in host:
        return "Reddit"
    if "steamcommunity.com" in host:
        return "Steam社区"
    if "indienova.com" in host:
        return "Indienova"
    return "其他"


def is_steam_project_url(url: str) -> bool:
    host = urlparse(url).netloc.casefold()
    return "store.steampowered.com" in host or "steamdb.info" in host


def extract_steam_url_slug(text: str) -> str:
    match = re.search(r"store\.steampowered\.com/app/\d+/([^/?#\s]+)", text or "", flags=re.I)
    if not match:
        return ""
    return match.group(1).strip().replace("_", " ")


def first_meaningful_capture_line(text: str, urls: list[str]) -> str:
    url_set = set(urls)
    for line in str(text or "").splitlines():
        clean = line.strip()
        if not clean or clean in url_set or clean.startswith("http"):
            continue
        if clean.isdigit():
            continue
        return clean[:120]
    return ""


def build_quick_capture_note(text: str, urls: list[str], appid: str, game_name: str) -> str:
    url_set = set(urls)
    note_lines = []
    for line in str(text or "").splitlines():
        clean = line.strip()
        if not clean or clean in url_set or clean.startswith("http"):
            continue
        if appid and clean == appid:
            continue
        if game_name and clean.casefold() == str(game_name).casefold():
            continue
        note_lines.append(clean)
    return "\n".join(note_lines).strip()


def render_home_metrics(
    daily_notes: pd.DataFrame,
    active_projects: pd.DataFrame,
    pending_projects: pd.DataFrame,
    candidate_pool: pd.DataFrame,
) -> None:
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    today_count = 0
    if not daily_notes.empty and "created_at" in daily_notes.columns:
        today_count = int(daily_notes["created_at"].astype(str).str.startswith(today_prefix).sum())

    recent_7_count = 0
    if not active_projects.empty and "created_at" in active_projects.columns:
        created_at = pd.to_datetime(active_projects["created_at"], errors="coerce")
        cutoff = pd.Timestamp(datetime.now() - pd.Timedelta(days=7))
        recent_7_count = int((created_at >= cutoff).sum())

    metric_cols = st.columns(4)
    metric_cols[0].metric("今日观察数", today_count)
    metric_cols[1].metric("待处理项目数", len(pending_projects))
    metric_cols[2].metric("最近 7 天新增项目数", recent_7_count)
    metric_cols[3].metric("当前项目候选数", 0 if candidate_pool.empty else len(candidate_pool))


def render_home_candidate_pool_summary(candidate_pool: pd.DataFrame) -> None:
    summary = candidate_pool_summary(candidate_pool)
    with st.container(border=True):
        st.markdown("**今日候选工作台**")
        cols = st.columns(6)
        cols[0].metric("今日新增候选", summary["today_new"])
        cols[1].metric("待处理项目", summary["pending"])
        cols[2].metric("待试玩项目", summary["demo"])
        cols[3].metric("值得联系项目", summary["contact"])
        cols[4].metric("高优先级项目", summary["high_priority"])
        cols[5].metric("资料不足", summary.get("insufficient", 0))

        action_cols = st.columns(4)
        if action_cols[0].button("打开候选池", key="home_open_candidate_pool", use_container_width=True):
            st.session_state["pending_home_target"] = "candidate_pool"
            st.session_state["candidate_pool_stage_filter"] = "全部"
            st.session_state["candidate_pool_priority_filter"] = "全部"
            st.success("已定位到【竞品与候选 / 项目候选池】。")
        if action_cols[1].button("查看待试玩", key="home_candidate_pool_demo", use_container_width=True):
            st.session_state["pending_home_target"] = "candidate_pool"
            st.session_state["candidate_pool_stage_filter"] = "待试玩"
            st.success("候选池筛选已设为待试玩。")
        if action_cols[2].button("查看值得联系", key="home_candidate_pool_contact", use_container_width=True):
            st.session_state["pending_home_target"] = "candidate_pool"
            st.session_state["candidate_pool_stage_filter"] = "值得联系"
            st.success("候选池筛选已设为值得联系。")
        if action_cols[3].button("进入今日工作流", key="home_open_daily_workflow", use_container_width=True):
            st.session_state["active_page"] = "今日工作流"
            st.session_state["pending_home_target"] = "daily_workflow"
            st.success("已定位到【今日工作流】，请打开对应 Tab。")
        report_cols = st.columns(2)
        if report_cols[0].button("批量补全资料不足", key="home_candidate_pool_bulk_insufficient", use_container_width=True):
            st.session_state["pending_home_target"] = "candidate_pool"
            st.session_state["candidate_pool_stage_filter"] = "全部"
            st.session_state["candidate_pool_bulk_scope"] = "所有资料不足项目"
            st.success("已定位到候选池；请在“批量补全候选信息”中确认执行。")
        if report_cols[1].button("导出今日候选日报", key="home_export_daily_candidate_report", use_container_width=True):
            export_path = export_daily_candidate_report(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel", MARKET_DATA_CSV_PATH)
            st.success(f"今日候选日报已导出：{export_path}")


def render_home_feed_header(feed: HomeFeedResult) -> None:
    info_col1, info_col2, info_col3 = st.columns([1, 1, 2])
    info_col1.caption(f"最后刷新时间：{feed.refreshed_at or '未刷新'}")
    info_col2.caption("数据来源：Steam / SteamDB / 本地记录")
    if feed.message:
        if feed.used_stale_cache:
            info_col3.warning(feed.message)
        elif feed.from_cache:
            info_col3.info(feed.message)
        elif "失败" in feed.message:
            info_col3.warning(feed.message)
        else:
            info_col3.success(feed.message)


def render_home_feed_sections(feed: HomeFeedResult) -> None:
    st.markdown("### SteamDB / Steam 热点")
    section_configs = [
        ("SteamDB 热门在线", "charts", "https://steamdb.info/charts/"),
        ("Trending Followers", "trending_followers", "https://steamdb.info/stats/trendingfollowers/"),
        ("Wishlist / Upcoming", "wishlist", "https://steamdb.info/stats/wishlistactivity/"),
    ]
    columns = st.columns(3)
    for column, (title, key, fallback_url) in zip(columns, section_configs):
        with column:
            render_home_feed_section_card(title, feed.sections.get(key, []), fallback_url)


def render_home_steam_store_discovery(
    steam_feed: SteamStoreFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
) -> None:
    if steam_feed.message:
        if steam_feed.used_stale_cache or "失败" in steam_feed.message:
            st.warning(steam_feed.message)
        elif steam_feed.from_cache:
            st.info(steam_feed.message)
        else:
            st.success(steam_feed.message)
    cards = collect_steam_store_cards(steam_feed)
    cards.extend(collect_manual_observation_cards(snapshots, daily_notes))
    cards = enrich_steam_store_cards(cards, limit=20)
    filtered_cards = apply_steam_home_filters(cards)
    visible_cards = filtered_cards[:8]
    if not cards:
        visible_cards = get_home_default_entry_cards()
    elif not visible_cards:
        st.info("当前筛选无结果，建议放宽筛选。")
        return
    if st.session_state.get("home_appdetails_refresh_result"):
        st.success(st.session_state.pop("home_appdetails_refresh_result"))
    if st.session_state.get("home_review_stats_refresh_result"):
        st.success(st.session_state.pop("home_review_stats_refresh_result"))
    if steam_feed.from_cache or steam_feed.used_stale_cache:
        st.caption("当前显示缓存数据。")
    else:
        st.caption(f"Steam 图文源 fetched_at：{steam_feed.fetched_at or '未获取'}")
    with st.expander("当前卡片调试", expanded=False):
        render_current_appdetails_debug_controls(visible_cards)
    columns = st.columns(min(4, max(1, len(visible_cards))))
    for index, card in enumerate(visible_cards):
        with columns[index % len(columns)]:
            render_home_discovery_project_card(card, index)
    stats = st.session_state.get("home_appdetails_visible_stats", {})
    missing_count = stats.get("cache_missing_fields", 0)
    completed_count = stats.get("success", 0)
    st.caption(
        f"数据状态：feed cache fetched_at={steam_feed.fetched_at or '未获取'}；"
        f"来自缓存={steam_feed.from_cache or steam_feed.used_stale_cache}；"
        f"当前展示卡片={len(visible_cards)}；"
        f"appdetails 已补全={completed_count}；"
        f"appdetails 缺字段={missing_count}"
    )


def render_home_quick_steam_search() -> None:
    if st.session_state.get("home_direct_lookup_clear_requested"):
        st.session_state["home_direct_lookup_input"] = ""
        st.session_state["home_direct_lookup_result"] = {}
        st.session_state["home_direct_lookup_message"] = ""
        st.session_state["home_direct_lookup_debug"] = {}
        st.session_state["home_direct_lookup_clear_requested"] = False

    st.markdown("### Steam 直查")
    st.caption("输入 AppID、Steam 链接或 SteamDB 链接，快速生成项目卡。")
    input_col, submit_col, clear_col = st.columns([4, 1, 1])
    with input_col:
        raw_input = st.text_input(
            "AppID / Steam 链接 / SteamDB app 链接",
            key="home_direct_lookup_input",
            placeholder="2679100 或 https://store.steampowered.com/app/2679100/Witchspire/",
        )
    with submit_col:
        st.write("")
        do_lookup = st.button("查询", key="home_direct_lookup_submit", use_container_width=True)
    with clear_col:
        st.write("")
        do_clear = st.button("清空", key="home_direct_lookup_clear", use_container_width=True)

    if do_clear:
        st.session_state["home_direct_lookup_clear_requested"] = True
        st.rerun()

    if do_lookup:
        result, debug = run_home_direct_lookup(raw_input)
        st.session_state["home_direct_lookup_result"] = result
        st.session_state["home_direct_lookup_debug"] = debug
        st.session_state["home_direct_lookup_message"] = debug.get("message", "")

    message = st.session_state.get("home_direct_lookup_message", "")
    if message:
        if st.session_state.get("home_direct_lookup_debug", {}).get("direct_lookup_error"):
            st.warning(message)
        else:
            st.success(message)

    result = st.session_state.get("home_direct_lookup_result", {})
    if isinstance(result, dict) and result:
        render_home_direct_lookup_card(result)


def run_home_direct_lookup(raw_input: str) -> tuple[dict, dict]:
    clean_input = str(raw_input or "").strip()
    appid = parse_appid(clean_input)
    debug = {
        "direct_lookup_input": clean_input,
        "direct_lookup_appid": appid,
        "direct_lookup_status": "pending",
        "direct_lookup_error": "",
        "direct_lookup_appdetails_status": "",
        "message": "",
    }
    if not appid:
        debug["direct_lookup_status"] = "failed"
        debug["direct_lookup_error"] = "appid_not_found"
        debug["message"] = "未识别到 AppID，请输入 Steam AppID、Steam app 链接或 SteamDB app 链接。"
        return {}, debug

    cards = build_home_quick_appid_result_cards(appid, raw_input=clean_input)
    card = cards[0] if cards else {}
    debug["direct_lookup_status"] = "success" if card else "failed"
    debug["direct_lookup_appdetails_status"] = str(card.get("appdetails_status") or card.get("detail_fetch_status") or "")
    debug["message"] = "查询完成。" if card else "未获取到 appdetails 数据。"
    return card, debug


def render_home_direct_lookup_card(card: dict) -> None:
    with st.container(border=True):
        image_url = resolve_home_card_image(card)
        if image_url:
            st.image(image_url, use_container_width=True)
        st.markdown(f"**{card.get('game_name') or card.get('title') or '未命名项目'}**")
        st.caption(f"AppID：{card.get('appid') or '未获取'}")
        st.caption(f"开发商：{compact_card_value(card.get('developer'))}")
        st.caption(f"发行商：{compact_card_value(card.get('publisher'))}")
        st.caption(f"发售日期：{compact_card_value(card.get('release_date'))}")
        st.caption(f"类型：{compact_genres_for_direct_lookup(card.get('genres'))}")
        st.caption(f"价格：{compact_card_value(card.get('price'))}")
        st.caption(f"简中：{card.get('supports_schinese') or '未确认'} · Demo：{card.get('has_demo') or '未确认'}")
        st.caption(f"appdetails_status：{card.get('appdetails_status') or card.get('detail_fetch_status') or '未获取'}")

        link_col1, link_col2, profile_col, clear_col = st.columns(4)
        with link_col1:
            if card.get("steam_url"):
                st.link_button("打开 Steam", card["steam_url"], use_container_width=True)
        with link_col2:
            if card.get("steamdb_url"):
                st.link_button("打开 SteamDB", card["steamdb_url"], use_container_width=True)
        with profile_col:
            if st.button("发送到项目画像", key=f"home_direct_lookup_profile_{card.get('appid')}", use_container_width=True):
                send_home_direct_lookup_to_profile(card)
        with clear_col:
            if st.button("清空结果", key=f"home_direct_lookup_card_clear_{card.get('appid')}", use_container_width=True):
                st.session_state["home_direct_lookup_clear_requested"] = True
                st.rerun()


def send_home_direct_lookup_to_profile(card: dict) -> None:
    set_profile_prefill_from_mapping(card, source_context="Steam 直查")
    st.session_state["pending_home_target"] = "profile"
    st.success("已发送到【一键项目画像】，请打开对应 Tab。")


def build_home_quick_appid_result_cards(appid: str, raw_input: str = "") -> list[dict]:
    clean_appid = str(appid or "").strip()
    if not clean_appid:
        return []
    input_slug = extract_steam_input_slug(raw_input)
    base_card = {
        "card_type": "steam_store",
        "record_id": clean_appid,
        "title": input_slug or f"AppID {clean_appid}",
        "subtitle": "AppID 直查",
        "game_name": input_slug or f"AppID {clean_appid}",
        "appid": clean_appid,
        "source": "AppID 直查",
        "source_group": "Steam 直查",
        "source_filter": "appid_lookup",
        "search_source_filter": "appid_lookup",
        "source_url": steam_url_from_appid(clean_appid),
        "steam_url": steam_url_from_appid(clean_appid),
        "steamdb_url": steamdb_app_url_from_appid(clean_appid),
        "image_path": "",
        "image_url": "",
        "developer": "未获取",
        "publisher": "未获取",
        "genres": "未获取",
        "release_date": "未获取",
        "price": "未获取",
        "has_demo": "未确认",
        "supports_schinese": "未确认",
        "note": "AppID 直查",
        "next_action": "生成项目画像",
        "card_data_source": "missing",
    }
    return enrich_steam_store_cards([base_card], limit=1)


def extract_steam_input_slug(raw_input: str) -> str:
    match = re.search(r"store\.steampowered\.com/app/\d+/([^/?#]+)", str(raw_input or ""), flags=re.I)
    if not match:
        return ""
    return match.group(1).strip().replace("_", " ")


def compact_genres_for_direct_lookup(value) -> str:
    text = compact_card_value(value, max_len=80)
    if text == "未获取":
        return text
    parts = [part.strip() for part in re.split(r"[,/，、]+", text) if part.strip()]
    return " / ".join(parts[:3]) if parts else text


def render_current_appdetails_debug_controls(visible_cards: list[dict]) -> None:
    steam_cards = [card for card in visible_cards if card.get("card_type") == "steam_store" and card.get("appid")]
    if not steam_cards:
        return
    options = []
    appid_to_card = {}
    for card in steam_cards:
        appid = str(card.get("appid", "") or "").strip()
        label = f"{card.get('game_name') or card.get('title') or appid} · {appid}"
        options.append(label)
        appid_to_card[label] = card

    debug_col1, debug_col2 = st.columns([2, 1])
    with debug_col1:
        selected_label = st.selectbox("当前 AppID 调试", options, key="home_appdetails_debug_select")
    with debug_col2:
        if st.button("调试当前 AppID 详情", key="home_appdetails_debug_button", use_container_width=True):
            selected_card = appid_to_card.get(selected_label, {})
            appid = str(selected_card.get("appid", "") or "").strip()
            if appid:
                detail = debug_appdetails_summary(appid, STEAM_APPDETAILS_CACHE_PATH, APPDETAILS_DEBUG_DIR)
                st.session_state["home_appdetails_debug_result"] = detail
                st.session_state["home_appdetails_debug_file"] = str(APPDETAILS_DEBUG_DIR / f"appdetails_{appid}.json")

    detail = st.session_state.get("home_appdetails_debug_result")
    if isinstance(detail, dict) and detail.get("appid"):
        with st.expander("当前 AppID appdetails 调试结果", expanded=False):
            st.write(
                {
                    "appid": detail.get("appid"),
                    "success": detail.get("success"),
                    "name": detail.get("name"),
                    "developers": detail.get("developers"),
                    "publishers": detail.get("publishers"),
                    "genres": detail.get("genres"),
                    "categories": detail.get("categories"),
                    "release_date": detail.get("release_date"),
                    "price_overview": detail.get("price_overview"),
                    "supported_languages_contains_schinese": detail.get("supports_schinese") == "是",
                    "appdetails_status": detail.get("detail_fetch_status"),
                    "appdetails_region_used": detail.get("appdetails_region_used"),
                    "html_fallback_status": detail.get("html_fallback_status"),
                    "suspected_region_restricted": detail.get("suspected_region_restricted"),
                    "steam_data_status": detail.get("steam_data_status"),
                    "cache_status": detail.get("cache_status"),
                    "debug_file": st.session_state.get("home_appdetails_debug_file", ""),
                }
            )


def collect_steam_store_cards(steam_feed: SteamStoreFeedResult) -> list[dict]:
    cards = []
    seen = set()
    for group_name in ["即将推出", "近期上架", "热销参考"]:
        for item in steam_feed.groups.get(group_name, []):
            key = str(item.appid or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            cards.append(steam_store_item_to_card(item))
    return cards


def collect_manual_observation_cards(snapshots: pd.DataFrame, daily_notes: pd.DataFrame) -> list[dict]:
    cards = []
    seen = set()
    if not snapshots.empty:
        active_snapshots = snapshots.loc[
            ~snapshots["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})
        ].copy()
        if not active_snapshots.empty:
            active_snapshots["_created_at"] = pd.to_datetime(active_snapshots["created_at"], errors="coerce")
            active_snapshots = active_snapshots.sort_values(by="_created_at", ascending=False)
            for _, row in active_snapshots.head(8).iterrows():
                card = home_snapshot_row_to_card(row)
                card["source_group"] = "手动观察"
                card["source"] = "手动观察"
                key = home_card_key(card)
                if key and key not in seen:
                    seen.add(key)
                    cards.append(card)
    if not daily_notes.empty:
        sorted_notes = sort_records_by_created_at(daily_notes)
        for _, row in sorted_notes.head(8).iterrows():
            game_name = str(row.get("game_name", "")).strip()
            appid = str(row.get("appid", "")).strip()
            key = appid or game_name.casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            cards.append(
                {
                    "card_type": "daily_watch",
                    "record_id": str(row.get("record_id", "")).strip(),
                    "title": game_name or f"AppID {appid}",
                    "subtitle": str(row.get("next_action", "")).strip(),
                    "game_name": game_name or "未命名项目",
                    "appid": appid,
                    "source": "手动观察",
                    "source_group": "手动观察",
                    "source_url": str(row.get("source_url", "")).strip(),
                    "steamdb_url": steamdb_app_url_from_appid(appid),
                    "steam_url": steam_url_from_appid(appid),
                    "image_path": "",
                    "image_url": "",
                    "note": str(row.get("note", "")).strip(),
                    "next_action": str(row.get("next_action", "")).strip(),
                }
            )
    return cards


def enrich_steam_store_cards(cards: list[dict], limit: int = 20) -> list[dict]:
    enriched = []
    stats = {"success": 0, "failed": 0, "cache_missing_fields": 0, "cache_hit": 0, "refetched": 0}
    force_refresh = bool(st.session_state.get("force_refresh_visible_appdetails"))
    review_stats = {"success": 0, "failed": 0, "cache_hit": 0, "refetched": 0}
    force_review_refresh = bool(st.session_state.get("force_refresh_visible_review_stats"))
    for index, card in enumerate(cards):
        if index < limit and card.get("appid"):
            detail = get_cached_appdetails_summary(
                str(card.get("appid", "")),
                STEAM_APPDETAILS_CACHE_PATH,
                force_refresh=force_refresh,
            )
            if detail.get("success"):
                stats["success"] += 1
            else:
                stats["failed"] += 1
            if "cache_missing_fields" in str(detail.get("detail_fetch_status", "")) or appdetails_missing_core_fields(detail):
                stats["cache_missing_fields"] += 1
            if detail.get("cache_status") == "cache_hit":
                stats["cache_hit"] += 1
            if detail.get("cache_status") in {"fetched", "refetched", "debug_refetched"}:
                stats["refetched"] += 1
            card = merge_appdetails_into_home_card(card, detail)
            reviews = get_cached_review_stats(
                str(card.get("appid", "")),
                STEAM_REVIEW_STATS_CACHE_PATH,
                force_refresh=force_review_refresh,
            )
            if reviews.get("success"):
                review_stats["success"] += 1
            else:
                review_stats["failed"] += 1
            if reviews.get("cache_status") == "cache_hit":
                review_stats["cache_hit"] += 1
            if reviews.get("cache_status") in {"fetched", "refetched"}:
                review_stats["refetched"] += 1
            card = merge_review_stats_into_home_card(card, reviews)
            card = normalize_steam_card_source_group(card)
        enriched.append(card)
    st.session_state["home_appdetails_visible_stats"] = stats
    st.session_state["home_review_stats_visible_stats"] = review_stats
    if force_refresh:
        st.session_state["home_appdetails_refresh_result"] = (
            f"当前卡片详情刷新完成：成功 {stats['success']}，失败 {stats['failed']}，"
            f"缺字段重取 {stats['cache_missing_fields']}。"
        )
        st.session_state["force_refresh_visible_appdetails"] = False
    if force_review_refresh:
        st.session_state["home_review_stats_refresh_result"] = (
            f"当前卡片评价刷新完成：成功 {review_stats['success']}，失败 {review_stats['failed']}。"
        )
        st.session_state["force_refresh_visible_review_stats"] = False
    return enriched


def merge_appdetails_into_home_card(card: dict, detail: dict) -> dict:
    merged = dict(card)
    feed_cache_status = merged.get("feed_cache_status", "")
    normalized = normalize_steam_game_data(
        appid=str(card.get("appid", "")),
        search_item=merged,
        appdetails=detail,
        review_stats={},
    )
    merged.update(normalized)
    merged = apply_home_card_core_field_priority(merged, card, detail, normalized)
    merged["title"] = normalized.get("game_name") or merged.get("title") or merged.get("game_name")
    merged["tags"] = detail.get("tags_text") or merged.get("tags") or "未获取"
    merged["steam_page_date"] = detail.get("steam_page_date") or "未获取"
    merged["steam_page_date_status"] = detail.get("steam_page_date_status") or "后续通过 SteamDB History 或人工摘录补充"
    merged["supported_languages_summary"] = detail.get("supported_languages_summary") or "未获取"
    merged["detail_fetch_status"] = detail.get("detail_fetch_status") or "未获取"
    merged["appdetails_status"] = detail.get("detail_fetch_status") or "未获取"
    merged["cache_status"] = detail.get("cache_status") or "未获取"
    merged["appdetails_cache_status"] = detail.get("cache_status") or "未获取"
    merged["appdetails_region_used"] = detail.get("appdetails_region_used") or ""
    merged["html_fallback_status"] = detail.get("html_fallback_status") or ""
    merged["suspected_region_restricted"] = detail.get("suspected_region_restricted") or ""
    merged["steam_data_status"] = detail.get("steam_data_status") or normalized.get("data_status") or ""
    merged["feed_cache_status"] = feed_cache_status
    merged["last_detail_fetched_at"] = detail.get("checked_at") or ""
    release_raw = detail.get("release_date_raw") if isinstance(detail.get("release_date_raw"), dict) else {}
    if release_raw:
        merged["release_coming_soon"] = bool(release_raw.get("coming_soon"))
    merged["discount_percent"] = detail.get("discount_percent", "")
    if detail.get("header_image"):
        merged["image_url"] = detail["header_image"]
    merged["card_data_source"] = resolve_home_card_data_source(card, detail, normalized)
    anomalies = detect_home_card_field_merge_anomalies(merged, detail)
    if anomalies:
        merged["field_merge_anomaly"] = "字段合并异常：appdetails 有值但卡片未使用"
        merged["field_merge_anomaly_fields"] = " / ".join(anomalies)
    return merged


def apply_home_card_core_field_priority(merged: dict, original: dict, detail: dict, normalized: dict) -> dict:
    output = dict(merged)
    detail_values = {
        "game_name": detail.get("name"),
        "developer": detail.get("developer") or _join_home_card_list(detail.get("developers")),
        "publisher": detail.get("publisher") or _join_home_card_list(detail.get("publishers")),
        "release_date": detail.get("release_date"),
        "genres": detail.get("genres_text") or _join_home_card_list(detail.get("genres")),
        "categories": detail.get("categories_text") or _join_home_card_list(detail.get("categories")),
        "price": detail.get("price"),
        "supports_schinese": detail.get("supports_schinese"),
        "has_demo": detail.get("has_demo"),
        "image_url": detail.get("header_image") or detail.get("capsule_image"),
    }
    fallback_by_field = {
        "game_name": "未命名项目",
        "developer": "未获取",
        "publisher": "未获取",
        "release_date": "未获取",
        "genres": "未获取",
        "categories": "未获取",
        "price": "未获取",
        "supports_schinese": "未确认",
        "has_demo": "未确认",
        "image_url": "",
    }
    for field_name, fallback in fallback_by_field.items():
        output[field_name] = first_home_card_value(
            detail_values.get(field_name),
            normalized.get(field_name),
            original.get(field_name),
            output.get(field_name),
            fallback=fallback,
        )
    if output.get("game_name") and not is_missing_card_value(output.get("game_name")):
        output["title"] = output.get("game_name")
    return output


def first_home_card_value(*values, fallback: str = "未获取") -> str:
    for value in values:
        if isinstance(value, list):
            text = _join_home_card_list(value)
        else:
            text = str(value or "").strip()
        if not is_missing_card_value(text):
            return text
    return fallback


def _join_home_card_list(value) -> str:
    if isinstance(value, list):
        return " / ".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def resolve_home_card_data_source(card: dict, detail: dict, normalized: dict) -> str:
    if detail_has_any_core_field(detail):
        return "appdetails"
    for key in ["developer", "publisher", "genres", "release_date", "price"]:
        if not is_missing_card_value(normalized.get(key)):
            return "search_item"
    if card.get("card_type") == "steam_store":
        return "feed_cache"
    return "missing"


def detail_has_any_core_field(detail: dict) -> bool:
    return any(
        not is_missing_card_value(value)
        for value in [
            detail.get("developer"),
            detail.get("publisher"),
            detail.get("genres_text"),
            detail.get("release_date"),
            detail.get("price"),
        ]
    )


def appdetails_missing_core_fields(detail: dict) -> bool:
    if not detail.get("success"):
        return False
    return all(
        is_missing_card_value(value)
        for value in [
            detail.get("developer"),
            detail.get("publisher"),
            detail.get("genres_text"),
        ]
    )


def detect_home_card_field_merge_anomalies(card: dict, detail: dict) -> list[str]:
    checks = [
        ("developer", detail.get("developer")),
        ("publisher", detail.get("publisher")),
        ("genres", detail.get("genres_text")),
    ]
    anomalies = []
    if not detail.get("success"):
        return anomalies
    for card_key, detail_value in checks:
        if not is_missing_card_value(detail_value) and is_missing_card_value(card.get(card_key)):
            anomalies.append(card_key)
    return anomalies


def is_missing_card_value(value) -> bool:
    text = str(value or "").strip()
    return not text or text in {"未获取", "未确认", "[]", "None", "nan"}


def merge_review_stats_into_home_card(card: dict, reviews: dict) -> dict:
    merged = dict(card)
    normalized = normalize_steam_game_data(
        appid=str(card.get("appid", "")),
        search_item=merged,
        appdetails={},
        review_stats=reviews,
    )
    for key in [
        "review_total",
        "review_positive",
        "review_negative",
        "positive_rate",
        "review_score_desc",
        "sample_review_count",
        "median_playtime_hours",
        "avg_playtime_hours",
        "median_playtime_at_review_hours",
        "avg_playtime_at_review_hours",
        "review_stats_status",
    ]:
        merged[key] = normalized.get(key)
    merged["review_cache_status"] = reviews.get("cache_status", "")
    return merged


def normalize_steam_card_source_group(card: dict) -> dict:
    normalized = dict(card)
    group = str(normalized.get("source_group", "") or "")
    game_name = str(normalized.get("game_name", "") or normalized.get("title", "") or "")
    release_date = parse_steam_release_date(normalized.get("release_date", ""))
    today = datetime.now().date()

    if group in {"Steam 新品趋势", "Steam 即将推出", "Steam 热销趋势", "Steam 折扣热点", "热销 / 热门趋势", "新品趋势"}:
        group = {
            "Steam 新品趋势": "近期上架",
            "Steam 即将推出": "即将推出",
            "Steam 热销趋势": "热销参考",
            "Steam 折扣热点": "热销参考",
            "热销 / 热门趋势": "热销参考",
            "新品趋势": "近期上架",
        }[group]

    if group == "手动观察":
        normalized["source_group"] = group
        normalized["source"] = group
        return normalized

    if group in {"即将推出", "近期上架"} and is_known_old_major(game_name):
        group = "热销参考"
    elif bool(normalized.get("release_coming_soon")) and group != "热销参考":
        group = "即将推出"
    elif release_date:
        age_days = (today - release_date).days
        if release_date > today:
            if group != "热销参考":
                group = "即将推出"
        elif group == "即将推出":
            group = "近期上架" if 0 <= age_days <= 90 else "热销参考"
        elif group == "近期上架" and age_days > 90:
            group = "热销参考"
    elif group == "近期上架":
        group = "热销参考"

    normalized["source_group"] = group
    normalized["source"] = group
    return normalized


def parse_steam_release_date(value) -> object:
    text = str(value or "").strip()
    if not text or text == "未获取":
        return None
    match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3))).date()
        except ValueError:
            return None
    iso_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if iso_match:
        try:
            return datetime(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))).date()
        except ValueError:
            return None
    return None


def is_known_old_major(game_name: str) -> bool:
    lowered = str(game_name or "").casefold()
    old_names = [
        "counter-strike 2",
        "apex legends",
        "dota 2",
        "pubg",
        "grand theft auto v",
        "gta v",
        "rust",
        "wallpaper engine",
        "street fighter 6",
        "resident evil 4",
    ]
    return any(name in lowered for name in old_names)


def is_early_access_or_upcoming(card: dict) -> bool:
    text = " ".join(
        str(card.get(key, "") or "")
        for key in ["game_name", "title", "genres", "categories", "release_date", "source_group", "note"]
    ).casefold()
    return any(marker in text for marker in ["抢先体验", "early access", "即将推出", "coming soon", "upcoming"])


def is_old_released_game(card: dict, max_age_days: int = 180) -> bool:
    if is_early_access_or_upcoming(card):
        return False
    release_date = parse_steam_release_date(card.get("release_date", ""))
    if not release_date:
        return False
    return (datetime.now().date() - release_date).days > max_age_days


def apply_steam_home_filters(cards: list[dict]) -> list[dict]:
    if not cards:
        return []
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    group_counts = {}
    for card in cards:
        group = str(card.get("source_group", "") or "").strip()
        if group:
            group_counts[group] = group_counts.get(group, 0) + 1
    group_label_map = {
        "即将推出": "即将推出",
        "近期上架": "近期上架",
        "热销参考": "热销参考",
        "手动观察": "手动观察",
    }
    source_options = [("全部", "")]
    for group_name, short_label in group_label_map.items():
        count = group_counts.get(group_name, 0)
        if count > 0:
            source_options.append((f"{short_label}（{count}）", group_name))
    option_labels = [label for label, _ in source_options]
    with col1:
        selected_state = st.session_state.get("home_steam_source_filter_v063")
        if selected_state not in option_labels:
            st.session_state["home_steam_source_filter_v063"] = option_labels[0]
        source_label = st.selectbox(
            "显示来源",
            option_labels,
            key="home_steam_source_filter_v063",
        )
    with col2:
        hide_big = st.checkbox("隐藏老游戏 / 已发行大作", value=True, key="home_steam_hide_big")
    with col3:
        only_upcoming = st.checkbox("只看即将推出", value=False, key="home_steam_only_upcoming")
    with col4:
        only_demo = st.checkbox("只看有 Demo", value=False, key="home_steam_only_demo")
    with col5:
        only_schinese = st.checkbox("只看支持简中", value=False, key="home_steam_only_schinese")
    with col6:
        show_ignored = st.checkbox("显示已忽略/已放弃", value=False, key="home_show_ignored_candidates")

    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6 = st.columns(6)
    with filter_col1:
        positive_filter = st.selectbox("好评率", ["任意", "90%+", "80%+", "75%+", "65%+", "50%以下"], key="home_positive_filter_v060")
    with filter_col2:
        review_count_filter = st.selectbox("评测数", ["任意", "10+", "50+", "100+", "500+"], key="home_review_count_filter_v060")
    with filter_col3:
        playtime_filter = st.selectbox("游玩时间中位数", ["任意", "低于 1h", "1-3h", "3-10h", "10h+"], key="home_playtime_filter_v060")
    with filter_col4:
        discount_filter = st.selectbox("当前折扣", ["任意", "50%+", "75%+", "90%+"], key="home_discount_filter_v060")
    with filter_col5:
        price_filter = st.selectbox("价格", ["任意", "低于 ¥3", "低于 ¥10", "低于 ¥40", "高于 ¥40"], key="home_price_filter_v060")
    with filter_col6:
        strict_fields = st.checkbox("严格筛选已获取字段", value=False, key="home_strict_filter_v060")

    filtered = cards
    selected_group = next((group for label, group in source_options if label == source_label), "")
    if selected_group == "热销参考":
        st.caption("热销参考不代表发行机会，只用于观察趋势。")
    if selected_group:
        filtered = [card for card in filtered if card.get("source_group") == selected_group]
    selected_group_name = selected_group or "全部"
    if only_upcoming:
        filtered = [card for card in filtered if card.get("source_group") == "即将推出"]
        selected_group_name = "即将推出"
    raw_partition_count = len(filtered)
    old_filtered_count = 0
    if hide_big:
        before_old_filter = len(filtered)
        filtered = [
            card
            for card in filtered
            if not is_known_old_major(card.get("game_name", "") or card.get("title", ""))
            and not is_old_released_game(card)
        ]
        old_filtered_count = before_old_filter - len(filtered)
    if only_demo:
        filtered = [card for card in filtered if str(card.get("has_demo", "")).strip() == "是"]
    if only_schinese:
        filtered = [card for card in filtered if str(card.get("supports_schinese", "")).strip() == "是"]
    if not show_ignored:
        hidden_appids = ignored_candidate_appids_for_home()
        if hidden_appids:
            filtered = [card for card in filtered if str(card.get("appid", "") or "").strip() not in hidden_appids]
    filtered = apply_review_dimension_filters(
        filtered,
        positive_filter=positive_filter,
        review_count_filter=review_count_filter,
        playtime_filter=playtime_filter,
        discount_filter=discount_filter,
        price_filter=price_filter,
        strict_fields=strict_fields,
    )
    st.session_state["home_steam_filter_debug"] = {
        "current_group": selected_group_name,
        "source_counts": group_counts,
        "raw_partition_count": raw_partition_count,
        "old_game_filtered_count": old_filtered_count,
        "final_count": len(filtered),
    }
    return filtered


def ignored_candidate_appids_for_home() -> set[str]:
    pool = load_candidate_pool(CANDIDATE_POOL_CSV_PATH)
    if pool.empty:
        return set()
    hidden = pool.loc[
        pool["stage"].astype(str).isin({"放弃"})
        | pool["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})
    ]
    return set(hidden["appid"].astype(str).str.strip()) - {""}


def apply_review_dimension_filters(
    cards: list[dict],
    *,
    positive_filter: str,
    review_count_filter: str,
    playtime_filter: str,
    discount_filter: str,
    price_filter: str,
    strict_fields: bool,
) -> list[dict]:
    filtered = []
    for card in cards:
        if not _card_matches_positive_filter(card, positive_filter, strict_fields):
            continue
        if not _card_matches_review_count_filter(card, review_count_filter, strict_fields):
            continue
        if not _card_matches_playtime_filter(card, playtime_filter, strict_fields):
            continue
        if not _card_matches_discount_filter(card, discount_filter, strict_fields):
            continue
        if not _card_matches_price_filter(card, price_filter, strict_fields):
            continue
        filtered.append(card)
    return filtered


def _keep_missing(value, strict_fields: bool) -> bool:
    return (value is None or value == "") and not strict_fields


def _card_matches_positive_filter(card: dict, selected: str, strict_fields: bool) -> bool:
    if selected == "任意":
        return True
    value = card.get("positive_rate")
    if _keep_missing(value, strict_fields):
        return True
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return not strict_fields
    if rate > 1:
        rate /= 100
    thresholds = {"90%+": 0.9, "80%+": 0.8, "75%+": 0.75, "65%+": 0.65}
    if selected == "50%以下":
        return rate < 0.5
    return rate >= thresholds.get(selected, 0)


def _card_matches_review_count_filter(card: dict, selected: str, strict_fields: bool) -> bool:
    if selected == "任意":
        return True
    raw = card.get("review_total")
    if _keep_missing(raw, strict_fields):
        return True
    try:
        total = int(float(raw or 0))
    except (TypeError, ValueError):
        return not strict_fields
    return total >= int(selected.replace("+", ""))


def _card_matches_playtime_filter(card: dict, selected: str, strict_fields: bool) -> bool:
    if selected == "任意":
        return True
    raw = card.get("median_playtime_hours")
    if _keep_missing(raw, strict_fields):
        return True
    try:
        hours = float(raw)
    except (TypeError, ValueError):
        return not strict_fields
    if selected == "低于 1h":
        return hours < 1
    if selected == "1-3h":
        return 1 <= hours < 3
    if selected == "3-10h":
        return 3 <= hours < 10
    if selected == "10h+":
        return hours >= 10
    return True


def _card_matches_discount_filter(card: dict, selected: str, strict_fields: bool) -> bool:
    if selected == "任意":
        return True
    discount = parse_discount_percent(card)
    if _keep_missing(discount, strict_fields):
        return True
    if discount is None:
        return not strict_fields
    return discount >= int(selected.replace("%+", ""))


def _card_matches_price_filter(card: dict, selected: str, strict_fields: bool) -> bool:
    if selected == "任意":
        return True
    price = parse_price_cny(card.get("price"))
    if _keep_missing(price, strict_fields):
        return True
    if price is None:
        return not strict_fields
    if selected == "低于 ¥3":
        return price < 3
    if selected == "低于 ¥10":
        return price < 10
    if selected == "低于 ¥40":
        return price < 40
    if selected == "高于 ¥40":
        return price > 40
    return True


def steam_search_url_for_group(group_name: str) -> str:
    filter_map = {
        "近期上架": "popularnew",
        "即将推出": "popularcomingsoon",
        "热销参考": "topsellers",
    }
    search_filter = filter_map.get(group_name, "popularnew")
    return f"https://store.steampowered.com/search/?filter={search_filter}&category1=998"


def render_home_common_entry_expander() -> None:
    with st.expander("Steam / SteamDB 常用入口", expanded=False):
        st.markdown("**Steam**")
        steam_links = [
            ("即将推出", steam_search_url_for_group("即将推出")),
            ("近期上架", steam_search_url_for_group("近期上架")),
            ("热销参考", steam_search_url_for_group("热销参考")),
            ("News Hub", "https://store.steampowered.com/news/"),
            ("Specials", "https://store.steampowered.com/specials"),
        ]
        render_link_button_grid(steam_links, "home_steam_compact")
        st.markdown("**SteamDB**")
        steamdb_links = [
            ("Top Rated Releases", f"https://steamdb.info/stats/gameratings/{datetime.now().year}/"),
            ("Trending Followers", "https://steamdb.info/stats/trendingfollowers/"),
            ("Wishlist Activity", "https://steamdb.info/stats/wishlistactivity/"),
            ("Most Wishlisted", "https://steamdb.info/stats/mostwished/"),
            ("Upcoming", "https://steamdb.info/upcoming/"),
            ("Calendar", "https://steamdb.info/calendar/"),
        ]
        render_link_button_grid(steamdb_links, "home_steamdb_compact")


def render_home_common_tools_grid() -> None:
    st.markdown("### 常用工具")
    tools = [
        ("SteamDB", "https://steamdb.info/", "external"),
        ("Steam 折扣", "https://store.steampowered.com/specials", "external"),
        ("Top Rated", f"https://steamdb.info/stats/gameratings/{datetime.now().year}/", "external"),
        ("Wishlist", "https://steamdb.info/stats/wishlistactivity/", "external"),
        ("Followers", "https://steamdb.info/stats/trendingfollowers/", "external"),
        ("Calendar", "https://steamdb.info/calendar/", "external"),
        ("B站搜索", "https://search.bilibili.com/all?keyword=Steam%20indie%20game", "external"),
        ("小黑盒搜索", "https://api.xiaoheihe.cn/maxnews/app/search?keyword=Steam", "external"),
        ("项目画像", "profile", "internal"),
        ("搜索中心", "search", "internal"),
    ]
    columns = st.columns(5)
    for index, (label, target, kind) in enumerate(tools):
        with columns[index % 5]:
            if kind == "external":
                st.link_button(label, target, use_container_width=True)
            elif st.button(label, key=f"home_common_tool_{label}", use_container_width=True):
                st.session_state["pending_home_target"] = target
                st.rerun()


def render_home_primary_entry_cards() -> None:
    st.markdown("### SteamDB 入口卡")
    links = [
        ("Top Rated Releases", f"https://steamdb.info/stats/gameratings/{datetime.now().year}/", "年度高评分新作"),
        ("Trending Followers", "https://steamdb.info/stats/trendingfollowers/", "关注增长趋势"),
        ("Wishlist Activity", "https://steamdb.info/stats/wishlistactivity/", "愿望单活动"),
        ("Most Wishlisted", "https://steamdb.info/stats/mostwished/", "愿望单总量"),
        ("Upcoming", "https://steamdb.info/upcoming/", "即将推出"),
        ("Calendar", "https://steamdb.info/calendar/", "发售日历"),
    ]
    columns = st.columns(3)
    for index, (label, url, note) in enumerate(links):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(note)
                st.link_button("打开入口", url, use_container_width=True)


def render_home_feed_section_card(title: str, items: list[HomeFeedItem], fallback_url: str) -> None:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        if not items:
            st.caption("暂无缓存项目，入口可直接打开。")
            st.link_button("打开入口", fallback_url, use_container_width=True)
            return
        for item in items[:3]:
            st.caption(f"{item.game_name or '未命名项目'} · {(item.metric or item.release_or_wishlist or '指标待确认')[:70]}")
        st.link_button("打开入口", fallback_url, use_container_width=True)


def render_home_discovery_projects(
    feed: HomeFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
    steamdb_notes: pd.DataFrame,
) -> None:
    st.markdown("### 首页快照卡片")
    items = collect_home_discovery_items(feed, snapshots, daily_notes, steamdb_notes)
    if not items:
        st.caption("暂无首页快照或今日观察，先使用上方 Steam 图文源。")
        return

    if feed.from_cache or feed.used_stale_cache:
        st.caption("当前显示缓存数据。")

    visible_items = items[:5]
    columns = st.columns(min(5, max(1, len(visible_items))))
    for index, item in enumerate(visible_items):
        with columns[index % len(columns)]:
            render_home_discovery_project_card(item, index)


def collect_home_discovery_items(
    feed: HomeFeedResult,
    snapshots: pd.DataFrame,
    daily_notes: pd.DataFrame,
    steamdb_notes: pd.DataFrame,
) -> list[dict]:
    items = []
    seen = set()

    if not snapshots.empty:
        active_snapshots = snapshots.loc[
            ~snapshots["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})
        ].copy()
        if not active_snapshots.empty:
            active_snapshots["_priority"] = pd.to_numeric(active_snapshots["priority"], errors="coerce").fillna(0)
            active_snapshots["_created_at"] = pd.to_datetime(active_snapshots["created_at"], errors="coerce")
            active_snapshots = active_snapshots.sort_values(
                by=["_priority", "_created_at"],
                ascending=[False, False],
            )
            for _, row in active_snapshots.head(12).iterrows():
                card = home_snapshot_row_to_card(row)
                key = home_card_key(card)
                if key and key not in seen:
                    seen.add(key)
                    items.append(card)
                if len(items) >= 12:
                    break

    if not daily_notes.empty:
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        today_notes = daily_notes.loc[daily_notes["created_at"].astype(str).str.startswith(today_prefix)].copy()
        today_notes = sort_records_by_created_at(today_notes)
        for _, row in today_notes.head(10).iterrows():
            game_name = str(row.get("game_name", "")).strip()
            appid = str(row.get("appid", "")).strip()
            key = appid or game_name.casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            items.append({
                "card_type": "daily_watch",
                "record_id": str(row.get("record_id", "")).strip(),
                "title": game_name or f"AppID {appid}",
                "subtitle": str(row.get("next_action", "")).strip(),
                "game_name": game_name or "未命名项目",
                "appid": appid,
                "source": str(row.get("source", "")).strip() or "今日观察",
                "source_url": str(row.get("source_url", "")).strip(),
                "steamdb_url": steamdb_app_url_from_appid(appid),
                "steam_url": steam_url_from_appid(appid),
                "image_path": "",
                "image_url": "",
                "note": str(row.get("note", "")).strip(),
                "next_action": str(row.get("next_action", "")).strip(),
            })
            if len(items) >= 12:
                break

    if not steamdb_notes.empty:
        for _, row in steamdb_notes.tail(10).iloc[::-1].iterrows():
            game_name = str(row.get("game_name", "")).strip()
            appid = str(row.get("appid", "")).strip()
            key = appid or game_name.casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            metric = " / ".join(
                part
                for part in [
                    str(row.get("rank_text", "")).strip(),
                    str(row.get("release_date", "")).strip(),
                    str(row.get("rating", "")).strip(),
                    str(row.get("followers", "")).strip(),
                ]
                if part
            )
            items.append({
                "card_type": "steamdb_watch",
                "record_id": str(row.get("record_id", "")).strip(),
                "title": game_name or f"AppID {appid}",
                "subtitle": metric,
                "game_name": game_name or f"AppID {appid}",
                "appid": appid,
                "source": str(row.get("source_page", "")).strip() or "SteamDB观察",
                "source_url": str(row.get("source_url", "")).strip(),
                "steamdb_url": str(row.get("steamdb_url", "")).strip() or steamdb_app_url_from_appid(appid),
                "steam_url": str(row.get("steam_url", "")).strip() or steam_url_from_appid(appid),
                "image_path": "",
                "image_url": "",
                "note": str(row.get("note", "")).strip(),
                "next_action": str(row.get("next_action", "")).strip(),
            })
            if len(items) >= 12:
                break

    for section_items in feed.sections.values():
        for item in section_items:
            key = item.appid or item.game_name.casefold()
            if key and key not in seen:
                seen.add(key)
                items.append(home_feed_item_to_card(item))
            if len(items) >= 12:
                break
        if len(items) >= 12:
            break
    return items


def render_home_discovery_project_card(item: dict, index: int, key_scope: str = "home_discovery") -> None:
    with st.container(border=True):
        image_url = resolve_home_card_image(item)
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.markdown("#### Steam / SteamDB")
            st.caption(item.get("subtitle") or "入口卡")
        title = item.get("title") or item.get("game_name") or "未命名项目"
        st.markdown(f"**{title}**")
        game_name = item.get("game_name", "")
        if game_name and game_name != title:
            st.caption(game_name)
        st.caption(f"{item.get('source_group') or item.get('source') or '信息流'} · AppID：{item.get('appid') or '未获取'}")
        if item.get("card_type") == "steam_store":
            review_total = int(float(item.get("review_total") or 0))
            if review_total <= 0:
                st.markdown("**暂无评测**")
            elif review_total < 10:
                st.markdown(f"**样本不足** · {review_total:,} 篇")
            else:
                st.markdown(f"**好评率：{format_positive_rate(item.get('positive_rate'))} / {review_total:,} 篇**")
            st.caption(f"评测：{item.get('review_score_desc') or item.get('review_stats_status') or '评价未获取'}")
            st.caption(
                "游玩：评测样本中位 "
                f"{format_hours(item.get('median_playtime_hours'))} / 平均 {format_hours(item.get('avg_playtime_hours'))}"
            )
            st.caption(f"简中：{item.get('supports_schinese') or '未确认'} · Demo：{item.get('has_demo') or '未确认'}")
            st.caption(f"开发：{compact_card_value(item.get('developer'))}")
            st.caption(f"发行：{compact_card_value(item.get('publisher'))}")
            st.caption(f"发售：{compact_card_value(item.get('release_date'))}")
            st.caption(f"类型：{compact_card_value(item.get('genres'), max_len=34)}")
            st.caption(f"价格：{compact_card_value(item.get('price'))}")
            with st.expander("详情", expanded=False):
                st.write(f"标签：{compact_card_value(item.get('tags'), max_len=220)}")
                st.write(f"评价摘要：{compact_card_value(item.get('review_summary') or item.get('review_score_desc'), max_len=220)}")
                st.write(
                    "Steam 评测样本："
                    f"正评 {format_review_total(item.get('review_positive'))} / "
                    f"差评 {format_review_total(item.get('review_negative'))} / "
                    f"样本 {format_review_total(item.get('sample_review_count'))}"
                )
                st.write(f"评价缓存状态：{item.get('review_cache_status') or item.get('review_stats_status') or '评价未获取'}")
                st.write(f"语言：{compact_card_value(item.get('supported_languages_summary'), max_len=220)}")
                st.write(f"Steam 上架日期 / 页面创建日期：{item.get('steam_page_date') or '未获取'}")
                st.caption(item.get("steam_page_date_status") or "后续通过 SteamDB History 或人工摘录补充")
                st.write(f"source_group：{item.get('source_group') or '未获取'}")
                st.write(f"search_source_filter：{item.get('source_filter') or item.get('search_source_filter') or '未获取'}")
                st.write(f"appdetails_status：{item.get('appdetails_status') or item.get('detail_fetch_status') or '未获取'}")
                st.write(f"cache_status：{item.get('cache_status') or '未获取'}")
                st.write(f"card_data_source：{item.get('card_data_source') or 'missing'}")
                st.write(f"last_detail_fetched_at：{item.get('last_detail_fetched_at') or '未获取'}")
                st.write(f"feed_fetched_at：{item.get('feed_fetched_at') or '未获取'}")
                st.write(f"raw_release_date：{item.get('raw_release_date') or '未获取'}")
                if item.get("field_merge_anomaly"):
                    st.error(item.get("field_merge_anomaly"))
                    st.caption(f"异常字段：{item.get('field_merge_anomaly_fields') or '未记录'}")
        else:
            detail_parts = [
                item.get("price", ""),
                item.get("release_date", ""),
                item.get("review_summary", ""),
            ]
            detail_text = " / ".join(str(part).strip() for part in detail_parts if str(part or "").strip())
            st.write((detail_text or item.get("note") or item.get("next_action") or item.get("subtitle") or "下一步：打开来源页人工筛选")[:120])
        if item.get("appid") and item.get("card_type") != "steam_store":
            st.caption(f"AppID：{item.get('appid')}")

        source_link = item.get("source_url") or item.get("steamdb_url") or item.get("steam_url")
        link_col1, link_col2, link_col3 = st.columns(3)
        with link_col1:
            if source_link:
                st.link_button("打开来源", source_link, use_container_width=True)
        with link_col2:
            if item.get("steam_url"):
                st.link_button("打开 Steam", item["steam_url"], use_container_width=True)
        with link_col3:
            if item.get("steamdb_url"):
                st.link_button("打开 SteamDB", item["steamdb_url"], use_container_width=True)

        action_cols = st.columns(6)
        with action_cols[0]:
            if st.button("加入观察", key=f"{key_scope}_watch_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                add_home_card_to_daily_watch(item)
        with action_cols[1]:
            if st.button("加入候选池", key=f"{key_scope}_candidate_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                add_home_card_to_candidate_pool(item)
        with action_cols[2]:
            if st.button("忽略", key=f"{key_scope}_ignore_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                ignore_home_card_candidate(item)
                st.rerun()
        with action_cols[3]:
            if st.button("标记放弃", key=f"{key_scope}_reject_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                reject_home_card_candidate(item)
                st.rerun()
        with action_cols[4]:
            if st.button("发送到项目画像", key=f"{key_scope}_profile_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                send_home_card_to_profile(item)
        with action_cols[5]:
            if st.button("搜索中心", key=f"{key_scope}_search_{item.get('card_type')}_{item.get('record_id')}_{index}", use_container_width=True):
                send_home_card_to_search_center(item)
        if item.get("card_type") == "snapshot":
            if st.button("归档快照", key=f"{key_scope}_archive_{item.get('record_id')}_{index}", use_container_width=True):
                update_home_snapshot_fields(HOME_SNAPSHOT_CSV_PATH, item.get("record_id", ""), {"is_archived": "True"})
                st.rerun()


def compact_card_value(value, max_len: int = 48) -> str:
    text = str(value or "").strip()
    if not text:
        return "未获取"
    if text in {"[]", "None", "nan"}:
        return "未获取"
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def format_positive_rate(value) -> str:
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return "暂无"
    if rate <= 1:
        rate *= 100
    return f"{rate:.0f}%"


def format_review_total(value) -> str:
    try:
        total = int(float(value or 0))
    except (TypeError, ValueError):
        total = 0
    return f"{total:,}" if total > 0 else "暂无"


def format_hours(value) -> str:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return "暂无"
    return f"{hours:.1f}h"


def parse_price_cny(value) -> float | None:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return None
    if "免费" in text or "Free" in text:
        return 0.0
    match = re.search(r"¥\s*([0-9]+(?:\.[0-9]+)?)", text)
    if match:
        return float(match.group(1))
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    return float(match.group(1)) if match else None


def parse_discount_percent(card: dict) -> int | None:
    for key in ["discount_percent", "discount"]:
        raw = str(card.get(key, "") or "").strip().replace("%", "")
        if raw.lstrip("-").isdigit():
            return abs(int(raw))
    text = " ".join(str(card.get(key, "") or "") for key in ["price", "note", "review_summary"])
    match = re.search(r"-\s*(\d{1,2})%", text)
    return int(match.group(1)) if match else None


def resolve_home_card_image(item: dict) -> str:
    image_path = str(item.get("image_path", "") or "").strip()
    if image_path and Path(image_path).exists():
        return image_path
    image_url = str(item.get("image_url", "") or "").strip()
    appid = str(item.get("appid", "") or "").strip()
    if image_url and "capsule_sm_120" not in image_url:
        return image_url
    if not appid:
        return image_url
    try:
        image_data = get_cached_steam_image(appid, STEAM_IMAGE_CACHE_PATH)
    except Exception:
        return image_url
    return str(image_data.get("header_image") or image_data.get("capsule_image") or image_url or "").strip()


def get_home_default_entry_cards() -> list[dict]:
    current_year = datetime.now().year
    return [
        build_entry_card(f"Top Rated Releases {current_year}", f"https://steamdb.info/stats/gameratings/{current_year}/", "从年度高评分新作里筛选可发行项目"),
        build_entry_card("Trending Followers", "https://steamdb.info/stats/trendingfollowers/", "查看近期关注增长异常的新项目"),
        build_entry_card("Wishlist Activity", "https://steamdb.info/stats/wishlistactivity/", "查看愿望单活动和即将发售机会"),
        build_entry_card("Upcoming / Calendar", "https://steamdb.info/upcoming/", "查看即将推出项目和发售日历"),
    ]


def build_entry_card(title: str, url: str, note: str) -> dict:
    return {
        "card_type": "entry",
        "record_id": re.sub(r"\W+", "_", title.casefold()),
        "title": title,
        "subtitle": "入口卡",
        "game_name": title,
        "appid": "",
        "source": "SteamDB入口",
        "source_url": url,
        "steam_url": "",
        "steamdb_url": url,
        "image_path": "",
        "image_url": "",
        "note": note,
        "next_action": "打开入口人工筛选",
    }


def home_card_key(card: dict) -> str:
    appid = str(card.get("appid", "") or "").strip()
    name = str(card.get("game_name", "") or card.get("title", "") or "").strip().casefold()
    return appid or name


def home_snapshot_row_to_card(row: pd.Series) -> dict:
    return {
        "card_type": "snapshot",
        "record_id": str(row.get("record_id", "")).strip(),
        "title": str(row.get("title", "")).strip() or str(row.get("game_name", "")).strip() or "未命名快照",
        "subtitle": str(row.get("subtitle", "")).strip(),
        "game_name": str(row.get("game_name", "")).strip(),
        "appid": str(row.get("appid", "")).strip(),
        "source": str(row.get("source", "")).strip() or "首页快照",
        "source_url": str(row.get("source_url", "")).strip(),
        "steam_url": str(row.get("steam_url", "")).strip(),
        "steamdb_url": str(row.get("steamdb_url", "")).strip(),
        "image_path": str(row.get("image_path", "")).strip(),
        "image_url": str(row.get("image_url", "")).strip(),
        "note": str(row.get("note", "")).strip(),
        "next_action": str(row.get("next_action", "")).strip(),
    }


def home_feed_item_to_card(item: HomeFeedItem) -> dict:
    return {
        "card_type": "feed",
        "record_id": item.appid or item.game_name,
        "title": item.game_name or f"AppID {item.appid}",
        "subtitle": item.metric or item.release_or_wishlist,
        "game_name": item.game_name,
        "appid": item.appid,
        "source": item.source,
        "source_url": item.source_url,
        "steam_url": item.steam_url,
        "steamdb_url": item.steamdb_url,
        "image_path": "",
        "image_url": "",
        "note": item.note or item.metric,
        "next_action": "生成项目画像",
    }


def steam_store_item_to_card(item: SteamStoreFeedItem) -> dict:
    detail_parts = [
        item.price,
        item.release_date,
        item.review_summary,
    ]
    note = " / ".join(part for part in detail_parts if str(part or "").strip())
    return {
        "card_type": "steam_store",
        "record_id": item.appid,
        "title": item.game_name or f"AppID {item.appid}",
        "subtitle": item.source_group,
        "game_name": item.game_name,
        "appid": item.appid,
        "source": item.source_group,
        "source_group": item.source_group,
        "source_filter": item.source_filter,
        "search_source_filter": item.source_filter,
        "feed_fetched_at": item.fetched_at,
        "feed_cache_status": "feed_cache",
        "source_url": item.steam_url,
        "steam_url": item.steam_url,
        "steamdb_url": steamdb_app_url_from_appid(item.appid),
        "image_path": "",
        "image_url": item.image_url,
        "price": item.price,
        "release_date": item.release_date,
        "raw_release_date": item.release_date,
        "review_summary": item.review_summary,
        "has_demo": item.has_demo,
        "supports_schinese": item.has_simplified_chinese or "未确认",
        "developer": "未获取",
        "publisher": "未获取",
        "genres": "未获取",
        "tags": "未获取",
        "steam_page_date": "未获取",
        "steam_page_date_status": "后续通过 SteamDB History 或人工摘录补充",
        "supported_languages_summary": "未获取",
        "detail_fetch_status": "未获取",
        "appdetails_status": "未获取",
        "cache_status": "未获取",
        "card_data_source": "feed_cache",
        "note": note,
        "next_action": "生成项目画像",
    }


def add_home_card_to_daily_watch(card: dict) -> None:
    note = DailyWatchNote(
        source=str(card.get("source", "") or "首页快照"),
        source_url=str(card.get("source_url", "") or card.get("steamdb_url", "") or card.get("steam_url", "")),
        game_name=str(card.get("game_name", "") or card.get("title", "")),
        appid=str(card.get("appid", "")),
        note=str(card.get("note", "") or card.get("subtitle", "")),
        next_action=str(card.get("next_action", "") or "生成项目画像"),
        imported_to_project="False",
    )
    if not note.game_name and not note.appid:
        st.warning("缺少游戏名和 AppID，无法加入今日观察。")
        return
    save_daily_watch_note_to_csv(note, DAILY_WATCH_CSV_PATH)
    st.success(f"已加入今日观察：{note.game_name or note.appid}")


def add_home_card_to_candidate_pool(card: dict) -> None:
    save_mapping_to_candidate_pool(
        card,
        source=str(card.get("source_group", "") or card.get("source", "") or "今日新游雷达"),
        stage="新发现",
        success_prefix="已加入项目候选池",
    )


def ignore_home_card_candidate(card: dict) -> None:
    data = dict(card)
    data["is_archived"] = "True"
    data["next_action"] = data.get("next_action") or "已忽略，默认不再显示"
    save_mapping_to_candidate_pool(
        data,
        source=str(card.get("source_group", "") or card.get("source", "") or "今日新游雷达"),
        stage="暂缓",
        success_prefix="已忽略候选",
        force_status_updates=True,
    )


def reject_home_card_candidate(card: dict) -> None:
    data = dict(card)
    data["reject_reason"] = data.get("reject_reason") or "今日新游雷达人工标记放弃"
    data["next_action"] = data.get("next_action") or "放弃"
    save_mapping_to_candidate_pool(
        data,
        source=str(card.get("source_group", "") or card.get("source", "") or "今日新游雷达"),
        stage="放弃",
        success_prefix="已标记放弃",
        force_status_updates=True,
    )


def send_home_card_to_profile(card: dict) -> None:
    normalized = normalize_steam_game_data(
        appid=str(card.get("appid", "")),
        search_item=card,
        appdetails={},
        review_stats=card,
    )
    row = pd.Series(
        {
            "game_name": str(normalized.get("game_name") or card.get("game_name", "") or card.get("title", "")),
            "appid": str(normalized.get("appid") or card.get("appid", "")),
            "source_url": str(card.get("source_url", "") or card.get("steamdb_url", "")),
            "steam_url": str(normalized.get("steam_url") or card.get("steam_url", "")),
            "steamdb_url": str(card.get("steamdb_url", "")),
            "image_url": str(normalized.get("image_url") or card.get("image_url", "")),
            "note": str(card.get("note", "") or card.get("subtitle", "")),
            "developer": str(normalized.get("developer", "")),
            "publisher": str(normalized.get("publisher", "")),
            "genres": str(normalized.get("genres", "")),
            "categories": str(normalized.get("categories", "") or card.get("categories", "")),
            "release_date": str(normalized.get("release_date", "")),
            "price": str(normalized.get("price", "")),
            "supports_schinese": str(normalized.get("supports_schinese", "")),
            "has_demo": str(normalized.get("has_demo", "")),
            "review_total": str(normalized.get("review_total", "")),
            "review_positive": str(normalized.get("review_positive", "")),
            "review_negative": str(normalized.get("review_negative", "")),
            "positive_rate": str(normalized.get("positive_rate", "")),
            "review_score_desc": str(normalized.get("review_score_desc", "")),
            "median_playtime_hours": str(normalized.get("median_playtime_hours", "")),
            "avg_playtime_hours": str(normalized.get("avg_playtime_hours", "")),
            "review_stats_status": str(normalized.get("review_stats_status", "")),
            "source_group": str(card.get("source_group", "")),
            "source_context": str(card.get("source_group", "") or card.get("source", "") or "首页卡片"),
        }
    )
    send_daily_watch_to_profile(row)


def send_home_card_to_search_center(card: dict) -> None:
    normalized = normalize_steam_game_data(
        appid=str(card.get("appid", "")),
        search_item=card,
        appdetails={},
        review_stats=card,
    )
    row = pd.Series(
        {
            "game_name": str(normalized.get("game_name") or card.get("game_name", "") or card.get("title", "")),
            "appid": str(normalized.get("appid") or card.get("appid", "")),
            "source": str(card.get("source", "")),
            "source_url": str(card.get("source_url", "") or normalized.get("steam_url", "") or card.get("steamdb_url", "")),
            "note": str(card.get("note", "") or card.get("subtitle", "")),
            "developer": str(normalized.get("developer", "")),
            "publisher": str(normalized.get("publisher", "")),
            "genres": str(normalized.get("genres", "")),
            "tags": str(card.get("tags", "")),
            "release_date": str(normalized.get("release_date", "")),
            "source_group": str(card.get("source_group", "")),
        }
    )
    send_daily_watch_to_search_center(row)


def render_home_snapshot_form() -> None:
    st.markdown("### 首页快照")
    with st.expander("添加首页快照", expanded=False):
        with st.form("home_snapshot_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                source = st.selectbox("来源", get_home_snapshot_source_options(), key="snapshot_source")
                game_name = st.text_input("游戏名", key="snapshot_game_name")
                appid_input = st.text_input("AppID", key="snapshot_appid")
                source_url = st.text_input("来源链接", key="snapshot_source_url")
            with col2:
                steam_url = st.text_input("Steam 链接", key="snapshot_steam_url")
                steamdb_url = st.text_input("SteamDB 链接", key="snapshot_steamdb_url")
                image_url = st.text_input("图片 URL（可选）", key="snapshot_image_url")
                uploaded_image = st.file_uploader(
                    "上传图片（可选）",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="snapshot_uploaded_image",
                )
            with col3:
                title = st.text_input("标题", key="snapshot_title")
                subtitle = st.text_input("副标题", key="snapshot_subtitle")
                next_action = st.selectbox(
                    "下一步动作",
                    ["生成项目画像", "搜索中心", "加入候选", "试玩Demo", "联系开发者", "暂缓", "放弃"],
                    key="snapshot_next_action",
                )
                priority = st.number_input("优先级", min_value=-100, max_value=100, value=0, step=1, key="snapshot_priority")
                pinned = st.checkbox("置顶（priority +10）", value=False, key="snapshot_pinned")
            note = st.text_area("观察备注", height=88, key="snapshot_note")
            save_only, save_profile, save_search = st.columns(3)
            save_snapshot = save_only.form_submit_button("保存快照")
            save_and_profile = save_profile.form_submit_button("保存并发送到项目画像")
            save_and_search = save_search.form_submit_button("保存并发送到搜索中心")

    if save_snapshot or save_and_profile or save_and_search:
        resolved_appid = parse_steamdb_appid(appid_input) or parse_steamdb_appid(source_url) or parse_steamdb_appid(steam_url) or parse_steamdb_appid(steamdb_url)
        resolved_steam_url = steam_url.strip() or steam_url_from_appid(resolved_appid)
        resolved_steamdb_url = steamdb_url.strip() or steamdb_app_url_from_appid(resolved_appid)
        local_image_path = save_home_snapshot_upload(uploaded_image, resolved_appid, game_name)
        final_priority = int(priority) + (10 if pinned else 0)
        snapshot = HomeSnapshot(
            source=source,
            source_url=source_url.strip() or resolved_steamdb_url or resolved_steam_url,
            game_name=game_name.strip(),
            appid=resolved_appid,
            steam_url=resolved_steam_url,
            steamdb_url=resolved_steamdb_url,
            image_path=local_image_path,
            image_url=image_url.strip(),
            title=title.strip() or game_name.strip() or (f"AppID {resolved_appid}" if resolved_appid else ""),
            subtitle=subtitle.strip(),
            note=note.strip(),
            next_action=next_action,
            priority=str(final_priority),
            is_archived="False",
        )
        if not snapshot.title and not snapshot.source_url and not snapshot.image_path and not snapshot.image_url:
            st.error("请至少填写标题、游戏名、来源链接或上传图片。")
            return
        save_home_snapshot_to_csv(snapshot, HOME_SNAPSHOT_CSV_PATH)
        card = home_snapshot_row_to_card(pd.Series({
            "record_id": snapshot.record_id,
            "title": snapshot.title,
            "subtitle": snapshot.subtitle,
            "game_name": snapshot.game_name,
            "appid": snapshot.appid,
            "source": snapshot.source,
            "source_url": snapshot.source_url,
            "steam_url": snapshot.steam_url,
            "steamdb_url": snapshot.steamdb_url,
            "image_path": snapshot.image_path,
            "image_url": snapshot.image_url,
            "note": snapshot.note,
            "next_action": snapshot.next_action,
        }))
        if save_and_profile:
            send_home_card_to_profile(card)
        elif save_and_search:
            send_home_card_to_search_center(card)
        else:
            st.success("已保存首页快照。")


def get_home_snapshot_source_options() -> list[str]:
    return [
        "Steam首页",
        "SteamDB榜单",
        "Top Rated",
        "Trending Followers",
        "Wishlist Activity",
        "Most Wishlisted",
        "Upcoming",
        "Calendar",
        "B站",
        "YouTube",
        "小黑盒",
        "其他",
    ]


def save_home_snapshot_upload(uploaded_image, appid: str, game_name: str) -> str:
    if uploaded_image is None:
        return ""
    HOME_SNAPSHOT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    original_name = str(getattr(uploaded_image, "name", "") or "snapshot.png")
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
    stem_parts = [
        datetime.now().strftime("%Y%m%d_%H%M%S"),
        str(appid or "").strip(),
        re.sub(r"[^A-Za-z0-9_-]+", "_", str(game_name or "snapshot").strip())[:40],
    ]
    filename = "_".join(part for part in stem_parts if part) + suffix
    target_path = HOME_SNAPSHOT_IMAGE_DIR / filename
    target_path.write_bytes(uploaded_image.getbuffer())
    return str(target_path)


def render_home_steam_news_summary(feed: HomeFeedResult) -> None:
    st.markdown("### Steam 新闻与活动")
    link_cols = st.columns(4)
    for index, (label, url) in enumerate(get_steam_news_links()):
        with link_cols[index]:
            st.link_button(label, url, use_container_width=True)

    if not feed.news:
        return
    news_cols = st.columns(3)
    for index, news in enumerate(feed.news[:3]):
        with news_cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{news.title[:80]}**")
                if news.url:
                    st.link_button("打开新闻", news.url, use_container_width=True)


def add_feed_item_to_daily_watch(item: HomeFeedItem) -> None:
    note = DailyWatchNote(
        source=item.source or "首页信息流",
        source_url=item.steamdb_url or item.source_url,
        game_name=item.game_name,
        appid=item.appid,
        note=item.metric or item.note,
        next_action="生成项目画像",
        imported_to_project="False",
    )
    if not note.game_name and not note.appid:
        st.warning("缺少游戏名和 AppID，无法加入今日观察。")
        return
    save_daily_watch_note_to_csv(note, DAILY_WATCH_CSV_PATH)
    st.success(f"已加入今日观察：{note.game_name or note.appid}")


def send_feed_item_to_profile(item: HomeFeedItem) -> None:
    row = pd.Series(
        {
            "game_name": item.game_name,
            "appid": item.appid,
            "source_url": item.steam_url or item.source_url or item.steamdb_url,
            "steam_url": item.steam_url,
            "note": item.metric or item.note,
        }
    )
    send_daily_watch_to_profile(row)


def send_feed_item_to_search_center(item: HomeFeedItem) -> None:
    row = pd.Series(
        {
            "game_name": item.game_name,
            "appid": item.appid,
            "source": item.source,
            "source_url": item.steamdb_url or item.source_url,
            "note": item.metric or item.note,
        }
    )
    send_daily_watch_to_search_center(row)


def add_feed_item_to_candidate_pool(item: HomeFeedItem) -> None:
    if feed_item_candidate_exists(item):
        st.info("该项目已在候选池中，不重复写入。")
        return
    candidate = CompetitorCandidate(
        target_game_name="首页信息流",
        target_appid="",
        candidate_name=item.game_name,
        candidate_steam_url=item.steam_url,
        candidate_appid=item.appid,
        source_keyword=item.source or "首页信息流",
        source_type="首页信息流",
        match_reason="首页榜单或趋势信息流出现，适合作为候选观察。",
        user_decision="待确认",
        notes=item.metric or item.note,
    )
    save_candidate_to_csv(candidate, CANDIDATE_CSV_PATH)
    st.success(f"已加入候选池：{item.game_name or item.appid}")


def feed_item_candidate_exists(item: HomeFeedItem) -> bool:
    candidates = load_candidates(CANDIDATE_CSV_PATH)
    if candidates.empty:
        return False
    appid = str(item.appid or "").strip()
    name = str(item.game_name or "").strip().casefold()
    if appid and "candidate_appid" in candidates.columns:
        return bool(candidates["candidate_appid"].astype(str).str.strip().eq(appid).any())
    if name and "candidate_name" in candidates.columns:
        return bool(candidates["candidate_name"].astype(str).str.strip().str.casefold().eq(name).any())
    return False


def render_home_quick_actions() -> None:
    st.markdown("### 快速操作")
    action_rows = [
        ("新建项目画像", "profile"),
        ("打开 SteamDB 发现", "steamdb"),
        ("打开搜索中心", "search"),
        ("打开候选池", "candidate_pool"),
        ("打开历史项目记录", "history"),
        ("打开今日观察记录", "daily_watch"),
    ]
    for index, (label, target) in enumerate(action_rows):
        if st.button(label, use_container_width=True, key=f"home_quick_action_{index}"):
            st.session_state["pending_home_target"] = target
            st.rerun()

    if st.button("导出 Excel", use_container_width=True, key="home_export_excel"):
        excel_path = export_projects_to_excel(
            CSV_PATH,
            EXCEL_REPORT_PATH,
            COMPETITOR_CSV_PATH,
            CANDIDATE_CSV_PATH,
            STEAMDB_WATCH_NOTE_CSV_PATH,
            STEAMDB_TEMPLATE_CSV_PATH,
            DAILY_WATCH_CSV_PATH,
            HOME_SNAPSHOT_CSV_PATH,
            STEAM_HOME_FEED_CACHE_PATH,
            STEAM_APPDETAILS_CACHE_PATH,
            STEAM_REVIEW_STATS_CACHE_PATH,
            EXTERNAL_INTEL_CSV_PATH,
        )
        st.success(f"Excel 已导出：{excel_path}")

    with st.expander("SteamDB / Steam 常用入口", expanded=False):
        render_home_steamdb_links()
        render_home_steam_news_links()


def render_home_steamdb_links() -> None:
    st.markdown("### SteamDB 发现入口")
    templates = load_templates(STEAMDB_TEMPLATE_CSV_PATH)
    favorite_templates = pd.DataFrame()
    if not templates.empty and "is_favorite" in templates.columns:
        favorite_templates = templates.loc[
            templates["is_favorite"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})
        ].copy()

    if not favorite_templates.empty:
        st.markdown("**收藏模板**")
        favorite_links = [
            (
                str(row.get("template_name", "")).strip() or "SteamDB 模板",
                str(row.get("steamdb_url", "")).strip(),
            )
            for _, row in favorite_templates.head(6).iterrows()
            if str(row.get("steamdb_url", "")).strip()
        ]
        render_link_button_grid(favorite_links, "home_steamdb_favorites")

    groups = get_steamdb_common_link_groups()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**新作发现**")
        render_link_button_grid(
            [
                ("Top Rated Releases 2026", "https://steamdb.info/stats/gameratings/2026/"),
                ("Top Rated Releases 2027", "https://steamdb.info/stats/gameratings/2027/"),
                ("Upcoming Releases", "https://steamdb.info/upcoming/"),
                ("Release Calendar", "https://steamdb.info/calendar/"),
            ],
            "home_steamdb_discovery",
        )
    with col2:
        st.markdown("**热度观察**")
        render_link_button_grid(groups["热度观察"], "home_steamdb_heat")


def render_home_steam_news_links() -> None:
    st.markdown("### Steam / 新闻 / 活动入口")
    render_link_button_grid(get_steam_news_links(), "home_steam_news")


def render_home_recent_projects(active_projects: pd.DataFrame) -> None:
    st.markdown("### 最近项目与待办")
    recent_projects = sort_records_by_created_at(active_projects).head(10)
    display_columns = [
        "created_at",
        "game_name",
        "appid",
        "release_status",
        "has_demo",
        "next_action",
        "demo_conclusion",
        "is_deleted",
    ]
    if recent_projects.empty:
        st.info("暂无最近项目。")
        return

    compact = build_home_project_display(recent_projects.head(5), display_columns)
    st.dataframe(compact, use_container_width=True, hide_index=True)

    with st.expander("查看完整最近项目", expanded=False):
        st.dataframe(build_home_project_display(recent_projects, display_columns), use_container_width=True, hide_index=True)


def render_home_pending_projects(pending_projects: pd.DataFrame) -> None:
    st.markdown("### 待处理项目")
    display_columns = [
        "created_at",
        "game_name",
        "appid",
        "release_status",
        "has_demo",
        "next_action",
        "demo_conclusion",
        "is_deleted",
    ]
    if pending_projects.empty:
        st.info("暂无待处理项目。")
        return
    pending_projects = sort_records_by_created_at(pending_projects)

    st.dataframe(
        build_home_project_display(pending_projects.head(5), display_columns),
        use_container_width=True,
        hide_index=True,
    )
    with st.expander("查看完整待处理项目", expanded=False):
        st.dataframe(
            build_home_project_display(pending_projects.head(10), display_columns),
            use_container_width=True,
            hide_index=True,
        )


def build_home_project_display(projects: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    existing_columns = [column for column in columns if column in projects.columns]
    display = projects.loc[:, existing_columns].copy()
    return display.rename(
        columns={
            "created_at": "创建时间",
            "game_name": "游戏名",
            "appid": "AppID",
            "release_status": "发售状态",
            "has_demo": "是否有 Demo",
            "next_action": "下一步动作",
            "demo_conclusion": "Demo 结论",
            "is_deleted": "是否已删除",
        }
    )


def filter_pending_projects(projects: pd.DataFrame) -> pd.DataFrame:
    if projects.empty or "next_action" not in projects.columns:
        return pd.DataFrame(columns=projects.columns)
    keywords = ["先试玩 Demo", "先查竞品", "联系开发者", "暂缓观察", "生成项目画像", "待补充"]
    pattern = "|".join(re.escape(keyword) for keyword in keywords)
    return projects.loc[projects["next_action"].astype(str).str.contains(pattern, case=False, na=False)].copy()


def render_home_daily_watch_form() -> None:
    st.markdown("### 今日观察记录")
    with st.expander("手动添加今日观察", expanded=False):
        with st.form("daily_watch_form"):
            col1, col2 = st.columns(2)
            with col1:
                source = st.selectbox(
                    "来源",
                    [
                        "Steam首页",
                        "SteamDB首页",
                        "Top Rated",
                        "Charts",
                        "Trending Followers",
                        "Wishlist Activity",
                        "Most Wishlisted",
                        "Upcoming",
                        "Calendar",
                        "B站",
                        "YouTube",
                        "小黑盒",
                        "其他",
                    ],
                )
                game_name = st.text_input("游戏名", key="daily_watch_game_name")
                appid = st.text_input("AppID", key="daily_watch_appid")
            with col2:
                source_url = st.text_input("来源链接", key="daily_watch_source_url")
                next_action = st.selectbox(
                    "下一步动作",
                    ["生成项目画像", "加入候选", "试玩Demo", "查竞品", "联系开发者", "暂缓", "放弃"],
                )
                note = st.text_area("观察备注", height=88, key="daily_watch_note")

            save_only, save_profile, save_search = st.columns(3)
            save_note = save_only.form_submit_button("保存今日观察")
            save_and_profile = save_profile.form_submit_button("保存并发送到项目画像")
            save_and_search = save_search.form_submit_button("保存并发送到搜索中心")

    if save_note or save_and_profile or save_and_search:
        resolved_appid = parse_steamdb_appid(appid) or parse_steamdb_appid(source_url)
        note_record = DailyWatchNote(
            source=source,
            source_url=source_url.strip(),
            game_name=game_name.strip(),
            appid=resolved_appid,
            note=note.strip(),
            next_action=next_action,
            imported_to_project="False",
        )
        if not note_record.game_name and not note_record.appid:
            st.error("请至少填写游戏名或 AppID。")
            return
        save_daily_watch_note_to_csv(note_record, DAILY_WATCH_CSV_PATH)
        row = pd.Series(
            {
                "source": note_record.source,
                "source_url": note_record.source_url,
                "game_name": note_record.game_name,
                "appid": note_record.appid,
                "note": note_record.note,
                "next_action": note_record.next_action,
            }
        )
        if save_and_profile:
            send_daily_watch_to_profile(row)
        elif save_and_search:
            send_daily_watch_to_search_center(row)
        else:
            st.success("已保存今日观察。")


def render_home_snapshot_manager(snapshots: pd.DataFrame) -> None:
    with st.expander("管理首页快照", expanded=False):
        st.caption("首页快照：某一时刻首页发现流或人工入口保存下来的项目快照，不等同于今日观察历史。")
        if st.button("刷新首页快照列表", key="snapshot_manager_refresh"):
            st.session_state["snapshot_manager_last_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        if st.session_state.get("snapshot_manager_last_loaded_at"):
            st.caption(f"快照列表最后读取时间：{st.session_state['snapshot_manager_last_loaded_at']}")
        current_snapshots = load_home_snapshots(HOME_SNAPSHOT_CSV_PATH)
        if current_snapshots.empty:
            st.info("暂无首页快照。")
            return

        show_archived = st.checkbox("显示已归档快照", value=False, key="snapshot_manager_show_archived")
        sources = sorted(
            source
            for source in current_snapshots["source"].astype(str).str.strip().unique().tolist()
            if source
        )
        source_filter = st.selectbox("按来源筛选", ["全部"] + sources, key="snapshot_manager_source")
        keyword = st.text_input("按游戏名搜索", key="snapshot_manager_keyword")

        filtered = current_snapshots.copy()
        if not show_archived:
            filtered = filtered.loc[
                ~filtered["is_archived"].astype(str).str.casefold().isin({"true", "1", "yes", "y"})
            ].copy()
        if source_filter != "全部":
            filtered = filtered.loc[filtered["source"].astype(str).str.strip() == source_filter].copy()
        if keyword.strip():
            pattern = re.escape(keyword.strip())
            filtered = filtered.loc[
                filtered["game_name"].astype(str).str.contains(pattern, case=False, na=False)
                | filtered["title"].astype(str).str.contains(pattern, case=False, na=False)
            ].copy()

        if filtered.empty:
            st.info("没有符合筛选条件的快照。")
            return

        display = filtered.tail(50).iloc[::-1].rename(
            columns={
                "created_at": "创建时间",
                "source": "来源",
                "game_name": "游戏名",
                "appid": "AppID",
                "title": "标题",
                "subtitle": "副标题",
                "next_action": "下一步动作",
                "priority": "优先级",
                "is_archived": "已归档",
            }
        )
        st.dataframe(
            display.loc[:, ["创建时间", "来源", "游戏名", "AppID", "标题", "副标题", "下一步动作", "优先级", "已归档"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("**快照操作**")
        for index, row in filtered.tail(20).iloc[::-1].iterrows():
            record_id = str(row.get("record_id", "")).strip()
            label = str(row.get("title", "")).strip() or str(row.get("game_name", "")).strip() or record_id
            archived = str(row.get("is_archived", "")).casefold() in {"true", "1", "yes", "y"}
            current_priority = pd.to_numeric(row.get("priority", "0"), errors="coerce")
            if pd.isna(current_priority):
                current_priority = 0
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.caption(f"{label} · {row.get('source', '')} · priority {row.get('priority', '0')}")
            with cols[1]:
                new_priority = st.number_input(
                    "priority",
                    min_value=-100,
                    max_value=100,
                    value=int(current_priority),
                    step=1,
                    key=f"snapshot_priority_edit_{record_id}_{index}",
                    label_visibility="collapsed",
                )
            with cols[2]:
                if st.button("更新", key=f"snapshot_priority_update_{record_id}_{index}", use_container_width=True):
                    update_home_snapshot_fields(HOME_SNAPSHOT_CSV_PATH, record_id, {"priority": str(new_priority)})
                    st.rerun()
            with cols[3]:
                action_label = "恢复" if archived else "归档"
                if st.button(action_label, key=f"snapshot_archive_toggle_{record_id}_{index}", use_container_width=True):
                    update_home_snapshot_fields(
                        HOME_SNAPSHOT_CSV_PATH,
                        record_id,
                        {"is_archived": "False" if archived else "True"},
                    )
                    st.rerun()


def render_home_daily_watch_history(daily_notes: pd.DataFrame) -> None:
    with st.expander("查看今日观察历史", expanded=False):
        st.caption("今日观察历史：用户手动观察过的项目记录；默认按创建时间倒序显示最近 10 条。")
        col_refresh, col_clear = st.columns([1, 2])
        with col_refresh:
            if st.button("刷新今日观察历史", key="daily_watch_history_refresh", use_container_width=True):
                st.session_state["daily_watch_last_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
        with col_clear:
            confirm_clear = st.checkbox("我确认清空今日观察历史", key="daily_watch_clear_confirm")
            if st.button("清空今日观察历史", key="daily_watch_clear_button", use_container_width=True):
                if not confirm_clear:
                    st.warning("请先勾选二次确认。")
                else:
                    pd.DataFrame(columns=DAILY_WATCH_COLUMNS).to_csv(DAILY_WATCH_CSV_PATH, index=False, encoding="utf-8-sig")
                    st.session_state["daily_watch_last_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("今日观察历史已清空。")
                    st.rerun()

        current_notes = sort_records_by_created_at(load_daily_watch_notes(DAILY_WATCH_CSV_PATH))
        last_loaded_at = st.session_state.get("daily_watch_last_loaded_at") or st.session_state.get("home_last_loaded_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"今日观察历史最后读取时间：{last_loaded_at}")
        if current_notes.empty:
            st.info("暂无今日观察记录。")
            return
        newest_created_at = str(current_notes.iloc[0].get("created_at", "") or "未记录").strip()
        st.caption(f"最新记录时间：{newest_created_at}")
        show_more = st.checkbox("显示最近 30 条", value=False, key="daily_watch_history_show_more")
        visible_notes = current_notes.head(30 if show_more else 10)
        display = visible_notes.rename(
            columns={
                "created_at": "创建时间",
                "source": "来源",
                "source_url": "来源链接",
                "game_name": "游戏名",
                "appid": "AppID",
                "note": "观察备注",
                "next_action": "下一步动作",
                "imported_to_project": "已导入项目",
            }
        )
        st.dataframe(display, use_container_width=True, hide_index=True)


def sort_records_by_created_at(records: pd.DataFrame) -> pd.DataFrame:
    if records.empty or "created_at" not in records.columns:
        return records.copy()
    sorted_records = records.copy()
    sorted_records["_created_at_sort"] = pd.to_datetime(sorted_records["created_at"], errors="coerce")
    sorted_records = sorted_records.sort_values(by="_created_at_sort", ascending=False, na_position="last")
    return sorted_records.drop(columns=["_created_at_sort"])


def render_home_data_health_check(steam_feed: SteamStoreFeedResult) -> None:
    with st.expander("数据健康检查", expanded=False):
        daily_notes = load_daily_watch_notes(DAILY_WATCH_CSV_PATH)
        snapshots = load_home_snapshots(HOME_SNAPSHOT_CSV_PATH)
        external_records = load_external_intel(EXTERNAL_INTEL_CSV_PATH)
        company_records = load_company_dossiers(COMPANY_DOSSIER_CSV_PATH)
        market_records = load_market_data(MARKET_DATA_CSV_PATH)
        search_history = load_search_history(SEARCH_HISTORY_CSV_PATH)
        latest_search = search_history.iloc[0].to_dict() if not search_history.empty else {}
        profile_prefill = st.session_state.get("profile_prefill_metadata", {})
        if not isinstance(profile_prefill, dict):
            profile_prefill = {}
        direct_debug = st.session_state.get("home_direct_lookup_debug", {})
        if not isinstance(direct_debug, dict):
            direct_debug = {}
        debug_detail = st.session_state.get("home_appdetails_debug_result", {})
        if not isinstance(debug_detail, dict):
            debug_detail = {}
        current_appid = (
            str(profile_prefill.get("appid", "") or "").strip()
            or str(direct_debug.get("direct_lookup_appid", "") or "").strip()
            or str(debug_detail.get("appid", "") or "").strip()
        )
        current_game_name = (
            str(profile_prefill.get("game_name", "") or "").strip()
            or str(debug_detail.get("name", "") or "").strip()
        )
        developer_names_count = len(parse_company_names(profile_prefill.get("developer") or debug_detail.get("developer")))
        publisher_names_count = len(parse_company_names(profile_prefill.get("publisher") or debug_detail.get("publisher")))
        current_company_records = filter_company_dossiers_for_project(company_records, appid=current_appid, game_name=current_game_name)
        current_company = latest_company_dossier(current_company_records)
        current_market_records = filter_market_data(market_records, appid=current_appid, game_name=current_game_name)
        market_sources = [
            source
            for source in current_market_records["source"].astype(str).str.strip().drop_duplicates().tolist()
            if source
        ] if not current_market_records.empty else []
        visible_stats = st.session_state.get("home_appdetails_visible_stats", {})
        if not isinstance(visible_stats, dict):
            visible_stats = {}
        health_rows = [
            {"字段": "quick_capture_last_parsed_at", "状态": st.session_state.get("quick_capture_last_parsed_at") or "暂无数据"},
            {"字段": "quick_capture_links_count", "状态": st.session_state.get("quick_capture_links_count", 0)},
            {"字段": "quick_capture_appid", "状态": st.session_state.get("quick_capture_appid") or "暂无数据"},
            {"字段": "search_history_count", "状态": len(search_history)},
            {"字段": "search_history_last_updated", "状态": latest_search.get("updated_at") or "暂无数据"},
            {"字段": "latest_search_game", "状态": latest_search.get("game_name") or "暂无数据"},
            {"字段": "project_history_count", "状态": len(load_projects(CSV_PATH, include_deleted=True))},
            {"字段": "当前 appid", "状态": current_appid or "暂无数据"},
            {"字段": "当前 game_name", "状态": current_game_name or "暂无数据"},
            {"字段": "首页缓存文件路径", "状态": str(STEAM_HOME_FEED_CACHE_PATH)},
            {"字段": "今日观察记录数量", "状态": len(daily_notes)},
            {"字段": "首页快照数量", "状态": len(snapshots)},
            {"字段": "外部情报记录数量", "状态": len(external_records)},
            {"字段": "company_dossier_count", "状态": len(company_records)},
            {"字段": "current_company_name", "状态": current_company.get("company_name") or "暂无数据"},
            {"字段": "current_company_confidence", "状态": current_company.get("confidence") or "暂无数据"},
            {"字段": "company_dossier_last_updated", "状态": current_company.get("updated_at") or "暂无数据"},
            {"字段": "developer_names_count", "状态": developer_names_count},
            {"字段": "publisher_names_count", "状态": publisher_names_count},
            {"字段": "selected_company_name", "状态": st.session_state.get("company_dossier_selected_company_name") or "暂无数据"},
            {"字段": "selected_company_role", "状态": st.session_state.get("company_dossier_selected_company_role") or "暂无数据"},
            {"字段": "market_data_count", "状态": len(market_records)},
            {"字段": "market_data_sources", "状态": " / ".join(market_sources) if market_sources else "暂无数据"},
            {"字段": "latest_market_data_date", "状态": latest_market_data_date(current_market_records) or "暂无数据"},
            {"字段": "market_data_last_error", "状态": st.session_state.get("market_data_last_error") or "暂无数据"},
            {"字段": "browser_open_mode", "状态": "streamlit_headless + launcher_open_once"},
            {"字段": "market_data_manual_mode", "状态": True},
            {"字段": "gamalytic_link_mode", "状态": "homepage"},
            {"字段": "vgi_link_mode", "状态": "homepage"},
            {"字段": "appdetails_status", "状态": debug_detail.get("detail_fetch_status") or direct_debug.get("direct_lookup_appdetails_status") or "暂无数据"},
            {"字段": "appdetails_region_used", "状态": debug_detail.get("appdetails_region_used") or "暂无数据"},
            {"字段": "html_fallback_status", "状态": debug_detail.get("html_fallback_status") or "暂无数据"},
            {"字段": "suspected_region_restricted", "状态": debug_detail.get("suspected_region_restricted") or "暂无数据"},
            {"字段": "latest_search_result_status", "状态": latest_search.get("last_result_status") or direct_debug.get("message") or "暂无数据"},
            {"字段": "card_data_source", "状态": profile_prefill.get("source_context") or direct_debug.get("direct_lookup_status") or "暂无数据"},
            {"字段": "last_loaded_at", "状态": st.session_state.get("home_last_loaded_at") or "暂无数据"},
            {"字段": "last_error", "状态": "; ".join(steam_feed.errors[:3]) if steam_feed.errors else (steam_feed.message if (steam_feed.used_stale_cache or "失败" in str(steam_feed.message)) else "暂无")},
        ]
        st.dataframe(pd.DataFrame(health_rows), use_container_width=True, hide_index=True)
        st.caption(
            "appdetails 当前卡片："
            f"成功 {visible_stats.get('success', 0)} / "
            f"失败 {visible_stats.get('failed', 0)} / "
            f"缺字段 {visible_stats.get('cache_missing_fields', 0)}"
        )


def render_home_debug_expander(feed: HomeFeedResult, steam_feed: SteamStoreFeedResult) -> None:
    with st.expander("详细调试 JSON", expanded=False):
        snapshots = load_home_snapshots(HOME_SNAPSHOT_CSV_PATH)
        steam_group_counts = {key: len(value) for key, value in steam_feed.groups.items()}
        appdetails_cache = load_cached_appdetails_summaries(STEAM_APPDETAILS_CACHE_PATH)
        appdetails_success_count = sum(1 for detail in appdetails_cache.values() if detail.get("success"))
        appdetails_failure_count = sum(1 for detail in appdetails_cache.values() if not detail.get("success"))
        appdetails_cache_hit_count = sum(1 for detail in appdetails_cache.values() if detail.get("cache_status") == "cache_hit")
        appdetails_missing_fields_count = count_missing_field_cache_entries(STEAM_APPDETAILS_CACHE_PATH)
        visible_appdetails_stats = st.session_state.get("home_appdetails_visible_stats", {})
        visible_review_stats = st.session_state.get("home_review_stats_visible_stats", {})
        filter_debug = st.session_state.get("home_steam_filter_debug", {})
        search_debug = st.session_state.get("home_quick_search_debug", {})
        direct_lookup_debug = st.session_state.get("home_direct_lookup_debug", {})
        st.caption(f"自动信息流缓存：{HOME_FEED_CACHE_PATH}")
        st.caption(f"Steam 图文源缓存：{STEAM_HOME_FEED_CACHE_PATH}")
        st.caption(f"Steam appdetails 详情缓存：{STEAM_APPDETAILS_CACHE_PATH}")
        st.caption(f"Steam 评价摘要缓存：{STEAM_REVIEW_STATS_CACHE_PATH}")
        st.caption(f"Steam 图片缓存：{STEAM_IMAGE_CACHE_PATH}")
        st.caption(f"首页快照 CSV：{HOME_SNAPSHOT_CSV_PATH}")
        st.caption(f"首页快照图片目录：{HOME_SNAPSHOT_IMAGE_DIR}")
        st.write(
            {
                "steam_home_feed_success": steam_feed.success,
                "steam_home_feed_fetched_at": steam_feed.fetched_at,
                "steam_home_feed_from_cache": steam_feed.from_cache,
                "steam_home_feed_used_stale_cache": steam_feed.used_stale_cache,
                "steam_home_feed_message": steam_feed.message,
                "steam_home_feed_group_counts": steam_group_counts,
                "steam_home_feed_errors": steam_feed.errors[:6],
                "search_query": search_debug.get("search_query", ""),
                "search_status_filter": search_debug.get("search_status_filter", ""),
                "search_cache_hit": search_debug.get("search_cache_hit", False),
                "search_result_count": search_debug.get("search_result_count", 0),
                "search_error": search_debug.get("search_error", ""),
                "direct_lookup_input": direct_lookup_debug.get("direct_lookup_input", ""),
                "direct_lookup_appid": direct_lookup_debug.get("direct_lookup_appid", ""),
                "direct_lookup_status": direct_lookup_debug.get("direct_lookup_status", ""),
                "direct_lookup_error": direct_lookup_debug.get("direct_lookup_error", ""),
                "direct_lookup_appdetails_status": direct_lookup_debug.get("direct_lookup_appdetails_status", ""),
                "appdetails_success_count": appdetails_success_count,
                "appdetails_failure_count": appdetails_failure_count,
                "appdetails_cache_entries": len(appdetails_cache),
                "appdetails_cache_hit_count": appdetails_cache_hit_count,
                "cache_missing_fields_count": appdetails_missing_fields_count,
                "current_group": filter_debug.get("current_group", ""),
                "current_group_raw_count": filter_debug.get("raw_partition_count", 0),
                "old_game_filtered_count": filter_debug.get("old_game_filtered_count", 0),
                "current_group_final_count": filter_debug.get("final_count", 0),
                "visible_appdetails_success_count": visible_appdetails_stats.get("success", 0),
                "visible_review_stats_success_count": visible_review_stats.get("success", 0),
                "visible_review_stats_failed_count": visible_review_stats.get("failed", 0),
                "visible_review_stats_cache_hit_count": visible_review_stats.get("cache_hit", 0),
                "visible_review_stats_refetched_count": visible_review_stats.get("refetched", 0),
                "visible_appdetails_failure_count": visible_appdetails_stats.get("failed", 0),
                "visible_appdetails_cache_missing_fields_count": visible_appdetails_stats.get("cache_missing_fields", 0),
                "visible_appdetails_refetched_count": visible_appdetails_stats.get("refetched", 0),
                "steamdb_auto_fetch": "已跳过，首页仅保留入口卡。",
                "feed_refreshed_at": feed.refreshed_at,
                "from_cache": feed.from_cache,
                "used_stale_cache": feed.used_stale_cache,
                "message": feed.message,
                "section_counts": {key: len(value) for key, value in feed.sections.items()},
                "news_count": len(feed.news),
                "snapshot_count": len(snapshots),
            }
        )


def send_daily_watch_to_profile(row: pd.Series) -> None:
    metadata = set_profile_prefill_from_mapping(row.to_dict(), source_context=str(row.get("source_context", "") or row.get("source", "") or "今日观察记录"))
    developer = metadata.get("developer", "")
    publisher = metadata.get("publisher", "")
    genres = metadata.get("genres", "")
    release_date = metadata.get("release_date", "")
    metadata_keywords = "\n".join(
        part
        for part in [
            f"开发商：{developer}" if developer and developer != "未获取" else "",
            f"发行商：{publisher}" if publisher and publisher != "未获取" else "",
            f"类型：{genres}" if genres and genres != "未获取" else "",
            f"发售日期：{release_date}" if release_date and release_date != "未获取" else "",
        ]
        if part
    )
    if metadata_keywords:
        pending = st.session_state.get("pending_profile_prefill", {})
        if isinstance(pending, dict):
            pending["keywords"] = metadata_keywords
            st.session_state["pending_profile_prefill"] = pending
    st.session_state["pending_home_target"] = "profile"
    st.rerun()


def consume_pending_profile_prefill() -> None:
    pending = st.session_state.pop("pending_profile_prefill", None)
    if not isinstance(pending, dict):
        return
    steam_input = str(pending.get("steam_input", "") or "").strip()
    metadata = pending.get("metadata", {})
    if steam_input:
        st.session_state["profile_steam_input"] = steam_input
    if isinstance(metadata, dict):
        st.session_state["profile_prefill_metadata"] = metadata
        game_name = str(metadata.get("game_name", "") or "").strip()
        if game_name:
            st.session_state["profile_chinese_name"] = game_name
    keywords = str(pending.get("keywords", "") or "").strip()
    if keywords and not st.session_state.get("profile_user_keywords"):
        st.session_state["profile_user_keywords"] = keywords


def set_profile_prefill_from_mapping(data: dict, source_context: str = "") -> dict:
    normalized = normalize_steam_game_data(
        appid=str(data.get("appid", "") or ""),
        search_item=data,
        appdetails={},
        review_stats=data,
    )
    appid = _clean_prefill_value(normalized.get("appid") or data.get("appid"))
    steam_url = _clean_prefill_value(normalized.get("steam_url") or data.get("steam_url") or steam_url_from_appid(appid))
    source_url = _clean_prefill_value(data.get("source_url"))
    game_name = _clean_prefill_value(normalized.get("game_name") or data.get("game_name") or data.get("title"))
    steamdb_url = _clean_prefill_value(data.get("steamdb_url") or steamdb_app_url_from_appid(appid))
    metadata = {
        "appid": appid,
        "game_name": game_name,
        "steam_url": steam_url or source_url or steam_url_from_appid(appid),
        "steamdb_url": steamdb_url,
        "image_url": _clean_prefill_value(normalized.get("image_url") or data.get("image_url")),
        "developer": _clean_prefill_value(normalized.get("developer") or data.get("developer")),
        "publisher": _clean_prefill_value(normalized.get("publisher") or data.get("publisher")),
        "release_date": _clean_prefill_value(normalized.get("release_date") or data.get("release_date")),
        "genres": _clean_prefill_value(normalized.get("genres") or data.get("genres")),
        "categories": _clean_prefill_value(normalized.get("categories") or data.get("categories")),
        "price": _clean_prefill_value(normalized.get("price") or data.get("price")),
        "supports_schinese": _clean_prefill_value(normalized.get("supports_schinese") or data.get("supports_schinese")),
        "has_demo": _clean_prefill_value(normalized.get("has_demo") or data.get("has_demo")),
        "source_context": _clean_prefill_value(source_context or data.get("source_context") or data.get("source") or data.get("source_group")),
        "review_total": _clean_prefill_value(data.get("review_total")),
        "review_positive": _clean_prefill_value(data.get("review_positive")),
        "review_negative": _clean_prefill_value(data.get("review_negative")),
        "positive_rate": _clean_prefill_value(data.get("positive_rate")),
        "review_score_desc": _clean_prefill_value(data.get("review_score_desc")),
        "median_playtime_hours": _clean_prefill_value(data.get("median_playtime_hours")),
        "avg_playtime_hours": _clean_prefill_value(data.get("avg_playtime_hours")),
        "review_stats_status": _clean_prefill_value(data.get("review_stats_status")),
    }
    st.session_state["pending_profile_prefill"] = {
        "steam_input": metadata["steam_url"] or source_url or appid,
        "source": source_context or "profile_prefill",
        "candidate_id": data.get("candidate_id", ""),
        "metadata": metadata,
    }
    return metadata


def _clean_prefill_value(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"未获取", "未确认", "暂无", "None", "nan", "[]"} else text


def send_daily_watch_to_search_center(row: pd.Series) -> None:
    appid = str(row.get("appid", "") or "").strip()
    game_name = str(row.get("game_name", "") or "").strip() or (f"AppID {appid}" if appid else "")
    source = str(row.get("source", "") or "").strip()
    note = str(row.get("note", "") or "").strip()
    source_url = str(row.get("source_url", "") or "").strip()
    developer = str(row.get("developer", "") or "").strip()
    publisher = str(row.get("publisher", "") or "").strip()
    genres = str(row.get("genres", "") or "").strip()
    tags = str(row.get("tags", "") or "").strip()
    release_date = str(row.get("release_date", "") or "").strip()
    source_group = str(row.get("source_group", "") or "").strip()
    search_values = {
        "game_name": game_name,
        "steam_url": steam_url_from_appid(appid) or source_url,
        "short_description": " / ".join(value for value in [note, release_date] if value and value != "未获取"),
        "tags": ", ".join(value for value in [genres, tags, source_group or source] if value and value != "未获取"),
        "core_keywords": ", ".join(value for value in [game_name, appid, developer, publisher, genres] if value and value != "未获取"),
        "theme_keywords": ", ".join(value for value in [genres, tags, source_group or source] if value and value != "未获取"),
        "english_keywords": "",
        "reference_games": "",
        "developer": developer if developer != "未获取" else "",
        "publisher": publisher if publisher != "未获取" else "",
    }
    apply_search_center_values(search_values)
    st.session_state["pending_home_target"] = "search"
    try:
        platforms = load_search_platforms(SEARCH_PLATFORM_CONFIG_PATH)
        navigation_table = build_platform_navigation(
            SearchCenterInput(**search_values),
            platforms,
            limit=int(st.session_state.get("search_keyword_limit", 20)),
        )
    except Exception as exc:
        st.error(f"搜索中心生成失败：{exc}")
        return
    st.session_state["search_navigation_table"] = navigation_table
    st.rerun()


STEAMDB_LIST_WATCH_COLUMNS = [
    "note_type",
    "list_name",
    "list_url",
    "filters",
    "observed_date",
    "import_count",
    "candidate_count",
    "attention_count",
    "updated_at",
]


def render_steamdb_import_page() -> None:
    st.subheader("SteamDB 导入")
    st.caption("用于把 SteamDB 榜单或搜索结果中复制的文本粘贴进来，自动识别 AppID、游戏名、排名、followers、reviews、peak、release、price 等字段，再发送到候选池。")
    st.caption("本页不硬爬 SteamDB、不调用外部 API，只处理你粘贴的文本。")

    raw_text = st.text_area(
        "粘贴 SteamDB 列表文本 / 表格文本 / 多行记录",
        key="steamdb_paste_import_text",
        height=240,
        placeholder=(
            "https://steamdb.info/app/1234560/\n"
            "https://store.steampowered.com/app/730/CounterStrike/\n"
            "1\tGame Name\t1234560\t12,345\t456\t1,234\t2026-06-01\t$19.99\n"
            "3678970"
        ),
    )

    parse_cols = st.columns([1, 1, 1, 1])
    if parse_cols[0].button("解析粘贴内容", key="steamdb_paste_parse", use_container_width=True):
        results = parse_steamdb_paste(raw_text)
        st.session_state["steamdb_paste_results"] = results
        st.session_state["steamdb_paste_selected_labels"] = [
            _steamdb_import_option_label(index, row)
            for index, row in enumerate(results)
            if row.get("parse_confidence") == "high"
        ]
        if results:
            st.success(f"已解析 {len(results)} 行。")
        else:
            st.warning("没有识别到可解析行。")

    results = st.session_state.get("steamdb_paste_results", [])
    if results:
        render_steamdb_paste_results(results)

    render_steamdb_list_watch_note_section(results)


def enrich_steamdb_paste_results_basic_info(results: list[dict]) -> tuple[list[dict], dict]:
    appids = []
    seen = set()
    for row in results:
        appid = clean_candidate_value(row.get("appid"))
        if appid and appid not in seen:
            appids.append(appid)
            seen.add(appid)

    enriched = enrich_appids_basic(appids)
    stats = {
        "pending": len(appids),
        "success": 0,
        "cache_hit": 0,
        "failed": 0,
        "cache_warning": "",
    }
    output = []
    for row in results:
        updated = dict(row)
        appid = clean_candidate_value(row.get("appid"))
        if not appid:
            output.append(updated)
            continue

        info = enriched.get(appid, {})
        if info.get("cache_warning") and not stats["cache_warning"]:
            stats["cache_warning"] = str(info.get("cache_warning") or "")
        if info.get("cache_hit"):
            stats["cache_hit"] += 1
        if info.get("success"):
            stats["success"] += 1
            for field in [
                "game_name",
                "steam_url",
                "developer",
                "publisher",
                "release_date",
                "release_status",
                "price",
                "review_score",
                "review_count",
                "has_demo",
                "supports_schinese",
            ]:
                value = clean_candidate_value(info.get(field))
                if value:
                    updated[field] = value
            updated["source_notes"] = append_note_text(updated.get("source_notes"), info.get("source_notes"))
            updated["parse_notes"] = append_note_text(updated.get("parse_notes"), "Steam basic info enriched")
        else:
            stats["failed"] += 1
            updated["steam_url"] = clean_candidate_value(updated.get("steam_url")) or clean_candidate_value(info.get("steam_url")) or steam_url_from_appid(appid)
            updated["parse_notes"] = append_note_text(updated.get("parse_notes"), "Steam 基础信息补全失败 / 需人工复核")
            updated["source_notes"] = append_note_text(updated.get("source_notes"), info.get("source_notes"))
        output.append(updated)
    return output, stats


def append_note_text(current, note) -> str:
    current_text = clean_candidate_value(current)
    note_text = clean_candidate_value(note)
    if not note_text:
        return current_text
    if note_text in current_text:
        return current_text
    return f"{current_text}；{note_text}" if current_text else note_text


def render_steamdb_paste_results(results: list[dict]) -> None:
    st.markdown("### 解析结果预览")
    option_labels = [_steamdb_import_option_label(index, row) for index, row in enumerate(results)]
    select_cols = st.columns(6)
    if select_cols[0].button("全选高可信", key="steamdb_select_high", use_container_width=True):
        st.session_state["steamdb_paste_selected_labels"] = [
            label
            for label, row in zip(option_labels, results)
            if row.get("parse_confidence") == "high"
        ]
    if select_cols[1].button("全选有 AppID", key="steamdb_select_appid", use_container_width=True):
        st.session_state["steamdb_paste_selected_labels"] = [
            label
            for label, row in zip(option_labels, results)
            if str(row.get("appid", "") or "").strip()
        ]
    if select_cols[2].button("清空选择", key="steamdb_select_clear", use_container_width=True):
        st.session_state["steamdb_paste_selected_labels"] = []
    if select_cols[3].button("导出解析结果 CSV", key="steamdb_export_parse_csv", use_container_width=True):
        export_path = export_steamdb_parse_results_csv(results)
        st.success(f"解析结果已导出：{export_path}")

    if select_cols[4].button("补全 Steam 基础信息", key="steamdb_enrich_basic_info", use_container_width=True):
        previous_selected = st.session_state.get("steamdb_paste_selected_labels", [])
        selected_index_before = {option_labels.index(label) for label in previous_selected if label in option_labels}
        enriched_results, stats = enrich_steamdb_paste_results_basic_info(results)
        st.session_state["steamdb_paste_results"] = enriched_results
        refreshed_labels = [_steamdb_import_option_label(index, row) for index, row in enumerate(enriched_results)]
        st.session_state["steamdb_paste_selected_labels"] = [
            refreshed_labels[index]
            for index in selected_index_before
            if index < len(refreshed_labels)
        ]
        st.session_state["steamdb_paste_enrich_stats"] = stats
        st.rerun()

    enrich_stats = st.session_state.get("steamdb_paste_enrich_stats", {})
    if enrich_stats:
        st.info(
            "Steam 基础信息补全："
            f"待补全 {enrich_stats.get('pending', 0)}，"
            f"成功 {enrich_stats.get('success', 0)}，"
            f"缓存命中 {enrich_stats.get('cache_hit', 0)}，"
            f"失败 {enrich_stats.get('failed', 0)}"
        )
        if enrich_stats.get("cache_warning"):
            st.warning(str(enrich_stats.get("cache_warning")))

    selected_labels = st.multiselect(
        "选择要导入候选池的记录",
        option_labels,
        default=st.session_state.get("steamdb_paste_selected_labels", []),
        key="steamdb_paste_selected_labels",
    )
    selected_index = {option_labels.index(label) for label in selected_labels if label in option_labels}
    preview_rows = []
    for index, row in enumerate(results):
        preview_rows.append(
            {
                "是否选择": "是" if index in selected_index else "",
                "游戏名": row.get("game_name", ""),
                "AppID": row.get("appid", ""),
                "Developer": row.get("developer", ""),
                "Publisher": row.get("publisher", ""),
                "Rank": row.get("rank", ""),
                "Followers": row.get("followers", ""),
                "Reviews": row.get("reviews", ""),
                "Peak": row.get("peak_ccu", ""),
                "Rating": row.get("rating", ""),
                "Release": row.get("release_date", ""),
                "Release Status": row.get("release_status", ""),
                "Price": row.get("price", ""),
                "Demo": row.get("has_demo", ""),
                "简中": row.get("supports_schinese", ""),
                "Steam": row.get("steam_url", ""),
                "解析可信度": row.get("parse_confidence", ""),
                "解析备注": row.get("parse_notes", ""),
            }
        )
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

    selected_rows = [row for index, row in enumerate(results) if index in selected_index]
    if select_cols[5].button("发送选中项到候选池", key="steamdb_import_selected_candidates", use_container_width=True):
        if not selected_rows:
            st.warning("请先选择至少一条记录。")
        else:
            stats = import_steamdb_paste_rows_to_candidate_pool(selected_rows)
            st.success(
                "导入完成："
                f"新增 {stats['created']} 条，"
                f"重复补空字段 {stats['updated']} 条，"
                f"失败 {stats['failed']} 条。"
            )
            if stats["failed_rows"]:
                st.dataframe(pd.DataFrame(stats["failed_rows"]), use_container_width=True, hide_index=True)


def _steamdb_import_option_label(index: int, row: dict) -> str:
    appid = str(row.get("appid", "") or "").strip()
    game_name = str(row.get("game_name", "") or "").strip() or (f"AppID {appid}" if appid else "未识别游戏名")
    confidence = str(row.get("parse_confidence", "") or "low")
    return f"{index + 1}. {game_name} | {appid or '无 AppID'} | {confidence}"


def export_steamdb_parse_results_csv(results: list[dict]) -> Path:
    SEARCH_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_path = SEARCH_EXPORT_DIR / f"steamdb_parse_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    pd.DataFrame(results).to_csv(export_path, index=False, encoding="utf-8-sig")
    return export_path


def ensure_steamdb_list_watch_note_columns() -> pd.DataFrame:
    ensure_watch_note_csv_exists(STEAMDB_WATCH_NOTE_CSV_PATH)
    try:
        data = pd.read_csv(STEAMDB_WATCH_NOTE_CSV_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    for column in STEAMDB_LIST_WATCH_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    for column in ["record_id", "created_at", "source_page", "source_url", "note"]:
        if column not in data.columns:
            data[column] = ""
    data.to_csv(STEAMDB_WATCH_NOTE_CSV_PATH, index=False, encoding="utf-8-sig")
    return data


def save_steamdb_list_watch_note(note: dict) -> Path:
    data = ensure_steamdb_list_watch_note_columns()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {column: "" for column in data.columns}
    row.update(
        {
            "record_id": str(uuid4()),
            "created_at": now,
            "updated_at": now,
            "note_type": "steamdb_list_watch",
            "source_page": "榜单观察记录",
            "source_url": note.get("list_url", ""),
            "game_name": note.get("list_name", ""),
            "list_name": note.get("list_name", ""),
            "list_url": note.get("list_url", ""),
            "filters": note.get("filters", ""),
            "observed_date": note.get("observed_date", ""),
            "note": note.get("note", ""),
            "next_action": "榜单观察",
            "import_count": note.get("import_count", ""),
            "candidate_count": note.get("candidate_count", ""),
            "attention_count": note.get("attention_count", ""),
        }
    )
    pd.concat([data, pd.DataFrame([row])], ignore_index=True).to_csv(STEAMDB_WATCH_NOTE_CSV_PATH, index=False, encoding="utf-8-sig")
    return STEAMDB_WATCH_NOTE_CSV_PATH


def render_steamdb_list_watch_note_section(results: list[dict]) -> None:
    with st.expander("榜单观察记录", expanded=False):
        st.caption("记录今天看过的 SteamDB 页面，避免重复翻同一页。")
        selected_count = len(st.session_state.get("steamdb_paste_selected_labels", []))
        with st.form("steamdb_list_watch_note_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                list_name = st.text_input("榜单名称", placeholder="例如：Top Rated 2026 / Next Fest")
                observed_date = st.date_input("观察日期", value=datetime.now().date())
                import_count = st.number_input("本次导入数量", min_value=0, value=len(results), step=1)
            with col2:
                list_url = st.text_input("榜单 URL", placeholder="https://steamdb.info/...")
                candidate_count = st.number_input("候选数量", min_value=0, value=selected_count, step=1)
                attention_count = st.number_input("值得关注项目数量", min_value=0, value=0, step=1)
            with col3:
                filters = st.text_area("筛选条件", height=80)
                note = st.text_area("备注", height=80)
            submitted = st.form_submit_button("保存榜单观察记录")
        if submitted:
            if not list_name.strip() and not list_url.strip():
                st.error("请至少填写榜单名称或榜单 URL。")
            else:
                save_steamdb_list_watch_note(
                    {
                        "list_name": list_name.strip(),
                        "list_url": list_url.strip(),
                        "filters": filters.strip(),
                        "observed_date": observed_date.strftime("%Y-%m-%d"),
                        "note": note.strip(),
                        "import_count": str(import_count),
                        "candidate_count": str(candidate_count),
                        "attention_count": str(attention_count),
                    }
                )
                st.success("已保存 SteamDB 榜单观察记录。")

        notes = ensure_steamdb_list_watch_note_columns()
        list_notes = notes.loc[notes["note_type"].astype(str).eq("steamdb_list_watch")].tail(10).copy()
        if not list_notes.empty:
            display = list_notes.loc[
                :,
                ["created_at", "list_name", "list_url", "filters", "observed_date", "import_count", "candidate_count", "attention_count", "note"],
            ].rename(
                columns={
                    "created_at": "创建时间",
                    "list_name": "榜单名称",
                    "list_url": "榜单 URL",
                    "filters": "筛选条件",
                    "observed_date": "观察日期",
                    "import_count": "本次导入数量",
                    "candidate_count": "候选数量",
                    "attention_count": "值得关注项目数量",
                    "note": "备注",
                }
            )
            st.dataframe(display, use_container_width=True, hide_index=True)


def render_steamdb_discovery_page() -> None:
    """Render SteamDB navigation, templates, watch notes, and import handoff."""
    ensure_template_csv_exists(STEAMDB_TEMPLATE_CSV_PATH)
    ensure_watch_note_csv_exists(STEAMDB_WATCH_NOTE_CSV_PATH)

    st.subheader("SteamDB 发现工作台")
    st.caption("只做 SteamDB 常用页面导航、筛选模板、榜单观察记录和项目导入；不自动抓 SteamDB 榜单内容。")

    render_steamdb_common_links()
    render_steamdb_candidate_bulk_import()
    render_steamdb_import_section()

    template_count = len(load_templates(STEAMDB_TEMPLATE_CSV_PATH))
    if st.checkbox(f"我的筛选模板（{template_count} 个）", value=False, key="steamdb_show_templates"):
        render_steamdb_template_section()

    watch_note_count = len(load_watch_notes(STEAMDB_WATCH_NOTE_CSV_PATH))
    if st.checkbox(f"榜单观察记录（{watch_note_count} 条）", value=False, key="steamdb_show_watch_notes"):
        render_steamdb_watch_note_section()

    with st.expander("数据来源 / 调试信息（仅排错时查看）", expanded=False):
        st.write(f"筛选模板文件：`{STEAMDB_TEMPLATE_CSV_PATH}`")
        st.write(f"榜单观察文件：`{STEAMDB_WATCH_NOTE_CSV_PATH}`")


def render_steamdb_common_links() -> None:
    st.markdown("### 常用榜单入口")
    groups = get_steamdb_common_link_groups()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**新作发现**")
        render_link_button_grid(groups["新作发现"], "steamdb_discovery")
    with col2:
        st.markdown("**热度观察**")
        render_link_button_grid(groups["热度观察"], "steamdb_heat")
    with col3:
        st.markdown("**活动 / 新品节**")
        render_link_button_grid(groups["活动 / 新品节"], "steamdb_event")
        st.caption("Next Fest 或活动页先手动筛选，再把 URL 保存为模板。")


def render_steamdb_candidate_bulk_import() -> None:
    with st.expander("批量导入候选", expanded=False):
        st.caption("支持多行 AppID、Steam 链接、SteamDB 链接或混合文本；本版只做轻量入池，不自动抓取全部详情。")
        raw_text = st.text_area(
            "每行一个项目",
            key="steamdb_candidate_bulk_import_text",
            height=150,
            placeholder="3915640\nhttps://steamdb.info/app/3915640/\nhttps://store.steampowered.com/app/3915640/",
        )
        if st.button("导入到候选池", key="steamdb_candidate_bulk_import_submit"):
            parsed_rows = parse_candidate_import_lines(raw_text)
            if not parsed_rows:
                st.warning("请先粘贴至少一行 AppID 或链接。")
                return
            max_import_count = 20
            success_count = 0
            placeholder_count = 0
            duplicate_count = 0
            failed_rows = []
            importable_rows = [row for row in parsed_rows if row.get("appid")]
            if len(importable_rows) > max_import_count:
                st.warning(f"单次最多补全 {max_import_count} 条，已截断后续 {len(importable_rows) - max_import_count} 条。")
            allowed_appids = {
                row.get("appid", "")
                for row in importable_rows[:max_import_count]
            }
            for parsed in parsed_rows:
                appid = parsed.get("appid", "")
                if not appid:
                    failed_rows.append(
                        {
                            "行号": parsed.get("line_number"),
                            "原文": parsed.get("raw_line"),
                            "失败原因": parsed.get("error") or "未解析到 AppID",
                        }
                    )
                    continue
                if appid not in allowed_appids:
                    continue
                try:
                    record, enriched = build_candidate_pool_record_from_appid(
                        appid,
                        source_url=parsed.get("raw_line", ""),
                        source="SteamDB 批量导入",
                    )
                except Exception as exc:
                    failed_rows.append(
                        {
                            "行号": parsed.get("line_number"),
                            "原文": parsed.get("raw_line"),
                            "失败原因": f"基础详情补全异常：{exc}",
                        }
                    )
                    continue
                _, action = upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
                if action != "created":
                    duplicate_count += 1
                elif enriched:
                    success_count += 1
                else:
                    placeholder_count += 1
            st.success(
                "导入完成："
                f"成功补全 {success_count} 条，"
                f"仅占位导入 {placeholder_count} 条，"
                f"重复跳过/更新 {duplicate_count} 条，"
                f"失败 {len(failed_rows)} 行。"
            )
            if failed_rows:
                st.dataframe(pd.DataFrame(failed_rows), use_container_width=True, hide_index=True)


def render_link_button_grid(links: list[tuple[str, str]], key_prefix: str) -> None:
    for label, url in links:
        st.link_button(label, url, use_container_width=True)


def render_steamdb_template_section() -> None:
    st.markdown("### 我的筛选模板")
    with st.form("steamdb_template_form"):
        col1, col2 = st.columns(2)
        with col1:
            template_name = st.text_input("模板名称", placeholder="例如：Next Fest 卡牌肉鸽观察")
            template_category = st.selectbox(
                "分类",
                ["新作发现", "热度观察", "活动 / 新品节", "自定义筛选", "Other"],
            )
            is_favorite = st.checkbox("收藏模板", value=True)
        with col2:
            steamdb_url = st.text_input(
                "SteamDB 筛选链接",
                placeholder="https://steamdb.info/stats/gameratings/2026/",
            )
            template_note = st.text_area("备注", height=88, placeholder="记录筛选条件、活动名或观察用途")
        save_template = st.form_submit_button("保存当前 SteamDB 链接为模板")

    if save_template:
        if not template_name.strip() or not steamdb_url.strip():
            st.error("请填写模板名称和 SteamDB 链接。")
        elif "steamdb.info" not in steamdb_url:
            st.error("请填写 SteamDB 链接。")
        else:
            template = SteamDBTemplate(
                template_name=template_name.strip(),
                category=template_category,
                steamdb_url=steamdb_url.strip(),
                note=template_note.strip(),
                is_favorite="True" if is_favorite else "False",
            )
            save_template_to_csv(template, STEAMDB_TEMPLATE_CSV_PATH)
            st.success("已保存 SteamDB 筛选模板。")

    templates = load_templates(STEAMDB_TEMPLATE_CSV_PATH)
    if templates.empty:
        st.info("暂无 SteamDB 模板。")
        return

    display_templates = templates.rename(
        columns={
            "template_name": "模板名称",
            "category": "分类",
            "steamdb_url": "SteamDB 链接",
            "note": "备注",
            "is_favorite": "收藏",
            "created_at": "创建时间",
        }
    )
    st.dataframe(
        display_templates.loc[:, ["模板名称", "分类", "SteamDB 链接", "备注", "收藏", "创建时间"]],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("打开已保存模板", expanded=False):
        for index, row in templates.head(30).iterrows():
            label = str(row.get("template_name", "")).strip() or f"SteamDB 模板 {index + 1}"
            url = str(row.get("steamdb_url", "")).strip()
            if url:
                st.link_button(f"{index + 1}. {label}", url)


def render_steamdb_watch_note_section() -> None:
    st.markdown("### 榜单观察记录")
    st.caption("从 SteamDB 表格手动摘录重点字段：Name、Release、Follows、Reviews、Peak、Rating、Price。")

    with st.form("steamdb_watch_note_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            source_page = st.selectbox(
                "来源页面",
                [
                    "Top Rated",
                    "Charts",
                    "Trending Followers",
                    "Wishlist Activity",
                    "Most Wishlisted",
                    "Upcoming",
                    "Calendar",
                    "Next Fest",
                    "Other",
                ],
            )
            game_name = st.text_input("游戏名")
            appid_input = st.text_input("AppID")
            steamdb_url = st.text_input("SteamDB 链接", placeholder="https://steamdb.info/app/3915640/")
        with col2:
            steam_url = st.text_input("Steam 链接", placeholder="https://store.steampowered.com/app/3915640/")
            source_url = st.text_input("来源榜单链接")
            rank_text = st.text_input("排名/位置")
            release_date = st.text_input("发售日期")
        with col3:
            followers = st.text_input("Followers")
            reviews = st.text_input("Reviews")
            rating = st.text_input("Rating")
            peak_players = st.text_input("Peak")
            price = st.text_input("价格")

        note_text = st.text_area("备注", height=80)
        next_action = st.selectbox("下一步动作", ["生成项目画像", "加入候选", "暂缓", "放弃", "待试玩"])
        save_note = st.form_submit_button("保存榜单观察记录")

    if save_note:
        appid = parse_steamdb_appid(appid_input) or parse_steamdb_appid(steamdb_url) or parse_steamdb_appid(steam_url)
        resolved_steam_url = steam_url.strip() or steam_url_from_appid(appid)
        resolved_steamdb_url = steamdb_url.strip() or steamdb_app_url_from_appid(appid)
        if not game_name.strip() and not appid:
            st.error("请至少填写游戏名或 AppID。")
        else:
            watch_note = SteamDBWatchNote(
                source_page=source_page,
                source_url=source_url.strip() or resolved_steamdb_url,
                game_name=game_name.strip(),
                appid=appid,
                steam_url=resolved_steam_url,
                steamdb_url=resolved_steamdb_url,
                rank_text=rank_text.strip(),
                release_date=release_date.strip(),
                followers=followers.strip(),
                reviews=reviews.strip(),
                rating=rating.strip(),
                peak_players=peak_players.strip(),
                price=price.strip(),
                note=note_text.strip(),
                next_action=next_action,
            )
            save_watch_note_to_csv(watch_note, STEAMDB_WATCH_NOTE_CSV_PATH)
            st.success("已保存 SteamDB 榜单观察记录。")

    watch_notes = load_watch_notes(STEAMDB_WATCH_NOTE_CSV_PATH)
    if watch_notes.empty:
        st.info("暂无榜单观察记录。")
        return

    display_notes = watch_notes.rename(
        columns={
            "created_at": "创建时间",
            "source_page": "来源页面",
            "game_name": "游戏名",
            "appid": "AppID",
            "rank_text": "排名/位置",
            "release_date": "发售日期",
            "followers": "Followers",
            "reviews": "Reviews",
            "rating": "Rating",
            "peak_players": "Peak",
            "price": "价格",
            "next_action": "下一步动作",
            "note": "备注",
        }
    )
    st.dataframe(
        display_notes.loc[
            :,
            [
                "创建时间",
                "来源页面",
                "游戏名",
                "AppID",
                "排名/位置",
                "发售日期",
                "Followers",
                "Reviews",
                "Rating",
                "Peak",
                "价格",
                "下一步动作",
                "备注",
            ],
        ],
        use_container_width=True,
        hide_index=True,
    )
    render_steamdb_watch_note_handoff(watch_notes)


def render_steamdb_watch_note_handoff(watch_notes: pd.DataFrame) -> None:
    with st.expander("从观察记录发送到项目画像或搜索中心", expanded=False):
        options = []
        for _, row in watch_notes.tail(50).iterrows():
            game_name = str(row.get("game_name", "")).strip() or "未命名游戏"
            appid = str(row.get("appid", "")).strip()
            created_at = str(row.get("created_at", "")).strip()
            record_id = str(row.get("record_id", "")).strip()
            label = f"{game_name} | {appid or '无 AppID'} | {created_at}"
            options.append({"label": label, "record_id": record_id})
        if not options:
            st.info("暂无可联动的观察记录。")
            return

        selected_label = st.selectbox(
            "选择观察记录",
            [option["label"] for option in options],
            key="steamdb_watch_note_selector",
        )
        selected_id = next(option["record_id"] for option in options if option["label"] == selected_label)
        selected_rows = watch_notes.loc[watch_notes["record_id"].astype(str) == str(selected_id)]
        if selected_rows.empty:
            st.warning("未找到所选观察记录。")
            return
        selected = selected_rows.iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("发送所选观察到项目画像"):
                send_steamdb_row_to_profile(selected)
        with col2:
            if st.button("发送所选观察到搜索中心"):
                send_steamdb_row_to_search_center(selected)
        with col3:
            if st.button("保存所选为快速项目记录"):
                save_steamdb_row_as_project(selected)


def render_steamdb_import_section() -> None:
    st.markdown("### 快速导入项目")
    col1, col2 = st.columns([2, 1])
    with col1:
        import_input = st.text_input(
            "AppID 或 SteamDB App 链接",
            key="steamdb_import_input",
            placeholder="https://steamdb.info/app/3915640/",
        )
    with col2:
        import_game_name = st.text_input("游戏名（可选）", key="steamdb_import_game_name")

    appid = parse_steamdb_appid(import_input)
    if import_input.strip() and not appid:
        st.warning("未能解析 AppID，请输入纯数字 AppID 或 SteamDB App 链接。")
        return
    if not appid:
        st.info("输入 AppID 后会生成 Steam / SteamDB 单 App 快捷入口。")
        return

    st.success(f"已解析 AppID：{appid}")
    link_columns = st.columns(4)
    for index, (label, url) in enumerate(steamdb_quick_links(appid)):
        with link_columns[index % 4]:
            st.link_button(label, url, use_container_width=True)

    row_data = pd.Series(
        {
            "game_name": import_game_name.strip(),
            "appid": appid,
            "steam_url": steam_url_from_appid(appid),
            "steamdb_url": steamdb_app_url_from_appid(appid),
            "source_page": "Quick Import",
            "source_url": steamdb_app_url_from_appid(appid),
            "next_action": "生成项目画像",
            "note": "来自 SteamDB 发现工作台快速导入",
        }
    )
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    with action_col1:
        if st.button("发送到一键项目画像", key="steamdb_send_profile"):
            send_steamdb_row_to_profile(row_data)
    with action_col2:
        if st.button("发送到搜索中心", key="steamdb_send_search"):
            send_steamdb_row_to_search_center(row_data)
    with action_col3:
        if st.button("保存为快速项目记录", key="steamdb_save_project"):
            save_steamdb_row_as_project(row_data)
    with action_col4:
        if st.button("加入候选池", key="steamdb_add_candidate_pool"):
            save_mapping_to_candidate_pool(
                row_data.to_dict(),
                source="SteamDB 快速导入",
                stage="新发现",
                success_prefix="已加入项目候选池",
            )


def render_steam_browser_collector_page() -> None:
    st.subheader("Steam 浏览器采集")
    st.caption(
        "打开一个受控浏览器窗口，用户在其中浏览 Steam 商店、搜索页、新品节、Coming Soon、标签页等页面；"
        "工具读取当前页面里的 Steam app 链接并导入候选池。"
    )
    st.caption("本页不抓 SteamDB、不做反爬对抗、不伪装登录，也不读取 Streamlit iframe DOM。")
    st.info("SteamDB 自动抓取入口已下线。SteamDB 仍可通过“SteamDB 导入”进行手动粘贴导入；新项目发现优先使用 Steam 浏览器采集。")

    if not playwright_available():
        st.error("当前环境未安装 Playwright，Steam 浏览器采集不可用。")
        st.code("pip install playwright\nplaywright install chromium", language="bash")
        return

    action_cols = st.columns(6)
    if action_cols[0].button("打开 Steam 浏览器", key="steam_browser_open", use_container_width=True):
        result = launch_browser(STEAM_BROWSER_USER_DATA_DIR, DEFAULT_STEAM_URL)
        st.session_state["steam_browser_running"] = bool(result.get("browser_running"))
        st.session_state["steam_browser_debug_port"] = result.get("debug_port", STEAM_BROWSER_DEBUG_PORT)
        if result.get("success"):
            st.success(result.get("message", "Steam 浏览器已打开。"))
        else:
            st.error(result.get("message", "Steam 浏览器启动失败。"))

    if action_cols[1].button("抓取当前页 AppID", key="steam_browser_collect_page", use_container_width=True):
        result = collect_current_page_appids(STEAM_BROWSER_COLLECTED_CSV_PATH, STEAM_BROWSER_DEBUG_PORT)
        if result.get("success"):
            st.session_state["steam_browser_last_rows"] = result.get("rows", [])
            stats = result.get("save_stats", {})
            suffix = f" 已保存：新增 {stats.get('created', 0)} 条，更新 {stats.get('updated', 0)} 条。" if stats else ""
            st.success(result.get("message", "已抓取当前页 AppID。") + suffix)
        else:
            st.warning(result.get("message", "当前页面未发现 Steam app 链接，请滚动或打开具体游戏页后再试。"))

    if action_cols[2].button("抓取当前打开游戏", key="steam_browser_collect_app", use_container_width=True):
        result = collect_current_app(STEAM_BROWSER_COLLECTED_CSV_PATH, STEAM_BROWSER_DEBUG_PORT)
        if result.get("success"):
            st.session_state["steam_browser_last_rows"] = result.get("rows", [])
            stats = result.get("save_stats", {})
            suffix = f" 已保存：新增 {stats.get('created', 0)} 条，更新 {stats.get('updated', 0)} 条。" if stats else ""
            st.success(result.get("message", "已抓取当前打开游戏。") + suffix)
        else:
            st.warning(result.get("message", "当前打开页面不是 Steam app 页面。"))

    last_rows = st.session_state.get("steam_browser_last_rows", [])
    if action_cols[3].button("保存本次采集", key="steam_browser_save", use_container_width=True):
        if not last_rows:
            st.warning("请先抓取当前页 AppID 或当前打开游戏。")
        else:
            stats = save_collected_rows(STEAM_BROWSER_COLLECTED_CSV_PATH, last_rows)
            st.success(f"已保存：新增 {stats['created']} 条，更新 {stats['updated']} 条，当前共 {stats['total']} 条。")

    if action_cols[4].button("补全基础信息", key="steam_browser_enrich", use_container_width=True):
        try:
            stats = enrich_collected_basic_info(STEAM_BROWSER_COLLECTED_CSV_PATH)
        except Exception as exc:
            st.error(f"Steam 基础信息补全失败：{exc}")
        else:
            st.success(
                f"补全完成：请求 {stats['requested']} 个，成功 {stats['updated']} 个，"
                f"失败 {stats['failed']} 个，缓存命中 {stats['cache_hit']} 个。"
            )

    is_browser_running = browser_is_open(STEAM_BROWSER_DEBUG_PORT)
    st.session_state["steam_browser_running"] = is_browser_running
    st.session_state["steam_browser_debug_port"] = STEAM_BROWSER_DEBUG_PORT
    action_cols[5].caption(f"浏览器状态：{'已打开' if is_browser_running else '未打开'}")

    if last_rows:
        with st.expander(f"本次抓取预览（{len(last_rows)} 条，保存后进入下方表格）", expanded=False):
            st.dataframe(pd.DataFrame(last_rows), use_container_width=True, hide_index=True)

    cleanup_cols = st.columns([1, 1, 2])
    if cleanup_cols[0].button("按 AppID 去重", key="steam_browser_dedupe_collected", use_container_width=True):
        stats = dedupe_collected_by_appid(STEAM_BROWSER_COLLECTED_CSV_PATH)
        st.success(
            "去重完成："
            f"before {stats['before']}，after {stats['after']}，removed {stats['removed']}。"
            f"备份：{stats['backup_path']}"
        )
    confirm_clear = cleanup_cols[1].checkbox(
        "我确认清空本次采集",
        key="steam_browser_confirm_clear_collected",
        help="会清空 data/steam_browser_collected.csv；清空前会自动备份，不会修改 candidate_pool.csv。",
    )
    if cleanup_cols[2].button("清空本次采集", key="steam_browser_clear_collected", use_container_width=True):
        if not confirm_clear:
            st.warning("清空前请先勾选确认。此操作只清空 data/steam_browser_collected.csv，不会修改 candidate_pool.csv。")
        else:
            stats = clear_collected_csv(STEAM_BROWSER_COLLECTED_CSV_PATH)
            st.session_state["steam_browser_last_rows"] = []
            st.success(
                "已清空本次采集："
                f"before {stats['before']}，after {stats['after']}，removed {stats['removed']}。"
                f"备份：{stats['backup_path']}"
            )

    data = apply_import_suggestions(load_collected(STEAM_BROWSER_COLLECTED_CSV_PATH))
    filter_cols = st.columns(6)
    filtered = filter_collected(
        data,
        demo_only=filter_cols[0].checkbox("只看有 Demo", key="steam_browser_filter_demo"),
        unreleased_only=filter_cols[1].checkbox("只看未发售 / TBA", key="steam_browser_filter_unreleased"),
        self_published_only=filter_cols[2].checkbox("只看自发行", key="steam_browser_filter_self"),
        schinese_only=filter_cols[3].checkbox("只看支持简中", key="steam_browser_filter_schinese"),
        observation_only=filter_cols[4].checkbox("只看候选池观察 / 待试玩", key="steam_browser_filter_observation"),
        exclude_reference=filter_cols[5].checkbox("排除竞品参考", key="steam_browser_filter_reference"),
    )

    if filtered.empty:
        st.info("暂无 Steam 浏览器采集记录。请先打开 Steam 浏览器并抓取当前页 AppID。")
        return

    select_cols = st.columns(6)
    selection_actions = [
        ("全选当前筛选结果", "select_visible"),
        ("全选有 Demo", "select_demo"),
        ("全选有 Demo + 自发行", "select_demo_self"),
        ("全选未上线 + 有 Demo", "select_unreleased_demo"),
        ("清空当前选择", "clear_visible"),
        ("反选当前筛选结果", "invert_visible"),
    ]
    for index, (label, mode) in enumerate(selection_actions):
        if select_cols[index].button(label, key=f"steam_browser_bulk_select_{mode}", use_container_width=True):
            bulk_update_collected_selection(STEAM_BROWSER_COLLECTED_CSV_PATH, filtered, mode)
            st.session_state["steam_browser_editor_version"] = int(st.session_state.get("steam_browser_editor_version", 0)) + 1
            data = apply_import_suggestions(load_collected(STEAM_BROWSER_COLLECTED_CSV_PATH))
            filtered = filter_collected(
                data,
                demo_only=st.session_state.get("steam_browser_filter_demo", False),
                unreleased_only=st.session_state.get("steam_browser_filter_unreleased", False),
                self_published_only=st.session_state.get("steam_browser_filter_self", False),
                schinese_only=st.session_state.get("steam_browser_filter_schinese", False),
                observation_only=st.session_state.get("steam_browser_filter_observation", False),
                exclude_reference=st.session_state.get("steam_browser_filter_reference", False),
            )

    display = collected_display_data_v074(filtered)
    edited = st.data_editor(
        display,
        key=f"steam_browser_collected_editor_{st.session_state.get('steam_browser_editor_version', 0)}",
        use_container_width=True,
        hide_index=True,
        disabled=[column for column in display.columns if column != "是否选择"],
        column_config={
            "Steam 链接": st.column_config.LinkColumn("Steam 链接", display_text="打开 Steam"),
        },
    )
    selected_display = edited.loc[edited["是否选择"].astype(bool)].copy() if "是否选择" in edited.columns else pd.DataFrame()
    selected_appids = set(selected_display["AppID"].astype(str).str.strip()) if not selected_display.empty else set()
    visible_appids = filtered["appid"].astype(str).str.strip().tolist()
    update_collected_selection(STEAM_BROWSER_COLLECTED_CSV_PATH, visible_appids, list(selected_appids))
    selected_rows = filtered.loc[filtered["appid"].astype(str).str.strip().isin(selected_appids)].copy()

    send_cols = st.columns([1, 3])
    if send_cols[0].button("发送选中项到候选池", key="steam_browser_send_candidates", use_container_width=True):
        if selected_rows.empty:
            st.warning("请先在表格中勾选要发送的项目。")
        else:
            stats = import_steam_browser_rows_to_candidate_pool(selected_rows.to_dict("records"))
            st.success(f"发送完成：新增 {stats['created']} 条，补空字段 {stats['updated']} 条，失败 {stats['failed']} 条。")
            if stats["failed_rows"]:
                st.caption("失败项：" + "；".join(stats["failed_rows"][:5]))
    send_cols[1].caption(f"当前筛选 {len(filtered)} 条，已选择 {len(selected_rows)} 条。数据文件：{STEAM_BROWSER_COLLECTED_CSV_PATH}")


def import_steam_browser_rows_to_candidate_pool(rows: list[dict]) -> dict:
    stats = {"created": 0, "updated": 0, "failed": 0, "failed_rows": []}
    for row in rows:
        appid = clean_candidate_value(row.get("appid"))
        game_name = clean_candidate_value(row.get("game_name")) or (f"AppID {appid}" if appid else "")
        if not appid:
            stats["failed"] += 1
            stats["failed_rows"].append(game_name or "未识别 AppID")
            continue

        steam_url = clean_candidate_value(row.get("steam_url")) or steam_url_from_appid(appid)
        source_url = clean_candidate_value(row.get("source_page_url")) or steam_url
        source_title = clean_candidate_value(row.get("source_page_title"))
        suggestion = clean_candidate_value(row.get("import_suggestion"))
        next_action = "试玩 Demo" if suggestion == "待试玩" else "补项目画像"
        incoming = {
            "appid": appid,
            "game_name": game_name,
            "steam_url": steam_url,
            "steamdb_url": steamdb_app_url_from_appid(appid),
            "developer": clean_candidate_value(row.get("developer")),
            "publisher": clean_candidate_value(row.get("publisher")),
            "release_status": clean_candidate_value(row.get("release_status") or row.get("release_date")),
            "release_date": clean_candidate_value(row.get("release_date")),
            "has_demo": clean_candidate_value(row.get("has_demo")),
            "supports_schinese": clean_candidate_value(row.get("supports_schinese")),
            "genres_tags": clean_candidate_value(row.get("genres_tags")),
            "review_score": clean_candidate_value(row.get("review_score")),
            "review_count": clean_candidate_value(row.get("review_count")),
            "source": "Steam Browser Collector",
            "source_url": source_url,
            "next_action": next_action,
            "stage": "新发现",
            "priority": "未定",
            "auto_suggestion": suggestion,
            "auto_reason": clean_candidate_value(row.get("import_reason")),
            "source_notes": f"来自 Steam 浏览器采集：{source_title}" if source_title else "来自 Steam 浏览器采集",
        }

        existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid)
        if existing:
            updates = {}
            for field in [
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
                "source",
                "source_url",
                "next_action",
                "auto_suggestion",
                "auto_reason",
            ]:
                current_value = clean_candidate_value(existing.get(field))
                new_value = incoming.get(field, "")
                if field == "game_name":
                    if (
                        is_empty_or_placeholder_game_name(current_value, appid)
                        and new_value
                        and not is_empty_or_placeholder_game_name(new_value, appid)
                    ):
                        updates[field] = new_value
                    continue
                if not current_value and new_value:
                    updates[field] = new_value
            current_notes = clean_candidate_value(existing.get("source_notes"))
            incoming_notes = clean_candidate_value(incoming.get("source_notes"))
            if incoming_notes and incoming_notes not in current_notes:
                updates["source_notes"] = append_note_text(current_notes, incoming_notes)
            if updates:
                update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, appid=appid, updates=updates)
            stats["updated"] += 1
            continue

        record = CandidatePoolRecord(**incoming)
        upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
        stats["created"] += 1
    return stats


def render_steam_search_import_page() -> None:
    st.subheader("Steam 搜索批量导入")
    st.caption("用于从 Steam 搜索结果批量导入 AppID，例如 Coming Soon、Demo、热门即将推出等。默认限制数量，避免一次拉取过多噪音数据。")

    source_options = ["Coming Soon 游戏", "Demo 池", "自定义 Steam 搜索 URL"]
    config_cols = st.columns([1.2, 2.2, 1, 1])
    source_label = config_cols[0].selectbox("导入来源", source_options, key="steam_search_import_source")
    custom_url = ""
    if source_label == "自定义 Steam 搜索 URL":
        custom_url = config_cols[1].text_input(
            "Steam 搜索 URL",
            key="steam_search_import_custom_url",
            placeholder="https://store.steampowered.com/search/?filter=comingsoon",
        )
    else:
        config_cols[1].caption("使用 Steam 官方搜索分页接口，不依赖页面“显示更多”。")
    max_apps = config_cols[2].selectbox(
        "最大导入数量",
        [20, 50, 100, 200, 500],
        index=1,
        format_func=lambda value: "500（高风险，不推荐）" if int(value) == 500 else str(value),
        key="steam_search_import_max",
    )
    batch_count = config_cols[3].selectbox("每批数量", [20, 50, 100], index=1, key="steam_search_import_count")
    sleep_seconds = config_cols[3].selectbox("请求间隔", [2, 3, 5], index=0, key="steam_search_import_sleep")
    if int(max_apps) == 500:
        st.warning("500 条可能触发 Steam 访问限制，不建议连续使用。建议优先使用 50 或 100。")
    elif int(max_apps) == 200:
        st.info("200 条适合单次较大筛选，建议间隔使用。")

    action_cols = st.columns(5)
    if action_cols[0].button("抓取 AppID", key="steam_search_import_fetch", use_container_width=True):
        filter_name = ""
        category1 = None
        if source_label == "Coming Soon 游戏":
            filter_name = "comingsoon"
            category1 = "998"
        elif source_label == "Demo 池":
            category1 = "10"
        if source_label == "自定义 Steam 搜索 URL" and not custom_url.strip():
            st.warning("请先粘贴 Steam 搜索页 URL。")
        else:
            effective_max_apps = int(max_apps)
            effective_count = min(int(batch_count), effective_max_apps)
            result = fetch_steam_search_appids_with_stats(
                filter_name=filter_name,
                category1=category1,
                search_url=custom_url,
                import_source=source_label,
                count=effective_count,
                max_apps=effective_max_apps,
                sleep_seconds=float(sleep_seconds),
            )
            records = result["rows"][:effective_max_apps]
            clear_search_imports(STEAM_SEARCH_IMPORT_CSV_PATH)
            stats = save_search_import_rows(STEAM_SEARCH_IMPORT_CSV_PATH, records)
            if result["errors"]:
                st.warning("部分批次抓取失败，已保留成功结果。接口结构变化时可改用 Steam 浏览器采集或手动 AppID 导入。")
                st.caption("；".join(result["errors"][:3]))
            st.success(f"抓取完成：本次 {len(records)} 条，新增 {stats['created']} 条，更新 {stats['updated']} 条。")

    if action_cols[1].button("补全基础信息", key="steam_search_import_enrich", use_container_width=True):
        try:
            stats = enrich_search_imports_basic_info(STEAM_SEARCH_IMPORT_CSV_PATH)
        except Exception as exc:
            st.error(f"Steam 基础信息补全失败：{exc}")
        else:
            st.success(f"补全完成：请求 {stats['requested']} 个，成功 {stats['updated']} 个，失败 {stats['failed']} 个，缓存命中 {stats['cache_hit']} 个。")

    if action_cols[2].button("清空本次导入", key="steam_search_import_clear", use_container_width=True):
        stats = clear_search_imports(STEAM_SEARCH_IMPORT_CSV_PATH)
        st.success(f"已清空本次导入：移除 {stats['removed']} 条。")

    if action_cols[3].button("按 AppID 去重", key="steam_search_import_dedupe", use_container_width=True):
        stats = dedupe_search_imports_by_appid(STEAM_SEARCH_IMPORT_CSV_PATH)
        st.success(f"去重完成：before {stats['before']}，after {stats['after']}，removed {stats['removed']}。")

    action_cols[4].caption(f"数据文件：{STEAM_SEARCH_IMPORT_CSV_PATH}")

    data = apply_search_import_suggestions(load_search_imports(STEAM_SEARCH_IMPORT_CSV_PATH)).head(int(max_apps)).copy()
    filter_cols = st.columns(6)
    filtered = filter_search_imports(
        data,
        demo_only=filter_cols[0].checkbox("只看有 Demo", key="steam_search_filter_demo"),
        unreleased_only=filter_cols[1].checkbox("只看未发售 / TBA", key="steam_search_filter_unreleased"),
        self_published_only=filter_cols[2].checkbox("只看自发行", key="steam_search_filter_self"),
        schinese_only=filter_cols[3].checkbox("只看支持简中", key="steam_search_filter_schinese"),
        observation_only=filter_cols[4].checkbox("只看候选池观察 / 待试玩", key="steam_search_filter_observation"),
        exclude_reference=filter_cols[5].checkbox("排除竞品参考", key="steam_search_filter_reference"),
    )

    selected_total = int(data["selected"].map(lambda value: str(value).strip().casefold() in {"1", "true", "yes", "y"} or str(value).strip() in {"是", "有"}).sum())
    stat_cols = st.columns(5)
    stat_cols[0].metric("本次抓取数量", len(data))
    stat_cols[1].metric("去重后数量", data["appid"].nunique() if not data.empty else 0)
    stat_cols[2].metric("当前筛选数量", len(filtered))
    stat_cols[3].metric("已选择数量", selected_total)
    stat_cols[4].caption(f"数据文件：{STEAM_SEARCH_IMPORT_CSV_PATH}")

    if filtered.empty:
        st.info("暂无 Steam 搜索导入记录。请先选择来源并抓取 AppID。")
        return

    select_cols = st.columns(6)
    selection_actions = [
        ("全选当前筛选结果", "select_visible"),
        ("全选有 Demo", "select_demo"),
        ("全选有 Demo + 自发行", "select_demo_self"),
        ("全选未上线 + 有 Demo", "select_unreleased_demo"),
        ("清空当前选择", "clear_visible"),
        ("反选当前筛选结果", "invert_visible"),
    ]
    for index, (label, mode) in enumerate(selection_actions):
        if select_cols[index].button(label, key=f"steam_search_bulk_select_{mode}", use_container_width=True):
            bulk_update_search_import_selection(STEAM_SEARCH_IMPORT_CSV_PATH, filtered, mode)
            st.session_state["steam_search_import_editor_version"] = int(st.session_state.get("steam_search_import_editor_version", 0)) + 1
            data = apply_search_import_suggestions(load_search_imports(STEAM_SEARCH_IMPORT_CSV_PATH)).head(int(max_apps)).copy()
            filtered = filter_search_imports(
                data,
                demo_only=st.session_state.get("steam_search_filter_demo", False),
                unreleased_only=st.session_state.get("steam_search_filter_unreleased", False),
                self_published_only=st.session_state.get("steam_search_filter_self", False),
                schinese_only=st.session_state.get("steam_search_filter_schinese", False),
                observation_only=st.session_state.get("steam_search_filter_observation", False),
                exclude_reference=st.session_state.get("steam_search_filter_reference", False),
            )

    show_source_url = st.checkbox("显示来源页面列", value=False, key="steam_search_show_source_url")
    display = search_import_display_data(filtered)
    if not show_source_url and "来源页面" in display.columns:
        display = display.drop(columns=["来源页面"])
    column_config = {
        "Steam 链接": st.column_config.LinkColumn("Steam 链接", display_text="打开 Steam"),
    }
    if "来源页面" in display.columns:
        column_config["来源页面"] = st.column_config.LinkColumn("来源页面", display_text="来源页面")
    edited = st.data_editor(
        display,
        key=f"steam_search_import_editor_{st.session_state.get('steam_search_import_editor_version', 0)}",
        use_container_width=True,
        hide_index=True,
        disabled=[column for column in display.columns if column != "是否选择"],
        column_config=column_config,
    )
    selected_display = edited.loc[edited["是否选择"].astype(bool)].copy() if "是否选择" in edited.columns else pd.DataFrame()
    selected_appids = set(selected_display["AppID"].astype(str).str.strip()) if not selected_display.empty else set()
    visible_appids = filtered["appid"].astype(str).str.strip().tolist()
    update_search_import_selection(STEAM_SEARCH_IMPORT_CSV_PATH, visible_appids, list(selected_appids))
    selected_rows = filtered.loc[filtered["appid"].astype(str).str.strip().isin(selected_appids)].copy()

    send_cols = st.columns([1, 3])
    if send_cols[0].button("发送选中项到候选池", key="steam_search_send_candidates", use_container_width=True):
        if selected_rows.empty:
            st.warning("请先选择要发送的项目。")
        else:
            stats = import_steam_search_rows_to_candidate_pool(selected_rows.to_dict("records"))
            st.success(f"发送完成：新增 {stats['created']} 条，补空字段 {stats['updated']} 条，失败 {stats['failed']} 条。")
            if stats["failed_rows"]:
                st.caption("失败项：" + "；".join(stats["failed_rows"][:5]))
    send_cols[1].caption(f"当前筛选 {len(filtered)} 条，已选择 {len(selected_rows)} 条。")


def import_steam_search_rows_to_candidate_pool(rows: list[dict]) -> dict:
    stats = {"created": 0, "updated": 0, "failed": 0, "failed_rows": []}
    for row in rows:
        appid = clean_candidate_value(row.get("appid"))
        game_name = clean_candidate_value(row.get("game_name")) or (f"AppID {appid}" if appid else "")
        if not appid:
            stats["failed"] += 1
            stats["failed_rows"].append(game_name or "未识别 AppID")
            continue

        steam_url = clean_candidate_value(row.get("steam_url")) or steam_url_from_appid(appid)
        source_url = clean_candidate_value(row.get("source_page_url")) or steam_url
        import_source = clean_candidate_value(row.get("import_source")) or "Steam 搜索批量导入"
        suggestion = clean_candidate_value(row.get("import_suggestion"))
        next_action = "试玩 Demo" if suggestion == "待试玩" else "补项目画像"
        incoming = {
            "appid": appid,
            "game_name": game_name,
            "steam_url": steam_url,
            "steamdb_url": steamdb_app_url_from_appid(appid),
            "developer": clean_candidate_value(row.get("developer")),
            "publisher": clean_candidate_value(row.get("publisher")),
            "release_status": clean_candidate_value(row.get("release_status") or row.get("release_date")),
            "release_date": clean_candidate_value(row.get("release_date")),
            "has_demo": clean_candidate_value(row.get("has_demo")),
            "supports_schinese": clean_candidate_value(row.get("supports_schinese")),
            "genres_tags": clean_candidate_value(row.get("genres_tags")),
            "review_score": clean_candidate_value(row.get("review_score")),
            "review_count": clean_candidate_value(row.get("review_count")),
            "source": "Steam Search Import",
            "source_url": source_url,
            "next_action": next_action,
            "stage": "新发现",
            "priority": "未定",
            "auto_suggestion": suggestion,
            "auto_reason": clean_candidate_value(row.get("import_reason")),
            "source_notes": f"来自 Steam 搜索批量导入：{import_source}",
        }

        existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid)
        if existing:
            updates = {}
            for field in [
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
                "source",
                "source_url",
                "next_action",
                "auto_suggestion",
                "auto_reason",
            ]:
                current_value = clean_candidate_value(existing.get(field))
                new_value = incoming.get(field, "")
                if field == "game_name":
                    if (
                        is_empty_or_placeholder_game_name(current_value, appid)
                        and new_value
                        and not is_empty_or_placeholder_game_name(new_value, appid)
                    ):
                        updates[field] = new_value
                    continue
                if not current_value and new_value:
                    updates[field] = new_value
            current_notes = clean_candidate_value(existing.get("source_notes"))
            incoming_notes = clean_candidate_value(incoming.get("source_notes"))
            if incoming_notes and incoming_notes not in current_notes:
                updates["source_notes"] = append_note_text(current_notes, incoming_notes)
            if updates:
                update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, appid=appid, updates=updates)
            stats["updated"] += 1
            continue

        record = CandidatePoolRecord(**incoming)
        upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
        stats["created"] += 1
    return stats


def render_new_store_monitor_page() -> None:
    st.subheader("新上架监控")
    st.caption("抓取 SteamDB Recent App Events 中的 New on store: Game；第一版只做近期巡检，不做 Coming Soon / TBA 存量池。")

    action_cols = st.columns(3)
    if action_cols[0].button("抓取最近新上架", key="new_store_fetch_recent", use_container_width=True):
        result = fetch_recent_new_store_games()
        if not result.success:
            st.error(result.message)
        else:
            stats = save_new_store_events(NEW_STORE_EVENTS_CSV_PATH, result.rows)
            st.success(f"{result.message} 新增 {stats['created']} 条，当前共 {stats['total']} 条。")
    if action_cols[1].button("补全基础信息", key="new_store_enrich_basic", use_container_width=True):
        try:
            stats = enrich_new_store_events_basic_info(NEW_STORE_EVENTS_CSV_PATH)
        except Exception as exc:
            st.error(f"新上架基础信息补全失败：{exc}")
        else:
            st.success(f"补全完成：请求 {stats['requested']} 个，成功 {stats['updated']} 个，失败 {stats['failed']} 个。")
    action_cols[2].caption(f"数据文件：{NEW_STORE_EVENTS_CSV_PATH}")

    data = apply_monitor_suggestions(load_new_store_events(NEW_STORE_EVENTS_CSV_PATH))
    filter_cols = st.columns(5)
    filtered = filter_new_store_events(
        data,
        self_published_only=filter_cols[0].checkbox("只看自发行", key="new_store_filter_self"),
        unreleased_only=filter_cols[1].checkbox("只看未发售/TBA", key="new_store_filter_unreleased"),
        demo_only=filter_cols[2].checkbox("只看有 Demo", key="new_store_filter_demo"),
        schinese_only=filter_cols[3].checkbox("只看支持简中", key="new_store_filter_schinese"),
        observation_only=filter_cols[4].checkbox("只看候选池观察", key="new_store_filter_observation"),
    )

    if filtered.empty:
        st.info("暂无新上架记录。点击“抓取最近新上架”开始巡检。")
        return

    display = new_store_events_display_data(filtered)
    edited = st.data_editor(
        display,
        key="new_store_events_editor",
        use_container_width=True,
        hide_index=True,
        disabled=[column for column in display.columns if column != "是否选择"],
    )
    selected_display = edited.loc[edited["是否选择"].astype(bool)].copy() if "是否选择" in edited.columns else pd.DataFrame()
    selected_appids = set(selected_display["AppID"].astype(str).str.strip()) if not selected_display.empty else set()
    selected_rows = filtered.loc[filtered["appid"].astype(str).str.strip().isin(selected_appids)].copy()

    send_cols = st.columns([1, 3])
    if send_cols[0].button("发送选中项到候选池", key="new_store_send_candidates", use_container_width=True):
        if selected_rows.empty:
            st.warning("请先在表格中勾选要发送的项目。")
        else:
            stats = import_new_store_rows_to_candidate_pool(selected_rows.to_dict("records"))
            st.success(f"发送完成：新增 {stats['created']} 条，补全 {stats['updated']} 条，失败 {stats['failed']} 条。")
            if stats["failed_rows"]:
                st.caption("失败项：" + "；".join(stats["failed_rows"][:5]))
    send_cols[1].caption(f"当前筛选 {len(filtered)} 条，已选择 {len(selected_rows)} 条。")


def import_new_store_rows_to_candidate_pool(rows: list[dict]) -> dict:
    stats = {"created": 0, "updated": 0, "failed": 0, "failed_rows": []}
    for row in rows:
        appid = clean_candidate_value(row.get("appid"))
        game_name = clean_candidate_value(row.get("name")) or (f"AppID {appid}" if appid else "")
        if not appid:
            stats["failed"] += 1
            stats["failed_rows"].append(game_name or "未识别 AppID")
            continue
        steam_url = clean_candidate_value(row.get("steam_url")) or steam_url_from_appid(appid)
        steamdb_url = clean_candidate_value(row.get("steamdb_url")) or steamdb_app_url_from_appid(appid)
        incoming = {
            "appid": appid,
            "game_name": game_name,
            "steam_url": steam_url,
            "steamdb_url": steamdb_url,
            "developer": clean_candidate_value(row.get("developer")),
            "publisher": clean_candidate_value(row.get("publisher")),
            "release_status": clean_candidate_value(row.get("release_status") or row.get("release_date")),
            "release_date": clean_candidate_value(row.get("release_date")),
            "has_demo": clean_candidate_value(row.get("has_demo")),
            "supports_schinese": clean_candidate_value(row.get("supports_schinese")),
            "genres_tags": clean_candidate_value(row.get("genres_tags")),
            "source": "SteamDB New Store",
            "source_url": steamdb_url,
            "next_action": "补项目画像",
            "stage": "新发现",
            "priority": "未定",
            "auto_suggestion": clean_candidate_value(row.get("monitor_suggestion")),
            "auto_reason": clean_candidate_value(row.get("monitor_reason")),
            "source_notes": "来自 SteamDB 新上架监控",
        }
        existing = find_candidate_by_appid(CANDIDATE_POOL_CSV_PATH, appid)
        if existing:
            updates = {}
            for field in [
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
                "source",
                "source_url",
                "next_action",
                "auto_suggestion",
                "auto_reason",
                "source_notes",
            ]:
                if not clean_candidate_value(existing.get(field)) and incoming.get(field):
                    updates[field] = incoming[field]
            if updates:
                update_candidate_pool_fields(CANDIDATE_POOL_CSV_PATH, appid=appid, updates=updates)
            stats["updated"] += 1
            continue
        record = CandidatePoolRecord(
            appid=incoming["appid"],
            game_name=incoming["game_name"],
            steam_url=incoming["steam_url"],
            steamdb_url=incoming["steamdb_url"],
            developer=incoming["developer"],
            publisher=incoming["publisher"],
            release_status=incoming["release_status"],
            release_date=incoming["release_date"],
            has_demo=incoming["has_demo"],
            supports_schinese=incoming["supports_schinese"],
            genres_tags=incoming["genres_tags"],
            source=incoming["source"],
            source_url=incoming["source_url"],
            next_action=incoming["next_action"],
            stage=incoming["stage"],
            priority=incoming["priority"],
            auto_suggestion=incoming["auto_suggestion"],
            auto_reason=incoming["auto_reason"],
            source_notes=incoming["source_notes"],
        )
        upsert_candidate_pool_record(record, CANDIDATE_POOL_CSV_PATH)
        stats["created"] += 1
    return stats


def send_steamdb_row_to_profile(row: pd.Series) -> None:
    set_profile_prefill_from_mapping(row.to_dict(), source_context=str(row.get("source_page", "") or "SteamDB 观察"))
    st.session_state["pending_home_target"] = "profile"
    st.success("已发送到一键项目画像。切换到该 Tab 后点击生成项目画像草稿。")
    st.rerun()


def send_steamdb_row_to_search_center(row: pd.Series) -> None:
    appid = str(row.get("appid", "") or "").strip()
    game_name = str(row.get("game_name", "") or "").strip() or (f"AppID {appid}" if appid else "")
    steam_url = str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    source_page = str(row.get("source_page", "") or "").strip()
    note = str(row.get("note", "") or "").strip()
    search_values = {
        "game_name": game_name,
        "steam_url": steam_url,
        "short_description": note,
        "tags": source_page,
        "core_keywords": ", ".join(value for value in [game_name, appid, source_page] if value),
        "theme_keywords": source_page,
        "english_keywords": "",
        "reference_games": "",
        "developer": "",
        "publisher": "",
    }
    apply_search_center_values(search_values)
    try:
        platforms = load_search_platforms(SEARCH_PLATFORM_CONFIG_PATH)
        navigation_table = build_platform_navigation(
            SearchCenterInput(**search_values),
            platforms,
            limit=int(st.session_state.get("search_keyword_limit", 20)),
        )
    except Exception as exc:
        st.error(f"搜索中心生成失败：{exc}")
        return
    st.session_state["search_navigation_table"] = navigation_table
    st.success("已发送到搜索中心并生成搜索入口。")


def save_steamdb_row_as_project(row: pd.Series) -> None:
    appid = str(row.get("appid", "") or "").strip()
    game_name = str(row.get("game_name", "") or "").strip() or (f"AppID {appid}" if appid else "SteamDB 未命名项目")
    project = ProjectCard(
        game_name=game_name,
        steam_url=str(row.get("steam_url", "") or "").strip() or steam_url_from_appid(appid),
        appid=appid,
        release_status=str(row.get("release_date", "") or "").strip(),
        first_impression="来自 SteamDB 发现工作台观察记录。",
        china_publishing_opportunity="待项目画像和人工复核。",
        risks=str(row.get("note", "") or "").strip(),
        next_action=str(row.get("next_action", "") or "").strip() or "生成项目画像",
    )
    save_project_to_csv(project, CSV_PATH)
    st.success(f"已保存为快速项目记录：{game_name}")


def render_history_records() -> None:
    """折叠展示历史项目记录和 Excel 导出按钮。"""
    all_projects = load_projects(CSV_PATH, include_deleted=True)
    visible_count = len(load_projects(CSV_PATH, include_deleted=False))

    with st.expander(f"历史项目记录（共 {visible_count} 条）", expanded=False):
        st.caption("这里展示已经保存为项目记录的项目，不等同于查查搜索历史。如果只是查过但没有保存，请到首页“查查 / 最近查过”查看。")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            game_name_query = st.text_input("按游戏名搜索")
        with filter_col2:
            appid_query = st.text_input("按 AppID 搜索")
        with filter_col3:
            release_options = ["全部"] + sorted(
                [status for status in all_projects["release_status"].dropna().unique().tolist() if status]
            )
            release_status = st.selectbox("按发售状态筛选", release_options)

        show_deleted = st.checkbox("显示已删除记录")
        show_more = st.checkbox("查看完整历史表（超过最近 10 条）")
        show_full = st.checkbox("显示完整字段")
        source_projects = load_projects(CSV_PATH, include_deleted=show_deleted)
        filtered_projects = filter_projects(source_projects, game_name_query, appid_query, release_status)
        displayed_projects = filtered_projects if show_more else filtered_projects.tail(10)
        history_data = get_history_display_data(displayed_projects, show_full=show_full)

        if history_data.empty:
            st.info("暂无项目记录")
        else:
            if not show_more:
                st.caption("默认显示最近 10 条。勾选“查看完整历史表”可显示更多记录。")
            st.dataframe(history_data, use_container_width=True)
            render_project_delete_actions(displayed_projects)

        if st.button("导出可读 Excel"):
            excel_path = export_projects_to_excel(
                CSV_PATH,
                EXCEL_REPORT_PATH,
                COMPETITOR_CSV_PATH,
                CANDIDATE_CSV_PATH,
                STEAMDB_WATCH_NOTE_CSV_PATH,
                STEAMDB_TEMPLATE_CSV_PATH,
                DAILY_WATCH_CSV_PATH,
                HOME_SNAPSHOT_CSV_PATH,
                STEAM_HOME_FEED_CACHE_PATH,
                STEAM_APPDETAILS_CACHE_PATH,
                STEAM_REVIEW_STATS_CACHE_PATH,
                EXTERNAL_INTEL_CSV_PATH,
            )
            st.success(f"Excel 已导出：{excel_path}")
        if st.button("导出候选池 Excel", key="history_export_candidate_pool"):
            export_path = export_candidate_pool_to_excel(CANDIDATE_POOL_CSV_PATH, BASE_DIR / "reports" / "excel")
            st.success(f"候选池 Excel 已导出：{export_path}")


def render_project_delete_actions(filtered_projects) -> None:
    """渲染项目快捷操作、软删除和恢复操作。"""
    options = build_project_action_options(filtered_projects)
    if not options:
        return

    selected_label = st.selectbox("选择项目进行快捷操作 / 删除 / 恢复", [option["label"] for option in options])
    selected_option = next(option for option in options if option["label"] == selected_label)
    selected_row = load_project_row(selected_option["record_id"])
    if selected_row is not None:
        render_history_project_quick_actions(selected_row)

    delete_col, restore_col = st.columns(2)
    with delete_col:
        if st.button("标记删除"):
            update_project_deleted(CSV_PATH, selected_option["record_id"], True)
            st.success("项目已标记删除。")
    with restore_col:
        if st.button("恢复记录"):
            update_project_deleted(CSV_PATH, selected_option["record_id"], False)
            st.success("项目已恢复。")


def render_history_project_quick_actions(row: pd.Series) -> None:
    data = row.to_dict()
    appid = str(data.get("appid", "") or "").strip()
    steam_url = str(data.get("steam_url", "") or "").strip() or steam_url_from_appid(appid)
    steamdb_url = steamdb_app_url_from_appid(appid)
    action_cols = st.columns(6)
    if action_cols[0].button("发送到查查", key="history_send_chacha", use_container_width=True):
        set_lookup_prefill_from_candidate(data, source="历史项目记录")
        st.success("已发送到查查，请回到工作台查看。")
    if action_cols[1].button("发送到项目画像", key="history_send_profile", use_container_width=True):
        set_profile_prefill_from_mapping(data, source_context="历史项目记录")
        st.session_state["pending_home_target"] = "profile"
        st.success("已发送到项目画像，请打开项目画像页。")
        st.rerun()
    with action_cols[2]:
        if steam_url:
            st.link_button("打开 Steam", steam_url, use_container_width=True)
    with action_cols[3]:
        if steamdb_url:
            st.link_button("打开 SteamDB", steamdb_url, use_container_width=True)
    with action_cols[4]:
        st.text_input("复制 Steam 链接", value=steam_url, key=f"history_copy_steam_url_{data.get('record_id', '')}")
    with action_cols[5]:
        st.text_input("复制 AppID", value=appid, key=f"history_copy_appid_{data.get('record_id', '')}")


def render_docs_status_page() -> None:
    """渲染文档与状态入口。"""
    st.subheader("文档与状态")
    st.markdown(
        """
- 当前版本：V0.7.4 高频入口与 Steam 批量导入收口版
- 数据文件：`data/projects.csv`、`data/candidate_pool.csv`、`data/steam_browser_collected.csv`、`data/steam_search_imports.csv`、`data/competitors.csv`、`data/competitor_candidates.csv`、`data/external_intel.csv`
- 图片目录：`data/snapshots/`
- 报告目录：`reports/markdown/`、`reports/txt/`、`reports/excel/`、`reports/profile/`
- 搜索中心导出目录：`exports/`
- 说明文档：`README.md`、`CHANGELOG.md`、`docs/PROJECT_STATUS.md`、`docs/NEXT_STEPS.md`
"""
    )
    with st.expander("开发者信息 / 缓存与调试路径", expanded=False):
        st.markdown(
            """
- Steam 浏览器采集：`data/steam_browser_collected.csv`、`data/browser_profiles/steam_browser_collector/`
- Steam 搜索批量导入：`data/steam_search_imports.csv`
- SteamDB 与观察记录：`data/steamdb_watch_notes.csv`、`data/steamdb_link_templates.csv`、`data/new_store_events.csv`
- 首页与观察缓存：`data/daily_watch_notes.csv`、`data/home_snapshots.csv`、`data/cache/home_feed_cache.json`
- Steam 缓存：`data/cache/steam_home_feed_cache.json`、`data/cache/steam_appdetails_cache.json`、`data/cache/steam_review_stats_cache.json`、`data/cache/steam_images_cache.json`
- Steam 动态缓存：`data/cache/steam_news/`
- Steam 评论预览缓存：`data/cache/steam_reviews_preview/`
"""
        )


def main() -> None:
    """启动 Streamlit 主页面。"""
    ensure_csv_exists(CSV_PATH)
    ensure_competitor_csv_exists(COMPETITOR_CSV_PATH)
    ensure_candidate_csv_exists(CANDIDATE_CSV_PATH)
    ensure_candidate_pool_csv_exists(CANDIDATE_POOL_CSV_PATH)
    ensure_template_csv_exists(STEAMDB_TEMPLATE_CSV_PATH)
    ensure_watch_note_csv_exists(STEAMDB_WATCH_NOTE_CSV_PATH)
    load_new_store_events(NEW_STORE_EVENTS_CSV_PATH)
    load_search_imports(STEAM_SEARCH_IMPORT_CSV_PATH)
    ensure_daily_watch_csv_exists(DAILY_WATCH_CSV_PATH)
    ensure_home_snapshot_csv_exists(HOME_SNAPSHOT_CSV_PATH)
    ensure_external_intel_csv_exists(EXTERNAL_INTEL_CSV_PATH)
    HOME_SNAPSHOT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    st.set_page_config(page_title="Steam 项目初筛助手", layout="wide")

    st.sidebar.title("Steam 项目初筛助手")
    st.sidebar.info("当前版本：V0.7.4 高频入口与 Steam 批量导入收口版")
    st.sidebar.warning(
        "退出提醒\n\n"
        "- 关闭浏览器标签页不会关闭后台服务。\n"
        "- 正常退出请关闭启动窗口，或双击 停止_项目初筛助手.bat。\n"
        "- 如果下次打不开，先运行 停止_项目初筛助手.bat。"
    )
    if st.sidebar.button("复制停止命令"):
        st.sidebar.code("停止_项目初筛助手.bat", language="bat")

    st.title("Steam 项目初筛助手")
    st.caption("当前版本支持查查前置、Steam 浏览器采集、Steam 搜索批量导入、SteamDB 手动导入、候选池和基础信息补全。")

    home_tab, chacha_tab, steam_browser_tab, steam_search_tab, steamdb_import_tab, competitor_tab, profile_tab, history_tab, docs_tab = st.tabs(
        ["首页 / 项目发现 Feed", "查查", "Steam 浏览器采集", "Steam 搜索批量导入", "SteamDB 导入", "竞品与候选", "一键项目画像", "历史与导出", "文档与状态"]
    )

    with home_tab:
        render_home_dashboard_page()
    with chacha_tab:
        render_chacha_page()
    with steam_browser_tab:
        render_steam_browser_collector_page()
    with steam_search_tab:
        render_steam_search_import_page()
    with steamdb_import_tab:
        render_steamdb_import_page()
    with competitor_tab:
        render_competitor_candidate_page()
    with profile_tab:
        render_profile_draft_page()
    with history_tab:
        render_history_records()
    with docs_tab:
        render_docs_status_page()


if __name__ == "__main__":
    main()
