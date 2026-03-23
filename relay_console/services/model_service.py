from __future__ import annotations

import time
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any

import httpx

from ..repositories.detection_repo import record_detection_run
from ..repositories.model_repo import list_site_models, replace_site_models, update_site_model_probe
from ..runtime.conversation_test import DEFAULT_BROWSER_USER_AGENT
from ..runtime.utils import describe_http_response
from .exceptions import DomainServiceError
from .request_service import send_request_with_preset

MODEL_PROBE_PROMPT = "Reply with OK only."


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_model_rows(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in models:
        model_id = str(item.get("model_id") or "").strip()
        if not model_id:
            continue
        normalized.append(
            {
                "model_id": model_id,
                "display_name": str(item.get("display_name") or model_id),
                "source": str(item.get("source") or "api_models"),
                "metadata": item.get("metadata", {}) if isinstance(item.get("metadata"), dict) else {},
            }
        )
    return normalized


def discover_site_models(site: dict[str, Any], *, timeout_seconds: float = 20.0) -> dict[str, Any]:
    site_id = str(site.get("id") or "").strip()
    base_url = str(site.get("url") or "").strip().rstrip("/")
    api_key = str(site.get("api_key") or "").strip()
    if not base_url or not api_key:
        raise DomainServiceError("请先填写站点 URL 和 API Key")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": DEFAULT_BROWSER_USER_AGENT,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    started = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True, http2=True) as client:
            response = client.get(f"{base_url}/v1/models", headers=headers)
    except httpx.ConnectError:
        return {
            "success": False,
            "message": "无法连接到模型列表接口",
            "latency_ms": 0,
            "models": [],
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "获取模型列表超时",
            "latency_ms": 0,
            "models": [],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "message": f"获取模型列表失败: {exc}",
            "latency_ms": 0,
            "models": [],
        }

    latency_ms = int((time.perf_counter() - started) * 1000)
    if response.status_code != 200:
        hint = describe_http_response(response.status_code, response.text, response.headers.get("Content-Type", ""))
        return {
            "success": False,
            "message": f"模型列表接口返回 HTTP {response.status_code}: {hint}",
            "latency_ms": latency_ms,
            "models": [],
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "success": False,
            "message": "模型列表返回了非 JSON 内容",
            "latency_ms": latency_ms,
            "models": [],
        }

    rows: list[dict[str, Any]] = []
    for item in data.get("data", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id") or "").strip()
        if not model_id:
            continue
        rows.append(
            {
                "model_id": model_id,
                "display_name": str(item.get("name") or model_id),
                "source": "api_models",
                "metadata": {
                    "owned_by": str(item.get("owned_by") or ""),
                    "object": str(item.get("object") or ""),
                },
            }
        )

    normalized = _normalize_model_rows(rows)
    replace_site_models(site_id, normalized, source="api_models")
    stored = list_site_models(site_id)
    if normalized:
        return {
            "success": True,
            "message": f"已获取 {len(normalized)} 个可用模型",
            "latency_ms": latency_ms,
            "models": stored,
        }
    return {
        "success": True,
        "message": "接口可达，但未返回模型列表",
        "latency_ms": latency_ms,
        "models": stored,
    }


def _record_model_probe(
    *,
    site: dict[str, Any],
    model_id: str,
    stream: bool,
    preset_id: str,
    probe_result: dict[str, Any],
    message: str,
    success: bool,
) -> None:
    run_id = f"det-{uuid.uuid4().hex[:10]}"
    now_iso = _now_iso()
    run = {
        "id": run_id,
        "profile_id": "",
        "site_id": str(site.get("id") or ""),
        "run_type": "model_stream" if stream else "model_nonstream",
        "status": "success" if success else "failed",
        "started_at": now_iso,
        "finished_at": now_iso,
        "latency_ms": probe_result.get("latency_ms"),
        "message": message,
        "request_format": str(probe_result.get("request_format") or ""),
        "preset_id": str(preset_id or ""),
        "model_id": str(model_id or ""),
        "detected_model": str(model_id or ""),
        "authenticity_score": 0,
        "metadata": {
            "transport": "stream" if stream else "nonstream",
            "status_lines": probe_result.get("status_lines", []),
        },
    }
    evidence = {
        "id": f"evd-{uuid.uuid4().hex[:10]}",
        "request": probe_result.get("request", {}) or {},
        "response_text": str(probe_result.get("response_text") or ""),
        "parsed_result": {
            "stream": bool(stream),
            "success": bool(success),
            "message": str(message or ""),
            "latency_ms": probe_result.get("latency_ms"),
        },
    }
    record_detection_run(run, evidence)


def probe_site_model(
    site: dict[str, Any],
    *,
    model_id: str,
    preset_id: str,
    stream: bool,
    timeout_seconds: float = 45.0,
) -> dict[str, Any]:
    normalized_model_id = str(model_id or "").strip()
    if not normalized_model_id:
        raise DomainServiceError("缺少模型 ID")

    probe_result = send_request_with_preset(
        site=site,
        message=MODEL_PROBE_PROMPT,
        preset_id=preset_id,
        model_id=normalized_model_id,
        with_thinking=False,
        with_system=False,
        stream=stream,
        timeout_seconds=timeout_seconds,
    )
    response_text = str(probe_result.get("response_text") or "").strip()
    success = bool(probe_result.get("success")) and bool(response_text)
    mode_label = "流式" if stream else "非流式"
    if success:
        message = f"{normalized_model_id} {mode_label}可用"
    else:
        message = str(probe_result.get("error") or "模型返回为空，无法确认可用性")

    update_site_model_probe(
        str(site.get("id") or ""),
        normalized_model_id,
        stream=stream,
        status="success" if success else "failed",
        checked_at=_now_text(),
        latency_ms=probe_result.get("latency_ms"),
        message=message,
        request_format=str(probe_result.get("request_format") or ""),
        preset_id=preset_id,
        display_name=normalized_model_id,
    )
    _record_model_probe(
        site=site,
        model_id=normalized_model_id,
        stream=stream,
        preset_id=preset_id,
        probe_result=probe_result,
        message=message,
        success=success,
    )
    return {
        **probe_result,
        "success": success,
        "message": message,
        "model_id": normalized_model_id,
        "transport": "stream" if stream else "nonstream",
    }


def probe_site_models(
    site: dict[str, Any],
    *,
    preset_id: str,
    stream: bool,
    model_id: str = "",
) -> dict[str, Any]:
    site_id = str(site.get("id") or "")
    targets: list[str]
    requested_model_id = str(model_id or "").strip()
    if requested_model_id:
        targets = [requested_model_id]
    else:
        known_models = [str(item.get("model_id") or "") for item in list_site_models(site_id)]
        targets = [item for item in known_models if item]
        if not targets:
            discovery = discover_site_models(site)
            targets = [str(item.get("model_id") or "") for item in discovery.get("models", []) if str(item.get("model_id") or "")]

    if not targets:
        raise DomainServiceError("当前站点还没有可测试模型，请先获取模型列表")

    results: list[dict[str, Any]] = []
    success_count = 0
    for target_model in targets:
        result = probe_site_model(site, model_id=target_model, preset_id=preset_id, stream=stream)
        if result.get("success"):
            success_count += 1
        results.append(
            {
                "model_id": str(result.get("model_id") or target_model),
                "success": bool(result.get("success")),
                "message": str(result.get("message") or ""),
                "latency_ms": result.get("latency_ms"),
                "request_format": str(result.get("request_format") or ""),
                "transport": str(result.get("transport") or ("stream" if stream else "nonstream")),
            }
        )

    return {
        "success": success_count == len(results),
        "message": f"已完成 {len(results)} 个模型探测，成功 {success_count} 个",
        "results": results,
        "success_count": success_count,
        "total_count": len(results),
        "site_models": list_site_models(site_id),
        "preset_id": preset_id,
        "transport": "stream" if stream else "nonstream",
    }


def build_site_model_cards(sites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in list_site_models():
        grouped[str(item.get("site_id") or "")].append(item)

    cards: list[dict[str, Any]] = []
    for site in sites:
        site_id = str(site.get("id") or "")
        models = grouped.get(site_id, [])
        timestamps = [
            str(item.get("last_stream_checked_at") or "")
            for item in models
            if str(item.get("last_stream_checked_at") or "")
        ] + [
            str(item.get("last_nonstream_checked_at") or "")
            for item in models
            if str(item.get("last_nonstream_checked_at") or "")
        ]
        cards.append(
            {
                "site_id": site_id,
                "site_name": str(site.get("name") or "未命名站点"),
                "url": str(site.get("url") or ""),
                "discovered_count": len(models),
                "stream_ok_count": sum(1 for item in models if str(item.get("last_stream_status") or "") == "success"),
                "stream_failed_count": sum(1 for item in models if str(item.get("last_stream_status") or "") == "failed"),
                "nonstream_ok_count": sum(1 for item in models if str(item.get("last_nonstream_status") or "") == "success"),
                "nonstream_failed_count": sum(1 for item in models if str(item.get("last_nonstream_status") or "") == "failed"),
                "last_checked_at": max(timestamps) if timestamps else "",
            }
        )
    return cards
