from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.badge import badge


class FluBadgeDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, temppath=None,
                         fill="transparent", fill_opacity=1,
                         outline="black", outline_opacity=1, width=1
                         ):
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), 20, 25,
                id=".Badge", transform="translate(0.500000 0.500000)",
                fill=fill, fill_opacity=fill_opacity,
                stroke=outline, stroke_opacity=outline_opacity, stroke_width=width,
            )
        )
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), 20, 25,
                id=".Badge", transform="translate(0.500000 0.500000)",
                fill="white", fill_opacity=0,
                stroke=outline, stroke_opacity=outline_opacity, stroke_width=width,
            )
        )
        drawing[1].save()
        return drawing[0]


class FluBadgeCanvas(DCanvas):
    draw = FluBadgeDraw

    def create_round_rectangle(self,
                               x1, y1, x2, y2, temppath=None,
                               fill="transparent", fill_opacity=1,
                               outline="black", outline_opacity=1, width=1
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, temppath=temppath,
            fill=fill, fill_opacity=fill_opacity,
            outline=outline, outline_opacity=outline_opacity, width=width
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle


class FluBadge(FluBadgeCanvas, DDrawWidget):

    def __init__(self, *args,
                 text="",
                 width=70,
                 height=30,
                 font=None,
                 mode="light",
                 style="standard",
                 **kwargs):

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

        super().__init__(*args, width=width, height=height, **kwargs)

        self.dconfigure(
            text=text,
        )

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")

        from .defs import set_default_font
        set_default_font(font, self.attributes)

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
                "text_color": None
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

        self.element_border = self.create_round_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), temppath=self.temppath,
            fill=_back_color, fill_opacity=_back_opacity,
            outline=_border_color, outline_opacity=_border_color_opacity, width=_border_width
        )

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

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