from __future__ import annotations

from ..runtime.db import (
    delete_waf_cookie_cache_payload,
    load_waf_cookie_cache_payload,
    save_waf_cookie_cache_payload,
)


def get_cached_waf_cookie(site_id: str) -> dict | None:
    return load_waf_cookie_cache_payload(site_id)


def save_cached_waf_cookie(site_id: str, cookies: dict, *, source: str = "playwright") -> None:
    save_waf_cookie_cache_payload(site_id, cookies, source=source)


def delete_cached_waf_cookie(site_id: str) -> None:
    delete_waf_cookie_cache_payload(site_id)
