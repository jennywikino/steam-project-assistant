import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from modules.company_dossier import (
    build_company_dossier_markdown_section,
    filter_company_dossiers_for_project,
    load_company_dossiers,
    parse_company_names,
)
from modules.external_intel import (
    build_external_intel_markdown_section,
    filter_external_intel,
    load_external_intel,
)
from modules.market_data import (
    build_market_data_markdown_section,
    filter_market_data,
    load_market_data,
)
from modules.genre_signal_extractor import GenreSignals, extract_genre_signals, genre_signals_to_dict


PLACEHOLDER = "未获取/需人工确认"
FINAL_LIMITATION_TEXT = "基于公开信息生成，需试玩复核。"

TRACK_RULES = {
    "roguelite": "Roguelite/Roguelike 赛道竞争：需确认局外成长、随机构筑和单局反馈是否足够强。",
    "roguelike": "Roguelite/Roguelike 赛道竞争：需确认随机性、构筑深度和失败复玩动机。",
    "strategy": "策略赛道竞争：需确认决策密度、关卡变化和长期目标是否能支撑留存。",
    "simulation": "模拟经营赛道竞争：需确认系统深度、成长反馈和题材差异化。",
    "metroidvania": "类银河恶魔城赛道竞争：需确认地图探索、动作手感和能力解锁节奏。",
    "action": "动作赛道竞争：需确认打击反馈、操作上限和前 10 分钟爽点。",
    "survival": "生存赛道竞争：需确认资源压力、建造/探索循环和多人或社区传播点。",
}

LOW_PRIORITY_TAGS = {"clicker", "idler", "incremental"}


@dataclass
class ProjectProfile:
    basic_info: dict[str, str]
    core_gameplay_judgment: str
    data_quality_level: str = "low"
    quick_summary: dict[str, Any] = field(default_factory=dict)
    selling_points: list[str] = field(default_factory=list)
    competition_points: list[str] = field(default_factory=list)
    competitor_anchors: list[str] = field(default_factory=list)
    competition_dimensions: list[str] = field(default_factory=list)
    china_opportunities: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    next_action: str = ""
    backup_next_action: str = ""
    manual_checklist: list[str] = field(default_factory=list)
    search_keywords: list[str] = field(default_factory=list)
    source_limitations: list[str] = field(default_factory=list)
    raw_store_info: dict[str, Any] = field(default_factory=dict)
    genre_signals: dict[str, Any] = field(default_factory=dict)
    external_title_clues: list[str] = field(default_factory=list)


