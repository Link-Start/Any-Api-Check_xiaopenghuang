from __future__ import annotations

from ..runtime.db import get_detection_evidence_payload, list_detection_runs_payload, record_detection_run_payload


def record_detection_run(run: dict, evidence: dict | None = None) -> None:
    record_detection_run_payload(run, evidence)


def list_detection_runs(limit: int = 50, site_id: str = "", run_type: str = "") -> list[dict]:
    return list_detection_runs_payload(limit=limit, site_id=site_id, run_type=run_type)


def get_detection_evidence(run_id: str) -> dict | None:
    return get_detection_evidence_payload(run_id)
