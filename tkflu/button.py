"""按钮组件。

``FluButton`` 是 tkfluent 最基础的交互组件，支持三种样式：

* ``standard`` —— 默认样式，浅色描边；
* ``accent``   —— 强调色填充（跟随 ``set_primary_color``）；
* ``menu``     —— 无边框的菜单项样式。

四种状态（``rest`` / ``hover`` / ``pressed`` / ``disabled``）的配色定义在
:mod:`tkflu.designs.button` 里。"""

from typing import Union

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.button import button


class FluButtonDraw(DSvgDraw):
    """按钮的 SVG 绘制后端。

    图元直接用 :class:`tkdeft.windows.draw.DSvgDraw` 的通用实现
    （``create_roundrect``：几何内缩半个线宽，四边描边都完整），
    因此这里不再重复写一遍。保留这个子类，是给"想给按钮换一套图元"的人
    留的扩展点。
    """


class FluButtonCanvas(DCanvas):
    """按钮的画布。

    ``create_round_rectangle`` / ``create_roundrect`` 直接继承
    :class:`tkdeft.windows.canvas.DCanvas`：它会调用
    :meth:`~tkdeft.windows.canvas.DCanvas.draw_roundrect`，
    当前引擎是 skia / pillow / cairo 时走进程内位图快速路径（不生成 SVG、
    不落盘，相同规格的图片还会被多个按钮共享），否则自动回退到 SVG 路径。
    组件层因此不再需要维护"先试快速路径、失败再回退"的样板代码。
    """

    draw = FluButtonDraw  # 设置svg绘图引擎


from tkinter import Event
from tkinter.font import Font

from ._after import TracedAfter
from .constants import BUTTONSTYLE, MODE, STATE
from .designs.gradient import FluGradient
from .tooltip import FluToolTipBase


