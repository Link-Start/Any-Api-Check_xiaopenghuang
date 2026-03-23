from __future__ import annotations

from copy import deepcopy

from ..repositories.provider_repo import get_provider


def resolve_site_profile(site: dict) -> dict:
    merged = deepcopy(site)
    provider_id = str(merged.get("provider_template") or "custom").strip() or "custom"
    provider = get_provider(provider_id)
    if not provider:
        provider = get_provider("custom")

    if provider:
        merged["provider"] = provider
        if not str(merged.get("checkin_api_path") or "").strip():
            merged["checkin_api_path"] = str(provider.get("sign_in_path") or "")
        if not merged.get("waf_cookie_names"):
            merged["waf_cookie_names"] = list(provider.get("waf_cookie_names", []) or [])
        if not str(merged.get("checkin_url") or "").strip():
            base_url = str(merged.get("url") or "").rstrip("/")
            login_path = str(provider.get("login_path") or "").strip()
            if base_url and login_path:
                if not login_path.startswith("/"):
                    login_path = "/" + login_path
                merged["checkin_url"] = f"{base_url}{login_path}"
    else:
        merged["provider"] = None
    return merged
