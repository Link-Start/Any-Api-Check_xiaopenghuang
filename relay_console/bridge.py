from __future__ import annotations

import json
import re
import sys
import webbrowser
from datetime import datetime
from typing import Any
import uuid

from .paths import APP_ROOT
from .formats.registry import list_request_formats
from .services.checkin_service import (
    browser_login_site,
    checkin_all_sites,
    checkin_site,
    query_balance_with_cookie_for_site,
    refresh_site_waf_cookie,
)
from .services.cookie_refresh_service import check_and_refresh_cookies
from .services.detection_service import (
    get_detection_run_evidence,
    get_recent_detection_runs,
    run_authenticity_probe,
    run_chat_probe,
    run_connectivity_probe,
)
from .services.exceptions import DomainServiceError
from .services.model_service import build_site_model_cards, discover_site_models, probe_site_models
from .services.provider_service import (
    create_provider_with_unique_name,
    delete_provider_by_id,
    save_provider_by_id,
)
from .services.site_service import (
    create_site_with_unique_name,
    delete_site_by_id,
    save_site_by_id,
)
from .repositories.provider_repo import list_providers
from .repositories.model_repo import list_site_models
from .repositories.action_log_repo import list_action_logs, record_action_log, trim_action_logs
from .runtime.api import (  # noqa: E402
    query_balance,
    query_logs,
    reset_debug_log_cache,
)
from .runtime.api_presets import (  # noqa: E402
    DEFAULT_MODELS,
    PRESET_LIST,
    delete_custom_preset,
    get_custom_presets,
    get_preset_format_id,
    save_custom_preset,
)
from .runtime.conversation_test import (  # noqa: E402
    MODEL_LIST,
)
from .runtime.stats import (  # noqa: E402
    add_checkin_log,
    add_site,
    create_site,
    delete_site,
    get_site_by_id,
    load_checkin_log,
    load_stats,
    save_stats,
    update_site,
)
from .runtime.utils import (  # noqa: E402
    describe_http_response,
    is_autostart_enabled,
    load_config,
    save_config,
    set_autostart,
)


