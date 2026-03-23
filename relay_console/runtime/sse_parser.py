"""
公共 SSE 流式响应解析模块

将 Anthropic SSE 流式解析逻辑统一到此处，
供 conversation_test.py 和 test_dialog.py 共用。
"""
import json
from typing import Optional, Callable


def parse_anthropic_sse_stream(
    response_iter,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_text: Optional[Callable[[str], None]] = None,
    on_status: Optional[Callable[[str], None]] = None,
) -> str:
    """
    解析 Anthropic SSE 流式响应。

    Args:
        response_iter: 可迭代的字节流（如 httpx response.iter_bytes()）
        on_thinking: 思考内容回调
        on_text: 文本内容回调
        on_status: 状态信息回调

    Returns:
        完整的回复文本
    """
    full_response = ""
    in_thinking = False
    buffer = ""

    for chunk in response_iter:
        buffer += chunk.decode('utf-8', errors='ignore')

        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            line = line.strip()

            if not line.startswith("data: "):
                continue

            data = line[6:]
            if data == "[DONE]":
                break

            try:
                event = json.loads(data)
                event_type = event.get("type", "")

                if event_type == "content_block_start":
                    block = event.get("content_block", {})
                    if block.get("type") == "thinking":
                        in_thinking = True
                        if on_status:
                            on_status("[💭 思考中...]")
                    else:
                        in_thinking = False

                elif event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        full_response += text
                        if on_text:
                            on_text(text)
                    elif delta.get("type") == "thinking_delta":
                        if on_thinking:
                            on_thinking(delta.get("thinking", ""))

                elif event_type == "message_start":
                    usage = event.get("message", {}).get("usage", {})
                    if usage and on_status:
                        on_status(f"[📊 输入 tokens: {usage.get('input_tokens', 'N/A')}]")

                elif event_type == "message_delta":
                    usage = event.get("usage", {})
                    if usage and on_status:
                        on_status(f"[📊 输出 tokens: {usage.get('output_tokens', 'N/A')}]")

            except json.JSONDecodeError:
                pass

    return full_response
