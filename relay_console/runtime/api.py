import asyncio
from typing import Optional
import os
import json
from datetime import datetime
import tempfile
import time
from urllib.parse import urlsplit
import requests

from ..paths import CONFIG_DIR, DEBUG_DIR
from .utils import load_config, describe_http_response


_debug_log_enabled: bool | None = None


def _should_log_debug() -> bool:
    global _debug_log_enabled
    if _debug_log_enabled is None:
        config = load_config()
        _debug_log_enabled = bool(config.get("debug", {}).get("enable_api_log", False))
    return _debug_log_enabled


def reset_debug_log_cache():
    """重置调试日志缓存（设置变更后调用）"""
    global _debug_log_enabled
    _debug_log_enabled = None


def _log_debug(message: str):
    if not _should_log_debug():
        return
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = DEBUG_DIR / "requests.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def _describe_http_response(status_code: int, text: str, content_type: str = "") -> str:
    return describe_http_response(status_code, text, content_type)


DEFAULT_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
)

LOGIN_HELPER_PROFILE_DIR = CONFIG_DIR / "browser_profiles" / "login_helper"
LOGIN_HELPER_COOKIES_FILE = CONFIG_DIR / "browser_profiles" / "login_helper_cookies.json"


def _save_login_helper_cookies(cookies: list[dict]) -> None:
    """Save all browser cookies to disk so session cookies survive restarts."""
    try:
        os.makedirs(LOGIN_HELPER_COOKIES_FILE.parent, exist_ok=True)
        with open(LOGIN_HELPER_COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False)
    except Exception:
        pass