def generate_project_profile(
    store_info: dict,
    chinese_name: str = "",
    user_keywords: str = "",
    user_has_demo: str = "",
    user_demo_played: str = "",
    external_title_clues: str = "",
) -> ProjectProfile:
    """Generate a deterministic project profile draft from public store fields."""
    info = dict(store_info or {})
    if chinese_name.strip():
        info["name"] = chinese_name.strip()
    if user_has_demo and user_has_demo != "未确认":
        info["has_demo"] = user_has_demo

    genres = _string_list(info.get("genres"))
    tags = _string_list(info.get("tags"))
    categories = _string_list(info.get("categories"))
    all_tags = _dedupe(genres + tags + categories + _split_terms(user_keywords))
    genre_signals = extract_genre_signals(
        short_description=str(info.get("short_description", "") or ""),
        about_the_game=str(info.get("about_the_game", "") or ""),
        genres=genres,
        tags=tags,
        user_keywords=user_keywords,
        external_title_clues=external_title_clues,
    )
    info["genre_signals"] = genre_signals_to_dict(genre_signals)
    info["external_title_clues"] = external_title_clues
    description_text = " ".join(
        [
            str(info.get("short_description", "")),
            str(info.get("about_the_game", "")),
            " ".join(all_tags),
            user_keywords,
        ]
    )

    basic_info = {
        "游戏名": _value(info.get("name")),
        "AppID": _value(info.get("appid")),
        "Steam 链接": _value(info.get("steam_url")),
        "开发商": _value(info.get("developer")),
        "发行商": _value(info.get("publisher")),
        "发售状态": _value(info.get("release_status") or info.get("release_date")),
        "价格": _value(info.get("price")),
        "好评率": _value(_format_positive_rate(info.get("positive_rate"))),
        "评测数": _value(info.get("review_total")),
        "评测摘要": _value(info.get("review_score_desc") or info.get("review_stats_status")),
        "中位游玩时间": _value(_format_hours(info.get("median_playtime_hours"))),
        "平均游玩时间": _value(_format_hours(info.get("avg_playtime_hours"))),
        "是否有 Demo": _value(info.get("has_demo") or user_has_demo),
        "是否已试玩": _value(user_demo_played),
        "是否支持简中": _value(info.get("has_simplified_chinese")),
        "类型/标签": _value(", ".join(all_tags)),
        "截图数量": _value(info.get("screenshots_count")),
        "视频/Trailer 数量": _value(info.get("movies_count")),
        "成人内容提示": _value(info.get("mature_content")),
    }

    selling_points = _build_selling_points(info, all_tags, description_text, genre_signals)
    competitor_anchors = _build_competitor_anchors(genre_signals)
    competition_dimensions = _build_competition_dimensions(genre_signals)
    competition_points = competition_dimensions
    china_opportunities, opportunity_score = _build_china_opportunities(info, all_tags)
    risks = _build_risks(info, all_tags, description_text)
    data_quality_level = _assess_data_quality(info, all_tags, user_demo_played)
    next_action = _choose_next_action(info, risks, opportunity_score)
    backup_next_action = _choose_backup_next_action(info, next_action, risks, opportunity_score)
    search_keywords = build_profile_search_keywords(info, all_tags, user_keywords)
    core_judgment = _build_core_gameplay_judgment(info, all_tags, description_text, genre_signals)
    quick_summary = _build_quick_summary(
        info,
        all_tags,
        core_judgment,
        selling_points,
        competitor_anchors,
        china_opportunities,
        risks,
        next_action,
        backup_next_action,
    )

    return ProjectProfile(
        basic_info=basic_info,
        core_gameplay_judgment=core_judgment,
        data_quality_level=data_quality_level,
        quick_summary=quick_summary,
        selling_points=selling_points,
        competition_points=competition_points,
        competitor_anchors=competitor_anchors,
        competition_dimensions=competition_dimensions,
        china_opportunities=china_opportunities,
        risks=risks,
        next_action=next_action,
        backup_next_action=backup_next_action,
        manual_checklist=[
            "核心循环是否真的成立",
            "Demo 前 15 分钟是否抓人",
            "是否已有发行/区域代理",
            "开发商是否愿意合作",
            "竞品是否真正贴近",
            "中国玩家是否有兴趣",
        ],
        search_keywords=search_keywords,
        source_limitations=[
            "基于 Steam 商店公开信息和 Steam 评测样本。",
            "Steam 评测游玩时间只取 1 页样本，不代表全体玩家。",
            "标签、Demo、语言等字段可能受 Steam 页面展示和地区语言影响，需要人工复核。",
            FINAL_LIMITATION_TEXT,
        ],
        raw_store_info=info,
        genre_signals=genre_signals_to_dict(genre_signals),
        external_title_clues=[line.strip() for line in external_title_clues.splitlines() if line.strip()],
    )


def build_profile_search_keywords(store_info: dict, tags: list[str] | None = None, user_keywords: str = "") -> list[str]:
    info = store_info or {}
    game_name = str(info.get("name", "") or "").strip()
    developer = str(info.get("developer", "") or "").strip()
    publisher = str(info.get("publisher", "") or "").strip()
    keywords = []

    def add(value: str) -> None:
        clean = " ".join(str(value or "").split())
        if clean and clean.casefold() not in {item.casefold() for item in keywords}:
            keywords.append(clean)

    if game_name:
        add(game_name)
        add(f"{game_name} Steam")
        add(f"{game_name} demo")
        add(f"{game_name} gameplay")
        add(f"{game_name} review")
        add(f"{game_name} trailer")
    add(developer)
    add(publisher)
    for tag in _string_list(tags):
        add(tag)
    for keyword in _split_terms(user_keywords):
        add(keyword)
    return keywords[:24]


