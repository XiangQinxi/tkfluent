from .popupmenu import FluPopupMenu
from tkdeft.object import DObject


class FluMenu(FluPopupMenu):
    def __init__(self, *args, **kwargs):
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

                "actions": {}
            }
        )

        self.theme(mode=mode, style=style)

    def add_command(self, custom_widget=None, width=40, **kwargs):
        if custom_widget:
            widget = custom_widget(self)
        else:
            from .button import FluButton
            widget = FluButton(self, width=width)
        if "label" in kwargs:
            label = kwargs.pop("label")
        else:
            label = ""
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

    def add_cascade(self, custom_widget=None, width=40, menu=None, **kwargs):
        if custom_widget:
            widget = custom_widget(self)
        else:
            from .button import FluButton
            widget = FluButton(self, width=width)
        if "label" in kwargs:
            label = kwargs.pop("label")
        else:
            label = ""
        if "style" in kwargs:
            style = kwargs.pop("style")
        else:
            style = "menu"
        if "id" in kwargs:
            id = kwargs.pop("id")
        else:
            id = widget._w

        def command():
            print(menu._w)
            menu.focus_set()

            menu.popup(widget.winfo_rootx()+widget.winfo_width()+100, widget.winfo_rooty())
            menu.window.deiconify()
            menu.window.attributes("-topmost")

        if hasattr(widget, "dconfigure"):
            widget.dconfigure(text=label, command=command)
        else:
            if hasattr(widget, "configure"):
                widget.configure(text=label, command=command)
        if hasattr(widget, "theme"):
            widget.theme(style=style)

        widget.pack(side="top", fill="x", padx=1, pady=(1, 0))
        self.dcget("actions")[id] = widget