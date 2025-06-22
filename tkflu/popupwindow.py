from tkinter import Toplevel


class FluPopupWindow(Toplevel):
    def __init__(self, *args, transparent_color="#ebebeb", mode="light", width=100, height=46, custom=True, **kwargs):
        super().__init__(*args, background=transparent_color, **kwargs)

        self.theme(mode=mode)

        self.geometry(f"{width}x{height}")

        if custom:
            self.transient_color = transparent_color
            self.overrideredirect(True)
            self.wm_attributes("-transparentcolor", transparent_color)

        self.withdraw()

        self.bind("<FocusOut>", self._event_focusout, add="+")

    def _event_focusout(self, event=None):
        self.withdraw()

    def popup(self, x, y):
        self.geometry(f"+{x}+{y}")
        #self.focus_set()

    def theme(self, mode=None):
        if mode:
            self.mode = mode
        for widget in self.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=self.mode.lower())