def _load_login_helper_cookies() -> list[dict]:
    """Load previously saved cookies."""
    try:
        if LOGIN_HELPER_COOKIES_FILE.exists():
            with open(LOGIN_HELPER_COOKIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

WAF_STATUS_CODES = {403, 406, 409, 412, 429, 503, 520, 521, 522, 524}
WAF_HINT_KEYWORDS = (
    "cloudflare",
    "cf-ray",
    "attention required",
    "just a moment",
    "security check",
    "verify you are human",
    "captcha",
    "ddos-guard",
    "waf",
)

DEFAULT_WAF_COOKIE_CANDIDATES = (
    "cf_clearance",
    "__cf_bm",
    "__cf_chl_tk",
    "cf_chl_rc_i",
    "cf_chl_rc_ni",
    "cf_chl_rc_m",
    "acw_tc",
    "acw_sc__v2",
    "cdn_sec_tc",
)


def _origin_from_url(url: str) -> str:
    parsed = urlsplit(url or "")
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def _build_browser_like_headers(base_url: str = "") -> dict:
    origin = _origin_from_url(base_url.rstrip("/")) if base_url else ""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": DEFAULT_BROWSER_USER_AGENT,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if origin:
        headers["Origin"] = origin
        headers["Referer"] = f"{origin}/"
    return headers


def _looks_like_waf_block(resp: requests.Response) -> bool:
    content_type = (resp.headers.get("Content-Type", "") or "").lower()
    body = (resp.text or "").strip()
    body_lower = body[:4000].lower()

    if any(keyword in body_lower for keyword in WAF_HINT_KEYWORDS):
        return True

    if resp.status_code in WAF_STATUS_CODES and (
        "text/html" in content_type
        or body_lower.startswith("<!doctype html")
        or body_lower.startswith("<html")
    ):
        return True
    return False


def _request_with_waf_retry(
    method: str,
    url: str,
    *,
    base_url: str = "",
    headers: Optional[dict] = None,
    timeout: int = 10,
    retry_waf: bool = True,
    **kwargs,
) -> requests.Response:
    merged_headers = _build_browser_like_headers(base_url or url)
    if headers:
        merged_headers.update(headers)

    resp = requests.request(method, url, headers=merged_headers, timeout=timeout, **kwargs)
    if not retry_waf or not _looks_like_waf_block(resp):
        return resp

    retry_headers = dict(merged_headers)
    retry_headers.setdefault("sec-ch-ua", '"Chromium";v="144", "Microsoft Edge";v="144", "Not.A/Brand";v="24"')
    retry_headers.setdefault("sec-ch-ua-mobile", "?0")
    retry_headers.setdefault("sec-ch-ua-platform", '"Windows"')
    retry_headers.setdefault("Sec-Fetch-Dest", "empty")
    retry_headers.setdefault("Sec-Fetch-Mode", "cors")
    retry_headers.setdefault("Sec-Fetch-Site", "same-origin")

    _log_debug(f"WAF detected, retrying {method.upper()} {url} with hardened headers")
    return requests.request(method, url, headers=retry_headers, timeout=timeout, **kwargs)


def _build_cookie_headers(base_url: str, session_cookie: str, user_id: str = "", include_content_type: bool = False) -> dict:
    base = base_url.rstrip("/")
    headers = _build_browser_like_headers(base)
    if base:
        headers["Referer"] = f"{base}/console"
    headers["Cookie"] = session_cookie
    if include_content_type:
        headers["Content-Type"] = "application/json"
    if user_id:
        headers["new-api-user"] = user_id
    return headers


def _build_auth_headers(base_url: str, jwt_token: str = "", session_cookie: str = "", user_id: str = "", include_content_type: bool = False) -> dict:
    """Build authentication headers supporting both JWT and Cookie auth."""
    base = base_url.rstrip("/")
    headers = _build_browser_like_headers(base)
    if base:
        headers["Referer"] = f"{base}/console"

    # JWT token takes priority over session cookie
    if jwt_token and str(jwt_token).strip():
        headers["Authorization"] = f"Bearer {jwt_token.strip()}"
    elif session_cookie and str(session_cookie).strip():
        headers["Cookie"] = session_cookie

    if include_content_type:
        headers["Content-Type"] = "application/json"
    if user_id:
        headers["new-api-user"] = user_id
    return headers


def normalize_waf_cookie_names(raw_names: Optional[list | str]) -> list[str]:
    """Normalize WAF cookie names from list or comma-separated string."""
    if not raw_names:
        return []

    names: list[str] = []
    if isinstance(raw_names, str):
        parts = raw_names.replace("\n", ",").split(",")
        names = [p.strip() for p in parts if p.strip()]
    elif isinstance(raw_names, (list, tuple, set)):
        names = [str(p).strip() for p in raw_names if str(p).strip()]
    else:
        return []

    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        lowered = name.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(name)
    return deduped


def parse_cookie_header(cookie_text: str) -> dict:
    """Parse cookie header string to dict."""
    result: dict[str, str] = {}
    for raw_part in (cookie_text or "").split(";"):
        part = raw_part.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        if not key:
            continue
        result[key] = value.strip()
    return result


def build_cookie_header(cookie_map: dict) -> str:
    """Build cookie header string from dict."""
    if not isinstance(cookie_map, dict):
        return ""
    return "; ".join(f"{k}={v}" for k, v in cookie_map.items() if str(k).strip())


def merge_cookie_header(existing_cookie: str, cookie_updates: dict) -> str:
    """Merge cookie updates into existing cookie string."""
    merged = parse_cookie_header(existing_cookie or "")
    if isinstance(cookie_updates, dict):
        for k, v in cookie_updates.items():
            key = str(k).strip()
            if not key:
                continue
            if v is None:
                continue
            merged[key] = str(v).strip()
    return build_cookie_header(merged)


def detect_missing_cookie_names(cookie_text: str, required_names: Optional[list | str]) -> list[str]:
    """Detect missing cookie names from cookie header."""
    required = normalize_waf_cookie_names(required_names)
    if not required:
        return []
    current = parse_cookie_header(cookie_text or "")
    current_lower = {k.lower() for k in current.keys()}
    missing: list[str] = []
    for name in required:
        if name.lower() not in current_lower:
            missing.append(name)
    return missing


async def _collect_waf_cookies_playwright_async(
    target_url: str,
    required_cookie_names: list[str],
    timeout_seconds: int,
    headless: bool,
    strict_required: bool,
) -> dict:
    from playwright.async_api import async_playwright

    required_lower = {name.lower() for name in required_cookie_names}
    target_host = (urlsplit(target_url).hostname or "").lower()

    def _cookie_belongs_to_target(cookie: dict) -> bool:
        if not target_host:
            return True
        domain = str(cookie.get("domain") or "").strip().lower().lstrip(".")
        if not domain:
            return True
        return target_host == domain or target_host.endswith(f".{domain}")

    primary_cookie_targets = [
        name
        for name in ("cf_clearance", "acw_tc", "acw_sc__v2", "cdn_sec_tc")
        if name in required_lower
    ]
    deadline = time.monotonic() + max(timeout_seconds, 5)
    captured: dict[str, str] = {}

    async with async_playwright() as p:
        local_appdata = os.getenv("LOCALAPPDATA", "")
        edge_user_data_dir = os.path.join(local_appdata, "Microsoft", "Edge", "User Data") if local_appdata else ""

        with tempfile.TemporaryDirectory() as temp_dir:
            launch_kwargs = {
                "headless": headless,
                "user_agent": DEFAULT_BROWSER_USER_AGENT,
                "viewport": {"width": 1366, "height": 900},
                "locale": "zh-CN",
                "timezone_id": "Asia/Shanghai",
                "ignore_default_args": ["--enable-automation"],
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-features=VizDisplayCompositor",
                ],
            }
            context = None

            # Edge-only mode: try existing Edge profile first to reuse login state.
            if edge_user_data_dir and os.path.isdir(edge_user_data_dir):
                try:
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=edge_user_data_dir,
                        channel="msedge",
                        **launch_kwargs,
                    )
                    _log_debug("waf helper launched msedge with existing Edge user data")
                except Exception as edge_profile_error:
                    _log_debug(f"msedge profile launch failed: {edge_profile_error}")
                    context = None

            # Fallback: use login helper persistent profile (has saved cookies including OAuth state).
            if context is None:
                try:
                    helper_profile = str(LOGIN_HELPER_PROFILE_DIR)
                    os.makedirs(helper_profile, exist_ok=True)
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=helper_profile,
                        channel="msedge",
                        **launch_kwargs,
                    )
                    saved_cookies = _load_login_helper_cookies()
                    if saved_cookies:
                        await context.add_cookies(saved_cookies)
                    _log_debug("waf helper launched msedge with login helper profile")
                except Exception as helper_error:
                    _log_debug(f"login helper profile launch failed: {helper_error}")
                    context = None

            # Last resort: temporary Edge profile (no login state).
            if context is None:
                try:
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=temp_dir,
                        channel="msedge",
                        **launch_kwargs,
                    )
                    _log_debug("waf helper launched msedge with temporary profile")
                except Exception as edge_error:
                    raise RuntimeError("无法启动 Edge(msedge)，请确认已安装 Edge 浏览器") from edge_error

            if context is None:
                raise RuntimeError("无法启动浏览器上下文")

            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await context.add_init_script(
                    """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
window.chrome = window.chrome || { runtime: {} };
                    """
                )
                await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(1500)

                while time.monotonic() < deadline:
                    cookies = await context.cookies()
                    for cookie in cookies:
                        name = str(cookie.get("name") or "").strip()
                        value = cookie.get("value")
                        if not name or value is None:
                            continue
                        if not _cookie_belongs_to_target(cookie):
                            continue
                        # 采集全部 cookies，required 仅用于成功判定，避免遗漏 Cloudflare 辅助 cookie。
                        captured[name] = str(value)

                    if captured:
                        captured_lower = {k.lower() for k in captured.keys()}
                        if primary_cookie_targets:
                            if any(name in captured_lower for name in primary_cookie_targets):
                                missing = [name for name in required_cookie_names if name.lower() not in captured_lower]
                                message = f"已获取 WAF Cookies: {', '.join(captured.keys())}"
                                if missing:
                                    message += f"；未命中: {', '.join(missing)}"
                                return {
                                    "success": True,
                                    "cookies": captured,
                                    "message": message,
                                }
                        elif strict_required and required_lower:
                            if required_lower.issubset(captured_lower):
                                return {
                                    "success": True,
                                    "cookies": captured,
                                    "message": f"已获取 WAF Cookies: {', '.join(captured.keys())}",
                                }
                        else:
                            return {
                                "success": True,
                                "cookies": captured,
                                "message": f"已获取 Cookies: {', '.join(captured.keys())}",
                            }

                    await page.wait_for_timeout(1000)

                if captured:
                    captured_lower = {k.lower() for k in captured.keys()}
                    if primary_cookie_targets:
                        missing_primary = [name for name in primary_cookie_targets if name not in captured_lower]
                        if missing_primary:
                            return {
                                "success": False,
                                "cookies": captured,
                                "message": f"仅获取到辅助 Cookies，缺少关键 WAF Cookie: {', '.join(missing_primary)}",
                            }
                    if strict_required and required_lower:
                        if required_lower.issubset(captured_lower):
                            return {
                                "success": True,
                                "cookies": captured,
                                "message": f"已获取 WAF Cookies: {', '.join(captured.keys())}",
                            }
                        missing = [name for name in required_cookie_names if name.lower() not in captured_lower]
                        return {
                            "success": False,
                            "cookies": captured,
                            "message": f"仅获取到部分 WAF Cookies，缺少: {', '.join(missing)}",
                        }
            finally:
                try:
                    all_cookies = await context.cookies()
                    _save_login_helper_cookies(all_cookies)
                except Exception:
                    pass
                await context.close()

    if captured:
        captured_lower = {k.lower() for k in captured.keys()}
        if primary_cookie_targets:
            missing_primary = [name for name in primary_cookie_targets if name not in captured_lower]
            if missing_primary:
                return {
                    "success": False,
                    "cookies": captured,
                    "message": f"仅获取到辅助 Cookies，缺少关键 WAF Cookie: {', '.join(missing_primary)}",
                }
        if not strict_required:
            return {
                "success": True,
                "cookies": captured,
                "message": f"已获取 Cookies: {', '.join(captured.keys())}",
            }
        missing = [name for name in required_cookie_names if name.lower() not in captured_lower]
        return {
            "success": False,
            "cookies": captured,
            "message": f"仅获取到部分 WAF Cookies，缺少: {', '.join(missing)}",
        }

    return {
        "success": False,
        "cookies": {},
        "message": "未获取到任何 WAF Cookie。挑战页可能陷入循环（自动化被识别），请关闭全部 Edge 后重试",
    }

def collect_waf_cookies_with_playwright(
    base_url: str,
    target_url: str = "",
    required_cookie_names: Optional[list | str] = None,
    timeout_seconds: int = 90,
    headless: bool = False,
) -> dict:
    """Collect WAF cookies by launching a browser with Playwright."""
    base = (base_url or "").strip().rstrip("/")
    target = (target_url or "").strip()
    if not target:
        target = f"{base}/login" if base else ""
    if not target:
        return {"success": False, "cookies": {}, "message": "缺少可访问地址，无法启动 WAF Cookie 获取"}

    required = normalize_waf_cookie_names(required_cookie_names)
    # 这里按“候选名称”处理，不要求全部命中，避免混合模板（如 newapi-waf）误判失败。
    strict_required = False
    if not required:
        required = list(DEFAULT_WAF_COOKIE_CANDIDATES)

    try:
        # noqa: F401 - runtime dependency check
        import playwright  # type: ignore
    except Exception:
        return {
            "success": False,
            "cookies": {},
            "message": "未安装 Playwright。请先执行: pip install playwright",
        }

    try:
        return asyncio.run(
            _collect_waf_cookies_playwright_async(
                target_url=target,
                required_cookie_names=required,
                timeout_seconds=timeout_seconds,
                headless=headless,
                strict_required=strict_required,
            )
        )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                _collect_waf_cookies_playwright_async(
                    target_url=target,
                    required_cookie_names=required,
                    timeout_seconds=timeout_seconds,
                    headless=headless,
                    strict_required=strict_required,
                )
            )
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as e:
        return {"success": False, "cookies": {}, "message": f"获取 WAF Cookie 失败: {e}"}


