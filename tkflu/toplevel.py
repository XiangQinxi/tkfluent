from tkinter import Toplevel
from tkdeft.object import DObject
from .bwm import BWm


class FluToplevel(Toplevel, BWm, DObject):

    """Fluent设计的子窗口"""

    def __init__(self, *args, mode="light", **kwargs):

        """
        初始化类

        :param args: 参照tkinter.TK.__init__
        :param className: 参照tkinter.TK.__init__
        :param mode: Fluent主题模式 分为 “light” “dark”
        :param kwargs: 参照tkinter.TK.__init__
        """

        Toplevel.__init__(self, *args, **kwargs)

        self._init(mode)

        self.custom = False

        # 设置窗口图标
        from .icons import light
        from tkinter import PhotoImage
        self.iconphoto(False, PhotoImage(file=light()))

        self.bind("<Configure>", self._event_configure, add="+")
        self.bind("<Escape>", self._event_key_esc, add="+")
        self.protocol("WM_DELETE_WINDOW", self._event_delete_window)

    def theme(self, mode: str):
        super().theme(mode)
        self._mode = mode
        for widget in self.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=mode)
                if hasattr(widget, "_draw"):
                    widget._draw()
                if hasattr(widget, "update_children"):
                    widget.update_children()
