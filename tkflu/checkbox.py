"""复选框组件。

``FluCheckBox`` 是 Fluent / WinUI3 风格的复选框：左边一个 20×20 的圆角方框，
右边是标签文字。

三种勾选状态
------------
与 Windows 一致，``checked`` 允许 ``True`` / ``False`` / ``None``：

====================== ==========================================
``dcget("checked")``   外观
====================== ==========================================
``False``              空的方框
``True``               强调色填充 + 勾号
``None``               强调色填充 + 横杠（不确定态）
====================== ==========================================

构造时传 ``three_state=True``，点击就会在这三种状态间循环
（``False`` → ``True`` → ``None`` → ``False``）。

.. code-block:: python

    import tkflu

    root = tkflu.FluWindow()
    box = tkflu.FluCheckBox(root, text="启用动画", checked=True)
    box.pack(padx=12, pady=8)

    def on_click():
        print("当前：", box.dcget("checked"))

    box.dconfigure(command=on_click)
    root.mainloop()

键盘
----
控件可以用 ``Tab`` 聚焦；聚焦后按 ``空格`` 切换（与 Windows 的复选框一致），
此时方框外侧会画一圈焦点环。
"""

from __future__ import annotations

from typing import Callable, Optional, Union

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .constants import MODE, STATE
from .designs.checkbox import CHECK_GLYPH as GLYPH_CHECK
from .designs.control import (
    FOCUS_INNER_WIDTH,
    FOCUS_MARGIN,
    FOCUS_OUTER_WIDTH,
    FOCUS_RADIUS,
)
from .designs.checkbox import checkbox as checkbox_design

__all__ = ["FluCheckBox", "FluCheckBoxCanvas", "FluCheckBoxDraw"]


class FluCheckBoxDraw(DSvgDraw):
    """复选框的 SVG 绘制后端。

    方框直接用 :meth:`tkdeft.windows.draw.DSvgDraw.create_roundrect`
    （几何内缩半个线宽，四边描边完整），勾号是画布上的线段，
    因此这里不需要额外的图元实现。
    """


class FluCheckBoxCanvas(DCanvas):
    """复选框的画布。

    除了换掉绘制后端之外不做别的事——"先试栅格快速路径、失败再回退 SVG"
    已经收敛在 :meth:`tkdeft.windows.canvas.DCanvas.draw_roundrect` 里。
    """

    draw = FluCheckBoxDraw


from tkinter import Event  # noqa: E402  （放在画布定义之后，保持文件阅读顺序）

from .defs import call_command, measure_label_width, set_default_font  # noqa: E402
from .tooltip import FluToolTipBase  # noqa: E402


def _resolve_master(args, kwargs):
    """从构造参数里找出 Tk 主控件（用于在创建画布前测量文字宽度）。"""
    if "master" in kwargs:
        return kwargs["master"]
    if args:
        return args[0]
    import tkinter

    return tkinter._default_root