def refresh_cookie_with_waf(
    session_cookie: str,
    base_url: str,
    target_url: str = "",
    required_cookie_names: Optional[list | str] = None,
    timeout_seconds: int = 90,
    headless: bool = False,
) -> dict:
    """Collect WAF cookies and merge them into existing cookie string."""
    collect_result = collect_waf_cookies_with_playwright(
        base_url=base_url,
        target_url=target_url,
        required_cookie_names=required_cookie_names,
        timeout_seconds=timeout_seconds,
        headless=headless,
    )
    if not collect_result.get("success"):
        return collect_result

    waf_cookies = collect_result.get("cookies", {}) if isinstance(collect_result.get("cookies"), dict) else {}
    merged_cookie = merge_cookie_header(session_cookie or "", waf_cookies)
    return {
        "success": True,
        "cookies": waf_cookies,
        "cookie": merged_cookie,
        "message": collect_result.get("message", "WAF Cookie 已更新"),
    }


def preflight_waf_refresh(sites: list[dict], stale_hours: float = 12.0) -> list[dict]:
    """
    对需要 WAF Cookie 的站点做过期预检，过期则自动刷新。
    返回刷新结果列表 [{"site_id": ..., "success": bool, "updated_cookie": ...}]
    """
    results: list[dict] = []
    now = datetime.now()

    for site in sites:
        site_id = site.get("id", "")
        waf_cookie_names = site.get("waf_cookie_names", [])
        session_cookie = site.get("session_cookie", "")

        if not normalize_waf_cookie_names(waf_cookie_names):
            continue
        if not session_cookie:
            continue

        updated_at_str = site.get("checkin_cookie_updated_at", "")
        needs_refresh = True
        if updated_at_str:
            try:
                updated_at = datetime.strptime(updated_at_str, "%Y-%m-%d %H:%M:%S")
                age_hours = (now - updated_at).total_seconds() / 3600
                needs_refresh = age_hours >= stale_hours
            except (ValueError, TypeError):
                needs_refresh = True

        if not needs_refresh:
            continue

        base_url = site.get("url", "")
        checkin_url = site.get("checkin_url", "")
        _log_debug(f"WAF preflight: refreshing cookies for site {site.get('name', site_id)}")

        refresh_result = refresh_cookie_with_waf(
            session_cookie=session_cookie,
            base_url=base_url,
            target_url=checkin_url or "",
            required_cookie_names=waf_cookie_names,
            timeout_seconds=90,
            headless=True,
        )

        entry = {"site_id": site_id, "success": refresh_result.get("success", False)}
        if refresh_result.get("success") and refresh_result.get("cookie"):
            entry["updated_cookie"] = refresh_result["cookie"]
        else:
            entry["message"] = refresh_result.get("message", "")
        results.append(entry)

    return results


async def _browser_fetch_with_playwright_async(
    base_url: str,
    request_path: str,
    method: str,
    session_cookie: str,
    target_url: str = "",
    user_id: str = "",
    extra_headers: Optional[dict] = None,
    timeout_seconds: int = 45,
) -> dict:
    """Use Edge (Playwright) to issue same-origin fetch with browser fingerprint/cookies."""
    from playwright.async_api import async_playwright

    base = (base_url or "").strip().rstrip("/")
    if not base:
        return {"success": False, "message": "缺少 base_url，无法执行浏览器内请求"}
    base_host = (urlsplit(base).hostname or "").lower()

    path = (request_path or "").strip() or "/"
    if not path.startswith("/"):
        path = "/" + path
    request_url = f"{base}{path}"
    open_url = (target_url or "").strip() or f"{base}/"

    launch_kwargs = {
        "headless": False,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "ignore_default_args": ["--enable-automation"],
        "viewport": {"width": 1366, "height": 900},
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-features=VizDisplayCompositor",
        ],
    }

    async with async_playwright() as p:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                channel="msedge",
                **launch_kwargs,
            )
            try:
                await context.add_init_script(
                    """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
window.chrome = window.chrome || { runtime: {} };
                    """
                )

                # Inject current cookie string into browser context.
                cookie_items = []
                for k, v in parse_cookie_header(session_cookie or "").items():
                    cookie_items.append({"name": k, "value": v, "url": base})
                if cookie_items:
                    await context.add_cookies(cookie_items)

                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(open_url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(1200)

                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                }
                if user_id:
                    headers["new-api-user"] = str(user_id)
                if isinstance(extra_headers, dict):
                    for k, v in extra_headers.items():
                        key = str(k or "").strip()
                        if not key:
                            continue
                        # Cookie 由浏览器上下文管理，避免冲突。
                        if key.lower() in {"cookie", "content-length"}:
                            continue
                        headers[key] = str(v)

                payload = await page.evaluate(
                    """
async ({ requestUrl, requestMethod, requestHeaders, timeoutMs }) => {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const resp = await fetch(requestUrl, {
      method: requestMethod,
      headers: requestHeaders,
      credentials: 'include',
      cache: 'no-store',
      signal: controller.signal
    });
    clearTimeout(timer);
    const text = await resp.text();
    return {
      ok: true,
      status: resp.status,
      content_type: resp.headers.get('content-type') || '',
      text
    };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}
                    """,
                    {
                        "requestUrl": request_url,
                        "requestMethod": method.upper(),
                        "requestHeaders": headers,
                        "timeoutMs": max(int(timeout_seconds * 1000), 5000),
                    },
                )

                if not payload or not payload.get("ok"):
                    return {"success": False, "message": f"浏览器内请求失败: {payload.get('error', '未知错误')}"}

                cookies_after = await context.cookies()
                cookie_map = {
                    str(item.get("name")): str(item.get("value"))
                    for item in cookies_after
                    if (
                        str(item.get("name") or "").strip()
                        and item.get("value") is not None
                        and (
                            not base_host
                            or not str(item.get("domain") or "").strip()
                            or base_host == str(item.get("domain") or "").strip().lower().lstrip(".")
                            or base_host.endswith("." + str(item.get("domain") or "").strip().lower().lstrip("."))
                        )
                    )
                }
                merged_cookie = merge_cookie_header(session_cookie or "", cookie_map)

                text = str(payload.get("text") or "")
                content_type = str(payload.get("content_type") or "")
                json_data = None
                try:
                    json_data = json.loads(text)
                except Exception:
                    json_data = None

                return {
                    "success": True,
                    "status": int(payload.get("status") or 0),
                    "content_type": content_type,
                    "text": text,
                    "json": json_data,
                    "cookie": merged_cookie,
                }
            finally:
                await context.close()


