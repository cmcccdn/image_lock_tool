"""System tray icon for Image Lock Tool."""
import os
import threading

from PIL import Image

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    HAS_TRAY = True
except ImportError:
    pystray = None
    HAS_TRAY = False


def _icon_image():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.normpath(os.path.join(here, "..", "..", "resources", "icon.png"))
    if os.path.exists(p):
        return Image.open(p)
    return Image.new("RGBA", (64, 64), (231, 76, 60, 255))


def run_tray(on_show, on_quit=None):
    if not HAS_TRAY:
        return None

    def _show(_icon=None, _item=None):
        try:
            on_show()
        except Exception:
            pass

    def _quit(icon, _item=None):
        try:
            icon.stop()
        finally:
            if on_quit:
                on_quit()

    icon = pystray.Icon(
        "image_lock_tool",
        _icon_image(),
        "图片查看锁定小工具",
        Menu(
            Item("打开主界面", _show, default=True),
            Item("退出", _quit),
        ),
    )

    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon
