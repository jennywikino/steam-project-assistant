from __future__ import annotations


EMPTY_MARKERS = {
    "",
    "none",
    "nan",
    "[]",
    "未获取",
    "未确认",
    "暂无",
    "资料不足",
    "unknown",
    "n/a",
}

LOWER_PRIORITY_TAGS = ("clicker", "idle", "incremental", "放置", "点击")
RISK_TOPIC_TAGS = ("visual novel", "dating sim", "nsfw", "成人", "乙女", "avg")


def evaluate_publishing_candidate(row: dict) -> dict:
    appid = _clean_value(row.get("appid"))
    game_name = _clean_value(row.get("game_name"))
    developer = _clean_value(row.get("developer"))
    publisher = _clean_value(row.get("publisher"))
    genres = _clean_value(row.get("genres_tags"))
    release_status = _clean_value(row.get("release_status"))
    release_date = _clean_value(row.get("release_date"))
    has_demo = _is_yes(row.get("has_demo"))
    has_playtest = _is_yes(row.get("has_playtest"))
    supports_schinese = _is_yes(row.get("supports_schinese"))

    missing_items = []
    if not _has_real_game_name(game_name, appid):
        missing_items.append("真实游戏名")
    if not developer:
        missing_items.append("开发商")
    if not genres:
        missing_items.append("类型标签")
    if not (release_status or release_date):
        missing_items.append("发售状态/日期")
    if missing_items:
        return _result(
            "待补资料",
            f"缺少{', '.join(missing_items)}，需要先补项目画像。",
            "补项目画像",
            "未定",
            "",
            row,
        )

    lowered_genres = genres.casefold()
    if _contains_any(lowered_genres, LOWER_PRIORITY_TAGS):
        return _result(
            "暂缓",
            "类型包含 Clicker/Idle/Incremental 或放置/点击方向，与当前发行筛选偏好不匹配，除非后续数据很强。",
            "作为竞品参考",
            "低",
            "",
            row,
        )
    if _contains_any(lowered_genres, RISK_TOPIC_TAGS):
        return _result(
            "暂缓",
            "题材包含 Visual Novel/Dating Sim/NSFW/成人/乙女/AVG 方向，题材适配需要人工复核。",
            "人工复核题材适配",
            "低",
            "",
            row,
        )
    if _has_distinct_publisher(publisher, developer):
        return _result(
            "竞品参考",
            "Steam 显示已有发行商，正式发行机会降低，但仍可评估区域 PR 或作为竞品参考。",
            "查发行合作空间",
            "低",
            "",
            row,
        )
    if developer and has_demo and supports_schinese and genres and not publisher:
        return _result(
            "值得联系",
            "无明显发行商，已有 Demo、支持简中，且基础资料较完整，适合查联系方式并准备外联。",
            "查联系方式 / 准备外联",
            "高",
            "",
            row,
        )
    if developer and genres and (has_demo or has_playtest):
        return _result(
            "待试玩",
            "有试玩入口，适合先验证玩法和转化。",
            "试玩 Demo",
            "中",
            "",
            row,
        )
    return _result(
        "待开发商调查",
        "基础信息可用，但仍需要人工调查开发商背景与发行合作空间。",
        "查开发商背景",
        "未定",
        "",
        row,
    )


def _result(
    auto_suggestion: str,
    auto_reason: str,
    next_action: str,
    priority_suggestion: str,
    reject_reason_suggestion: str,
    row: dict,
) -> dict:
    reason = auto_reason.strip() or "规则给出保守建议，需要人工判断。"
    context = _market_context(row)
    if context:
        reason = f"{reason} {context}"
    return {
        "auto_suggestion": auto_suggestion,
        "auto_reason": reason,
        "next_action": next_action,
        "priority_suggestion": priority_suggestion,
        "reject_reason_suggestion": reject_reason_suggestion,
    }


def _clean_value(value) -> str:
    text = str(value or "").strip()
    return "" if text.casefold() in EMPTY_MARKERS else text


def _has_real_game_name(game_name: str, appid: str) -> bool:
    if not game_name:
        return False
    return not (appid and game_name.strip().casefold() == f"appid {appid}".casefold())


def _is_yes(value) -> bool:
    return str(value or "").strip().casefold() in {"是", "yes", "true", "1", "y", "有"}


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker.casefold() in text for marker in markers)


def _has_distinct_publisher(publisher: str, developer: str) -> bool:
    if not publisher:
        return False
    if not developer:
        return True
    return publisher.casefold() != developer.casefold()


def _market_context(row: dict) -> str:
    parts = []
    followers = _clean_value(row.get("steamdb_followers") or row.get("followers"))
    review_count = _clean_value(row.get("review_count"))
    peak_ccu = _clean_value(row.get("steamdb_peak_ccu") or row.get("peak_ccu"))
    if followers:
        parts.append(f"followers={followers}")
    if review_count:
        parts.append(f"review_count={review_count}")
    if peak_ccu:
        parts.append(f"peak_ccu={peak_ccu}")
    return f"参考数据：{', '.join(parts)}。" if parts else ""
