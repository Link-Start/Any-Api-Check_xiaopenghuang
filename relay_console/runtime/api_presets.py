"""
API 接口预设配置
支持四种预设 + 自定义接口
"""
import copy
import os
import json
from typing import Optional

from ..formats.registry import get_request_format, infer_request_format_id
from ..paths import CONFIG_DIR, CONFIG_PRESETS_DIR


def get_presets_config_path():
    """获取预设配置文件路径"""
    return str(CONFIG_DIR / "presets" / "api_presets.json")


def get_cli_tools_path():
    """获取 CLI tools 定义文件路径"""
    return str(CONFIG_PRESETS_DIR / "cli_tools.json")


def get_cli_system_path():
    """获取 CLI system prompt 文件路径"""
    return str(CONFIG_PRESETS_DIR / "cli_system.json")


def load_cli_tools() -> list:
    """加载 Claude CLI 的 tools 定义"""
    path = get_cli_tools_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_cli_system() -> list:
    """加载 Claude CLI 的 system prompt"""
    path = get_cli_system_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ============ 预设接口定义 ============

API_PRESETS = {
    "anthropic_native": {
        "name": "原生 Anthropic",
        "description": "Anthropic 官方 API 格式",
        "endpoint": "/v1/messages",
        "headers": {
            "accept": "application/json",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        "body_template": {
            "model": "{model}",
            "max_tokens": 8192,
            "messages": [
                {"role": "user", "content": "{message}"}
            ],
            "stream": True
        },
        "auth_header": "x-api-key",
        "auth_prefix": "",
        "supports_thinking": True,
        "thinking_config": {
            "thinking": {
                "type": "enabled",
                "budget_tokens": 10000
            }
        }
    },
    "openai_native": {
        "name": "原生 OpenAI",
        "description": "OpenAI 官方 API 格式",
        "endpoint": "/v1/chat/completions",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "body_template": {
            "model": "{model}",
            "max_tokens": 8192,
            "messages": [
                {"role": "user", "content": "{message}"}
            ],
            "stream": True
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": False,
        "thinking_config": {}
    },
    "openai_responses": {
        "name": "OpenAI Responses",
        "description": "OpenAI Responses API 格式",
        "endpoint": "/v1/responses",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "body_template": {
            "model": "{model}",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "{message}"}
                    ]
                }
            ],
            "metadata": {},
            "text": {
                "format": {
                    "type": "text"
                }
            },
            "max_output_tokens": 8192,
            "stream": True
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": False,
        "thinking_config": {}
    },
    "anthropic_relay": {
        "name": "中转站 Anthropic",
        "description": "中转站 Anthropic 兼容格式（模拟 Claude CLI）",
        "endpoint": "/v1/messages",
        "headers": {
            "accept": "application/json",
            "anthropic-beta": "claude-code-20250219,interleaved-thinking-2025-05-14",
            "anthropic-dangerous-direct-browser-access": "true",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent": "claude-cli/2.0.76 (external, cli)",
            "x-app": "cli",
            # "x-claude-code-attribution-header": "0",
            # "x-claude-code-disable-nonessential-traffic": "true",
            # "x-enable-lsp-tools": "1",
        },
        "body_template": {
            "model": "{model}",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "null"},
                        {"type": "text", "text": "null"},
                        {"type": "text", "text": "{message}", "cache_control": {"type": "ephemeral"}}
                    ]
                }
            ],
            "system": [
                {"type": "text", "text": "null", "cache_control": {"type": "ephemeral"}}
            ],
            "max_tokens": 32000,
            "stream": True
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": True,
        "thinking_config": {
            "thinking": {
                "type": "enabled",
                "budget_tokens": 31999
            }
        }
    },
    "anthropic_cli_real": {
        "name": "Claude CLI 真实格式",
        "description": "完全模拟 Claude Code CLI 真实请求（抓包所得）",
        "endpoint": "/v1/messages?beta=true",
        "headers": {
            "Accept": "application/json",
            "X-Stainless-Retry-Count": "0",
            "X-Stainless-Timeout": "600",
            "X-Stainless-Lang": "js",
            "X-Stainless-Package-Version": "0.70.0",
            "X-Stainless-OS": "Windows",
            "X-Stainless-Arch": "x64",
            "X-Stainless-Runtime": "node",
            "X-Stainless-Runtime-Version": "v22.17.1",
            "anthropic-dangerous-direct-browser-access": "true",
            "anthropic-version": "2023-06-01",
            "x-app": "cli",
            "User-Agent": "claude-cli/2.1.30 (external, cli)",
            "content-type": "application/json",
            "anthropic-beta": "claude-code-20250219,interleaved-thinking-2025-05-14,prompt-caching-scope-2026-01-05",
            "accept-language": "*",
            "sec-fetch-mode": "cors",
            "accept-encoding": "br, gzip, deflate",
        },
        "body_template": {
            "model": "{model}",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "null"},
                        {"type": "text", "text": "null"},
                        {"type": "text", "text": "{message}", "cache_control": {"type": "ephemeral"}}
                    ]
                }
            ],
            "system": [
                {"type": "text", "text": "null", "cache_control": {"type": "ephemeral"}}
            ],
            "metadata": {
                "user_id": "user_cli_test_session"
            },
            "max_tokens": 32000,
            "stream": True
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": True,
        "include_cli_tools": True,
        "include_cli_system": True,
        "thinking_config": {
            "thinking": {
                "type": "enabled",
                "budget_tokens": 31999
            }
        }
    },
    "openai_relay": {
        "name": "中转站 OpenAI",
        "description": "中转站 OpenAI 兼容格式",
        "endpoint": "/v1/chat/completions",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
        },
        "body_template": {
            "model": "{model}",
            "max_tokens": 8192,
            "messages": [
                {"role": "user", "content": "{message}"}
            ],
            "stream": True
        },
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "supports_thinking": False,
        "thinking_config": {}
    }
}

