from __future__ import annotations

from ..repositories.site_repo import create_site_record, delete_site_record, get_site, load_site_state, update_site_record
from .exceptions import DomainServiceError


def create_site_with_unique_name(base_name: str = "新站点") -> dict:
    data = load_site_state()
    existing = {str(site.get("name") or "").strip().casefold() for site in data.get("sites", [])}
    new_name = base_name
    suffix = 2
    while new_name.casefold() in existing:
        new_name = f"{base_name}{suffix}"
        suffix += 1
    site = create_site_record(name=new_name, url="https://", site_type="paid", api_key="")
    site.setdefault("checkin_api_path", "/api/user/checkin")
    update_site_record(site["id"], {"checkin_api_path": "/api/user/checkin", "provider_template": "custom"})
    return get_site(site["id"]) or site


def delete_site_by_id(site_id: str) -> tuple[str, str]:
    site = get_site(site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")
    success, next_id = delete_site_record(site_id)
    if not success:
        raise DomainServiceError("删除站点失败")
    return str(site.get("name") or ""), next_id


def save_site_by_id(site_id: str, updates: dict) -> dict:
    site = get_site(site_id)
    if not site:
        raise DomainServiceError("站点不存在或已被删除")
    if "url" in updates:
        updates["url"] = str(updates.get("url") or "").rstrip("/")
    success = update_site_record(site_id, updates)
    if not success:
        raise DomainServiceError("保存站点失败")
    saved = get_site(site_id)
    if not saved:
        raise DomainServiceError("保存后无法读取站点")
    return saved
