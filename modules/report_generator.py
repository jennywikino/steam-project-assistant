import re
from pathlib import Path
from typing import Any

import pandas as pd

from modules.competitor_candidate import markdown_table_for_candidates
from modules.competitor_compare import markdown_table_for_competitors
from modules.project_card import ProjectCard


def safe_filename(name: str) -> str:
    """清理 Windows 文件名中的非法字符。"""
    clean_name = re.sub(r'[\\/:*?"<>|]+', "_", str(name)).strip()
    return clean_name or "未命名项目"


def empty_to_placeholder(value: Any) -> str:
    """把空内容转换为报告中的占位文本。"""
    if value is None:
        return "未填写"
    text = str(value).strip()
    return text if text else "未填写"


def _has_demo_record(project: ProjectCard) -> bool:
    """判断项目是否已经录入实际 Demo 试玩内容。"""
    demo_fields = [
        project.demo_played,
        project.first_5min_experience,
        project.first_15min_experience,
        project.first_30min_experience,
        project.core_loop_clarity,
        project.tutorial_issue,
        project.control_issue,
        project.combat_or_system_issue,
        project.localization_issue,
        project.performance_issue,
        project.content_depth,
        project.video_hook,
        project.china_player_reaction,
        project.demo_conclusion,
    ]
    if any(str(value).strip() for value in demo_fields):
        return True
    return int(project.playtime_minutes or 0) > 0


def _build_demo_section(project: ProjectCard) -> str:
    """生成 Demo 试玩报告段落。"""
    if not _has_demo_record(project):
        return "暂无记录"

    return f"""- 是否已试玩 Demo：{empty_to_placeholder(project.demo_played)}
- 试玩时长分钟：{empty_to_placeholder(project.playtime_minutes)}
- 核心循环是否清晰：{empty_to_placeholder(project.core_loop_clarity)}
- 是否有视频传播点：{empty_to_placeholder(project.video_hook)}

### 0-5分钟体验

{empty_to_placeholder(project.first_5min_experience)}

### 5-15分钟体验

{empty_to_placeholder(project.first_15min_experience)}

### 15-30分钟体验

{empty_to_placeholder(project.first_30min_experience)}

### 主要问题记录

- 新手引导问题：{empty_to_placeholder(project.tutorial_issue)}
- 操作/手感问题：{empty_to_placeholder(project.control_issue)}
- 战斗/系统/经营问题：{empty_to_placeholder(project.combat_or_system_issue)}
- 本地化问题：{empty_to_placeholder(project.localization_issue)}
- 性能/稳定性问题：{empty_to_placeholder(project.performance_issue)}
- 内容深度判断：{empty_to_placeholder(project.content_depth)}
- 中国玩家可能的反馈：{empty_to_placeholder(project.china_player_reaction)}

### Demo 试玩结论

{empty_to_placeholder(project.demo_conclusion)}"""


def build_markdown_report(
    project: ProjectCard,
    competitors: pd.DataFrame | None = None,
    candidates: pd.DataFrame | None = None,
) -> str:
    """根据项目卡片生成 Markdown 初筛报告正文。"""
    competitor_section = markdown_table_for_competitors(competitors) if competitors is not None else "暂无记录"
    candidate_section = markdown_table_for_candidates(candidates) if candidates is not None else "暂无记录"
    demo_section = _build_demo_section(project)

    return f"""# {empty_to_placeholder(project.game_name)} 初筛报告

## 基础信息

- 游戏名：{empty_to_placeholder(project.game_name)}
- Steam 链接：{empty_to_placeholder(project.steam_url)}
- Steam AppID：{empty_to_placeholder(project.appid)}
- 开发商：{empty_to_placeholder(project.developer)}
- 发行商：{empty_to_placeholder(project.publisher)}
- 发售状态：{empty_to_placeholder(project.release_status)}
- 是否有 Demo：{empty_to_placeholder(project.has_demo)}
- 是否支持简体中文：{empty_to_placeholder(project.has_simplified_chinese)}
- 类型/标签：{empty_to_placeholder(project.genre_tags)}
- 创建时间：{empty_to_placeholder(project.created_at)}

## 核心玩法

{empty_to_placeholder(project.core_loop)}

## 商店页/第一印象

{empty_to_placeholder(project.first_impression)}

## Demo 试玩记录

{demo_section}

## 竞品对照

{competitor_section}

## 竞品候选

{candidate_section}

## 中国区发行机会

{empty_to_placeholder(project.china_publishing_opportunity)}

## 主要风险

{empty_to_placeholder(project.risks)}

## 下一步建议

{empty_to_placeholder(project.next_action)}

## 初步结论

基于当前手动录入信息、Demo 试玩记录和竞品对照，本项目需要结合后续评论分析再做进一步判断。
"""


def markdown_to_text(markdown: str) -> str:
    """把 Markdown 报告转换为简单 txt 文本。"""
    text = re.sub(r"^#+\s*", "", markdown, flags=re.MULTILINE)
    text = text.replace("- ", "")
    return text.strip() + "\n"


def generate_reports(
    project: ProjectCard,
    markdown_dir: Path,
    txt_dir: Path,
    competitors: pd.DataFrame | None = None,
    candidates: pd.DataFrame | None = None,
) -> tuple[Path, Path]:
    """生成 Markdown 和 txt 两种初筛报告。"""
    markdown_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    filename_stem = f"{safe_filename(project.game_name)}_初筛报告"
    markdown_path = markdown_dir / f"{filename_stem}.md"
    txt_path = txt_dir / f"{filename_stem}.txt"

    markdown_report = build_markdown_report(project, competitors, candidates)
    txt_report = markdown_to_text(markdown_report)

    markdown_path.write_text(markdown_report, encoding="utf-8")
    txt_path.write_text(txt_report, encoding="utf-8")

    return markdown_path, txt_path
