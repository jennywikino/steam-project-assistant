from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd


DAILY_WATCH_COLUMNS = [
    "record_id",
    "created_at",
    "source",
    "source_url",
    "game_name",
    "appid",
    "note",
    "next_action",
    "imported_to_project",
]

DAILY_WATCH_FIELD_LABELS = {
    "record_id": "记录 ID",
    "created_at": "创建时间",
    "source": "来源",
    "source_url": "来源链接",
    "game_name": "游戏名",
    "appid": "AppID",
    "note": "观察备注",
    "next_action": "下一步动作",
    "imported_to_project": "已导入项目",
}


@dataclass
class DailyWatchNote:
    source: str = ""
    source_url: str = ""
    game_name: str = ""
    appid: str = ""
    note: str = ""
    next_action: str = ""
    imported_to_project: str = "False"
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_daily_watch_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=DAILY_WATCH_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=DAILY_WATCH_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in DAILY_WATCH_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True
    if "record_id" in existing.columns:
        missing_id = existing["record_id"].astype(str).str.strip() == ""
        if missing_id.any():
            existing.loc[missing_id, "record_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
            changed = True
    if changed:
        extra_columns = [column for column in existing.columns if column not in DAILY_WATCH_COLUMNS]
        existing.to_csv(csv_path, columns=DAILY_WATCH_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_daily_watch_notes(csv_path: Path) -> pd.DataFrame:
    ensure_daily_watch_csv_exists(csv_path)
    try:
        notes = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        notes = pd.DataFrame(columns=DAILY_WATCH_COLUMNS)
    for column in DAILY_WATCH_COLUMNS:
        if column not in notes.columns:
            notes[column] = ""
    return notes.loc[:, DAILY_WATCH_COLUMNS].copy()


def save_daily_watch_note_to_csv(note: DailyWatchNote, csv_path: Path) -> Path:
    ensure_daily_watch_csv_exists(csv_path)
    row = pd.DataFrame([daily_watch_note_to_dict(note)], columns=DAILY_WATCH_COLUMNS)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def daily_watch_note_to_dict(note: DailyWatchNote) -> dict:
    raw = asdict(note)
    return {column: raw.get(column, "") for column in DAILY_WATCH_COLUMNS}
