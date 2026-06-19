from __future__ import annotations

from datetime import datetime
from html import unescape
from pathlib import Path
import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

from modules.steam_app_enricher import enrich_appids_basic
from modules.steam_browser_collector import suggest_import, steam_url_from_appid


STEAM_SEARCH_IMPORT_COLUMNS = [
    "appid",
    "game_name",
    "steam_url",
    "import_source",
    "source_page_url",
    "collected_at",
    "collect_method",
    "selected",
    "developer",
    "publisher",
    "release_status",
    "release_date",
    "has_demo",
    "supports_schinese",
    "genres_tags",
    "short_desc",
    "header_image",
    "review_score",
    "review_count",
    "import_suggestion",
    "import_reason",
]

SEARCH_RESULTS_URL = "https://store.steampowered.com/search/results/"
SEARCH_PAGE_URL = "https://store.steampowered.com/search/"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def fetch_steam_search_appids(
    filter_name: str = "",
    category1: str | None = None,
    start: int = 0,
    count: int = 50,
    max_apps: int = 50,
    sleep_seconds: float = 2.0,
) -> list[dict]:
    result = fetch_steam_search_appids_with_stats(
        filter_name=filter_name,
        category1=category1,
        start=start,
        count=count,
        max_apps=max_apps,
        sleep_seconds=sleep_seconds,
    )
    return result["rows"]


def fetch_steam_search_appids_with_stats(
    *,
    filter_name: str = "",
    category1: str | None = None,
    search_url: str = "",
    import_source: str = "",
    start: int = 0,
    count: int = 50,
    max_apps: int = 50,
    sleep_seconds: float = 2.0,
    timeout: float = 15.0,
) -> dict:
    params = search_params_from_url(search_url) if search_url else {}
    if filter_name:
        params["filter"] = filter_name
    if category1:
        params["category1"] = str(category1)

    max_apps = max(1, int(max_apps or 50))
    count = max(1, min(int(count or 50), 100, max_apps))
    start = max(0, int(start or 0))
    import_source = import_source or describe_import_source(params)
    source_page_url = build_search_page_url(params)

    rows: list[dict] = []
    seen: set[str] = set()
    errors: list[str] = []
    current_start = start

    while len(rows) < max_apps:
        batch_count = min(count, max_apps - len(rows))
        request_params = dict(params)
        request_params.update({"start": str(current_start), "count": str(batch_count), "infinite": "1"})
        url = f"{SEARCH_RESULTS_URL}?{urllib.parse.urlencode(request_params, doseq=True)}"
        try:
            payload = _fetch_search_payload(url, timeout=timeout)
        except Exception as exc:
            errors.append(f"start={current_start}: {exc}")
            break

        html = _results_html_from_payload(payload)
        batch_rows = parse_search_results_html(html, import_source=import_source, source_page_url=source_page_url)
        new_count = 0
        for row in batch_rows:
            appid = str(row.get("appid", "") or "").strip()
            if not appid or appid in seen:
                continue
            seen.add(appid)
            rows.append(row)
            new_count += 1
            if len(rows) >= max_apps:
                break

        total_count = _parse_total_count(payload)
        current_start += batch_count
        if new_count == 0 or (total_count is not None and current_start >= total_count):
            break
        if sleep_seconds > 0:
            time.sleep(float(sleep_seconds))

    rows = rows[:max_apps]
    return {
        "rows": rows,
        "errors": errors,
        "requested": len(rows),
        "source_page_url": source_page_url,
        "import_source": import_source,
    }


def search_params_from_url(search_url: str) -> dict:
    parsed = urllib.parse.urlparse(str(search_url or "").strip())
    params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=False))
    for key in ["start", "count", "infinite"]:
        params.pop(key, None)
    return params


def build_search_page_url(params: dict) -> str:
    clean = {key: value for key, value in params.items() if value not in (None, "")}
    query = urllib.parse.urlencode(clean, doseq=True)
    return f"{SEARCH_PAGE_URL}?{query}" if query else SEARCH_PAGE_URL


def describe_import_source(params: dict) -> str:
    if str(params.get("filter", "")).strip().casefold() == "comingsoon" and str(params.get("category1", "")).strip() == "998":
        return "Coming Soon 游戏"
    if str(params.get("category1", "")).strip() == "10":
        return "Demo 池"
    if str(params.get("filter", "")).strip():
        return f"Steam 搜索：filter={params.get('filter')}"
    return "自定义 Steam 搜索"


