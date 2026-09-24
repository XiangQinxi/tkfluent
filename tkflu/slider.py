"""滑块组件。

``FluSlider`` 由两部分绘制而成：

* **轨道**（track）—— 左侧已选中的进度 + 右侧未选中的底轨；
* **把手**（thumb）—— 圆形滑块，带渐变伪阴影。

两者都由 :class:`~tkflu.slider.FluSliderDraw` 生成，
支持横向/纵向、刻度吸附与 ``changed`` 回调。

.. code-block:: python

    import tkflu

    root = tkflu.FluWindow()
    slider = tkflu.FluSlider(root, width=240, min=0, max=100, value=40)
    slider.pack(padx=16, pady=16)

    slider.changed = lambda value: print("值变成", value)   # 或构造时传 changed=
    root.mainloop()

取值与坐标
----------
* ``value`` 会被**夹到** ``[min, max]`` 区间里；``min`` 与 ``max`` 写反了也能
  正常工作（内部会自行排序）；
* 横向滑块**左端是最小值**；纵向滑块**上端是最小值**（与 tkinter 原生
  ``Scale`` 的默认方向一致），最大值都在另一端；
* ``pos(event)`` 只对横向滑块用 ``event.x``，纵向用 ``event.y``。

回调
----
* ``changed(value)`` / ``command(value)`` —— 鼠标松开时若值确实变了才触发；
  只写 ``lambda: ...`` 也照样可用（见 :func:`tkflu.defs.call_command`）。
* 键盘：``←/→``（横向）或 ``↑/↓``（纵向）调整 ``step``，
  ``Home`` / ``End`` 直达两端。
"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.slider import slider

#: 支持的方向
ORIENTS = ("horizontal", "vertical")


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
        step=1,
        changed=None,
        command=None,
        **kwargs,
    ):
        """构造滑块。

        :param args: 透传给 :class:`tkinter.Canvas.__init__`
        :param width: 默认宽度
        :param height: 默认高度
        :param orient: ``"horizontal"`` / ``"vertical"``
        :param tick: 是否把取值吸附到整数
        :param font: 预留的字体参数（滑块当前不绘制文字）
        :param mode: ``"light"`` / ``"dark"``
        :param state: ``"normal"`` / ``"disabled"``
        :param value: 初始值（会被夹到 ``[min, max]``）
        :param max: 最大值
        :param min: 最小值
        :param step: 键盘方向键每次调整的幅度
        :param changed: 值变化回调，尽量以 ``(value,)`` 调用
        :param command: ``changed`` 的同义参数（Tk ``Scale`` 的叫法）
        :param kwargs: 其余参数透传给 :class:`tkinter.Canvas.__init__`

        :raises ValueError: ``orient`` 无法识别

        .. note::
           历史上 ``command`` 只写在属性表里、构造函数并不接收它，
           于是 ``FluSlider(command=cb)`` 会把 ``-command`` 透给
           :class:`tkinter.Canvas` 并抛 ``TclError: unknown option "-command"``。
           现在两个名字都接受。
        """
        if str(orient).lower() not in ORIENTS:
            raise ValueError(f"未知的方向 {orient!r}；应为 {list(ORIENTS)} 之一")

        self._init(mode)

        self.dconfigure(
            state=state or "normal",
            value=value,
            max=max,
            min=min,
            orient=str(orient).lower(),
            tick=tick,
            step=step,
            changed=changed,
            command=command,
        )
        # 初始值也要夹进区间：`_ratio()` 画图时会夹，但属性里留着 200
        # 这种越界值会让 `get()` 与画面对不上（也会顺着 changed 回调传出去）。
        self.attributes.value = self._clamp_value(value)

        # 这些状态位必须在 super().__init__() 之前就位：基类的构造函数里
        # 会立刻调用一次 self._draw()，而 _draw 会读它们。
        self.enter_thumb = False
        #: 上一次排队的"拖动重绘" after id（用于合并连发的 <B1-Motion>）
        self._motion_after = None
        #: 按下瞬间的值，用于判断松开时要不要触发回调
        self._value_on_press = None
        #: 本帧把手的位置（命中测试用）
        self._thumb_box = None
        #: 已渲染把手对应的"样式键"，一样就只挪位置、不重新渲染
        self._thumb_key = None

        super().__init__(*args, width=width, height=height, **kwargs)

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<B1-Motion>", self._event_button1_motion, add="+")
        self.bind("<Motion>", self._event_motion, add="+")
        self.configure(takefocus=1)

        horizontal = self.attributes.orient == "horizontal"
        self.bind(
            "<Right>" if horizontal else "<Down>",
            lambda event=None: self.step_by(+1),
            add="+",
        )
        self.bind(
            "<Left>" if horizontal else "<Up>",
            lambda event=None: self.step_by(-1),
            add="+",
        )
        self.bind("<Home>", lambda event=None: self.set(self.attributes.min), add="+")
        self.bind("<End>", lambda event=None: self.set(self.attributes.max), add="+")

        from .defs import set_default_font

        set_default_font(font, self.attributes, master=self)

    # ------------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------------
    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "command": None,
                "state": "normal",
                "orient": "horizontal",
                "tick": False,
                "step": 1,
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

    # ------------------------------------------------------------------
    # 取值
    # ------------------------------------------------------------------
    def _range(self):
        """返回排好序的 ``(最小值, 最大值)``。

        ``min`` / ``max`` 写反了也照样能用——直接对调，而不是画出反的滑块。
        """
        low = float(self.attributes.min)
        high = float(self.attributes.max)
        return (low, high) if low <= high else (high, low)

    def _clamp_value(self, value):
        """把取值夹进区间（``tick`` 打开时顺带吸附到整数）。"""
        low, high = self._range()
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = low
        if self.attributes.tick:
            number = round(number)
        return max(low, min(high, number))

    def _ratio(self):
        """当前值在区间里的比例（``0``–``1``）。"""
        low, high = self._range()
        span = high - low
        if span <= 0:
            return 0.0
        return (self._clamp_value(self.attributes.value) - low) / span

    def get(self):
        """取当前值（保证落在 ``[min, max]`` 之内）。"""
        return self._clamp_value(self.attributes.value)

    def set(self, value, redraw: bool = True, notify: bool = False):
        """设置当前值（自动夹到区间内）。

        :param value: 新值
        :param redraw: 是否立即重绘，默认 ``True``
        :param notify: 是否触发 ``changed`` / ``command``，默认 ``False``
        :returns: 值是否真的改变了
        """
        clamped = self._clamp_value(value)
        changed = self._value_differs(clamped, self.attributes.value)
        self.attributes.value = clamped
        if redraw:
            self._draw()
        if notify and changed:
            self._emit_changed()
        return changed

    def step_by(self, direction: int):
        """按 ``step`` 调整值（键盘方向键用）。

        :param direction: ``+1`` 增大、``-1`` 减小
        """
        if self.attributes.state == "disabled":
            return
        try:
            step = abs(float(self.attributes.step)) or 1.0
        except (TypeError, ValueError):
            step = 1.0
        if self.set(self.attributes.value + direction * step, notify=True):
            self.focus_set()

    def _value_differs(self, a, b):
        """两个取值是否不同（容忍 int/float 混用与非法值）。"""
        try:
            return float(a) != float(b)
        except (TypeError, ValueError):
            return a is not b

    def _emit_changed(self):
        """触发 ``changed`` / ``command``（两个名字等价）。"""
        from .defs import call_command

        call_command(self.attributes.changed, self.attributes.value)
        call_command(self.attributes.command, self.attributes.value)

    # ------------------------------------------------------------------
    # 配色
    # ------------------------------------------------------------------
    def _palette(self):
        """按当前交互状态挑一组配色。

        .. note::
           旧实现写成 ``if event:`` —— 只有"带事件的调用"才会进入
           hover/pressed 分支，而拖动路径最后调的是不带事件的 ``_draw()``，
           于是**拖动手感永远是 rest**（把手不会变大、内圆也不会缩）。
           这里改成只看状态位 ``button1`` / ``enter``，与事件无关。
        """
        if self.attributes.state != "normal":
            return "disabled", self.attributes.disabled
        if self.button1:
            return "pressed", self.attributes.pressed
        if self.enter:
            return "hover", self.attributes.hover
        return "rest", self.attributes.rest

    def _draw(self, event=None):
        """重新绘制组件。"""
        super()._draw(event)

        self.delete("track")

        state_name, _dict = self._palette()

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

        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return  # 布局还没完成，画出来只会更难看的

        from .designs.renderer import get_renderer

        is_wand = get_renderer() == 1

        ratio = self._ratio()
        center_x, center_y, progress = self._thumb_geometry(width, height, _thumb_width, ratio)

        self._draw_track(
            width,
            height,
            progress,
            _thumb_width,
            _track_height,
            _radius,
            _track_back_color,
            _track_back_opacity,
            _rail_back_color,
            _rail_back_opacity,
            is_wand,
        )

        self._draw_thumb(
            center_x,
            center_y,
            _thumb_width,
            _thumb_radius,
            _thumb_inner_radius,
            _thumb_back_color,
            _thumb_back_opacity,
            _thumb_border_color,
            _thumb_border_color_opacity,
            _thumb_border_color2,
            _thumb_border_color2_opacity,
            _thumb_inner_back_color,
            _thumb_inner_back_opacity,
            state_name,
            is_wand,
        )

    # ------------------------------------------------------------------
    # 几何
    # ------------------------------------------------------------------
    def _thumb_geometry(self, width, height, thumb_size, ratio):
        """算出把手的**中心点**与"进度终点"。

        :returns: ``(center_x, center_y, progress)``，``progress`` 是进度条
            应当画到的位置（横向是 x，纵向是 y）
        """
        if self.attributes.orient == "vertical":
            span = max(1.0, height - thumb_size)
            progress = thumb_size / 2 + ratio * span
            return width / 2, progress, progress

        span = max(1.0, width - thumb_size)
        progress = thumb_size / 2 + ratio * span
        return progress, height / 2, progress

    def _thumb_render_size(self):
        """把手位图的**实际**像素尺寸。

        SVG 引擎（tksvg / wand）会按内容的包围盒出图：一个"28px 的圆"实际
        只有 24px（圆心在 14、半径 12）。若仍按 28 去摆放，把手就会偏左
        2px，与鼠标位置对不上。栅格引擎返回的正是请求的尺寸。

        这里量一次、记住，之后按真实尺寸居中。
        """
        item = getattr(self, "element_thumb", None)
        photo = self._photo_refs.get(item) if item is not None else None
        if photo is None:
            return None
        try:
            return (photo.width(), photo.height())
        except Exception:
            return None

    def _draw_track(
        self,
        width,
        height,
        center,
        thumb_size,
        track_height,
        radius,
        track_color,
        track_opacity,
        rail_color,
        rail_opacity,
        is_wand,
    ):
        """画进度条槽。"""
        if self.attributes.orient == "vertical":
            # tkdeft 的 create_track 只会画横向的槽，纵向用两个圆角矩形拼：
            # 上段是已选中部分，下段是底轨。这样五个引擎的画面完全一致。
            thickness = track_height
            x = width / 2 - thickness / 2
            y1 = thumb_size / 4
            y2 = height - thumb_size / 2
            split = min(max(center, y1), y2)
            self.element_rail = self.draw_roundrect(
                x,
                y1,
                x + thickness,
                y2,
                radius,
                temppath=self.temppath,
                temppath2=self.temppath3,
                fill=rail_color,
                fill_opacity=rail_opacity,
                outline=None,
                outline_opacity=0.0,
                width=0,
            )
            self.element_track = self.draw_roundrect(
                x,
                y1,
                x + thickness,
                max(split, y1 + thickness),
                radius,
                temppath=self.temppath2,
                temppath2=self.temppath4,
                fill=track_color,
                fill_opacity=track_opacity,
                outline=None,
                outline_opacity=0.0,
                width=0,
            )
            return

        track_x1 = thumb_size / 4
        track_x2 = width - thumb_size / 2
        track_y = height / 2 - track_height / 2
        if is_wand:
            # wand 引擎在位图边缘会多算一个像素，历史组件都按这个约定补偿
            track_x2 -= 0.5
            track_height = max(1, track_height - 1)
        track_length = max(1.0, track_x2 - track_x1)
        filled = min(max(center - thumb_size / 4, 0.0), track_length)

        self.element_track = self.create_track(
            track_x1,
            track_y,
            track_x2,
            track_height,
            filled,
            temppath=self.temppath,
            temppath2=self.temppath3,
            radius=radius,
            track_fill=track_color,
            track_opacity=track_opacity,
            rail_fill=rail_color,
            rail_opacity=rail_opacity,
        )

    def _draw_thumb(
        self,
        center_x,
        center_y,
        thumb_size,
        r1,
        r2,
        fill,
        fill_opacity,
        border,
        border_opacity,
        border2,
        border2_opacity,
        inner_fill,
        inner_opacity,
        state_name,
        is_wand,
    ):
        """画圆形把手。

        把手位图只跟**样式与尺寸**有关，与位置无关。拖动时位置一直在变、
        样式却不变，所以这里记下"样式键"：键没变就只把已有图元挪过去
        （``coords``，实测 0.01ms），不再走一遍"生成 SVG → 解析 → 出图"
        （默认 tksvg 下约 8ms）。

        位置按**位图真实尺寸**居中：SVG 引擎出的是内容包围盒（28px 的圆
        实际 24px），按请求尺寸摆放会整体偏 2px。
        """
        size = thumb_size - 3.5 if is_wand else thumb_size
        key = (
            state_name,
            round(size, 2),
            r1,
            r2,
            fill,
            fill_opacity,
            border,
            border_opacity,
            border2,
            border2_opacity,
            inner_fill,
            inner_opacity,
        )

        existing = getattr(self, "element_thumb", None)
        if existing is not None and self._thumb_key == key:
            actual = self._thumb_render_size()
            if actual is not None:
                self._place_thumb(existing, center_x, center_y, actual)
                return

        self.delete("thumb")
        self.element_thumb = self.create_thumb(
            center_x - size / 2,
            center_y - size / 2,
            size,
            size,
            r1,
            r2,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill=fill,
            fill_opacity=fill_opacity,
            outline=border,
            outline_opacity=border_opacity,
            outline2=border2,
            outline2_opacity=border2_opacity,
            inner_fill=inner_fill,
            inner_fill_opacity=inner_opacity,
        )
        try:
            self.itemconfigure(self.element_thumb, tags="thumb")
        except Exception:
            pass
        self._thumb_key = key

        actual = self._thumb_render_size() or (size, size)
        self._place_thumb(self.element_thumb, center_x, center_y, actual)

    def _place_thumb(self, item, center_x, center_y, size):
        """把把手挪到以 ``(center_x, center_y)`` 为中心的位置，并记录命中框。"""
        width, height = size
        left = center_x - width / 2.0
        top = center_y - height / 2.0
        try:
            self.coords(item, left, top)
        except Exception:
            return
        self._thumb_box = (left, top, left + width, top + height)
        self.tag_raise(item)

    # ------------------------------------------------------------------
    # 交互
    # ------------------------------------------------------------------
    def pos(self, event):
        """按鼠标位置更新滑块的值（并重绘）。

        :param event: 鼠标事件；**缺失时直接返回**——``_event_on_button1()``
            这类钩子的签名是 ``event=None``，程序化调用（例如 ``python -m tkflu
            --check`` 的自检）不会带事件，这里不能去读 ``event.x``。
        """
        if event is None:
            return
        if self.attributes.state != "normal":
            return

        thumb_size = self.attributes.pressed.thumb.width
        if self.attributes.orient == "vertical":
            position = event.y
            extent = self.winfo_height()
        else:
            position = event.x
            extent = self.winfo_width()

        # 分母必须至少是 1：滑块比把手还窄时 (extent - thumb_size) 是负数，
        # 比例会整体反号，往右拖反而变小。
        span = max(1.0, extent - thumb_size)
        ratio = (position - thumb_size / 2) / span
        ratio = max(0.0, min(1.0, ratio))

        low, high = self._range()
        self.set(low + ratio * (high - low), redraw=True)

    def _event_on_button1(self, event=None):
        if self.attributes.state != "normal":
            return
        self.focus_set()
        self._value_on_press = self.attributes.value
        super()._event_on_button1(event=event)
        self.pos(event)

    def _event_off_button1(self, event=None):
        # 只有"值真的变了"才回调：原地按一下不该触发 changed
        if self._value_on_press is not None and self._value_differs(
            self.attributes.value, self._value_on_press
        ):
            self._emit_changed()
        self._value_on_press = None
        super()._event_off_button1(event=event)

    def _event_button1_motion(self, event):
        """拖动：合并连发的移动事件，一个空闲周期只重绘一次。

        每次重绘都要重新渲染轨道（默认 tksvg 下约 8ms），鼠标快速划过时
        一次拖动能堆出上百个 ``<B1-Motion>``；不合并的话界面会明显发滞。
        """
        if event is None:
            return
        self._pending_motion = event
        if self._motion_after is None:
            self._motion_after = self.after_idle(self._flush_motion)

    def _flush_motion(self):
        """把攒下来的最后一次移动事件真正应用掉。"""
        self._motion_after = None
        event = getattr(self, "_pending_motion", None)
        self._pending_motion = None
        if event is None:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        self.pos(event)

    def _event_motion(self, event=None):
        """鼠标移动：判断是否悬停在把手上（只有状态变了才重绘）。

        旧实现用 ``tag_bind`` 绑在把手图元上，但取消绑定那行绑错了对象
        （``tag_unbind(self.element_track, ...)``），而且拖动时把手会被整体
        重画，绑定关系并不牢靠。这里改成按几何判定，不依赖图元绑定。
        """
        inside = self._point_in_thumb(event)
        if inside != self.enter_thumb:
            self.enter_thumb = inside
            self._draw()

    def _point_in_thumb(self, event):
        """坐标是否落在把手上。"""
        box = getattr(self, "_thumb_box", None)
        if box is None or event is None:
            return False
        return box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]

    def _event_leave(self, event=None):
        """鼠标离开 → 清掉"悬停在把手上"的标记。"""
        self.enter_thumb = False
        super()._event_leave(event)

    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------
    def theme(self, mode=None, style=None):
        """切换主题。

        :param mode: ``"light"`` / ``"dark"``；省略或传空表示沿用当前值
        :param style: 滑块没有样式之分，接受但忽略（与其它组件签名保持一致）
        """
        # `self.mode` 在 `_init` 里还不存在（theme 就是在那里被调用的），
        # 所以这里必须用 getattr 兜底，否则 FluSlider(mode="") 会抛
        # AttributeError: 'FluSlider' object has no attribute 'mode'。
        resolved = mode or getattr(self, "mode", None) or "light"
        self.mode = resolved
        if str(resolved).lower() == "dark":
            self._dark()
        else:
            self._light()
        self._thumb_key = None  # 配色变了，把手必须重渲染

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
