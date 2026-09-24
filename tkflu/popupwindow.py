"""通用弹出窗口。

``FluPopupWindow`` 提供淡入淡出、置顶、自动关闭等行为的无边框窗口，
是提示气泡、右键菜单等组件的基础。"""

from tkinter import Toplevel


class FluPopupWindow(Toplevel):
    def __init__(
        self,
        *args,
        transparent_color=None,
        mode="light",
        width=100,
        height=46,
        custom=True,
        **kwargs,
    ):
        super().__init__(*args, background=transparent_color, **kwargs)

        self.theme(mode=mode)

        self._transparent_color = transparent_color

        if width > 0 and height > 0:
            self.geometry(f"{width}x{height}")

        if custom:
            self.overrideredirect(True)

            self._draw()

        self.withdraw()

        self.bind("<FocusOut>", self._event_focusout, add="+")
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        if hasattr(self, "tk"):
            if self.overrideredirect():
                if self._transparent_color is None:
                    from .designs.window import window

                    self.transparent_color = window(self.mode)["transparent_color"]
                else:
                    self.transparent_color = self._transparent_color
                # print(self.transparent_color)
                self.wm_attributes("-transparentcolor", self.transparent_color)
                self.configure(background=self.transparent_color)

    def _event_focusout(self, event=None):
        """self.wm_attributes("-alpha", 1)
        self.deiconify()

        from .designs.animation import get_animation_steps, get_animation_step_time

        FRAMES_COUNT = get_animation_steps()
        FRAME_DELAY = get_animation_step_time()

        def fade_out(step=1):
            alpha = step / FRAMES_COUNT  # 按帧数变化，从0到1
            self.wm_attributes("-alpha", alpha)
            if step < FRAMES_COUNT:
                # 每执行一次，增加一次透明度，间隔由帧数决定
                self.after(int(round(FRAME_DELAY * FRAMES_COUNT / FRAMES_COUNT)), lambda: fade_out(step - 1))

        fade_out()  # 启动动画"""
        self.withdraw()

    def popup(self, x, y):
        """在 ``(x, y)`` 处显示弹出窗口（带淡入动画）。

        .. note::
           旧实现的条件写成 ``if FRAMES_COUNT != 0 or FRAME_DELAY != 0``，
           但动画里要做 ``alpha = step / FRAMES_COUNT``。只要用户把**帧数**
           设成 0、只留帧间隔（``set_animation_steps(0)`` +
           ``set_animation_step_time(30)``，这是很自然的"我只想调慢一点"），
           淡入就会 ``ZeroDivisionError``——表现为菜单打不开、提示气泡
           一悬停就报错。这里同时修两件事：条件改成"两个都非零"，
           并且给帧数兜底成 1。
        """
        from .designs.animation import get_animation_step_time, get_animation_steps

        frames = max(0, int(get_animation_steps()))
        delay = max(0, int(get_animation_step_time()))

        self.geometry(f"+{x}+{y}")
        if frames > 0 and delay > 0:
            self.wm_attributes("-alpha", 0.0)
            self.deiconify()

            def fade_in(step=0):
                self.wm_attributes("-alpha", step / float(frames))
                if step < frames:
                    # 每执行一次，透明度提高一档，间隔为 FRAME_DELAY
                    self.after(delay, lambda: fade_in(step + 1))

            fade_in()  # 启动动画
        else:
            # 关掉动画时把透明度复位，否则上一次动画留下的 0.4 会让窗口半透明
            self.wm_attributes("-alpha", 1.0)
            self.deiconify()

    def theme(self, mode=None):
        if mode:
            self.mode = mode
            self._draw()
        for widget in self.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=self.mode.lower())

    def destroy(self):
        """销毁弹出窗口前先收回它子树里的 ``after`` 回调。

        .. warning::
           弹出窗口里可能装着会做过渡动画的组件（菜单项就是
           :class:`~tkflu.button.FluButton`）。Toplevel 被销毁时，
           Tkinter 会删掉这些控件自己注册的 Tcl 命令，但**不会**取消已经
           排队的 ``after``——那些定时器随后触发时就会在控制台刷

           .. code-block:: text

               invalid command name "140234567890123run"

           所以这里必须显式清一遍（``FluWindow`` / ``FluToplevel`` 早就这么做了，
           弹出窗口是漏网的那个）。
        """
        from ._after import cancel_all_after

        try:
            cancel_all_after(self)
        except Exception:
            pass
        super().destroy()
