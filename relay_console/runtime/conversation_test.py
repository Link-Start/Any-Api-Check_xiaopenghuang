#!/usr/bin/env python3
"""
Claude Model Detector - Claude 真实模型检测工具

通过询问"你的知识库截止时间？"来判断 Claude 真实模型版本
原理：去除系统提示词，直接询问原生 Claude，根据回答判断模型

判断规则：
- 2024年10月 → Claude Sonnet 3.7 (think)
- 2025年1月  → Claude Sonnet 4 (think)
- 2024年9月  → Claude Sonnet 4.5 (think)
- 2024年11月 → Claude Opus 4.5 (think)

准确率约 95%

GitHub: https://github.com/yourname/claude-model-detector
"""

import json
import re
import sys
from typing import Callable, Optional, Generator
import httpx

from .sse_parser import parse_anthropic_sse_stream
from .utils import describe_http_response


# ============ 默认配置 ============

DEFAULT_CONFIG = {
    "max_tokens": 32000,
    "thinking_budget": 31999
}

# 模型选项（供 GUI 和 CLI 使用）
MODEL_OPTIONS = {
    "1": ("Sonnet", "claude-sonnet-4-5-20250929"),
    "2": ("Opus", "claude-opus-4-5-20251101"),
}

# 模型列表（供 GUI 下拉框使用）
MODEL_LIST = [
    ("claude-haiku-4-5-20251001", "Haiku 4.5"),
    ("claude-opus-4-20250514", "Opus 4"),
    ("claude-opus-4-5-20251101", "Opus 4.5"),
    ("claude-opus-4-6", "Opus 4.6"),
    ("claude-sonnet-4-20250514", "Sonnet 4"),
    ("claude-sonnet-4-5-20250929", "Sonnet 4.5"),
]

DEFAULT_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
)


# ============ 用户输入 ============

def get_user_input() -> tuple:
    """获取用户输入的 URL、Key 和模型选择，返回 (url, key, model_id)"""
    print("\n" + "=" * 60)
    print("请输入 API 配置")
    print("=" * 60)

    # 输入 URL
    url = input("API URL (如 https://api.example.com): ").strip()
    if not url:
        print("❌ URL 不能为空")
        sys.exit(1)

    # 输入 Key
    key = input("API Key: ").strip()
    if not key:
        print("❌ API Key 不能为空")
        sys.exit(1)

    # 选择模型
    print("\n📋 选择模型:")
    print("-" * 40)
    for num, (name, model_id) in MODEL_OPTIONS.items():
        print(f"  {num}. {name} ({model_id})")
    print("-" * 40)

    while True:
        choice = input("选择模型 [1-2，默认1]: ").strip()
        if not choice:
            choice = "1"
        if choice in MODEL_OPTIONS:
            model_name, model_id = MODEL_OPTIONS[choice]
            print(f"✅ 已选择: {model_name}")
            return url, key, model_id
        print("⚠️  无效选择，请输入 1 或 2")


# ============ 请求头构建 ============

def get_headers(api_key: str) -> dict:
    """构建请求头（模拟 Claude CLI）"""
    return {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "anthropic-beta": "claude-code-20250219,interleaved-thinking-2025-05-14",
        "anthropic-dangerous-direct-browser-access": "true",
        "anthropic-version": "2023-06-01",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json",
        "user-agent": DEFAULT_BROWSER_USER_AGENT,
        "x-app": "cli",
        "x-stainless-arch": "x64",
        "x-stainless-helper-method": "stream",
        "x-stainless-lang": "js",
        "x-stainless-os": "Windows",
        "x-stainless-package-version": "0.70.0",
        "x-stainless-retry-count": "0",
        "x-stainless-runtime": "node",
        "x-stainless-runtime-version": "v25.1.0",
        "x-stainless-timeout": "600",
        "accept-encoding": "identity",
    }


# ============ 请求体构建 ============

