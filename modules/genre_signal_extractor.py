import re
from dataclasses import dataclass, field
from typing import Any


HIGH_VALUE_PATTERNS = [
    ("roguelite deckbuilder", ["roguelite deckbuilder", "roguelike deckbuilder"]),
    ("card battler roguelite", ["card battler roguelite", "roguelite card battler", "roguelike card battler"]),
    ("deckbuilder roguelike", ["deckbuilder roguelike", "deckbuilder roguelite"]),
    ("card game roguelite", ["card game roguelite", "roguelite card game", "roguelike card game"]),
    ("deckbuilder", ["deckbuilder", "deck builder", "deck-building", "deckbuilding"]),
    ("card battler", ["card battler", "card battle", "card combat"]),
    ("卡牌肉鸽", ["卡牌肉鸽", "卡牌 roguelike", "卡牌 roguelite", "肉鸽卡牌"]),
    ("卡组构筑", ["卡组构筑", "牌组构筑", "构筑卡组", "牌库构筑"]),
    ("类杀戮尖塔", ["类杀戮尖塔", "杀戮尖塔like", "slay the spire-like"]),
    ("类小丑牌", ["类小丑牌", "小丑牌like", "balatro-like"]),
    ("bullet heaven", ["bullet heaven", "survivor-like", "survivors-like", "auto shooter", "reverse bullet hell"]),
    ("弹幕幸存者", ["弹幕幸存者", "幸存者like", "类吸血鬼幸存者", "逆弹幕射击"]),
    ("colony sim", ["colony sim", "colony simulator", "base building"]),
    ("殖民地模拟", ["殖民地模拟", "生存建造", "基地经营"]),
    ("metroidvania", ["metroidvania", "类银河战士恶魔城", "银河城"]),
    ("city builder", ["city builder", "settlement", "automation"]),
    ("城市建造", ["城市建造", "自动化", "自动化管理"]),
]

REFERENCE_GAMES = {
    "Slay the Spire": ["slay the spire", "杀戮尖塔"],
    "Balatro": ["balatro", "小丑牌"],
    "Monster Train": ["monster train", "怪物火车"],
    "Hearthstone": ["hearthstone", "炉石", "炉石传说"],
    "Vampire Survivors": ["vampire survivors", "吸血鬼幸存者"],
    "Brotato": ["brotato", "土豆兄弟"],
    "Hollow Knight": ["hollow knight", "空洞骑士"],
    "RimWorld": ["rimworld", "环世界"],
}

LOW_WEIGHT_TAGS = {
    "strategy",
    "turn-based tactics",
    "turn based tactics",
    "casual",
    "indie",
    "adventure",
    "rpg",
    "simulation",
    "action",
    "休闲",
    "独立",
    "策略",
    "回合制战术",
    "角色扮演",
    "模拟",
}

CARD_ROGUELITE_KEYWORDS = {
    "roguelite",
    "roguelike",
    "deckbuilder",
    "deck builder",
    "deck-building",
    "card battler",
    "card game",
    "card combat",
    "卡牌肉鸽",
    "卡组构筑",
    "牌组构筑",
    "类杀戮尖塔",
    "类小丑牌",
}


@dataclass
class GenreSignals:
    primary_type: str = "类型待定"
    core_loop: str = "核心循环待试玩"
    high_confidence_phrases: list[str] = field(default_factory=list)
    reference_games: list[str] = field(default_factory=list)
    low_weight_tags: list[str] = field(default_factory=list)
    search_keywords: list[str] = field(default_factory=list)
    competitor_anchors: list[str] = field(default_factory=list)
    comparison_dimensions: list[str] = field(default_factory=list)
    signal_sources: list[str] = field(default_factory=list)
    external_title_terms: list[str] = field(default_factory=list)


