from __future__ import annotations

import uuid

from ..repositories.provider_repo import (
    count_sites_using_provider,
    create_provider,
    delete_provider,
    get_provider,
    list_providers,
    update_provider,
)
from .exceptions import DomainServiceError


def _validate_provider_name_uniqueness(provider_id: str | None, name: str) -> None:
    normalized = str(name or "").strip().casefold()
    if not normalized:
        raise DomainServiceError("Provider 名称不能为空")
    for provider in list_providers():
        if provider.get("id") == provider_id:
            continue
        if str(provider.get("name") or "").strip().casefold() == normalized:
            raise DomainServiceError(f"Provider 名称重复: {name}")


def create_provider_with_unique_name(base_name: str = "自定义 Provider") -> dict:
    providers = list_providers()
    existing_names = {str(provider.get("name") or "").strip().casefold() for provider in providers}
    new_name = base_name
    suffix = 2
    while new_name.casefold() in existing_names:
        new_name = f"{base_name}{suffix}"
        suffix += 1

    provider_id = f"provider-{uuid.uuid4().hex[:8]}"
    provider = {
        "id": provider_id,
        "name": new_name,
        "description": "",
        "login_path": "/login",
        "sign_in_path": "/api/user/checkin",
        "user_info_path": "/api/user/self",
        "api_user_key": "new-api-user",
        "waf_cookie_names": [],
        "supports_cookie_auth": True,
        "supports_browser_login": False,
        "auto_checkin_via_user_info": False,
    }
    create_provider(provider)
    created = get_provider(provider_id)
    if not created:
        raise DomainServiceError("创建 Provider 失败")
    return created


def save_provider_by_id(provider_id: str, updates: dict) -> dict:
    existing = get_provider(provider_id)
    if not existing:
        raise DomainServiceError("Provider 不存在或已被删除")
    if existing.get("is_builtin"):
        raise DomainServiceError("内置 Provider 不允许直接修改")

    name = str(updates.get("name") or existing.get("name") or "").strip()
    _validate_provider_name_uniqueness(provider_id, name)
    success = update_provider(provider_id, updates)
    if not success:
        raise DomainServiceError("保存 Provider 失败")
    saved = get_provider(provider_id)
    if not saved:
        raise DomainServiceError("保存后无法读取 Provider")
    return saved


def delete_provider_by_id(provider_id: str) -> str:
    existing = get_provider(provider_id)
    if not existing:
        raise DomainServiceError("Provider 不存在或已被删除")
    if existing.get("is_builtin"):
        raise DomainServiceError("内置 Provider 不允许删除")
    usage_count = count_sites_using_provider(provider_id)
    if usage_count > 0:
        raise DomainServiceError(f"当前仍有 {usage_count} 个站点在使用该 Provider，无法删除")
    success = delete_provider(provider_id)
    if not success:
        raise DomainServiceError("删除 Provider 失败")
    return str(existing.get("name") or "")
