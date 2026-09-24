"""开关组件。

``FluToggleButton`` 在按钮的基础上维护 ``checked`` 状态，
点击后触发 ``command``。常用于"切换主题""启用某项功能"等场景。"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget


class FluToggleButtonDraw(DSvgDraw):
    """开关按钮的 SVG 绘制后端。

    图元直接用 :meth:`tkdeft.windows.draw.DSvgDraw.create_roundrect`
    （几何内缩半个线宽，四边描边完整），不再重复实现一遍。
    """


class FluToggleButtonCanvas(DCanvas):
    draw = FluToggleButtonDraw

    def create_round_rectangle_with_text(
        self,
        x1,
        y1,
        x2,
        y2,
        r1,
        r2=None,
        temppath=None,
        temppath2=None,
        **kwargs,
    ) -> int:
        """画开关按钮的圆角背景。

        :param x1: 左上角 x
        :param y1: 左上角 y
        :param x2: 右下角 x
        :param y2: 右下角 y
        :param r1: 圆角半径（x 方向）
        :param r2: 圆角半径（y 方向）；为空时取 ``r1``
        :param temppath: SVG 兜底路径用的临时文件
        :param temppath2: Wand 引擎的 PNG 输出路径
        :param kwargs: ``fill`` / ``fill_opacity`` / ``outline`` / ``outline2`` /
            ``outline_opacity`` / ``outline2_opacity`` / ``width``
        :returns: 画布上的 item id

        名字里的 ``_with_text`` 是历史遗留——文字其实是 ``create_text``
        叠加上去的。实现等价于
        :meth:`tkdeft.windows.canvas.DCanvas.draw_roundrect`
        （栅格引擎走位图快速路径，否则自动回退 SVG）。
        """
        return self.draw_roundrect(
            x1,
            y1,
            x2,
            y2,
            r1,
            r2,
            temppath=temppath,
            temppath2=temppath2,
            **kwargs,
        )

    create_roundrect = create_round_rectangle_with_text


from .designs.gradient import FluGradient
from .tooltip import FluToolTipBase
from ._after import TracedAfter


class FluToggleButton(FluToggleButtonCanvas, DDrawWidget, FluToolTipBase, FluGradient, TracedAfter):
    def __init__(
        self,
        *args,
        text="",
        width=120,
        height=32,
        command=None,
        font=None,
        mode="light",
        state="normal",
        **kwargs,
    ):
        self._init(mode)

        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:

            def empty():
                pass

            command = empty

        self.dconfigure(
            text=text,
            command=command,
            state=state,
        )

        self.bind("<<Clicked>>", lambda event=None: self.toggle(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.invoke(), add="+")

        self.bind(
            "<Return>", lambda event=None: self.invoke(), add="+"
        )  # 可以使用回车键模拟点击
        self.bind(
            "<Return>", lambda event=None: self.toggle(), add="+"
        )  # 可以使用回车键模拟点击

        from .defs import set_default_font

        set_default_font(font, self.attributes, master=self)

    def _init(self, mode):

        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "state": "normal",
                "checked": False,
                "uncheck": {},
                "check": {},
            }
        )

        self.theme(mode=mode)

    def _draw(self, event=None, tempcolor: dict = None):
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()

        self.delete("all")

        state = self.dcget("state")

        _dict = None
        if not tempcolor:
            if not self.attributes.checked:
                if state == "normal":
                    if self.enter:
                        if self.button1:
                            _dict = self.attributes.uncheck.pressed
                        else:
                            _dict = self.attributes.uncheck.hover
                    else:
                        _dict = self.attributes.uncheck.rest
                else:
                    _dict = self.attributes.uncheck.disabled
            else:
                if state == "normal":
                    if self.enter:
                        if self.button1:
                            _dict = self.attributes.check.pressed
                        else:
                            _dict = self.attributes.check.hover
                    else:
                        _dict = self.attributes.check.rest
                else:
                    _dict = self.attributes.check.disabled

            _back_color = _dict.back_color
            _back_opacity = _dict.back_opacity
            _border_color = _dict.border_color
            _border_color_opacity = _dict.border_color_opacity
            _border_color2 = _dict.border_color2
            _border_color2_opacity = _dict.border_color2_opacity
            _border_width = _dict.border_width
            _radius = _dict.radius
            _text_color = _dict.text_color
        else:
            _back_color = tempcolor.back_color
            _back_opacity = tempcolor.back_opacity
            _border_color = tempcolor.border_color
            _border_color_opacity = tempcolor.border_color_opacity
            _border_color2 = tempcolor.border_color2
            _border_color2_opacity = tempcolor.border_color2_opacity
            _border_width = tempcolor.border_width
            _radius = tempcolor.radius
            _text_color = tempcolor.text_color

        from .designs.renderer import get_renderer

        if get_renderer() == 1:
            width -= 1
            height -= 1

        self.element_border = self.create_round_rectangle_with_text(
            0,
            0,
            width,
            height,
            _radius,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=_back_color,
            fill_opacity=_back_opacity,
            outline=_border_color,
            outline_opacity=_border_color_opacity,
            outline2=_border_color2,
            outline2_opacity=_border_color2_opacity,
            width=_border_width,
        )

        self.element_text = self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            anchor="center",
            fill=_text_color,
            text=self.attributes.text,
            font=self.attributes.font,
        )
        # 同 FluButton：_draw 里再 mark_dirty 自己只会造成重复重绘，已移除。

    def theme(self, mode=None, style=None):
        """切换主题。

        :param mode: ``"light"`` / ``"dark"``；省略或传空表示沿用当前值
        :param style: 开关没有样式之分，接受但忽略——
            :class:`~tkflu.menu.FluMenu` 会用 ``custom_widget`` 把一个自定义
            组件当菜单项，并且统一按 ``theme(style=...)`` 调用它。旧签名
            只收 ``mode``，于是"把 FluToggleButton 当菜单项"会直接
            ``TypeError: theme() got an unexpected keyword argument 'style'``。
        """
        resolved = mode or getattr(self, "mode", None) or "light"
        self.mode = resolved
        if str(resolved).lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        from tkflu.designs.primary_color import get_primary_color

        self.dconfigure(
            uncheck={
                "rest": {
                    "back_color": "#ffffff",
                    "back_opacity": "0.7",
                    "border_color": "#000000",
                    "border_color_opacity": "0.2",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.3",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "hover": {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.5",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.2",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "pressed": {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.3",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#636363",
                },
                "disabled": {
                    "back_color": "#ffffff",
                    "back_opacity": "1.000000",
                    "border_color": "#000000",
                    "border_color_opacity": "0.058824",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.160784",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a2a2a2",
                },
            },
            check={
                "rest": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#ffffff",
                },
                "hover": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#ffffff",
                },
                "pressed": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.08",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#c2d9ee",
                },
                "disabled": {
                    "back_color": "#000000",
                    "back_opacity": "0.22",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "1",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "1",
                    "border_width": 0,
                    "radius": 6,
                    "text_color": "#f3f3f3",
                },
            },
        )

    def _dark(self):
        from tkflu.designs.primary_color import get_primary_color

        self.dconfigure(
            uncheck={
                "rest": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.06",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#FFFFFF",
                },
                "hover": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.08",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#FFFFFF",
                },
                "pressed": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.03",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#7D7D7D",
                },
                "disabled": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.04",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a2a2a2",
                },
            },
            check={
                "rest": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "hover": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "pressed": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#295569",
                },
                "disabled": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.16",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.16",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a7a7a7",
                },
            },
        )

    def invoke(self):
        if self.attributes.state == "normal":
            self.attributes.command()

    def toggle(self, animation_steps: int = None, animation_step_time: int = None):
        if self.attributes.state == "normal":
            if animation_steps is None:
                from .designs.animation import get_animation_steps

                animation_steps = get_animation_steps()
            if animation_step_time is None:
                from .designs.animation import get_animation_step_time

                animation_step_time = get_animation_step_time()
            check = self.attributes.check
            uncheck = self.attributes.uncheck
            if not animation_steps == 0 or not animation_step_time == 0:
                # 撤销上一轮还没跑完的动画帧：连点两下时，上一轮的帧会迟到，
                # 把这一轮的状态覆盖掉。
                self.cancel_traced()
                steps = animation_steps
                if uncheck.pressed.border_color2 is None:
                    uncheck.pressed.border_color2 = uncheck.pressed.border_color
                if check.pressed.border_color2 is None:
                    check.pressed.border_color2 = check.pressed.border_color
                if uncheck.pressed.border_color2_opacity is None:
                    uncheck.pressed.border_color2_opacity = (
                        uncheck.pressed.border_color_opacity
                    )
                if check.pressed.border_color2_opacity is None:
                    check.pressed.border_color2_opacity = (
                        check.pressed.border_color_opacity
                    )
                if self.attributes.checked:
                    self.attributes.checked = False
                    back_colors = self.generate_hex2hex(
                        check.pressed.back_color, uncheck.rest.back_color, steps
                    )
                    border_colors = self.generate_hex2hex(
                        check.pressed.border_color, uncheck.rest.border_color, steps
                    )
                    border_colors2 = self.generate_hex2hex(
                        check.pressed.border_color2, uncheck.rest.border_color2, steps
                    )
                    text_colors = self.generate_hex2hex(
                        check.pressed.text_color, uncheck.rest.text_color, steps
                    )
                    import numpy as np

                    back_opacitys = np.linspace(
                        float(check.pressed.back_opacity),
                        float(uncheck.rest.back_opacity),
                        steps,
                    ).tolist()
                    border_color_opacitys = np.linspace(
                        float(check.pressed.border_color_opacity),
                        float(uncheck.rest.border_color_opacity),
                        steps,
                    ).tolist()
                    border_color2_opacitys = np.linspace(
                        float(check.pressed.border_color2_opacity),
                        float(uncheck.rest.border_color2_opacity),
                        steps,
                    ).tolist()
                else:
                    self.attributes.checked = True
                    back_colors = self.generate_hex2hex(
                        uncheck.pressed.back_color, check.rest.back_color, steps
                    )
                    # 描边要从**描边色**插值，不是背景色。
                    # 旧实现这里复制粘贴了上面一行，于是打勾的过程中边框
                    # 会从浅灰一路闪成强调蓝（而且和填充同色，看起来像没有边框）。
                    border_colors = self.generate_hex2hex(
                        uncheck.pressed.border_color, check.rest.border_color, steps
                    )
                    border_colors2 = self.generate_hex2hex(
                        uncheck.pressed.border_color2, check.rest.border_color2, steps
                    )
                    text_colors = self.generate_hex2hex(
                        uncheck.pressed.text_color, check.rest.text_color, steps
                    )
                    import numpy as np

                    back_opacitys = np.linspace(
                        float(uncheck.pressed.back_opacity),
                        float(check.rest.back_opacity),
                        steps,
                    ).tolist()
                    border_color_opacitys = np.linspace(
                        float(uncheck.pressed.border_color_opacity),
                        float(check.rest.border_color_opacity),
                        steps,
                    ).tolist()
                    border_color2_opacitys = np.linspace(
                        float(uncheck.pressed.border_color2_opacity),
                        float(check.rest.border_color2_opacity),
                        steps,
                    ).tolist()
                for i in range(steps):

                    def update(ii=i):
                        from easydict import EasyDict

                        tempcolor = EasyDict(
                            {
                                "back_color": back_colors[ii],
                                "back_opacity": back_opacitys[ii],
                                "border_color": border_colors[ii],
                                "border_color_opacity": str(border_color_opacitys[ii]),
                                "border_color2": border_colors2[ii],
                                "border_color2_opacity": str(
                                    border_color2_opacitys[ii]
                                ),
                                "border_width": 1,
                                "text_color": text_colors[ii],
                                "radius": 6,
                            }
                        )
                        self._draw(None, tempcolor)

                    self.after_traced(i * animation_step_time, update)
                self.after_traced(
                    steps * animation_step_time + 10,
                    lambda: self._draw(None, None),
                )
            else:
                if self.attributes.checked:
                    self.attributes.checked = False
                else:
                    self.attributes.checked = True
                self._draw()
