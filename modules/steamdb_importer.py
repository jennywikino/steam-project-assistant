from __future__ import annotations

import re


STEAM_APP_RE = re.compile(r"store\.steampowered\.com/app/(\d{3,10})", re.IGNORECASE)
STEAMDB_APP_RE = re.compile(r"steamdb\.info/app/(\d{3,10})", re.IGNORECASE)
APPID_RE = re.compile(r"\bappid\b\s*[:：#-]?\s*(\d{3,10})\b", re.IGNORECASE)
PURE_APPID_RE = re.compile(r"^\d{3,10}$")
RANK_RE = re.compile(r"^\s*#?\s*(\d{1,5})\b")
DATE_RE = re.compile(r"\b(?:19|20)\d{2}[-/.年](?:0?[1-9]|1[0-2])(?:[-/.月](?:0?[1-9]|[12]\d|3[01]))?")
PRICE_RE = re.compile(r"(?:free|免费|¥\s*[\d,.]+|\$\s*[\d,.]+|(?:USD|CNY|RMB)\s*[\d,.]+)", re.IGNORECASE)
RATING_RE = re.compile(r"\b\d{1,3}(?:\.\d+)?%")
NUMBER_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")


def parse_steamdb_paste(text: str) -> list[dict]:
    return [_parse_line(record) for record in _split_paste_records(str(text or ""))]


def _split_paste_records(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []

    pure_appid_list = re.fullmatch(r"\s*\d{3,10}(?:[\s,，;；]+\d{3,10})+\s*", stripped)
    if pure_appid_list:
        return re.findall(r"\d{3,10}", stripped)

    records: list[str] = []
    for raw_line in stripped.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fragments = re.split(r"[，;；]+|(?<!\d),|,(?!\d)", line)
        for fragment in fragments:
            clean_fragment = fragment.strip()
            if not clean_fragment:
                continue
            tab_parts = [part.strip() for part in clean_fragment.split("\t") if part.strip()]
            if len(tab_parts) <= 3:
                records.extend(tab_parts)
            else:
                records.append(clean_fragment)
    return records


def _parse_line(line: str) -> dict:
    appid, appid_source = _parse_appid(line)
    rank = _parse_rank(line)
    release_date = _first_match(DATE_RE, line)
    price = _first_match(PRICE_RE, line)
    rating = _first_match(RATING_RE, line)
    game_name = _parse_game_name(line, appid, rank, release_date, price, rating)
    followers, reviews, peak_ccu = _parse_numeric_metrics(line, appid, rank, release_date, price, rating)

    notes: list[str] = []
    if appid_source:
        notes.append(f"AppID: {appid_source}")
    if not appid:
        notes.append("未识别 AppID；请输入 Steam / SteamDB App 链接或纯 AppID")
    if not game_name:
        notes.append("未识别游戏名")
    if not any([followers, reviews, peak_ccu, rating, price, release_date]):
        notes.append("未识别榜单字段")

    if appid and (game_name or appid_source in {"steam_link", "steamdb_link"}):
        confidence = "high"
    elif appid:
        confidence = "medium"
    elif game_name:
        confidence = "low"
    else:
        confidence = "low"

    steam_url = f"https://store.steampowered.com/app/{appid}/" if appid else ""
    steamdb_url = f"https://steamdb.info/app/{appid}/" if appid else ""

    return {
        "source_row": line,
        "appid": appid,
        "game_name": game_name,
        "steam_url": steam_url,
        "steamdb_url": steamdb_url,
        "rank": rank,
        "followers": followers,
        "reviews": reviews,
        "peak_ccu": peak_ccu,
        "rating": rating,
        "price": price,
        "release_date": release_date,
        "source_type": "steamdb_paste",
        "parse_confidence": confidence,
        "parse_notes": "；".join(notes),
    }


def _parse_appid(line: str) -> tuple[str, str]:
    for pattern, source in [(STEAMDB_APP_RE, "steamdb_link"), (STEAM_APP_RE, "steam_link"), (APPID_RE, "appid_label")]:
        match = pattern.search(line)
        if match:
            return match.group(1), source
    if PURE_APPID_RE.fullmatch(line.strip()):
        return line.strip(), "pure_appid"

    tokens = _split_columns(line)
    if len(tokens) >= 4:
        for token in tokens:
            clean = token.strip()
            if PURE_APPID_RE.fullmatch(clean) and len(clean) >= 5:
                return clean, "table_column"
    return "", ""


def _parse_rank(line: str) -> str:
    match = RANK_RE.search(line)
    if not match:
        return ""
    value = match.group(1)
    if PURE_APPID_RE.fullmatch(line.strip()):
        return ""
    return value


def _parse_game_name(line: str, appid: str, rank: str, release_date: str, price: str, rating: str) -> str:
    text = re.sub(r"https?://\S+", " ", line)
    if appid:
        text = re.sub(rf"\b{re.escape(appid)}\b", " ", text)
    if rank:
        text = re.sub(r"^\s*#?\s*" + re.escape(rank) + r"\b", " ", text)
    for value in [release_date, price, rating]:
        if value:
            text = text.replace(value, " ")
    text = re.sub(r"\b(?:followers?|reviews?|peak|rating|price|release|rank|app)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d[\d,]*(?:\.\d+)?\b", " ", text)
    text = re.sub(r"[\t|]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" -–—·|,;")
    if not text or PURE_APPID_RE.fullmatch(text):
        return ""
    return text[:120]


def _parse_numeric_metrics(line: str, appid: str, rank: str, release_date: str, price: str, rating: str) -> tuple[str, str, str]:
    scrubbed = line
    if appid:
        scrubbed = re.sub(rf"\b{re.escape(appid)}\b", " ", scrubbed)
    if rank:
        scrubbed = re.sub(r"^\s*#?\s*" + re.escape(rank) + r"\b", " ", scrubbed)
    for value in [release_date, price, rating]:
        if value:
            scrubbed = scrubbed.replace(value, " ")

    candidates: list[str] = []
    for match in NUMBER_RE.finditer(scrubbed):
        value = match.group(0)
        clean = value.replace(",", "")
        if len(clean) == 4 and 1900 <= int(float(clean)) <= 2099:
            continue
        if clean.isdigit() and int(clean) < 10:
            continue
        candidates.append(value)

    followers = candidates[0] if len(candidates) >= 1 else ""
    reviews = candidates[1] if len(candidates) >= 2 else ""
    peak_ccu = candidates[2] if len(candidates) >= 3 else ""
    return followers, reviews, peak_ccu


def _first_match(pattern: re.Pattern[str], line: str) -> str:
    match = pattern.search(line)
    return match.group(0).strip() if match else ""


def _split_columns(line: str) -> list[str]:
    if "\t" in line:
        return [part.strip() for part in line.split("\t") if part.strip()]
    return [part.strip() for part in re.split(r"\s{2,}|\|", line) if part.strip()]
