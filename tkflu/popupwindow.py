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

        from .designs.animation import get_animation_step_time, get_animation_steps

        FRAMES_COUNT = get_animation_steps()
        FRAME_DELAY = get_animation_step_time()

        # print(FRAMES_COUNT,FRAME_DELAY)

        self.geometry(f"+{x}+{y}")
        # self.focus_set()
        if FRAMES_COUNT != 0 or FRAME_DELAY != 0:
            self.wm_attributes("-alpha", 0.0)
            self.deiconify()

            def fade_in(step=0):
                alpha = step / FRAMES_COUNT  # 按帧数变化，从0到1
                self.wm_attributes("-alpha", alpha)
                if step < FRAMES_COUNT:
                    # 每执行一次，增加一次透明度，间隔由帧数决定
                    self.after(
                        int(round(FRAME_DELAY * FRAMES_COUNT / FRAMES_COUNT)),
                        lambda: fade_in(step + 1),
                    )

            fade_in()  # 启动动画
        else:
            self.deiconify()

    def theme(self, mode=None):
        if mode:
            self.mode = mode
            self._draw()
        for widget in self.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=self.mode.lower())