# 预设列表（供下拉框使用）
PRESET_LIST = [
    ("anthropic_cli_real", "Claude CLI 真实格式 (推荐)"),
    ("anthropic_relay", "中转站 Anthropic"),
    ("openai_relay", "中转站 OpenAI"),
    ("openai_responses", "OpenAI Responses"),
    ("anthropic_native", "原生 Anthropic"),
    ("openai_native", "原生 OpenAI"),
    ("custom", "自定义接口"),
]

# 默认模型列表
DEFAULT_MODELS = {
    "anthropic": [
        ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
        ("claude-opus-4-20250514", "Claude Opus 4"),
        ("claude-opus-4-5-20251101", "Claude Opus 4.5"),
        ("claude-opus-4-6", "Claude Opus 4.6"),
        ("claude-sonnet-4-20250514", "Claude Sonnet 4"),
        ("claude-sonnet-4-5-20250929", "Claude Sonnet 4.5"),
    ],
    "openai": [
        ("gpt-5-codex", "GPT-5 Codex"),
        ("gpt-5.1-codex", "GPT-5.1 Codex"),
        ("gpt-5.2-codex", "GPT-5.2 Codex"),
        ("gpt-5.3-codex", "GPT-5.3 Codex"),
    ]
}


# ============ 配置管理 ============

def get_preset(preset_id: str) -> Optional[dict]:
    """获取预设配置"""
    return API_PRESETS.get(preset_id)


def get_preset_format_id(preset_id: str, config: dict | None = None) -> str:
    source = config if isinstance(config, dict) else get_preset(preset_id) or {}
    return infer_request_format_id(preset_id, source)


