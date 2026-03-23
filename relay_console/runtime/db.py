from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Any

from ..paths import CONFIG_DIR
from ..providers.templates import BUILTIN_PROVIDER_TEMPLATES

DB_PATH = CONFIG_DIR / "app.db"
WAF_CACHE_TTL_HOURS = 24
_db_lock = threading.RLock()

DEFAULT_CONFIG: dict[str, Any] = {
    "profiles": [],
    "minimize_to_tray": False,
    "low_balance_threshold": 10.0,
    "api_endpoints": {
        "logs_page_size": 50,
    },
    "auto_query": {
        "enabled": False,
        "interval_minutes": 30,
    },
    "debug": {
        "enable_api_log": False,
    },
    "action_logs": {
        "max_rows": 500,
    },
    "ui": {
        "theme": "cosmo",
        "use_background_image": False,
    },
    "auto_checkin": {
        "enabled": False,
        "time": "09:00",
    },
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    payload TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sites (
    id TEXT PRIMARY KEY,
    sort_order INTEGER NOT NULL DEFAULT 0,
    name TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'paid',
    tags_json TEXT NOT NULL DEFAULT '[]',
    balance REAL NOT NULL DEFAULT 0,
    balance_unit TEXT NOT NULL DEFAULT 'USD',
    api_balance REAL NOT NULL DEFAULT 0,
    api_balance_unit TEXT NOT NULL DEFAULT 'USD',
    api_last_query_time TEXT NOT NULL DEFAULT '',
    account_balance REAL NOT NULL DEFAULT 0,
    account_balance_unit TEXT NOT NULL DEFAULT 'USD',
    account_last_query_time TEXT NOT NULL DEFAULT '',
    account_status_message TEXT NOT NULL DEFAULT '',
    last_query_time TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    api_key TEXT NOT NULL DEFAULT '',
    checkin_url TEXT NOT NULL DEFAULT '',
    checkin_api_path TEXT NOT NULL DEFAULT '/api/user/checkin',
    session_cookie TEXT NOT NULL DEFAULT '',
    checkin_headers_json TEXT NOT NULL DEFAULT '{}',
    provider_template TEXT NOT NULL DEFAULT '',
    waf_cookie_names_json TEXT NOT NULL DEFAULT '[]',
    checkin_cookie_updated_at TEXT NOT NULL DEFAULT '',
    checkin_user_id TEXT NOT NULL DEFAULT '',
    balance_auth_type TEXT NOT NULL DEFAULT 'bearer',
    log_auth_type TEXT NOT NULL DEFAULT 'url_key',
    proxy TEXT NOT NULL DEFAULT '',
    jwt_token TEXT NOT NULL DEFAULT '',
    endpoints_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS recharge_records (
    id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    date TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkin_logs (
    id TEXT PRIMARY KEY,
    sort_order INTEGER NOT NULL DEFAULT 0,
    time TEXT NOT NULL DEFAULT '',
    site_name TEXT NOT NULL DEFAULT '',
    site_id TEXT NOT NULL DEFAULT '',
    success INTEGER NOT NULL DEFAULT 0,
    quota_awarded REAL NOT NULL DEFAULT 0,
    message TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    login_path TEXT NOT NULL DEFAULT '/login',
    sign_in_path TEXT NOT NULL DEFAULT '/api/user/checkin',
    user_info_path TEXT NOT NULL DEFAULT '/api/user/self',
    api_user_key TEXT NOT NULL DEFAULT 'new-api-user',
    waf_cookie_names_json TEXT NOT NULL DEFAULT '[]',
    supports_cookie_auth INTEGER NOT NULL DEFAULT 1,
    supports_browser_login INTEGER NOT NULL DEFAULT 0,
    auto_checkin_via_user_info INTEGER NOT NULL DEFAULT 0,
    is_builtin INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS waf_cookie_cache (
    site_id TEXT PRIMARY KEY,
    cookie_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS site_models (
    site_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    display_name TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'api_models',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_stream_status TEXT NOT NULL DEFAULT '',
    last_stream_checked_at TEXT NOT NULL DEFAULT '',
    last_stream_latency_ms INTEGER,
    last_nonstream_status TEXT NOT NULL DEFAULT '',
    last_nonstream_checked_at TEXT NOT NULL DEFAULT '',
    last_nonstream_latency_ms INTEGER,
    last_message TEXT NOT NULL DEFAULT '',
    last_request_format TEXT NOT NULL DEFAULT '',
    last_preset_id TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (site_id, model_id),
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS detection_profiles (
    id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    request_format TEXT NOT NULL DEFAULT '',
    preset_id TEXT NOT NULL DEFAULT '',
    model_id TEXT NOT NULL DEFAULT '',
    probe_types_json TEXT NOT NULL DEFAULT '[]',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS detection_runs (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL DEFAULT '',
    site_id TEXT NOT NULL DEFAULT '',
    run_type TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    latency_ms INTEGER,
    message TEXT NOT NULL DEFAULT '',
    request_format TEXT NOT NULL DEFAULT '',
    preset_id TEXT NOT NULL DEFAULT '',
    model_id TEXT NOT NULL DEFAULT '',
    detected_model TEXT NOT NULL DEFAULT '',
    authenticity_score REAL NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS detection_evidence (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    request_json TEXT NOT NULL DEFAULT '{}',
    response_text TEXT NOT NULL DEFAULT '',
    parsed_result_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (run_id) REFERENCES detection_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS action_logs (
    id TEXT PRIMARY KEY,
    action_key TEXT NOT NULL DEFAULT '',
    site_id TEXT NOT NULL DEFAULT '',
    success INTEGER NOT NULL DEFAULT 0,
    title TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL DEFAULT '',
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sites_sort_order ON sites(sort_order);
CREATE INDEX IF NOT EXISTS idx_recharge_site_sort ON recharge_records(site_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_checkin_logs_sort_order ON checkin_logs(sort_order);
CREATE INDEX IF NOT EXISTS idx_checkin_logs_site_id ON checkin_logs(site_id);
CREATE INDEX IF NOT EXISTS idx_providers_builtin ON providers(is_builtin, id);
CREATE INDEX IF NOT EXISTS idx_waf_cookie_cache_expires_at ON waf_cookie_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_site_models_site_id ON site_models(site_id, model_id);
CREATE INDEX IF NOT EXISTS idx_detection_profiles_site_id ON detection_profiles(site_id);
CREATE INDEX IF NOT EXISTS idx_detection_runs_site_started_at ON detection_runs(site_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_detection_runs_type_started_at ON detection_runs(run_type, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_detection_evidence_run_id ON detection_evidence(run_id);
CREATE INDEX IF NOT EXISTS idx_action_logs_created_at ON action_logs(created_at DESC);
"""


def get_db_path() -> str:
    return str(DB_PATH)


def _connect() -> sqlite3.Connection:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _seed_builtin_providers(conn: sqlite3.Connection) -> None:
    for provider in BUILTIN_PROVIDER_TEMPLATES:
        conn.execute(
            """
            INSERT INTO providers (
                id, name, description, login_path, sign_in_path, user_info_path,
                api_user_key, waf_cookie_names_json, supports_cookie_auth,
                supports_browser_login, auto_checkin_via_user_info, is_builtin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                login_path = excluded.login_path,
                sign_in_path = excluded.sign_in_path,
                user_info_path = excluded.user_info_path,
                api_user_key = excluded.api_user_key,
                waf_cookie_names_json = excluded.waf_cookie_names_json,
                supports_cookie_auth = excluded.supports_cookie_auth,
                supports_browser_login = excluded.supports_browser_login,
                auto_checkin_via_user_info = excluded.auto_checkin_via_user_info,
                is_builtin = 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                provider["id"],
                provider["name"],
                provider["description"],
                provider["login_path"],
                provider["sign_in_path"],
                provider["user_info_path"],
                provider["api_user_key"],
                json.dumps(provider["waf_cookie_names"], ensure_ascii=False),
                1 if provider["supports_cookie_auth"] else 0,
                1 if provider["supports_browser_login"] else 0,
                1 if provider["auto_checkin_via_user_info"] else 0,
            ),
        )


def _ensure_table_columns(conn: sqlite3.Connection, table_name: str, columns: dict[str, str]) -> None:
    existing = {
        str(row["name"] or "")
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    for column_name, column_spec in columns.items():
        if column_name in existing:
            continue
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_spec}")


def ensure_db() -> str:
    with _connect() as conn:
        conn.executescript(SCHEMA)
        _ensure_table_columns(
            conn,
            "sites",
            {
                "api_balance": "REAL NOT NULL DEFAULT 0",
                "api_balance_unit": "TEXT NOT NULL DEFAULT 'USD'",
                "api_last_query_time": "TEXT NOT NULL DEFAULT ''",
                "account_balance": "REAL NOT NULL DEFAULT 0",
                "account_balance_unit": "TEXT NOT NULL DEFAULT 'USD'",
                "account_last_query_time": "TEXT NOT NULL DEFAULT ''",
                "account_status_message": "TEXT NOT NULL DEFAULT ''",
            },
        )
        _seed_builtin_providers(conn)
    return str(DB_PATH)


def _clone_default(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _parse_json(text: str | None, default: Any) -> Any:
    if not text:
        return _clone_default(default)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _clone_default(default)


def load_config_payload(default_config: dict[str, Any] | None = None) -> dict[str, Any]:
    ensure_db()
    with _connect() as conn:
        row = conn.execute("SELECT payload FROM app_settings WHERE id = 1").fetchone()
    if row and row["payload"]:
        parsed = _parse_json(row["payload"], default_config or DEFAULT_CONFIG)
        if isinstance(parsed, dict):
            return parsed
    return _clone_default(default_config or DEFAULT_CONFIG)


def save_config_payload(config: dict[str, Any]) -> None:
    ensure_db()
    payload = json.dumps(config, ensure_ascii=False)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (id, payload)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = CURRENT_TIMESTAMP
            """,
            (payload,),
        )


def _site_from_row(row: sqlite3.Row) -> dict[str, Any]:
    legacy_balance = float(row["balance"] or 0)
    legacy_balance_unit = str(row["balance_unit"] or "USD")
    legacy_last_query_time = str(row["last_query_time"] or "")
    return {
        "id": str(row["id"] or ""),
        "name": str(row["name"] or ""),
        "url": str(row["url"] or ""),
        "type": str(row["type"] or "paid"),
        "tags": _parse_json(row["tags_json"], []),
        "balance": legacy_balance,
        "balance_unit": legacy_balance_unit,
        "last_query_time": legacy_last_query_time,
        "api_balance": float(row["api_balance"] or legacy_balance),
        "api_balance_unit": str(row["api_balance_unit"] or legacy_balance_unit),
        "api_last_query_time": str(row["api_last_query_time"] or legacy_last_query_time),
        "account_balance": float(row["account_balance"] or 0),
        "account_balance_unit": str(row["account_balance_unit"] or "USD"),
        "account_last_query_time": str(row["account_last_query_time"] or ""),
        "account_status_message": str(row["account_status_message"] or ""),
        "notes": str(row["notes"] or ""),
        "api_key": str(row["api_key"] or ""),
        "checkin_url": str(row["checkin_url"] or ""),
        "checkin_api_path": str(row["checkin_api_path"] or ""),
        "session_cookie": str(row["session_cookie"] or ""),
        "checkin_headers": _parse_json(row["checkin_headers_json"], {}),
        "provider_template": str(row["provider_template"] or ""),
        "waf_cookie_names": _parse_json(row["waf_cookie_names_json"], []),
        "checkin_cookie_updated_at": str(row["checkin_cookie_updated_at"] or ""),
        "checkin_user_id": str(row["checkin_user_id"] or ""),
        "balance_auth_type": str(row["balance_auth_type"] or "bearer"),
        "log_auth_type": str(row["log_auth_type"] or "url_key"),
        "proxy": str(row["proxy"] or ""),
        "jwt_token": str(row["jwt_token"] or ""),
        "endpoints": _parse_json(row["endpoints_json"], {}),
        "recharge_records": [],
    }


def load_sites_payload() -> list[dict[str, Any]]:
    with _db_lock:
        ensure_db()
        with _connect() as conn:
            site_rows = conn.execute(
                "SELECT * FROM sites ORDER BY sort_order ASC, name COLLATE NOCASE ASC, id ASC"
            ).fetchall()
            recharge_rows = conn.execute(
                "SELECT * FROM recharge_records ORDER BY sort_order ASC, id ASC"
            ).fetchall()

        sites = [_site_from_row(row) for row in site_rows]
        site_map = {site["id"]: site for site in sites}
        for row in recharge_rows:
            site = site_map.get(str(row["site_id"] or ""))
            if not site:
                continue
            site["recharge_records"].append(
                {
                    "id": str(row["id"] or ""),
                    "date": str(row["date"] or ""),
                    "amount": float(row["amount"] or 0),
                    "note": str(row["note"] or ""),
                }
            )
        return sites


def save_sites_payload(sites: list[dict[str, Any]]) -> None:
    with _db_lock:
        ensure_db()
        normalized_sites = sites if isinstance(sites, list) else []
        with _connect() as conn:
            site_ids = [str(site.get("id") or "") for site in normalized_sites if str(site.get("id") or "")]
            if site_ids:
                placeholders = ", ".join("?" for _ in site_ids)
                conn.execute(
                    f"DELETE FROM recharge_records WHERE site_id NOT IN ({placeholders})",
                    site_ids,
                )
                conn.execute(
                    f"DELETE FROM sites WHERE id NOT IN ({placeholders})",
                    site_ids,
                )
            else:
                conn.execute("DELETE FROM recharge_records")
                conn.execute("DELETE FROM sites")

            for site_index, site in enumerate(normalized_sites):
                site_id = str(site.get("id") or "")
                if not site_id:
                    continue
                conn.execute(
                """
                INSERT INTO sites (
                    id, sort_order, name, url, type, tags_json, balance, balance_unit,
                    api_balance, api_balance_unit, api_last_query_time,
                    account_balance, account_balance_unit, account_last_query_time, account_status_message,
                    last_query_time, notes, api_key, checkin_url, checkin_api_path,
                    session_cookie, checkin_headers_json, provider_template,
                    waf_cookie_names_json, checkin_cookie_updated_at, checkin_user_id,
                    balance_auth_type, log_auth_type, proxy, jwt_token, endpoints_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    sort_order = excluded.sort_order,
                    name = excluded.name,
                    url = excluded.url,
                    type = excluded.type,
                    tags_json = excluded.tags_json,
                    balance = excluded.balance,
                    balance_unit = excluded.balance_unit,
                    api_balance = excluded.api_balance,
                    api_balance_unit = excluded.api_balance_unit,
                    api_last_query_time = excluded.api_last_query_time,
                    account_balance = excluded.account_balance,
                    account_balance_unit = excluded.account_balance_unit,
                    account_last_query_time = excluded.account_last_query_time,
                    account_status_message = excluded.account_status_message,
                    last_query_time = excluded.last_query_time,
                    notes = excluded.notes,
                    api_key = excluded.api_key,
                    checkin_url = excluded.checkin_url,
                    checkin_api_path = excluded.checkin_api_path,
                    session_cookie = excluded.session_cookie,
                    checkin_headers_json = excluded.checkin_headers_json,
                    provider_template = excluded.provider_template,
                    waf_cookie_names_json = excluded.waf_cookie_names_json,
                    checkin_cookie_updated_at = excluded.checkin_cookie_updated_at,
                    checkin_user_id = excluded.checkin_user_id,
                    balance_auth_type = excluded.balance_auth_type,
                    log_auth_type = excluded.log_auth_type,
                    proxy = excluded.proxy,
                    jwt_token = excluded.jwt_token,
                    endpoints_json = excluded.endpoints_json
                """,
                (
                    site_id,
                    site_index,
                    str(site.get("name") or ""),
                    str(site.get("url") or ""),
                    str(site.get("type") or "paid"),
                    json.dumps(site.get("tags", []) or [], ensure_ascii=False),
                    float(site.get("balance") or 0),
                    str(site.get("balance_unit") or "USD"),
                    float(site.get("api_balance", site.get("balance", 0)) or 0),
                    str(site.get("api_balance_unit", site.get("balance_unit", "USD")) or "USD"),
                    str(site.get("api_last_query_time", site.get("last_query_time", "")) or ""),
                    float(site.get("account_balance") or 0),
                    str(site.get("account_balance_unit") or "USD"),
                    str(site.get("account_last_query_time") or ""),
                    str(site.get("account_status_message") or ""),
                    str(site.get("last_query_time") or ""),
                    str(site.get("notes") or ""),
                    str(site.get("api_key") or ""),
                    str(site.get("checkin_url") or ""),
                    str(site.get("checkin_api_path") or "/api/user/checkin"),
                    str(site.get("session_cookie") or ""),
                    json.dumps(site.get("checkin_headers", {}) or {}, ensure_ascii=False),
                    str(site.get("provider_template") or ""),
                    json.dumps(site.get("waf_cookie_names", []) or [], ensure_ascii=False),
                    str(site.get("checkin_cookie_updated_at") or ""),
                    str(site.get("checkin_user_id") or ""),
                    str(site.get("balance_auth_type") or "bearer"),
                    str(site.get("log_auth_type") or "url_key"),
                    str(site.get("proxy") or ""),
                    str(site.get("jwt_token") or ""),
                    json.dumps(site.get("endpoints", {}) or {}, ensure_ascii=False),
                ),
                )
                conn.execute("DELETE FROM recharge_records WHERE site_id = ?", (site_id,))
                recharge_records = site.get("recharge_records", []) or []
                for record_index, record in enumerate(recharge_records):
                    record_id = str(record.get("id") or "")
                    if not record_id:
                        continue
                    conn.execute(
                        """
                        INSERT INTO recharge_records (id, site_id, sort_order, date, amount, note)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record_id,
                            site_id,
                            record_index,
                            str(record.get("date") or ""),
                            float(record.get("amount") or 0),
                            str(record.get("note") or ""),
                        ),
                    )


def load_checkin_logs_payload() -> list[dict[str, Any]]:
    ensure_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM checkin_logs ORDER BY sort_order ASC, id ASC"
        ).fetchall()
    return [
        {
            "id": str(row["id"] or ""),
            "time": str(row["time"] or ""),
            "site_name": str(row["site_name"] or ""),
            "site_id": str(row["site_id"] or ""),
            "success": bool(row["success"]),
            "quota_awarded": float(row["quota_awarded"] or 0),
            "message": str(row["message"] or ""),
        }
        for row in rows
    ]


def save_checkin_logs_payload(logs: list[dict[str, Any]]) -> None:
    ensure_db()
    normalized_logs = logs if isinstance(logs, list) else []
    with _connect() as conn:
        conn.execute("DELETE FROM checkin_logs")
        for log_index, log in enumerate(normalized_logs):
            log_id = str(log.get("id") or "")
            if not log_id:
                continue
            conn.execute(
                """
                INSERT INTO checkin_logs (
                    id, sort_order, time, site_name, site_id, success, quota_awarded, message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    log_index,
                    str(log.get("time") or ""),
                    str(log.get("site_name") or ""),
                    str(log.get("site_id") or ""),
                    1 if log.get("success") else 0,
                    float(log.get("quota_awarded") or 0),
                    str(log.get("message") or ""),
                ),
            )


def _provider_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": str(row["id"] or ""),
        "name": str(row["name"] or ""),
        "description": str(row["description"] or ""),
        "login_path": str(row["login_path"] or "/login"),
        "sign_in_path": str(row["sign_in_path"] or ""),
        "user_info_path": str(row["user_info_path"] or "/api/user/self"),
        "api_user_key": str(row["api_user_key"] or "new-api-user"),
        "waf_cookie_names": _parse_json(row["waf_cookie_names_json"], []),
        "supports_cookie_auth": bool(row["supports_cookie_auth"]),
        "supports_browser_login": bool(row["supports_browser_login"]),
        "auto_checkin_via_user_info": bool(row["auto_checkin_via_user_info"]),
        "is_builtin": bool(row["is_builtin"]),
    }


def load_provider_payloads() -> list[dict[str, Any]]:
    ensure_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM providers ORDER BY is_builtin DESC, id ASC"
        ).fetchall()
    return [_provider_from_row(row) for row in rows]


def get_provider_payload(provider_id: str) -> dict[str, Any] | None:
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM providers WHERE id = ?",
            (str(provider_id or "").strip(),),
        ).fetchone()
    if not row:
        return None
    return _provider_from_row(row)


def create_provider_payload(provider: dict[str, Any]) -> None:
    ensure_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO providers (
                id, name, description, login_path, sign_in_path, user_info_path,
                api_user_key, waf_cookie_names_json, supports_cookie_auth,
                supports_browser_login, auto_checkin_via_user_info, is_builtin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                str(provider.get("id") or "").strip(),
                str(provider.get("name") or "").strip(),
                str(provider.get("description") or "").strip(),
                str(provider.get("login_path") or "/login").strip() or "/login",
                str(provider.get("sign_in_path") or "").strip(),
                str(provider.get("user_info_path") or "/api/user/self").strip() or "/api/user/self",
                str(provider.get("api_user_key") or "new-api-user").strip() or "new-api-user",
                json.dumps(provider.get("waf_cookie_names", []) or [], ensure_ascii=False),
                1 if provider.get("supports_cookie_auth") else 0,
                1 if provider.get("supports_browser_login") else 0,
                1 if provider.get("auto_checkin_via_user_info") else 0,
            ),
        )


def update_provider_payload(provider_id: str, updates: dict[str, Any]) -> bool:
    ensure_db()
    existing = get_provider_payload(provider_id)
    if not existing or existing.get("is_builtin"):
        return False

    with _connect() as conn:
        conn.execute(
            """
            UPDATE providers
            SET name = ?, description = ?, login_path = ?, sign_in_path = ?, user_info_path = ?,
                api_user_key = ?, waf_cookie_names_json = ?, supports_cookie_auth = ?,
                supports_browser_login = ?, auto_checkin_via_user_info = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND is_builtin = 0
            """,
            (
                str(updates.get("name") or existing.get("name") or "").strip(),
                str(updates.get("description") or existing.get("description") or "").strip(),
                str(updates.get("login_path") or existing.get("login_path") or "/login").strip() or "/login",
                str(updates.get("sign_in_path") or existing.get("sign_in_path") or "").strip(),
                str(updates.get("user_info_path") or existing.get("user_info_path") or "/api/user/self").strip() or "/api/user/self",
                str(updates.get("api_user_key") or existing.get("api_user_key") or "new-api-user").strip() or "new-api-user",
                json.dumps(updates.get("waf_cookie_names", existing.get("waf_cookie_names", [])) or [], ensure_ascii=False),
                1 if updates.get("supports_cookie_auth", existing.get("supports_cookie_auth", True)) else 0,
                1 if updates.get("supports_browser_login", existing.get("supports_browser_login", False)) else 0,
                1 if updates.get("auto_checkin_via_user_info", existing.get("auto_checkin_via_user_info", False)) else 0,
                str(provider_id or "").strip(),
            ),
        )
        return True


def count_sites_using_provider_payload(provider_id: str) -> int:
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM sites WHERE provider_template = ?",
            (str(provider_id or "").strip(),),
        ).fetchone()
    return int(row["count"] or 0) if row else 0


def delete_provider_payload(provider_id: str) -> bool:
    ensure_db()
    existing = get_provider_payload(provider_id)
    if not existing or existing.get("is_builtin"):
        return False
    with _connect() as conn:
        conn.execute(
            "DELETE FROM providers WHERE id = ? AND is_builtin = 0",
            (str(provider_id or "").strip(),),
        )
        return True


def load_waf_cookie_cache_payload(site_id: str) -> dict[str, Any] | None:
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM waf_cookie_cache WHERE site_id = ?",
            (str(site_id or "").strip(),),
        ).fetchone()
    if not row:
        return None

    expires_at_text = str(row["expires_at"] or "")
    if expires_at_text:
        try:
            if datetime.now() >= datetime.fromisoformat(expires_at_text):
                delete_waf_cookie_cache_payload(site_id)
                return None
        except ValueError:
            delete_waf_cookie_cache_payload(site_id)
            return None

    return {
        "site_id": str(row["site_id"] or ""),
        "cookies": _parse_json(row["cookie_json"], {}),
        "fetched_at": str(row["fetched_at"] or ""),
        "expires_at": expires_at_text,
        "source": str(row["source"] or ""),
    }


def save_waf_cookie_cache_payload(
    site_id: str,
    cookies: dict[str, Any],
    *,
    source: str = "playwright",
    ttl_hours: int = WAF_CACHE_TTL_HOURS,
) -> None:
    ensure_db()
    fetched_at = datetime.now()
    expires_at = fetched_at + timedelta(hours=max(ttl_hours, 1))
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO waf_cookie_cache (site_id, cookie_json, fetched_at, expires_at, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(site_id) DO UPDATE SET
                cookie_json = excluded.cookie_json,
                fetched_at = excluded.fetched_at,
                expires_at = excluded.expires_at,
                source = excluded.source
            """,
            (
                str(site_id or "").strip(),
                json.dumps(cookies or {}, ensure_ascii=False),
                fetched_at.isoformat(timespec="seconds"),
                expires_at.isoformat(timespec="seconds"),
                str(source or ""),
            ),
        )


def delete_waf_cookie_cache_payload(site_id: str) -> None:
    ensure_db()
    with _connect() as conn:
        conn.execute(
            "DELETE FROM waf_cookie_cache WHERE site_id = ?",
            (str(site_id or "").strip(),),
        )


def _site_model_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "site_id": str(row["site_id"] or ""),
        "model_id": str(row["model_id"] or ""),
        "display_name": str(row["display_name"] or row["model_id"] or ""),
        "source": str(row["source"] or "api_models"),
        "metadata": _parse_json(row["metadata_json"], {}),
        "discovered_at": str(row["discovered_at"] or ""),
        "updated_at": str(row["updated_at"] or ""),
        "last_stream_status": str(row["last_stream_status"] or ""),
        "last_stream_checked_at": str(row["last_stream_checked_at"] or ""),
        "last_stream_latency_ms": row["last_stream_latency_ms"],
        "last_nonstream_status": str(row["last_nonstream_status"] or ""),
        "last_nonstream_checked_at": str(row["last_nonstream_checked_at"] or ""),
        "last_nonstream_latency_ms": row["last_nonstream_latency_ms"],
        "last_message": str(row["last_message"] or ""),
        "last_request_format": str(row["last_request_format"] or ""),
        "last_preset_id": str(row["last_preset_id"] or ""),
    }


def list_site_models_payload(site_id: str = "") -> list[dict[str, Any]]:
    ensure_db()
    params: list[Any] = []
    where_sql = ""
    if str(site_id or "").strip():
        where_sql = "WHERE site_id = ?"
        params.append(str(site_id or "").strip())
    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM site_models
            {where_sql}
            ORDER BY site_id ASC, model_id COLLATE NOCASE ASC
            """,
            params,
        ).fetchall()
    return [_site_model_from_row(row) for row in rows]


def replace_site_models_payload(site_id: str, models: list[dict[str, Any]], *, source: str = "api_models") -> None:
    ensure_db()
    normalized_site_id = str(site_id or "").strip()
    normalized_models = models if isinstance(models, list) else []
    keep_ids = [str(model.get("model_id") or "").strip() for model in normalized_models if str(model.get("model_id") or "").strip()]

    with _connect() as conn:
        if keep_ids:
            placeholders = ", ".join("?" for _ in keep_ids)
            conn.execute(
                f"DELETE FROM site_models WHERE site_id = ? AND model_id NOT IN ({placeholders})",
                [normalized_site_id, *keep_ids],
            )
        else:
            conn.execute("DELETE FROM site_models WHERE site_id = ?", (normalized_site_id,))

        for model in normalized_models:
            model_id = str(model.get("model_id") or "").strip()
            if not model_id:
                continue
            conn.execute(
                """
                INSERT INTO site_models (
                    site_id, model_id, display_name, source, metadata_json, discovered_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(site_id, model_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    source = excluded.source,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    normalized_site_id,
                    model_id,
                    str(model.get("display_name") or model_id),
                    str(model.get("source") or source),
                    json.dumps(model.get("metadata", {}) or {}, ensure_ascii=False),
                ),
            )


def update_site_model_probe_payload(
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
    ensure_db()
    normalized_site_id = str(site_id or "").strip()
    normalized_model_id = str(model_id or "").strip()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO site_models (
                site_id, model_id, display_name, source, metadata_json, discovered_at, updated_at
            )
            VALUES (?, ?, ?, 'manual_probe', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(site_id, model_id) DO NOTHING
            """,
            (
                normalized_site_id,
                normalized_model_id,
                str(display_name or normalized_model_id),
            ),
        )

        if stream:
            conn.execute(
                """
                UPDATE site_models
                SET last_stream_status = ?,
                    last_stream_checked_at = ?,
                    last_stream_latency_ms = ?,
                    last_message = ?,
                    last_request_format = ?,
                    last_preset_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE site_id = ? AND model_id = ?
                """,
                (
                    str(status or ""),
                    str(checked_at or ""),
                    int(latency_ms) if latency_ms is not None else None,
                    str(message or ""),
                    str(request_format or ""),
                    str(preset_id or ""),
                    normalized_site_id,
                    normalized_model_id,
                ),
            )
        else:
            conn.execute(
                """
                UPDATE site_models
                SET last_nonstream_status = ?,
                    last_nonstream_checked_at = ?,
                    last_nonstream_latency_ms = ?,
                    last_message = ?,
                    last_request_format = ?,
                    last_preset_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE site_id = ? AND model_id = ?
                """,
                (
                    str(status or ""),
                    str(checked_at or ""),
                    int(latency_ms) if latency_ms is not None else None,
                    str(message or ""),
                    str(request_format or ""),
                    str(preset_id or ""),
                    normalized_site_id,
                    normalized_model_id,
                ),
            )


def record_detection_run_payload(run: dict[str, Any], evidence: dict[str, Any] | None = None) -> None:
    ensure_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO detection_runs (
                id, profile_id, site_id, run_type, status, started_at, finished_at,
                latency_ms, message, request_format, preset_id, model_id,
                detected_model, authenticity_score, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(run.get("id") or ""),
                str(run.get("profile_id") or ""),
                str(run.get("site_id") or ""),
                str(run.get("run_type") or ""),
                str(run.get("status") or ""),
                str(run.get("started_at") or ""),
                str(run.get("finished_at") or ""),
                int(run.get("latency_ms")) if run.get("latency_ms") is not None else None,
                str(run.get("message") or ""),
                str(run.get("request_format") or ""),
                str(run.get("preset_id") or ""),
                str(run.get("model_id") or ""),
                str(run.get("detected_model") or ""),
                float(run.get("authenticity_score") or 0),
                json.dumps(run.get("metadata", {}) or {}, ensure_ascii=False),
            ),
        )
        if evidence is not None:
            conn.execute(
                """
                INSERT INTO detection_evidence (
                    id, run_id, request_json, response_text, parsed_result_json
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(evidence.get("id") or ""),
                    str(run.get("id") or ""),
                    json.dumps(evidence.get("request", {}) or {}, ensure_ascii=False),
                    str(evidence.get("response_text") or ""),
                    json.dumps(evidence.get("parsed_result", {}) or {}, ensure_ascii=False),
                ),
            )


def list_detection_runs_payload(limit: int = 50, site_id: str = "", run_type: str = "") -> list[dict[str, Any]]:
    ensure_db()
    clauses: list[str] = []
    params: list[Any] = []
    if str(site_id or "").strip():
        clauses.append("site_id = ?")
        params.append(str(site_id or "").strip())
    if str(run_type or "").strip():
        clauses.append("run_type = ?")
        params.append(str(run_type or "").strip())
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(max(int(limit), 1))
    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM detection_runs
            {where_sql}
            ORDER BY started_at DESC, id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        results.append(
            {
                "id": str(row["id"] or ""),
                "profile_id": str(row["profile_id"] or ""),
                "site_id": str(row["site_id"] or ""),
                "run_type": str(row["run_type"] or ""),
                "status": str(row["status"] or ""),
                "started_at": str(row["started_at"] or ""),
                "finished_at": str(row["finished_at"] or ""),
                "latency_ms": row["latency_ms"],
                "message": str(row["message"] or ""),
                "request_format": str(row["request_format"] or ""),
                "preset_id": str(row["preset_id"] or ""),
                "model_id": str(row["model_id"] or ""),
                "detected_model": str(row["detected_model"] or ""),
                "authenticity_score": float(row["authenticity_score"] or 0),
                "metadata": _parse_json(row["metadata_json"], {}),
            }
        )
    return results


def get_detection_evidence_payload(run_id: str) -> dict[str, Any] | None:
    ensure_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM detection_evidence WHERE run_id = ?",
            (str(run_id or "").strip(),),
        ).fetchone()
    if not row:
        return None
    return {
        "id": str(row["id"] or ""),
        "run_id": str(row["run_id"] or ""),
        "request": _parse_json(row["request_json"], {}),
        "response_text": str(row["response_text"] or ""),
        "parsed_result": _parse_json(row["parsed_result_json"], {}),
    }


def record_action_log_payload(entry: dict[str, Any]) -> None:
    ensure_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO action_logs (id, action_key, site_id, success, title, message, details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(entry.get("id") or ""),
                str(entry.get("action_key") or ""),
                str(entry.get("site_id") or ""),
                1 if entry.get("success") else 0,
                str(entry.get("title") or ""),
                str(entry.get("message") or ""),
                json.dumps(entry.get("details", {}) or {}, ensure_ascii=False),
                str(entry.get("created_at") or ""),
            ),
        )


def trim_action_logs_payload(max_rows: int = 500) -> None:
    ensure_db()
    keep_rows = max(int(max_rows), 0)
    with _connect() as conn:
        if keep_rows <= 0:
            conn.execute("DELETE FROM action_logs")
            return
        conn.execute(
            """
            DELETE FROM action_logs
            WHERE id NOT IN (
                SELECT id FROM action_logs
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            )
            """,
            (keep_rows,),
        )


def list_action_logs_payload(limit: int = 50) -> list[dict[str, Any]]:
    ensure_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM action_logs
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (max(int(limit), 1),),
        ).fetchall()
    return [
        {
            "id": str(row["id"] or ""),
            "action_key": str(row["action_key"] or ""),
            "site_id": str(row["site_id"] or ""),
            "success": bool(row["success"]),
            "title": str(row["title"] or ""),
            "message": str(row["message"] or ""),
            "details": _parse_json(row["details_json"], {}),
            "created_at": str(row["created_at"] or ""),
        }
        for row in rows
    ]
