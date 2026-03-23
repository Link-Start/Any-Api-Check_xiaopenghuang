from __future__ import annotations

import argparse
import threading

try:
    import webview
except ImportError:
    webview = None

try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

from .bridge import PreviewBridge
from .paths import WEB_DIR
from .runtime.utils import load_config

ICON_PATH = WEB_DIR / "icon.ico"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Any-API-Check pywebview UI")
    parser.add_argument("--debug", action="store_true", help="Enable pywebview debug mode")
    return parser.parse_args()


def create_tray_icon(window):
    """创建系统托盘图标"""
    if pystray is None or Image is None:
        return None

    # 加载图标
    try:
        if ICON_PATH.exists():
            icon_image = Image.open(str(ICON_PATH))
        else:
            # 如果没有图标文件，创建一个简单的默认图标
            icon_image = Image.new('RGB', (64, 64), color='#0f766e')
    except Exception:
        icon_image = Image.new('RGB', (64, 64), color='#0f766e')

    def show_window(icon, item):
        window.show()

    def quit_app(icon, item):
        icon.stop()
        window.destroy()

    # 创建托盘菜单
    menu = pystray.Menu(
        pystray.MenuItem("显示窗口", show_window, default=True),
        pystray.MenuItem("退出", quit_app)
    )

    # 创建托盘图标
    icon = pystray.Icon("Any-API-Check", icon_image, "Any-API-Check", menu)
    return icon


def main() -> int:
    args = parse_args()

    if webview is None:
        print("缺少依赖：pywebview")
        print("请先安装：pip install -r requirements.txt")
        return 1

    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        print(f"找不到页面文件：{index_file}")
        return 1

    # 加载配置，检查是否启用托盘
    config = load_config()
    minimize_to_tray = config.get("minimize_to_tray", False)

    window = webview.create_window(
        title="Any-API-Check",
        url=index_file.as_uri(),
        js_api=PreviewBridge(),
        width=1480,
        height=960,
        min_size=(1180, 760),
        background_color="#ffffff",
        text_select=True,
        on_top=False,
    )

    tray_icon = None

    # 如果启用托盘，设置窗口关闭时隐藏而不是退出
    if minimize_to_tray and pystray is not None:
        tray_icon = create_tray_icon(window)

        def on_closing():
            """窗口关闭时隐藏到托盘"""
            window.hide()
            return False  # 返回 False 阻止窗口关闭

        window.events.closing += on_closing

        # 在后台线程启动托盘图标
        def run_tray():
            if tray_icon:
                tray_icon.run()

        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()

    webview.start(gui="edgechromium", debug=args.debug)

    # 清理托盘图标
    if tray_icon:
        try:
            tray_icon.stop()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
