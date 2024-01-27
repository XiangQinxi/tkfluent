from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget


class FluTextDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, radius, radiusy=None, temppath=None,
                         fill="transparent", outline="black", outline2="black", width=1
                         ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        border = drawing[1].linearGradient(start=(x1, y1), end=(x1, y2), id="DButton.Border")
        border.add_stop_color("0%", outline)
        border.add_stop_color("85%", outline)
        border.add_stop_color("100%", outline2)
        drawing[1].defs.add(border)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill, stroke_width=width,
                stroke=f"url(#{border.get_id()})",
            )
        )
        drawing[1].save()
        return drawing[0]


class FluTextCanvas(DCanvas):
    draw = FluTextDraw

    def create_round_rectangle(self,
                               x1, y1, x2, y2, r1, r2=None, temppath=None,
                               fill="transparent", outline="black", outline2="black", width=1
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill, outline=outline, outline2=outline2, width=width
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle


class FluText(FluTextCanvas, DDrawWidget):
    def __init__(self, *args,
                 width=120,
                 height=90,
                 font=None,
                 cursor="xterm",
                 mode="light",
                 **kwargs):
        self._init(mode)

        from tkinter import Text

        self.text = Text(border=0, width=width, height=height, cursor=cursor)

        self.text.bind("<Enter>", self._event_enter, add="+")
        self.text.bind("<Leave>", self._event_leave, add="+")
        self.text.bind("<Button-1>", self._event_on_button1, add="+")
        self.text.bind("<ButtonRelease-1>", self._event_off_button1, add="+")
        self.text.bind("<FocusIn>", self._event_focus_in, add="+")
        self.text.bind("<FocusOut>", self._event_focus_out, add="+")

        super().__init__(*args, width=width, height=height, cursor=cursor, **kwargs)

        if font is None:
            from tkdeft.utility.fonts import SegoeFont
            self.attributes.font = SegoeFont()

    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "font": None,

                "rest": {},

                "focus": {}

            }
        )

        self.theme(mode=mode)

    def _draw(self, event=None):
        super()._draw(event)

        self.text.configure(font=self.attributes.font)

        self.delete("all")

        if self.isfocus:
            _back_color = self.attributes.focus.back_color
            _border_color = self.attributes.focus.border_color
            _border_color2 = self.attributes.focus.border_color2
            _border_width = self.attributes.focus.border_width
            _radius = self.attributes.focus.radius
            _text_color = self.attributes.focus.text_color
        else:
            _back_color = self.attributes.rest.back_color
            _border_color = self.attributes.rest.border_color
            _border_color2 = self.attributes.rest.border_color2
            _border_width = self.attributes.rest.border_width
            _radius = self.attributes.rest.radius
            _text_color = self.attributes.rest.text_color

        self.text.configure(
            background=_back_color, insertbackground=_text_color, foreground=_text_color,
            width=self.winfo_width() - _border_width * 2 - _radius,
            height=self.winfo_height() - _border_width * 2 - _radius
        )

        self.element_border = self.create_round_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), _radius, temppath=self.temppath,
            fill=_back_color, outline=_border_color, outline2=_border_color2, width=_border_width
        )

        self.element_text = self.create_window(
            self.winfo_width() / 2, self.winfo_height() / 2,
            window=self.text,
            width=self.winfo_width() - _border_width * 2 - _radius,
            height=self.winfo_height() - _border_width * 2 - _radius
        )

    def _event_focus_in(self, event=None):
        self.isfocus = True

        self._draw(event)

    def _event_focus_out(self, event=None):
        self.isfocus = False

        self._draw(event)

    def theme(self, mode="light"):
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        self.dconfigure(
            rest={
                "back_color": "#ffffff",
                "border_color": "#f0f0f0",
                "border_color2": "#8d8d8d",
                "border_width": 1,
                "radius": 6,
                "text_color": "#646464",
            },
            focus={
                "back_color": "#ffffff",
                "border_color": "#f0f0f0",
                "border_color2": "#005fb8",
                "border_width": 2,
                "radius": 6,
                "text_color": "#636363",
            }
        )

    def _dark(self):
        self.dconfigure(
            rest={
                "back_color": "#272727",
                "border_color": "#2c2c2c",
                "border_color2": "#979797",
                "border_width": 1,
                "radius": 6,
                "text_color": "#ffffff",
            },
            focus={
                "back_color": "#1d1d1d",
                "border_color": "#272727",
                "border_color2": "#60cdff",
                "border_width": 2,
                "radius": 6,
                "text_color": "#ffffff",
            }
        )