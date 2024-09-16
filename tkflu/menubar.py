from tkinter import Frame, Menu
from tkdeft.object import DObject


class FluMenuBar(Frame, DObject):
    def __init__(self, *args, mode="light", height=40, **kwargs):
        self._init(mode)

        super().__init__(*args, height=height, **kwargs)

        self._draw(None)

        self.bind("<Configure>", self._event_configure, add="+")

    def _init(self, mode):

        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "back_color": "#f3f3f3",

                "actions": {}
            }
        )

        self.theme(mode=mode)

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
            command = kwargs.pop("command")
        else:
            def empty():
                pass

            command = empty
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

        widget.pack(side="left", padx=5, pady=5)
        self.dcget("actions")[id] = widget

    from .menu import FluMenu

    def add_cascade(self, custom_widget=None, width=40, menu: FluMenu = None, **kwargs):
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
            menu.focus_set()
            menu.popup(widget.winfo_rootx(), widget.winfo_rooty() + widget.winfo_height())
            menu.window.deiconify()
            menu.window.attributes("-topmost")

        if hasattr(widget, "dconfigure"):
            widget.dconfigure(text=label, command=command)
        else:
            if hasattr(widget, "configure"):
                widget.configure(text=label, command=command)
        if hasattr(widget, "theme"):
            widget.theme(style=style)

        widget.pack(side="left", padx=5, pady=5)
        self.dcget("actions")[id] = widget

    def action(self, id):
        return self.dcget("actions")[id]

    def theme(self, mode="light"):
        self.theme_myself(mode=mode)

        actions = self.dcget("actions")

        for key in actions:
            widget = actions[key]
            if hasattr(widget, "theme"):
                widget.theme(mode=mode)
                if hasattr(widget, "_draw"):
                    widget._draw()
                widget.update()

    def theme_myself(self, mode="light"):
        self.mode = mode
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        self.dconfigure(
            back_color="#f3f3f3"
        )

    def _dark(self):
        self.dconfigure(
            back_color="#202020"
        )

    def _draw(self, event=None):
        self.config(background=self.attributes.back_color)

    def _event_configure(self, event=None):
        self._draw(event)
