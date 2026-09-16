"""滑块组件。

``FluSlider`` 由两部分绘制而成：

* **轨道**（track）—— 左侧已选中的进度 + 右侧未选中的底轨；
* **把手**（thumb）—— 圆形滑块，带渐变伪阴影。

两者都由 :class:`~tkflu.slider.FluSliderDraw` 生成，
支持横向/纵向、刻度吸附与 ``changed`` 回调。"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.slider import slider


class FluSliderDraw(DSvgDraw):
    """滑块的 SVG 绘制后端。

    两种图元都由 tkdeft 提供，不再在这里重复实现：

    * 进度条槽 → :meth:`tkdeft.windows.draw.DSvgDraw.create_track`
    * 圆形把手 → :meth:`tkdeft.windows.draw.DSvgDraw.create_thumb`
      （外圈是 0.500208→0.954545 的竖直渐变伪阴影 + 外填充 + 内填充）

    保留这个子类，是给"想给滑块换一套图元"的人留的扩展点。
    """


class FluSliderCanvas(DCanvas):
    draw = FluSliderDraw

    def create_track(
        self,
        x1,
        y1,
        width,
        height,
        width2,
        temppath=None,
        temppath2=None,
        radius=3,
        track_fill="transparent",
        track_opacity=1,
        rail_fill="transparent",
        rail_opacity=1,
    ) -> int:
        """画滑块/滚动条的进度条槽。

        :param x1: 左上角 x
        :param y1: 左上角 y
        :param width: 位图宽度
        :param height: 位图高度
        :param width2: 左半段（已选中部分）的宽度
        :param temppath: SVG 兜底路径用的临时文件
        :param temppath2: Wand 引擎的 PNG 输出路径
        :param radius: 圆角半径
        :param track_fill: 已选中部分的颜色
        :param track_opacity: 已选中部分的透明度
        :param rail_fill: 未选中底轨的颜色
        :param rail_opacity: 未选中底轨的透明度
        :returns: 画布上的 item id

        转调 :meth:`tkdeft.windows.canvas.DCanvas.draw_track`：
        栅格引擎走进程内位图快速路径，否则自动回退到 SVG。
        """
        return self.draw_track(
            x1,
            y1,
            width,
            height,
            width2,
            temppath=temppath,
            temppath2=temppath2,
            radius=radius,
            track_fill=track_fill,
            track_opacity=track_opacity,
            rail_fill=rail_fill,
            rail_opacity=rail_opacity,
        )

    def create_thumb(
        self,
        x1,
        y1,
        width,
        height,
        r1,
        r2,
        temppath=None,
        temppath2=None,
        fill="transparent",
        fill_opacity=1,
        outline="transparent",
        outline_opacity=1,
        outline2="transparent",
        outline2_opacity=1,
        inner_fill="transparent",
        inner_fill_opacity=1,
    ) -> int:
        """画滑块的圆形把手。

        :param r1: 外圆半径（伪阴影那一圈）
        :param r2: 内圆半径
        :param fill: 外填充色
        :param outline: 伪阴影渐变的第一个颜色
        :param outline2: 伪阴影渐变的第二个颜色
        :param inner_fill: 内圆填充色
        :returns: 画布上的 item id

        转调 :meth:`tkdeft.windows.canvas.DCanvas.draw_thumb`：
        栅格引擎走进程内位图快速路径，否则自动回退到 SVG。
        """
        return self.draw_thumb(
            x1,
            y1,
            width,
            height,
            r1,
            r2,
            temppath=temppath,
            temppath2=temppath2,
            fill=fill,
            fill_opacity=fill_opacity,
            outline=outline,
            outline_opacity=outline_opacity,
            outline2=outline2,
            outline2_opacity=outline2_opacity,
            inner_fill=inner_fill,
            inner_fill_opacity=inner_fill_opacity,
        )


class FluSlider(FluSliderCanvas, DDrawWidget):
    def __init__(
        self,
        *args,
        text="",
        width=70,
        height=28,
        orient="horizontal",
        tick=False,  # 自动吸附
        font=None,
        mode="light",
        state="normal",
        value=20,
        max=100,
        min=0,
        changed=None,
        **kwargs,
    ):
        """

        初始化类

        :param args: 参照tkinter.Canvas.__init__
        :param text:
        :param width:
        :param height:
        :param font:
        :param mode: Fluent主题模式 分为 “light” “dark”
        :param style:
        :param kwargs: 参照tkinter.Canvas.__init__
        """

        self._init(mode)

        self.dconfigure(
            state=state,
            value=value,
            max=max,
            min=min,
            orient=orient,
            tick=tick,
            changed=changed,
        )

        super().__init__(*args, width=width, height=height, **kwargs)

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")

        # self.bind("<Left>", lambda event:print("asd1"))

        self.bind("<B1-Motion>", self._event_button1_motion)

        self.enter_thumb = False

        from .defs import set_default_font

        set_default_font(font, self.attributes)

    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "command": None,
                "state": None,
                "orient": "horizontal",
                "tick": False,
                "changed": None,
                "value": 20,
                "max": 100,
                "min": 0,
                "rest": {},
                "hover": {},
                "pressed": {},
                "disabled": {},
            }
        )

        self.theme(mode)

    def _draw(self, event=None):
        """
        重新绘制组件

        :param event:
        """

        super()._draw(event)

        # print("width:", self.winfo_width(), "\n", "height:", self.winfo_height(), sep="")

        # print("")

        if hasattr(self, "_e1"):
            self.tag_unbind(self.element_track, "<Enter>", self._e1)
        if hasattr(self, "_e2"):
            self.tag_unbind(self.element_track, "<Leave>", self._e2)

        self.delete("all")

        state = self.dcget("state")

        _dict = None

        if state == "normal":
            if event:
                if self.enter:  # 先检查是否在组件内
                    if self.enter_thumb:  # 再检查是否在滑块上
                        if self.button1:
                            _dict = self.attributes.pressed
                        else:
                            _dict = self.attributes.hover
                    else:
                        _dict = self.attributes.hover  # 在组件内但不在滑块上
                else:
                    _dict = self.attributes.rest  # 不在组件内
            else:
                _dict = self.attributes.rest
        else:
            _dict = self.attributes.disabled

        _radius = _dict.radius

        _track_height = _dict.track.width
        _track_back_color = _dict.track.back_color
        _track_back_opacity = _dict.track.back_opacity

        _rail_back_color = _dict.rail.back_color
        _rail_back_opacity = _dict.rail.back_opacity

        _thumb_radius = _dict.thumb.radius
        _thumb_inner_radius = _dict.thumb.inner_radius

        _thumb_width = _dict.thumb.width

        _thumb_back_color = _dict.thumb.back_color
        _thumb_back_opacity = _dict.thumb.back_opacity

        _thumb_border_color = _dict.thumb.border_color
        _thumb_border_color_opacity = _dict.thumb.border_color_opacity

        _thumb_border_color2 = _dict.thumb.border_color2
        _thumb_border_color2_opacity = _dict.thumb.border_color2_opacity

        _thumb_inner_back_color = _dict.thumb.inner_back_color
        _thumb_inner_back_opacity = _dict.thumb.inner_back_opacity

        if self.attributes.orient == "horizontal":
            thumb_xp = self.attributes.value / (
                self.attributes.max - self.attributes.min
            )  # 滑块对应数值的比例
            thumb_x = self.winfo_width() * thumb_xp  # 滑块对应数值的x左边

            width = self.winfo_width()
            height = self.winfo_height()
            # 修改滑块位置计算
            thumb_width = _thumb_width
            min_x = thumb_width / 2
            max_x = self.winfo_width() - thumb_width / 2
            track_length = max_x - min_x

            # 计算轨道实际可用宽度（减去滑块宽度）
            effective_track_width = self.winfo_width() - thumb_width

            thumb_xp = (self.attributes.value - self.attributes.min) / (
                self.attributes.max - self.attributes.min
            )
            thumb_center = thumb_width / 2 + thumb_xp * effective_track_width

            thumb_width = _thumb_width
            effective_width = self.winfo_width() - thumb_width
            ratio = (self.attributes.value - self.attributes.min) / (
                self.attributes.max - self.attributes.min
            )
            thumb_left = thumb_width / 2 + ratio * effective_width - thumb_width / 2

            # 确保不会超出右边界
            thumb_left = min(thumb_left, self.winfo_width() - thumb_width)
            from .designs.renderer import get_renderer

            if get_renderer() != 1:
                # 默认几何（tksvg 以及 skia / pillow / cairo 等栅格引擎）
                # 注意：这里必须是 != 1 而不是 == 0，否则新增的栅格引擎编号
                # 会落进"两个分支都不匹配"的空档，导致轨道与把手根本不被创建，
                # 随后 tag_bind 直接抛 AttributeError。
                # 创建轨道时，width2 参数应为选中部分的宽度（滑块中心位置）
                self.element_track = self.create_track(
                    _thumb_width / 4,
                    height / 2 - _track_height,
                    self.winfo_width() - _thumb_width / 2,
                    _track_height,
                    thumb_center
                    - _thumb_width / 4,  # 关键修正：使用滑块中心相对于轨道起点的距离
                    temppath=self.temppath,
                    temppath2=self.temppath3,
                    radius=_radius,
                    track_fill=_track_back_color,
                    track_opacity=_track_back_opacity,
                    rail_fill=_rail_back_color,
                    rail_opacity=_rail_back_opacity,
                )

                self.element_thumb = self.create_thumb(
                    thumb_left,
                    0,  # 直接使用计算出的左上角位置
                    thumb_width,
                    thumb_width,
                    _thumb_radius,
                    _thumb_inner_radius,
                    temppath=self.temppath2,
                    temppath2=self.temppath4,
                    fill=_thumb_back_color,
                    fill_opacity=_thumb_back_opacity,
                    outline=_thumb_border_color,
                    outline_opacity=_thumb_border_color_opacity,
                    outline2=_thumb_border_color2,
                    outline2_opacity=_thumb_border_color2_opacity,
                    inner_fill=_thumb_inner_back_color,
                    inner_fill_opacity=_thumb_inner_back_opacity,
                )
            elif get_renderer() == 1:
                # 创建轨道时，width2 参数应为选中部分的宽度（滑块中心位置）
                self.element_track = self.create_track(
                    _thumb_width / 4,
                    height / 2 - _track_height,
                    self.winfo_width() - _thumb_width / 2 - 1,
                    _track_height - 1,
                    thumb_center
                    - _thumb_width / 4,  # 关键修正：使用滑块中心相对于轨道起点的距离
                    temppath=self.temppath,
                    temppath2=self.temppath3,
                    radius=_radius,
                    track_fill=_track_back_color,
                    track_opacity=_track_back_opacity,
                    rail_fill=_rail_back_color,
                    rail_opacity=_rail_back_opacity,
                )

                self.element_thumb = self.create_thumb(
                    thumb_left,
                    0,  # 直接使用计算出的左上角位置
                    thumb_width - 3.5,
                    thumb_width - 3.5,
                    _thumb_radius,
                    _thumb_inner_radius,
                    temppath=self.temppath2,
                    temppath2=self.temppath4,
                    fill=_thumb_back_color,
                    fill_opacity=_thumb_back_opacity,
                    outline=_thumb_border_color,
                    outline_opacity=_thumb_border_color_opacity,
                    outline2=_thumb_border_color2,
                    outline2_opacity=_thumb_border_color2_opacity,
                    inner_fill=_thumb_inner_back_color,
                    inner_fill_opacity=_thumb_inner_back_opacity,
                )

        self._e1 = self.tag_bind(
            self.element_thumb, "<Enter>", self._event_enter_thumb, add="+"
        )
        self._e2 = self.tag_bind(
            self.element_thumb, "<Leave>", self._event_leave_thumb, add="+"
        )

    def pos(self, event):
        """按鼠标位置更新滑块的值（并重绘）。

        :param event: 鼠标事件；**缺失时直接返回**——``_event_on_button1()``
            这类钩子的签名是 ``event=None``，程序化调用（例如 ``python -m tkflu
            --check`` 的自检）不会带事件，这里不能去读 ``event.x``。
        """
        if event is None:
            return
        if self.attributes.state == "normal":
            # print(event.x, event.y)
            # if self.enter and self.button1:
            # 获取滑块宽度
            thumb_width = self.attributes.pressed.thumb.width

            # 计算有效轨道长度
            effective_width = self.winfo_width() - thumb_width

            # 计算滑块位置比例（考虑滑块宽度边界）
            ratio = (event.x - thumb_width / 2) / effective_width
            ratio = max(0, min(1, ratio))  # 限制在0-1范围内

            # 计算实际值
            value = self.attributes.min + ratio * (
                self.attributes.max - self.attributes.min
            )
            if self.attributes.tick:
                value = round(value)
            self.dconfigure(value=value)
            self._draw()
            # print(self.focus_get())

    def _event_off_button1(self, event=None):
        if self.attributes.state == "normal":
            if self.attributes.changed:
                self.attributes.changed()

    def _event_enter_thumb(self, event=None):
        self.enter_thumb = True
        self.update()

    def _event_leave_thumb(self, event=None):
        self.enter_thumb = False

    def _event_button1_motion(self, event):
        self.pos(event)

    def _event_on_button1(self, event=None):
        super()._event_on_button1(event=event)
        self.pos(event)

    def theme(self, mode=None):
        if mode:
            self.mode = mode
        if self.mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _theme(self, mode):
        r = slider(mode, "rest")
        h = slider(mode, "hover")
        p = slider(mode, "pressed")
        d = slider(mode, "disabled")
        self.dconfigure(
            rest={
                "radius": r["radius"],
                "thumb": {
                    "radius": r["thumb"]["radius"],
                    "inner_radius": r["thumb"]["inner_radius"],
                    "width": r["thumb"]["width"],
                    "back_color": r["thumb"]["back_color"],
                    "back_opacity": r["thumb"]["back_opacity"],
                    "border_color": r["thumb"]["border_color"],
                    "border_color_opacity": r["thumb"]["border_color_opacity"],
                    "border_color2": r["thumb"]["border_color2"],
                    "border_color2_opacity": r["thumb"]["border_color2_opacity"],
                    "inner_back_color": r["thumb"]["inner_back_color"],
                    "inner_back_opacity": r["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": r["track"]["back_color"],
                    "back_opacity": r["track"]["back_opacity"],
                    "width": r["track"]["width"],
                },
                "rail": {
                    "back_color": r["rail"]["back_color"],
                    "back_opacity": r["rail"]["back_opacity"],
                },
            },
            hover={
                "radius": h["radius"],
                "thumb": {
                    "radius": h["thumb"]["radius"],
                    "inner_radius": h["thumb"]["inner_radius"],
                    "width": r["thumb"]["width"],
                    "back_color": h["thumb"]["back_color"],
                    "back_opacity": h["thumb"]["back_opacity"],
                    "border_color": h["thumb"]["border_color"],
                    "border_color_opacity": h["thumb"]["border_color_opacity"],
                    "border_color2": h["thumb"]["border_color2"],
                    "border_color2_opacity": h["thumb"]["border_color2_opacity"],
                    "inner_back_color": h["thumb"]["inner_back_color"],
                    "inner_back_opacity": h["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": h["track"]["back_color"],
                    "back_opacity": h["track"]["back_opacity"],
                    "width": h["track"]["width"],
                },
                "rail": {
                    "back_color": h["rail"]["back_color"],
                    "back_opacity": h["rail"]["back_opacity"],
                },
            },
            pressed={
                "radius": p["radius"],
                "thumb": {
                    "radius": p["thumb"]["radius"],
                    "inner_radius": p["thumb"]["inner_radius"],
                    "width": r["thumb"]["width"],
                    "back_color": p["thumb"]["back_color"],
                    "back_opacity": p["thumb"]["back_opacity"],
                    "border_color": p["thumb"]["border_color"],
                    "border_color_opacity": p["thumb"]["border_color_opacity"],
                    "border_color2": p["thumb"]["border_color2"],
                    "border_color2_opacity": p["thumb"]["border_color2_opacity"],
                    "inner_back_color": p["thumb"]["inner_back_color"],
                    "inner_back_opacity": p["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": p["track"]["back_color"],
                    "back_opacity": p["track"]["back_opacity"],
                    "width": p["track"]["width"],
                },
                "rail": {
                    "back_color": p["rail"]["back_color"],
                    "back_opacity": p["rail"]["back_opacity"],
                },
            },
            disabled={
                "radius": d["radius"],
                "thumb": {
                    "radius": d["thumb"]["radius"],
                    "inner_radius": d["thumb"]["inner_radius"],
                    "width": r["thumb"]["width"],
                    "back_color": d["thumb"]["back_color"],
                    "back_opacity": d["thumb"]["back_opacity"],
                    "border_color": d["thumb"]["border_color"],
                    "border_color_opacity": d["thumb"]["border_color_opacity"],
                    "border_color2": d["thumb"]["border_color2"],
                    "border_color2_opacity": d["thumb"]["border_color2_opacity"],
                    "inner_back_color": d["thumb"]["inner_back_color"],
                    "inner_back_opacity": d["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": d["track"]["back_color"],
                    "back_opacity": d["track"]["back_opacity"],
                    "width": d["track"]["width"],
                },
                "rail": {
                    "back_color": d["rail"]["back_color"],
                    "back_opacity": d["rail"]["back_opacity"],
                },
            },
        )

    def _light(self):
        self._theme("light")

    def _dark(self):
        self._theme("dark")
