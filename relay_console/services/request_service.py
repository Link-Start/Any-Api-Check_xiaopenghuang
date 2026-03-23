from __future__ import annotations

import time
from typing import Any

import httpx

from ..formats.registry import get_format_parser
from ..runtime.api_presets import build_request_payload
from ..runtime.utils import describe_http_response
from .exceptions import DomainServiceError


def _time_only() -> str:
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


def send_request_with_preset(
    *,
    site: dict[str, Any],
    message: str,
    preset_id: str,
    model_id: str,
    with_thinking: bool,
    with_system: bool,
    stream: bool | None = None,
    timeout_seconds: float = 600.0,
) -> dict[str, Any]:
    if not str(site.get("api_key") or "").strip():
        raise DomainServiceError("当前站点缺少 API Key")

    payload = build_request_payload(
        preset_id,
        str(site.get("url") or ""),
        str(site.get("api_key") or ""),
        model_id,
        message,
        with_thinking=with_thinking,
        with_system=with_system,
        stream=stream,
    )
    if not payload["success"]:
        raise DomainServiceError(str(payload["error"] or "请求构建失败"))

    full_url = payload["url"]
    headers = dict(payload["headers"])
    body = dict(payload["body"])
    request_format = str(payload["request_format"] or "")
    use_stream = bool(body.get("stream", True)) if stream is None else bool(stream)
    parser = get_format_parser(request_format, stream=use_stream)

    safe_headers = dict(headers)
    for key in list(safe_headers.keys()):
        if key.lower() in {"authorization", "x-api-key", "x-goog-api-key"}:
            safe_headers[key] = "***"

    status_lines = [f"[{_time_only()}] 连接中: {full_url}"]

    try:
        started = time.perf_counter()
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True, http2=True) as client:
            if use_stream:
                with client.stream("POST", full_url, headers=headers, json=body) as response:
                    if response.status_code != 200:
                        error_text = response.read().decode("utf-8", errors="ignore")
                        hint = describe_http_response(
                            response.status_code,
                            error_text,
                            response.headers.get("Content-Type", ""),
                        )
                        return {
                            "success": False,
                            "request": {"url": full_url, "headers": safe_headers, "body": body},
                            "response_text": error_text,
                            "request_format": request_format,
                            "latency_ms": int((time.perf_counter() - started) * 1000),
                            "stream": use_stream,
                            "status_lines": status_lines + [f"[{_time_only()}] 请求失败 [{response.status_code}]: {hint}"],
                            "error": f"HTTP {response.status_code}: {hint}",
                        }

                    status_lines.append(f"[{_time_only()}] 连接成功，等待流式响应")
                    parsed = parser(response, status_lines)
            else:
                response = client.post(full_url, headers=headers, json=body)
                if response.status_code != 200:
                    error_text = response.text
                    hint = describe_http_response(
                        response.status_code,
                        error_text,
                        response.headers.get("Content-Type", ""),
                    )
                    return {
                        "success": False,
                        "request": {"url": full_url, "headers": safe_headers, "body": body},
                        "response_text": error_text,
                        "request_format": request_format,
                        "latency_ms": int((time.perf_counter() - started) * 1000),
                        "stream": use_stream,
                        "status_lines": status_lines + [f"[{_time_only()}] 请求失败 [{response.status_code}]: {hint}"],
                        "error": f"HTTP {response.status_code}: {hint}",
                    }

                status_lines.append(f"[{_time_only()}] 连接成功，已收到完整响应")
                parsed = parser(response, status_lines)

            latency_ms = int((time.perf_counter() - started) * 1000)
    except httpx.ConnectError:
        return {
            "success": False,
            "request": {"url": full_url, "headers": safe_headers, "body": body},
            "response_text": "",
            "request_format": request_format,
            "latency_ms": 0,
            "stream": use_stream,
            "status_lines": status_lines + [f"[{_time_only()}] 连接失败: 无法连接到服务器"],
            "error": "连接失败: 无法连接到服务器",
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "request": {"url": full_url, "headers": safe_headers, "body": body},
            "response_text": "",
            "request_format": request_format,
            "latency_ms": 0,
            "stream": use_stream,
            "status_lines": status_lines + [f"[{_time_only()}] 请求超时"],
            "error": "请求超时",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "request": {"url": full_url, "headers": safe_headers, "body": body},
            "response_text": "",
            "request_format": request_format,
            "latency_ms": 0,
            "stream": use_stream,
            "status_lines": status_lines + [f"[{_time_only()}] 请求异常: {exc}"],
            "error": f"请求异常: {exc}",
        }

    return {
        "success": True,
        "request": {"url": full_url, "headers": safe_headers, "body": body},
        "response_text": str(parsed.get("response_text") or ""),
        "thought_text": str(parsed.get("thought_text") or ""),
        "text_chunks": parsed.get("text_chunks", []) if isinstance(parsed.get("text_chunks"), list) else [],
        "request_format": request_format,
        "latency_ms": latency_ms,
        "stream": use_stream,
        "status_lines": parsed.get("status_lines", status_lines),
    }
