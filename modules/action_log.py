from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


ACTION_LOG_COLUMNS = ["created_at", "action", "appid", "game_name", "detail", "target_page", "batch_id", "result", "source_page"]


def ensure_action_log_csv(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        pd.DataFrame(columns=ACTION_LOG_COLUMNS).to_csv(csv_path, index=False, encoding="utf-8-sig")


def load_action_log(csv_path: Path) -> pd.DataFrame:
    ensure_action_log_csv(csv_path)
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame(columns=ACTION_LOG_COLUMNS)
    for column in ACTION_LOG_COLUMNS:
        if column not in data.columns:
            data[column] = ""
    return data.loc[:, ACTION_LOG_COLUMNS].copy()


def append_action_log(
    csv_path: Path,
    *,
    action: str,
    appid: str = "",
    game_name: str = "",
    detail: str = "",
    target_page: str = "",
    batch_id: str = "",
    result: str = "",
    source_page: str = "",
) -> None:
    data = load_action_log(csv_path)
    row = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": str(action or "").strip(),
        "appid": str(appid or "").strip(),
        "game_name": str(game_name or "").strip(),
        "detail": str(detail or "").strip(),
        "target_page": str(target_page or "").strip(),
        "batch_id": str(batch_id or "").strip(),
        "result": str(result or "").strip(),
        "source_page": str(source_page or "").strip(),
    }
    data = pd.concat([data, pd.DataFrame([row], columns=ACTION_LOG_COLUMNS)], ignore_index=True)
    data.tail(500).to_csv(csv_path, index=False, encoding="utf-8-sig")