def _assess_data_quality(info: dict, tags: list[str], user_demo_played: str = "") -> str:
    has_name = _has_value(info.get("name")) or _has_value(info.get("game_name"))
    has_party = _has_value(info.get("developer")) or _has_value(info.get("publisher"))
    has_tags = bool(tags)
    has_media = _to_int(info.get("screenshots_count")) > 0 or _to_int(info.get("movies_count")) > 0
    has_reviews = _to_int(info.get("review_total")) >= 10
    has_demo_signal = str(info.get("has_demo", "") or "").strip() == "是"
    has_played_signal = str(user_demo_played or "").strip() == "已试玩"

    if has_name and has_party and has_tags and has_media and (has_reviews or has_demo_signal or has_played_signal):
        return "high"
    if has_name and has_party and has_tags and has_media:
        return "medium"
    if has_name and has_reviews:
        return "medium"
    return "low"


def _markdown_quick_screening(profile: ProjectProfile) -> str:
    level = profile.data_quality_level or "low"
    has_reviews = _to_int((profile.raw_store_info or {}).get("review_total")) >= 10
    if level == "low":
        return "\n".join(
            [
                "- 数据不足：缺少游戏名、类型、截图/视频等核心信息，或只有少量 Steam 字段。",
                "- 当前只能做记录，需人工验证。",
                "- 下一步动作：补商店截图、视频、Demo、评测或社区声量。",
            ]
        )

    if level == "medium":
        if has_reviews and not _has_value((profile.raw_store_info or {}).get("developer")):
            return "\n".join(
                [
                    "- 数据部分可用，需人工确认。",
                    f"- 好评率 / 评测数：{profile.basic_info.get('好评率', PLACEHOLDER)} / {profile.basic_info.get('评测数', PLACEHOLDER)}",
                    "- 商店详情可能受地区限制或页面展示影响，需打开 Steam / SteamDB 人工复核。",
                    "- 下一步动作：补开发商、发行商、商店图文和社区声量。",
                ]
            )
        return "\n".join(
            [
                f"- 类型定位：{_quick_text(profile, '游戏类型 / 赛道定位')}",
                f"- 卖点一句话：{_first_or_placeholder(profile.quick_summary.get('主卖点', []))}",
                "- 当前信息不足以判断商业潜力。",
                "- 最大风险：缺少评测/游玩时长/社区声量。",
                "- 下一步动作：先看 Trailer / Demo / B站小黑盒声量。",
            ]
        )

    lines = [
        f"- 类型定位：{_quick_text(profile, '游戏类型 / 赛道定位')}",
        f"- 卖点一句话：{_first_or_placeholder(profile.quick_summary.get('主卖点', []))}",
    ]
    if has_reviews:
        lines.extend(
            [
                f"- 好评率 / 评测数：{profile.basic_info.get('好评率', PLACEHOLDER)} / {profile.basic_info.get('评测数', PLACEHOLDER)}",
                f"- 中位 / 平均游玩：{profile.basic_info.get('中位游玩时间', PLACEHOLDER)} / {profile.basic_info.get('平均游玩时间', PLACEHOLDER)}",
            ]
        )
    else:
        lines.append("- 暂无 Steam 评测数据，无法判断口碑和游玩时长。")
    lines.extend(
        [
            f"- 最大风险：{_first_or_placeholder(profile.quick_summary.get('主要风险', []))}",
            f"- 建议下一步：{profile.next_action or PLACEHOLDER}",
        ]
    )
    return "\n".join(lines)


