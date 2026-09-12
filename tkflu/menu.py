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

    def add_command(self, custom_widget=None, width=None, label: str = "", **kwargs):
        if width is None:
            width = len(label) * 8
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
            width = len(label) * 8
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
            height = len(self.dcget("actions")) * 45
            # print(height)
            menu.window.geometry(f"100x{height}")
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
