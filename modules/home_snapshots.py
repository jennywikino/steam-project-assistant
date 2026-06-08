from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd


HOME_SNAPSHOT_COLUMNS = [
    "record_id",
    "created_at",
    "source",
    "source_url",
    "game_name",
    "appid",
    "steam_url",
    "steamdb_url",
    "image_path",
    "image_url",
    "title",
    "subtitle",
    "note",
    "next_action",
    "priority",
    "is_archived",
]

HOME_SNAPSHOT_EXPORT_COLUMNS = [
    "created_at",
    "source",
    "game_name",
    "appid",
    "source_url",
    "steam_url",
    "steamdb_url",
    "title",
    "subtitle",
    "note",
    "next_action",
    "priority",
    "is_archived",
]

HOME_SNAPSHOT_FIELD_LABELS = {
    "record_id": "记录 ID",
    "created_at": "创建时间",
    "source": "来源",
    "source_url": "来源链接",
    "game_name": "游戏名",
    "appid": "AppID",
    "steam_url": "Steam 链接",
    "steamdb_url": "SteamDB 链接",
    "image_path": "本地图片路径",
    "image_url": "图片 URL",
    "title": "标题",
    "subtitle": "副标题",
    "note": "观察备注",
    "next_action": "下一步动作",
    "priority": "优先级",
    "is_archived": "已归档",
}


@dataclass
class HomeSnapshot:
    source: str = ""
    source_url: str = ""
    game_name: str = ""
    appid: str = ""
    steam_url: str = ""
    steamdb_url: str = ""
    image_path: str = ""
    image_url: str = ""
    title: str = ""
    subtitle: str = ""
    note: str = ""
    next_action: str = ""
    priority: str = "0"
    is_archived: str = "False"
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_home_snapshot_csv_exists(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=HOME_SNAPSHOT_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    try:
        existing = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=HOME_SNAPSHOT_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")
        return

    changed = False
    for column in HOME_SNAPSHOT_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
            changed = True
    missing_id = existing["record_id"].astype(str).str.strip() == ""
    if missing_id.any():
        existing.loc[missing_id, "record_id"] = [str(uuid4()) for _ in range(int(missing_id.sum()))]
        changed = True
    if changed:
        extra_columns = [column for column in existing.columns if column not in HOME_SNAPSHOT_COLUMNS]
        existing.to_csv(csv_path, columns=HOME_SNAPSHOT_COLUMNS + extra_columns, index=False, encoding="utf-8-sig")


def load_home_snapshots(csv_path: Path) -> pd.DataFrame:
    ensure_home_snapshot_csv_exists(csv_path)
    try:
        snapshots = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        snapshots = pd.DataFrame(columns=HOME_SNAPSHOT_COLUMNS)
    for column in HOME_SNAPSHOT_COLUMNS:
        if column not in snapshots.columns:
            snapshots[column] = ""
    return snapshots.loc[:, HOME_SNAPSHOT_COLUMNS].copy()


def save_home_snapshot_to_csv(snapshot: HomeSnapshot, csv_path: Path) -> Path:
    ensure_home_snapshot_csv_exists(csv_path)
    row = pd.DataFrame([home_snapshot_to_dict(snapshot)], columns=HOME_SNAPSHOT_COLUMNS)
    row.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8-sig")
    return csv_path


def update_home_snapshot_fields(csv_path: Path, record_id: str, updates: dict) -> bool:
    snapshots = load_home_snapshots(csv_path)
    mask = snapshots["record_id"].astype(str) == str(record_id)
    if not mask.any():
        return False
    for column, value in updates.items():
        if column in HOME_SNAPSHOT_COLUMNS:
            snapshots.loc[mask, column] = str(value)
    snapshots.to_csv(csv_path, columns=HOME_SNAPSHOT_COLUMNS, index=False, encoding="utf-8-sig")
    return True


def home_snapshot_to_dict(snapshot: HomeSnapshot) -> dict:
    raw = asdict(snapshot)
    return {column: raw.get(column, "") for column in HOME_SNAPSHOT_COLUMNS}