def parse_search_results_html(html: str, *, import_source: str, source_page_url: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    collected_at = _now_text()
    for match in re.finditer(r"<a\b[^>]*href=\"https?://store\.steampowered\.com/app/(\d+)[^\"]*\"[^>]*>(.*?)</a>", html, re.I | re.S):
        appid = match.group(1).strip()
        if not appid or appid in seen:
            continue
        seen.add(appid)
        block = match.group(2)
        title_match = re.search(r"<span\b[^>]*class=\"[^\"]*\btitle\b[^\"]*\"[^>]*>(.*?)</span>", block, re.I | re.S)
        game_name = _strip_tags(title_match.group(1)) if title_match else ""
        rows.append(
            {
                "appid": appid,
                "game_name": game_name,
                "steam_url": steam_url_from_appid(appid),
                "import_source": import_source,
                "source_page_url": source_page_url,
                "collected_at": collected_at,
                "collect_method": "steam_search_paging",
                "selected": "False",
                "import_suggestion": "待补资料",
                "import_reason": "来自 Steam 搜索分页结果，尚未补全基础信息。",
            }
        )
    if rows:
        return rows

    for appid in re.findall(r"data-ds-appid=\"(\d+)\"", html, re.I):
        if appid in seen:
            continue
        seen.add(appid)
        rows.append(
            {
                "appid": appid,
                "game_name": "",
                "steam_url": steam_url_from_appid(appid),
                "import_source": import_source,
                "source_page_url": source_page_url,
                "collected_at": collected_at,
                "collect_method": "steam_search_paging",
                "selected": "False",
                "import_suggestion": "待补资料",
                "import_reason": "来自 Steam 搜索分页结果，尚未补全基础信息。",
            }
        )
    return rows


def ensure_search_import_csv(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=STEAM_SEARCH_IMPORT_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")


def load_search_imports(csv_path: Path) -> pd.DataFrame:
    ensure_search_import_csv(csv_path)
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=STEAM_SEARCH_IMPORT_COLUMNS)
    for column in STEAM_SEARCH_IMPORT_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, STEAM_SEARCH_IMPORT_COLUMNS].copy()


def save_search_import_rows(csv_path: Path, rows: list[dict]) -> dict:
    data = load_search_imports(csv_path)
    stats = {"created": 0, "updated": 0, "total": 0}
    for raw in rows:
        row = _normalize_row(raw)
        appid = row.get("appid", "")
        if not appid:
            continue
        mask = data["appid"].astype(str).str.strip().eq(appid)
        if mask.any():
            index = data.loc[mask].index[0]
            for column in ["import_source", "source_page_url", "collected_at", "collect_method"]:
                data.loc[index, column] = row.get(column, "")
            for column, value in row.items():
                if column in {"appid", "selected"}:
                    continue
                if value and not str(data.loc[index, column] or "").strip():
                    data.loc[index, column] = value
            stats["updated"] += 1
        else:
            data = pd.concat([data, pd.DataFrame([row], columns=STEAM_SEARCH_IMPORT_COLUMNS)], ignore_index=True)
            stats["created"] += 1
    data = data.drop_duplicates(subset=["appid"], keep="last")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    stats["total"] = len(data)
    return stats


def backup_search_imports_csv(csv_path: Path) -> Path:
    ensure_search_import_csv(csv_path)
    backup_path = csv_path.with_name(f"{csv_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{csv_path.suffix}")
    shutil.copy2(csv_path, backup_path)
    return backup_path


def clear_search_imports(csv_path: Path) -> dict:
    backup_path = backup_search_imports_csv(csv_path)
    data = load_search_imports(csv_path)
    before = len(data)
    pd.DataFrame(columns=STEAM_SEARCH_IMPORT_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"before": before, "after": 0, "removed": before, "backup_path": str(backup_path)}


def dedupe_search_imports_by_appid(csv_path: Path) -> dict:
    backup_path = backup_search_imports_csv(csv_path)
    data = load_search_imports(csv_path)
    before = len(data)
    if data.empty:
        data.to_csv(csv_path, index=False, encoding="utf-8-sig")
        return {"before": before, "after": 0, "removed": 0, "backup_path": str(backup_path)}
    data = data.drop_duplicates(subset=["appid"], keep="last")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    after = len(data)
    return {"before": before, "after": after, "removed": before - after, "backup_path": str(backup_path)}


