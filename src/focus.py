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

    # Pas de retour auto du focus, utiliser ALT + TAB
    elif sys.platform.startswith("linux"):
        if os.environ.get("WAYLAND_DISPLAY"):
            # WSLg / Wayland :
            # restauration de focus non autorisée par le protocole
            pass

        elif os.environ.get("DISPLAY"):
            # X11 : possible avec xdotool/python-xlib
            pass
        