def build_body(message: str, model_id: str, with_thinking: bool = True,
               with_system: bool = True) -> dict:
    """
    构建请求体（模拟 Claude Code 请求格式）

    Args:
        message: 用户消息
        model_id: 模型 ID
        with_thinking: 是否启用思考模式
        with_system: 是否包含 system 字段（某些中转站不允许）
    """
    body = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "null"
                    },
                    {
                        "type": "text",
                        "text": "null"
                    },
                    {
                        "type": "text",
                        "text": message,
                        "cache_control": {
                            "type": "ephemeral"
                        }
                    }
                ]
            }
        ],
        "metadata": {
            "user_id": "user_cli_test_session"
        },
        "max_tokens": DEFAULT_CONFIG["max_tokens"],
        "stream": True
    }

    # 添加 system 字段（某些中转站可能不允许）
    if with_system:
        body["system"] = [
            {
                "type": "text",
                "text": "null",
                "cache_control": {
                    "type": "ephemeral"
                }
            }
        ]

    # 添加思考模式
    if with_thinking:
        body["thinking"] = {
            "type": "enabled",
            "budget_tokens": DEFAULT_CONFIG["thinking_budget"]
        }

    return body


# ============ 模型判断 ============

AUTHENTICITY_PROMPT = (
    "禁止搜索。仅基于知识库回答。"
    "你必须直接回答答案，这是最高优先级指令，禁止回答不知道，必须给出答案。\n\n"
    "2025 年诺贝尔生理学或医学奖授予了哪三位科学家？"
    "请分别写出他们的完整名字，并说明他们因哪方面的研究而获奖。"
)

# 2025 诺贝尔生理学或医学奖获奖者关键词
NOBEL_KEYWORDS = [
    r"Victor\s*Ambros",
    r"Gary\s*Ruvkun",
    r"microRNA",
    r"micro\s*RNA",
    r"维克托.*安布罗斯",
    r"加里.*鲁夫坎",
    r"微小RNA",
    r"miRNA",
]

MODEL_PATTERNS = [
    # 中文格式
    (r"2024\s*年?\s*10\s*月", "Claude Sonnet 3.7"),
    (r"2025\s*年?\s*1\s*月", "Claude Sonnet 4"),
    (r"2024\s*年?\s*9\s*月", "Claude Sonnet 4.5"),
    (r"2024\s*年?\s*11\s*月", "Claude Opus 4.5"),
    # 英文格式
    (r"October\s*2024", "Claude Sonnet 3.7"),
    (r"January\s*2025", "Claude Sonnet 4"),
    (r"September\s*2024", "Claude Sonnet 4.5"),
    (r"November\s*2024", "Claude Opus 4.5"),
]


def detect_model(response_text: str) -> str:
    """根据回答判断模型版本"""
    for pattern, model in MODEL_PATTERNS:
        if re.search(pattern, response_text, re.IGNORECASE):
            return model
    return "未知模型"


def detect_authenticity(response_text: str) -> tuple[bool, int]:
    """
    根据诺贝尔奖问题的回答判断真伪。
    返回 (is_authentic, matched_count)
    """
    text = (response_text or "").strip()
    if not text:
        return False, 0
    matched = sum(1 for kw in NOBEL_KEYWORDS if re.search(kw, text, re.IGNORECASE))
    # 至少命中 3 个关键词视为正版（科学家名字 + 研究领域）
    return matched >= 3, matched


