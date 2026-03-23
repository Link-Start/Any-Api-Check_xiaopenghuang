from __future__ import annotations

from ..runtime.stats import (
    add_site,
    create_site,
    delete_site,
    get_site_by_id,
    load_stats,
    save_stats,
    update_site,
)


def load_site_state() -> dict:
    return load_stats()


def save_site_state(data: dict) -> bool:
    return save_stats(data)


def get_site(site_id: str) -> dict | None:
    data = load_stats()
    return get_site_by_id(data, site_id)


def create_site_record(name: str, url: str = "https://", site_type: str = "paid", api_key: str = "") -> dict:
    data = load_stats()
    site = create_site(name=name, url=url, site_type=site_type, api_key=api_key)
    add_site(data, site)
    save_stats(data)
    return site


def update_site_record(site_id: str, updates: dict) -> bool:
    data = load_stats()
    success = update_site(data, site_id, updates)
    if success:
        save_stats(data)
    return success


def delete_site_record(site_id: str) -> tuple[bool, str]:
    data = load_stats()
    success = delete_site(data, site_id)
    next_id = data.get("sites", [{}])[0].get("id", "") if data.get("sites") else ""
    if success:
        save_stats(data)
    return success, str(next_id or "")