class BridgeError(Exception):
    pass


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def time_only() -> str:
    return datetime.now().strftime("%H:%M:%S")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_csv_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).replace("\n", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def parse_headers(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise BridgeError(f"附加请求头 JSON 格式错误: {exc}") from exc
    if not isinstance(parsed, dict):
        raise BridgeError("附加请求头必须是 JSON 对象")
    return parsed


def parse_json_object(value: Any, *, field_name: str) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise BridgeError(f"{field_name} JSON 格式错误: {exc}") from exc
    if not isinstance(parsed, dict):
        raise BridgeError(f"{field_name} 必须是 JSON 对象")
    return parsed


def normalize_preset_id(raw_id: Any, fallback_name: Any) -> str:
    text = str(raw_id or "").strip()
    if not text:
        text = str(fallback_name or "").strip()
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_").lower()
    if not slug:
        slug = f"custom_{uuid.uuid4().hex[:8]}"
    if not slug.startswith("custom_"):
        slug = f"custom_{slug}"
    return slug


def mask_secret(value: str, keep: int = 4) -> str:
    text = str(value or "")
    if not text:
        return ""
    if len(text) <= keep * 2:
        return "*" * len(text)
    return f"{text[:keep]}***{text[-keep:]}"


def compute_site_status(site: dict[str, Any], low_balance_threshold: float) -> str:
    balance_unit = str(site.get("api_balance_unit", site.get("balance_unit", "USD")) or "USD")
    balance = safe_float(site.get("api_balance", site.get("balance", 0)))
    if balance_unit == "USD" and balance < low_balance_threshold:
        return "warning"
    if not str(site.get("url") or "").strip():
        return "muted"
    return "healthy"


def serialize_recharge_records(records: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [
        {
            "id": str(record.get("id") or ""),
            "date": str(record.get("date") or ""),
            "amount": safe_float(record.get("amount", 0)),
            "note": str(record.get("note") or ""),
        }
        for record in (records or [])
    ]


def serialize_site(site: dict[str, Any], low_balance_threshold: float) -> dict[str, Any]:
    tags = site.get("tags", []) if isinstance(site.get("tags"), list) else []
    checkin_headers = site.get("checkin_headers", {}) if isinstance(site.get("checkin_headers"), dict) else {}
    endpoints = site.get("endpoints", {}) if isinstance(site.get("endpoints"), dict) else {}
    return {
        "id": str(site.get("id") or ""),
        "name": str(site.get("name") or "未命名站点"),
        "url": str(site.get("url") or ""),
        "api_key": str(site.get("api_key") or ""),
        "api_key_masked": mask_secret(str(site.get("api_key") or "")),
        "type": str(site.get("type") or "paid"),
        "tags": [str(tag) for tag in tags],
        "tags_text": ", ".join(str(tag) for tag in tags),
        "balance": safe_float(site.get("balance", 0)),
        "balance_unit": str(site.get("balance_unit") or "USD"),
        "last_query_time": str(site.get("last_query_time") or "未查询"),
        "api_balance": safe_float(site.get("api_balance", site.get("balance", 0))),
        "api_balance_unit": str(site.get("api_balance_unit") or site.get("balance_unit") or "USD"),
        "api_last_query_time": str(site.get("api_last_query_time") or site.get("last_query_time") or "未查询"),
        "account_balance": safe_float(site.get("account_balance", 0)),
        "account_balance_unit": str(site.get("account_balance_unit") or "USD"),
        "account_last_query_time": str(site.get("account_last_query_time") or "未查询"),
        "account_status_message": str(site.get("account_status_message") or ""),
        "notes": str(site.get("notes") or ""),
        "checkin_url": str(site.get("checkin_url") or ""),
        "checkin_api_path": str(site.get("checkin_api_path") or "/api/user/checkin"),
        "session_cookie": str(site.get("session_cookie") or ""),
        "session_cookie_masked": mask_secret(str(site.get("session_cookie") or ""), keep=6),
        "checkin_headers": checkin_headers,
        "checkin_headers_text": json.dumps(checkin_headers, ensure_ascii=False, indent=2) if checkin_headers else "{}",
        "provider_template": str(site.get("provider_template") or "custom"),
        "waf_cookie_names": [str(name) for name in site.get("waf_cookie_names", []) or []],
        "waf_cookie_names_text": ", ".join(str(name) for name in site.get("waf_cookie_names", []) or []),
        "checkin_cookie_updated_at": str(site.get("checkin_cookie_updated_at") or ""),
        "checkin_user_id": str(site.get("checkin_user_id") or ""),
        "balance_auth_type": str(site.get("balance_auth_type") or "bearer"),
        "log_auth_type": str(site.get("log_auth_type") or "url_key"),
        "proxy": str(site.get("proxy") or ""),
        "jwt_token": str(site.get("jwt_token") or ""),
        "endpoints": endpoints,
        "endpoint_balance_subscription": str(endpoints.get("balance_subscription") or ""),
        "endpoint_balance_usage": str(endpoints.get("balance_usage") or ""),
        "endpoint_logs": str(endpoints.get("logs") or ""),
        "recharge_records": serialize_recharge_records(site.get("recharge_records", [])),
        "has_cookie": bool(str(site.get("session_cookie") or "").strip()),
        "status": compute_site_status(site, low_balance_threshold),
    }


def serialize_checkin_log(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(record.get("id") or ""),
        "time": str(record.get("time") or ""),
        "site_name": str(record.get("site_name") or ""),
        "site_id": str(record.get("site_id") or ""),
        "success": bool(record.get("success", False)),
        "quota_awarded": safe_float(record.get("quota_awarded", 0)),
        "message": str(record.get("message") or ""),
    }


def serialize_site_model(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "site_id": str(record.get("site_id") or ""),
        "model_id": str(record.get("model_id") or ""),
        "display_name": str(record.get("display_name") or record.get("model_id") or ""),
        "source": str(record.get("source") or "api_models"),
        "metadata": record.get("metadata", {}) if isinstance(record.get("metadata"), dict) else {},
        "discovered_at": str(record.get("discovered_at") or ""),
        "updated_at": str(record.get("updated_at") or ""),
        "last_stream_status": str(record.get("last_stream_status") or ""),
        "last_stream_checked_at": str(record.get("last_stream_checked_at") or ""),
        "last_stream_latency_ms": record.get("last_stream_latency_ms"),
        "last_nonstream_status": str(record.get("last_nonstream_status") or ""),
        "last_nonstream_checked_at": str(record.get("last_nonstream_checked_at") or ""),
        "last_nonstream_latency_ms": record.get("last_nonstream_latency_ms"),
        "last_message": str(record.get("last_message") or ""),
        "last_request_format": str(record.get("last_request_format") or ""),
        "last_preset_id": str(record.get("last_preset_id") or ""),
    }


def group_site_models(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        site_id = str(record.get("site_id") or "")
        grouped.setdefault(site_id, []).append(serialize_site_model(record))
    return grouped


def serialize_custom_preset(record: dict[str, Any]) -> dict[str, Any]:
    preset_id = str(record.get("id") or "")
    request_format = get_preset_format_id(preset_id, record)
    return {
        "id": preset_id,
        "name": str(record.get("name") or preset_id),
        "description": str(record.get("description") or ""),
        "request_format": request_format,
        "endpoint": str(record.get("endpoint") or ""),
        "headers": record.get("headers", {}) if isinstance(record.get("headers"), dict) else {},
        "headers_text": json.dumps(record.get("headers", {}) or {}, ensure_ascii=False, indent=2),
        "body_template": record.get("body_template", {}) if isinstance(record.get("body_template"), dict) else {},
        "body_template_text": json.dumps(record.get("body_template", {}) or {}, ensure_ascii=False, indent=2),
        "auth_header": str(record.get("auth_header") or ""),
        "auth_prefix": str(record.get("auth_prefix") or ""),
        "supports_thinking": bool(record.get("supports_thinking", False)),
        "thinking_config": record.get("thinking_config", {}) if isinstance(record.get("thinking_config"), dict) else {},
        "thinking_config_text": json.dumps(record.get("thinking_config", {}) or {}, ensure_ascii=False, indent=2),
        "include_cli_tools": bool(record.get("include_cli_tools", False)),
        "include_cli_system": bool(record.get("include_cli_system", False)),
    }


def serialize_config(config: dict[str, Any]) -> dict[str, Any]:
    api_endpoints = config.get("api_endpoints", {}) if isinstance(config.get("api_endpoints"), dict) else {}
    auto_query = config.get("auto_query", {}) if isinstance(config.get("auto_query"), dict) else {}
    auto_checkin = config.get("auto_checkin", {}) if isinstance(config.get("auto_checkin"), dict) else {}
    debug = config.get("debug", {}) if isinstance(config.get("debug"), dict) else {}
    action_logs = config.get("action_logs", {}) if isinstance(config.get("action_logs"), dict) else {}
    ui = config.get("ui", {}) if isinstance(config.get("ui"), dict) else {}
    return {
        "autostart": is_autostart_enabled(),
        "minimize_to_tray": bool(config.get("minimize_to_tray", True)),
        "low_balance_threshold": safe_float(config.get("low_balance_threshold", 10), 10),
        "logs_page_size": safe_int(api_endpoints.get("logs_page_size", 50), 50),
        "auto_query_enabled": bool(auto_query.get("enabled", False)),
        "auto_query_interval": safe_int(auto_query.get("interval_minutes", 30), 30),
        "auto_checkin_enabled": bool(auto_checkin.get("enabled", False)),
        "auto_checkin_time": str(auto_checkin.get("time", "09:00") or "09:00"),
        "enable_api_log": bool(debug.get("enable_api_log", False)),
        "action_log_max_rows": safe_int(action_logs.get("max_rows", 500), 500),
        "theme": str(ui.get("theme", "flatly") or "flatly"),
        "use_background_image": bool(ui.get("use_background_image", False)),
        "api_endpoints": {
            "balance_subscription": str(api_endpoints.get("balance_subscription") or "/v1/dashboard/billing/subscription"),
            "balance_usage": str(api_endpoints.get("balance_usage") or "/v1/dashboard/billing/usage"),
            "logs": str(api_endpoints.get("logs") or "/api/log/token"),
            "logs_page_size": safe_int(api_endpoints.get("logs_page_size", 50), 50),
        },
    }


def build_metrics(sites: list[dict[str, Any]], settings: dict[str, Any]) -> dict[str, Any]:
    usd_sites = [site for site in sites if site.get("api_balance_unit") == "USD"]
    token_sites = [site for site in sites if site.get("api_balance_unit") == "Token"]
    logs = load_checkin_log()
    today = datetime.now().strftime("%Y-%m-%d")
    threshold = safe_float(settings.get("low_balance_threshold", 10), 10)
    return {
        "total_sites": len(sites),
        "usd_total": round(sum(safe_float(site.get("api_balance", 0)) for site in usd_sites), 2),
        "token_total": int(sum(safe_float(site.get("api_balance", 0)) for site in token_sites)),
        "low_balance_count": sum(1 for site in usd_sites if safe_float(site.get("api_balance", 0)) < threshold),
        "cookie_enabled_count": sum(1 for site in sites if site.get("has_cookie")),
        "auto_query_label": "已启用" if settings.get("auto_query_enabled") else "未启用",
        "auto_checkin_label": "已启用" if settings.get("auto_checkin_enabled") else "未启用",
        "today_checkin_success": sum(1 for log in logs if str(log.get("time", "")).startswith(today) and log.get("success")),
        "today_checkin_failed": sum(1 for log in logs if str(log.get("time", "")).startswith(today) and not log.get("success")),
    }


def build_activity(sites: list[dict[str, Any]], checkin_logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    activities: list[dict[str, Any]] = []
    for log in checkin_logs[:6]:
        activities.append(
            {
                "time": str(log.get("time") or "")[-8:],
                "title": f"{log.get('site_name', '站点')} · {'签到成功' if log.get('success') else '签到失败'}",
                "description": str(log.get("message") or "无详细信息"),
                "kind": "success" if log.get("success") else "warning",
            }
        )
    if activities:
        return activities
    for site in sites[:6]:
        activities.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "title": f"{site.get('name', '站点')} · 已加载到新界面",
                "description": f"API 余额 {site.get('api_balance', site.get('balance', 0))} {site.get('api_balance_unit', site.get('balance_unit', 'USD'))}",
                "kind": "warning" if site.get("status") == "warning" else "success",
            }
        )
    return activities


def build_chart_data(sites: list[dict[str, Any]], checkin_logs: list[dict[str, Any]]) -> dict[str, Any]:
    # Balance ranking (account balance)
    balance_sites = sorted(
        [s for s in sites if safe_float(s.get("account_balance", 0)) > 0],
        key=lambda s: safe_float(s.get("account_balance", 0)),
        reverse=True,
    )[:10]
    balance_chart = {
        "names": [str(s.get("name") or "未命名") for s in balance_sites],
        "values": [round(safe_float(s.get("account_balance", 0)), 2) for s in balance_sites],
        "types": [str(s.get("type") or "paid") for s in balance_sites],
    }

    # Type distribution
    type_map: dict[str, dict[str, Any]] = {}
    for s in sites:
        t = str(s.get("type") or "paid")
        if t not in type_map:
            type_map[t] = {"count": 0, "balance": 0.0}
        type_map[t]["count"] += 1
        type_map[t]["balance"] += safe_float(s.get("account_balance", 0))
    type_labels = {"paid": "付费站", "free": "公益站", "subscription": "订阅转API"}
    type_chart = {
        "labels": [type_labels.get(t, t) for t in type_map],
        "counts": [type_map[t]["count"] for t in type_map],
        "balances": [round(type_map[t]["balance"], 2) for t in type_map],
    }

    # Checkin trend (last 30 days)
    from datetime import timedelta
    today = datetime.now().date()
    day_keys = [(today - timedelta(days=i)).strftime("%m-%d") for i in range(29, -1, -1)]
    day_full = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    success_by_day = {d: 0 for d in day_full}
    fail_by_day = {d: 0 for d in day_full}
    quota_by_day = {d: 0.0 for d in day_full}
    for log in checkin_logs:
        t = str(log.get("time") or "")[:10]
        if t in success_by_day:
            if log.get("success"):
                success_by_day[t] += 1
                quota_by_day[t] += safe_float(log.get("quota_awarded", 0))
            else:
                fail_by_day[t] += 1
    checkin_chart = {
        "days": day_keys,
        "success": [success_by_day[d] for d in day_full],
        "failed": [fail_by_day[d] for d in day_full],
        "quota": [round(quota_by_day[d], 2) for d in day_full],
    }

    # Recharge trend (last 12 months)
    now = datetime.now()
    month_keys = []
    cursor = now.replace(day=1)
    for _ in range(12):
        month_keys.append(cursor.strftime("%Y-%m"))
        cursor = (cursor - timedelta(days=1)).replace(day=1)
    month_keys.reverse()
    month_totals = {k: 0.0 for k in month_keys}
    for s in sites:
        for rec in (s.get("recharge_records") or []):
            amt = safe_float(rec.get("amount", 0))
            if amt <= 0:
                continue
            d = str(rec.get("date") or "")[:7]
            if d in month_totals:
                month_totals[d] += amt
    recharge_chart = {
        "months": [k[2:] for k in month_keys],
        "values": [round(month_totals[k], 2) for k in month_keys],
    }

    return {
        "balance": balance_chart,
        "type": type_chart,
        "checkin": checkin_chart,
        "recharge": recharge_chart,
    }


def build_test_meta() -> dict[str, Any]:
    formats = list_request_formats()
    format_name_map = {str(item.get("id") or ""): str(item.get("name") or item.get("id") or "") for item in formats}
    presets = [
        {
            "id": preset_id,
            "name": name,
            "request_format": get_preset_format_id(preset_id),
            "request_format_name": format_name_map.get(get_preset_format_id(preset_id), get_preset_format_id(preset_id)),
        }
        for preset_id, name in PRESET_LIST
    ]
    for custom in get_custom_presets():
        custom_id = str(custom.get("id") or "")
        if custom_id:
            format_id = get_preset_format_id(custom_id, custom)
            presets.append(
                {
                    "id": custom_id,
                    "name": str(custom.get("name") or custom_id),
                    "request_format": format_id,
                    "request_format_name": format_name_map.get(format_id, format_id),
                }
            )
    return {
        "presets": presets,
        "default_preset": "anthropic_cli_real",
        "models": [{"id": model_id, "name": name} for model_id, name in MODEL_LIST],
        "default_model": MODEL_LIST[0][0] if MODEL_LIST else "",
        "default_with_thinking": True,
        "default_with_system": True,
        "request_formats": formats,
    }


def resolve_balance_summary(result: dict[str, Any]) -> tuple[float, str]:
    if "hard_limit_usd" in result:
        return safe_float(result.get("remaining_usd", 0)), "USD"
    if "total_available" in result:
        return safe_float(result.get("total_available", 0)), "Token"
    if "balance" in result:
        return safe_float(result.get("balance", 0)), str(result.get("unit") or "USD")
    return 0.0, "USD"


def collect_site_update_payload(payload: dict[str, Any]) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    for key in (
        "name",
        "url",
        "api_key",
        "type",
        "notes",
        "checkin_url",
        "checkin_api_path",
        "session_cookie",
        "provider_template",
        "checkin_cookie_updated_at",
        "checkin_user_id",
        "balance_auth_type",
        "log_auth_type",
        "proxy",
        "jwt_token",
        "balance_unit",
    ):
        if key in payload:
            updates[key] = str(payload.get(key) or "").strip()
    if "balance" in payload:
        updates["balance"] = safe_float(payload.get("balance", 0))
    if "tags" in payload or "tags_text" in payload:
        updates["tags"] = normalize_csv_list(payload.get("tags", payload.get("tags_text")))
    if "waf_cookie_names" in payload or "waf_cookie_names_text" in payload:
        updates["waf_cookie_names"] = normalize_csv_list(payload.get("waf_cookie_names", payload.get("waf_cookie_names_text")))
    if "checkin_headers" in payload or "checkin_headers_text" in payload:
        updates["checkin_headers"] = parse_headers(payload.get("checkin_headers", payload.get("checkin_headers_text")))
    endpoint_values = {
        "balance_subscription": str(payload.get("endpoint_balance_subscription") or "").strip(),
        "balance_usage": str(payload.get("endpoint_balance_usage") or "").strip(),
        "logs": str(payload.get("endpoint_logs") or "").strip(),
    }
    if any(endpoint_values.values()) or any(key in payload for key in ("endpoint_balance_subscription", "endpoint_balance_usage", "endpoint_logs")):
        updates["endpoints"] = {key: value for key, value in endpoint_values.items() if value}
    return updates


class PreviewBridge:
    def __init__(self) -> None:
        self.last_test_request: dict[str, Any] | None = None
        self.last_test_response: str = ""
        self.last_site_logs: dict[str, Any] = {}

    def bootstrap(self, selected_site_id: str | None = None) -> dict[str, Any]:
        return self._build_payload(selected_site_id=selected_site_id)

    def run_action(self, action: str, site_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        handler = getattr(self, f"_action_{action}", None)
        if handler is None:
            return self._error_response("未知动作", f"未实现的动作: {action}", site_id=site_id)
        try:
            response = handler(site_id, payload or {})
        except BridgeError as exc:
            response = self._error_response(action, str(exc), site_id=site_id)
        except DomainServiceError as exc:
            response = self._error_response(action, str(exc), site_id=site_id)
        except Exception as exc:  # noqa: BLE001
            response = self._error_response(action, f"未预期错误: {exc}", site_id=site_id)
        self._record_action_log(action, site_id, response)
        return response

    def _build_payload(self, selected_site_id: str | None = None) -> dict[str, Any]:
        config = load_config()
        settings = serialize_config(config)
        stats_data = load_stats()
        sites = [serialize_site(site, settings["low_balance_threshold"]) for site in stats_data.get("sites", [])]
        checkin_logs = [serialize_checkin_log(record) for record in load_checkin_log()]
        effective_site_id = selected_site_id or (sites[0]["id"] if sites else "")
        all_site_models = list_site_models()
        site_models_by_site = group_site_models(all_site_models)
        custom_presets = [serialize_custom_preset(item) for item in get_custom_presets()]
        return {
            "app": {
                "name": "Any-API-Check",
                "workspace": str(APP_ROOT),
                "mode": "pywebview live bridge",
                "generated_at": now_text(),
            },
            "sites": sites,
            "providers": list_providers(),
            "metrics": build_metrics(sites, settings),
            "activity": build_activity(sites, checkin_logs),
            "checkin_logs": checkin_logs,
            "site_model_cards": build_site_model_cards(sites),
            "site_models_by_site": site_models_by_site,
            "site_models": site_models_by_site.get(effective_site_id, []),
            "detection_runs": get_recent_detection_runs(site_id=effective_site_id, limit=20) if effective_site_id else [],
            "action_logs": list_action_logs(limit=30),
            "chart_data": build_chart_data(sites, checkin_logs),
            "settings": settings,
            "custom_presets": custom_presets,
            "test_meta": build_test_meta(),
            "selected_site_id": effective_site_id,
        }

    def _record_action_log(self, action: str, site_id: str | None, response: dict[str, Any]) -> None:
        if action in {"action_logs"}:
            return
        try:
            config = load_config()
            record_action_log(
                {
                    "id": f"act-{uuid.uuid4().hex[:10]}",
                    "action_key": action,
                    "site_id": str(site_id or ""),
                    "success": bool(response.get("success")),
                    "title": str(response.get("title") or action),
                    "message": str(response.get("message") or ""),
                    "details": {
                        "data_keys": sorted(list((response.get("data") or {}).keys())),
                        "output_lines": list(response.get("output_lines") or []),
                    },
                    "created_at": now_text(),
                }
            )
            max_rows = safe_int((config.get("action_logs") or {}).get("max_rows", 500), 500)
            trim_action_logs(max_rows=max_rows)
        except Exception:
            pass

    def _success_response(self, title: str, message: str, *, site_id: str | None = None, payload: bool = False, data: dict[str, Any] | None = None, output_lines: list[str] | None = None) -> dict[str, Any]:
        result = {
            "success": True,
            "title": title,
            "message": message,
            "data": data or {},
            "output_lines": output_lines or [f"[{time_only()}] {title}", f"[{time_only()}] {message}"],
        }
        if payload:
            result["payload"] = self._build_payload(selected_site_id=site_id)
        return result

    def _error_response(self, title: str, message: str, *, site_id: str | None = None) -> dict[str, Any]:
        return {
            "success": False,
            "title": str(title),
            "message": message,
            "data": {},
            "payload": self._build_payload(selected_site_id=site_id),
            "output_lines": [f"[{time_only()}] {title}", f"[{time_only()}] {message}"],
        }

    def _load_site_or_raise(self, site_id: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
        stats_data = load_stats()
        if not site_id:
            raise BridgeError("未选择站点")
        site = get_site_by_id(stats_data, site_id)
        if not site:
            raise BridgeError("站点不存在或已被删除")
        return stats_data, site

    def _validate_unique_name(self, stats_data: dict[str, Any], site_id: str | None, name: str) -> None:
        normalized = name.strip().casefold()
        if not normalized:
            raise BridgeError("站点名称不能为空")
        for site in stats_data.get("sites", []):
            if site.get("id") == site_id:
                continue
            if str(site.get("name") or "").strip().casefold() == normalized:
                raise BridgeError(f"站点名称重复: {name}")

    def _resolve_site_query_options(self, site: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        global_endpoints = config.get("api_endpoints", {}) if isinstance(config.get("api_endpoints"), dict) else {}
        site_endpoints = site.get("endpoints", {}) if isinstance(site.get("endpoints"), dict) else {}
        return {
            "balance_subscription": site_endpoints.get("balance_subscription") or global_endpoints.get("balance_subscription", "/v1/dashboard/billing/subscription"),
            "balance_usage": site_endpoints.get("balance_usage") or global_endpoints.get("balance_usage", "/v1/dashboard/billing/usage"),
            "logs": site_endpoints.get("logs") or global_endpoints.get("logs", "/api/log/token"),
            "logs_page_size": safe_int(global_endpoints.get("logs_page_size", 50), 50),
        }

    def _update_site_balance_from_result(self, stats_data: dict[str, Any], site_id: str, result: dict[str, Any]) -> None:
        if "error" in result:
            return
        balance_value, unit = resolve_balance_summary(result)
        update_site(
            stats_data,
            site_id,
            {
                "balance": balance_value,
                "balance_unit": unit,
                "last_query_time": now_text(),
                "api_balance": balance_value,
                "api_balance_unit": unit,
                "api_last_query_time": now_text(),
            },
        )

    def _action_refresh_sites(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._success_response("刷新列表", "已重新读取本地配置与站点数据", site_id=site_id, payload=True)

    def _action_reload_preview(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._success_response("重新加载", "已刷新新的桥接载荷", site_id=site_id, payload=True)

    def _action_add_site(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        site = create_site_with_unique_name()
        return self._success_response("新增站点", f"已创建站点 {site.get('name', '')}", site_id=site.get("id"), payload=True)

    def _action_add_provider(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        provider = create_provider_with_unique_name()
        return self._success_response(
            "新增 Provider",
            f"已创建 Provider {provider.get('name', '')}",
            site_id=site_id,
            payload=True,
            data={"provider_id": provider.get("id")},
        )

    def _action_delete_selected(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        site_name, next_id = delete_site_by_id(str(site_id or ""))
        return self._success_response("删除站点", f"已删除站点 {site_name}", site_id=next_id, payload=True)

    def _action_delete_provider(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        provider_id = str(payload.get("provider_id") or "").strip()
        if not provider_id:
            raise BridgeError("缺少 Provider ID")
        provider_name = delete_provider_by_id(provider_id)
        return self._success_response(
            "删除 Provider",
            f"已删除 Provider {provider_name}",
            site_id=site_id,
            payload=True,
            data={"provider_id": provider_id},
        )

    def _action_save_site(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        stats_data, site = self._load_site_or_raise(site_id)
        updates = collect_site_update_payload(payload)
        new_name = str(updates.get("name", site.get("name", ""))).strip()
        self._validate_unique_name(stats_data, site_id, new_name)
        saved = save_site_by_id(str(site_id or ""), updates)
        return self._success_response("保存站点", f"已保存站点 {saved.get('name', new_name)}", site_id=site_id, payload=True)

    def _action_save_provider(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        provider_id = str(payload.get("provider_id") or "").strip()
        if not provider_id:
            raise BridgeError("缺少 Provider ID")
        saved = save_provider_by_id(provider_id, payload)
        return self._success_response(
            "保存 Provider",
            f"已保存 Provider {saved.get('name', '')}",
            site_id=site_id,
            payload=True,
            data={"provider_id": provider_id},
        )

    def _action_query_site_balance(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        stats_data, site = self._load_site_or_raise(site_id)
        if not str(site.get("url") or "").strip() or not str(site.get("api_key") or "").strip():
            raise BridgeError("请先填写站点 URL 和 API Key")
        config = load_config()
        options = self._resolve_site_query_options(site, config)
        result = query_balance(
            str(site.get("api_key") or ""),
            str(site.get("url") or ""),
            subscription_api=options["balance_subscription"],
            usage_api=options["balance_usage"],
            auth_type=str(site.get("balance_auth_type") or "bearer"),
        )
        self._update_site_balance_from_result(stats_data, site_id, result)
        save_stats(stats_data)
        if "error" in result:
            return self._error_response("API 余额", str(result.get("error") or "查询失败"), site_id=site_id)
        return self._success_response("API 余额", f"{site.get('name', '')} 查询完成", site_id=site_id, payload=True, data={"result": result})

    def _action_query_all_balance(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        stats_data = load_stats()
        config = load_config()
        summary: list[dict[str, Any]] = []
        success_count = 0
        for site in stats_data.get("sites", []):
            name = str(site.get("name") or "未命名")
            url = str(site.get("url") or "")
            api_key = str(site.get("api_key") or "")
            if not url or not api_key:
                summary.append({"site": name, "success": False, "message": "配置不完整"})
                continue
            options = self._resolve_site_query_options(site, config)
            result = query_balance(
                api_key,
                url,
                subscription_api=options["balance_subscription"],
                usage_api=options["balance_usage"],
                auth_type=str(site.get("balance_auth_type") or "bearer"),
            )
            if "error" not in result:
                success_count += 1
                self._update_site_balance_from_result(stats_data, str(site.get("id") or ""), result)
            summary.append({"site": name, "success": "error" not in result, "message": result.get("error") or f"余额 {resolve_balance_summary(result)[0]}"})
        save_stats(stats_data)
        return self._success_response("查询全部余额", f"已完成 {len(summary)} 个站点，其中成功 {success_count} 个", site_id=site_id, payload=True, data={"summary": summary})

    def _action_cookie_balance(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        result, _ = query_balance_with_cookie_for_site(str(site_id or ""))
        if not result.get("success"):
            return self._error_response("账户信息", str(result.get("message") or "查询失败"), site_id=site_id)
        stats_data, site = self._load_site_or_raise(site_id)
        return self._success_response("账户信息", f"{site.get('name', '')} 账户信息获取成功", site_id=site_id, payload=True, data={"result": result})

    def _action_browser_login_helper(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        result, _ = browser_login_site(str(site_id or ""), timeout_seconds=max(60, safe_int(payload.get("timeout_seconds") or 180, 180)))
        if not result.get("success"):
            return self._error_response("获取登录态", str(result.get("message") or "登录失败"), site_id=site_id)
        return self._success_response(
            "获取登录态",
            str(result.get("message") or "已获取浏览器登录态"),
            site_id=site_id,
            payload=True,
            data={"result": result},
        )

    def _action_query_site_logs(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        if not str(site.get("url") or "").strip() or not str(site.get("api_key") or "").strip():
            raise BridgeError("请先填写站点 URL 和 API Key")
        config = load_config()
        options = self._resolve_site_query_options(site, config)
        result = query_logs(
            str(site.get("api_key") or ""),
            str(site.get("url") or ""),
            page_size=safe_int(payload.get("page_size") or options["logs_page_size"], options["logs_page_size"]),
            page=safe_int(payload.get("page") or 1, 1),
            order=str(payload.get("order") or "desc"),
            custom_api_path=options["logs"],
            proxy_url=str(site.get("proxy") or ""),
            auth_type=str(site.get("log_auth_type") or "url_key"),
        )
        self.last_site_logs[site_id or ""] = result
        if "error" in result:
            return self._error_response("当前站点日志", str(result.get("error") or "查询失败"), site_id=site_id)
        return self._success_response("当前站点日志", f"已加载 {result.get('total', 0)} 条日志", site_id=site_id, data={"logs": result})

    def _action_sync_site_models(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        result = discover_site_models(site)
        if not result.get("success"):
            return self._error_response("获取模型列表", str(result.get("message") or "获取失败"), site_id=site_id)
        return self._success_response(
            "获取模型列表",
            str(result.get("message") or "已更新模型列表"),
            site_id=site_id,
            payload=True,
            data={"result": result, "site_models": result.get("models", [])},
        )

    def _run_model_probe_action(
        self,
        site_id: str | None,
        payload: dict[str, Any],
        *,
        stream: bool,
        single: bool,
    ) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        preset_id = str(payload.get("preset_id") or "openai_relay")
        model_id = str(payload.get("model_id") or "").strip()
        result = probe_site_models(
            site,
            preset_id=preset_id,
            stream=stream,
            model_id=model_id if single else model_id,
        )
        output_lines = [
            f"[model] {item.get('model_id')} · {'成功' if item.get('success') else '失败'} · {item.get('message')}"
            for item in result.get("results", [])
        ]
        title = "模型流式探测" if stream else "模型非流探测"
        if not result.get("success") and not safe_int(result.get("success_count") or 0, 0):
            return self._error_response(title, str(result.get("message") or "探测失败"), site_id=site_id)
        return self._success_response(
            title,
            str(result.get("message") or "探测完成"),
            site_id=site_id,
            payload=True,
            data={"result": result, "site_models": result.get("site_models", [])},
            output_lines=output_lines,
        )

    def _action_probe_site_models_stream(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run_model_probe_action(site_id, payload, stream=True, single=False)

    def _action_probe_site_models_nonstream(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run_model_probe_action(site_id, payload, stream=False, single=False)

    def _action_probe_single_model_stream(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run_model_probe_action(site_id, payload, stream=True, single=True)

    def _action_probe_single_model_nonstream(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        return self._run_model_probe_action(site_id, payload, stream=False, single=True)

    def _perform_single_checkin(self, stats_data: dict[str, Any], site: dict[str, Any]) -> dict[str, Any]:
        site_id = str(site.get("id") or "")
        site_name = str(site.get("name") or "未命名")
        extra_headers = site.get("checkin_headers", {}) if isinstance(site.get("checkin_headers"), dict) else {}
        result = do_checkin(
            str(site.get("url") or ""),
            str(site.get("session_cookie") or ""),
            str(site.get("checkin_user_id") or ""),
            checkin_path=str(site.get("checkin_api_path") or "/api/user/checkin"),
            extra_headers=extra_headers,
            checkin_url=str(site.get("checkin_url") or ""),
            waf_cookie_names=site.get("waf_cookie_names", []),
            auto_get_waf_cookie=True,
        )
        if result.get("updated_cookie"):
            update_site(stats_data, site_id, {"session_cookie": str(result.get("updated_cookie") or ""), "checkin_cookie_updated_at": now_text()})
        if result.get("success"):
            add_checkin_log(site_name, site_id, True, safe_float(result.get("quota_awarded", 0)) / 500000, result.get("message", ""))
            balance_result = query_balance_by_cookie(
                str(site.get("url") or ""),
                str(result.get("updated_cookie") or site.get("session_cookie") or ""),
                str(site.get("checkin_user_id") or ""),
                extra_headers=extra_headers,
                checkin_url=str(site.get("checkin_url") or ""),
                waf_cookie_names=site.get("waf_cookie_names", []),
                auto_get_waf_cookie=False,
            )
            if balance_result.get("success"):
                update_site(
                    stats_data,
                    site_id,
                    {
                        "account_balance": safe_float(balance_result.get("balance", 0)),
                        "account_balance_unit": str(balance_result.get("unit") or "USD"),
                        "account_last_query_time": now_text(),
                        "account_status_message": str(balance_result.get("message") or ""),
                    },
                )
            return {"site": site_name, "success": True, "message": str(result.get("message") or "签到成功")}
        add_checkin_log(site_name, site_id, False, 0, result.get("message", ""))
        return {"site": site_name, "success": False, "message": str(result.get("message") or "签到失败")}

    def _action_checkin_current(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        result, _ = checkin_site(str(site_id or ""))
        if result.get("success"):
            return self._success_response("当前站点签到", result["message"], site_id=site_id, payload=True, data={"result": result})
        return self._error_response("当前站点签到", result["message"], site_id=site_id)

    def _action_checkin_all(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        outcome, _ = checkin_all_sites(open_browser=bool(payload.get("open_browser")))
        output_lines = [
            f"[{time_only()}] 批量签到完成",
            f"[{time_only()}] {outcome['message']}",
        ]
        if outcome.get("browser_sites"):
            output_lines.append(f"[{time_only()}] 已为以下站点打开登录页: {', '.join(outcome['browser_sites'])}")
        return self._success_response(
            "一键签到",
            outcome["message"],
            site_id=site_id,
            payload=True,
            data={
                "results": outcome["results"],
                "browser_sites": outcome["browser_sites"],
                "checkin_logs": [serialize_checkin_log(log) for log in outcome["checkin_logs"]],
            },
            output_lines=output_lines,
        )

    def _action_refresh_cookies(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        auto_refresh = bool(payload.get("auto_refresh", True))
        ttl_hours = int(payload.get("ttl_hours", 20))
        result = check_and_refresh_cookies(auto_refresh=auto_refresh, ttl_hours=ttl_hours)
        output_lines = [
            f"[{time_only()}] Cookie 检查完成",
            f"[{time_only()}] 检查 {result['checked']} 个站点，发现 {result['expired']} 个过期",
        ]
        if auto_refresh:
            output_lines.append(f"[{time_only()}] 成功刷新 {result['refreshed']} 个，失败 {result['failed']} 个")
        return self._success_response(
            "Cookie 自动刷新",
            f"检查 {result['checked']} 个站点，刷新 {result['refreshed']} 个",
            site_id=site_id,
            payload=True,
            data=result,
            output_lines=output_lines,
        )

    def _action_checkin_logs(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        logs = [serialize_checkin_log(record) for record in load_checkin_log()]
        return self._success_response("签到记录", f"已加载 {len(logs)} 条签到记录", site_id=site_id, data={"checkin_logs": logs})

    def _action_waf_helper(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        refresh_result, _ = refresh_site_waf_cookie(str(site_id or ""))
        if not refresh_result.get("success"):
            return self._error_response("WAF 助手", str(refresh_result.get("message") or "刷新失败"), site_id=site_id)
        return self._success_response("WAF 助手", "Cookie 已刷新", site_id=site_id, payload=True, data={"result": refresh_result})

    def _action_test_connectivity(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        result = run_connectivity_probe(site)
        if result.get("success"):
            return self._success_response("连通性测试", result.get("message", "完成"), site_id=site_id, data={"result": result})
        return self._error_response("连通性测试", result.get("message", "失败"), site_id=site_id)

    def _action_test_authenticity(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        result = run_authenticity_probe(site, payload)
        if not result.get("success"):
            return self._error_response("真伪性测试", str(result.get("error") or "测试失败"), site_id=site_id)
        return self._success_response(
            "真伪性测试",
            "测试完成",
            site_id=site_id,
            data={"result": result},
            output_lines=list(result.get("status_lines") or []),
        )

    def _action_send_chat(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        _, site = self._load_site_or_raise(site_id)
        result = run_chat_probe(site, payload)
        if not result.get("success"):
            return self._error_response("发送对话", str(result.get("error") or "请求失败"), site_id=site_id)
        return self._success_response(
            "发送对话",
            "请求完成",
            site_id=site_id,
            data={"result": result},
            output_lines=list(result.get("status_lines") or []),
        )

    def _action_detection_history(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        runs = get_recent_detection_runs(
            site_id=str(site_id or ""),
            run_type=str(payload.get("run_type") or ""),
            limit=safe_int(payload.get("limit") or 20, 20),
        )
        return self._success_response(
            "检测历史",
            f"已加载 {len(runs)} 条检测记录",
            site_id=site_id,
            data={"runs": runs},
        )

    def _action_detection_evidence(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = str(payload.get("run_id") or "").strip()
        if not run_id:
            raise BridgeError("缺少检测记录 ID")
        evidence = get_detection_run_evidence(run_id)
        if not evidence:
            raise BridgeError("未找到检测详情")
        return self._success_response(
            "检测详情",
            "已加载检测详情",
            site_id=site_id,
            data={"evidence": evidence},
        )

    def _action_action_logs(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        logs = list_action_logs(limit=safe_int(payload.get("limit") or 30, 30))
        return self._success_response(
            "动作日志",
            f"已加载 {len(logs)} 条动作日志",
            site_id=site_id,
            data={"logs": logs},
        )

    def _action_save_settings(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        config = load_config()
        if "autostart" in payload:
            set_autostart(bool(payload.get("autostart")))
        config["minimize_to_tray"] = bool(payload.get("minimize_to_tray", config.get("minimize_to_tray", True)))
        config["low_balance_threshold"] = safe_float(payload.get("low_balance_threshold", config.get("low_balance_threshold", 10)), 10)
        config.setdefault("api_endpoints", {})
        config["api_endpoints"]["logs_page_size"] = max(1, safe_int(payload.get("logs_page_size", config["api_endpoints"].get("logs_page_size", 50)), 50))
        config["auto_query"] = {
            "enabled": bool(payload.get("auto_query_enabled", config.get("auto_query", {}).get("enabled", False))),
            "interval_minutes": max(1, safe_int(payload.get("auto_query_interval", config.get("auto_query", {}).get("interval_minutes", 30)), 30)),
        }
        config["auto_checkin"] = {
            "enabled": bool(payload.get("auto_checkin_enabled", config.get("auto_checkin", {}).get("enabled", False))),
            "time": str(payload.get("auto_checkin_time", config.get("auto_checkin", {}).get("time", "09:00")) or "09:00"),
        }
        config.setdefault("debug", {})
        config["debug"]["enable_api_log"] = bool(payload.get("enable_api_log", config.get("debug", {}).get("enable_api_log", False)))
        config["action_logs"] = {
            "max_rows": max(0, safe_int(payload.get("action_log_max_rows", config.get("action_logs", {}).get("max_rows", 500)), 500)),
        }
        config.setdefault("ui", {})
        config["ui"]["theme"] = str(payload.get("theme") or config.get("ui", {}).get("theme", "flatly"))
        config["ui"]["use_background_image"] = bool(payload.get("use_background_image", config.get("ui", {}).get("use_background_image", False)))
        save_config(config)
        trim_action_logs(max_rows=max(0, safe_int(config.get("action_logs", {}).get("max_rows", 500), 500)))
        reset_debug_log_cache()
        return self._success_response("保存设置", "设置已保存", site_id=site_id, payload=True)

    def _action_save_custom_preset(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        request_format = str(payload.get("request_format") or "").strip()
        if not request_format:
            raise BridgeError("请选择请求格式")

        preset_name = str(payload.get("name") or "").strip()
        if not preset_name:
            raise BridgeError("预设名称不能为空")
        endpoint = str(payload.get("endpoint") or "").strip()
        if not endpoint:
            raise BridgeError("Endpoint 不能为空")

        preset_id = normalize_preset_id(payload.get("id"), preset_name)
        preset = {
            "id": preset_id,
            "name": preset_name,
            "description": str(payload.get("description") or "").strip(),
            "request_format": request_format,
            "endpoint": endpoint,
            "headers": parse_json_object(payload.get("headers", payload.get("headers_text")), field_name="请求头"),
            "body_template": parse_json_object(payload.get("body_template", payload.get("body_template_text")), field_name="请求体模板"),
            "auth_header": str(payload.get("auth_header") or "").strip(),
            "auth_prefix": str(payload.get("auth_prefix") or ""),
            "supports_thinking": bool(payload.get("supports_thinking", False)),
            "thinking_config": parse_json_object(payload.get("thinking_config", payload.get("thinking_config_text")), field_name="Thinking 配置"),
            "include_cli_tools": bool(payload.get("include_cli_tools", False)),
            "include_cli_system": bool(payload.get("include_cli_system", False)),
        }
        if not save_custom_preset(preset):
            raise BridgeError("保存自定义预设失败")
        return self._success_response(
            "保存自定义预设",
            f"已保存预设 {preset_name}",
            site_id=site_id,
            payload=True,
            data={"preset_id": preset_id},
        )

    def _action_delete_custom_preset(self, site_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
        preset_id = str(payload.get("id") or payload.get("preset_id") or "").strip()
        if not preset_id:
            raise BridgeError("缺少预设 ID")
        if not delete_custom_preset(preset_id):
            raise BridgeError("删除自定义预设失败")
        return self._success_response(
            "删除自定义预设",
            f"已删除预设 {preset_id}",
            site_id=site_id,
            payload=True,
            data={"preset_id": preset_id},
        )