def profile_to_markdown(
    profile: ProjectProfile,
    external_intel_records: pd.DataFrame | None = None,
    company_dossier_records: pd.DataFrame | None = None,
    market_data_records: pd.DataFrame | None = None,
) -> str:
    game_name = profile.basic_info.get("游戏名", PLACEHOLDER)
    info = profile.raw_store_info or {}
    tags = profile.basic_info.get("类型/标签", PLACEHOLDER)
    data_quality_level = profile.data_quality_level or "low"
    data_quality_note = ""
    if data_quality_level != "high":
        data_quality_note = "\n当前信息不足，仅生成项目初筛记录，需人工验证。\n"
    quick_section = _markdown_quick_screening(profile)
    external_section = build_external_intel_markdown_section(external_intel_records)
    associated_companies = _profile_associated_companies(profile)
    company_dossier_section = build_company_dossier_markdown_section(company_dossier_records, associated_companies)
    market_data_section = build_market_data_markdown_section(market_data_records)
    quick_capture_note = str(info.get("quick_capture_note", "") or "").strip()
    source_note_section = f"\n## 3. 来源备注\n- {quick_capture_note}\n" if quick_capture_note else ""
    return f"""# {game_name} 项目画像草稿
{data_quality_note}
## 0. 快速初筛
{quick_section}

## 1. 基础信息
- 游戏名：{profile.basic_info.get("游戏名", PLACEHOLDER)}
- AppID：{profile.basic_info.get("AppID", PLACEHOLDER)}
- Steam 链接：{profile.basic_info.get("Steam 链接", PLACEHOLDER)}
- 开发商：{profile.basic_info.get("开发商", PLACEHOLDER)}
- 发行商：{profile.basic_info.get("发行商", PLACEHOLDER)}
- 发售状态：{profile.basic_info.get("发售状态", PLACEHOLDER)}
- 价格：{profile.basic_info.get("价格", PLACEHOLDER)}
- Demo：{profile.basic_info.get("是否有 Demo", PLACEHOLDER)}
- 简中：{profile.basic_info.get("是否支持简中", PLACEHOLDER)}
- 类型/标签：{tags}

## 2. 商店素材
- 截图数量：{profile.basic_info.get("截图数量", PLACEHOLDER)}
- 视频数量：{profile.basic_info.get("视频/Trailer 数量", PLACEHOLDER)}
- 短描述：{_value(info.get("short_description"))}

{source_note_section}
{external_section}
{company_dossier_section}
{market_data_section}
## 5. 人工确认项
- Demo 前 15 分钟是否抓人
- 是否已有发行/区域代理
- 核心循环是否成立
- 中文区玩家是否可能有兴趣

## 6. 信息限制
- 基于 Steam 商店公开信息和 Steam 评测样本
- 需试玩复核
"""


def profile_to_text(
    profile: ProjectProfile,
    external_intel_records: pd.DataFrame | None = None,
    company_dossier_records: pd.DataFrame | None = None,
    market_data_records: pd.DataFrame | None = None,
) -> str:
    text = re.sub(
        r"^#+\s*",
        "",
        profile_to_markdown(profile, external_intel_records, company_dossier_records, market_data_records),
        flags=re.MULTILINE,
    )
    text = text.replace("- ", "")
    return text.strip() + "\n"


def save_profile_reports(
    profile: ProjectProfile,
    report_dir: Path,
    external_intel_csv_path: Path | None = None,
    company_dossier_csv_path: Path | None = None,
    market_data_csv_path: Path | None = None,
) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    game_name = profile.basic_info.get("游戏名", "") or "未命名项目"
    filename_stem = f"{safe_filename(game_name)}_项目画像"
    markdown_path = report_dir / f"{filename_stem}.md"
    txt_path = report_dir / f"{filename_stem}.txt"
    external_intel_records = pd.DataFrame()
    if external_intel_csv_path is not None:
        external_intel_records = filter_external_intel(
            load_external_intel(external_intel_csv_path),
            appid=profile.basic_info.get("AppID", ""),
            game_name=game_name,
        )
    company_dossier_records = pd.DataFrame()
    if company_dossier_csv_path is not None:
        company_dossier_records = filter_company_dossiers_for_project(
            load_company_dossiers(company_dossier_csv_path),
            appid=profile.basic_info.get("AppID", ""),
            game_name=game_name,
        )
    market_data_records = pd.DataFrame()
    if market_data_csv_path is not None:
        market_data_records = filter_market_data(
            load_market_data(market_data_csv_path),
            appid=profile.basic_info.get("AppID", ""),
            game_name=game_name,
        )
    markdown_path.write_text(
        profile_to_markdown(profile, external_intel_records, company_dossier_records, market_data_records),
        encoding="utf-8",
    )
    txt_path.write_text(
        profile_to_text(profile, external_intel_records, company_dossier_records, market_data_records),
        encoding="utf-8",
    )
    return markdown_path, txt_path


