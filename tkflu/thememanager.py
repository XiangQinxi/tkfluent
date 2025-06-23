from .window import FluWindow
from .toplevel import FluToplevel


class FluThemeManager(object):
    def __init__(self, window=None, mode: str = "light", delay: int or None = 100):
        if window:
            self._window = window
        else:
            from tkinter import _default_root
            self._window = _default_root
        self._mode = mode
        self.mode(self._mode)
        self._window.after(delay, lambda: self.mode(self._mode))

    def mode(self, mode: str, delay: int or None = 50):
        def _():
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
                    if hasattr(widget, "update_children"):
                        widget.update_children()
                    #widget.update()
        if not delay == 0:
            self._window.after(delay, _)
        else:
            _()
        def __():
            for widget in self._window.winfo_children():
                if hasattr(widget, "_draw"):
                    widget._draw()
                if hasattr(widget, "update_children"):
                    widget.update_children()
                widget.update()
        print(len(self._window.winfo_children()))
        self._window.after(delay+len(self._window.winfo_children()), __)

    def toggle(self, delay: int or None = None):
        if self._mode == "light":
            mode = "dark"
        else:
            mode = "light"
        self.mode(mode)
