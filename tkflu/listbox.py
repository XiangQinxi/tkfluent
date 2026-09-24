"""列表组件。

``FluListBox`` 是一个真正的列表控件：条目数据、单选/多选、键盘导航、
滚轮与可拖动的滚动条，全部由控件自己绘制，不依赖任何原生 Tk 列表控件。

.. code-block:: python

    import tkflu

    root = tkflu.FluWindow()
    box = tkflu.FluListBox(root, width=260, height=180,
                           items=[f"第 {i} 行" for i in range(1, 31)])
    box.pack(padx=12, pady=12)
    box.dconfigure(command=lambda index, item: print("激活", index, item))
    root.mainloop()

数据与选择
----------
====================== ==========================================================
方法                   说明
====================== ==========================================================
``insert(index, item)`` 在 ``index`` 处插入条目（``"end"`` 表示追加）
``append(item)``        追加到末尾
``delete_item(index)``  删除一个条目；``"all"`` 清空（``remove`` 是同义别名）
``clear()``             清空全部条目
``get(index)``          取条目原始对象
``index(item)``         取条目下标；找不到返回 ``None``
``selection()``         当前选中的下标元组（``curselection()`` 是同义别名）
``select(index)``       选中；``deselect`` 取消、``select_all`` 全选
``see(index)``          把某一条滚进可视区
====================== ==========================================================

``selectmode`` 支持三种，语义与 Windows 一致：

* ``"single"``   —— 一次只能选一条（默认）；
* ``"multiple"`` —— 点一条切换一条，互不影响；
* ``"extended"`` —— ``Ctrl+点`` 切换、``Shift+点`` 选择区间。

回调
----
* ``command``   —— **激活**时触发（双击、或选中后按 ``Enter``），
  调用时会尽量带上 ``(index, item)``；只写 ``lambda: ...`` 的老代码照样能用
  （见 :func:`tkflu.defs.call_command`）。
* ``on_select`` —— 选中集合变化时触发，参数同样是 ``(indices, items)``。

.. note::
   构造参数 ``text`` 是老占位实现的遗留：列表为空时它会作为居中提示文字
   显示出来（空列表状态）。想放条目请用 ``items``。
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Set, Tuple, Union

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .constants import MODE, STATE
from .designs.listbox import RADIUS
from .designs.listbox import listbox as listbox_design

__all__ = ["FluListBox", "FluListBoxCanvas", "FluListBoxDraw"]

#: 支持的三种选择模式
SELECT_MODES = ("single", "multiple", "extended")


class FluListBoxDraw(DSvgDraw):
    """列表的 SVG 绘制后端。

    ``create_roundrect`` 里固定了渐变定义的 id（``DListBox.Border``），
    其余图元都直接用 :class:`tkdeft.windows.draw.DSvgDraw` 的通用实现。
    """

    def create_roundrect(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        radiusy=None,
        temppath=None,
        fill="transparent",
        outline="black",
        outline2="black",
        width=1,
        gradient_stop1=0.0,
        gradient_stop2=1.0,
        **extra,
    ):
        """列表背景的 SVG 图元。

        :param gradient_stop1: 渐变描边起点（列表用 0%→100%，不同于 button 的 0.9→1.0）
        :param gradient_stop2: 渐变描边终点
        :param extra: 其余关键字透传给 svgwrite 的 ``rect()``
        :returns: 生成好的 SVG 文件路径

        渐变的 id 固定为 ``DListBox.Border``；几何由
        :func:`tkdeft.svg.add_roundrect` 内缩半个线宽，四边描边才完整。
        """
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        from tkdeft.svg import add_roundrect

        add_roundrect(
            drawing[1],
            x1,
            y1,
            x2,
            y2,
            _rx,
            _ry,
            fill=fill,
            outline=outline,
            outline2=outline2,
            width=width,
            gradient_id="DListBox.Border",
            gradient_stop1=gradient_stop1,
            gradient_stop2=gradient_stop2,
            **extra,
        )
        drawing[1].save()
        return drawing[0]


class FluListBoxCanvas(DCanvas):
    """列表的画布。"""

    draw = FluListBoxDraw

    def create_round_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        r1,
        r2=None,
        temppath=None,
        fill="transparent",
        outline="black",
        outline2="black",
        width=1,
    ) -> int:
        """画列表的圆角背景。

        :param r1: 圆角半径（x 方向）
        :param r2: 圆角半径（y 方向）
        :returns: 画布上的 item id

        列表的描边是 0%→100% 的竖直渐变（button 是 0.9→1.0），
        所以这里显式把两个 stop 传给
        :meth:`tkdeft.windows.canvas.DCanvas.draw_roundrect`。
        快速路径的判定与回退都在 tkdeft 里，组件层不再重复。
        """
        return self.draw_roundrect(
            x1,
            y1,
            x2,
            y2,
            r1,
            r2,
            temppath=temppath,
            gradient_stop1=0.0,
            gradient_stop2=1.0,
            fill=fill,
            outline=outline,
            outline2=outline2,
            width=width,
        )

    create_roundrect = create_round_rectangle


from tkinter import Event  # noqa: E402

from .defs import call_command, set_default_font  # noqa: E402
from .theme_transition import blend_theme_design  # noqa: E402
from .tooltip import FluToolTipBase  # noqa: E402

#: 文本宽度测量结果的缓存上限（避免长列表反复二分）
_TEXT_CACHE_LIMIT = 512


class FluListBox(FluListBoxCanvas, DDrawWidget, FluToolTipBase):
    """可滚动、可选择的列表控件。

    :cvar ITEM_HEIGHT: 单行高度（像素）
    :cvar PADDING_X: 条目文字与左边缘的距离
    :cvar ROW_RADIUS: 条目高亮的圆角半径
    """

    #: 单行高度（设计稿：单行 40、两行 56、三行 72 —— 每多一行 +16）
    ITEM_HEIGHT = 40
    #: 条目文字与条目左边缘的距离（设计稿：16）
    PADDING_X = 16
    #: 条目高亮相对控件内边距的横向内缩（设计稿：左右各 5）
    ROW_INSET_X = 5
    #: 条目高亮相对控件内边距的纵向内缩（设计稿：上下各 3）
    ROW_INSET_Y = 3
    #: 条目高亮的圆角半径（设计稿：3）
    ROW_RADIUS = 3
    #: 选中指示条的宽度（设计稿：3，圆角 1.5）
    INDICATOR_WIDTH = 3
    #: 选中指示条的长度（设计稿：40/56 高的行用 16，72 高的行用 32）
    INDICATOR_HEIGHT = 16
    #: 选中指示条距条目左边缘的距离（设计稿：4）
    INDICATOR_INSET = 4
    #: 滚动条滑块宽度（设计稿：细态 2 / 展开态 6；这里取展开态，
    #: 因为本控件的滑块是常驻的，太细会看不见）
    THUMB_WIDTH = 6
    #: 滑块的最小高度
    MIN_THUMB = 20

    def __init__(
        self,
        *args,
        items: Optional[Iterable] = None,
        text: str = "",
        width: Union[int, float] = 200,
        height: Optional[Union[int, float]] = None,
        command: Optional[Callable] = None,
        on_select: Optional[Callable] = None,
        font=None,
        mode: MODE = "light",
        style: str = "standard",
        state: STATE = "normal",
        selectmode: str = "single",
        item_height: Optional[int] = None,
        scrollbar: bool = True,
        **kwargs,
    ) -> None:
        """构造列表。

        :param args: 透传给 :class:`tkinter.Canvas.__init__`
        :param items: 初始条目（任意对象，显示时取 ``str()``）
        :param text: 空列表时显示的居中提示文字（老占位实现的遗留参数）
        :param width: 控件宽度
        :param height: 控件高度；``None`` 时"只给 text 的旧写法"用 32，
            其余情况用 160
        :param command: 激活回调，尽量以 ``(index, item)`` 调用
        :param on_select: 选中集合变化回调，尽量以 ``(indices, items)`` 调用
        :param font: 条目字体
        :param mode: ``"light"`` / ``"dark"``
        :param style: ``"standard"`` / ``"accent"``
        :param state: ``"normal"`` / ``"disabled"``
        :param selectmode: ``"single"`` / ``"multiple"`` / ``"extended"``
        :param item_height: 单行高度；``None`` 时用类属性 ``ITEM_HEIGHT``
        :param scrollbar: 是否绘制并允许拖动滚动条
        :param kwargs: 其余参数透传给 :class:`tkinter.Canvas.__init__`

        :raises ValueError: ``selectmode`` 无法识别
        """
        if str(selectmode).lower() not in SELECT_MODES:
            raise ValueError(
                f"未知的选择模式 {selectmode!r}；应为 {list(SELECT_MODES)} 之一"
            )

        self.selectmode = str(selectmode).lower()
        if item_height is not None:
            self.ITEM_HEIGHT = int(item_height)

        #: 条目原始对象
        self._items: List = []
        #: 选中的下标集合
        self._selected: Set[int] = set()
        #: 第一个可见行的下标
        self._offset = 0
        #: 鼠标悬停的行
        self._hover_index: Optional[int] = None
        #: Shift 区间选择的锚点
        self._anchor: Optional[int] = None
        #: 滚动条滑块拖拽状态
        self._drag: Optional[dict] = None
        self._show_scrollbar = bool(scrollbar)
        self._text_cache: dict = {}
        #: 最近一次选中集合的快照，用于判断是否要触发 on_select
        self._last_selection: Tuple[int, ...] = ()

        self._init(mode, style, state)

        if height is None:
            # 老写法（只给 text）继续按单行高度渲染，新写法默认给一个能看的高度
            height = 32 if (items is None and text) else 160

        super().__init__(*args, width=width, height=height, **kwargs)

        self.dconfigure(text=text, command=command, on_select=on_select)
        set_default_font(font, self.attributes, master=self)

        self.configure(takefocus=1)
        if items:
            self._items = list(items)

        self._bind_events()

    # ------------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------------
    def _init(self, mode, style, state):
        """建立属性字典（此时还没有 Tk 画布，不能碰任何 Tk 调用）。"""
        from easydict import EasyDict

        self.enter = False
        self.button1 = False
        self.isfocus = False
        self.mode = mode
        self.style = style

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "on_select": None,
                "font": None,
                "state": "normal",
                "back_color": "#ffffff",
                "border_color": "#f0f0f0",
                "border_color2": "#d6d6d6",
                "border_width": 1,
                "radius": RADIUS,
                "text_color": "#1b1b1b",
                "item_text_color": "#1b1b1b",
                "item_hover_back": "#f0f0f0",
                "item_pressed_back": "#f4f4f4",
                "item_selected_back": "#f0f0f0",
                "item_selected_text": "#1b1b1b",
                "indicator_color": "#005fb8",
                "indicator_disabled": "#c8c8c8",
                "scroll_thumb_color": "#8a8a8a",
                "scroll_thumb_opacity": 1.0,
            }
        )

        self.attributes.state = state
        self._apply_design()

    def _bind_events(self):
        """绑定列表专属的鼠标 / 键盘事件。"""
        self.bind("<Motion>", self._event_motion, add="+")
        self.bind("<B1-Motion>", self._event_drag, add="+")
        self.bind("<Double-Button-1>", self._event_double_click, add="+")
        self.bind("<MouseWheel>", self._event_wheel, add="+")
        # X11 没有 <MouseWheel>，滚轮是 Button-4 / Button-5
        self.bind("<Button-4>", self._event_wheel, add="+")
        self.bind("<Button-5>", self._event_wheel, add="+")

        self.bind("<Up>", lambda e=None: self._move_selection(-1), add="+")
        self.bind("<Down>", lambda e=None: self._move_selection(1), add="+")
        self.bind("<Prior>", lambda e=None: self._move_selection(-self._visible_rows()), add="+")
        self.bind("<Next>", lambda e=None: self._move_selection(self._visible_rows()), add="+")
        self.bind("<Home>", lambda e=None: self._move_selection_to(0), add="+")
        self.bind("<End>", lambda e=None: self._move_selection_to(len(self._items) - 1), add="+")
        self.bind("<Return>", lambda e=None: self.activate(), add="+")
        self.bind("<space>", lambda e=None: self.activate(), add="+")

    # ------------------------------------------------------------------
    # 数据
    # ------------------------------------------------------------------
    def __len__(self):
        """条目个数。"""
        return len(self._items)

    def items(self) -> List:
        """返回条目列表的一份拷贝。"""
        return list(self._items)

    def get(self, index: int):
        """取第 ``index`` 条的原始对象。

        :raises IndexError: 下标越界
        """
        return self._items[self._normalize_index(index)]

    def index(self, item) -> Optional[int]:
        """取某个条目对象的下标；不存在时返回 ``None``。"""
        try:
            return self._items.index(item)
        except ValueError:
            return None

    def insert(self, index, item):
        """插入一个条目。

        :param index: 插入位置；``"end"`` 表示追加到末尾
        :param item: 任意对象，显示时取 ``str()``
        """
        if isinstance(index, str):
            position = len(self._items) if index.lower() == "end" else int(index)
        else:
            position = int(index)
        position = max(0, min(position, len(self._items)))

        self._items.insert(position, item)
        # 插入点之后的选中下标要整体后移，否则选中项会"跟着数据跑掉"
        self._selected = {
            value + 1 if value >= position else value for value in self._selected
        }
        self._clamp_offset()
        self._draw()

    def append(self, item):
        """追加一个条目（:meth:`insert` 的便捷写法）。"""
        self.insert("end", item)

    def set(self, index: int, item):
        """替换第 ``index`` 条的内容。"""
        self._items[self._normalize_index(index)] = item
        self._draw()

    def delete_item(self, index):
        """删除条目。

        :param index: 下标；``"all"`` 表示清空整个列表

        .. warning::
           这个方法**不叫** ``delete``。``FluListBox`` 本身是一个
           :class:`tkinter.Canvas`，而 ``Canvas.delete`` 是用来删除画布元素的
           （``_draw`` 开头就是 ``self.delete("all")``）。一旦把条目删除也叫
           ``delete``，重绘时就会递归调用自己，直接 ``RecursionError``。
           要清空列表请用 :meth:`clear` 或 ``delete_item("all")``。
        """
        if isinstance(index, str) and index.lower() == "all":
            self.clear()
            return

        position = self._normalize_index(index)
        self._items.pop(position)
        self._selected = {
            (value - 1 if value > position else value)
            for value in self._selected
            if value != position
        }
        self._hover_index = None
        self._clamp_offset()
        self._draw()
        self._notify_selection()

    #: :meth:`delete_item` 的别名
    remove = delete_item

    def clear(self):
        """清空全部条目与选择。"""
        self._items.clear()
        self._selected.clear()
        self._offset = 0
        self._hover_index = None
        self._draw()
        self._notify_selection()

    def _normalize_index(self, index) -> int:
        """把下标规整成合法值（支持负数）。"""
        position = int(index)
        if position < 0:
            position += len(self._items)
        if not 0 <= position < len(self._items):
            raise IndexError(f"条目下标越界：{index}（共 {len(self._items)} 条）")
        return position

    # ------------------------------------------------------------------
    # 选择
    # ------------------------------------------------------------------
    def selection(self) -> Tuple[int, ...]:
        """当前选中的下标（升序元组）。"""
        return tuple(sorted(self._selected))

    #: Tk 风格的别名
    curselection = selection

    def selected_items(self) -> List:
        """当前选中的条目对象列表。"""
        return [self._items[i] for i in self.selection()]

    def is_selected(self, index: int) -> bool:
        """某一条是否被选中。"""
        return int(index) in self._selected

    def select(self, index: int, notify: bool = True):
        """选中一条（``"single"`` 模式下会先清空其它选择）。"""
        position = self._normalize_index(index)
        if self.selectmode == "single":
            self._selected = {position}
        else:
            self._selected.add(position)
        self._anchor = position
        self.see(position)
        self._draw()
        if notify:
            self._notify_selection()

    def deselect(self, index: int, notify: bool = True):
        """取消选中一条。"""
        self._selected.discard(self._normalize_index(index))
        self._draw()
        if notify:
            self._notify_selection()

    def select_all(self, notify: bool = True):
        """全选（``"single"`` 模式下只选中第一条）。"""
        if self.selectmode == "single":
            self._selected = {0} if self._items else set()
        else:
            self._selected = set(range(len(self._items)))
        self._draw()
        if notify:
            self._notify_selection()

    def clear_selection(self, notify: bool = True):
        """清空选择。"""
        self._selected.clear()
        self._anchor = None
        self._draw()
        if notify:
            self._notify_selection()

    def _notify_selection(self):
        """选中集合真的变了才回调 ``on_select``。"""
        current = self.selection()
        if current == self._last_selection:
            return
        self._last_selection = current
        call_command(self.attributes.on_select, current, self.selected_items())

    # ------------------------------------------------------------------
    # 滚动
    # ------------------------------------------------------------------
    def _visible_rows(self) -> int:
        """当前能完整显示的行数（至少 1）。"""
        _width, height = self._paint_size()
        return max(1, int(height // self.ITEM_HEIGHT))

    def _max_offset(self) -> int:
        """``_offset`` 的上界。"""
        return max(0, len(self._items) - self._visible_rows())

    def _clamp_offset(self):
        """把 ``_offset`` 夹回合法范围。"""
        self._offset = max(0, min(self._offset, self._max_offset()))

    def see(self, index: int):
        """把第 ``index`` 条滚进可视区（不会画出界）。"""
        position = int(index)
        if position < 0 or position >= len(self._items):
            return
        rows = self._visible_rows()
        if position < self._offset:
            self._offset = position
        elif position >= self._offset + rows:
            self._offset = position - rows + 1
        self._clamp_offset()

    def yview(self, *args):
        """Tk 风格的滚动接口。

        * ``yview()`` → ``(首个可见行的比例, 末行之后的比例)``
        * ``yview(index)`` → 把该条滚进可视区（返回 ``(offset, offset+rows)`` 之类的二元组）
        * ``yview_moveto(fraction)`` / ``yview_scroll(n, what)``
        """
        if not args:
            total = len(self._items)
            if not total:
                return (0.0, 1.0)
            rows = self._visible_rows()
            return (self._offset / total, min(1.0, (self._offset + rows) / total))

        if len(args) == 1 and not isinstance(args[0], str):
            self.see(args[0])
            self._draw()
            return (self._offset, min(len(self._items), self._offset + self._visible_rows()))

        if len(args) == 2:
            if args[0] == "moveto":
                self.yview_moveto(args[1])
            elif args[0] == "scroll":
                self.yview_scroll(*args[1:])
            return None

        raise TypeError(f"yview() 不认识的参数：{args!r}")

    def yview_moveto(self, fraction):
        """按比例滚动（``0.0`` 顶部，``1.0`` 底部）。"""
        total = len(self._items)
        if total:
            rows = self._visible_rows()
            self._offset = int(float(fraction) * max(0, total - rows))
            self._clamp_offset()
        self._draw()

    def yview_scroll(self, number, what="units"):
        """按行（``units``）或按页（``pages``）滚动。"""
        if str(what).startswith("page"):
            step = max(1, self._visible_rows()) * int(number)
        else:
            step = int(number)
        self.scroll(step)

    def scroll(self, rows: int):
        """滚动 ``rows`` 行（正数向下）。"""
        previous = self._offset
        self._offset += int(rows)
        self._clamp_offset()
        if self._offset != previous:
            self._draw()

    # ------------------------------------------------------------------
    # 激活 / 键盘
    # ------------------------------------------------------------------
    def activate(self, index: Optional[int] = None):
        """触发 ``command``。

        :param index: 要激活的条目；``None`` 时用当前选中的第一条
        """
        if self.attributes.state == "disabled":
            return None
        if index is None:
            current = self.selection()
            index = current[0] if current else None
        if index is None or not 0 <= int(index) < len(self._items):
            return None
        position = int(index)
        return call_command(
            self.attributes.command, position, self._items[position]
        )

    def invoke(self):
        """``activate`` 的历史别名。"""
        return self.activate()

    def _move_selection(self, delta: int):
        """把选择上下移动 ``delta`` 行（不触发 ``on_select`` 的额外语义）。"""
        if not self._items:
            return
        current = self.selection()
        if current:
            target = current[0] + delta
        else:
            target = 0 if delta >= 0 else len(self._items) - 1
        self._move_selection_to(target)

    def _move_selection_to(self, target: int):
        """把选择移动到某一行并保证它可见。"""
        if not self._items:
            return
        target = max(0, min(int(target), len(self._items) - 1))
        self.focus_set()
        self.select(target)

    # ------------------------------------------------------------------
    # 命中测试
    # ------------------------------------------------------------------
    def _row_at(self, y) -> Optional[int]:
        """画布坐标 ``y`` 落在第几行；不在任何行上时返回 ``None``。"""
        inset = self.attributes.border_width
        local = float(y) - inset
        if local < 0:
            return None
        position = self._offset + int(local // self.ITEM_HEIGHT)
        if 0 <= position < len(self._items):
            return position
        return None

    def _row_geometry(self, position: int):
        """第 ``position`` 行的**高亮底**在画布上的 ``(x1, y1, x2, y2)``。

        设计稿：高亮底相对条目左右各内缩 5、上下各内缩 3，圆角 3。
        """
        inset = self.attributes.border_width
        width, height = self._paint_size()

        top = inset + (position - self._offset) * self.ITEM_HEIGHT
        y1 = top + self.ROW_INSET_Y
        y2 = top + self.ITEM_HEIGHT - self.ROW_INSET_Y
        return (
            inset + self.ROW_INSET_X,
            y1,
            max(inset + self.ROW_INSET_X + 1, width - inset - self.ROW_INSET_X),
            min(y2, height - inset),
        )

    def _row_text_x(self, x1):
        """条目文字的左边距：高亮底左边缘 + 16（设计稿）。"""
        return x1 - self.ROW_INSET_X + self.PADDING_X

    def _paint_size(self):
        """本帧实际使用的画布尺寸。

        ``_draw`` 里会对 wand 引擎做 1 像素补偿，行的几何必须跟着同一套尺寸走，
        否则拖拽、命中测试与画出来的东西会对不上。
        """
        return (
            getattr(self, "_paint_width", None) or self.winfo_width(),
            getattr(self, "_paint_height", None) or self.winfo_height(),
        )

    def _scrollbar_geometry(self):
        """滑轨与滑块的几何；不需要滚动条时返回 ``None``。

        :returns: ``(track, thumb)``，每个都是 ``(x1, y1, x2, y2)``
        """
        total = len(self._items)
        rows = self._visible_rows()
        if not self._show_scrollbar or total <= rows:
            return None

        inset = self.attributes.border_width
        width, height = self._paint_size()

        x2 = width - inset - 2
        x1 = x2 - self.THUMB_WIDTH
        y1 = inset + 2
        y2 = height - inset - 2
        track_height = max(1.0, y2 - y1)

        thumb_height = max(self.MIN_THUMB, track_height * rows / float(total))
        thumb_height = min(thumb_height, track_height)
        span = track_height - thumb_height
        max_offset = max(1, self._max_offset())
        thumb_y1 = y1 + span * (self._offset / float(max_offset))
        thumb_y2 = thumb_y1 + thumb_height

        return (x1, y1, x2, y2), (x1, thumb_y1, x2, thumb_y2)

    def _hit_scrollbar(self, x, y) -> bool:
        """判断某个点是否落在滑块上。"""
        geometry = self._scrollbar_geometry()
        if geometry is None:
            return False
        thumb = geometry[1]
        return thumb[0] - 2 <= x <= thumb[2] + 2 and thumb[1] <= y <= thumb[3]

    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------
    def theme(self, mode: Optional[MODE] = None, style: Optional[str] = None):
        """切换主题（并可顺带改样式）。

        :param mode: ``"light"`` / ``"dark"``
        :param style: ``"standard"`` / ``"accent"``；省略表示沿用构造时的样式

        .. warning::
           分支判断必须用 ``self.style``，**不能**用这个参数：
           一键换肤时 :class:`~tkflu.thememanager.FluThemeManager` 只会传
           ``mode``，参数 ``style`` 是 ``None``，拿它去 ``.lower()``
           会直接抛 ``AttributeError``。
        """
        if mode:
            self.mode = mode
        if style:
            self.style = style
        self._apply_design()

    def _apply_design(self):
        """按 ``(mode, style, 状态)`` 刷新整套配色。

        :meth:`_draw` 开头就会调这里重算配色，所以换肤过渡期间必须让
        :func:`~tkflu.theme_transition.blend_theme_design` 把目标色换成当前帧的
        中间色——不然列表会是整屏里唯一不参与过渡的组件。
        """
        design = listbox_design(
            getattr(self, "mode", "light"),
            getattr(self, "style", "standard"),
            self._visual_state(),
        )
        self.dconfigure(blend_theme_design(self, design))

    def _visual_state(self):
        """把交互状态位归并成设计规范认识的状态名。"""
        if self.attributes.state == "disabled":
            return "disabled"
        return self.interaction_state()

    def _light(self):
        """切到浅色标准样式（历史 API）。"""
        self.theme(mode="light", style="standard")

    def _light_accent(self):
        """切到浅色强调样式（历史 API）。"""
        self.theme(mode="light", style="accent")

    def _dark(self):
        """切到深色标准样式（历史 API）。"""
        self.theme(mode="dark", style="standard")

    def _dark_accent(self):
        """切到深色强调样式（历史 API）。"""
        self.theme(mode="dark", style="accent")

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------
    def _draw(self, event: Optional[Event] = None):
        """把列表画出来：背景 + 可见行 + 滚动条 + 空状态提示。"""
        super()._draw(event)

        # 与其它新组件一致：每次重绘按当前状态重算配色，
        # 这样 dconfigure(state=...) 与 hover 都能立刻反映出来。
        self._apply_design()

        self.delete("all")
        self._clamp_offset()

        width = self.winfo_width()
        height = self.winfo_height()

        from .designs.renderer import get_renderer

        if get_renderer() == 1:
            width -= 1
            height -= 1

        # 本帧的画布尺寸：命中测试与拖拽都读这一份，保证和画出来的一致
        self._paint_width = width
        self._paint_height = height

        inset = self.attributes.border_width

        self.element_border = self.create_round_rectangle(
            0,
            0,
            width,
            height,
            self.attributes.radius,
            temppath=self.temppath,
            fill=self.attributes.back_color,
            outline=self.attributes.border_color,
            outline2=self.attributes.border_color2,
            width=inset,
        )

        if not self._items:
            self._draw_empty_state(width, height)
            return

        # 只画"完整显示"的行。滚动是按整行步进的，底部最多空出一行的高度，
        # 看起来就是内边距；而画半行在 Tk 里没法裁剪（画布会把行压扁）。
        last = min(len(self._items), self._offset + self._visible_rows())
        for position in range(self._offset, last):
            self._draw_row(position)

        self._draw_scrollbar()

    def _draw_empty_state(self, width, height):
        """列表为空时居中显示 ``text``（老占位实现的外观）。"""
        if not self.attributes.text:
            return
        self.element_text = self.create_text(
            width / 2.0,
            height / 2.0,
            anchor="center",
            fill=self.attributes.item_text_color,
            text=self.attributes.text,
            font=self.attributes.font,
        )

    def _draw_row(self, position: int):
        """画一行：高亮底 + 选中指示条 + 文字。"""
        x1, y1, x2, y2 = self._row_geometry(position)
        if y2 <= y1:
            return

        selected = position in self._selected
        hovered = position == self._hover_index
        pressed = hovered and self.button1 and self.attributes.state != "disabled"

        # 设计稿：选中行与悬停行**同色**（都是中性色），强调色只给左侧指示条
        background = None
        if self.attributes.state != "disabled":
            if pressed:
                background = self.attributes.item_pressed_back
            elif hovered:
                background = self.attributes.item_hover_back
            elif selected:
                background = self.attributes.item_selected_back

        if background:
            self.create_roundrect_highlight(x1, y1, x2, y2, background)

        if selected:
            self._draw_indicator(x1, y1, y2)

        text_x = self._row_text_x(x1)
        available = (x2 - text_x) - 6
        self.create_text(
            text_x,
            (y1 + y2) / 2.0,
            anchor="w",
            fill=self.attributes.item_text_color,
            text=self._ellipsize(str(self._items[position]), available),
            font=self.attributes.font,
        )

    def create_roundrect_highlight(self, x1, y1, x2, y2, color):
        """画一行的高亮底（单独抽出来是为了方便子类换图元）。"""
        return self.draw_roundrect(
            x1,
            y1,
            x2,
            y2,
            self.ROW_RADIUS,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill=color,
            fill_opacity=1.0,
            outline=None,
            outline_opacity=0.0,
            width=0,
        )

    def _draw_indicator(self, x1, y1, y2):
        """画选中行左侧的强调色指示条。

        设计稿：``Selector`` 是 3 宽、圆角 1.5、垂直居中、长 16（行高 72 时 32）、
        距条目左边缘 4（不是紧贴高亮底的左边缘——高亮底本身已经内缩了 5，
        所以这里要从条目左边缘算起）。
        """
        width = self.INDICATOR_WIDTH
        row_height = y2 - y1 + self.ROW_INSET_Y * 2
        length = self.INDICATOR_HEIGHT * 2 if row_height > 56 else self.INDICATOR_HEIGHT
        length = min(float(length), max(4.0, row_height - 8))
        center = (y1 + y2) / 2.0
        left = x1 - self.ROW_INSET_X + self.INDICATOR_INSET
        self.draw_roundrect(
            left,
            center - length / 2.0,
            left + width,
            center + length / 2.0,
            width / 2.0,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=self.attributes.indicator_color,
            fill_opacity=1.0,
            outline=None,
            outline_opacity=0.0,
            width=0,
        )

    def _draw_scrollbar(self):
        """画自绘滚动条（不占用条目宽度，作为浮层盖在右侧）。"""
        geometry = self._scrollbar_geometry()
        if geometry is None:
            return
        _track, thumb = geometry
        if thumb[3] - thumb[1] <= 0:
            return
        self.draw_roundrect(
            thumb[0],
            thumb[1],
            thumb[2],
            thumb[3],
            self.THUMB_WIDTH / 2.0,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill=self.attributes.scroll_thumb_color,
            fill_opacity=self.attributes.scroll_thumb_opacity,
            outline=None,
            outline_opacity=0.0,
            width=0,
        )

    # ------------------------------------------------------------------
    # 文本截断
    # ------------------------------------------------------------------
    def _ellipsize(self, text: str, max_width: float) -> str:
        """把过长的条目文字截断成 ``abc…``。

        :param text: 原始文字
        :param max_width: 可用的像素宽度
        :returns: 能放下的文本（放得下时原样返回）

        Tk 画布没有裁剪概念，超长文本会直接糊到控件外面去。这里用一个
        临时的离屏 text item 逐次二分测量；结果按 ``(文字, 宽度)`` 缓存，
        长列表反复重绘时不会重复测量。

        .. note::
           画布尚未映射时 :meth:`tkinter.Canvas.bbox` 拿不到度量，
           这时原样返回、不做截断（宁可溢出也不要显示成空）。
        """
        if not text:
            return text
        if max_width <= 8:
            return text

        key = (text, int(max_width))
        cached = self._text_cache.get(key)
        if cached is not None:
            return cached

        if not self._can_measure():
            return text

        result = self._measure_and_truncate(text, max_width)
        if len(self._text_cache) < _TEXT_CACHE_LIMIT:
            self._text_cache[key] = result
        return result

    def _can_measure(self):
        """画布当前是否能给出文字度量。

        未映射的窗口里 ``bbox`` 一律返回 ``None``（没有显示环境可量），
        这时不做截断——宁可让文字溢出，也不要把它显示成空。
        """
        try:
            return bool(self.bbox(self.element_border))
        except Exception:
            return False

    def _measure_and_truncate(self, text, max_width):
        """用离屏 text item 二分出最长的可显示前缀。"""
        marker = "…"
        try:
            probe = self.create_text(
                -10000, -10000, anchor="w", text=text, font=self.attributes.font
            )
        except Exception:
            return text

        try:
            if self._text_width(probe, text) <= max_width:
                return text
            low, high = 0, len(text)
            while low < high:
                middle = (low + high + 1) // 2
                candidate = text[:middle] + marker
                if self._text_width(probe, candidate) <= max_width:
                    low = middle
                else:
                    high = middle - 1
            if low <= 0:
                return marker
            return text[:low] + marker
        finally:
            try:
                self.delete(probe)
            except Exception:
                pass

    def _text_width(self, probe, text):
        """量一段文字在画布上的像素宽度。"""
        self.itemconfigure(probe, text=text)
        box = self.bbox(probe)
        if not box:
            return 0
        return box[2] - box[0]

    # ------------------------------------------------------------------
    # 事件
    # ------------------------------------------------------------------
    def _event_on_button1(self, event: Optional[Event] = None):
        """左键按下：点在滑块上 → 拖滚动条；点在行上 → 改选择。"""
        if self.attributes.state == "disabled":
            return

        if event is not None and self._hit_scrollbar(event.x, event.y):
            self.focus_set()
            self._begin_thumb_drag(event)
            super()._event_on_button1(event)
            return

        if event is not None:
            position = self._row_at(event.y)
            if position is not None:
                self.focus_set()
                self._apply_click_selection(position, event)

        super()._event_on_button1(event)

    def _event_off_button1(self, event: Optional[Event] = None):
        """左键松开：结束滑块拖拽。"""
        self._drag = None
        super()._event_off_button1(event)

    def _event_drag(self, event: Optional[Event] = None):
        """左键拖动：拖滑块时按比例滚动。"""
        if self._drag is None or event is None:
            return
        geometry = self._scrollbar_geometry()
        if geometry is None:
            return
        _track, thumb = geometry
        span = max(1.0, (thumb[3] - thumb[1]))
        travel = (event.y - self._drag["y"]) / span
        target = self._drag["offset"] + travel * max(1, self._max_offset())
        self._offset = int(round(target))
        self._clamp_offset()
        self._draw()

    def _event_motion(self, event: Optional[Event] = None):
        """鼠标移动：更新悬停行（只有真的换了行才重绘）。"""
        if self.attributes.state == "disabled":
            return
        if self._drag is not None:
            return
        position = self._row_at(event.y) if event is not None else None
        if position != self._hover_index:
            self._hover_index = position
            self._draw()

    def _event_leave(self, event: Optional[Event] = None):
        """鼠标离开 → 清掉悬停行。"""
        self._hover_index = None
        super()._event_leave(event)

    def _event_double_click(self, event: Optional[Event] = None):
        """双击 → 激活该行。"""
        if event is None:
            return
        position = self._row_at(event.y)
        if position is not None:
            self.activate(position)

    def _event_wheel(self, event: Optional[Event] = None):
        """滚轮 → 上下滚动。

        Windows / macOS 走 ``<MouseWheel>``（``delta`` 为 ±120 的倍数），
        X11 走 ``<Button-4>`` / ``<Button-5>``（没有 ``delta``）。
        """
        if event is None:
            return
        if getattr(event, "num", None) == 4:
            steps = -3
        elif getattr(event, "num", None) == 5:
            steps = 3
        else:
            delta = getattr(event, "delta", 0) or 0
            if delta == 0:
                return
            magnitude = max(1, abs(int(delta)) // 120)
            steps = -3 * magnitude if delta > 0 else 3 * magnitude
        self.scroll(steps)

    def _begin_thumb_drag(self, event):
        """记录拖拽起点，用于 :meth:`_event_drag` 换算偏移。"""
        geometry = self._scrollbar_geometry()
        if geometry is None:
            self._drag = None
            return
        _track, thumb = geometry
        self._drag = {"y": event.y, "offset": self._offset, "thumb": thumb}

    def _apply_click_selection(self, position: int, event):
        """按修饰键与 ``selectmode`` 决定这次点击如何改选择。"""
        state = int(getattr(event, "state", 0) or 0)
        ctrl = bool(state & 0x0004)
        shift = bool(state & 0x0001)

        if self.selectmode == "single":
            self._selected = {position}
        elif self.selectmode == "multiple":
            if position in self._selected:
                self._selected.discard(position)
            else:
                self._selected.add(position)
        else:  # extended
            if shift and self._anchor is not None:
                low, high = sorted((self._anchor, position))
                self._selected |= set(range(low, high + 1))
            elif ctrl:
                if position in self._selected:
                    self._selected.discard(position)
                else:
                    self._selected.add(position)
                self._anchor = position
            else:
                self._selected = {position}
                self._anchor = position

        if not shift:
            self._anchor = position
        self.see(position)
        self._notify_selection()
