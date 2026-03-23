from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ..repositories.site_repo import load_site_state
from .checkin_service import refresh_site_waf_cookie


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _is_cookie_expired(updated_at: str, ttl_hours: int = 20) -> bool:
    """检查 Cookie 是否即将过期（默认 20 小时，留 4 小时缓冲）"""
    if not updated_at:
        return True
    last_update = _parse_datetime(updated_at)
    if not last_update:
        return True
    expiry_time = last_update + timedelta(hours=ttl_hours)
    return datetime.now() >= expiry_time


def check_and_refresh_cookies(*, auto_refresh: bool = True, ttl_hours: int = 20) -> dict[str, Any]:
    """检查所有站点的 Cookie 状态，自动刷新即将过期的"""
    data = load_site_state()
    sites = data.get("sites", [])

    results = []
    expired_count = 0
    refreshed_count = 0
    failed_count = 0

    for site in sites:
        site_id = str(site.get("id") or "")
        site_name = str(site.get("name") or "未命名")
        updated_at = str(site.get("checkin_cookie_updated_at") or "")

        if not _is_cookie_expired(updated_at, ttl_hours):
            continue

        expired_count += 1

        if not auto_refresh:
            results.append({
                "site_id": site_id,
                "site_name": site_name,
                "status": "expired",
                "message": "Cookie 即将过期"
            })
            continue

        try:
            refresh_result, _ = refresh_site_waf_cookie(site_id)
            if refresh_result.get("success"):
                refreshed_count += 1
                results.append({
                    "site_id": site_id,
                    "site_name": site_name,
                    "status": "refreshed",
                    "message": "已自动刷新"
                })
            else:
                failed_count += 1
                results.append({
                    "site_id": site_id,
                    "site_name": site_name,
                    "status": "failed",
                    "message": str(refresh_result.get("message") or "刷新失败")
                })
        except Exception as e:
            failed_count += 1
            results.append({
                "site_id": site_id,
                "site_name": site_name,
                "status": "error",
                "message": f"刷新异常: {str(e)}"
            })

    return {
        "checked": len(sites),
        "expired": expired_count,
        "refreshed": refreshed_count,
        "failed": failed_count,
        "results": results
    }