def profile_summary_for_project(profile: ProjectProfile) -> dict[str, str]:
    """Map profile fields to the existing projects.csv schema."""
    info = profile.raw_store_info or {}
    return {
        "game_name": _empty_if_placeholder(profile.basic_info.get("游戏名")),
        "steam_url": _empty_if_placeholder(profile.basic_info.get("Steam 链接")),
        "appid": _empty_if_placeholder(profile.basic_info.get("AppID")),
        "developer": _empty_if_placeholder(profile.basic_info.get("开发商")),
        "publisher": _empty_if_placeholder(profile.basic_info.get("发行商")),
        "release_status": _empty_if_placeholder(profile.basic_info.get("发售状态")),
        "has_demo": _empty_if_placeholder(profile.basic_info.get("是否有 Demo")),
        "has_simplified_chinese": _empty_if_placeholder(profile.basic_info.get("是否支持简中")),
        "genre_tags": _empty_if_placeholder(profile.basic_info.get("类型/标签")),
        "core_loop": profile.core_gameplay_judgment,
        "first_impression": _shorten(str(info.get("short_description", "")) or "画像草稿由公开信息规则生成，需人工确认。", 500),
        "china_publishing_opportunity": "\n".join(profile.china_opportunities),
        "risks": "\n".join(profile.risks),
        "next_action": profile.next_action,
    }


def _profile_associated_companies(profile: ProjectProfile) -> list[tuple[str, str]]:
    info = profile.raw_store_info or {}
    developer_names = (
        parse_company_names(info.get("developers"))
        or parse_company_names(info.get("developer"))
        or parse_company_names(profile.basic_info.get("开发商"))
    )
    publisher_names = (
        parse_company_names(info.get("publishers"))
        or parse_company_names(info.get("publisher"))
        or parse_company_names(profile.basic_info.get("发行商"))
    )
    companies = []
    for name in developer_names:
        companies.append(("developer", name))
    for name in publisher_names:
        companies.append(("publisher", name))
    return companies


def _build_core_gameplay_judgment(
    info: dict,
    tags: list[str],
    description_text: str,
    genre_signals: GenreSignals,
) -> str:
    if genre_signals.primary_type != "类型待定":
        return f"{genre_signals.primary_type}；{genre_signals.core_loop}"
    if len(_visible_text(description_text)) < 40 and not tags:
        return "类型和核心循环待补充。"

    genre_hint = ", ".join(tags[:4]) if tags else "未获取明确类型"
    loop_hint = _infer_loop(tags, description_text)
    if loop_hint:
        return f"{genre_hint}；{loop_hint}"
    return f"{genre_hint}；核心循环待试玩"


def _infer_loop(tags: list[str], description_text: str) -> str:
    text = description_text.casefold()
    checks = [
        (["roguelite", "roguelike"], "反复挑战、构筑成长并在随机内容中优化策略"),
        (["strategy", "tactics"], "围绕资源、阵容或战术选择做长期决策"),
        (["simulation", "management"], "经营资源、扩张系统并持续优化效率"),
        (["metroidvania"], "探索地图、获得能力并解锁新区域"),
        (["survival"], "收集资源、抵御压力并扩展生存空间"),
        (["action"], "通过操作、战斗反馈和关卡推进形成即时挑战"),
        (["puzzle"], "理解规则、解谜推进并逐步提升难度"),
    ]
    haystack = " ".join(tags).casefold() + " " + text
    for needles, loop in checks:
        if any(needle in haystack for needle in needles):
            return loop
    return ""