def browser_fetch_with_playwright(
    base_url: str,
    request_path: str,
    method: str,
    session_cookie: str,
    target_url: str = "",
    user_id: str = "",
    extra_headers: Optional[dict] = None,
    timeout_seconds: int = 45,
) -> dict:
    """Sync wrapper for browser fetch fallback."""
    try:
        # noqa: F401
        import playwright  # type: ignore
    except Exception:
        return {
            "success": False,
            "message": "未安装 Playwright，无法执行浏览器内请求。请先执行: pip install playwright",
        }

    try:
        return asyncio.run(
            _browser_fetch_with_playwright_async(
                base_url=base_url,
                request_path=request_path,
                method=method,
                session_cookie=session_cookie,
                target_url=target_url,
                user_id=user_id,
                extra_headers=extra_headers,
                timeout_seconds=timeout_seconds,
            )
        )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                _browser_fetch_with_playwright_async(
                    base_url=base_url,
                    request_path=request_path,
                    method=method,
                    session_cookie=session_cookie,
                    target_url=target_url,
                    user_id=user_id,
                    extra_headers=extra_headers,
                    timeout_seconds=timeout_seconds,
                )
            )
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as e:
        return {"success": False, "message": f"浏览器内请求异常: {e}"}


async def _capture_login_session_with_playwright_async(
    base_url: str,
    target_url: str = "",
    session_cookie: str = "",
    timeout_seconds: int = 180,
    cookie_name_candidates: Optional[list | str] = None,
) -> dict:
    """Launch a visible browser, wait for manual login/OAuth completion, then collect cookies."""
    from playwright.async_api import async_playwright

    base = (base_url or "").strip().rstrip("/")
    if not base:
        return {"success": False, "message": "缺少 base_url，无法启动浏览器登录助手"}
    base_host = (urlsplit(base).hostname or "").lower()
    open_url = (target_url or "").strip() or f"{base}/login"
    expected_cookie_names = {name.lower() for name in normalize_waf_cookie_names(cookie_name_candidates)}
    expected_cookie_names.add("session")
    initial_cookie_map = parse_cookie_header(session_cookie or "")

    launch_kwargs = {
        "headless": False,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "ignore_default_args": ["--enable-automation"],
        "viewport": {"width": 1366, "height": 900},
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-features=VizDisplayCompositor",
        ],
    }

    async with async_playwright() as p:
        profile_dir = str(LOGIN_HELPER_PROFILE_DIR)
        os.makedirs(profile_dir, exist_ok=True)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="msedge",
            **launch_kwargs,
        )
        try:
            await context.add_init_script(
                """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
window.chrome = window.chrome || { runtime: {} };
                """
            )
            _log_debug(f"login helper launched msedge with persistent profile: {profile_dir}")

            saved_cookies = _load_login_helper_cookies()
            if saved_cookies:
                await context.add_cookies(saved_cookies)
                _log_debug(f"login helper restored {len(saved_cookies)} saved cookies")

            cookie_items = []
            for key, value in initial_cookie_map.items():
                cookie_items.append({"name": key, "value": value, "url": base})
            if cookie_items:
                await context.add_cookies(cookie_items)

            page = context.pages[0] if context.pages else await context.new_page()

            # 使用 commit 而不是 domcontentloaded，避免在 Cloudflare 挑战页面卡住
            try:
                await page.goto(open_url, wait_until="commit", timeout=30000)
            except Exception as e:
                _log_debug(f"login helper page.goto exception (continuing): {e}")
                # 即使 goto 失败也继续，因为页面可能已经开始加载

            # 清除持久化 Profile 中可能残留的旧登录态，防止误判
            try:
                await page.evaluate("""
() => {
  try { localStorage.removeItem('user'); } catch {}
  try { sessionStorage.removeItem('user'); } catch {}
}
                """)
                _log_debug("login helper cleared stale localStorage/sessionStorage user key")
            except Exception:
                pass

            # 记录浏览器初始 Cookie 快照（含持久化 Profile 的旧 Cookie），用于后续变化检测
            initial_browser_cookies = await context.cookies()
            initial_browser_cookie_map = {
                str(item.get("name")): str(item.get("value"))
                for item in initial_browser_cookies
                if (
                    str(item.get("name") or "").strip()
                    and item.get("value") is not None
                    and (
                        not base_host
                        or not str(item.get("domain") or "").strip()
                        or base_host == str(item.get("domain") or "").strip().lower().lstrip(".")
                        or base_host.endswith("." + str(item.get("domain") or "").strip().lower().lstrip("."))
                    )
                )
            }

            started = time.time()
            min_wait_seconds = 5
            cf_challenge_detected = False
            cf_cleared = False

            while time.time() - started < max(timeout_seconds, 30):
                await page.wait_for_timeout(1500)
                cookies_after = await context.cookies()
                cookie_map = {
                    str(item.get("name")): str(item.get("value"))
                    for item in cookies_after
                    if (
                        str(item.get("name") or "").strip()
                        and item.get("value") is not None
                        and (
                            not base_host
                            or not str(item.get("domain") or "").strip()
                            or base_host == str(item.get("domain") or "").strip().lower().lstrip(".")
                            or base_host.endswith("." + str(item.get("domain") or "").strip().lower().lstrip("."))
                        )
                    )
                }
                merged_cookie = merge_cookie_header(session_cookie or "", cookie_map)
                current_url = page.url or open_url
                cookie_lower_names = {key.lower() for key in cookie_map.keys()}

                # 检测 Cloudflare 挑战
                if not cf_challenge_detected:
                    try:
                        is_cf_challenge = await page.evaluate(
                            """
() => {
  const title = document.title || '';
  const body = document.body ? document.body.innerText : '';
  return title.includes('Just a moment') ||
         title.includes('Checking your browser') ||
         body.includes('Cloudflare') ||
         body.includes('Checking your browser') ||
         body.includes('Just a moment');
}
                            """
                        )
                        if is_cf_challenge:
                            cf_challenge_detected = True
                            _log_debug("login helper detected Cloudflare challenge, waiting for clearance...")
                    except Exception:
                        pass

                # 检测 Cloudflare 是否已通过
                if cf_challenge_detected and not cf_cleared:
                    has_cf_clearance = "cf_clearance" in cookie_lower_names
                    if has_cf_clearance:
                        cf_cleared = True
                        _log_debug("login helper detected cf_clearance cookie, Cloudflare challenge passed")

                login_state = await page.evaluate(
                    """
() => {
  const raw = localStorage.getItem('user') || sessionStorage.getItem('user') || '';
  if (!raw) {
    return { user_id: '', token: '', raw: '' };
  }
  try {
    const parsed = JSON.parse(raw);
    return {
      user_id: String(parsed.id || parsed.user_id || parsed.uid || ''),
      token: String(parsed.token || parsed.access_token || ''),
      raw
    };
  } catch {
    return { user_id: '', token: '', raw };
  }
}
                    """
                )
                has_expected_cookie = any(name in cookie_lower_names for name in expected_cookie_names)
                # 用浏览器实际初始快照作为基准，而不是参数里的 session_cookie
                cookie_changed = cookie_map != initial_browser_cookie_map
                left_login_page = "/login" not in current_url.lower()
                has_user_state = bool(login_state.get("user_id") or login_state.get("token"))
                elapsed = time.time() - started

                # 最短等待时间内不判定登录成功，防止持久化 Profile 旧状态误判
                if elapsed >= min_wait_seconds and (has_user_state or (left_login_page and (cookie_changed or has_expected_cookie))):
                    message = "已检测到浏览器登录态，Cookie 已回收"
                    if cf_cleared:
                        message += "（已通过 Cloudflare 验证）"
                    return {
                        "success": True,
                        "cookie": merged_cookie,
                        "cookies": cookie_map,
                        "current_url": current_url,
                        "user_id": str(login_state.get("user_id") or ""),
                        "token": str(login_state.get("token") or ""),
                        "message": message,
                    }

            cookies_after = await context.cookies()
            cookie_map = {
                str(item.get("name")): str(item.get("value"))
                for item in cookies_after
                if str(item.get("name") or "").strip() and item.get("value") is not None
            }
            return {
                "success": False,
                "cookie": merge_cookie_header(session_cookie or "", cookie_map),
                "cookies": cookie_map,
                "current_url": page.url or open_url,
                "message": "等待浏览器登录超时，请确认是否已完成 OAuth / 登录并返回站点",
            }
        finally:
            try:
                all_cookies = await context.cookies()
                _save_login_helper_cookies(all_cookies)
                _log_debug(f"login helper saved {len(all_cookies)} cookies to disk")
            except Exception:
                pass
            await context.close()


