from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget


class FluListBoxDraw(DSvgDraw):
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
        border = drawing[1].linearGradient(start=(x1, y1), end=(x1, y2), id="DListBox.Border")
        border.add_stop_color("0%", outline)
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


class FluListBoxCanvas(DCanvas):
    draw = FluListBoxDraw

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


class FluListBox(FluListBoxCanvas, DDrawWidget):
    def __init__(self, *args,
                 text="",
                 width=120,
                 height=32,
                 command=None,
                 font=None,
                 mode="light",
                 style="standard",
                 **kwargs):
        self._init(mode, style)

        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:
            def empty(): pass

            command = empty

        self.dconfigure(
            text=text,
            command=command
        )

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.attributes.command(), add="+")

        self.bind("<Return>", lambda event=None: self.attributes.command(), add="+")  # 可以使用回车键模拟点击

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

                "rest": {
                    "back_color": "#ffffff",
                    "border_color": "#f0f0f0",
                    "border_color2": "#d6d6d6",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#1b1b1b",
                },
                "hover": {
                    "back_color": "#fcfcfc",
                    "border_color": "#f0f0f0",
                    "border_color2": "#d6d6d6",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#1b1b1b",
                },
                "pressed": {
                    "back_color": "#fdfdfd",
                    "border_color": "#f0f0f0",
                    "border_color2": "#f0f0f0",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#636363",
                }
            }
        )

        self.theme(mode=mode, style=style)

    def _draw(self, event=None):
        super()._draw(event)

        self.delete("all")

        if self.enter:
            if self.button1:
                _back_color = self.attributes.pressed.back_color
                _border_color = self.attributes.pressed.border_color
                _border_color2 = self.attributes.pressed.border_color2
                _border_width = self.attributes.pressed.border_width
                _radius = self.attributes.pressed.radius
                _text_color = self.attributes.pressed.text_color
            else:
                _back_color = self.attributes.hover.back_color
                _border_color = self.attributes.hover.border_color
                _border_color2 = self.attributes.hover.border_color2
                _border_width = self.attributes.hover.border_width
                _radius = self.attributes.hover.radius
                _text_color = self.attributes.hover.text_color
        else:
            _back_color = self.attributes.rest.back_color
            _border_color = self.attributes.rest.border_color
            _border_color2 = self.attributes.rest.border_color2
            _border_width = self.attributes.rest.border_width
            _radius = self.attributes.rest.radius
            _text_color = self.attributes.rest.text_color

        self.element_border = self.create_round_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), _radius, temppath=self.temppath,
            fill=_back_color, outline=_border_color, outline2=_border_color2, width=_border_width
        )
        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

    def theme(self, mode="light", style=None):
        self.mode = mode
        if style:
            self.style = style
        if mode.lower() == "dark":
            if style.lower() == "accent":
                self._dark_accent()
            else:
                self._dark()
        else:
            if style.lower() == "accent":
                self._light_accent()
            else:
                self._light()

    def _light(self):
        self.dconfigure(
            rest={
                "back_color": "#ffffff",
                "border_color": "#f0f0f0",
                "border_color2": "#d6d6d6",
                "border_width": 1,
                "radius": 6,
                "text_color": "#1b1b1b",
            },
            hover={
                "back_color": "#fcfcfc",
                "border_color": "#f0f0f0",
                "border_color2": "#d6d6d6",
                "border_width": 1,
                "radius": 6,
                "text_color": "#1b1b1b",
            },
            pressed={
                "back_color": "#fdfdfd",
                "border_color": "#f0f0f0",
                "border_color2": "#f0f0f0",
                "border_width": 1,
                "radius": 6,
                "text_color": "#636363",
            }
        )

    def _light_accent(self):
        self.dconfigure(
            rest={
                "back_color": "#005fb8",
                "border_color": "#146cbe",
                "border_color2": "#00396e",
                "border_width": 1,
                "radius": 6,
                "text_color": "#ffffff",
            },
            hover={
                "back_color": "#0359a9",
                "border_color": "#1766b0",
                "border_color2": "#0f4373",
                "border_width": 1,
                "radius": 6,
                "text_color": "#ffffff",
            },
            pressed={
                "back_color": "#005fb8",
                "border_color": "#4389ca",
                "border_color2": "#4389ca",
                "border_width": 1,
                "radius": 6,
                "text_color": "#b4cbe0",
            }
        )

    def _dark(self):
        self.dconfigure(
            rest={
                "back_color": "#272727",
                "border_color": "#303030",
                "border_color2": "#262626",
                "border_width": 1,
                "radius": 6,
                "text_color": "#ffffff",
            },
            hover={
                "back_color": "#2d2d2d",
                "border_color": "#303030",
                "border_color2": "#262626",
                "border_width": 1,
                "radius": 6,
                "text_color": "#ffffff",
            },
            pressed={
                "back_color": "#212121",
                "border_color": "#2a2a2a",
                "border_color2": "#262626",
                "border_width": 1,
                "radius": 6,
                "text_color": "#cfcfcf",
            }
        )

    def _dark_accent(self):
        self.dconfigure(
            rest={
                "back_color": "#60cdff",
                "border_color": "#6cd1ff",
                "border_color2": "#56b4df",
                "border_width": 1,
                "radius": 6,
                "text_color": "#000000",
            },
            hover={
                "back_color": "#5abce9",
                "border_color": "#67c1eb",
                "border_color2": "#50a5cc",
                "border_width": 1,
                "radius": 6,
                "text_color": "#000000",
            },
            pressed={
                "back_color": "#52a9d1",
                "border_color": "#60b0d5",
                "border_color2": "#60b0d5",
                "border_width": 1,
                "radius": 6,
                "text_color": "#295468",
            }
        )

    def invoke(self):
        self.attributes.command()