def extract_genre_signals(
    short_description: str = "",
    about_the_game: str = "",
    genres: Any = None,
    tags: Any = None,
    user_keywords: str = "",
    external_title_clues: str = "",
) -> GenreSignals:
    genre_terms = _to_terms(genres)
    tag_terms = _to_terms(tags)
    user_terms = _to_terms(user_keywords)
    external_terms = _to_terms(external_title_clues)
    text = "\n".join(
        [
            short_description or "",
            about_the_game or "",
            " ".join(genre_terms),
            " ".join(tag_terms),
            " ".join(user_terms),
            external_title_clues or "",
        ]
    )
    normalized = _normalize(text)

    high_phrases = _extract_high_phrases(normalized)
    references = _dedupe(_extract_reference_games(normalized) + _extract_reference_games(_normalize(external_title_clues)))
    low_tags = _dedupe([term for term in genre_terms + tag_terms if _normalize(term) in LOW_WEIGHT_TAGS])
    external_title_terms = _dedupe(_extract_external_terms(external_title_clues))

    is_card_roguelite = _is_card_roguelite(normalized, high_phrases, references)
    if is_card_roguelite:
        primary_type = "卡牌肉鸽 / Roguelite Deckbuilder / Card Battler"
        core_loop = "基础卡组 → 战斗 → 拿牌/道具 → 构筑成长"
        search_keywords = _card_roguelite_keywords(high_phrases, references)
        anchors = _card_roguelite_anchors(references)
        dimensions = _comparison_dimensions_for("card_roguelite")
    elif _is_bullet_heaven(normalized, high_phrases, references):
        primary_type = "弹幕幸存者 / 逆弹幕射击 / 轻度 Rogue"
        core_loop = "移动走位 → 自动战斗 → 升级选技能 → 构筑成长"
        search_keywords = _bullet_heaven_keywords(high_phrases, references)
        anchors = _bullet_heaven_anchors(references)
        dimensions = _comparison_dimensions_for("bullet_heaven")
    elif _is_colony_builder(normalized, high_phrases):
        primary_type = "殖民地模拟 / 生存建造 / 基地经营"
        core_loop = "采集资源 → 建造基地 → 管理居民 → 长期生存"
        search_keywords = _builder_keywords(high_phrases, ["colony sim", "base building", "survival base building"])
        anchors = _colony_anchors(references)
        dimensions = _comparison_dimensions_for("colony")
    elif _is_metroidvania(normalized, high_phrases, references):
        primary_type = "银河城 / Metroidvania / 探索动作"
        core_loop = "探索地图 → 获得能力 → 解锁区域 → 强化战斗"
        search_keywords = _builder_keywords(high_phrases, ["metroidvania", "exploration action"])
        anchors = _metroidvania_anchors(references)
        dimensions = _comparison_dimensions_for("action_roguelite")
    elif _is_city_builder(normalized, high_phrases):
        primary_type = "城市建造 / 经营模拟 / 自动化管理"
        core_loop = "规划布局 → 建造生产 → 自动化管理 → 扩张城市"
        search_keywords = _builder_keywords(high_phrases, ["city builder", "automation management"])
        anchors = _city_builder_anchors()
        dimensions = _comparison_dimensions_for("colony")
    elif _has_strategy_signal(genre_terms + tag_terms, normalized):
        primary_type = "类型信息不足，需结合视频和 Demo 确认"
        core_loop = "战术决策 → 执行回合 → 资源成长"
        search_keywords = _strategy_keywords(genre_terms, tag_terms, user_terms)
        anchors = ["待从候选池确认"]
        dimensions = ["价格和内容量", "核心循环完成度", "前 5-10 分钟吸引力", "美术识别度"]
    else:
        primary_type = _fallback_type(genre_terms, tag_terms, high_phrases)
        core_loop = _fallback_loop(normalized)
        search_keywords = _fallback_keywords(high_phrases, user_terms, genre_terms, tag_terms)
        anchors = _fallback_anchors(high_phrases, references, primary_type)
        dimensions = _fallback_dimensions(primary_type)

    sources = []
    if short_description.strip():
        sources.append("Steam short_description")
    if about_the_game.strip():
        sources.append("Steam about_the_game")
    if genre_terms or tag_terms:
        sources.append("Steam genres/tags")
    if user_terms:
        sources.append("用户补充关键词")
    if external_title_clues.strip():
        sources.append("外部标题线索")

    return GenreSignals(
        primary_type=primary_type,
        core_loop=core_loop,
        high_confidence_phrases=high_phrases,
        reference_games=references,
        low_weight_tags=low_tags,
        search_keywords=search_keywords[:5],
        competitor_anchors=anchors[:5],
        comparison_dimensions=dimensions[:8],
        signal_sources=sources,
        external_title_terms=external_title_terms,
    )


