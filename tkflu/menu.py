"""下拉菜单。

``FluMenu`` 继承自 :class:`~tkflu.popupmenu.FluPopupMenu`，
用 :class:`~tkflu.button.FluButton`（``style="menu"``）逐项拼出菜单内容，
因此菜单项天然具备主题切换与悬停动画。

用 :meth:`~tkflu.menu.FluMenu.add_command` 添加普通项，
:meth:`~tkflu.menu.FluMenu.add_cascade` 添加子菜单。"""

from tkdeft.object import DObject

from .popupmenu import FluPopupMenu
from .tooltip import FluToolTipBase


class FluMenu(FluPopupMenu, FluToolTipBase):
    def __init__(self, height=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _init(self, mode, style):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "back_color": None,
                "back_opacity": None,
                "border_color": None,
                "border_color_opacity": None,
                "border_width": None,
                "radius": None,
                "actions": {},
            }
        )

        self.theme(mode=mode, style=style)

    def preferred_size(self, item_height: int = 45):
        """按当前菜单项算出弹出窗口该多大。

        历史实现把宽度写死成 100px、高度按 ``项数 * 45`` 算。
        中文菜单项在 100px 内会被截断，所以这里按最长标签实测宽度。

        :param item_height: 每项占的高度（与 ``add_command`` 里的间距对应）
        :returns: ``(width, height)``
        """
        from .defs import measure_label_width

        actions = self.dcget("actions") or {}
        widest = 0
        for widget in actions.values():
            label = ""
            if hasattr(widget, "dcget"):
                label = widget.dcget("text") or ""
            elif hasattr(widget, "cget"):
                try:
                    label = widget.cget("text") or ""
                except Exception:
                    label = ""
            # 弹出窗口每侧留 1px 内边距，再加一点外边距
            widest = max(widest, measure_label_width(self, label) + 8)

        width = max(100, widest)
        height = max(item_height, len(actions) * item_height)
        return width, height

    def add_command(self, custom_widget=None, width=None, label: str = "", **kwargs):
        if width is None:
            from .defs import measure_label_width

            width = measure_label_width(self, label)
        if custom_widget:
            widget = custom_widget(self)
        else:
            from .button import FluButton

            widget = FluButton(self, width=width)
        if "style" in kwargs:
            style = kwargs.pop("style")
        else:
            style = "menu"
        if "command" in kwargs:
            c = kwargs.pop("command")

            def command():
                c()
                self.window.wm_withdraw()

        else:

            def c():
                self.window.wm_withdraw()

            command = c
        if "id" in kwargs:
            id = kwargs.pop("id")
        else:
            id = widget._w
        if hasattr(widget, "dconfigure"):
            widget.dconfigure(text=label, command=command)
        else:
            if hasattr(widget, "configure"):
                widget.configure(text=label, command=command)
        if hasattr(widget, "theme"):
            widget.theme(style=style)

        widget.pack(side="top", fill="x", padx=1, pady=(1, 0))
        self.dcget("actions")[id] = widget

    def add_cascade(
        self, custom_widget=None, width=None, menu=None, label: str = "", **kwargs
    ):
        if width is None:
            from .defs import measure_label_width

            width = measure_label_width(self, label)
        if custom_widget:
            widget = custom_widget(self)
        else:
            from .button import FluButton

            widget = FluButton(self, width=width)
        if "style" in kwargs:
            style = kwargs.pop("style")
        else:
            style = "menu"
        if "id" in kwargs:
            id = kwargs.pop("id")
        else:
            id = widget._w

        def command(event=None):
            self.l1 = True
            # print(menu._w)

            menu.popup(
                widget.winfo_rootx() + widget.winfo_width(), widget.winfo_rooty() - 5
            )
            # 子菜单弹窗也按内容算尺寸（原来写死 100px 宽）
            menu_width, menu_height = menu.preferred_size()
            menu.window.geometry(f"{menu_width}x{menu_height}")
            menu.window.deiconify()
            menu.window.attributes("-topmost")

        if hasattr(widget, "dconfigure"):
            widget.dconfigure(text=label)
        else:
            if hasattr(widget, "configure"):
                widget.configure(text=label)
        widget.bind("<Enter>", command, add="+")
        if hasattr(widget, "theme"):
            widget.theme(style=style)

        widget.pack(side="top", fill="x", padx=1, pady=(1, 0))
        self.dcget("actions")[id] = widget
