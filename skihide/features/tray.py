import threading
import traceback
import pystray
from pystray import MenuItem as item
from PIL import Image

from ..utils.paths import resource_path

def start_tray(app, logger):
    """Start pystray icon in background thread. app must provide _restore_window() and quit_app()."""
    try:
        icon_path = resource_path("icon.ico")
        image = Image.open(icon_path)

        def on_show(icon, _item):
            app.root.after(0, app._restore_window)

        def on_exit(icon, _item):
            app.root.after(0, app.quit_app)

        # Invisible default item (handles double-click) without bold visible menu entry
        menu = pystray.Menu(
            item(" ", on_show, default=True, visible=False),
            item("显示主界面", on_show),
            item("退出程序", on_exit),
        )

        tray_icon = pystray.Icon("SkiHide", image, "SkiHide", menu)

        t = threading.Thread(target=tray_icon.run, daemon=True)
        t.start()
        return tray_icon, t
    except Exception:
        logger.error(f"托盘图标创建失败: {traceback.format_exc()}")
        raise