def genre_signals_to_dict(signals: GenreSignals) -> dict:
    return {
        "primary_type": signals.primary_type,
        "core_loop": signals.core_loop,
        "high_confidence_phrases": signals.high_confidence_phrases,
        "reference_games": signals.reference_games,
        "low_weight_tags": signals.low_weight_tags,
        "search_keywords": signals.search_keywords,
        "competitor_anchors": signals.competitor_anchors,
        "comparison_dimensions": signals.comparison_dimensions,
        "signal_sources": signals.signal_sources,
        "external_title_terms": signals.external_title_terms,
    }


def _extract_high_phrases(normalized_text: str) -> list[str]:
    phrases = []
    for phrase, patterns in HIGH_VALUE_PATTERNS:
        if any(_normalize(pattern) in normalized_text for pattern in patterns):
            phrases.append(phrase)
    if "card" in normalized_text and ("roguelite" in normalized_text or "roguelike" in normalized_text):
        phrases.append("card game roguelite")
    if ("卡牌" in normalized_text or "卡组" in normalized_text or "牌组" in normalized_text) and "肉鸽" in normalized_text:
        phrases.append("卡牌肉鸽")
    return _dedupe(phrases)


def _extract_reference_games(normalized_text: str) -> list[str]:
    references = []
    for name, aliases in REFERENCE_GAMES.items():
        if any(_normalize(alias) in normalized_text for alias in aliases):
            references.append(name)
    return references


def _extract_external_terms(raw_titles: str) -> list[str]:
    terms = []
    for pattern in [
        "放置卡牌战斗",
        "卡牌战斗",
        "回合制战术",
        "steam新品节",
        "试玩推荐",
        "卡牌肉鸽",
        "卡组构筑",
        "牌组构筑",
        "类炉石",
        "类杀戮尖塔",
        "类小丑牌",
    ]:
        if pattern.casefold() in str(raw_titles).casefold():
            terms.append(pattern)
    terms.extend(_extract_reference_games(_normalize(raw_titles)))
    title_names = re.findall(r"[A-Z][A-Za-z0-9: '&-]{2,40}", str(raw_titles or ""))
    for name in title_names:
        clean = " ".join(name.split()).strip(" -|")
        if clean and clean.casefold() not in {"steam", "youtube", "google"}:
            terms.append(clean)
    return _dedupe(terms)


def _is_card_roguelite(normalized_text: str, high_phrases: list[str], references: list[str]) -> bool:
    has_card = any(term in normalized_text for term in ["card", "deck", "卡牌", "卡组", "牌组"])
    has_rogue = any(term in normalized_text for term in ["roguelite", "roguelike", "肉鸽"])
    has_reference = any(ref in {"Slay the Spire", "Balatro", "Monster Train"} for ref in references)
    return has_reference or (has_card and has_rogue) or any(phrase in CARD_ROGUELITE_KEYWORDS for phrase in high_phrases)