def capture_login_session_with_playwright(
    base_url: str,
    target_url: str = "",
    session_cookie: str = "",
    timeout_seconds: int = 180,
    cookie_name_candidates: Optional[list | str] = None,
) -> dict:
    """Sync wrapper for manual browser login helper."""
    try:
        import playwright  # type: ignore  # noqa: F401
    except Exception:
        return {
            "success": False,
            "message": "未安装 Playwright，无法启动浏览器登录助手。请先执行: pip install playwright",
        }

    try:
        return asyncio.run(
            _capture_login_session_with_playwright_async(
                base_url=base_url,
                target_url=target_url,
                session_cookie=session_cookie,
                timeout_seconds=timeout_seconds,
                cookie_name_candidates=cookie_name_candidates,
            )
        )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                _capture_login_session_with_playwright_async(
                    base_url=base_url,
                    target_url=target_url,
                    session_cookie=session_cookie,
                    timeout_seconds=timeout_seconds,
                    cookie_name_candidates=cookie_name_candidates,
                )
            )
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as exc:
        return {"success": False, "message": f"浏览器登录助手异常: {exc}"}


def query_balance(
    api_key: str,
    base_url: str = "",
    subscription_api: str = "/v1/dashboard/billing/subscription",
    usage_api: str = "/v1/dashboard/billing/usage",
    auth_type: str = "bearer"
) -> dict:
    """
    查询中转站余额（USD 和 Token 两种统计）
    支持自动检测多种 API 体系

    Args:
        api_key: API Key (sk-xxx 格式) 或 JWT Token
        base_url: API 基础地址
        subscription_api: 订阅信息接口路径
        usage_api: 用量信息接口路径
        auth_type: 认证方式，"bearer" 使用 Header 认证，"url_key" 使用 URL 参数

    Returns:
        dict: 包含余额信息的字典
    """
    base = base_url.rstrip("/")

    # 根据认证类型构建请求参数
    if auth_type == "url_key":
        headers = {"Content-Type": "application/json"}
        auth_params = {"key": api_key}
    else:  # bearer (默认)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        auth_params = {}

    result = {}
    raw_responses = {}  # 保存原始返回数据
    openai_api_success = False
    waf_error = ""

    # 1. 尝试 OpenAI 兼容 API
    try:
        params = {**auth_params}
        sub_resp = _request_with_waf_retry(
            "GET",
            f"{base}{subscription_api}",
            base_url=base,
            headers=headers,
            params=params if params else None,
            timeout=10,
        )
        if _looks_like_waf_block(sub_resp):
            detail = _describe_http_response(sub_resp.status_code, sub_resp.text, sub_resp.headers.get("Content-Type", ""))
            if not waf_error:
                waf_error = f"WAF 拦截: {detail}"
            _log_debug(f"query_balance subscription waf status={sub_resp.status_code} detail={detail}")
        sub_resp.raise_for_status()
        sub_data = sub_resp.json()
        raw_responses["subscription"] = sub_data

        # 检查是否是新 API 体系 (code/message/data 格式)
        if sub_data.get("code") == 0 and "data" in sub_data:
            data = sub_data["data"]
            # /api/v1/auth/me 格式
            if "balance" in data:
                result["balance"] = data.get("balance", 0)
                result["email"] = data.get("email", "")
                result["status"] = data.get("status", "")
                openai_api_success = True
        elif "hard_limit_usd" in sub_data:
            # OpenAI 兼容格式
            openai_api_success = True
            result["hard_limit_usd"] = sub_data.get("hard_limit_usd", 0)

            # 计算日期范围（最近 100 天）
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=100)

            usage_params = {
                **auth_params,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }
            usage_resp = _request_with_waf_retry(
                "GET",
                f"{base}{usage_api}",
                base_url=base,
                headers=headers,
                params=usage_params,
                timeout=10,
            )
            if _looks_like_waf_block(usage_resp):
                detail = _describe_http_response(usage_resp.status_code, usage_resp.text, usage_resp.headers.get("Content-Type", ""))
                if not waf_error:
                    waf_error = f"WAF 拦截: {detail}"
                _log_debug(f"query_balance usage waf status={usage_resp.status_code} detail={detail}")
            usage_resp.raise_for_status()
            usage_data = usage_resp.json()
            raw_responses["usage"] = usage_data
            total_usage_cents = usage_data.get("total_usage", 0)
            result["used_usd"] = round(total_usage_cents / 100, 2)
            result["remaining_usd"] = round(
                result["hard_limit_usd"] - result["used_usd"], 2
            )
    except requests.exceptions.RequestException:
        pass  # billing API 可能不可用，继续尝试其他接口

    # 2. 如果 OpenAI API 失败，尝试 sub2api 格式 (/v1/usage)
    if not openai_api_success:
        try:
            usage_resp = _request_with_waf_retry(
                "GET",
                f"{base}/v1/usage",
                base_url=base,
                headers=headers,
                params=auth_params if auth_params else None,
                timeout=10,
            )
            if _looks_like_waf_block(usage_resp):
                detail = _describe_http_response(usage_resp.status_code, usage_resp.text, usage_resp.headers.get("Content-Type", ""))
                if not waf_error:
                    waf_error = f"WAF 拦截: {detail}"
                _log_debug(f"query_balance v1_usage waf status={usage_resp.status_code} detail={detail}")
            # 不管状态码，先尝试解析 JSON（sub2api 可能返回 403 + JSON 错误信息）
            try:
                usage_data = usage_resp.json()
                raw_responses["v1_usage"] = usage_data

                # 检查是否返回错误码（如 INSUFFICIENT_BALANCE）
                if "code" in usage_data and "message" in usage_data:
                    # 站点返回了错误信息
                    error_code = usage_data.get("code", "")
                    error_msg = usage_data.get("message", "")
                    if error_code == "INSUFFICIENT_BALANCE":
                        result["error"] = f"余额不足: {error_msg}"
                    elif error_code == "INVALID_API_KEY":
                        result["error"] = f"API Key 无效: {error_msg}"
                    else:
                        result["error"] = f"{error_code}: {error_msg}"
                    openai_api_success = True  # 标记已处理，不再尝试其他接口

                # sub2api /v1/usage 格式
                elif "balance" in usage_data or "remaining" in usage_data:
                    openai_api_success = True
                    result["balance"] = usage_data.get("balance", usage_data.get("remaining", 0))
                    result["remaining"] = usage_data.get("remaining", 0)
                    result["plan_name"] = usage_data.get("planName", "")
                    result["unit"] = usage_data.get("unit", "USD")

                    # 解析 usage 统计
                    usage = usage_data.get("usage", {})
                    if usage:
                        today = usage.get("today", {})
                        total = usage.get("total", {})
                        result["today_requests"] = today.get("requests", 0)
                        result["today_tokens"] = today.get("total_tokens", 0)
                        result["today_cost"] = today.get("cost", 0)
                        result["total_requests"] = total.get("requests", 0)
                        result["total_tokens"] = total.get("total_tokens", 0)
                        result["total_cost"] = total.get("cost", 0)
            except ValueError:
                # JSON 解析失败，检查 HTTP 状态码
                if usage_resp.status_code != 200:
                    pass  # 继续尝试其他接口
        except requests.exceptions.RequestException:
            pass

    # 3. 如果还是失败，尝试 /api/v1/auth/me (JWT Token 认证的站点)
    if not openai_api_success:
        try:
            me_resp = _request_with_waf_retry(
                "GET",
                f"{base}/api/v1/auth/me",
                base_url=base,
                headers=headers,
                params=auth_params if auth_params else None,
                timeout=10,
            )
            if _looks_like_waf_block(me_resp):
                detail = _describe_http_response(me_resp.status_code, me_resp.text, me_resp.headers.get("Content-Type", ""))
                if not waf_error:
                    waf_error = f"WAF 拦截: {detail}"
                _log_debug(f"query_balance auth_me waf status={me_resp.status_code} detail={detail}")
            me_resp.raise_for_status()
            me_data = me_resp.json()
            raw_responses["auth_me"] = me_data

            if me_data.get("code") == 0 and "data" in me_data:
                data = me_data["data"]
                result["balance"] = data.get("balance", 0)
                result["email"] = data.get("email", "")
                result["status"] = data.get("status", "")
        except requests.exceptions.RequestException:
            pass

    # 4. 尝试新 API 体系用量统计 (/api/v1/usage/dashboard/stats)
    # 如果配置了新 API 路径，或者 OpenAI API 失败时自动尝试
    should_try_new_stats = "/api/v1/" in usage_api or not openai_api_success
    if should_try_new_stats and "today_requests" not in result:
        stats_url = usage_api if "/api/v1/" in usage_api else "/api/v1/usage/dashboard/stats"
        try:
            stats_resp = _request_with_waf_retry(
                "GET",
                f"{base}{stats_url}",
                base_url=base,
                headers=headers,
                params=auth_params if auth_params else None,
                timeout=10,
            )
            if _looks_like_waf_block(stats_resp):
                detail = _describe_http_response(stats_resp.status_code, stats_resp.text, stats_resp.headers.get("Content-Type", ""))
                if not waf_error:
                    waf_error = f"WAF 拦截: {detail}"
                _log_debug(f"query_balance stats waf status={stats_resp.status_code} detail={detail}")
            stats_resp.raise_for_status()
            stats_data = stats_resp.json()
            raw_responses["stats"] = stats_data

            if stats_data.get("code") == 0 and "data" in stats_data:
                data = stats_data["data"]
                result["total_requests"] = data.get("total_requests", 0)
                result["total_tokens"] = data.get("total_tokens", 0)
                result["total_cost"] = data.get("total_cost", 0)
                result["today_requests"] = data.get("today_requests", 0)
                result["today_tokens"] = data.get("today_tokens", 0)
                result["today_cost"] = data.get("today_cost", 0)
        except requests.exceptions.RequestException:
            pass

    # 5. 查询 Token 用量 (NewAPI 风格)
    try:
        token_params = {**auth_params} if auth_params else None
        token_resp = _request_with_waf_retry(
            "GET",
            f"{base}/api/usage/token/",
            base_url=base,
            headers=headers,
            params=token_params,
            timeout=10,
        )
        if _looks_like_waf_block(token_resp):
            detail = _describe_http_response(token_resp.status_code, token_resp.text, token_resp.headers.get("Content-Type", ""))
            if not waf_error:
                waf_error = f"WAF 拦截: {detail}"
            _log_debug(f"query_balance token waf status={token_resp.status_code} detail={detail}")
        token_resp.raise_for_status()
        token_data = token_resp.json()
        raw_responses["token"] = token_data
        if token_data.get("code") == 0 and "data" in token_data:
            data = token_data["data"]
            result["total_granted"] = data.get("total_granted", 0)
            result["total_used"] = data.get("total_used", 0)
            result["total_available"] = data.get("total_available", 0)
    except requests.exceptions.RequestException:
        pass  # token API 可能不可用

    if not result:
        result["error"] = waf_error or "无法获取余额信息"

    result["raw_response"] = raw_responses
    return result


