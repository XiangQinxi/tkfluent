from tkinter import Frame, Menu
from tkdeft.object import DObject
from .designs.gradient import FluGradient


class FluMenuBar(Frame, DObject, FluGradient):
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

    def show(self):
        self.pack(fill="x")

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

    def update_children(self):
        actions = self.dcget("actions")
        for key in actions:
            widget = actions[key]
            if hasattr(widget, "theme"):
                widget.theme(mode=self.mode)
                if hasattr(widget, "_draw"):
                    widget._draw()
                widget.update()

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

    def theme_myself(self, mode="light", animate_steps: int = 10):
        from .designs.menubar import menubar
        m = menubar(mode)
        self.mode = mode
        if mode.lower() == "dark":
            if hasattr(self, "tk"):
                back_colors = self.generate_hex2hex(self.attributes.back_color, m["back_color"], steps=10)
                for i in range(10):
                    def update(ii=i):  # 使用默认参数立即捕获i的值
                        self.dconfigure(back_color=back_colors[ii])
                        self._draw()

                    self.after(i * 10, update)  # 直接传递函数，不需要lambda
                self.after(animate_steps*10+50, lambda: self.update_children())
        else:
            if hasattr(self, "tk"):
                back_colors = self.generate_hex2hex(self.attributes.back_color, m["back_color"], steps=10)
                for i in range(10):
                    def update(ii=i):  # 使用默认参数立即捕获i的值
                        self.dconfigure(back_color=back_colors[ii])
                        self._draw()

                    self.after(i * 20, update)  # 直接传递函数，不需要lambda


    def _draw(self, event=None):
        self.config(background=self.attributes.back_color)

    def _event_configure(self, event=None):
        self._draw(event)