def _is_bullet_heaven(normalized_text: str, high_phrases: list[str], references: list[str]) -> bool:
    has_bullet = any(
        term in normalized_text
        for term in ["bullet heaven", "survivor-like", "auto shooter", "reverse bullet hell", "弹幕幸存者", "逆弹幕射击"]
    )
    has_reference = any(ref in {"Vampire Survivors", "Brotato"} for ref in references)
    return has_bullet or has_reference or any(phrase in {"bullet heaven", "弹幕幸存者"} for phrase in high_phrases)


def _is_colony_builder(normalized_text: str, high_phrases: list[str]) -> bool:
    return any(
        term in normalized_text
        for term in ["colony sim", "base building", "殖民地模拟", "生存建造", "基地经营"]
    ) or any(phrase in {"colony sim", "殖民地模拟"} for phrase in high_phrases)


def _is_metroidvania(normalized_text: str, high_phrases: list[str], references: list[str]) -> bool:
    return (
        "metroidvania" in normalized_text
        or "银河城" in normalized_text
        or "类银河战士恶魔城" in normalized_text
        or "metroidvania" in high_phrases
        or "Hollow Knight" in references
    )


def _is_city_builder(normalized_text: str, high_phrases: list[str]) -> bool:
    return any(
        term in normalized_text
        for term in ["city builder", "settlement", "automation", "城市建造", "自动化"]
    ) or any(phrase in {"city builder", "城市建造"} for phrase in high_phrases)


def _has_strategy_signal(tags: list[str], normalized_text: str) -> bool:
    strategy_terms = {"strategy", "turn-based tactics", "turn based tactics", "策略", "回合制战术"}
    return any(_normalize(tag) in strategy_terms for tag in tags) or any(term in normalized_text for term in strategy_terms)


def _card_roguelite_keywords(high_phrases: list[str], references: list[str]) -> list[str]:
    keywords = [
        "roguelite deckbuilder",
        "card battler roguelite",
        "card game roguelite",
        "卡牌肉鸽",
        "卡组构筑",
    ]
    for phrase in high_phrases:
        if phrase.isascii():
            keywords.insert(0, phrase)
    for reference in references:
        if reference in {"Slay the Spire", "Balatro", "Monster Train"}:
            keywords.append(reference)
    return _dedupe(keywords)


def _card_roguelite_anchors(references: list[str]) -> list[str]:
    anchors = []
    priority = {
        "Slay the Spire": "Slay the Spire / 杀戮尖塔",
        "Balatro": "Balatro / 小丑牌",
        "Monster Train": "Monster Train",
    }
    for reference, label in priority.items():
        if reference in references:
            anchors.append(label)
    for fallback in ["Slay the Spire / 杀戮尖塔", "Balatro / 小丑牌", "Monster Train"]:
        if fallback not in anchors:
            anchors.append(fallback)
    return anchors[:3]


def _bullet_heaven_keywords(high_phrases: list[str], references: list[str]) -> list[str]:
    keywords = ["bullet heaven", "survivor-like roguelite", "auto shooter roguelite", "弹幕幸存者", "逆弹幕射击"]
    for reference in references:
        if reference in {"Vampire Survivors", "Brotato"}:
            keywords.append(reference)
    return _dedupe(high_phrases + keywords)


def _builder_keywords(high_phrases: list[str], defaults: list[str]) -> list[str]:
    return _dedupe(high_phrases + defaults)


def _bullet_heaven_anchors(references: list[str]) -> list[str]:
    anchors = []
    if "Vampire Survivors" in references:
        anchors.append("Vampire Survivors-like")
    if "Brotato" in references:
        anchors.append("Brotato-like")
    for fallback in ["Vampire Survivors-like", "Brotato-like", "Bullet Heaven"]:
        if fallback not in anchors:
            anchors.append(fallback)
    return anchors[:3]


def _colony_anchors(references: list[str]) -> list[str]:
    anchors = ["RimWorld-like"] if "RimWorld" in references else []
    for fallback in ["RimWorld-like", "Colony Sim", "Base Building"]:
        if fallback not in anchors:
            anchors.append(fallback)
    return anchors[:3]