def _build_selling_points(
    info: dict,
    tags: list[str],
    description_text: str,
    genre_signals: GenreSignals,
) -> list[str]:
    points = []
    if "卡牌肉鸽" in genre_signals.primary_type:
        points.append("卡牌肉鸽方向清晰")
        points.append("卡组构筑带来复玩")
        points.append("适合用战斗片段传播")
        return points
    if tags:
        points.append(f"标签集中：{', '.join(tags[:4])}")
    if _infer_loop(tags, description_text):
        points.append(f"核心循环：{_infer_loop(tags, description_text)}")
    short_description = str(info.get("short_description", "") or "").strip()
    if short_description:
        points.append(f"短描述可提炼：{_shorten(short_description, 80)}")
    screenshots_count = _to_int(info.get("screenshots_count"))
    movies_count = _to_int(info.get("movies_count"))
    if screenshots_count >= 5:
        points.append(f"{screenshots_count} 张截图可看美术")
    if movies_count >= 1:
        points.append(f"{movies_count} 个视频可看钩子")
    if not points:
        points.append("卖点待从试玩补充")
    return points[:5]


def _build_competitor_anchors(genre_signals: GenreSignals) -> list[str]:
    anchors = [
        anchor
        for anchor in genre_signals.competitor_anchors
        if anchor not in {"同核心类型 Steam 候选", "价格和内容量参考", "同类玩法完成度竞争"}
    ]
    return anchors[:3] if anchors else ["待从候选池确认"]


def _build_competition_dimensions(genre_signals: GenreSignals) -> list[str]:
    dimensions = [
        dimension
        for dimension in genre_signals.comparison_dimensions
        if dimension not in {"待从候选池确认"}
    ]
    return dimensions[:8] if dimensions else ["价格和内容量", "核心循环完成度", "美术识别度"]


def _build_china_opportunities(info: dict, tags: list[str]) -> tuple[list[str], int]:
    opportunities = []
    score = 0
    has_chinese = str(info.get("has_simplified_chinese", "") or "").strip()
    has_demo = str(info.get("has_demo", "") or "").strip()

    if has_chinese == "否":
        opportunities.append("暂未发现简中支持，需人工确认中文区进入门槛。")
    elif has_chinese == "是":
        score += 1
        opportunities.append("已显示支持简中，可检查本地化质量和中文社区反馈。")
    else:
        opportunities.append("简中支持状态未获取，需要人工确认。")
    if has_demo == "是":
        score += 1
        opportunities.append("已有 Demo，可先用试玩反馈验证中文区兴趣。")
    else:
        opportunities.append("Demo 状态未确认或暂未发现，需确认是否有试玩版本。")
    if _has_any(tags, ["roguelite", "roguelike", "strategy", "simulation", "metroidvania", "survival", "action"]):
        opportunities.append("类型标签适合后续用 B站/小黑盒/Steam 中文评论验证受众。")
    return opportunities, score


def _build_risks(info: dict, tags: list[str], description_text: str) -> list[str]:
    risks = []
    if len(_visible_text(description_text)) < 120:
        risks.append("商店页描述过短或过泛，卖点表达不足。")
    if len(tags) < 3:
        risks.append("标签/类型信息不足，赛道判断需要人工确认。")
    if str(info.get("has_demo", "") or "").strip() != "是":
        risks.append("未确认有 Demo，试玩验证和转化判断会变慢。")
    developer = str(info.get("developer", "") or "").strip()
    publisher = str(info.get("publisher", "") or "").strip()
    if publisher and developer and publisher.casefold() != developer.casefold():
        risks.append("已有发行商，合作空间和区域权利需要进一步确认。")
    if str(info.get("has_simplified_chinese", "") or "").strip() == "否":
        risks.append("缺少简中，中文区转化存在门槛，同时也需要评估本地化成本。")
    if _has_any(tags, ["horror", "visual novel", "dating sim", "nsfw"]):
        risks.append("题材在中国区可能偏窄，需要先看社区接受度和内容合规风险。")
    if _to_int(info.get("screenshots_count")) < 4:
        risks.append("截图数量偏少，视觉卖点和传播判断不充分。")
    if _to_int(info.get("movies_count")) < 1:
        risks.append("视频/Trailer 不足，难以判断前 15 秒传播钩子。")
    if _has_any(tags, LOW_PRIORITY_TAGS):
        risks.append("Clicker/Idler/Incremental 类型与当前筛选偏好不匹配，除非数据很强，否则降权。")
    risks.append("当前信息仍需试玩或社区声量复核，不能只凭商店标签判断。")
    return _dedupe(risks)