def enrich_search_imports_basic_info(csv_path: Path, appids: list[str] | None = None) -> dict:
    data = load_search_imports(csv_path)
    if data.empty:
        return {"requested": 0, "updated": 0, "failed": 0, "cache_hit": 0}
    target_appids = _target_appids(data, appids)
    results = enrich_appids_basic(target_appids)
    stats = {"requested": len(target_appids), "updated": 0, "failed": 0, "cache_hit": 0}
    for appid, info in results.items():
        if info.get("cache_hit"):
            stats["cache_hit"] += 1
        mask = data["appid"].astype(str).str.strip().eq(str(appid))
        if not mask.any():
            continue
        if not info.get("success"):
            stats["failed"] += 1
            continue
        index = data.loc[mask].index[0]
        for source_field, target_field in [
            ("game_name", "game_name"),
            ("steam_url", "steam_url"),
            ("developer", "developer"),
            ("publisher", "publisher"),
            ("release_status", "release_status"),
            ("release_date", "release_date"),
            ("has_demo", "has_demo"),
            ("supports_schinese", "supports_schinese"),
            ("genres_tags", "genres_tags"),
            ("short_desc", "short_desc"),
            ("header_image", "header_image"),
            ("review_score", "review_score"),
            ("review_count", "review_count"),
        ]:
            value = _clean(info.get(source_field))
            if value:
                data.loc[index, target_field] = value
        suggestion, reason = suggest_import(data.loc[index].to_dict())
        data.loc[index, "import_suggestion"] = suggestion
        data.loc[index, "import_reason"] = reason
        stats["updated"] += 1
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return stats


def apply_search_import_suggestions(data: pd.DataFrame) -> pd.DataFrame:
    output = data.copy()
    for index, row in output.iterrows():
        suggestion, reason = suggest_import(row.to_dict())
        output.loc[index, "import_suggestion"] = suggestion
        output.loc[index, "import_reason"] = reason
    return output


def filter_search_imports(
    data: pd.DataFrame,
    *,
    demo_only: bool = False,
    unreleased_only: bool = False,
    self_published_only: bool = False,
    schinese_only: bool = False,
    observation_only: bool = False,
    exclude_reference: bool = False,
) -> pd.DataFrame:
    filtered = data.copy()
    if demo_only:
        filtered = filtered.loc[filtered["has_demo"].map(_is_yes)]
    if unreleased_only:
        filtered = filtered.loc[filtered.apply(lambda row: _is_unreleased(row.to_dict()), axis=1)]
    if self_published_only:
        filtered = filtered.loc[filtered.apply(lambda row: _is_self_published(row.to_dict()), axis=1)]
    if schinese_only:
        filtered = filtered.loc[filtered["supports_schinese"].map(_is_yes)]
    if observation_only:
        filtered = filtered.loc[filtered["import_suggestion"].astype(str).isin({"候选池观察 / 值得联系", "待试玩"})]
    if exclude_reference:
        filtered = filtered.loc[~filtered["import_suggestion"].astype(str).eq("竞品参考")]
    return filtered.copy()


def search_import_display_data(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in data.iterrows():
        rows.append(
            {
                "是否选择": _truthy(row.get("selected")),
                "游戏名": row.get("game_name", "") or f"AppID {row.get('appid', '')}",
                "AppID": row.get("appid", ""),
                "来源": row.get("import_source", ""),
                "开发商": row.get("developer", ""),
                "发行商": row.get("publisher", ""),
                "发售状态": row.get("release_status", "") or row.get("release_date", ""),
                "Demo": row.get("has_demo", ""),
                "简中": row.get("supports_schinese", ""),
                "类型": row.get("genres_tags", ""),
                "评测": row.get("review_score", ""),
                "评论数": row.get("review_count", ""),
                "导入建议": row.get("import_suggestion", ""),
                "建议理由": row.get("import_reason", ""),
                "Steam 链接": row.get("steam_url", ""),
                "来源页面": row.get("source_page_url", ""),
            }
        )
    return pd.DataFrame(rows)


def update_search_import_selection(csv_path: Path, visible_appids: list[str], selected_appids: list[str]) -> dict:
    data = load_search_imports(csv_path)
    visible_set = {str(appid or "").strip() for appid in visible_appids if str(appid or "").strip()}
    selected_set = {str(appid or "").strip() for appid in selected_appids if str(appid or "").strip()}
    appids = data["appid"].astype(str).str.strip()
    visible_mask = appids.isin(visible_set)
    data.loc[visible_mask, "selected"] = appids.loc[visible_mask].isin(selected_set).map(lambda value: "True" if value else "False")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"visible": int(visible_mask.sum()), "selected": int(_selected_mask(data).sum())}