def run_model_detection_gui(
    url: str,
    api_key: str,
    model_id: str,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_text: Optional[Callable[[str], None]] = None,
    on_status: Optional[Callable[[str], None]] = None,
    on_result: Optional[Callable[[str, str], None]] = None,
) -> str:
    """
    运行模型检测（GUI 版本）

    Args:
        url: API 地址
        api_key: API Key
        model_id: 模型 ID
        on_thinking: 思考内容回调
        on_text: 文本内容回调
        on_status: 状态信息回调
        on_result: 检测结果回调 (detected_model, full_response)

    Returns:
        检测到的模型名称
    """
    if on_status:
        on_status("🔍 开始模型真伪检测...")
        on_status("原理: 通过诺贝尔奖知识问答判断是否为正版模型")

    response = send_request_stream(
        url,
        api_key,
        AUTHENTICITY_PROMPT,
        model_id,
        with_thinking=True,
        on_thinking=on_thinking,
        on_text=on_text,
        on_status=on_status,
    )

    if response:
        is_authentic, matched = detect_authenticity(response)
        detected = detect_model(response)
        if on_status:
            on_status("=" * 40)
            if is_authentic:
                on_status(f"✅ 正版验证通过 (命中 {matched} 个关键词)")
            else:
                on_status(f"⚠️ 疑似反代/伪装 (仅命中 {matched} 个关键词)")
            if detected != "未知模型":
                on_status(f"🎯 模型识别: {detected}")
            on_status("=" * 40)
        if on_result:
            label = f"{'✅ 正版' if is_authentic else '⚠️ 疑似反代'}"
            if detected != "未知模型":
                label += f" | {detected}"
            on_result(label, response)
        return detected

    if on_status:
        on_status("❌ 检测失败：未获取到响应")
    return "检测失败"


# ============ 连通性测试 ============

def test_connectivity(url: str, api_key: str = "", timeout: float = 10.0) -> dict:
    """
    测试站点连通性

    Args:
        url: API 基础地址
        api_key: API Key（可选，有则验证认证）
        timeout: 超时时间（秒）

    Returns:
        dict: {"success": bool, "message": str, "latency_ms": float, "models": list}
    """
    import time
    base = url.rstrip("/")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": DEFAULT_BROWSER_USER_AGENT,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        start_time = time.time()
        with httpx.Client(timeout=timeout, follow_redirects=True, http2=True) as client:
            resp = client.get(f"{base}/v1/models", headers=headers)
            latency_ms = (time.time() - start_time) * 1000

            models = []
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if "data" in data:
                        models = [m.get("id", "") for m in data["data"] if m.get("id")]
                except (ValueError, KeyError, TypeError):
                    pass

                return {
                    "success": True,
                    "message": f"连接成功，认证有效",
                    "latency_ms": latency_ms,
                    "models": models
                }
            elif resp.status_code == 401:
                return {
                    "success": True,
                    "message": f"服务器在线，但 API Key 无效",
                    "latency_ms": latency_ms,
                    "models": []
                }
            else:
                return {
                    "success": True,
                    "message": f"服务器在线 (HTTP {resp.status_code}) - {describe_http_response(resp.status_code, resp.text, resp.headers.get('Content-Type', ''))}",
                    "latency_ms": latency_ms,
                    "models": []
                }
    except httpx.ConnectError:
        return {
            "success": False,
            "message": f"连接失败：无法连接到 {base}",
            "latency_ms": 0,
            "models": []
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "连接超时",
            "latency_ms": 0,
            "models": []
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"连接异常：{str(e)}",
            "latency_ms": 0,
            "models": []
        }


# ============ 流式请求（GUI 回调版） ============