def _choose_next_action(info: dict, risks: list[str], opportunity_score: int) -> str:
    if str(info.get("has_demo", "") or "").strip() == "是":
        return "先试玩 Demo"
    if _to_int(info.get("movies_count")) > 0:
        return "先看视频/社区声量"
    if str(info.get("has_demo", "") or "").strip() != "是":
        return "先确认是否有 Demo；如果没有 Demo，先看 Trailer / 社区声量"
    if not str(info.get("publisher", "") or "").strip():
        return "先查开发商背景"
    if len(risks) >= 5:
        return "暂缓观察"
    return "先查竞品"


def _choose_backup_next_action(info: dict, next_action: str, risks: list[str], opportunity_score: int) -> str:
    candidates = [
        "先查竞品",
        "先查开发商背景",
        "先看视频/社区声量",
        "先确认是否有 Demo；如果没有 Demo，先看 Trailer / 社区声量",
        "暂缓观察",
        "暂不跟进",
    ]
    if str(info.get("has_demo", "") or "").strip() == "是":
        candidates.insert(0, "先看视频/社区声量")
    if opportunity_score >= 2:
        candidates.insert(0, "先查开发商背景")
    if len(risks) >= 5:
        candidates.insert(0, "先查竞品")
    for candidate in candidates:
        if candidate != next_action:
            return candidate
    return "先查竞品"


def _build_quick_summary(
    info: dict,
    tags: list[str],
    core_judgment: str,
    selling_points: list[str],
    competition_points: list[str],
    china_opportunities: list[str],
    risks: list[str],
    next_action: str,
    backup_next_action: str,
) -> dict[str, Any]:
    return {
        "游戏类型 / 赛道定位": _compact_type(genre_signals_from_info(info, tags), tags),
        "核心循环": _compact_core_loop(tags, core_judgment),
        "竞品锚点 / 相似参考": _compact_items(competition_points, 3, 35),
        "主卖点": _compact_items(selling_points, 3, 24),
        "中国区机会": _compact_items(china_opportunities, 3, 30),
        "主要风险": _compact_items(risks, 3, 30),
        "建议下一步": next_action,
        "备用建议": backup_next_action,
    }


def _infer_type(tags: list[str]) -> str:
    if not tags:
        return "类型待确认"
    return _shorten(" / ".join(tags[:3]), 30)


def genre_signals_from_info(info: dict, tags: list[str]) -> dict:
    signals = info.get("genre_signals")
    if isinstance(signals, dict):
        return signals
    return {"primary_type": _infer_type(tags)}


def _compact_type(signals: dict, tags: list[str]) -> str:
    primary_type = str(signals.get("primary_type", "") or "")
    if primary_type and primary_type != "类型待定":
        return _shorten(primary_type, 60)
    return _infer_type(tags)


def _compact_core_loop(tags: list[str], core_judgment: str) -> str:
    if "基础卡组" in core_judgment:
        return "基础卡组 → 战斗 → 拿牌/道具 → 构筑成长"
    if "移动走位" in core_judgment:
        return "移动走位 → 自动/半自动战斗 → 升级选技能 → 构筑成长 → 继续生存"
    if "采集资源" in core_judgment:
        return "采集资源 → 建造基地 → 管理居民 → 长期生存"
    if "探索地图" in core_judgment:
        return "探索地图 → 获得能力 → 解锁区域 → 强化战斗"
    if "规划布局" in core_judgment:
        return "规划布局 → 建造生产 → 自动化管理 → 扩张城市"
    loop = _infer_loop(tags, core_judgment)
    if loop:
        return _shorten(loop, 30)
    if "公开信息不足" in core_judgment:
        return "核心循环待试玩确认"
    return _shorten(_remove_hedge_words(core_judgment), 30)


