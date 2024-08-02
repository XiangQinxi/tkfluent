from .window import FluWindow
from .toplevel import FluToplevel


class FluThemeManager(object):
    def __init__(self, window=None, mode: str = "light"):
        if window:
            self._window = window
        else:
            from tkinter import _default_root
            self._window = _default_root
        self._mode = mode
        self.mode(self._mode)
        self._window.after(100, lambda: self.mode(self._mode))

    def mode(self, mode: str):
        self._mode = mode
        if hasattr(self._window, "theme"):
            self._window.theme(mode=mode)
            if hasattr(self._window, "_draw"):
                self._window._draw()
            self._window.update()
        for widget in self._window.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=mode)
                if hasattr(widget, "_draw"):
                    widget._draw()
                widget.update()
