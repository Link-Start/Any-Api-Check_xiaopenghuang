from __future__ import annotations

from ..runtime.db import list_action_logs_payload, record_action_log_payload, trim_action_logs_payload


def record_action_log(entry: dict) -> None:
    record_action_log_payload(entry)


def list_action_logs(limit: int = 50) -> list[dict]:
    return list_action_logs_payload(limit=limit)


def trim_action_logs(max_rows: int = 500) -> None:
    trim_action_logs_payload(max_rows=max_rows)
