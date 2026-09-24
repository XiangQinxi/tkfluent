"""徽标组件。

``FluBadge`` 是一个胶囊形的小标签，通常用来显示状态、计数或分类。
支持 ``standard`` / ``accent`` 两种样式，以及 ``light`` / ``dark`` 两种主题。"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.badge import badge


class FluBadgeDraw(DSvgDraw):
    """徽标的 SVG 绘制后端。

    badge 的形状（rx=20 / ry=25 的胶囊形）由 :class:`FluBadgeCanvas` 决定，
    这里不再重复实现圆角矩形——通用实现来自
    :meth:`tkdeft.windows.draw.DSvgDraw.create_roundrect`：几何会自动内缩
    半个线宽，四边描边才完整（旧写法用 ``translate(0.5,0.5)`` 会丢掉下/右边框）。
    """


class FluBadgeCanvas(DCanvas):
    draw = FluBadgeDraw

    #: badge 固定使用的胶囊形圆角（x / y 两个方向）
    RADIUS_X = 20
    RADIUS_Y = 25

    def create_round_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        temppath=None,
        temppath2=None,
        **kwargs,
    ) -> int:
        """画徽标背景（固定胶囊形圆角）。

        :param x1: 左上角 x
        :param y1: 左上角 y
        :param x2: 右下角 x
        :param y2: 右下角 y
        :param temppath: SVG 兜底路径用的临时文件
        :param temppath2: Wand 引擎的 PNG 输出路径
        :param kwargs: ``fill`` / ``fill_opacity`` / ``outline`` /
            ``outline_opacity`` / ``width`` 等，透传给
            :meth:`tkdeft.windows.canvas.DCanvas.draw_roundrect`
        :returns: 画布上的 item id

        与旧实现相比，这里不再手写"先试栅格快速路径、失败再回退 SVG"：
        那套判定已经收敛到 tkdeft 的 ``draw_roundrect`` 里。
        """
        return self.draw_roundrect(
            x1,
            y1,
            x2,
            y2,
            self.RADIUS_X,
            self.RADIUS_Y,
            temppath=temppath,
            temppath2=temppath2,
            **kwargs,
        )

    create_roundrect = create_round_rectangle

    def draw_roundrect_svg(self, *args, **kwargs) -> int:
        """SVG 兜底：给矩形补上 ``id=".Badge"``（与设计稿导出的 SVG 一致）。"""
        kwargs.setdefault("id", ".Badge")
        return super().draw_roundrect_svg(*args, **kwargs)


from .tooltip import FluToolTipBase


class FluBadge(FluBadgeCanvas, DDrawWidget, FluToolTipBase):

    def __init__(
        self,
        *args,
        text="",
        width=70,
        height=30,
        font=None,
        mode="light",
        style="standard",
        **kwargs
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

        self._init(mode, style)

        # 这两个标记必须在 super().__init__() **之前**就位：基类的构造函数里
        # 会立刻调用 self._draw()，而 _draw 结尾会排一个 after 回调。
        # 旧实现是在 super().__init__() 之后才赋值，等于把那第一个回调 id
        # 覆盖成 None —— 它再也无法被取消（虽然触发时会自己判断并退出）。
        self._update_after_id = None
        self._destroyed = False

        super().__init__(*args, width=width, height=height, **kwargs)

        self.bind("<Destroy>", self._event_destroy_badge, add="+")

        self.dconfigure(
            text=text,
        )

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")

        from .defs import set_default_font

        set_default_font(font, self.attributes, master=self)

    def _init(self, mode, style):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "back_color": None,
                "back_opacity": None,
                "border_color": None,
                "border_color_opacity": None,
                "border_width": None,
                "text_color": None,
            }
        )

        self.theme(mode, style)

    def _draw(self, event=None):
        """
        重新绘制组件

        :param event:
        """

        super()._draw(event)

        self.delete("all")

        _back_color = self.attributes.back_color
        _back_opacity = self.attributes.back_opacity
        _border_color = self.attributes.border_color
        _border_color_opacity = self.attributes.border_color_opacity
        _border_width = self.attributes.border_width
        _text_color = self.attributes.text_color
        from .designs.renderer import get_renderer

        width = self.winfo_width()
        height = self.winfo_height()
        if get_renderer() == 1:
            width -= 1
            height -= 1
        self.element_border = self.create_round_rectangle(
            0,
            0,
            width,
            height,
            temppath=self.temppath,
            temppath2=self.temppath3,
            fill=_back_color,
            fill_opacity=_back_opacity,
            outline=_border_color,
            outline_opacity=_border_color_opacity,
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

        # 旧实现是无条件 self.after(10, lambda: self.update())：
        # 每次重绘都排一个新回调且从不取消，快速重绘时会堆积大量待执行回调，
        # 控件销毁后还会触发，控制台刷 "invalid command name ...<lambda>"。
        # 这里只保留一个可取消的回调，并在销毁时撤销。
        self._cancel_pending_update()
        if self.winfo_exists():
            self._update_after_id = self.after(10, self._deferred_update)

    def _cancel_pending_update(self):
        after_id = getattr(self, "_update_after_id", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
            self._update_after_id = None

    def _deferred_update(self):
        self._update_after_id = None
        if getattr(self, "_destroyed", False) or not self.winfo_exists():
            return
        try:
            self.update()
        except Exception:
            pass

    def _event_destroy_badge(self, event=None):
        if event is not None and getattr(event, "widget", None) is not self:
            return
        self._destroyed = True
        self._cancel_pending_update()

    def theme(self, mode=None, style=None):
        if mode:
            self.mode = mode
        if style:
            self.style = style
        if self.mode.lower() == "dark":
            if self.style.lower() == "accent":
                self._dark_accent()
            else:
                self._dark()
        else:
            if self.style.lower() == "accent":
                self._light_accent()
            else:
                self._light()

    def _theme(self, mode, style):
        n = badge(mode, style)
        self.dconfigure(
            back_color=n["back_color"],
            back_opacity=n["back_opacity"],
            border_color=n["border_color"],
            border_color_opacity=n["border_color_opacity"],
            border_width=n["border_width"],
            text_color=n["text_color"],
        )

    def _light(self):
        self._theme("light", "standard")

    def _light_accent(self):
        self._theme("light", "accent")

    def _dark(self):
        self._theme("dark", "standard")

    def _dark_accent(self):
        self._theme("dark", "accent")