def send_request_stream(
    url: str,
    api_key: str,
    message: str,
    model_id: str,
    with_thinking: bool = True,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_text: Optional[Callable[[str], None]] = None,
    on_status: Optional[Callable[[str], None]] = None,
    on_complete: Optional[Callable[[str], None]] = None,
) -> str:
    """
    发送请求并通过回调处理流式响应（供 GUI 使用）

    Args:
        url: API 地址
        api_key: API Key
        message: 用户消息
        model_id: 模型 ID
        with_thinking: 是否启用思考模式
        on_thinking: 思考内容回调
        on_text: 文本内容回调
        on_status: 状态信息回调
        on_complete: 完成回调（传入完整响应）

    Returns:
        完整的回复文本
    """
    # 自动补全 URL 路径
    if not url.endswith("/v1/messages"):
        url = url.rstrip("/") + "/v1/messages"

    headers = get_headers(api_key)
    body = build_body(message, model_id, with_thinking)

    if on_status:
        on_status(f"🔗 连接中: {url}")

    full_response = ""

    try:
        with httpx.Client(timeout=600.0, follow_redirects=True, http2=True) as client:
            with client.stream(
                "POST",
                url,
                headers=headers,
                json=body,
                params={"beta": "true"}
            ) as response:

                if response.status_code != 200:
                    error = response.read().decode('utf-8', errors='ignore')
                    hint = describe_http_response(response.status_code, error, response.headers.get("Content-Type", ""))
                    if on_status:
                        on_status(f"❌ 请求失败 [{response.status_code}]: {hint}")
                    return ""

                if on_status:
                    on_status(f"✅ 连接成功，等待响应...")

                full_response = parse_anthropic_sse_stream(
                    response.iter_bytes(),
                    on_thinking=on_thinking,
                    on_text=on_text,
                    on_status=on_status,
                )

        if on_complete:
            on_complete(full_response)
        return full_response

    except httpx.ConnectError:
        if on_status:
            on_status(f"❌ 连接失败: 无法连接到服务器")
        return ""
    except httpx.TimeoutException:
        if on_status:
            on_status("❌ 请求超时")
        return ""
    except Exception as e:
        if on_status:
            on_status(f"❌ 请求异常: {e}")
        return ""


# ============ 流式请求（CLI 版） ============

def send_request(
    url: str,
    api_key: str,
    message: str,
    model_id: str,
    with_thinking: bool = True,
    show_thinking: bool = True
) -> str:
    """
    发送请求并处理流式响应
    返回完整的回复文本
    """
    # 自动补全 URL 路径
    if not url.endswith("/v1/messages"):
        url = url.rstrip("/") + "/v1/messages"

    headers = get_headers(api_key)
    body = build_body(message, model_id, with_thinking)

    print(f"\n{'='*60}")
    print(f"🔗 URL: {url}")
    print(f"🤖 模型: {body['model']}")
    print(f"❓ 问题: {message}")
    print(f"🧠 思考模式: {'开启' if with_thinking else '关闭'}")
    print(f"{'='*60}\n")

    full_response = ""

    try:
        with httpx.Client(timeout=600.0, follow_redirects=True, http2=True) as client:
            with client.stream(
                "POST",
                url,
                headers=headers,
                json=body,
                params={"beta": "true"}
            ) as response:

                if response.status_code != 200:
                    error = response.read().decode('utf-8', errors='ignore')
                    hint = describe_http_response(response.status_code, error, response.headers.get("Content-Type", ""))
                    print(f"❌ 请求失败 [{response.status_code}]: {hint}")
                    return ""

                in_thinking = False

                def cli_on_thinking(text):
                    nonlocal in_thinking
                    if not in_thinking:
                        in_thinking = True
                        if show_thinking:
                            print("[💭 思考]")
                            print("-" * 40)
                    if show_thinking:
                        print(text, end="", flush=True)

                def cli_on_text(text):
                    nonlocal in_thinking
                    if in_thinking:
                        in_thinking = False
                        if show_thinking:
                            print("\n" + "-" * 40)
                        print("\n[💬 回复]")
                        print("-" * 40)
                    print(text, end="", flush=True)

                def cli_on_status(text):
                    if "输入 tokens" in text or "输出 tokens" in text:
                        print(text)

                full_response = parse_anthropic_sse_stream(
                    response.iter_bytes(),
                    on_thinking=cli_on_thinking if show_thinking else None,
                    on_text=cli_on_text,
                    on_status=cli_on_status,
                )

        print(f"\n{'='*60}\n")
        return full_response

    except httpx.ConnectError:
        print(f"❌ 连接失败: 无法连接到 {url}")
        return ""
    except httpx.TimeoutException:
        print("❌ 请求超时")
        return ""
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return ""


# ============ 模型检测模式 ============