def query_logs(
    api_key: str,
    base_url: str,
    page_size: int = 50,
    page: int = 1,
    order: str = "desc",
    custom_api_path: str = "",
    proxy_url: str = "",
    auth_type: str = "bearer",
) -> dict:
    """
    查询调用日志（使用 API Key）

    Args:
        api_key: API Key (sk-xxx 格式) 或 JWT Token
        base_url: API 基础地址
        page_size: 每页返回多少条日志（默认 50）
        page: 页码（默认 1）
        order: 排序方式，desc=降序/最新在前，asc=升序（默认 desc）
        custom_api_path: 自定义日志接口路径（如 /api/log/custom），留空使用默认 /api/log/token
        proxy_url: 代理地址（如 https://proxy.cifang.xyz/proxy），留空则直接访问
        auth_type: 认证方式，"bearer" 使用 Header 认证，"url_key" 使用 URL 参数

    Returns:
        dict: 包含日志列表的字典
            - total: 总条数
            - items: 日志列表，每条包含 model_name, token_name, quota,
                     prompt_tokens, completion_tokens, created_at 等
            - raw_response: 原始 API 返回数据
    """
    from urllib.parse import urlencode, quote

    base = base_url.rstrip("/")
    api_path = custom_api_path.strip() if custom_api_path else "/api/log/token"

    # 根据认证类型构建请求
    if auth_type == "url_key":
        headers = {
            "Content-Type": "application/json",
        }
        # 构建目标 URL (URL 参数认证)
        target_url = f"{base}{api_path}?key={api_key}&p={page}&per_page={page_size}&order={order}"

        # 如果有代理，通过代理访问
        if proxy_url.strip():
            request_url = f"{proxy_url.rstrip('/')}?url={quote(target_url, safe='')}"
            params = None
        else:
            request_url = f"{base}{api_path}"
            params = {
                "key": api_key,
                "p": page,
                "per_page": page_size,
                "order": order,
            }
    else:  # bearer (默认)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # Bearer 认证不在 URL 中传 key
        if proxy_url.strip():
            target_url = f"{base}{api_path}?p={page}&per_page={page_size}&order={order}"
            request_url = f"{proxy_url.rstrip('/')}?url={quote(target_url, safe='')}"
            params = None
        else:
            request_url = f"{base}{api_path}"
            params = {
                "p": page,
                "per_page": page_size,
                "order": order,
            }

    try:
        resp = _request_with_waf_retry(
            "GET",
            request_url,
            base_url=base,
            headers=headers,
            params=params,
            timeout=10,
        )
        if _looks_like_waf_block(resp):
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"query_logs {request_url} waf status={resp.status_code} detail={detail}")
            return {"error": f"WAF 拦截: {detail}"}
        if resp.status_code != 200:
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"query_logs {request_url} status={resp.status_code} detail={detail}")
            return {"error": f"HTTP {resp.status_code}: {detail}"}

        # 检查响应内容是否为空
        if not resp.text.strip():
            return {"error": "API 返回空响应，请检查接口路径是否正确"}

        try:
            data = resp.json()
        except ValueError:
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"query_logs {request_url} json_error detail={detail}")
            return {"error": f"API 返回非 JSON 格式: {detail}"}

        # 保存原始返回数据
        raw_response = data

        # 新接口直接返回 {"data": [...]}
        items = data.get("data", [])

        # 强制按 created_at 降序排序（确保最新的在前面）
        # 因为有些 API 不支持 order 参数
        items = sorted(items, key=lambda x: x.get("created_at", 0), reverse=True)

        return {
            "total": len(items),
            "items": items,
            "raw_response": raw_response
        }
    except requests.exceptions.RequestException as e:
        _log_debug(f"query_logs {request_url} exception={e}")
        return {"error": str(e)}


