"""Any-API-Check local utility functions."""

from __future__ import annotations

import json
import platform
import sys

from ..paths import APP_ROOT, CONFIG_TEMPLATES_DIR, RUNTIME_ROOT
from .db import DEFAULT_CONFIG, ensure_db, get_db_path, load_config_payload, save_config_payload

if platform.system() == "Windows":
    import winreg
else:
    winreg = None


APP_NAME = "Any-API-Check"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
CONFIG_FILE = CONFIG_TEMPLATES_DIR / "config.json"


def get_exe_dir() -> str:
    return str(APP_ROOT)


def get_resource_dir() -> str:
    return str(APP_ROOT)


def resource_path(relative_path: str) -> str:
    return str(APP_ROOT / relative_path)


def get_config_public_path() -> str:
    return str(CONFIG_FILE)


def get_config_local_path() -> str:
    return get_db_path()


def get_config_path() -> str:
    return get_db_path()


def get_data_dir() -> str:
    return str(RUNTIME_ROOT)


def _load_public_config_template() -> dict:
    if CONFIG_FILE.exists():
        try:
            parsed = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, OSError):
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))


def load_config() -> dict:
    ensure_db()
    return load_config_payload(default_config=_load_public_config_template())


def save_config(config: dict) -> None:
    ensure_db()
    save_config_payload(config)


def get_exe_path() -> str:
    if getattr(sys, "frozen", False):
        return sys.executable
    main_py = APP_ROOT / "app.py"
    return f'"{sys.executable}" "{main_py}"'


def is_autostart_enabled() -> bool:
    if winreg is None:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def set_autostart(enable: bool) -> bool:
    if winreg is None:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_exe_path())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def format_compact_number(number):
    if number is None:
        return "0"
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return f"{int(number)}"


def describe_http_response(status_code: int, text: str, content_type: str = "") -> str:
    content = (text or "").strip()
    lower = content.lower()
    ct = (content_type or "").lower()
    is_cf = (
        "cloudflare" in lower
        or "cf-ray" in lower
        or "cf-error" in lower
        or "error code 502" in lower
        or "error code 503" in lower
        or "error code 504" in lower
    )
    if status_code >= 500 and (is_cf or "text/html" in ct or lower.startswith("<!doctype html")):
        return "Cloudflare/源站 5xx 错误：上游异常或暂时不可用"
    if "text/html" in ct or lower.startswith("<!doctype html"):
        return "返回 HTML 页面，可能被 WAF 拦截或登录态失效"
    if content:
        preview = content[:200] + ("..." if len(content) > 200 else "")
        return preview
    return "空响应或未知错误"
