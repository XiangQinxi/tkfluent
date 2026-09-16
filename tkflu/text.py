"""多行文本框组件。

``FluText`` 与 :class:`~tkflu.entry.FluEntry` 类似，
把原生 ``tkinter.Text`` 嵌进圆角画布中以获得 Fluent 外观。"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.text import text


class FluTextDraw(DSvgDraw):
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
        fill_opacity=1,
        stop1="0.93",
        outline="black",
        outline_opacity=1,
        stop2="0.94",
        outline2=None,
        outline2_opacity=1,
        width=1,
    ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath, fill="none")
        if outline2:
            border = drawing[1].linearGradient(
                start=(x1, y1 + 1),
                end=(x1, y2 - 1),
                id="DButton.Border",
                gradientUnits="userSpaceOnUse",
            )
            border.add_stop_color(stop1, outline, outline_opacity)
            border.add_stop_color(stop2, outline2, outline2_opacity)
            drawing[1].defs.add(border)
            stroke = f"url(#{border.get_id()})"
            stroke_opacity = 1
        else:
            stroke = outline
            stroke_opacity = outline_opacity

        drawing[1].add(
            drawing[1].rect(
                (x1 + 1, y1 + 1),
                (x2 - x1 - 2, y2 - y1 - 2),
                _rx,
                _ry,
                id="Base",
                fill=fill,
                fill_opacity=fill_opacity,
            )
        )
        drawing[1].add(
            drawing[1].rect(
                (x1 + 0.5, y1 + 0.5),
                (x2 - x1 - 1, y2 - y1 - 1),
                _rx,
                _ry,
                id="Base",
                fill="white",
                fill_opacity="0",
                stroke=stroke,
                stroke_width=width,
                stroke_opacity=stroke_opacity,
            )
        )
        # print("FluEntry", drawing[0])
        drawing[1].save()
        return drawing[0]


class FluTextCanvas(DCanvas):
    draw = FluTextDraw

    def create_round_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        r1,
        r2=None,
        temppath=None,
        temppath2=None,
        fill="transparent",
        fill_opacity=1,
        stop1="0.93",
        stop2="0.94",
        outline="black",
        outline2="black",
        outline_opacity=1,
        outline2_opacity=1,
        width=1,
    ) -> int:
        """画文本框的圆角背景。

        :param stop1: 描边渐变的第一个 stop（文本框用的是很短的 0.93→0.94）
        :param stop2: 描边渐变的第二个 stop
        :param r1: 圆角半径（x 方向）
        :param r2: 圆角半径（y 方向）
        :returns: 画布上的 item id

        实现转调 :meth:`tkdeft.windows.canvas.DCanvas.draw_roundrect`：
        ``stop1`` / ``stop2`` 是历史写法，tkdeft 那边统一叫
        ``gradient_stop1`` / ``gradient_stop2``，这里做一次翻译。
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
            stop1=stop1,
            stop2=stop2,
            fill=fill,
            fill_opacity=fill_opacity,
            outline=outline,
            outline2=outline2,
            outline_opacity=outline_opacity,
            outline2_opacity=outline2_opacity,
            width=width,
        )

    create_roundrect = create_round_rectangle

    def draw_roundrect_svg(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        radiusy=None,
        *,
        temppath=None,
        temppath2=None,
        gradient_stop1="0.93",
        gradient_stop2="0.94",
        **kwargs,
    ) -> int:
        """SVG 兜底：文本框的描边是设计稿规定的 0.93→0.94 短渐变。"""
        self._img = self.svgdraw.create_roundrect(
            x1,
            y1,
            x2,
            y2,
            radius,
            radiusy,
            temppath=temppath,
            stop1=gradient_stop1,
            stop2=gradient_stop2,
            **kwargs,
        )
        return self.draw_svg_item(self._img, temppath2, x1, y1)


from .tooltip import FluToolTipBase


