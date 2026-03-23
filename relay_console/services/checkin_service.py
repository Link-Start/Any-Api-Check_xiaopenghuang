from __future__ import annotations

import webbrowser
from datetime import datetime
from typing import Any

from ..providers.registry import resolve_site_profile
from ..repositories.site_repo import load_site_state, save_site_state
from ..repositories.waf_cookie_repo import get_cached_waf_cookie, save_cached_waf_cookie
from ..runtime.api import (
    capture_login_session_with_playwright,
    do_checkin,
    merge_cookie_header,
    normalize_waf_cookie_names,
    parse_cookie_header,
    query_balance_by_cookie,
    refresh_cookie_with_waf,
)
from ..runtime.stats import add_checkin_log, load_checkin_log
from .exceptions import DomainServiceError


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _find_site(data: dict[str, Any], site_id: str) -> dict[str, Any] | None:
    for site in data.get("sites", []):
        if str(site.get("id") or "") == str(site_id or ""):
            return site
    return None


def _update_site_in_state(data: dict[str, Any], site_id: str, updates: dict[str, Any]) -> None:
    site = _find_site(data, site_id)
    if site:
        site.update(updates)


def _resolve_checkin_url(site: dict[str, Any]) -> str:
    if str(site.get("checkin_url") or "").strip():
        return str(site.get("checkin_url") or "")
    provider = site.get("provider") or {}
    base_url = str(site.get("url") or "").rstrip("/")
    login_path = str(provider.get("login_path") or "").strip()
    if base_url and login_path:
        if not login_path.startswith("/"):
            login_path = "/" + login_path
        return f"{base_url}{login_path}"
    return base_url


def _extract_waf_cookie_subset(cookie_header: str, required_names: list[str]) -> dict[str, str]:
    if not required_names:
        return {}
    cookie_map = parse_cookie_header(cookie_header or "")
    lowered = {name.lower(): name for name in required_names}
    subset: dict[str, str] = {}
    for key, value in cookie_map.items():
        target = lowered.get(key.lower())
        if target:
            subset[target] = value
    return subset


def _merge_site_cookie_with_cache(site: dict[str, Any]) -> str:
    required_names = normalize_waf_cookie_names(site.get("waf_cookie_names", []))
    cookie_header = str(site.get("session_cookie") or "")
    if not required_names:
        return cookie_header

    cached = get_cached_waf_cookie(str(site.get("id") or ""))
    if not cached:
        return cookie_header

    cached_cookie_map = cached.get("cookies", {})
    if not isinstance(cached_cookie_map, dict):
        return cookie_header
    return merge_cookie_header(cookie_header, cached_cookie_map)


def _persist_waf_cache_from_cookie(site: dict[str, Any], cookie_header: str, *, source: str) -> None:
    required_names = normalize_waf_cookie_names(site.get("waf_cookie_names", []))
    if not required_names:
        return
    subset = _extract_waf_cookie_subset(cookie_header, required_names)
    if subset:
        save_cached_waf_cookie(str(site.get("id") or ""), subset, source=source)