def bulk_update_search_import_selection(csv_path: Path, filtered: pd.DataFrame, mode: str) -> dict:
    data = load_search_imports(csv_path)
    visible_appids = {
        str(appid or "").strip()
        for appid in filtered.get("appid", pd.Series(dtype=str)).astype(str).tolist()
        if str(appid or "").strip()
    }
    current_selected = set(data.loc[_selected_mask(data), "appid"].astype(str).str.strip().tolist())
    if mode == "select_visible":
        next_selected = current_selected | visible_appids
    elif mode == "select_demo":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")))
    elif mode == "select_demo_self":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")) and _is_self_published(row))
    elif mode == "select_unreleased_demo":
        next_selected = current_selected | _matching_appids(filtered, lambda row: _is_yes(row.get("has_demo")) and _is_unreleased(row))
    elif mode == "clear_visible":
        next_selected = current_selected - visible_appids
    elif mode == "invert_visible":
        next_selected = set(current_selected)
        for appid in visible_appids:
            if appid in next_selected:
                next_selected.remove(appid)
            else:
                next_selected.add(appid)
    else:
        next_selected = current_selected

    appids = data["appid"].astype(str).str.strip()
    visible_mask = appids.isin(visible_appids)
    data.loc[visible_mask, "selected"] = appids.loc[visible_mask].isin(next_selected).map(lambda value: "True" if value else "False")
    data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"visible": len(visible_appids), "selected": int(_selected_mask(data).sum())}


def _fetch_search_payload(url: str, *, timeout: float) -> dict | str:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Steam 搜索请求失败：HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Steam 搜索请求失败：{exc.reason}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _results_html_from_payload(payload: dict | str) -> str:
    if isinstance(payload, dict):
        return str(payload.get("results_html") or payload.get("html") or "")
    return str(payload or "")


def _parse_total_count(payload: dict | str) -> int | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("total_count")
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _normalize_row(raw: dict) -> dict:
    row = {column: _clean(raw.get(column)) for column in STEAM_SEARCH_IMPORT_COLUMNS}
    if row["appid"] and not row["steam_url"]:
        row["steam_url"] = steam_url_from_appid(row["appid"])
    if not row["collected_at"]:
        row["collected_at"] = _now_text()
    if not row["collect_method"]:
        row["collect_method"] = "steam_search_paging"
    if not row["selected"]:
        row["selected"] = "False"
    if not row["import_suggestion"]:
        row["import_suggestion"], row["import_reason"] = suggest_import(row)
    return row


def _target_appids(data: pd.DataFrame, appids: list[str] | None) -> list[str]:
    candidates = appids if appids else data["appid"].astype(str).str.strip().tolist()
    output = []
    seen = set()
    for raw in candidates:
        appid = str(raw or "").strip()
        if appid and appid.isdigit() and appid not in seen:
            seen.add(appid)
            output.append(appid)
    return output


def _matching_appids(data: pd.DataFrame, predicate) -> set[str]:
    matched: set[str] = set()
    for _, row in data.iterrows():
        row_dict = row.to_dict()
        appid = _clean(row_dict.get("appid"))
        if appid and predicate(row_dict):
            matched.add(appid)
    return matched


def _selected_mask(data: pd.DataFrame) -> pd.Series:
    if "selected" not in data.columns:
        return pd.Series(False, index=data.index)
    return data["selected"].map(_truthy)


def _is_yes(value) -> bool:
    text = _clean(value)
    return text.casefold() in {"yes", "true", "1", "y"} or text in {"是", "有", "有 Demo"}


def _is_self_published(row: dict) -> bool:
    developer = _clean(row.get("developer"))
    publisher = _clean(row.get("publisher"))
    return bool(developer and (not publisher or publisher == developer))


def _is_unreleased(row: dict) -> bool:
    text = " ".join([_clean(row.get("release_status")), _clean(row.get("release_date"))]).casefold()
    if any(token in text for token in ["coming soon", "tba", "to be announced", "即将推出", "未发售", "待定", "未来"]):
        return True
    parsed_date = pd.to_datetime(_clean(row.get("release_date")), errors="coerce")
    if pd.notna(parsed_date):
        return parsed_date.date() > datetime.now().date()
    return False


def _truthy(value) -> bool:
    text = str(value or "").strip()
    return text.casefold() in {"1", "true", "yes", "y"} or text in {"是", "有"}


def _strip_tags(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", str(value or ""))).strip()


def _clean(value) -> str:
    text = str(value or "").strip()
    return "" if text in {"None", "nan", "[]"} else text


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
