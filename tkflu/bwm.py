"""窗口外观管理（Border/Window Manager 混入）。

``BWm`` 负责窗口级的背景色、主题切换、自定义标题栏与关闭行为，
由 :class:`~tkflu.window.FluWindow` 与 :class:`~tkflu.toplevel.FluToplevel`
共同继承。"""

from .designs.gradient import FluGradient


class BWm(FluGradient):
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
                        "back_color": "#ffffff",
                        "back_opacity": 0,
                        "border_color": "#000000",
                        "border_color_opacity": 0,
                        "border_color2": None,
                        "border_color2_opacity": None,
                        "border_width": 1,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_color,
                    },
                    hover={
                        "back_color": self.attributes.closebutton.back_color,
                        "back_opacity": 1,
                        "border_color": "#000000",
                        "border_color_opacity": 0,
                        "border_color2": None,
                        "border_color2_opacity": None,
                        "border_width": 1,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_hover_color,
                    },
                    pressed={
                        "back_color": self.attributes.closebutton.back_color,
                        "back_opacity": 0.7,
                        "border_color": "#000000",
                        "border_color_opacity": 0,
                        "border_color2": None,
                        "border_color2_opacity": None,
                        "border_width": 1,
                        "radius": 0,
                        "text_color": self.attributes.closebutton.text_hover_color,
                    },
                    disabled={
                        "back_color": "#ffffff",
                        "back_opacity": 0.3,
                        "border_color": "#000000",
                        "border_color_opacity": 0,
                        "border_color2": None,
                        "border_color2_opacity": None,
                        "border_width": 1,
                        "radius": 0,
                        "text_color": "#a2a2a2",
                    },
                )
                self.closebutton._draw()

    def _event_key_esc(self, event=None):
        self._event_delete_window()

    def _event_delete_window(self):
        self.destroy()

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
                    "text_hover_color": None,
                },
            }
        )

        self.theme(mode)

    def theme(self, mode: str):
        """
        把窗口（连同里面的控件）切到 ``mode``。

        旧实现只改窗口自己的配色，子控件要等 ``FluThemeManager`` 一个一个来；
        而换到窗口背景色的那一趟用的是**裸 ``after``**、还夹着 ``update()``。
        现在整棵子树交给统一过渡：所有组件共用一条时间轴（见
        :mod:`tkflu.theme_transition`）。

        :param mode:
        :return:
        """
        from .theme_transition import applying_themes, run_theme_transition

        # 两种情况只能"只改自己"：
        #  * applying_themes()：正被统一过渡驱动，子控件由驱动方负责；
        #  * 还没有 Tk 实例：``FluWindow.__init__`` 是在 ``Tk.__init__``
        #    **之前**调 ``_init()`` 的，那时还没法遍历控件树。
        if applying_themes() or not self._tk_ready():
            self.theme_myself(mode=mode)
            return
        run_theme_transition(self, mode)

    def _tk_ready(self) -> bool:
        """这个控件是否已经拿到 Tk 解释器。

        .. warning::
           不能用 ``getattr(self, "tk", None)``——``tkinter.Misc.__getattr__``
           会把未知属性转发给 ``self.tk``，而 ``self.tk`` 正是要问的东西，
           结果是无限递归 ``RecursionError``。所以直接查实例字典。
        """
        return self.__dict__.get("tk") is not None

    def theme_myself(self, mode: str):
        """
        修改该窗口的Fluent主题（只改这个窗口自己）

        :param mode:
        :return:
        """

        previous = self.__dict__.get("mode")
        self.mode = mode
        if str(mode).lower() != str(previous or "").lower():
            self._apply_titlebar_style(mode)
        if str(mode).lower() == "dark":
            self._dark()
        else:
            self._light()

    def _apply_titlebar_style(self, mode: str):
        """把 Windows 原生的标题栏也染成对应深浅（没有 pywinstyles 就跳过）。

        .. warning::
           只在**模式真的变了**的时候调，不是随手调调就行：
           ``pywinstyles.detect()`` 内部会 ``window.update()``——那会把
           **全部待办事件**（含用户输入）跑一遍。换肤本来就是我们刚拆掉的
           "在换肤里跑事件循环"，没必要因为一次重复设置又把它请回来。
        """
        try:
            import pywinstyles

            pywinstyles.apply_style(
                self, "dark" if str(mode).lower() == "dark" else "light"
            )
        except ModuleNotFoundError:
            pass
        except Exception:
            # 个别 Windows 版本 / 主题组合下 apply_style 会失败，
            # 那不该让窗口换不了肤。
            pass

    def _theme(
        self, mode, animation_steps: int = None, animation_step_time: int = None
    ):
        from .designs.window import window

        n = window(mode)
        """if self.attributes.back_color is not None:
            n["back_color"] = self.attributes.back_color"""
        if animation_steps is None:
            from .designs.animation import get_animation_steps

            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time

            animation_step_time = get_animation_step_time()
        if not animation_steps == 0 or not animation_step_time == 0:
            if self.dcget("back_color"):
                back_colors = self.generate_hex2hex(
                    self.dcget("back_color"), n["back_color"], steps=animation_steps
                )
                for i in range(animation_steps):

                    def update(ii=i):  # 使用默认参数立即捕获i的值
                        self.dconfigure(back_color=back_colors[ii])
                        self._draw()

                    self.after(
                        i * animation_step_time, update
                    )  # 直接传递函数，不需要lambda

        self.dconfigure(
            back_color=n["back_color"],
            text_color=n["text_color"],
            closebutton={
                "back_color": n["closebutton"]["back_color"],
                "text_color": n["closebutton"]["text_color"],
                "text_hover_color": n["closebutton"]["text_hover_color"],
            },
        )

    def _light(self):
        self._theme("light")

    def _dark(self):
        self._theme("dark")

    def wincustom(self, wait=200, way=1):
        """
        自定义窗口 仅限`Windows系统`

        :param wait: 直接执行自定义窗口容易出错误 需要一点时间等待才能执行 同`after()`中的`ms`
        :param way: 取0时保留原版边框，但稳定性很差，容易崩溃。取1时不保留原版边框，但稳定性较好。
        :return:
        """

        from sys import platform
        from tkinter import Frame

        from .button import FluButton
        from .label import FluLabel

        self.titlebar = Frame(
            self, width=180, height=35, background=self.attributes.back_color
        )
        self.titlelabel = FluLabel(self.titlebar, text=self.title(), width=50)
        self.titlelabel.pack(fill="y", side="left")
        self.closebutton = FluButton(
            self.titlebar,
            text="",
            width=32,
            height=32,
            command=lambda: self._event_delete_window(),
        )
        self.closebutton.pack(fill="y", side="right")
        self.titlebar.pack(fill="x", side="top")

        if platform == "win32":
            if way == 0:
                import warnings

                from .customwindow import CustomWindow

                warnings.warn(
                    "This is EXPERIMENTAL! Please consider way=1 in production."
                )
                self.customwindow = CustomWindow(self, wait=wait)
                self.customwindow.bind_drag(self.titlebar)
                self.customwindow.bind_drag(self.titlelabel)
            else:
                self.overrideredirect(True)
                try:
                    from win32con import GWL_EXSTYLE, WS_EX_APPWINDOW, WS_EX_TOOLWINDOW
                    from win32gui import GetParent, GetWindowLong, SetWindowLong

                    hwnd = GetParent(self.winfo_id())
                    style = GetWindowLong(hwnd, GWL_EXSTYLE)
                    style = style & ~WS_EX_TOOLWINDOW
                    style = style | WS_EX_APPWINDOW
                    SetWindowLong(hwnd, GWL_EXSTYLE, style)
                    self.after(30, lambda: self.withdraw())
                    self.after(60, lambda: self.deiconify())
                except Exception:
                    # 这段是"自绘标题栏 + 任务栏归属"的实验性 Win32 调用，
                    # 失败不该让窗口建不出来（不同 Windows 版本行为不一样）。
                    pass

                self.wm_attributes("-topmost", True)

                from .customwindow2 import WindowDragArea

                self.dragarea = WindowDragArea(self)
                self.dragarea.bind(self.titlebar)
                self.dragarea.bind(self.titlelabel)

        self.custom = True
