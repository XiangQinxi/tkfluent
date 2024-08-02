class BWm(object):
    def _draw(self, event=None):

        """
        重新绘制窗口及自定义的窗口组件

        :param event:
        """

        self.configure(background=self.attributes.back_color)
        if self.custom:
            if hasattr(self, "titlebar"):
                self.titlebar.configure(background=self.attributes.back_color)
                self.titlebar.update()
            if hasattr(self, "titlelabel"):
                self.titlelabel.dconfigure(text_color=self.attributes.text_color)
                self.titlelabel._draw()
            if hasattr(self, "closebutton"):
                self.closebutton.dconfigure(
                    rest={
                        "back_color": self.titlebar.cget("background"),
                        "border_color": "#f0f0f0",
                        "border_color2": "#d6d6d6",
                        "border_width": 0,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_color,
                    },
                    hover={
                        "back_color": self.attributes.closebutton.back_color,
                        "border_color": "#f0f0f0",
                        "border_color2": "#d6d6d6",
                        "border_width": 0,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_hover_color,
                    },
                    pressed={
                        "back_color": self.attributes.closebutton.back_color,
                        "border_color": "#f0f0f0",
                        "border_color2": "#f0f0f0",
                        "border_width": 0,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_hover_color,
                    }
                )
                self.closebutton._draw()

    def _event_configure(self, event=None):

        """
        触发 `<Configure>` 事件

        :param event:
        :return:
        """

        self._draw()

    def _init(self, mode):
        from easydict import EasyDict
        self.attributes = EasyDict(
            {
                "back_color": None,
                "text_color": None,
                "closebutton": {
                    "back_color": None,
                    "text_color": None,
                    "text_hover_color": None
                }
            }
        )

        self.theme(mode)

    def _exit(self):
        self.quit()

    def theme(self, mode: str):

        """
        同 `theme_myself`

        :param mode:
        :return:
        """

        self.theme_myself(mode=mode)

    def theme_myself(self, mode: str):

        """
        修改该窗口的Fluent主题

        :param mode:
        :return:
        """

        self.mode = mode
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        self.dconfigure(
            back_color="#ffffff",
            text_color="#000000",
            closebutton={
                "back_color": "red",
                "text_color": "#000000",
                "text_hover_color": "#ffffff"
            }
        )

    def _dark(self):
        self.dconfigure(
            back_color="#202020",
            text_color="#ffffff",
            closebutton={
                "back_color": "red",
                "text_color": "#ffffff",
                "text_hover_color": "#000000"
            }
        )

    def wincustom(self, wait=200, way=1):

        """
        自定义窗口 仅限`Windows系统`

        :param wait: 直接执行自定义窗口容易出错误 需要一点时间等待才能执行 同`after()`中的`ms`
        :param way: 取0时保留原版边框，但稳定性很差，容易崩溃。取1时不保留原版边框，但稳定性较好。
        :return:
        """

        from sys import platform
        from .button import FluButton
        from .label import FluLabel
        from tkinter import Frame
        self.titlebar = Frame(self, width=180, height=35, background=self.attributes.back_color)
        self.titlelabel = FluLabel(self.titlebar, text=self.title(), width=50)
        self.titlelabel.pack(fill="y", side="left")
        self.closebutton = FluButton(self.titlebar, text="", width=32, height=32, command=lambda: self._exit())
        self.closebutton.pack(fill="y", side="right")
        self.titlebar.pack(fill="x", side="top")

        if platform == "win32":
            if way == 0:
                from .customwindow import CustomWindow
                self.customwindow = CustomWindow(self, wait=wait)
                self.customwindow.bind_drag(self.titlebar)
                self.customwindow.bind_drag(self.titlelabel)
            else:
                self.overrideredirect(True)
                try:
                    from win32gui import GetParent, GetWindowLong, SetWindowLong
                    from win32con import GWL_EXSTYLE, WS_EX_APPWINDOW, WS_EX_TOOLWINDOW
                    hwnd = GetParent(self.winfo_id())
                    style = GetWindowLong(hwnd, GWL_EXSTYLE)
                    style = style & ~WS_EX_TOOLWINDOW
                    style = style | WS_EX_APPWINDOW
                    SetWindowLong(hwnd, GWL_EXSTYLE, style)
                    self.after(30, lambda: self.withdraw())
                    self.after(60, lambda: self.deiconify())
                except:
                    pass

                self.wm_attributes("-topmost", True)

                from .customwindow2 import WindowDragArea
                self.dragarea = WindowDragArea(self)
                self.dragarea.bind(self.titlebar)
                self.dragarea.bind(self.titlelabel)

        self.custom = True