def do_checkin(
    base_url: str,
    session_cookie: str = "",
    jwt_token: str = "",
    user_id: str = "",
    checkin_path: str = "/api/user/checkin",
    extra_headers: Optional[dict] = None,
    checkin_url: str = "",
    waf_cookie_names: Optional[list | str] = None,
    auto_get_waf_cookie: bool = False,
) -> dict:
    """
    执行签到（支持 Session Cookie 或 JWT Token 认证）

    Args:
        base_url: API 基础地址
        session_cookie: 浏览器 Session Cookie（包含 session=xxx 等）
        jwt_token: JWT Token（优先使用，如果提供）
        user_id: 用户 ID（某些站点需要 new-api-user Header）
        checkin_path: 签到接口路径（默认 /api/user/checkin）
        extra_headers: 额外请求头（JSON 对象）
        checkin_url: 站点签到页/登录页，用于自动获取 WAF Cookie
        waf_cookie_names: 指定所需 WAF Cookie 名称
        auto_get_waf_cookie: 命中 WAF 时是否自动获取 Cookie 并重试

    Returns:
        dict: 签到结果
    """
    base = base_url.rstrip("/")
    path = checkin_path.strip() or "/api/user/checkin"
    if not path.startswith("/"):
        path = "/" + path

    effective_cookie = session_cookie
    effective_jwt = jwt_token
    updated_cookie = ""
    required_waf_names = normalize_waf_cookie_names(waf_cookie_names)

    def _send(cookie_value: str = "", token_value: str = "") -> requests.Response:
        headers = _build_auth_headers(base, token_value, cookie_value, user_id, include_content_type=True)
        if extra_headers:
            headers.update(extra_headers)
        return _request_with_waf_retry(
            "POST",
            f"{base}{path}",
            base_url=base,
            headers=headers,
            timeout=15,
        )

    try:
        resp = _send(effective_cookie, effective_jwt)

        content_type = resp.headers.get("Content-Type", "")
        response_text = resp.text

        if _looks_like_waf_block(resp):
            detail = _describe_http_response(resp.status_code, response_text, content_type)
            _log_debug(f"checkin {base}{path} status={resp.status_code} detail={detail}")
            missing_names = detect_missing_cookie_names(effective_cookie, required_waf_names)
            missing_hint = f" 缺少 Cookie: {', '.join(missing_names)}。" if missing_names else ""

            # JWT token 认证不支持 WAF Cookie 刷新，直接返回错误
            if effective_jwt:
                return {"success": False, "message": f"WAF 拦截: {detail}。JWT 认证模式不支持自动 WAF Cookie 刷新。"}

            if auto_get_waf_cookie:
                refresh_result = refresh_cookie_with_waf(
                    session_cookie=effective_cookie,
                    base_url=base,
                    target_url=checkin_url or f"{base}/login",
                    required_cookie_names=required_waf_names or None,
                    timeout_seconds=90,
                    headless=False,
                )
                if not refresh_result.get("success"):
                    refresh_msg = str(refresh_result.get("message", ""))
                    return {"success": False, "message": f"WAF 拦截: {detail}。{refresh_msg}{missing_hint}"}

                effective_cookie = str(refresh_result.get("cookie") or effective_cookie)
                updated_cookie = effective_cookie
                resp = _send(effective_cookie, "")
                content_type = resp.headers.get("Content-Type", "")
                response_text = resp.text
                if _looks_like_waf_block(resp):
                    detail = _describe_http_response(resp.status_code, response_text, content_type)
                    _log_debug(f"checkin retry {base}{path} waf status={resp.status_code} detail={detail}")
                    browser_result = browser_fetch_with_playwright(
                        base_url=base,
                        request_path=path,
                        method="POST",
                        session_cookie=effective_cookie,
                        target_url=checkin_url or f"{base}/",
                        user_id=user_id,
                        extra_headers=extra_headers,
                        timeout_seconds=60,
                    )
                    if browser_result.get("success"):
                        browser_cookie = str(browser_result.get("cookie") or "")
                        if browser_cookie:
                            updated_cookie = browser_cookie

                        browser_json = browser_result.get("json")
                        browser_status = int(browser_result.get("status") or 0)
                        browser_text = str(browser_result.get("text") or "")
                        browser_ct = str(browser_result.get("content_type") or "")

                        if isinstance(browser_json, dict):
                            data = browser_json
                            message = str(data.get("message") or "").strip()
                            if data.get("success"):
                                result = {
                                    "success": True,
                                    "message": message or "签到成功",
                                    "quota_awarded": data.get("data", {}).get("quota_awarded", 0),
                                    "checkin_date": data.get("data", {}).get("checkin_date", ""),
                                }
                                if updated_cookie:
                                    result["updated_cookie"] = updated_cookie
                                return result

                            normalized_message = message.lower()
                            already_checked_keywords = (
                                "已签到",
                                "已经签到",
                                "今日已签到",
                                "already checked",
                                "already check",
                                "checked in today",
                                "already signed",
                            )
                            if any((keyword in message) or (keyword in normalized_message) for keyword in already_checked_keywords):
                                result = {
                                    "success": True,
                                    "already_checked_in": True,
                                    "message": message or "今日已签到",
                                    "quota_awarded": 0,
                                    "checkin_date": data.get("data", {}).get("checkin_date", ""),
                                }
                                if updated_cookie:
                                    result["updated_cookie"] = updated_cookie
                                return result

                            result = {
                                "success": False,
                                "message": message or "签到失败",
                            }
                            if updated_cookie:
                                result["updated_cookie"] = updated_cookie
                            return result

                        detail_browser = _describe_http_response(browser_status, browser_text, browser_ct)
                        return {
                            "success": False,
                            "message": f"WAF 拦截: {detail}。已尝试浏览器内请求但失败: {detail_browser}",
                            "updated_cookie": updated_cookie,
                        }

                    browser_message = str(browser_result.get("message", "未知错误"))
                    return {
                        "success": False,
                        "message": f"WAF 拦截: {detail}。已尝试自动刷新 WAF Cookie 与浏览器内请求但仍失败（{browser_message}）",
                        "updated_cookie": updated_cookie,
                    }
            else:
                return {
                    "success": False,
                    "message": f"WAF 拦截: {detail}。可在站点详情中使用 WAF 助手刷新 Cookie。{missing_hint}",
                }

        if not response_text.strip():
            result = {"success": False, "message": "API 返回空响应，请检查 Cookie 是否有效"}
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        try:
            data = resp.json()
        except ValueError:
            detail = _describe_http_response(resp.status_code, response_text, content_type)
            _log_debug(f"checkin {base}{path} json_error detail={detail}")
            result = {"success": False, "message": f"API 返回非 JSON: {detail}"}
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        message = str(data.get("message") or "").strip()
        if data.get("success"):
            result = {
                "success": True,
                "message": message or "签到成功",
                "quota_awarded": data.get("data", {}).get("quota_awarded", 0),
                "checkin_date": data.get("data", {}).get("checkin_date", ""),
            }
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        normalized_message = message.lower()
        already_checked_keywords = (
            "已签到",
            "已经签到",
            "今日已签到",
            "already checked",
            "already check",
            "checked in today",
            "already signed",
        )
        if any((keyword in message) or (keyword in normalized_message) for keyword in already_checked_keywords):
            result = {
                "success": True,
                "already_checked_in": True,
                "message": message or "今日已签到",
                "quota_awarded": 0,
                "checkin_date": data.get("data", {}).get("checkin_date", ""),
            }
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        result = {
            "success": False,
            "message": message or "签到失败",
        }
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result
    except requests.exceptions.Timeout:
        _log_debug(f"checkin {base}{path} timeout")
        result = {"success": False, "message": "请求超时，请检查网络"}
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result
    except requests.exceptions.ConnectionError:
        _log_debug(f"checkin {base}{path} connection_error")
        result = {"success": False, "message": "连接失败，请检查网络或站点是否可访问"}
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result
    except requests.exceptions.RequestException as e:
        _log_debug(f"checkin {base}{path} exception={e}")
        result = {"success": False, "message": f"网络错误: {str(e)}"}
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result