class FluText(FluTextCanvas, DDrawWidget, FluToolTipBase):
    def __init__(
        self,
        *args,
        width=120,
        height=90,
        font=None,
        cursor="xterm",
        mode="light",
        state="normal",
        **kwargs,
    ):
        self._init(mode)

        #: 内嵌的原生 Text。
        #: 真正的实例在 super().__init__() **之后** 才创建——那时 self 已经是
        #: 一个可用的画布，才能把它当作 master。父类构造里的首次 _draw 会因为
        #: 它是 None 而跳过内嵌控件，随后我们补一次 _draw。
        self.text = None

        super().__init__(*args, width=width, height=height, cursor=cursor, **kwargs)

        from tkinter import Text

        # master=self 很关键：不传的话 Text 会挂到**默认根窗口**上，而不是
        # 这个控件内部（原因同 FluEntry）。
        self.text = Text(self, border=0, cursor=cursor)

        self.text.bind("<Enter>", self._event_enter, add="+")
        self.text.bind("<Leave>", self._event_leave, add="+")
        self.text.bind("<Button-1>", self._event_on_button1, add="+")
        self.text.bind("<ButtonRelease-1>", self._event_off_button1, add="+")
        self.text.bind("<FocusIn>", self._event_focus_in, add="+")
        self.text.bind("<FocusOut>", self._event_focus_out, add="+")

        self.bind("<Button-1>", lambda e: self.text.focus_set(), add="+")

        self.dconfigure(
            state=state,
        )

        from .defs import set_default_font

        set_default_font(font, self.attributes)

        # Text 建好之后再画一次，把它嵌进画布
        self._draw()

    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "font": None,
                "state": "normal",
                "rest": {},
                "hover": {},
                "pressed": {},
                "disabled": {},
            }
        )

        self.theme(mode=mode)

    def _draw(self, event=None):
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()

        # 构造过程中（super().__init__ 里的首次 _draw）Text 还没建好，
        # 这时只画背景，等 Text 创建完成后再补一次 _draw。
        text_widget = self.text
        if text_widget is not None:
            text_widget.configure(font=self.attributes.font)

        self.delete("all")

        state = self.dcget("state")

        _dict = None

        if state == "normal":
            if self.isfocus:
                _dict = self.attributes.pressed
            else:
                if self.enter:
                    _dict = self.attributes.hover
                else:
                    _dict = self.attributes.rest
            if text_widget is not None:
                text_widget.configure(state="normal")
        else:
            _dict = self.attributes.disabled
            if text_widget is not None:
                text_widget.configure(state="disabled")

        _stop1 = _dict.stop1
        _stop2 = _dict.stop2
        _back_color = _dict.back_color
        _back_opacity = _dict.back_opacity
        _border_color = _dict.border_color
        _border_color_opacity = _dict.border_color_opacity
        _border_color2 = _dict.border_color2
        _border_color2_opacity = _dict.border_color2_opacity
        _border_width = _dict.border_width
        _radius = _dict.radius
        _text_color = _dict.text_color
        _underline_fill = _dict.underline_fill
        _underline_width = _dict.underline_width

        if text_widget is not None:
            text_widget.configure(
                background=_back_color,
                insertbackground=_text_color,
                foreground=_text_color,
                width=self.winfo_width() - _border_width * 2 - _radius,
                height=self.winfo_height() - _border_width * 2 - _radius,
            )

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
            stop1=_stop1,
            stop2=_stop2,
            outline=_border_color,
            outline_opacity=_border_color_opacity,
            outline2=_border_color2,
            outline2_opacity=_border_color2_opacity,
            width=_border_width,
        )
        """if _underline_fill:
            if not hasattr(self, "element_line"):
                self.element_line = self.create_line(
                    _radius / 3 + _border_width, self.winfo_height() - _radius / 3,
                    self.winfo_width() - _radius / 3 - _border_width * 2, self.winfo_height() - _radius / 3,
                    width=_underline_width, fill=_underline_fill
                )
            else:
                self.coords(
                    self.element_line, _radius / 3 + _border_width, self.winfo_height() - _radius / 3,
                    self.winfo_width() - _radius / 3 - _border_width * 2, self.winfo_height() - _radius / 3,
                )
                self.itemconfigure(self.element_line, width=_underline_width, fill=_underline_fill)
        """

        """        
        if not hasattr(self, "element_text"):
            self.element_text = self.create_window(
                self.winfo_width() / 2, self.winfo_height() / 2,
                window=self.text,
                width=self.winfo_width() - _border_width * 2 - _radius,
                height=self.winfo_height() - _border_width * 2 - _radius
            )
        else:
            self.coords(self.element_text, self.winfo_width() / 2, self.winfo_height() / 2,
                        self.winfo_width() - _border_width * 2 - _radius, self.winfo_height() - _border_width * 2 - _radius)
        """
        if text_widget is not None:
            if hasattr(self, "element_text"):
                self.delete(self.element_text)
            self.element_text = self.create_window(
                self.winfo_width() / 2,
                self.winfo_height() / 2,
                window=text_widget,
                width=self.winfo_width() - _border_width * 2 - _radius,
                height=self.winfo_height() - _border_width * 2 - _radius,
            )
        if hasattr(self, "element_line"):
            self.delete(self.element_line)
        if _underline_fill:
            self.element_line = self.create_line(
                _radius / 3 + _border_width,
                self.winfo_height() - _radius / 3,
                self.winfo_width() - _radius / 3 - _border_width * 2,
                self.winfo_height() - _radius / 3,
                width=_underline_width,
                fill=_underline_fill,
            )
        if hasattr(self, "element_text"):
            self.tag_raise(self.element_text, self.element_border)
        # self.tag_raise(self.element_line, self.element_text)

        # self.tag_raise(self.element_text)

    def _event_focus_in(self, event=None):
        self.isfocus = True

        self.text.focus_set()

        self._draw(event)

    def _event_focus_out(self, event=None):
        self.isfocus = False

        self._draw(event)

    def theme(self, mode="light"):
        self.mode = mode
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _theme(self, mode):
        r = text(mode, "rest")
        h = text(mode, "hover")
        p = text(mode, "pressed")
        d = text(mode, "disabled")
        self.dconfigure(
            rest={
                "back_color": r["back_color"],
                "back_opacity": r["back_opacity"],
                "stop1": r["stop1"],
                "border_color": r["border_color"],
                "border_color_opacity": r["border_color_opacity"],
                "stop2": r["stop2"],
                "border_color2": r["border_color2"],
                "border_color2_opacity": r["border_color2_opacity"],
                "border_width": r["border_width"],
                "radius": r["radius"],
                "text_color": r["text_color"],
                "underline_fill": r["underline_fill"],
                "underline_width": r["underline_width"],
            },
            hover={
                "back_color": h["back_color"],
                "back_opacity": h["back_opacity"],
                "stop1": h["stop1"],
                "border_color": h["border_color"],
                "border_color_opacity": h["border_color_opacity"],
                "stop2": h["stop2"],
                "border_color2": h["border_color2"],
                "border_color2_opacity": h["border_color2_opacity"],
                "border_width": h["border_width"],
                "radius": h["radius"],
                "text_color": h["text_color"],
                "underline_fill": h["underline_fill"],
                "underline_width": r["underline_width"],
            },
            pressed={
                "back_color": p["back_color"],
                "back_opacity": p["back_opacity"],
                "stop1": p["stop1"],
                "border_color": p["border_color"],
                "border_color_opacity": p["border_color_opacity"],
                "stop2": p["stop2"],
                "border_color2": p["border_color2"],
                "border_color2_opacity": p["border_color2_opacity"],
                "border_width": p["border_width"],
                "radius": p["radius"],
                "text_color": p["text_color"],
                "underline_fill": p["underline_fill"],
                "underline_width": r["underline_width"],
            },
            disabled={
                "back_color": d["back_color"],
                "back_opacity": r["back_opacity"],
                "stop1": d["stop1"],
                "border_color": d["border_color"],
                "border_color_opacity": d["border_color_opacity"],
                "stop2": d["stop2"],
                "border_color2": d["border_color2"],
                "border_color2_opacity": d["border_color2_opacity"],
                "border_width": d["border_width"],
                "radius": d["radius"],
                "text_color": d["text_color"],
                "underline_fill": d["underline_fill"],
                "underline_width": r["underline_width"],
            },
        )

    def _light(self):
        self._theme("light")

    def _dark(self):
        self._theme("dark")
