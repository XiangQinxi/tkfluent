from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget


class FluBadgeDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, temppath=None,
                         fill="transparent", outline="black", width=1
                         ):
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), 20, 25,
                fill=fill, stroke_width=width,
                stroke=outline,
            )
        )
        drawing[1].save()
        return drawing[0]


class FluBadgeCanvas(DCanvas):
    draw = FluBadgeDraw

    def create_round_rectangle(self,
                               x1, y1, x2, y2, temppath=None,
                               fill="transparent", outline="black", width=1
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, temppath=temppath,
            fill=fill, outline=outline, width=width
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

        if font is None:
            from tkdeft.utility.fonts import SegoeFont
            self.attributes.font = SegoeFont()

    def _init(self, mode, style):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,

                "back_color": None,
                "border_color": None,
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
        _border_color = self.attributes.border_color
        _border_width = self.attributes.border_width
        _text_color = self.attributes.text_color

        self.element_border = self.create_round_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), temppath=self.temppath,
            fill=_back_color, outline=_border_color, width=_border_width
        )

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

    def theme(self, mode, style=None):
        self.mode = mode
        if style:
            self.style = style
        if mode.lower() == "dark":
            if self.style.lower() == "accent":
                self._dark_accent()
            else:
                self._dark()
        else:
            if self.style.lower() == "accent":
                self._light_accent()
            else:
                self._light()

    def _light(self):
        self.dconfigure(
            back_color="#f9f9f9",
            border_color="#f0f0f0",
            border_width=1,
            text_color="#191919",
        )

    def _light_accent(self):
        self.dconfigure(
            back_color="#005fb8",
            border_color="#005fb8",
            border_width=1,
            text_color="#ffffff",
        )

    def _dark(self):
        self.dconfigure(
            back_color="#242424",
            border_color="#242424",
            border_width=1,
            text_color="#ffffff",
        )

    def _dark_accent(self):
        self.dconfigure(
            back_color="#60cdff",
            border_color="#60cdff",
            border_width=1,
            text_color="#000000",
        )