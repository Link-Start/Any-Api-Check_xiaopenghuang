from __future__ import annotations

import json
from typing import Any, Callable

import httpx

from ..runtime.sse_parser import parse_anthropic_sse_stream

FormatParser = Callable[[httpx.Response, list[str]], dict[str, Any]]
FormatBodyBuilder = Callable[[str, str, bool, bool], dict[str, Any]]


def _parse_openai_chat_stream(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    full_response = ""
    buffer = ""
    for chunk in response.iter_bytes():
        buffer += chunk.decode("utf-8", errors="ignore")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = event.get("choices", [])
            if choices:
                content = choices[0].get("delta", {}).get("content", "")
                if content:
                    full_response += content
    return {
        "response_text": full_response,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _parse_openai_responses_stream(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    full_response = ""
    buffer = ""
    for chunk in response.iter_bytes():
        buffer += chunk.decode("utf-8", errors="ignore")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            event_type = event.get("type", "")
            if event_type == "response.output_text.delta":
                full_response += str(event.get("delta") or "")
            elif event_type == "response.output_text.done" and not full_response:
                full_response = str(event.get("text") or "")
            elif event_type == "response.refusal.delta":
                full_response += str(event.get("delta") or "")
    return {
        "response_text": full_response,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _parse_claude_messages_stream(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    thought_chunks: list[str] = []
    text_chunks: list[str] = []
    lines = list(status_lines)
    response_text = parse_anthropic_sse_stream(
        response.iter_bytes(),
        on_thinking=lambda text: thought_chunks.append(text),
        on_text=lambda text: text_chunks.append(text),
        on_status=lambda text: lines.append(text),
    )
    return {
        "response_text": response_text,
        "thought_text": "".join(thought_chunks),
        "text_chunks": text_chunks,
        "status_lines": lines,
    }


def _parse_passthrough_text(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    try:
        response_text = response.read().decode("utf-8", errors="ignore")
    except Exception:
        response_text = ""
    return {
        "response_text": response_text,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _extract_text_segments(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return parts
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str):
            return [text]
    return []


def _parse_openai_chat_response(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        return _parse_passthrough_text(response, status_lines)

    message = {}
    choices = data.get("choices", [])
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {}) or {}
    response_text = "".join(_extract_text_segments(message.get("content")))
    if not response_text:
        response_text = str(data.get("output_text") or "")
    return {
        "response_text": response_text,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _parse_openai_responses_response(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        return _parse_passthrough_text(response, status_lines)

    response_text = str(data.get("output_text") or "")
    if not response_text:
        output = data.get("output", [])
        if isinstance(output, list):
            chunks: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []) or []:
                    if not isinstance(content, dict):
                        continue
                    text = content.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            response_text = "".join(chunks)
    return {
        "response_text": response_text,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _parse_claude_messages_response(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        return _parse_passthrough_text(response, status_lines)

    response_text = ""
    content = data.get("content", [])
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str):
                chunks.append(text)
        response_text = "".join(chunks)
    return {
        "response_text": response_text,
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _parse_gemini_native_response(response: httpx.Response, status_lines: list[str]) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        return _parse_passthrough_text(response, status_lines)

    chunks: list[str] = []
    candidates = data.get("candidates", [])
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content", {}) or {}
            for part in content.get("parts", []) or []:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return {
        "response_text": "".join(chunks),
        "thought_text": "",
        "text_chunks": [],
        "status_lines": status_lines,
    }


def _build_openai_chat_body(message: str, model: str, with_thinking: bool, with_system: bool) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    if with_system:
        messages.append({"role": "system", "content": "You are a helpful assistant."})
    messages.append({"role": "user", "content": message})
    body = {
        "model": model,
        "max_tokens": 8192,
        "messages": messages,
        "stream": True,
    }
    if with_thinking:
        body["reasoning_effort"] = "medium"
    return body


def _build_openai_responses_body(message: str, model: str, with_thinking: bool, with_system: bool) -> dict[str, Any]:
    body = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": message}],
            }
        ],
        "text": {"format": {"type": "text"}},
        "max_output_tokens": 8192,
        "stream": True,
    }
    if with_system:
        body["instructions"] = "You are a helpful assistant."
    if with_thinking:
        body["reasoning"] = {"effort": "medium"}
    return body


def _build_claude_messages_body(message: str, model: str, with_thinking: bool, with_system: bool) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 8192,
        "stream": True,
    }
    if with_system:
        body["system"] = "You are a helpful assistant."
    if with_thinking:
        body["thinking"] = {"type": "enabled", "budget_tokens": 10000}
    return body


def _build_gemini_native_body(message: str, model: str, with_thinking: bool, with_system: bool) -> dict[str, Any]:
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}],
            }
        ],
        "generationConfig": {},
    }
    if with_system:
        body["systemInstruction"] = {"parts": [{"text": "You are a helpful assistant."}]}
    if with_thinking:
        body["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 1024}
    return body


REQUEST_FORMATS: dict[str, dict[str, Any]] = {
    "openai_chat": {
        "id": "openai_chat",
        "name": "OpenAI Chat Completions",
        "default_endpoint": "/v1/chat/completions",
        "default_headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": False,
        "supports_system": True,
        "supports_tools": True,
        "body_builder": _build_openai_chat_body,
        "parser": _parse_openai_chat_stream,
        "response_parser": _parse_openai_chat_response,
    },
    "openai_responses": {
        "id": "openai_responses",
        "name": "OpenAI Responses",
        "default_endpoint": "/v1/responses",
        "default_headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": False,
        "supports_system": True,
        "supports_tools": True,
        "body_builder": _build_openai_responses_body,
        "parser": _parse_openai_responses_stream,
        "response_parser": _parse_openai_responses_response,
    },
    "claude_messages": {
        "id": "claude_messages",
        "name": "Claude Messages",
        "default_endpoint": "/v1/messages",
        "default_headers": {
            "accept": "application/json",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        "auth_header": "x-api-key",
        "auth_prefix": "",
        "supports_thinking": True,
        "supports_system": True,
        "supports_tools": True,
        "body_builder": _build_claude_messages_body,
        "parser": _parse_claude_messages_stream,
        "response_parser": _parse_claude_messages_response,
    },
    "gemini_native": {
        "id": "gemini_native",
        "name": "Gemini Native",
        "default_endpoint": "/v1beta/models/{model}:streamGenerateContent",
        "default_headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "auth_header": "x-goog-api-key",
        "auth_prefix": "",
        "supports_thinking": True,
        "supports_system": True,
        "supports_tools": False,
        "body_builder": _build_gemini_native_body,
        "parser": _parse_passthrough_text,
        "response_parser": _parse_gemini_native_response,
    },
}


def get_request_format(format_id: str) -> dict[str, Any]:
    format_key = str(format_id or "").strip()
    if format_key not in REQUEST_FORMATS:
        raise KeyError(f"未知请求格式: {format_id}")
    return REQUEST_FORMATS[format_key]


def list_request_formats() -> list[dict[str, Any]]:
    hidden_keys = {"body_builder", "parser", "response_parser"}
    return [{k: v for k, v in item.items() if k not in hidden_keys} for item in REQUEST_FORMATS.values()]


def infer_request_format_id(preset_id: str, config: dict[str, Any]) -> str:
    explicit = str(config.get("request_format") or "").strip()
    if explicit:
        return explicit

    endpoint = str(config.get("endpoint") or "").strip().lower()
    preset_name = str(preset_id or "").strip().lower()

    if "/v1/responses" in endpoint or "responses" in preset_name:
        return "openai_responses"
    if "/v1/messages" in endpoint or "anthropic" in preset_name or "claude" in preset_name:
        return "claude_messages"
    if "/models/" in endpoint or "gemini" in preset_name:
        return "gemini_native"
    return "openai_chat"


def get_format_parser(format_id: str, *, stream: bool = True) -> FormatParser:
    spec = get_request_format(format_id)
    if stream:
        return spec["parser"]
    return spec.get("response_parser") or spec["parser"]
