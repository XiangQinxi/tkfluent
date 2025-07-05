from .frame import FluFrame
from .popupwindow import FluPopupWindow


class FluPopupMenuWindow(FluPopupWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FluPopupMenu(FluFrame):
    def __init__(self, *args, width=100, height=46, transparent_color="gray", style="popupmenu", **kwargs):
        self.window = FluPopupMenuWindow(transparent_color=transparent_color, width=width, height=height)

        super().__init__(self.window, *args, style=style, **kwargs)

        self.pack(fill="both", expand="yes", padx=5, pady=5)

    def wm_attributes(self, *args, **kwargs):
        self.window.wm_attributes(*args, **kwargs)

    attributes = wm_attributes

    def wm_protocol(self, *args,  **kwargs):
        self.window.wm_protocol(*args, **kwargs)

    protocol = wm_protocol

    def wm_deiconify(self, *args,  **kwargs):
        self.window.wm_deiconify(*args, **kwargs)

    deiconify = wm_deiconify

    def wm_withdraw(self, *args,  **kwargs):
        self.window.wm_withdraw(*args, **kwargs)

    withdraw = wm_withdraw

    def wm_iconify(self, *args,  **kwargs):
        self.window.wm_iconify(*args, **kwargs)

    iconify = wm_iconify

    def wm_resizable(self, *args,  **kwargs):
        self.window.wm_resizable(*args, **kwargs)

    resizable = wm_resizable

    def wm_geometry(self, *args,  **kwargs):
        self.window.wm_geometry(*args, **kwargs)

    geometry = wm_geometry

    def wm_popup(self, x, y):
        self.window.popup(x=x, y=y)

    popup = wm_popup
