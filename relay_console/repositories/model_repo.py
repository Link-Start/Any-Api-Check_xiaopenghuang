from __future__ import annotations

from ..runtime.db import list_site_models_payload, replace_site_models_payload, update_site_model_probe_payload


def list_site_models(site_id: str = "") -> list[dict]:
    return list_site_models_payload(site_id=site_id)


def replace_site_models(site_id: str, models: list[dict], *, source: str = "api_models") -> None:
    replace_site_models_payload(site_id, models, source=source)


def update_site_model_probe(
    site_id: str,
    model_id: str,
    *,
    stream: bool,
    status: str,
    checked_at: str,
    latency_ms: int | None,
    message: str,
    request_format: str = "",
    preset_id: str = "",
    display_name: str = "",
) -> None:
    update_site_model_probe_payload(
        site_id,
        model_id,
        stream=stream,
        status=status,
        checked_at=checked_at,
        latency_ms=latency_ms,
        message=message,
        request_format=request_format,
        preset_id=preset_id,
        display_name=display_name,
    )
