"""单选框组件。

``FluRadioBox`` 是 Fluent / WinUI3 风格的单选框：左边一个圆环（选中时里面
多一个实心圆点），右边是标签文字。同一组里**最多只有一个**能被选中。

两种分组写法
------------
1. **共享变量**（与 ``tkinter`` / ``ttk.Radiobutton`` 一致，推荐）::

       import tkinter as tk
       import tkflu

       root = tkflu.FluWindow()
       choice = tk.StringVar(master=root, value="b")

       for key, title in (("a", "方案 A"), ("b", "方案 B"), ("c", "方案 C")):
           tkflu.FluRadioBox(root, text=title, variable=choice, value=key).pack(
               anchor="w", padx=14, pady=4
           )

       print(choice.get())      # 'b'

2. **组名**（写起来更短，适合不想自己建变量的场合）::

       tkflu.FluRadioBox(root, text="方案 A", group="plan", value="a")
       tkflu.FluRadioBox(root, text="方案 B", group="plan", value="b")

   ``group`` 会把同一个窗口（Toplevel）内同名的单选框绑到同一个共享变量上，
   窗口销毁时自动回收。

取值比较
--------
Tk 变量内部一律是字符串，因此判断"这个单选框是否选中"用的是
``str(variable.get()) == str(value)``。这既是 Tk 一贯的语义，也避免了
``IntVar`` 与字符串 ``value`` 混用时"看起来选了但没高亮"的坑。

回调
----
``command`` 在**用户操作导致选中状态变化**时触发，不带参数；
需要新值请读 ``widget.dcget("checked")`` 或 ``variable.get()``。
用代码调 :meth:`FluRadioBox.set_checked` 也会触发 ``command``
（与点一下按钮等价）；只想改状态、不要回调时传 ``notify=False``。
"""

from __future__ import annotations

from typing import Callable, Optional, Union

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .constants import MODE, STATE
from .designs.radiobox import RING_WIDTH
from .designs.radiobox import radiobox as radiobox_design

__all__ = ["FluRadioBox", "FluRadioBoxCanvas", "FluRadioBoxDraw"]


class FluRadioBoxDraw(DSvgDraw):
    """单选框的 SVG 绘制后端。"""


class FluRadioBoxCanvas(DCanvas):
    """单选框的画布。

    圆环就是把圆角半径取成"外径的一半"的圆角矩形——SVG 与三个栅格引擎
    都会把半径夹到半个边长，因此拿到的就是一个正圆。这样单选框不需要
    任何新图元，五个引擎的画面完全一致。
    """

    draw = FluRadioBoxDraw


from tkinter import Event  # noqa: E402

from .defs import call_command, measure_label_width, set_default_font  # noqa: E402
from .tooltip import FluToolTipBase  # noqa: E402

#: ``group="..."`` 用到的共享变量登记表。
#: 键是 ``(窗口路径, 组名)``，值是 ``[StringVar, 引用计数]``。
#: 引用计数归零时条目会被删掉，因此不会随窗口开关无限增长。
_GROUP_VARS = {}


def _resolve_master(args, kwargs):
    """从构造参数里找出 Tk 主控件。"""
    if "master" in kwargs:
        return kwargs["master"]
    if args:
        return args[0]
    import tkinter

    return tkinter._default_root


def _acquire_group_variable(master, group):
    """取得（必要时创建）组名对应的共享变量。

    :param master: 任意 Tk 控件，用于定位所属窗口
    :param group: 组名
    :returns: ``(键, StringVar)``；键用于销毁时释放
    """
    import tkinter

    toplevel = master.winfo_toplevel() if hasattr(master, "winfo_toplevel") else master
    key = (str(toplevel), str(group))
    entry = _GROUP_VARS.get(key)
    if entry is None:
        entry = [tkinter.StringVar(master=toplevel), 0]
        _GROUP_VARS[key] = entry
    entry[1] += 1
    return key, entry[0]


def _release_group_variable(key):
    """释放一次组名变量的引用；归零时连同条目一起删除。"""
    entry = _GROUP_VARS.get(key)
    if entry is None:
        return
    entry[1] -= 1
    if entry[1] <= 0:
        _GROUP_VARS.pop(key, None)


