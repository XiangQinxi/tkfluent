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
                "border_color": "#e5e5e5",

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

    def theme_myself(self, mode="light", animation_steps: int = None, animation_step_time: int = None):
        if animation_steps is None:
            from .designs.animation import get_animation_steps
            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time
            animation_step_time = get_animation_step_time()
        from .designs.menubar import menubar
        m = menubar(mode)
        self.mode = mode
        if hasattr(self, "tk"):
            if not animation_steps == 0 or not animation_step_time == 0:
                if mode.lower() == "dark":
                    back_colors = self.generate_hex2hex(self.attributes.back_color, m["back_color"], steps=animation_steps)
                    border_colors = self.generate_hex2hex(self.attributes.border_color, m["border_color"],
                                                          steps=animation_steps)
                else:
                    back_colors = self.generate_hex2hex(self.attributes.back_color, m["back_color"], steps=animation_steps)
                    border_colors = self.generate_hex2hex(self.attributes.border_color, m["border_color"],
                                                          steps=animation_steps)
                for i in range(animation_steps):
                    def update(ii=i):  # 使用默认参数立即捕获i的值
                        self.dconfigure(back_color=back_colors[ii], border_color=border_colors[ii])
                        self._draw()

                    self.after(i * animation_step_time, update)  # 直接传递函数，不需要lambda

                self.after(animation_steps * animation_step_time + 50, lambda: self.update_children())
            else:
                self.dconfigure(back_color=m["back_color"])
                self.dconfigure(border_color=m["border_color"])
                self._draw()

    def _draw(self, event=None):
        self.config(background=self.attributes.back_color)
        if not hasattr(self, "border"):
            self.border = Frame(self, height=1.2, background=self.attributes.border_color)
        else:
            self.border.configure(background=self.attributes.border_color)
        self.border.pack(fill="x", expand="yes", side="bottom")

    def _event_configure(self, event=None):
        self._draw(event)
