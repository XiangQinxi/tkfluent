from .popupwindow import FluPopupWindow
from tkinter import Event, Widget
import sys


class FluToolTip(FluPopupWindow):
    def __init__(self, widget: Widget, text, mode="light", delay=400, show_time=100.0, *args, **kwargs):
        super().__init__(*args, transparent_color="#ebebeb", **kwargs)

        from .label import FluLabel
        from .frame import FluFrame

        self.overrideredirect(True)

        self._delay = delay
        self._show_time = show_time
        self._widget = widget

        self._frame = FluFrame(self)
        self._frame.theme(mode, style="popupmenu")

        self._label = FluLabel(self._frame, text=text)
        self._label.pack(fill="both", expand=True, padx=3, pady=3)

        self._frame.pack(fill="both", expand=True, padx=3, pady=3)

        self._widget.bind('<Enter>', self.enter, add="+")
        self._widget.bind('<Leave>', self.leave, add="+")

        self.theme(mode)

    def enter(self, event: Event):
        def check() -> None:
            if self._enter:
                # 先定位工具提示位置
                self.popup(
                    round(self._widget.winfo_rootx() + self._widget.winfo_width() / 2 - self.winfo_width() / 2),
                    round(self._widget.winfo_rooty() + self._widget.winfo_height() + 2)
                )

        self.id = self.after(self._delay, check)
        self._enter = True

    def leave(self, event):
        self.after_cancel(self.id)
        self._enter = False
        self.withdraw()

    def theme(self, mode=None):
        from .designs.tooltip import tooltip
        n = tooltip(mode)
        self.configure(
            background=n["back_color"]
        )
        self.wm_attributes("-transparentcolor", n["back_color"])
        #print(n["back_color"])
        if hasattr(self, "_frame"):
            self._frame.dconfigure(
                back_color=n["frame_color"],
                border_color=n["frame_border_color"],
                border_color_opacity=1,
                border_width=2,
                radius=7,
            )
        if hasattr(self, "_label"):
            self._label.theme(mode)
        super().theme(mode)


class FluToolTip2(FluPopupWindow):
    def __init__(self, widget, text, mode="light", *args, **kwargs):
        super().__init__(*args, transparent_color="#ebebeb", **kwargs)

        from .label import FluLabel
        from .frame import FluFrame

        self.overrideredirect(True)

        self._widget = widget

        self._frame = FluFrame(self)
        self._frame.theme(mode, style="popupmenu")

        self._label = FluLabel(self._frame, text=text)
        self._label.pack(fill="both", expand=True, padx=3, pady=3)

        self._frame.pack(fill="both", expand=True, padx=3, pady=3)

        self._widget.bind('<Enter>', self.show, add="+")
        self._widget.bind('<Leave>', self.hide, add="+")
        self._widget.bind('<Motion>', self.move, add="+")

        self.theme(mode)

    def popup2(self, x, y):
        self.geometry(f"+{x}+{y}")

    def show(self, event: Event):
        self.popup(
            round(event.x_root - self.winfo_width() / 2),
            round(event.y_root + 10)
        )
        self.deiconify()

    def hide(self, event):
        self.withdraw()

    def move(self, event):
        self.popup2(
            round(event.x_root - self.winfo_width() / 2),
            round(event.y_root + 10)
        )

    def theme(self, mode=None):
        from .designs.tooltip import tooltip
        n = tooltip(mode)
        self.configure(
            background=n["back_color"]
        )

        self.wm_attributes("-transparentcolor", n["back_color"])
        #print(n["back_color"])
        if hasattr(self, "_frame"):
            self._frame.dconfigure(
                back_color=n["frame_color"],
                border_color=n["frame_border_color"],
                border_color_opacity=1,
                border_width=2,
                radius=7,
            )
        if hasattr(self, "_label"):
            self._label.theme(mode)
        super().theme(mode)


class FluToolTipBase:
    def tooltip(self, *args, way=0, **kwargs):
        if way == 0:
            self._tooltip = FluToolTip(*args, widget=self, **kwargs)
        elif way == 1:
            self._tooltip = FluToolTip2(*args, widget=self, **kwargs)

