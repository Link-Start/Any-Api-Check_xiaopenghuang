from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_NAME = "Any-API-Check"
PACKAGE_ROOT = Path(__file__).resolve().parent
APP_ROOT = PACKAGE_ROOT.parent
PACKAGE_CONFIG_DIR = APP_ROOT / "config"
CONFIG_TEMPLATES_DIR = PACKAGE_CONFIG_DIR / "templates"
CONFIG_PRESETS_DIR = PACKAGE_CONFIG_DIR / "presets"
WEB_DIR = PACKAGE_ROOT / "web"
DOCS_DIR = APP_ROOT / "docs"


def _resolve_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / APP_NAME
    return APP_ROOT


RUNTIME_ROOT = _resolve_runtime_root()
CONFIG_DIR = RUNTIME_ROOT / "config"
DEBUG_DIR = RUNTIME_ROOT / "debug"


def _move_if_missing(source: Path, target: Path) -> None:
    if not source.exists() or target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(source), str(target))
    except OSError:
        pass


def _migrate_legacy_runtime_data() -> None:
    if RUNTIME_ROOT == APP_ROOT:
        return

    legacy_config_dir = APP_ROOT / "config"
    _move_if_missing(legacy_config_dir / "app.db", CONFIG_DIR / "app.db")
    _move_if_missing(legacy_config_dir / "app.db-shm", CONFIG_DIR / "app.db-shm")
    _move_if_missing(legacy_config_dir / "app.db-wal", CONFIG_DIR / "app.db-wal")
    _move_if_missing(legacy_config_dir / "browser_profiles", CONFIG_DIR / "browser_profiles")
    _move_if_missing(
        legacy_config_dir / "presets" / "api_presets.json",
        CONFIG_DIR / "presets" / "api_presets.json",
    )
    _move_if_missing(APP_ROOT / "debug", DEBUG_DIR)


_migrate_legacy_runtime_data()