class FluCheckBox(FluCheckBoxCanvas, DDrawWidget, FluToolTipBase):
    """Fluent 风格的复选框。

    :cvar BOX: 方框边长（像素）
    :cvar GAP: 方框与标签之间的间距
    :cvar PADDING: 控件左右两侧的内边距
    """

    #: 方框边长
    BOX = 20
    #: 方框与文字之间的间距
    GAP = 8
    #: 控件左/右内边距。
    #: Figma 设计稿里三个实例的框都是「控件左边缘 + 4」——
    #: ``120x32 @x=538`` → 方框 ``20x20 @x=542``，另两组是 680→684、989→993。
    PADDING = 4
    #: 勾号字号（WinUI 模板里 CheckGlyph 是 FontSize="12"）
    GLYPH_FONT_SIZE = 12
    #: 勾号相对方框中心的微调。实测（8 倍放大后量墨迹包围盒）图标字体的
    #: 字形单元格在 ``anchor="center"`` 下正好居中，所以这里是 0。
    GLYPH_OFFSET_Y = 0
    #: 不确定态横杠的尺寸。设计稿里是 ``Dash12`` 这个部件，
    #: 实测包围盒 **8.0 × 1.0**、端头半径 0.5、位于方框内 (6.0, 9.5)。
    DASH_WIDTH = 8
    DASH_HEIGHT = 1

    def __init__(
        self,
        *args,
        text: str = "",
        checked: Optional[bool] = False,
        command: Optional[Callable] = None,
        font=None,
        mode: MODE = "light",
        state: STATE = "normal",
        three_state: bool = False,
        width: Optional[Union[int, float]] = None,
        height: Union[int, float] = 32,
        **kwargs,
    ) -> None:
        """构造复选框。

        :param args: 透传给 :class:`tkinter.Canvas.__init__`
        :param text: 标签文字
        :param checked: 初始勾选状态；``True`` / ``False`` / ``None``（不确定态）
        :param command: 状态变化后触发的回调，**不带参数**（需要新状态请读
            ``dcget("checked")``）
        :param font: 自定义字体；``None`` 时用库默认的 Segoe UI
        :param mode: ``"light"`` / ``"dark"``
        :param state: ``"normal"`` / ``"disabled"``
        :param three_state: 是否允许"不确定态"参与点击循环
        :param width: 控件宽度；``None`` 表示按文字自适应（只增不减）
        :param height: 控件高度，默认 32（Fluent 的触控目标高度）
        :param kwargs: 其余参数透传给 :class:`tkinter.Canvas.__init__`

        .. note::
           ``command`` 在**鼠标点击与空格键**之后都会触发。它不带参数；
           想知道新状态请读 ``dcget("checked")``。
        """
        self.three_state = bool(three_state)
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

        self.configure(takefocus=1)
        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.invoke(), add="+")
        self.bind("<space>", lambda event=None: self.invoke(), add="+")
        self.bind("<Return>", lambda event=None: self.invoke(), add="+")

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
                "checked": False,
                # 下面这组由 designs.checkbox 填充
                "back_color": None,
                "back_opacity": 0.0,
                "border_color": None,
                "border_color_opacity": 0.0,
                "border_width": 1,
                "radius": 4,
                "text_color": "#1b1b1b",
                "glyph_color": None,
                "glyph": "none",
                "focus_color": "#000000",
                "focus_opacity": 0.0,
                "focus_inner_color": "#ffffff",
                "focus_inner_opacity": 1.0,
            }
        )

        self.attributes.checked = checked
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

        .. note::
           这里**不接收** ``style`` 参数（复选框没有标准/强调之分），
           但签名与其它组件保持一致，方便 :class:`~tkflu.thememanager.FluThemeManager`
           用同一套递归调用。
        """
        if mode:
            self.mode = mode
        if state:
            self.attributes.state = state
        self._apply_design()

    def _apply_design(self):
        """按 ``(mode, 交互状态, 勾选态)`` 刷新配色。"""
        design = checkbox_design(
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
    # 勾选状态
    # ------------------------------------------------------------------
    @property
    def checked(self):
        """当前勾选状态（``True`` / ``False`` / ``None``）。"""
        return self.attributes.checked

    @checked.setter
    def checked(self, value):
        self.set_checked(value)

    def set_checked(self, value, redraw: bool = True):
        """直接设置勾选状态（**不触发** ``command``）。

        :param value: ``True`` / ``False`` / ``None``
        :param redraw: 是否立即重绘，默认 ``True``
        """
        self.attributes.checked = value
        self._apply_design()
        if redraw:
            self._draw()

    def next_checked(self):
        """算出"点一下之后"的状态。

        :returns: 单态复选框返回取反结果；三态复选框按
            ``False`` → ``True`` → ``None`` → ``False`` 循环
        """
        current = self.attributes.checked
        if not self.three_state:
            return not current
        if current is False:
            return True
        if current is True:
            return None
        return False

    def toggle(self):
        """切换勾选状态并重绘（**不触发** ``command``）。"""
        self.set_checked(self.next_checked())

    def invoke(self):
        """走一遍"用户点击"的完整流程：切换状态 → 重绘 → 触发 ``command``。

        禁用状态下什么都不做。
        """
        if self.attributes.state == "disabled":
            return
        self.focus_set()
        self.toggle()
        call_command(self.attributes.command)

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------
    def _box_origin(self, width=None, height=None):
        """方框左上角在画布坐标系里的位置。"""
        width = self.winfo_width() if width is None else width
        height = self.winfo_height() if height is None else height
        return self.PADDING, (height - self.BOX) / 2.0

    def _draw(self, event: Optional[Event] = None):
        """把复选框整个画出来（焦点环 + 方框 + 勾号 + 标签）。"""
        super()._draw(event)

        # 每次重绘都按当前状态重算配色。这样 ``dconfigure(state="disabled")``
        # 以及 hover/按压的切换都能立刻反映出来，不需要调用方额外调 theme()。
        self._apply_design()

        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        from .designs.renderer import get_renderer

        if get_renderer() == 1:
            # wand 引擎在位图边缘会多算一个像素，历史组件都按这个约定补偿
            width -= 1
            height -= 1

        box_x, box_y = self._box_origin(width, height)
        radius = self.attributes.radius

        if self.isfocus and self.attributes.focus_opacity:
            self._draw_focus_ring(box_x, box_y, radius, width, height)

        self.element_box = self.draw_roundrect(
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

        self._draw_glyph(box_x, box_y)

        self.element_text = self.create_text(
            box_x + self.BOX + self.GAP,
            height / 2.0,
            anchor="w",
            fill=self.attributes.text_color,
            text=self.attributes.text,
            font=self.attributes.font,
        )

        self._fit_to_text()

    def _draw_focus_ring(self, box_x, box_y, radius, width=None, height=None):
        """画焦点带：**贴着整个控件外沿的 3px 两层带**。

        设计稿里 ``Focus Inner`` / ``Focus Outer`` 的包围盒是 126×38，
        而控件本身是 120×32 —— 也就是紧贴控件外沿、外扩 3px，没有间隙。
        两层叠出来的可见结果是「外 2px 深色 + 内 1px 浅色」：
        先铺 3px 的"内色"，再在上面盖 2px 的"外色"。
        """
        width = self.winfo_width() if width is None else width
        height = self.winfo_height() if height is None else height
        margin = FOCUS_MARGIN
        self.element_focus = self.draw_roundrect(
            -margin,
            -margin,
            width + margin,
            height + margin,
            FOCUS_RADIUS,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill="transparent",
            fill_opacity=0.0,
            outline=self.attributes.focus_inner_color,
            outline_opacity=self.attributes.focus_inner_opacity,
            width=FOCUS_INNER_WIDTH + FOCUS_OUTER_WIDTH,
        )
        self.element_focus_inner = self.draw_roundrect(
            -margin,
            -margin,
            width + margin,
            height + margin,
            FOCUS_RADIUS,
            temppath=self.temppath2,
            temppath2=self.temppath4,
            fill="transparent",
            fill_opacity=0.0,
            outline=self.attributes.focus_color,
            outline_opacity=self.attributes.focus_opacity,
            width=FOCUS_OUTER_WIDTH,
        )

    def _draw_glyph(self, box_x, box_y):
        """画勾号（不确定态画横杠）。

        **勾号用内嵌的 Segoe Fluent Icons 字形 ``\\uE73E``**，不用手画的折线。

        为什么：WinUI 的 CheckBox 模板里，勾号是一个
        ``FontIcon Glyph="&#xE73E;" FontSize="12"``——它的轮廓是字体给的，
        笔画细、端点略带斜切。自己用 ``create_line`` 拼折线，无论怎么调都会
        显得又粗又大、和 Windows 对不上。这个字体本来就随包分发
        （``tkflu/designs/fonts/segoe_fluent_icons.ttf``），不用白不用。

        不确定态则照抄模板里的 ``Rectangle Width="10" Height="2"
        RadiusX="1" RadiusY="1"``：一个 10×2 的圆角矩形。
        """
        glyph = self.attributes.glyph
        if glyph == "none" or not self.attributes.glyph_color:
            self.element_glyph = None
            return

        center_x = box_x + self.BOX / 2.0
        center_y = box_y + self.BOX / 2.0

        if glyph == "dash":
            half_w = self.DASH_WIDTH / 2.0
            half_h = self.DASH_HEIGHT / 2.0
            self.element_glyph = self.draw_roundrect(
                center_x - half_w,
                center_y - half_h,
                center_x + half_w,
                center_y + half_h,
                half_h,
                temppath=self.temppath2,
                temppath2=self.temppath4,
                fill=self.attributes.glyph_color,
                fill_opacity=1.0,
                outline=None,
                outline_opacity=0.0,
                width=0,
            )
            return

        font = self._icon_font()
        if font is None:
            # 拿不到真正的图标字体：退回手画折线，总比画一个"豆腐块"强
            self._draw_glyph_fallback(box_x, box_y)
            return

        self.element_glyph = self.create_text(
            center_x,
            center_y + self.GLYPH_OFFSET_Y,
            anchor="center",
            text=GLYPH_CHECK,
            fill=self.attributes.glyph_color,
            font=font,
        )

    def _icon_font(self):
        """勾号用的图标字体（按控件自己的解释器创建，惰性缓存）。

        :returns: 可用的图标字体对象；**拿不到真正的 Segoe Fluent Icons 时返回
            ``None``**（调用方退回手画折线）。字体包精简 / 加载失败的机器上，
        Tk 会安静地退回默认字体——那样画出来是个"豆腐块"，比手画的折线还难看。
        """
        if not self.__dict__.get("_glyph_font_ready"):
            font = None
            try:
                from .designs.fonts import SegoeFluentIcons

                # master=self 不能省：字体是按 Tk 解释器注册的，不传就挂到默认根
                # 窗口，同进程的第二个窗口会认不出这个名字（见 designs/fonts）。
                candidate = SegoeFluentIcons(
                    size=self.GLYPH_FONT_SIZE, master=self
                )
                family = str(candidate.actual().get("family", ""))
                if family == "Segoe Fluent Icons":
                    font = candidate
            except Exception:
                font = None
            self.__dict__["_glyph_font"] = font
            self.__dict__["_glyph_font_ready"] = True
        return self.__dict__.get("_glyph_font")

    def _draw_glyph_fallback(self, box_x, box_y):
        """手画折线版的勾号（只在图标字体不可用时使用）。"""
        points = (
            (0.26, 0.53),
            (0.44, 0.70),
            (0.75, 0.32),
        )
        flat = []
        for fx, fy in points:
            flat.extend((box_x + self.BOX * fx, box_y + self.BOX * fy))
        self.element_glyph = self.create_line(
            *flat,
            fill=self.attributes.glyph_color,
            width=2,
            capstyle="round",
            joinstyle="round",
            smooth=False,
        )

    def _fit_to_text(self):
        """文字比控件宽时把控件加宽（只增不减，避免反复触发重排）。

        只在调用方**没有**显式指定 ``width`` 时生效。
        """
        if self._fixed_width is not None:
            return
        if not getattr(self, "element_text", None):
            return

        try:
            bbox = self.bbox(self.element_text)
        except Exception:
            return
        if not bbox:
            return  # 尚未映射，量不到

        needed = self.PADDING * 2 + self.BOX + self.GAP + int(bbox[2] - bbox[0])
        if needed > self.winfo_reqwidth():
            self.config(width=needed)