def get_custom_presets() -> list:
    """获取用户自定义的接口配置"""
    config_path = get_presets_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("custom_presets", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_custom_preset(preset: dict) -> bool:
    """保存自定义接口配置"""
    config_path = get_presets_config_path()
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"custom_presets": []}

        # 检查是否已存在同名配置
        presets = data.get("custom_presets", [])
        for i, p in enumerate(presets):
            if p.get("id") == preset.get("id"):
                presets[i] = preset
                break
        else:
            presets.append(preset)

        data["custom_presets"] = presets

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def delete_custom_preset(preset_id: str) -> bool:
    """删除自定义接口配置"""
    config_path = get_presets_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        presets = data.get("custom_presets", [])
        data["custom_presets"] = [p for p in presets if p.get("id") != preset_id]

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def export_presets(file_path: str) -> bool:
    """导出所有配置到文件"""
    try:
        data = {
            "builtin_presets": API_PRESETS,
            "custom_presets": get_custom_presets()
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def import_presets(file_path: str) -> tuple:
    """从文件导入配置，返回 (success, message)"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        custom = data.get("custom_presets", [])
        if not custom:
            return False, "文件中没有自定义配置"

        config_path = get_presets_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing = {"custom_presets": []}

        # 合并配置
        existing_ids = {p.get("id") for p in existing.get("custom_presets", [])}
        imported = 0
        for preset in custom:
            if preset.get("id") not in existing_ids:
                existing.setdefault("custom_presets", []).append(preset)
                imported += 1

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return True, f"成功导入 {imported} 个配置"
    except json.JSONDecodeError:
        return False, "文件格式错误"
    except Exception as e:
        return False, f"导入失败: {str(e)}"


# ============ 请求构建 ============

def _resolve_preset_config(preset_id: str, custom_config: dict | None = None) -> tuple[dict | None, str | None]:
    if preset_id == "custom" and custom_config:
        return custom_config, None
    if preset_id.startswith("custom_"):
        customs = get_custom_presets()
        config = next((p for p in customs if p.get("id") == preset_id), None)
        if not config:
            return None, "未找到自定义配置"
        return config, None
    config = get_preset(preset_id)
    if not config:
        return None, f"未知的预设: {preset_id}"
    return config, None


def build_request_payload(
    preset_id: str,
    url: str,
    api_key: str,
    model: str,
    message: str,
    with_thinking: bool = False,
    with_system: bool = True,
    stream: bool | None = None,
    custom_config: dict = None,
) -> dict:
    """
    根据预设构建请求

    Returns:
        {
            "success": bool,
            "url": str,
            "headers": dict,
            "body": dict,
            "request_format": str,
            "preset": dict,
            "error": str,
        }
    """
    config, error = _resolve_preset_config(preset_id, custom_config)
    if error or not config:
        return {
            "success": False,
            "url": "",
            "headers": {},
            "body": {},
            "request_format": "",
            "preset": {},
            "error": error or "预设配置无效",
        }

    request_format_id = get_preset_format_id(preset_id, config)
    format_spec = get_request_format(request_format_id)

    base_url = url.rstrip("/")
    endpoint = str(config.get("endpoint") or format_spec.get("default_endpoint") or "")
    full_url = base_url + endpoint

    headers = dict(format_spec.get("default_headers", {}))
    headers.update(dict(config.get("headers", {})))
    auth_header = str(config.get("auth_header") or format_spec.get("auth_header") or "Authorization")
    auth_prefix = str(config.get("auth_prefix") or format_spec.get("auth_prefix") or "")
    headers[auth_header] = auth_prefix + api_key

    body_template = config.get("body_template")
    if body_template:
        body = copy.deepcopy(body_template)
    else:
        body_builder = format_spec.get("body_builder")
        body = body_builder(message, model, with_thinking, with_system) if callable(body_builder) else {}

    def replace_placeholders(obj):
        if isinstance(obj, str):
            return obj.replace("{model}", model).replace("{message}", message)
        elif isinstance(obj, dict):
            return {k: replace_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_placeholders(item) for item in obj]
        return obj

    body = replace_placeholders(body)

    if stream is not None:
        if request_format_id == "gemini_native":
            if stream:
                full_url = full_url.replace(":generateContent", ":streamGenerateContent")
            else:
                full_url = full_url.replace(":streamGenerateContent", ":generateContent")
        if "stream" in body or request_format_id in {"openai_chat", "openai_responses", "claude_messages"}:
            body["stream"] = bool(stream)

    if with_thinking and config.get("supports_thinking", format_spec.get("supports_thinking", False)):
        thinking_config = config.get("thinking_config", {})
        body.update(thinking_config)

    if not with_system and "system" in body:
        del body["system"]
    if not with_system and request_format_id == "openai_chat" and isinstance(body.get("messages"), list):
        body["messages"] = [item for item in body["messages"] if str(item.get("role") or "") != "system"]
    if not with_system and request_format_id == "openai_responses" and "instructions" in body:
        del body["instructions"]
    if not with_system and request_format_id == "gemini_native" and "systemInstruction" in body:
        del body["systemInstruction"]

    if config.get("include_cli_tools"):
        tools = load_cli_tools()
        if tools:
            body["tools"] = tools

    if config.get("include_cli_system"):
        cli_system = load_cli_system()
        if cli_system:
            body["system"] = cli_system

    return {
        "success": True,
        "url": full_url,
        "headers": headers,
        "body": body,
        "request_format": request_format_id,
        "preset": config,
        "error": "",
    }


def build_request(
    preset_id: str,
    url: str,
    api_key: str,
    model: str,
    message: str,
    with_thinking: bool = False,
    with_system: bool = True,
    stream: bool | None = None,
    custom_config: dict = None,
) -> tuple:
    payload = build_request_payload(
        preset_id,
        url,
        api_key,
        model,
        message,
        with_thinking=with_thinking,
        with_system=with_system,
        stream=stream,
        custom_config=custom_config,
    )
    if not payload["success"]:
        return None, None, payload["error"]
    return payload["url"], payload["headers"], payload["body"]
