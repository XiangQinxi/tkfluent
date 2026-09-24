"""轻量导航栏组件。

``FluLiteNav`` 是一个"一排可点条目 + 一个选中项"的导航控件，对应 Windows 的
``NavigationView`` 里最常用的那部分：条目、悬停、选中指示条、切换回调。
它刻意做得很轻——没有页面容器、没有折叠按钮、没有标题栏，就是一个导航条。

.. code-block:: python

    import tkflu

    root = tkflu.FluWindow()
    nav = tkflu.FluLiteNav(
        root,
        items=[
            ("🏠", "首页"),
            ("🔍", "搜索"),
            ("⚙", "设置"),
        ],
        orient="vertical",
    )
    nav.pack(side="left", fill="y", padx=8, pady=8)
    nav.dconfigure(command=lambda index, item: print("切到", item["label"]))
    root.mainloop()

条目的写法
----------
``items`` 里每一项可以是三种形式，混用也没问题：

============================ ==================================================
写法                          含义
============================ ==================================================
``"首页"``                    只有标签
``("🏠", "首页")``            图标 + 标签
``{"label": "首页", ...}``    完整字典，可带 ``icon`` / ``key`` / ``enabled``
============================ ==================================================

字典形式额外支持 ``key``（给 :meth:`FluLiteNav.select` 用的稳定标识）和
``enabled``（单项禁用）。

回调
----
``command`` 在**选中项发生变化**时触发，尽量以 ``(index, item)`` 调用；
条目字典里的 ``"command"`` 优先于控件级 ``command``（适合"这一项要多做点事"）。
只写 ``lambda: ...`` 的老写法照样能用，见 :func:`tkflu.defs.call_command`。
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Union

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .constants import MODE
from .designs.litenav import STYLES
from .designs.litenav import litenav as litenav_design

__all__ = ["FluLiteNav", "FluLiteNavCanvas", "FluLiteNavDraw"]

#: 支持的方向
ORIENTS = ("vertical", "horizontal")


class FluLiteNavDraw(DSvgDraw):
    """导航栏的 SVG 绘制后端（图元全部走通用实现）。"""


class FluLiteNavCanvas(DCanvas):
    """导航栏的画布。"""

    draw = FluLiteNavDraw


from tkinter import Event  # noqa: E402

from .defs import call_command, measure_label_width, set_default_font  # noqa: E402
from .theme_transition import blend_theme_design  # noqa: E402
from .tooltip import FluToolTipBase  # noqa: E402


def _normalize_item(spec) -> Dict:
    """把 ``items`` 里的任意一种写法归一成条目字典。

    :param spec: ``str`` / ``(icon, label)`` / ``dict``
    :returns: 含 ``label`` / ``icon`` / ``key`` / ``enabled`` / ``command`` 的字典
    :raises TypeError: 写法无法识别
    """
    if isinstance(spec, dict):
        return {
            "label": str(spec.get("label", "")),
            "icon": spec.get("icon"),
            "key": spec.get("key", spec.get("label", "")),
            "enabled": bool(spec.get("enabled", True)),
            "command": spec.get("command"),
        }

    if isinstance(spec, (tuple, list)):
        if len(spec) == 1:
            return _normalize_item(spec[0])
        if len(spec) == 2:
            icon, label = spec
            return {
                "label": str(label),
                "icon": None if icon is None else str(icon),
                "key": str(label),
                "enabled": True,
                "command": None,
            }
        raise TypeError(f"导航条目最多两元（图标, 标签），收到 {spec!r}")

    return {
        "label": str(spec),
        "icon": None,
        "key": str(spec),
        "enabled": True,
        "command": None,
    }


class FluLiteNav(FluLiteNavCanvas, DDrawWidget, FluToolTipBase):
    """轻量导航栏。

    :cvar ITEM_HEIGHT: 条目高度（竖直方向是行高，水平方向是控件高度）
    :cvar PADDING_X: 条目内左右留白
    :cvar GAP: 图标与标签之间的距离
    :cvar ICON_WIDTH: 图标列宽度（竖直排列时用来对齐标签）
    """

    #: 条目高度
    ITEM_HEIGHT = 40
    #: 条目内左右留白
    PADDING_X = 10
    #: 图标与标签之间的距离
    GAP = 8
    #: 图标列宽度
    ICON_WIDTH = 22
    #: 选中指示条的厚度
    INDICATOR_THICKNESS = 3
    #: 选中指示条的长度
    INDICATOR_LENGTH = 16

    def __init__(
        self,
        *args,
        items: Optional[Sequence] = None,
        orient: str = "vertical",
        selected: Optional[Union[int, str]] = None,
        command: Optional[Callable] = None,
        on_select: Optional[Callable] = None,
        font=None,
        mode: MODE = "light",
        style: str = "standard",
        width: Optional[Union[int, float]] = None,
        height: Optional[Union[int, float]] = None,
        item_height: Optional[int] = None,
        **kwargs,
    ) -> None:
        """构造导航栏。

        :param args: 透传给 :class:`tkinter.Canvas.__init__`
        :param items: 初始条目，写法见模块文档
        :param orient: ``"vertical"``（竖排）或 ``"horizontal"``（横排）
        :param selected: 初始选中项，可以是下标或 ``key``；``None`` 表示不选
        :param command: 选中项变化时的回调，尽量以 ``(index, item)`` 调用
        :param on_select: 与 ``command`` 同义（写起来更直白）
        :param font: 标签字体
        :param mode: ``"light"`` / ``"dark"``
        :param style: ``"standard"``（透明底）/ ``"card"``（圆角卡片底）
        :param width: 控件宽度；``None`` 时按内容自适应
        :param height: 控件高度；``None`` 时按内容自适应
        :param item_height: 条目高度；``None`` 时用类属性 ``ITEM_HEIGHT``
        :param kwargs: 其余参数透传给 :class:`tkinter.Canvas.__init__`

        :raises ValueError: ``orient`` 或 ``style`` 无法识别
        """
        if str(orient).lower() not in ORIENTS:
            raise ValueError(f"未知的方向 {orient!r}；应为 {list(ORIENTS)} 之一")
        if str(style).lower() not in STYLES:
            raise ValueError(f"未知的样式 {style!r}；应为 {list(STYLES)} 之一")

        self.orient = str(orient).lower()
        if item_height is not None:
            self.ITEM_HEIGHT = int(item_height)

        #: 条目字典列表
        self._items: List[Dict] = []
        #: 当前选中的下标；``-1`` 表示没有选中
        self._selected = -1
        #: 鼠标悬停的下标
        self._hover_index: Optional[int] = None
        #: 当前按下的下标
        self._pressed_index: Optional[int] = None
        #: 调用方是否显式指定过宽高（指定过就不再按内容自适应）
        self._fixed_size = width is not None or height is not None

        self._init(mode, style)

        if items:
            self._items = [_normalize_item(spec) for spec in items]

        master = args[0] if args else kwargs.get("master")
        auto_width, auto_height = self._measure(master)

        super().__init__(
            *args,
            width=auto_width if width is None else width,
            height=auto_height if height is None else height,
            **kwargs,
        )

        self.dconfigure(command=command, on_select=on_select)
        set_default_font(font, self.attributes, master=self)

        self.configure(takefocus=1)
        self._bind_events()

        if selected is not None:
            position = self._resolve_index(selected)
            if position is not None:
                self._selected = position
                self._draw()

    # ------------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------------
    def _init(self, mode, style):
        """建立属性字典（此时还没有 Tk 画布，不能碰任何 Tk 调用）。"""
        from easydict import EasyDict

        self.enter = False
        self.button1 = False
        self.isfocus = False
        self.mode = mode
        self.style = style

        self.attributes = EasyDict(
            {
                "command": None,
                "on_select": None,
                "font": None,
                "state": "normal",
                # 由 designs.litenav 填充
                "back_color": None,
                "back_opacity": 0.0,
                "border_color": None,
                "border_color_opacity": 0.0,
                "border_width": 0,
                "radius": 7,
                "item_text_color": "#1b1b1b",
                "item_disabled_text": "#a2a2a2",
                "item_selected_text": "#005fb8",
                "item_hover_back": "#f5f5f5",
                "item_pressed_back": "#efefef",
                "item_selected_back": "#e8f0f8",
                "indicator_color": "#005fb8",
                "indicator_idle": "#b9d3ea",
                "glyph_disabled": "#ffffff",
            }
        )
        self._apply_design()

    def _bind_events(self):
        """绑定导航栏专属事件。"""
        self.bind("<Motion>", self._event_motion, add="+")
        self.bind("<Double-Button-1>", self._event_double_click, add="+")

        forward, backward = (
            ("<Down>", "<Up>") if self.orient == "vertical" else ("<Right>", "<Left>")
        )
        self.bind(forward, lambda e=None: self._move(1), add="+")
        self.bind(backward, lambda e=None: self._move(-1), add="+")
        self.bind("<Home>", lambda e=None: self._move(-len(self._items)), add="+")
        self.bind("<End>", lambda e=None: self._move(len(self._items)), add="+")
        self.bind("<Return>", lambda e=None: self.activate(), add="+")
        self.bind("<space>", lambda e=None: self.activate(), add="+")

    # ------------------------------------------------------------------
    # 尺寸测算
    # ------------------------------------------------------------------
    def _measure(self, master):
        """按条目内容算出控件的默认宽高。"""
        widths = [self._item_width(item, master) for item in self._items]
        height = max(1, len(self._items) * self.ITEM_HEIGHT)
        if self.orient == "vertical":
            return (max(widths) if widths else 120), height
        return (sum(widths) if widths else 120), self.ITEM_HEIGHT

    def _item_width(self, item, master=None):
        """一个条目需要的宽度（含左右留白）。"""
        width = self.PADDING_X * 2
        if item.get("icon"):
            width += self.ICON_WIDTH + self.GAP
        if item.get("label"):
            width += measure_label_width(master, item["label"], padding=0)
        return int(width)

    # ------------------------------------------------------------------
    # 条目
    # ------------------------------------------------------------------
    def __len__(self):
        """条目个数。"""
        return len(self._items)

    def items(self) -> List[Dict]:
        """返回条目字典列表的一份拷贝（改它不影响控件）。"""
        return [dict(item) for item in self._items]

    def get_item(self, index) -> Dict:
        """取某个条目的字典拷贝。

        :param index: 下标或 ``key``
        :raises IndexError: 既不是合法下标，也找不到同名的 ``key``
        """
        position = self._resolve_index(index)
        if position is None:
            raise IndexError(f"找不到导航条目 {index!r}（共 {len(self._items)} 条）")
        return dict(self._items[position])

    def add_item(
        self,
        label: str = "",
        icon=None,
        key=None,
        command: Optional[Callable] = None,
        enabled: bool = True,
        index: Optional[int] = None,
    ) -> int:
        """追加（或插入）一个条目。

        :returns: 新条目的下标
        """
        item = _normalize_item(
            {
                "label": label,
                "icon": icon,
                "key": label if key is None else key,
                "command": command,
                "enabled": enabled,
            }
        )
        if index is None:
            self._items.append(item)
            position = len(self._items) - 1
        else:
            position = max(0, min(int(index), len(self._items)))
            self._items.insert(position, item)
            if self._selected >= position:
                self._selected += 1

        self.resize()
        self._draw()
        return position

    def remove_item(self, index):
        """删除一个条目（下标或 ``key``）。

        .. warning::
           不叫 ``delete``：本控件是 :class:`tkinter.Canvas`，
           ``Canvas.delete`` 用来删除画布元素（``_draw`` 开头就是
           ``self.delete("all")``），同名会递归调用自己。
        """
        position = self._resolve_index(index)
        if position is None:
            return
        self._items.pop(position)
        if self._selected == position:
            self._selected = -1
        elif self._selected > position:
            self._selected -= 1
        self._hover_index = None
        self._pressed_index = None
        self.resize()
        self._draw()

    #: :meth:`remove_item` 的别名
    delete_item = remove_item

    def configure_item(self, index, **changes):
        """修改某个条目。

        :param index: 下标或 ``key``
        :param changes: 可改 ``label`` / ``icon`` / ``key`` / ``enabled`` / ``command``
        """
        position = self._resolve_index(index)
        if position is None:
            return
        item = self._items[position]
        for field in ("label", "icon", "key", "enabled", "command"):
            if field in changes:
                item[field] = changes[field]
        self.resize()
        self._draw()

    def clear(self):
        """清空全部条目。"""
        self._items.clear()
        self._selected = -1
        self._hover_index = None
        self._pressed_index = None
        self.resize()
        self._draw()

    def resize(self):
        """按内容重新计算控件尺寸（只在没有显式指定宽高时生效）。"""
        if self._fixed_size:
            return
        width, height = self._measure(self.master)
        self.config(width=width, height=height)

    def _resolve_index(self, reference) -> Optional[int]:
        """把下标或 ``key`` 解析成下标；找不到时返回 ``None``。"""
        if isinstance(reference, str):
            for position, item in enumerate(self._items):
                if str(item.get("key")) == reference:
                    return position
            return None
        try:
            position = int(reference)
        except (TypeError, ValueError):
            return None
        return position if 0 <= position < len(self._items) else None

    def _normalize_index(self, index) -> int:
        """把下标规整成合法值（支持负数）。"""
        position = int(index)
        if position < 0:
            position += len(self._items)
        if not 0 <= position < len(self._items):
            raise IndexError(f"导航条目下标越界：{index}（共 {len(self._items)} 条）")
        return position

    # ------------------------------------------------------------------
    # 选择
    # ------------------------------------------------------------------
    def selected(self) -> int:
        """当前选中的下标；没有选中时返回 ``-1``。"""
        return self._selected

    def selected_key(self):
        """当前选中项的 ``key``；没有选中时返回 ``None``。"""
        if 0 <= self._selected < len(self._items):
            return self._items[self._selected].get("key")
        return None

    def selected_item(self) -> Optional[Dict]:
        """当前选中项的字典拷贝；没有选中时返回 ``None``。"""
        if 0 <= self._selected < len(self._items):
            return dict(self._items[self._selected])
        return None

    def select(self, reference, notify: bool = True) -> bool:
        """选中一项。

        :param reference: 下标或 ``key``
        :param notify: 是否触发回调
        :returns: 是否真的改变了选中项（重复选中 / 禁用项返回 ``False``）
        """
        position = self._resolve_index(reference)
        if position is None:
            return False
        if not self._items[position].get("enabled", True):
            return False
        if position == self._selected:
            return False
        self._selected = position
        self._draw()
        if notify:
            self._notify()
        return True

    def _notify(self):
        """触发选中回调（条目级 ``command`` 优先）。"""
        if not 0 <= self._selected < len(self._items):
            return
        item = self._items[self._selected]
        target = item.get("command") or self.attributes.command
        if target is None:
            target = self.attributes.on_select
        call_command(target, self._selected, dict(item))

    def activate(self, reference=None):
        """激活某一项：选中它（若尚未选中）并触发回调。

        :param reference: 下标或 ``key``；``None`` 表示当前选中项
        """
        if reference is not None:
            position = self._resolve_index(reference)
            if position is None:
                return
            if self.select(position, notify=True):
                return
            self._notify()
            return
        self._notify()

    def _move(self, delta: int):
        """把选中项移动若干个条目（跳过禁用项）。"""
        if not self._items:
            return
        total = len(self._items)
        position = self._selected
        if position < 0:
            position = -1 if delta > 0 else total
        step = 1 if delta >= 0 else -1
        for _ in range(max(1, abs(delta))):
            candidate = position + step
            while 0 <= candidate < total and not self._items[candidate].get(
                "enabled", True
            ):
                candidate += step
            if not 0 <= candidate < total:
                break
            position = candidate
        if position != self._selected:
            self.select(position)

    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------
    def theme(self, mode: Optional[MODE] = None, style: Optional[str] = None):
        """切换主题（并可顺带改样式）。

        :param mode: ``"light"`` / ``"dark"``；省略表示沿用当前值
        :param style: ``"standard"`` / ``"card"``；省略表示沿用当前值
        """
        if mode:
            self.mode = mode
        if style:
            self.style = style
        self._apply_design()
        self._draw()

    def _apply_design(self):
        """按 ``(mode, style)`` 刷新整套配色（过渡期间会取中间色）。"""
        self.dconfigure(
            blend_theme_design(
                self,
                litenav_design(
                    getattr(self, "mode", "light"),
                    getattr(self, "style", "standard"),
                ),
            )
        )

    # ------------------------------------------------------------------
    # 几何 / 绘制
    # ------------------------------------------------------------------
    def _item_geometry(self, position: int):
        """第 ``position`` 个条目的 ``(x1, y1, x2, y2)``。"""
        width, height = self._paint_size()
        inset = self.attributes.border_width
        if self.orient == "vertical":
            y1 = inset + position * self.ITEM_HEIGHT
            return (
                inset + 1,
                y1,
                max(inset + 1, width - inset - 1),
                y1 + self.ITEM_HEIGHT,
            )
        x1 = inset + sum(
            self._item_width(item, self) for item in self._items[:position]
        )
        return (
            x1,
            inset + 1,
            x1 + self._item_width(self._items[position], self),
            height - inset - 1,
        )

    def _paint_size(self):
        """本帧实际使用的画布尺寸。"""
        return (
            getattr(self, "_paint_width", None) or self.winfo_width(),
            getattr(self, "_paint_height", None) or self.winfo_height(),
        )

    def _hit_index(self, x, y) -> Optional[int]:
        """坐标落在第几个条目上；不在任何条目上时返回 ``None``。"""
        width, height = self._paint_size()
        if not (0 <= x <= width and 0 <= y <= height):
            return None
        for position in range(len(self._items)):
            x1, y1, x2, y2 = self._item_geometry(position)
            if x1 <= x <= x2 and y1 <= y <= y2:
                return position
        return None

    def _draw(self, event: Optional[Event] = None):
        """把导航栏画出来。"""
        super()._draw(event)

        self.delete("all")

        # 这里必须直接读 winfo_*，**不能**经过 `_paint_size()`：
        # 构造期的第一次 _draw 是在控件还没映射时跑的（尺寸是 1x1），
        # 那次会把 `_paint_width` 记成 1；再通过 `_paint_size()` 读回来
        # 就永远是那个陈旧的 1，条目几何算出来是负高度，于是一个字都画不出来。
        width = self.winfo_width()
        height = self.winfo_height()
        self._paint_width = width
        self._paint_height = height

        if width <= 1 or height <= 1:
            return

        if self.attributes.back_color:
            self.draw_roundrect(
                0,
                0,
                width,
                height,
                self.attributes.radius,
                temppath=self.temppath,
                temppath2=self.temppath3,
                fill=self.attributes.back_color,
                fill_opacity=self.attributes.back_opacity,
                outline=self.attributes.border_color,
                outline_opacity=self.attributes.border_color_opacity,
                width=self.attributes.border_width,
            )

        for position in range(len(self._items)):
            self._draw_item(position)

    def _draw_item(self, position: int):
        """画一个条目：底色 + 指示条 + 图标 + 标签。"""
        item = self._items[position]
        x1, y1, x2, y2 = self._item_geometry(position)
        if x2 <= x1 or y2 <= y1:
            return

        enabled = bool(item.get("enabled", True))
        is_selected = position == self._selected
        is_pressed = position == self._pressed_index
        is_hover = position == self._hover_index

        if enabled:
            background = None
            if is_pressed:
                background = self.attributes.item_pressed_back
            elif is_hover:
                background = self.attributes.item_hover_back
            elif is_selected:
                background = self.attributes.item_selected_back
            if background:
                self.draw_roundrect(
                    x1 + 2,
                    y1 + 2,
                    x2 - 2,
                    y2 - 2,
                    max(0, self.attributes.radius - 2),
                    temppath=self.temppath2,
                    temppath2=self.temppath4,
                    fill=background,
                    fill_opacity=1.0,
                    outline=None,
                    outline_opacity=0.0,
                    width=0,
                )

        if is_selected:
            self._draw_indicator(x1, y1, x2, y2)

        if not enabled:
            text_color = self.attributes.item_disabled_text
        elif is_selected:
            text_color = self.attributes.item_selected_text
        else:
            text_color = self.attributes.item_text_color

        text_x = x1 + self.PADDING_X
        center_y = (y1 + y2) / 2.0

        if item.get("icon"):
            self.create_text(
                text_x + self.ICON_WIDTH / 2.0,
                center_y,
                anchor="center",
                fill=text_color,
                text=str(item["icon"]),
                font=self.attributes.font,
            )
            text_x += self.ICON_WIDTH + self.GAP

        if item.get("label"):
            self.create_text(
                text_x,
                center_y,
                anchor="w" if self.orient == "vertical" else "center",
                fill=text_color,
                text=str(item["label"]),
                font=self.attributes.font,
            )

    def _draw_indicator(self, x1, y1, x2, y2):
        """画选中指示条（竖排在左，横排在下）。"""
        thickness = self.INDICATOR_THICKNESS

        if self.orient == "vertical":
            center = (y1 + y2) / 2.0
            length = min(float(self.INDICATOR_LENGTH), max(4.0, (y2 - y1) - 12))
            box = (x1 + 2, center - length / 2.0, x1 + 2 + thickness, center + length / 2.0)
        else:
            center = (x1 + x2) / 2.0
            length = min(float(self.INDICATOR_LENGTH + 10), max(4.0, (x2 - x1) - 16))
            box = (center - length / 2.0, y2 - 2 - thickness, center + length / 2.0, y2 - 2)

        self.draw_roundrect(
            box[0],
            box[1],
            box[2],
            box[3],
            thickness / 2.0,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=self.attributes.indicator_color,
            fill_opacity=1.0,
            outline=None,
            outline_opacity=0.0,
            width=0,
        )

    # ------------------------------------------------------------------
    # 事件
    # ------------------------------------------------------------------
    def _event_on_button1(self, event: Optional[Event] = None):
        """左键按下：记下按下的条目。"""
        if event is not None:
            position = self._hit_index(event.x, event.y)
            if position is not None:
                self.focus_set()
                self._pressed_index = (
                    position
                    if self._items[position].get("enabled", True)
                    else None
                )
                super()._event_on_button1(event)
                return
        self._pressed_index = None
        super()._event_on_button1(event)

    def _event_off_button1(self, event: Optional[Event] = None):
        """左键松开：在按下的条目上松开才算一次点击。"""
        position = self._pressed_index
        self._pressed_index = None
        if position is not None:
            self.select(position, notify=True)
            self._draw()
        super()._event_off_button1(event)

    def _event_motion(self, event: Optional[Event] = None):
        """鼠标移动：更新悬停下标（只有换了条目才重绘）。"""
        position = self._hit_index(event.x, event.y) if event is not None else None
        if position != self._hover_index:
            self._hover_index = position
            self._draw()

    def _event_leave(self, event: Optional[Event] = None):
        """鼠标离开 → 清掉悬停与按压。"""
        self._hover_index = None
        self._pressed_index = None
        super()._event_leave(event)

    def _event_double_click(self, event: Optional[Event] = None):
        """双击 → 激活该条目（已选中时也会再触发一次回调）。"""
        if event is None:
            return
        position = self._hit_index(event.x, event.y)
        if position is None:
            return
        if not self._items[position].get("enabled", True):
            return
        self._selected = position
        self._draw()
        self._notify()