def query_balance_with_cookie_for_site(site_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_site_state()
    site = _find_site(data, site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")

    resolved = resolve_site_profile(site)
    jwt_token = str(resolved.get("jwt_token") or "")
    session_cookie = str(resolved.get("session_cookie") or "")

    if not str(resolved.get("url") or "").strip():
        raise DomainServiceError("请先为当前站点配置 URL")
    if not jwt_token and not session_cookie:
        raise DomainServiceError("请先为当前站点配置签到凭证（Cookie 或 JWT Token）")

    effective_cookie = _merge_site_cookie_with_cache(resolved) if session_cookie else ""
    extra_headers = resolved.get("checkin_headers", {}) if isinstance(resolved.get("checkin_headers"), dict) else {}
    result = query_balance_by_cookie(
        str(resolved.get("url") or ""),
        effective_cookie,
        jwt_token,
        str(resolved.get("checkin_user_id") or ""),
        extra_headers=extra_headers,
        checkin_url=_resolve_checkin_url(resolved),
        waf_cookie_names=resolved.get("waf_cookie_names", []),
        auto_get_waf_cookie=True,
    )
    if result.get("success"):
        updates = {
            "account_balance": float(result.get("balance", 0) or 0),
            "account_balance_unit": str(result.get("unit") or "USD"),
            "account_last_query_time": _now_text(),
            "account_status_message": str(result.get("message") or ""),
        }
        updated_cookie = str(result.get("updated_cookie") or "")
        if updated_cookie:
            updates["session_cookie"] = updated_cookie
            updates["checkin_cookie_updated_at"] = _now_text()
            _persist_waf_cache_from_cookie(resolved, updated_cookie, source="balance_query")
        _update_site_in_state(data, site_id, updates)
        save_site_state(data)
    return result, data


def refresh_site_waf_cookie(site_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_site_state()
    site = _find_site(data, site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")

    resolved = resolve_site_profile(site)
    target_url = _resolve_checkin_url(resolved)
    if not str(resolved.get("url") or "").strip() or not target_url.strip():
        raise DomainServiceError("请先配置站点 URL 和签到页面地址")

    refresh_result = refresh_cookie_with_waf(
        session_cookie=str(resolved.get("session_cookie") or ""),
        base_url=str(resolved.get("url") or ""),
        target_url=target_url,
        required_cookie_names=resolved.get("waf_cookie_names", []),
        timeout_seconds=90,
        headless=False,
    )
    if refresh_result.get("success"):
        updates = {
            "session_cookie": str(refresh_result.get("cookie") or resolved.get("session_cookie") or ""),
            "checkin_cookie_updated_at": _now_text(),
        }
        _update_site_in_state(data, site_id, updates)
        _persist_waf_cache_from_cookie(
            {**resolved, **updates},
            str(updates["session_cookie"]),
            source="waf_helper",
        )
        save_site_state(data)
    return refresh_result, data


def browser_login_site(site_id: str, *, timeout_seconds: int = 180) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_site_state()
    site = _find_site(data, site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")

    resolved = resolve_site_profile(site)
    base_url = str(resolved.get("url") or "").strip()
    if not base_url:
        raise DomainServiceError("请先配置站点 URL")

    target_url = _resolve_checkin_url(resolved) or base_url
    provider = resolved.get("provider") or {}
    if provider and not provider.get("supports_browser_login") and str(resolved.get("provider_template") or "") not in {"custom", ""}:
        raise DomainServiceError("当前 Provider 未标记支持浏览器登录")

    capture_result = capture_login_session_with_playwright(
        base_url=base_url,
        target_url=target_url,
        session_cookie=str(resolved.get("session_cookie") or ""),
        timeout_seconds=timeout_seconds,
        cookie_name_candidates=["session", *list(resolved.get("waf_cookie_names", []) or [])],
    )
    if not capture_result.get("success"):
        return capture_result, data

    merged_cookie = str(capture_result.get("cookie") or "")
    updates = {
        "session_cookie": merged_cookie,
        "checkin_cookie_updated_at": _now_text(),
    }
    captured_user_id = str(capture_result.get("user_id") or "").strip()
    if captured_user_id:
        updates["checkin_user_id"] = captured_user_id
    _update_site_in_state(data, site_id, updates)
    _persist_waf_cache_from_cookie({**resolved, **updates}, merged_cookie, source="browser_login")

    verify_result = query_balance_by_cookie(
        base_url,
        merged_cookie,
        "",
        str(updates.get("checkin_user_id") or resolved.get("checkin_user_id") or ""),
        extra_headers=resolved.get("checkin_headers", {}) if isinstance(resolved.get("checkin_headers"), dict) else {},
        checkin_url=target_url,
        waf_cookie_names=resolved.get("waf_cookie_names", []),
        auto_get_waf_cookie=False,
    )
    if verify_result.get("success"):
        _update_site_in_state(
            data,
            site_id,
            {
                "account_balance": float(verify_result.get("balance", 0) or 0),
                "account_balance_unit": str(verify_result.get("unit") or "USD"),
                "account_last_query_time": _now_text(),
                "account_status_message": str(verify_result.get("message") or ""),
            },
        )
        capture_result["verify"] = verify_result
    save_site_state(data)
    return capture_result, data


def _perform_auto_checkin_via_user_info(data: dict[str, Any], site: dict[str, Any]) -> dict[str, Any]:
    effective_cookie = _merge_site_cookie_with_cache(site)
    jwt_token = str(site.get("jwt_token") or "")
    extra_headers = site.get("checkin_headers", {}) if isinstance(site.get("checkin_headers"), dict) else {}
    result = query_balance_by_cookie(
        str(site.get("url") or ""),
        effective_cookie,
        jwt_token,
        str(site.get("checkin_user_id") or ""),
        extra_headers=extra_headers,
        checkin_url=_resolve_checkin_url(site),
        waf_cookie_names=site.get("waf_cookie_names", []),
        auto_get_waf_cookie=True,
    )
    if result.get("success"):
        updates = {
            "account_balance": float(result.get("balance", 0) or 0),
            "account_balance_unit": str(result.get("unit") or "USD"),
            "account_last_query_time": _now_text(),
            "account_status_message": str(result.get("message") or ""),
        }
        updated_cookie = str(result.get("updated_cookie") or "")
        if updated_cookie:
            updates["session_cookie"] = updated_cookie
            updates["checkin_cookie_updated_at"] = _now_text()
            _persist_waf_cache_from_cookie(site, updated_cookie, source="auto_user_info")
        _update_site_in_state(data, str(site.get("id") or ""), updates)
        add_checkin_log(
            str(site.get("name") or "未命名"),
            str(site.get("id") or ""),
            True,
            0,
            "用户信息接口返回成功（自动签到模式）",
        )
        return {"site": str(site.get("name") or ""), "success": True, "message": "用户信息接口返回成功（自动签到模式）"}
    add_checkin_log(
        str(site.get("name") or "未命名"),
        str(site.get("id") or ""),
        False,
        0,
        str(result.get("message") or "自动签到失败"),
    )
    return {"site": str(site.get("name") or ""), "success": False, "message": str(result.get("message") or "自动签到失败")}


def _perform_single_checkin_in_state(data: dict[str, Any], site: dict[str, Any]) -> dict[str, Any]:
    site_id = str(site.get("id") or "")
    site_name = str(site.get("name") or "未命名")
    resolved = resolve_site_profile(site)
    if not str(resolved.get("url") or "").strip():
        return {"site": site_name, "success": False, "message": "缺少站点 URL"}

    # 支持 JWT Token 或 Session Cookie 认证
    jwt_token = str(resolved.get("jwt_token") or "")
    session_cookie = str(resolved.get("session_cookie") or "")
    if not jwt_token and not session_cookie:
        return {"site": site_name, "success": False, "message": "缺少签到凭证（Cookie 或 JWT Token）"}

    provider = resolved.get("provider") or {}
    if provider.get("auto_checkin_via_user_info") and not str(resolved.get("checkin_api_path") or "").strip():
        return _perform_auto_checkin_via_user_info(data, resolved)

    effective_cookie = _merge_site_cookie_with_cache(resolved) if session_cookie else ""
    extra_headers = resolved.get("checkin_headers", {}) if isinstance(resolved.get("checkin_headers"), dict) else {}
    result = do_checkin(
        str(resolved.get("url") or ""),
        effective_cookie,
        jwt_token,
        str(resolved.get("checkin_user_id") or ""),
        checkin_path=str(resolved.get("checkin_api_path") or "/api/user/checkin"),
        extra_headers=extra_headers,
        checkin_url=_resolve_checkin_url(resolved),
        waf_cookie_names=resolved.get("waf_cookie_names", []),
        auto_get_waf_cookie=True,
    )

    current_cookie = str(result.get("updated_cookie") or effective_cookie or "")
    if current_cookie and current_cookie != str(site.get("session_cookie") or ""):
        _update_site_in_state(
            data,
            site_id,
            {
                "session_cookie": current_cookie,
                "checkin_cookie_updated_at": _now_text(),
            },
        )
        _persist_waf_cache_from_cookie(resolved, current_cookie, source="checkin")

    if result.get("success"):
        add_checkin_log(
            site_name,
            site_id,
            True,
            float(result.get("quota_awarded", 0) or 0) / 500000,
            str(result.get("message") or "签到成功"),
        )
        balance_result = query_balance_by_cookie(
            str(resolved.get("url") or ""),
            current_cookie or str(site.get("session_cookie") or ""),
            jwt_token,
            str(resolved.get("checkin_user_id") or ""),
            extra_headers=extra_headers,
            checkin_url=_resolve_checkin_url(resolved),
            waf_cookie_names=resolved.get("waf_cookie_names", []),
            auto_get_waf_cookie=False,
        )
        if balance_result.get("success"):
            _update_site_in_state(
                data,
                site_id,
                {
                    "account_balance": float(balance_result.get("balance", 0) or 0),
                    "account_balance_unit": str(balance_result.get("unit") or "USD"),
                    "account_last_query_time": _now_text(),
                    "account_status_message": str(balance_result.get("message") or ""),
                },
            )
        return {"site": site_name, "success": True, "message": str(result.get("message") or "签到成功")}

    add_checkin_log(site_name, site_id, False, 0, str(result.get("message") or "签到失败"))
    return {"site": site_name, "success": False, "message": str(result.get("message") or "签到失败")}


def checkin_site(site_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_site_state()
    site = _find_site(data, site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")
    result = _perform_single_checkin_in_state(data, site)
    save_site_state(data)
    return result, data


def checkin_all_sites(*, open_browser: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_site_state()
    results: list[dict[str, Any]] = []
    browser_sites: list[str] = []

    for site in data.get("sites", []):
        # 只有公益站才有签到功能，订阅站和付费站跳过
        site_type = str(site.get("type") or "paid").strip().lower()
        if site_type != "free":
            continue

        resolved = resolve_site_profile(site)
        has_checkin = (
            bool(str(resolved.get("checkin_url") or "").strip())
            or bool(str(resolved.get("checkin_api_path") or "").strip())
            or bool((resolved.get("provider") or {}).get("auto_checkin_via_user_info"))
        )
        if not has_checkin:
            continue

        # 有认证凭证（Cookie 或 JWT Token）的站点直接 API 签到
        has_auth = bool(str(resolved.get("session_cookie") or "").strip() or str(resolved.get("jwt_token") or "").strip())
        if has_auth and str(resolved.get("url") or "").strip():
            result = _perform_single_checkin_in_state(data, site)
            results.append(result)
            # 公益站签到失败，自动打开浏览器签到页
            if not result.get("success"):
                target_url = _resolve_checkin_url(resolved) or str(resolved.get("url") or "")
                if target_url.strip():
                    browser_sites.append(str(site.get("name") or "未命名"))
                    webbrowser.open(target_url)
            continue

        # 无凭证的公益站，也打开浏览器
        target_url = _resolve_checkin_url(resolved) or str(resolved.get("url") or "")
        if target_url.strip():
            browser_sites.append(str(site.get("name") or "未命名"))
            webbrowser.open(target_url)

    save_site_state(data)
    success_count = sum(1 for item in results if item.get("success"))
    message = f"已处理 {len(results)} 个 API 签到站点，成功 {success_count} 个"
    if browser_sites:
        message += f"；另有 {len(browser_sites)} 个站点需要浏览器辅助"
    return {
        "results": results,
        "browser_sites": browser_sites,
        "message": message,
        "checkin_logs": load_checkin_log(),
    }, data
