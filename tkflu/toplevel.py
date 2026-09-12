"""子窗口。

``FluToplevel`` 是 :class:`~tkflu.window.FluWindow` 的子窗口版本，
共享同一套主题与图标设置。"""

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

        # 设置窗口图标：直接用内嵌 base64 建图，不落盘（见 .icons 模块说明）
        from .icons import icon_photoimage

        self._icon_photo = icon_photoimage("light", master=self)
        self.iconphoto(False, self._icon_photo)

        self.bind("<Configure>", self._event_configure, add="+")
        self.bind("<Escape>", self._event_key_esc, add="+")
        self.protocol("WM_DELETE_WINDOW", self._event_delete_window)

    def destroy(self):
        """关闭子窗口前先回收待执行的 ``after`` 回调（详见 :mod:`tkflu._after`）。"""
        from ._after import cancel_all_after

        cancel_all_after(self)
        super().destroy()

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