class FluRadioBox(FluRadioBoxCanvas, DDrawWidget, FluToolTipBase):
    """Fluent 风格的单选框。

    :cvar BOX: 圆环外径（像素）
    :cvar GAP: 圆环与标签之间的间距
    :cvar PADDING: 控件左右两侧的内边距
    """

    #: 圆环外径
    BOX = 20
    #: 圆环与文字之间的间距
    GAP = 8
    #: 控件左右两侧的内边距
    PADDING = 6

    def __init__(
        self,
        *args,
        text: str = "",
        value=None,
        variable=None,
        group: Optional[str] = None,
        checked: Optional[bool] = None,
        command: Optional[Callable] = None,
        font=None,
        mode: MODE = "light",
        state: STATE = "normal",
        width: Optional[Union[int, float]] = None,
        height: Union[int, float] = 32,
        **kwargs,
    ) -> None:
        """构造单选框。

        :param args: 透传给 :class:`tkinter.Canvas.__init__`
        :param text: 标签文字
        :param value: 本项在被选中时写进 ``variable`` 的值
        :param variable: 共享的 Tk 变量（``StringVar`` / ``IntVar`` …）；
            与同一变量的其它单选框自动互斥
        :param group: 组名；没有 ``variable`` 时按它取一个窗口内共享的变量
        :param checked: 初始是否选中。默认 ``None`` 表示"由变量决定"——
            变量的值等于 ``value`` 时即选中
        :param command: 选中状态变化后的回调，不带参数
        :param font: 自定义字体
        :param mode: ``"light"`` / ``"dark"``
        :param state: ``"normal"`` / ``"disabled"``
        :param width: 控件宽度；``None`` 表示按文字自适应（只增不减）
        :param height: 控件高度，默认 32
        :param kwargs: 其余参数透传给 :class:`tkinter.Canvas.__init__`

        :raises ValueError: 同时传了 ``variable`` 和 ``group``
        """
        if variable is not None and group is not None:
            raise ValueError("variable 与 group 只能二选一")

        self.value = value
        self._group_key = None
        if variable is None and group is not None:
            master = _resolve_master(args, kwargs)
            if master is not None:
                self._group_key, variable = _acquire_group_variable(master, group)
        self._variable = variable

        self._init(mode, state, checked)

        #: 调用方显式指定的宽度；``None`` 表示"按文本自适应"
        self._fixed_width = width

        super().__init__(
            *args,
            width=self._initial_width(args, kwargs, text, width),
            height=height,
            **kwargs,
        )

        self.dconfigure(text=text, command=command)
        set_default_font(font, self.attributes, master=self)

        self._trace_id = None
        self._syncing = False
        self.configure(takefocus=1)

        if variable is not None:
            self._sync_from_variable()
            try:
                self._trace_id = variable.trace_add("write", self._on_variable_write)
            except Exception:
                self._trace_id = None

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.invoke(), add="+")
        self.bind("<space>", lambda event=None: self.invoke(), add="+")
        self.bind("<Return>", lambda event=None: self.invoke(), add="+")
        self.bind("<Destroy>", self._event_destroy_radio, add="+")

    # ------------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------------
    def _initial_width(self, args, kwargs, text, width):
        """创建画布之前先算出一个合理的初始宽度。"""
        if width is not None:
            return width
        return self._needed_width(_resolve_master(args, kwargs), text)

    def _needed_width(self, master, text):
        """按当前文字算出控件需要多宽。"""
        width = self.PADDING * 2 + self.BOX
        if text:
            width += self.GAP + measure_label_width(master, text, padding=0)
        return int(width)

    def _init(self, mode, state, checked):
        """建立属性字典（此时还没有 Tk 画布，不能碰任何 Tk 调用）。"""
        from easydict import EasyDict

        self.enter = False
        self.button1 = False
        self.isfocus = False

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "state": "normal",
                "checked": bool(checked),
                # 下面这组由 designs.radiobox 填充
                "back_color": None,
                "back_opacity": 0.0,
                "border_color": None,
                "border_color_opacity": 1.0,
                "border_width": RING_WIDTH,
                "text_color": "#1b1b1b",
                "dot_color": None,
                "dot_ratio": 0.5,
                "focus_color": "#000000",
                "focus_opacity": 0.0,
            }
        )

        if checked is not None:
            self.attributes.checked = bool(checked)
        self.attributes.state = state
        self.mode = mode
        self._apply_design()

    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------
    def theme(self, mode=None, state=None):
        """切换主题 / 状态配色。

        :param mode: ``"light"`` / ``"dark"``；省略表示沿用当前值
        :param state: 交互状态；省略表示沿用当前值
        """
        if mode:
            self.mode = mode
        if state:
            self.attributes.state = state
        self._apply_design()

    def _apply_design(self):
        """按 ``(mode, 交互状态, 勾选态)`` 刷新配色。"""
        design = radiobox_design(
            getattr(self, "mode", "light"),
            self._visual_state(),
            self.attributes.checked,
        )
        self.dconfigure(design)

    def _visual_state(self):
        """把交互状态位归并成设计规范认识的状态名。"""
        if self.attributes.state == "disabled":
            return "disabled"
        return self.interaction_state()

    # ------------------------------------------------------------------
    # 分组 / 变量同步
    # ------------------------------------------------------------------
    @property
    def variable(self):
        """本单选框绑定的 Tk 变量（没绑定时为 ``None``）。"""
        return self._variable

    def _on_variable_write(self, *_args):
        """共享变量被改动（可能是别的单选框改的）→ 跟着刷新。"""
        if self._syncing:
            return
        self._sync_from_variable(notify=True)

    def _sync_from_variable(self, notify: bool = False):
        """按共享变量当前的值刷新 ``checked``。

        :param notify: 本项**被选中**时是否触发 ``command``

        .. note::
           只有"变成选中"才会通知，**取消选中不会**。同一个组里换选另一项时，
           变量写入会让旧项的监听也回调一次；如果取消选中也发 ``command``，
           用户点一次会收到两条回调（旧项 + 新项），而且旧项那条几乎肯定
           不是他想要的。
        """
        if self._variable is None:
            return
        try:
            current = self._variable.get()
        except Exception:
            return
        checked = str(current) == str(self.value)
        if checked == self.attributes.checked:
            return
        self.attributes.checked = checked
        self._apply_design()
        self._draw()
        if notify and checked:
            call_command(self.attributes.command)

    # ------------------------------------------------------------------
    # 选中状态
    # ------------------------------------------------------------------
    @property
    def checked(self):
        """当前是否被选中。"""
        return bool(self.attributes.checked)

    @checked.setter
    def checked(self, value):
        self.set_checked(value)

    def set_checked(self, checked: bool = True, notify: bool = False):
        """直接设置选中状态。

        :param checked: ``True`` 选中；``False`` 取消选中
        :param notify: 是否触发 ``command``，默认 ``False``

        绑定变量时，选中会把变量写成 ``value``；取消选中则把变量写成
        空字符串（Tk 的惯用做法：谁都不选），从而让同组的其它单选框
        一起取消高亮。
        """
        checked = bool(checked)
        changed = checked != bool(self.attributes.checked)

        if self._variable is not None:
            self._syncing = True
            try:
                self._variable.set(self.value if checked else "")
            except Exception:
                pass
            finally:
                self._syncing = False

        self.attributes.checked = checked
        self._apply_design()
        self._draw()

        if notify and changed:
            call_command(self.attributes.command)

    def select(self, notify: bool = False):
        """选中本项。"""
        self.set_checked(True, notify=notify)

    def deselect(self, notify: bool = False):
        """取消选中本项。"""
        self.set_checked(False, notify=notify)

    def invoke(self):
        """走一遍"用户点击"的完整流程。

        已经是选中状态时不做任何事（单选框不能靠再点一下取消，
        这是 Windows 的行为）；这样也避免重复点选时反复触发 ``command``。
        """
        if self.attributes.state == "disabled":
            return
        self.focus_set()
        if self.attributes.checked:
            return
        self.set_checked(True, notify=True)

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------
    def _draw(self, event: Optional[Event] = None):
        """把单选框画出来（焦点环 + 圆环 + 圆点 + 标签）。"""
        super()._draw(event)

        # 与 FluCheckBox 同理：每次重绘都按当前状态重算配色，这样
        # ``dconfigure(state=...)`` 与 hover/按压都能立刻反映出来。
        self._apply_design()

        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        from .designs.renderer import get_renderer

        if get_renderer() == 1:
            width -= 1
            height -= 1

        box_x = self.PADDING
        box_y = (height - self.BOX) / 2.0
        radius = self.BOX / 2.0

        if self.isfocus and self.attributes.focus_opacity:
            self._draw_focus_ring(box_x, box_y, radius)

        self.element_ring = self.draw_roundrect(
            box_x,
            box_y,
            box_x + self.BOX,
            box_y + self.BOX,
            radius,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=self.attributes.back_color,
            fill_opacity=self.attributes.back_opacity,
            outline=self.attributes.border_color,
            outline_opacity=self.attributes.border_color_opacity,
            width=self.attributes.border_width,
        )

        self._draw_dot(box_x, box_y, radius)
        self._draw_label(box_x, height)
        self._fit_to_text()

    def _draw_focus_ring(self, box_x, box_y, radius):
        """在圆环外侧画一圈焦点环。"""
        pad = 2.0
        self.element_focus = self.draw_roundrect(
            box_x - pad,
            box_y - pad,
            box_x + self.BOX + pad,
            box_y + self.BOX + pad,
            radius + pad,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill="transparent",
            fill_opacity=0.0,
            outline=self.attributes.focus_color,
            outline_opacity=self.attributes.focus_opacity,
            width=2,
        )

    def _draw_dot(self, box_x, box_y, radius):
        """画中间的实心圆点（未选中时不画）。"""
        dot_color = self.attributes.dot_color
        if not dot_color:
            self.element_dot = None
            return

        dot_radius = radius * float(self.attributes.dot_ratio or 0.5)
        center_x = box_x + self.BOX / 2.0
        center_y = box_y + self.BOX / 2.0
        self.element_dot = self.draw_roundrect(
            center_x - dot_radius,
            center_y - dot_radius,
            center_x + dot_radius,
            center_y + dot_radius,
            dot_radius,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=dot_color,
            fill_opacity=1.0,
            outline=None,
            outline_opacity=0.0,
            width=0,
        )

    def _draw_label(self, box_x, height):
        """画右侧标签。"""
        self.element_text = self.create_text(
            box_x + self.BOX + self.GAP,
            height / 2.0,
            anchor="w",
            fill=self.attributes.text_color,
            text=self.attributes.text,
            font=self.attributes.font,
        )

    def _fit_to_text(self):
        """文字比控件宽时把控件加宽（只增不减，避免反复触发重排）。"""
        if self._fixed_width is not None:
            return
        if not getattr(self, "element_text", None):
            return

        try:
            bbox = self.bbox(self.element_text)
        except Exception:
            return
        if not bbox:
            return

        needed = self.PADDING * 2 + self.BOX + self.GAP + int(bbox[2] - bbox[0])
        if needed > self.winfo_reqwidth():
            self.config(width=needed)

    # ------------------------------------------------------------------
    # 事件
    # ------------------------------------------------------------------
    def _event_on_button1(self, event=None):
        """左键按下：禁用时不进入按压态。"""
        if self.attributes.state == "disabled":
            return
        super()._event_on_button1(event)

    def _event_off_button1(self, event=None):
        """左键松开：禁用时不发 ``<<Clicked>>``。"""
        if self.attributes.state == "disabled":
            return
        super()._event_off_button1(event)

    def _event_destroy_radio(self, event=None):
        """销毁时摘掉变量监听并释放组名引用。"""
        if event is not None and getattr(event, "widget", None) is not self:
            return
        if getattr(self, "_trace_id", None) is not None and self._variable is not None:
            try:
                self._variable.trace_remove("write", self._trace_id)
            except Exception:
                pass
            self._trace_id = None
        if getattr(self, "_group_key", None) is not None:
            _release_group_variable(self._group_key)
            self._group_key = None
        self._variable = None