def _compact_items(values: list[str], limit: int, char_limit: int) -> list[str]:
    output = []
    for value in values:
        clean = _compact_sentence(value, char_limit)
        if clean and clean not in output:
            output.append(clean)
        if len(output) >= limit:
            break
    return output or [PLACEHOLDER]


def _compact_sentence(value: str, char_limit: int) -> str:
    text = _remove_hedge_words(str(value or ""))
    text = re.sub(r"^[^：:]{1,12}[：:]", "", text).strip()
    replacements = {
        "商店标签集中在": "标签集中：",
        "可先围绕这些关键词验证受众": "验证受众",
        "公开描述显示核心循环": "核心循环",
        "当前有": "",
        "可初步判断": "可看",
        "需要进一步确认": "待确认",
        "需要人工确认": "人工确认",
        "需要确认": "待确认",
        "需确认": "确认",
        "可能存在": "存在",
        "可能": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = " ".join(text.split())
    return _shorten(text, char_limit)


def _remove_hedge_words(value: str) -> str:
    text = str(value or "")
    text = text.replace("这可能是一款", "")
    text = text.replace("可能是", "")
    text = text.replace("可能", "")
    text = text.replace("需要通过试玩确认", "试玩确认")
    text = text.replace("需要人工确认", "人工确认")
    return text.strip(" 。")


def _quick_text(profile: ProjectProfile, key: str) -> str:
    value = profile.quick_summary.get(key, "")
    if isinstance(value, list):
        return _first_or_placeholder(value)
    return str(value or PLACEHOLDER)


def _first_or_placeholder(values) -> str:
    if isinstance(values, list):
        for value in values:
            text = str(value or "").strip()
            if text:
                return text
        return PLACEHOLDER
    return str(values or PLACEHOLDER)


def _dict_to_bullets(values: dict[str, str]) -> str:
    return "\n".join(f"- {key}：{value or PLACEHOLDER}" for key, value in values.items())


def _list_to_bullets(values: list[str]) -> str:
    clean_values = [str(item).strip() for item in values if str(item).strip()]
    if not clean_values:
        return f"- {PLACEHOLDER}"
    return "\n".join(f"- {item}" for item in clean_values)


def _join_or_placeholder(values) -> str:
    if isinstance(values, list):
        clean_values = [str(item).strip() for item in values if str(item).strip()]
        return " / ".join(clean_values) if clean_values else PLACEHOLDER
    text = str(values or "").strip()
    return text if text else PLACEHOLDER


def _string_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return _split_terms(str(value or ""))


def _split_terms(raw_text: str) -> list[str]:
    return _dedupe([part.strip() for part in re.split(r"[,，、;\n\r]+", str(raw_text or "")) if part.strip()])


def _dedupe(values: list[str]) -> list[str]:
    output = []
    seen = set()
    for value in values:
        clean = str(value).strip()
        marker = clean.casefold()
        if clean and marker not in seen:
            seen.add(marker)
            output.append(clean)
    return output


def _value(value) -> str:
    if value is None:
        return PLACEHOLDER
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value if str(item).strip())
    text = str(value).strip()
    return text if text else PLACEHOLDER


def _has_value(value) -> bool:
    text = str(value or "").strip()
    return bool(text and text not in {PLACEHOLDER, "未获取", "未确认", "[]", "None", "nan"})


def _format_positive_rate(value) -> str:
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return ""
    if rate <= 1:
        rate *= 100
    return f"{rate:.0f}%"


def _format_hours(value) -> str:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{hours:.1f}h（基于 Steam 评测样本）"


def _empty_if_placeholder(value: str) -> str:
    text = str(value or "").strip()
    return "" if text == PLACEHOLDER else text


def _visible_text(value: str) -> str:
    return re.sub(r"\s+", "", str(value or ""))


def _shorten(value: str, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


def _to_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _has_any(tags: list[str], needles) -> bool:
    haystack = " ".join(tags).casefold()
    return any(str(needle).casefold() in haystack for needle in needles)


def safe_filename(name: str) -> str:
    clean_name = re.sub(r'[\\/:*?"<>|]+', "_", str(name)).strip()
    return clean_name or "未命名项目"
