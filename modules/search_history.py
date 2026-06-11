from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd


SEARCH_HISTORY_COLUMNS = [
    "history_id",
    "created_at",
    "updated_at",
    "query_text",
    "query_type",
    "appid",
    "game_name",
    "steam_url",
    "steamdb_url",
    "developer",
    "publisher",
    "release_date",
    "review_score",
    "review_count",
    "last_result_status",
    "hit_count",
    "note",
]

QUERY_TYPE_OPTIONS = ["steam_url", "steamdb_url", "appid", "game_name", "mixed_text", "unknown"]
MAX_SEARCH_HISTORY_ROWS = 300


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class SearchHistoryRecord:
    query_text: str = ""
    query_type: str = "unknown"
    appid: str = ""
    game_name: str = ""
    steam_url: str = ""
    steamdb_url: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: str = ""
    review_score: str = ""
    review_count: str = ""
    last_result_status: str = ""
    note: str = ""
    history_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    hit_count: str = "1"


def ensure_search_history_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=SEARCH_HISTORY_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return
    try:
        records = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        records = pd.DataFrame(columns=SEARCH_HISTORY_COLUMNS)
    normalized = _normalize_history_frame(records)
    if list(records.columns) != list(normalized.columns) or not normalized.equals(records.loc[:, normalized.columns]):
        normalized.to_csv(csv_path, index=False, encoding="utf-8-sig")


def load_search_history(csv_path: Path) -> pd.DataFrame:
    ensure_search_history_csv_exists(csv_path)
    try:
        records = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        records = pd.DataFrame(columns=SEARCH_HISTORY_COLUMNS)
    return sort_search_history(_normalize_history_frame(records))


def upsert_search_history(csv_path: Path, record: SearchHistoryRecord) -> pd.DataFrame:
    records = load_search_history(csv_path)
    row = sanitize_search_history_record(asdict(record))
    if not row["appid"] and not row["game_name"]:
        return records

    now = _now()
    match = pd.Series([False] * len(records), index=records.index)
    if row["appid"]:
        match = records["appid"].astype(str).str.strip().eq(row["appid"])
    elif row["query_text"]:
        match = records["query_text"].astype(str).str.strip().str.casefold().eq(row["query_text"].casefold())

    if match.any():
        index = records.loc[match].index[0]
        created_at = records.at[index, "created_at"] or now
        history_id = records.at[index, "history_id"] or str(uuid4())
        try:
            hit_count = int(str(records.at[index, "hit_count"] or "0").strip()) + 1
        except ValueError:
            hit_count = 1
        for column in SEARCH_HISTORY_COLUMNS:
            records.at[index, column] = row.get(column, "")
        records.at[index, "history_id"] = history_id
        records.at[index, "created_at"] = created_at
        records.at[index, "updated_at"] = now
        records.at[index, "hit_count"] = str(hit_count)
    else:
        row["history_id"] = row["history_id"] or str(uuid4())
        row["created_at"] = row["created_at"] or now
        row["updated_at"] = now
        records = pd.concat([records, pd.DataFrame([row], columns=SEARCH_HISTORY_COLUMNS)], ignore_index=True)

    records = sort_search_history(_normalize_history_frame(records))
    if len(records) > MAX_SEARCH_HISTORY_ROWS:
        records = records.head(MAX_SEARCH_HISTORY_ROWS).copy()
    records.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return records


def delete_search_history_record(csv_path: Path, history_id: str = "", appid: str = "") -> pd.DataFrame:
    records = load_search_history(csv_path)
    if records.empty:
        return records

    history_id = _clean_text(history_id)
    appid = _clean_text(appid)
    mask = pd.Series([False] * len(records), index=records.index)
    if history_id:
        mask = mask | records["history_id"].astype(str).str.strip().eq(history_id)
    if appid:
        mask = mask | records["appid"].astype(str).str.strip().eq(appid)

    if not mask.any():
        return records
    records = records.loc[~mask].copy()
    records = sort_search_history(_normalize_history_frame(records))
    records.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return records


def clear_search_history(csv_path: Path) -> pd.DataFrame:
    ensure_search_history_csv_exists(csv_path)
    records = pd.DataFrame(columns=SEARCH_HISTORY_COLUMNS)
    records.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return records


def filter_search_history(records: pd.DataFrame, keyword: str = "", limit: int = 30) -> pd.DataFrame:
    records = sort_search_history(_normalize_history_frame(records))
    clean = " ".join(str(keyword or "").split()).casefold()
    if clean:
        mask = pd.Series([False] * len(records), index=records.index)
        for column in ["query_text", "appid", "game_name", "developer", "publisher"]:
            mask = mask | records[column].astype(str).str.casefold().str.contains(clean, regex=False, na=False)
        records = records.loc[mask].copy()
    return records.head(limit).copy()


def history_option_label(row: dict) -> str:
    name = _display(row.get("game_name"))
    appid = _display(row.get("appid"))
    updated_at = _display(row.get("updated_at"))
    return f"{name} · {appid} · {updated_at}"


def search_history_to_prefill(row: dict) -> dict:
    return {column: str(row.get(column, "") or "") for column in SEARCH_HISTORY_COLUMNS}


def sort_search_history(records: pd.DataFrame) -> pd.DataFrame:
    output = _normalize_history_frame(records)
    if output.empty:
        return output
    output["_updated_at_sort"] = pd.to_datetime(output["updated_at"], errors="coerce")
    output = output.sort_values(by=["_updated_at_sort", "updated_at"], ascending=[False, False], na_position="last")
    return output.drop(columns=["_updated_at_sort"]).loc[:, SEARCH_HISTORY_COLUMNS].copy()


def sanitize_search_history_record(record: dict) -> dict:
    clean = {column: _clean_text(record.get(column, "")) for column in SEARCH_HISTORY_COLUMNS}
    if clean["query_type"] not in QUERY_TYPE_OPTIONS:
        clean["query_type"] = "unknown"
    if not clean["history_id"]:
        clean["history_id"] = str(uuid4())
    now = _now()
    if not clean["created_at"]:
        clean["created_at"] = now
    if not clean["updated_at"]:
        clean["updated_at"] = now
    try:
        clean["hit_count"] = str(max(1, int(clean["hit_count"] or "1")))
    except ValueError:
        clean["hit_count"] = "1"
    return clean


def _normalize_history_frame(records: pd.DataFrame | None) -> pd.DataFrame:
    output = records.copy() if records is not None else pd.DataFrame(columns=SEARCH_HISTORY_COLUMNS)
    for column in SEARCH_HISTORY_COLUMNS:
        if column not in output.columns:
            output[column] = ""
        output[column] = output[column].astype(str).map(_clean_text)
    for index, row in output.iterrows():
        if not row.get("history_id"):
            output.at[index, "history_id"] = str(uuid4())
        if not row.get("created_at"):
            output.at[index, "created_at"] = _now()
        if not row.get("updated_at"):
            output.at[index, "updated_at"] = output.at[index, "created_at"]
        if not row.get("hit_count"):
            output.at[index, "hit_count"] = "1"
        if row.get("query_type") not in QUERY_TYPE_OPTIONS:
            output.at[index, "query_type"] = "unknown"
    return output.loc[:, SEARCH_HISTORY_COLUMNS].copy()


def _clean_text(value) -> str:
    return " ".join(str(value or "").split())


def _display(value) -> str:
    text = str(value or "").strip()
    return text if text else "未获取"
