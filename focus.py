# focus.py

import sys

_previous_hwnd = None


def remember_focus():
    global _previous_hwnd

    if sys.platform == "win32":
        import ctypes

        _previous_hwnd = ctypes.windll.user32.GetForegroundWindow()


def restore_focus():
    if sys.platform == "win32" and _previous_hwnd:
        import ctypes

        ctypes.windll.user32.SetForegroundWindow(_previous_hwnd)

    elif sys.platform.startswith("linux"):
        # pas de garantie sous Wayland
        pass
