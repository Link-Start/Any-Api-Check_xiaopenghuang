from __future__ import annotations

from ..runtime.db import (
    count_sites_using_provider_payload,
    create_provider_payload,
    delete_provider_payload,
    get_provider_payload,
    load_provider_payloads,
    update_provider_payload,
)


def list_providers() -> list[dict]:
    return load_provider_payloads()


def get_provider(provider_id: str) -> dict | None:
    return get_provider_payload(provider_id)


def create_provider(provider: dict) -> None:
    create_provider_payload(provider)


def update_provider(provider_id: str, updates: dict) -> bool:
    return update_provider_payload(provider_id, updates)


def delete_provider(provider_id: str) -> bool:
    return delete_provider_payload(provider_id)


def count_sites_using_provider(provider_id: str) -> int:
    return count_sites_using_provider_payload(provider_id)
