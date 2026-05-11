"""Entry point for the image-extension lock tool GUI.

Run:  python gui.py
"""
import os
import sys
import ctypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_lock.gui.main_window import MainWindow
from image_lock.gui.tray import run_tray


def is_admin():
    if os.name != "nt":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def main():
    app = MainWindow()

    def show():
        try:
            app.deiconify()
            app.lift()
            app.focus_force()
        except Exception:
            pass

    def hide_to_tray():
        try:
            app.withdraw()
        except Exception:
            pass

    # close button hides to tray
    app.protocol("WM_DELETE_WINDOW", hide_to_tray)
    run_tray(show, on_quit=lambda: app.after(0, app.destroy))

    app.mainloop()


if __name__ == "__main__":
    if os.name == "nt" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    main()