def _metroidvania_anchors(references: list[str]) -> list[str]:
    anchors = ["Hollow Knight-like"] if "Hollow Knight" in references else []
    for fallback in ["Hollow Knight-like", "Metroidvania"]:
        if fallback not in anchors:
            anchors.append(fallback)
    return anchors[:3]


def _city_builder_anchors() -> list[str]:
    return ["City Builder", "Automation Management"]


def _comparison_dimensions_for(signal_type: str) -> list[str]:
    if signal_type == "card_roguelite":
        return ["构筑深度", "单局节奏", "卡牌组合爽点", "随机性控制", "UI 可读性", "价格带"]
    if signal_type == "bullet_heaven":
        return ["前 5 分钟爽感", "敌潮密度", "技能 Build 差异", "局外成长", "画面辨识度", "价格带"]
    if signal_type == "colony":
        return ["系统深度", "中长期目标", "教程门槛", "自动化程度", "内容量", "MOD / 长期运营空间"]
    if signal_type == "action_roguelite":
        return ["打击反馈", "Build 差异", "关卡重复感", "Boss 设计", "操作手感", "价格带"]
    return ["价格和内容量", "前 5-10 分钟吸引力", "核心循环完成度", "美术识别度", "中文本地化", "社区传播素材"]


def _strategy_keywords(genres: list[str], tags: list[str], user_terms: list[str]) -> list[str]:
    combos = []
    clean_tags = [term for term in tags + genres + user_terms if _normalize(term) not in LOW_WEIGHT_TAGS]
    if clean_tags:
        for term in clean_tags[:3]:
            combos.append(f"{term} strategy")
    combos.extend(["turn-based tactics indie", "strategy tactics indie"])
    return _dedupe(combos)[:5]


def _fallback_type(genres: list[str], tags: list[str], high_phrases: list[str]) -> str:
    if high_phrases:
        return " / ".join(high_phrases[:3])
    terms = [term for term in tags + genres if _normalize(term) not in LOW_WEIGHT_TAGS]
    return " / ".join(terms[:3]) if terms else "类型待定"


def _fallback_loop(normalized_text: str) -> str:
    if "survival" in normalized_text or "生存" in normalized_text:
        return "收集资源 → 生存压力 → 扩张成长"
    if "simulation" in normalized_text or "模拟" in normalized_text:
        return "经营资源 → 优化系统 → 扩张目标"
    return "核心循环待试玩"


def _fallback_keywords(high_phrases: list[str], user_terms: list[str], genres: list[str], tags: list[str]) -> list[str]:
    strong = high_phrases + [term for term in user_terms if _normalize(term) not in LOW_WEIGHT_TAGS]
    combo_terms = [term for term in tags + genres if _normalize(term) not in LOW_WEIGHT_TAGS]
    if len(combo_terms) >= 2:
        strong.append(f"{combo_terms[0]} {combo_terms[1]}")
    return _dedupe(strong)[:5]


def _fallback_anchors(high_phrases: list[str], references: list[str], primary_type: str) -> list[str]:
    anchors = [reference for reference in references if reference != "Hearthstone"]
    if anchors:
        return anchors[:3]
    if primary_type == "类型信息不足，需结合视频和 Demo 确认" or primary_type == "类型待定":
        return ["待从候选池确认"]
    return ["待从候选池确认"]


def _fallback_dimensions(primary_type: str) -> list[str]:
    if "Action" in primary_type or "动作" in primary_type:
        return _comparison_dimensions_for("action_roguelite")
    return _comparison_dimensions_for("general")


def _to_terms(value: Any) -> list[str]:
    if isinstance(value, list):
        parts = value
    else:
        parts = re.split(r"[,，、;/\n\r]+", str(value or ""))
    return _dedupe([str(part).strip() for part in parts if str(part).strip()])


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


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
