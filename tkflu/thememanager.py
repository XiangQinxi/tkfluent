from .window import FluWindow
from .toplevel import FluToplevel
from typing import Union


class FluThemeManager(object):
    def __init__(self, window=None, mode: str = "light", delay: Union[int, None] = 100):
        if window:
            self._window = window
        else:
            from tkinter import _default_root
            self._window = _default_root
        self._mode = mode
        #self.mode(self._mode)
        #self._window.after(delay, lambda: self.mode(self._mode))

    def mode(self, mode: str, delay: Union[int, None] = None):
        def update_window():
            self._mode = mode
            if hasattr(self._window, "theme"):
                self._window.theme(mode=mode)
                if hasattr(self._window, "_draw"):
                    self._window._draw()
                self._window.update()
        def update_children():
            for widget in self._window.winfo_children():
                if hasattr(widget, "theme"):
                    widget.theme(mode=mode)
                    if hasattr(widget, "_draw"):
                        widget._draw()
                    if hasattr(widget, "update_children"):
                        widget.update_children()
                    #widget.update()
        update_window()
        update_children()

        def update_children2():
            for widget in self._window.winfo_children():
                if hasattr(widget, "_draw"):
                    widget._draw()
                if hasattr(widget, "update_children"):
                    widget.update_children()
                widget.update()

        #self._window.after(len(self._window.winfo_children())*50, update_children2)

    def toggle(self, delay: Union[int, None] = None):
        if self._mode == "light":
            mode = "dark"
        else:
            mode = "light"
        self.mode(mode)
