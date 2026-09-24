"""弹出菜单窗口。

``FluPopupMenu`` 是 :class:`~tkflu.menu.FluMenu` 的基类，
以一个无边框置顶窗口的形式呈现菜单内容。"""

from .frame import FluFrame
from .popupwindow import FluPopupWindow


class FluPopupMenuWindow(FluPopupWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FluPopupMenu(FluFrame):
    def __init__(
        self,
        master=None,
        *args,
        width=100,
        height=46,
        transparent_color=None,
        style="popupmenu",
        **kwargs
    ):
        """构造弹出菜单。

        :param master: 弹出窗口的**属主**控件（通常是它所属的窗口或父菜单）。
            传了它，弹出窗口才是属主的子窗口，属主销毁时一起消失；
            不传时会挂到默认根窗口上，属主关了它还留在屏幕上。

        .. note::
           旧实现把 ``master`` 收进 ``*args`` 却只传给内部的 ``FluFrame``，
           弹出窗口本身没有 master。再加上 :class:`~tkflu.menu.FluMenu`
           的签名是 ``(height=None, *args, ...)``，``FluMenu(toplevel)``
           实际是把 toplevel 当成了**高度**——两个问题叠在一起，
           菜单窗口永远挂在根窗口上。
        """
        self.window = FluPopupMenuWindow(
            master,
            transparent_color=transparent_color,
            width=width,
            height=height,
        )

        super().__init__(self.window, *args, style=style, **kwargs)

        self.pack(fill="both", expand="yes", padx=5, pady=5)

    def wm_attributes(self, *args, **kwargs):
        self.window.wm_attributes(*args, **kwargs)

    attributes = wm_attributes

    def wm_protocol(self, *args, **kwargs):
        self.window.wm_protocol(*args, **kwargs)

    protocol = wm_protocol

    def wm_deiconify(self, *args, **kwargs):
        self.window.wm_deiconify(*args, **kwargs)

    deiconify = wm_deiconify

    def wm_withdraw(self, *args, **kwargs):
        self.window.wm_withdraw(*args, **kwargs)

    withdraw = wm_withdraw

    def wm_iconify(self, *args, **kwargs):
        self.window.wm_iconify(*args, **kwargs)

    iconify = wm_iconify

    def wm_resizable(self, *args, **kwargs):
        self.window.wm_resizable(*args, **kwargs)

    resizable = wm_resizable

    def wm_geometry(self, *args, **kwargs):
        self.window.wm_geometry(*args, **kwargs)

    geometry = wm_geometry

    def wm_popup(self, x, y):
        self.window.popup(x=x, y=y)

    popup = wm_popup

    def hide_all(self):
        """收起自己**以及所有上级菜单**。

        菜单是可以层层嵌套的（子菜单挂在某个菜单项上）。点掉子菜单里的
        一项时，如果只收起子菜单自己，父菜单会孤零零地留在屏幕上。
        """
        node = self
        seen = set()
        while node is not None and id(node) not in seen:
            seen.add(id(node))
            window = getattr(node, "window", None)
            if window is not None:
                try:
                    window.wm_withdraw()
                except Exception:
                    pass
            node = getattr(node, "_parent_menu", None)

    def destroy(self):
        """销毁菜单，连同它的弹出窗口。"""
        window = getattr(self, "window", None)
        try:
            super().destroy()
        finally:
            if window is not None:
                try:
                    window.destroy()
                except Exception:
                    pass