def get_checkin_status(base_url: str, session_cookie: str, month: str = None) -> dict:
    """
    获取签到状态（使用 Session Cookie 认证）

    Args:
        base_url: API 基础地址
        session_cookie: 浏览器 Session Cookie
        month: 月份（格式 2026-02），默认当前月

    Returns:
        dict: 签到状态信息
    """
    from datetime import datetime

    base = base_url.rstrip("/")
    if not month:
        month = datetime.now().strftime("%Y-%m")

    headers = _build_cookie_headers(base, session_cookie)

    try:
        resp = _request_with_waf_retry(
            "GET",
            f"{base}/api/user/checkin",
            base_url=base,
            headers=headers,
            params={"month": month},
            timeout=15,
        )
        if _looks_like_waf_block(resp):
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"checkin_status waf status={resp.status_code} detail={detail}")
            return {"success": False, "message": f"WAF 拦截: {detail}"}
        data = resp.json()

        if data.get("success"):
            return {
                "success": True,
                "data": data.get("data", {}),
            }
        else:
            return {
                "success": False,
                "message": data.get("message", "获取签到状态失败"),
            }
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"网络错误: {str(e)}"}
    except ValueError:
        return {"success": False, "message": "API 返回非 JSON 格式"}


def query_balance_by_cookie(
    base_url: str,
    session_cookie: str = "",
    jwt_token: str = "",
    user_id: str = "",
    extra_headers: Optional[dict] = None,
    checkin_url: str = "",
    waf_cookie_names: Optional[list | str] = None,
    auto_get_waf_cookie: bool = False,
) -> dict:
    """
    使用 Cookie 或 JWT Token 查询用户余额（通过 /api/user/self 接口）

    Args:
        base_url: API 基础地址
        session_cookie: 浏览器 Session Cookie
        jwt_token: JWT Token（优先使用，如果提供）
        user_id: 用户 ID（某些站点需要 new-api-user Header）
        extra_headers: 额外请求头
        checkin_url: 站点签到页/登录页，用于自动获取 WAF Cookie
        waf_cookie_names: 指定所需 WAF Cookie 名称
        auto_get_waf_cookie: 命中 WAF 时是否自动获取 Cookie 并重试

    Returns:
        dict: 用户信息和余额
    """
    base = base_url.rstrip("/")
    effective_cookie = session_cookie
    effective_jwt = jwt_token
    updated_cookie = ""
    required_waf_names = normalize_waf_cookie_names(waf_cookie_names)

    def _send(cookie_value: str = "", token_value: str = "") -> requests.Response:
        headers = _build_auth_headers(base, token_value, cookie_value, user_id)
        if extra_headers:
            headers.update(extra_headers)
        return _request_with_waf_retry(
            "GET",
            f"{base}/api/user/self",
            base_url=base,
            headers=headers,
            timeout=15,
        )

    try:
        resp = _send(effective_cookie, effective_jwt)
        if _looks_like_waf_block(resp):
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"balance_by_cookie waf status={resp.status_code} detail={detail}")
            missing_names = detect_missing_cookie_names(effective_cookie, required_waf_names)
            missing_hint = f" 缺少 Cookie: {', '.join(missing_names)}。" if missing_names else ""

            # JWT token 认证不支持 WAF Cookie 刷新
            if effective_jwt:
                return {"success": False, "message": f"WAF 拦截: {detail}。JWT 认证模式不支持自动 WAF Cookie 刷新。"}

            if auto_get_waf_cookie:
                refresh_result = refresh_cookie_with_waf(
                    session_cookie=effective_cookie,
                    base_url=base,
                    target_url=checkin_url or f"{base}/login",
                    required_cookie_names=required_waf_names or None,
                    timeout_seconds=90,
                    headless=False,
                )
                if not refresh_result.get("success"):
                    refresh_msg = str(refresh_result.get("message", ""))
                    return {"success": False, "message": f"WAF 拦截: {detail}。{refresh_msg}{missing_hint}"}

                effective_cookie = str(refresh_result.get("cookie") or effective_cookie)
                updated_cookie = effective_cookie
                resp = _send(effective_cookie, "")
                if _looks_like_waf_block(resp):
                    detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
                    _log_debug(f"balance_by_cookie retry waf status={resp.status_code} detail={detail}")
                    browser_result = browser_fetch_with_playwright(
                        base_url=base,
                        request_path="/api/user/self",
                        method="GET",
                        session_cookie=effective_cookie,
                        target_url=checkin_url or f"{base}/",
                        user_id=user_id,
                        extra_headers=extra_headers,
                        timeout_seconds=60,
                    )
                    if browser_result.get("success"):
                        browser_cookie = str(browser_result.get("cookie") or "")
                        if browser_cookie:
                            updated_cookie = browser_cookie

                        browser_json = browser_result.get("json")
                        browser_status = int(browser_result.get("status") or 0)
                        browser_text = str(browser_result.get("text") or "")
                        browser_ct = str(browser_result.get("content_type") or "")

                        if isinstance(browser_json, dict) and browser_json.get("success") and "data" in browser_json:
                            user_data = browser_json["data"]
                            quota = user_data.get("quota", 0)
                            balance = quota / 500000 if quota else 0
                            result = {
                                "success": True,
                                "balance": round(balance, 2),
                                "quota": quota,
                                "username": user_data.get("username", ""),
                                "email": user_data.get("email", ""),
                                "display_name": user_data.get("display_name", ""),
                                "raw_data": user_data,
                            }
                            if updated_cookie:
                                result["updated_cookie"] = updated_cookie
                            return result

                        detail_browser = _describe_http_response(browser_status, browser_text, browser_ct)
                        return {
                            "success": False,
                            "message": f"WAF 拦截: {detail}。已尝试浏览器内请求但失败: {detail_browser}",
                            "updated_cookie": updated_cookie,
                        }

                    browser_message = str(browser_result.get("message", "未知错误"))
                    return {
                        "success": False,
                        "message": f"WAF 拦截: {detail}。已尝试自动刷新 WAF Cookie 与浏览器内请求但仍失败（{browser_message}）",
                        "updated_cookie": updated_cookie,
                    }
            else:
                return {
                    "success": False,
                    "message": f"WAF 拦截: {detail}。可在站点详情中使用 WAF 助手刷新 Cookie。{missing_hint}",
                }

        try:
            data = resp.json()
        except ValueError:
            detail = _describe_http_response(resp.status_code, resp.text, resp.headers.get("Content-Type", ""))
            _log_debug(f"balance_by_cookie {base}/api/user/self json_error detail={detail}")
            result = {"success": False, "message": f"API 返回非 JSON 格式: {detail}"}
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        if data.get("success") and "data" in data:
            user_data = data["data"]
            quota = user_data.get("quota", 0)
            balance = quota / 500000 if quota else 0

            result = {
                "success": True,
                "balance": round(balance, 2),
                "quota": quota,
                "username": user_data.get("username", ""),
                "email": user_data.get("email", ""),
                "display_name": user_data.get("display_name", ""),
                "raw_data": user_data,
            }
            if updated_cookie:
                result["updated_cookie"] = updated_cookie
            return result

        result = {
            "success": False,
            "message": data.get("message", "获取用户信息失败"),
        }
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result
    except requests.exceptions.RequestException as e:
        _log_debug(f"balance_by_cookie {base}/api/user/self exception={e}")
        result = {"success": False, "message": f"网络错误: {str(e)}"}
        if updated_cookie:
            result["updated_cookie"] = updated_cookie
        return result

if __name__ == "__main__":
    # 测试用法示例
    # test_key = "sk-your-api-key"
    # base_url = "https://your-api-url.com"
    # result = query_balance(test_key, base_url)
    # print("余额:", result)
    pass