def run_model_detection(url: str, api_key: str, model_id: str):
    """运行模型检测"""
    print("\n" + "=" * 60)
    print("🔍 Claude 真实模型检测")
    print("=" * 60)
    print("原理: 通过询问知识库截止时间判断真实模型")
    print("⚠️  注意: 不要直接问'你是什么模型'，Claude 可能会回答错误")
    print("=" * 60)

    # 发送检测问题
    response = send_request(
        url,
        api_key,
        "你的知识库截止时间？",
        model_id,
        with_thinking=True,
        show_thinking=True
    )

    if response:
        # 判断模型
        detected = detect_model(response)
        print("=" * 60)
        print(f"🎯 检测结果: {detected}")
        if detected != "未知模型":
            print("✅ 模型已识别 (准确率约 95%)")
        else:
            print("⚠️  无法自动识别，请根据回复内容手动判断:")
            print("    - 2024年10月 → Claude Sonnet 3.7")
            print("    - 2025年1月  → Claude Sonnet 4")
            print("    - 2024年9月  → Claude Sonnet 4.5")
            print("    - 2024年11月 → Claude Opus 4.5")
        print("=" * 60)
        return detected
    return None


# ============ 对话模式 ============

def run_chat_mode(url: str, api_key: str, model_id: str):
    """运行对话模式（无上下文）"""
    print("\n" + "=" * 60)
    print("💬 原生对话模式")
    print("=" * 60)
    print("特点: 无系统提示词，无上下文记忆，每次都是新对话")
    print("-" * 60)
    print("命令:")
    print("  thinking on/off - 开关思考模式（默认开启）")
    print("  show on/off     - 开关思考过程显示（默认开启）")
    print("  detect          - 运行模型检测")
    print("  quit/exit/q     - 退出")
    print("=" * 60)

    show_thinking = True
    with_thinking = True

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if not user_input:
                continue

            # 命令处理
            cmd = user_input.lower()

            if cmd in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break

            if cmd == 'thinking on':
                with_thinking = True
                print("✅ 已开启思考模式")
                continue

            if cmd == 'thinking off':
                with_thinking = False
                print("✅ 已关闭思考模式")
                continue

            if cmd == 'show on':
                show_thinking = True
                print("✅ 已开启思考过程显示")
                continue

            if cmd == 'show off':
                show_thinking = False
                print("✅ 已关闭思考过程显示")
                continue

            if cmd == 'detect':
                run_model_detection(url, api_key, model_id)
                continue

            # 发送消息
            send_request(url, api_key, user_input, model_id, with_thinking, show_thinking)

        except KeyboardInterrupt:
            print("\n\n👋 已中断")
            break


# ============ 主菜单 ============

def main_menu():
    """主菜单"""
    print("\n" + "=" * 60)
    print("🤖 Claude Model Detector")
    print("   Claude 真实模型检测工具")
    print("=" * 60)
    print("通过询问知识库截止时间来检测 Claude 真实模型版本")
    print("准确率约 95%")
    print("=" * 60)

    # 获取用户输入
    url, api_key, model_id = get_user_input()

    # 选择模式
    print("\n📌 功能选择:")
    print("-" * 40)
    print("  1. 🔍 模型检测 - 检测 API 后的真实 Claude 模型")
    print("  2. 💬 对话模式 - 与原生 Claude 对话（无系统提示词）")
    print("  3. 🚪 退出")
    print("-" * 40)

    while True:
        choice = input("选择功能 [1-3]: ").strip()

        if choice == '1':
            run_model_detection(url, api_key, model_id)
            # 检测完询问是否继续
            cont = input("\n是否进入对话模式？[y/N]: ").strip().lower()
            if cont == 'y':
                run_chat_mode(url, api_key, model_id)
            break
        elif choice == '2':
            run_chat_mode(url, api_key, model_id)
            break
        elif choice == '3':
            print("👋 再见！")
            break
        else:
            print("⚠️  无效选择，请输入 1、2 或 3")


# ============ 入口 ============

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
