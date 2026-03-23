from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from ..repositories.detection_repo import get_detection_evidence, list_detection_runs, record_detection_run
from ..runtime.conversation_test import (
    AUTHENTICITY_PROMPT,
    MODEL_LIST,
    detect_authenticity,
    detect_model,
    test_connectivity,
)
from .exceptions import DomainServiceError
from .request_service import send_request_with_preset


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _build_run_record(
    *,
    site: dict[str, Any],
    run_type: str,
    status: str,
    started_at: str,
    finished_at: str,
    message: str,
    latency_ms: int | None = None,
    request_format: str = "",
    preset_id: str = "",
    model_id: str = "",
    detected_model: str = "",
    authenticity_score: float = 0.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": f"det-{uuid.uuid4().hex[:10]}",
        "profile_id": "",
        "site_id": str(site.get("id") or ""),
        "run_type": run_type,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "latency_ms": latency_ms,
        "message": message,
        "request_format": request_format,
        "preset_id": preset_id,
        "model_id": model_id,
        "detected_model": detected_model,
        "authenticity_score": authenticity_score,
        "metadata": metadata or {},
    }


def _persist_probe_result(
    *,
    site: dict[str, Any],
    run_type: str,
    started_at: str,
    result: dict[str, Any],
    preset_id: str = "",
    model_id: str = "",
) -> None:
    finished_at = _now_iso()
    status = "success" if result.get("success") else "failed"
    authenticity_score = 1.0 if result.get("is_authentic") else 0.0
    run = _build_run_record(
        site=site,
        run_type=run_type,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        message=str(result.get("message") or result.get("error") or ""),
        latency_ms=result.get("latency_ms"),
        request_format=str(result.get("request_format") or ""),
        preset_id=preset_id,
        model_id=model_id,
        detected_model=str(result.get("detected_model") or ""),
        authenticity_score=authenticity_score,
        metadata={
            "matched": result.get("matched"),
            "status_lines": result.get("status_lines", []),
        },
    )
    evidence = {
        "id": f"evd-{uuid.uuid4().hex[:10]}",
        "request": result.get("request", {}),
        "response_text": str(result.get("response_text") or ""),
        "parsed_result": {
            "is_authentic": result.get("is_authentic"),
            "matched": result.get("matched"),
            "detected_model": result.get("detected_model"),
            "text_chunks": result.get("text_chunks", []),
            "thought_text": result.get("thought_text", ""),
        },
    }
    record_detection_run(run, evidence)


def run_connectivity_probe(site: dict[str, Any], persist: bool = True) -> dict[str, Any]:
    started_at = _now_iso()
    result = test_connectivity(str(site.get("url") or ""), str(site.get("api_key") or ""))
    result["latency_ms"] = result.get("latency_ms") if result.get("latency_ms") is not None else None
    if persist:
        _persist_probe_result(site=site, run_type="connectivity", started_at=started_at, result=result)
    return result


def run_authenticity_probe(site: dict[str, Any], payload: dict[str, Any], persist: bool = True) -> dict[str, Any]:
    preset_id = str(payload.get("preset_id") or "anthropic_cli_real")
    model_id = str(payload.get("model_id") or (MODEL_LIST[0][0] if MODEL_LIST else ""))
    started_at = _now_iso()
    result = send_request_with_preset(
        site=site,
        message=AUTHENTICITY_PROMPT,
        preset_id=preset_id,
        model_id=model_id,
        with_thinking=bool(payload.get("with_thinking", True)),
        with_system=bool(payload.get("with_system", True)),
    )
    if result.get("success"):
        response_text = str(result.get("response_text") or "")
        is_authentic, matched = detect_authenticity(response_text)
        detected = detect_model(response_text)
        result["is_authentic"] = is_authentic
        result["matched"] = matched
        result["detected_model"] = detected
        result["status_lines"] = list(result.get("status_lines") or []) + [
            f"[auth] 真伪检测: {'正版验证通过' if is_authentic else '疑似反代/伪装'}",
            f"[auth] 命中关键词: {matched}",
            f"[auth] 模型识别: {detected}",
        ]
    if persist:
        _persist_probe_result(
            site=site,
            run_type="authenticity",
            started_at=started_at,
            result=result,
            preset_id=preset_id,
            model_id=model_id,
        )
    return result


def run_chat_probe(site: dict[str, Any], payload: dict[str, Any], persist: bool = True) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    if not message:
        raise DomainServiceError("请输入测试消息")
    preset_id = str(payload.get("preset_id") or "anthropic_cli_real")
    model_id = str(payload.get("model_id") or (MODEL_LIST[0][0] if MODEL_LIST else ""))
    started_at = _now_iso()
    result = send_request_with_preset(
        site=site,
        message=message,
        preset_id=preset_id,
        model_id=model_id,
        with_thinking=bool(payload.get("with_thinking", True)),
        with_system=bool(payload.get("with_system", True)),
    )
    if result.get("success"):
        result["status_lines"] = list(result.get("status_lines") or []) + [
            f"[chat] 对话已完成，输出长度 {len(str(result.get('response_text') or ''))} 字符"
        ]
    if persist:
        _persist_probe_result(
            site=site,
            run_type="chat",
            started_at=started_at,
            result=result,
            preset_id=preset_id,
            model_id=model_id,
        )
    return result


def run_detection_suite(site: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    connectivity = run_connectivity_probe(site, persist=True)
    authenticity = run_authenticity_probe(site, payload, persist=True)
    result = {
        "success": bool(connectivity.get("success")) and bool(authenticity.get("success")),
        "connectivity": connectivity,
        "authenticity": authenticity,
    }
    return result


def get_recent_detection_runs(site_id: str = "", run_type: str = "", limit: int = 20) -> list[dict[str, Any]]:
    return list_detection_runs(limit=limit, site_id=site_id, run_type=run_type)


def get_detection_run_evidence(run_id: str) -> dict[str, Any] | None:
    return get_detection_evidence(run_id)
