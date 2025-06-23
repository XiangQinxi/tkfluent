from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.button import button


class FluButtonDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, radius, radiusy=None, temppath=None,
                         fill="transparent", fill_opacity=1,
                         outline="black", outline2=None, outline_opacity=1, outline2_opacity=1, width=1,
                         ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        if outline2:
            border = drawing[1].linearGradient(start=(x1, y1), end=(x1, y2), id="DButton.Border",
                                               gradientUnits="userSpaceOnUse")
            border.add_stop_color("0.9", outline, outline_opacity)
            border.add_stop_color("1", outline2, outline2_opacity)
            drawing[1].defs.add(border)
            stroke = f"url(#{border.get_id()})"
            stroke_opacity = 1
        else:
            stroke = outline
            stroke_opacity = outline_opacity
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill, fill_opacity=fill_opacity,
                stroke=stroke, stroke_width=width, stroke_opacity=stroke_opacity,
                transform="translate(0.500000 0.500000)"
            )
        )
        drawing[1].save()
        return drawing[0]


class FluButtonCanvas(DCanvas):
    draw = FluButtonDraw

    def create_round_rectangle(self,
                               x1, y1, x2, y2, r1, r2=None, temppath=None,
                               fill="transparent", fill_opacity=1,
                               outline="black", outline2="black", outline_opacity=1, outline2_opacity=1,
                               width=1,
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill, fill_opacity=fill_opacity,
            outline=outline, outline2=outline2, outline_opacity=outline_opacity, outline2_opacity=outline2_opacity,
            width=width,
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle


from .constants import MODE, STATE, BUTTONSTYLE
from .tooltip import FluToolTipBase
from .designs.gradient import FluGradient

class FluButton(FluButtonCanvas, DDrawWidget, FluToolTipBase, FluGradient):
    def __init__(self, *args,
                 text="",
                 width=120,
                 height=32,
                 command=None,
                 font=None,
                 mode: MODE = "light",
                 style: BUTTONSTYLE = "standard",
                 state: STATE = "normal",
                 **kwargs):
        self._init(mode, style)

        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:
            def empty(): pass

            command = empty

        self.dconfigure(
            text=text,
            command=command,
            state=state,
        )

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.attributes.command(), add="+")

        self.bind("<Return>", lambda event=None: self.attributes.command(), add="+")  # 可以使用回车键模拟点击

        from .defs import set_default_font
        set_default_font(font, self.attributes)

    def _init(self, mode: MODE, style: BUTTONSTYLE):

        from easydict import EasyDict

        self.enter = False
        self.button1 = False

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "state": "normal",

                "rest": {},
                "hover": {},
                "pressed": {},
                "disabled": {}
            }
        )

        self.theme(mode=mode, style=style)

    def _draw(self, event=None, tempcolor: dict = None):
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()

        self.delete("all")

        state = self.dcget("state")

        _dict = None

        if not tempcolor:
            if state == "normal":
                if self.enter:
                    if self.button1:
                        _dict = self.attributes.pressed
                    else:
                        _dict = self.attributes.hover
                else:
                    _dict = self.attributes.rest
            else:
                _dict = self.attributes.disabled

            _back_color = _dict.back_color
            _back_opacity = _dict.back_opacity
            _border_color = _dict.border_color
            _border_color_opacity = _dict.border_color_opacity
            _border_color2 = _dict.border_color2
            _border_color2_opacity = _dict.border_color2_opacity
            _border_width = _dict.border_width
            _radius = _dict.radius
            _text_color = _dict.text_color
        else:
            _back_color = tempcolor.back_color
            _back_opacity = tempcolor.back_opacity
            _border_color = tempcolor.border_color
            _border_color_opacity = tempcolor.border_color_opacity
            _border_color2 = tempcolor.border_color2
            _border_color2_opacity = tempcolor.border_color2_opacity
            _border_width = tempcolor.border_width
            _radius = tempcolor.radius
            _text_color = tempcolor.text_color

        self.element_border = self.create_round_rectangle(
            0, 0, width, height, _radius, temppath=self.temppath,
            fill=_back_color, fill_opacity=_back_opacity,
            outline=_border_color, outline_opacity=_border_color_opacity, outline2=_border_color2,
            outline2_opacity=_border_color2_opacity,
            width=_border_width,
        )

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

        self.update()

    def theme(self, mode: MODE = None, style: BUTTONSTYLE = None):
        if mode:
            self.mode = mode
        if style:
            self.style = style
        if self.mode.lower() == "dark":
            if self.style.lower() == "accent":
                self._dark_accent()
            elif self.style.lower() == "menu":
                self._dark_menu()
            else:
                self._dark()
        else:
            if self.style.lower() == "accent":
                self._light_accent()
            elif self.style.lower() == "menu":
                self._light_menu()
            else:
                self._light()

    def _theme(self, mode, style, animation_steps: int = None, animation_step_time: int = None):
        if animation_steps is None:
            from .designs.animation import get_animation_steps
            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time
            animation_step_time = get_animation_step_time()
        r = button(mode, style, "rest")
        h = button(mode, style, "hover")
        p = button(mode, style, "pressed")
        d = button(mode, style, "disabled")
        if self.dcget("state") == "normal":
            if self.enter:
                if self.button1:
                    now = p
                else:
                    now = h
            else:
                now = r
        else:
            now = d
        #print(animation_step_time)
        #print(type(animation_step_time))
        if hasattr(self.attributes.rest, "back_color"):
            back_colors = self.generate_hex2hex(
                self.attributes.rest.back_color, now["back_color"], animation_steps
            )
            border_colors = self.generate_hex2hex(
                self.attributes.rest.border_color, now["border_color"], animation_steps
            )
            if self.attributes.rest.border_color2 is None:
                self.attributes.rest.border_color2 = self.attributes.rest.border_color
            if now["border_color2"] is None:
                now["border_color2"] = now["border_color"]
            border_colors2 = self.generate_hex2hex(
                self.attributes.rest.border_color2, now["border_color2"], animation_steps
            )
            text_colors = self.generate_hex2hex(
                self.attributes.rest.text_color, now["text_color"], animation_steps
            )
            import numpy as np
            back_opacitys = np.linspace(
                float(self.attributes.rest.back_opacity), float(now["back_opacity"]), animation_steps).tolist()
            border_color_opacitys = np.linspace(
                float(self.attributes.rest.border_color_opacity), float(now["border_color_opacity"]), animation_steps).tolist()
            if self.attributes.rest.border_color2_opacity is None:
                self.attributes.rest.border_color2_opacity = self.attributes.rest.border_color_opacity
            if now["border_color2_opacity"] is None:
                now["border_color2_opacity"] = now["border_color_opacity"]
            border_color2_opacitys = np.linspace(
                float(self.attributes.rest.border_color2_opacity), float(now["border_color2_opacity"]), animation_steps).tolist()
            for i in range(animation_steps):
                def update(ii=i):
                    from easydict import EasyDict
                    tempcolor = EasyDict(
                        {
                            "back_color": back_colors[ii],
                            "back_opacity": back_opacitys[ii],
                            "border_color": border_colors[ii],
                            "border_color_opacity": str(border_color_opacitys[ii]),
                            "border_color2": border_colors2[ii],
                            "border_color2_opacity": str(border_color2_opacitys[ii]),
                            "border_width": 1,
                            "text_color": text_colors[ii],
                            "radius": 6,
                        }
                    )
                    self._draw(None, tempcolor)

                self.after(i * animation_step_time, update)
            #self.after(animation_steps * animation_step_time + 10, lambda: self._draw(None, None))

        self.dconfigure(
            rest={
                "back_color": r["back_color"],
                "back_opacity": r["back_opacity"],
                "border_color": r["border_color"],
                "border_color_opacity": r["border_color_opacity"],
                "border_color2": r["border_color2"],
                "border_color2_opacity": r["border_color2_opacity"],
                "border_width": r["border_width"],
                "radius": r["radius"],
                "text_color": r["text_color"],
            },
            hover={
                "back_color": h["back_color"],
                "back_opacity": h["back_opacity"],
                "border_color": h["border_color"],
                "border_color_opacity": h["border_color_opacity"],
                "border_color2": h["border_color2"],
                "border_color2_opacity": h["border_color2_opacity"],
                "border_width": h["border_width"],
                "radius": h["radius"],
                "text_color": h["text_color"],
            },
            pressed={
                "back_color": p["back_color"],
                "back_opacity": p["back_opacity"],
                "border_color": p["border_color"],
                "border_color_opacity": p["border_color_opacity"],
                "border_color2": p["border_color2"],
                "border_color2_opacity": p["border_color2_opacity"],
                "border_width": p["border_width"],
                "radius": p["radius"],
                "text_color": p["text_color"],
            },
            disabled={
                "back_color": d["back_color"],
                "back_opacity": d["back_opacity"],
                "border_color": d["border_color"],
                "border_color_opacity": d["border_color_opacity"],
                "border_color2": d["border_color2"],
                "border_color2_opacity": d["border_color2_opacity"],
                "border_width": d["border_width"],
                "radius": d["radius"],
                "text_color": d["text_color"],
            }
        )

    def _light(self):
        self._theme("light", "standard")

    def _light_menu(self):
        self._theme("light", "menu")

    def _light_accent(self):
        self._theme("light", "accent")

    def _dark(self):
        self._theme("dark", "standard")

    def _dark_menu(self):
        self._theme("dark", "menu")

    def _dark_accent(self):
        self._theme("dark", "accent")

    def invoke(self):
        self.attributes.command()

    def _event_off_button1(self, event=None):
        self.button1 = False

        self._draw(event)

        if self.enter:
            # self.focus_set()
            if self.dcget("state") == "normal":
                self.event_generate("<<Clicked>>")