class FluButton(FluButtonCanvas, DDrawWidget, FluToolTipBase, FluGradient, TracedAfter):
    def __init__(
        self,
        *args,
        text: Union[str, int, float] = "",
        width: Union[int, float] = 120,
        height: Union[int, float] = 32,
        command: callable = None,
        font: Union[Font, tuple] = None,
        mode: MODE = "light",
        style: BUTTONSTYLE = "standard",
        state: STATE = "normal",
        **kwargs,
    ) -> None:
        """
        按钮组件

        Parameters:
          text: 按钮的标签文本
          width: 默认宽带
          height: 默认高度
          command: 点击时出发的事件
          font: 自定义标签字体
          mode: 按钮深浅主题，参考tkflu.constants.MODE
          style: 按钮样式，参考tkflu.constants.BUTTONSTYLE
          state: 按钮的状态，参考tkflu.constants.STATE
        """
        self._init(mode, style)

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

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.invoke(), add="+")

        self.bind(
            "<Return>", lambda event=None: self.invoke(), add="+"
        )  # 可以使用回车键模拟点击

        from .defs import set_default_font

        set_default_font(font, self.attributes, master=self)

    def _init(self, mode: MODE, style: BUTTONSTYLE):
        """
        初始化按钮，正常情况下无需在程序中调用

        Parameters:
          mode: 按钮深浅主题，参考tkflu.constants.MODE
          style: 按钮样式，参考tkflu.constants.BUTTONSTYLE
        """

        from easydict import EasyDict

        self.enter = False
        self.button1 = False
        #: 先落一份"出厂"的 mode / style。`theme()` 只在参数**为真**时才覆盖它们，
        #: 所以不预置的话，`FluButton(mode=None)` 会在 `theme()` 里撞
        #: `AttributeError: 'FluButton' object has no attribute 'mode'`。
        self.mode = mode or "light"
        self.style = style or "standard"

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "state": "normal",
                "rest": {},
                "hover": {},
                "pressed": {},
                "disabled": {},
            }
        )

        self.theme(mode=mode, style=style)

    def _draw(
        self, event: Union[Event, None] = None, tempcolor: Union[dict, None] = None
    ):
        """

        Parameters:
          绘制按钮
        """
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()
        # 提前定义，反正多次调用浪费资源

        state = self.dcget("state")

        _dict = None

        if not tempcolor:
            if state == "normal":
                if self.enter:
                    if self.button1:
                        _dict = self.attributes.pressed
                    else:
                        _dict = self.attributes.hover
                else:
                    _dict = self.attributes.rest
            else:
                _dict = self.attributes.disabled

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

        if hasattr(self, "element_border"):
            self.delete(self.element_border)

        from .designs.renderer import get_renderer

        if get_renderer() == 1:
            width -= 1
            height -= 1

        self.element_border = self.create_round_rectangle(
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

        if hasattr(self, "element_text"):
            self.itemconfigure(
                self.element_text,
                fill=_text_color,
                text=self.attributes.text,
                font=self.attributes.font,
            )
            self.coords(self.element_text, width / 2, height / 2)
        else:
            self.element_text = self.create_text(
                width / 2,
                height / 2,
                anchor="center",
                fill=_text_color,
                text=self.attributes.text,
                font=self.attributes.font,
            )
        self.tag_raise(self.element_text, self.element_border)

        # 注意：这里曾经调用 render_manager.mark_dirty(self)。
        # _draw 本身就是"把控件画出来"，再把自己标记为脏只会让集中式调度器
        # 在下一轮把同一个控件重画一遍（开着 optimized_rendering 时是纯粹的
        # 双倍开销）。真正的重绘请求应当由事件处理函数发出。

    def theme(self, mode: MODE = None, style: BUTTONSTYLE = None):
        """切换主题 / 样式。

        :param mode: ``"light"`` / ``"dark"``；省略表示沿用当前值
        :param style: ``"standard"`` / ``"accent"`` / ``"menu"``；省略同上

        .. note::
           无法识别的取值会**退回默认值**（``light`` / ``standard``）而不是
           存下来。旧实现直接查表再无条件调用结果，于是：

           * ``theme(style="bogus")`` → ``TypeError: 'NoneType' object is not callable``，
             而且 ``self.style`` 已经变成 ``"bogus"``，**这个按钮从此再也切不了主题**；
           * 只要画廊里有一个这样的按钮，``FluThemeManager.mode()``
             整趟遍历都会崩在那里，后面的兄弟组件全都轮不到换肤。

           同样地，``mode`` / ``style`` 在 :meth:`_init` 里就有了初值，
           ``FluButton(mode=None)`` 不再抛 ``AttributeError``。
        """
        if mode:
            self.mode = mode if str(mode).lower() in ("light", "dark") else "light"
        if style:
            self.style = (
                style
                if str(style).lower() in ("standard", "accent", "menu")
                else "standard"
            )
        theme_handlers = {
            ("light", "accent"): self._light_accent,
            ("light", "menu"): self._light_menu,
            ("light", "standard"): self._light,
            ("dark", "accent"): self._dark_accent,
            ("dark", "menu"): self._dark_menu,
            ("dark", "standard"): self._dark,
        }
        handler = theme_handlers.get(
            (str(self.mode).lower(), str(self.style).lower())
        )
        if handler is None:  # 理论上到不了这里，留一道保险
            handler = self._light
        handler()

    def _theme(
        self,
        mode: MODE,
        style: BUTTONSTYLE,
        animation_steps: int = None,
        animation_step_time: int = None,
    ):
        if animation_steps is None:
            from .designs.animation import get_animation_steps

            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time

            animation_step_time = get_animation_step_time()
        r = button(mode, style, "rest")
        h = button(mode, style, "hover")
        p = button(mode, style, "pressed")
        d = button(mode, style, "disabled")
        if not animation_steps == 0 or not animation_step_time == 0:
            # 撤销上一轮还没跑完的动画帧。用户来回悬停时，上一轮的帧会迟到，
            # 把这一轮刚画好的状态覆盖回去，看起来"悬停了却没反应"。
            self.cancel_traced()
            if self.dcget("state") == "normal":
                if self.enter:
                    if self.button1:
                        now = p
                    else:
                        now = h
                else:
                    now = r
            else:
                now = d
            # print(animation_step_time)
            # print(type(animation_step_time))
            if hasattr(self.attributes.rest, "back_color"):
                back_colors = self.generate_hex2hex(
                    self.attributes.rest.back_color, now["back_color"], animation_steps
                )
                border_colors = self.generate_hex2hex(
                    self.attributes.rest.border_color,
                    now["border_color"],
                    animation_steps,
                )
                if self.attributes.rest.border_color2 is None:
                    self.attributes.rest.border_color2 = (
                        self.attributes.rest.border_color
                    )
                if now["border_color2"] is None:
                    now["border_color2"] = now["border_color"]
                border_colors2 = self.generate_hex2hex(
                    self.attributes.rest.border_color2,
                    now["border_color2"],
                    animation_steps,
                )
                text_colors = self.generate_hex2hex(
                    self.attributes.rest.text_color, now["text_color"], animation_steps
                )
                import numpy as np

                back_opacitys = np.linspace(
                    float(self.attributes.rest.back_opacity),
                    float(now["back_opacity"]),
                    animation_steps,
                ).tolist()
                border_color_opacitys = np.linspace(
                    float(self.attributes.rest.border_color_opacity),
                    float(now["border_color_opacity"]),
                    animation_steps,
                ).tolist()
                if self.attributes.rest.border_color2_opacity is None:
                    self.attributes.rest.border_color2_opacity = (
                        self.attributes.rest.border_color_opacity
                    )
                if now["border_color2_opacity"] is None:
                    now["border_color2_opacity"] = now["border_color_opacity"]
                border_color2_opacitys = np.linspace(
                    float(self.attributes.rest.border_color2_opacity),
                    float(now["border_color2_opacity"]),
                    animation_steps,
                ).tolist()
                for i in range(animation_steps):

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
                                # 线宽与圆角要跟**目标状态**一致，不能写死。
                                # light+accent 的 disabled 状态 border_width 是 0，
                                # 写死 1 会留下一圈目标状态里根本没有的白边。
                                "border_width": now["border_width"],
                                "text_color": text_colors[ii],
                                "radius": now["radius"],
                            }
                        )
                        self._draw(None, tempcolor)

                    self.after_traced(i * animation_step_time, update)
                # 动画的最后一帧永远是"中间态"，必须补一次权威重绘回到
                # 目标状态。旧实现把这一句注释掉了，后果是：
                #   * steps=1 时（np.linspace(0,1,1) 只给出起始色）按钮
                #     会**停留在旧主题**上，直到下一次无关事件才刷新；
                #   * 动画途中鼠标移入/按下时，迟到的旧帧会把 hover/pressed
                #     的绘制覆盖掉，看起来"鼠标悬停却没反应"。
                self.after_traced(
                    animation_steps * animation_step_time + 10,
                    lambda: self._draw(None, None),
                )

        self.dconfigure(
            rest={
                "back_color": r["back_color"],
                "back_opacity": r["back_opacity"],
                "border_color": r["border_color"],
                "border_color_opacity": r["border_color_opacity"],
                "border_color2": r["border_color2"],
                "border_color2_opacity": r["border_color2_opacity"],
                "border_width": r["border_width"],
                "radius": r["radius"],
                "text_color": r["text_color"],
            },
            hover={
                "back_color": h["back_color"],
                "back_opacity": h["back_opacity"],
                "border_color": h["border_color"],
                "border_color_opacity": h["border_color_opacity"],
                "border_color2": h["border_color2"],
                "border_color2_opacity": h["border_color2_opacity"],
                "border_width": h["border_width"],
                "radius": h["radius"],
                "text_color": h["text_color"],
            },
            pressed={
                "back_color": p["back_color"],
                "back_opacity": p["back_opacity"],
                "border_color": p["border_color"],
                "border_color_opacity": p["border_color_opacity"],
                "border_color2": p["border_color2"],
                "border_color2_opacity": p["border_color2_opacity"],
                "border_width": p["border_width"],
                "radius": p["radius"],
                "text_color": p["text_color"],
            },
            disabled={
                "back_color": d["back_color"],
                "back_opacity": d["back_opacity"],
                "border_color": d["border_color"],
                "border_color_opacity": d["border_color_opacity"],
                "border_color2": d["border_color2"],
                "border_color2_opacity": d["border_color2_opacity"],
                "border_width": d["border_width"],
                "radius": d["radius"],
                "text_color": d["text_color"],
            },
        )

    def _light(self):
        self._theme("light", "standard")

    def _light_menu(self):
        self._theme("light", "menu")

    def _light_accent(self):
        self._theme("light", "accent")

    def _dark(self):
        self._theme("dark", "standard")

    def _dark_menu(self):
        self._theme("dark", "menu")

    def _dark_accent(self):
        self._theme("dark", "accent")

    def invoke(self):
        """走一遍"用户点击"的完整流程（禁用状态下什么都不做）。

        .. note::
           旧实现不检查 ``state``，于是 ``disabled`` 的按钮用
           ``invoke()`` 或**回车键**照样会触发 ``command``——鼠标点击却被
           正确挡住，行为不自相矛盾。:class:`FluToggleButton` 一直是有这道
           判断的，这里补齐。
        """
        if self.dcget("state") != "normal":
            return
        self.attributes.command()

    def _event_off_button1(self, event: Event = None):
        self.button1 = False

        self._draw(event)

        if self.enter:
            # self.focus_set()
            if self.dcget("state") == "normal":
                self.event_generate("<<Clicked>>")
