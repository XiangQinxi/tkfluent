from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.entry import entry

class FluEntryDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, radius, radiusy=None, temppath=None,
                         fill="transparent", fill_opacity=1,
                         stop1="0.93", outline="black", outline_opacity=1,
                         stop2="0.94", outline2=None, outline2_opacity=1,
                         width=1
                         ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath, fill="none")
        if outline2:
            border = drawing[1].linearGradient(start=(x1, y1 + 1), end=(x1, y2 - 1), id="DButton.Border",
                                               gradientUnits="userSpaceOnUse")
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
                (x1 + 1, y1 + 1), (x2 - x1 - 2, y2 - y1 - 2), _rx, _ry,
                id="Base",
                fill=fill, fill_opacity=fill_opacity,
            )
        )
        drawing[1].add(
            drawing[1].rect(
                (x1 + 0.5, y1 + 0.5), (x2 - x1 - 1, y2 - y1 - 1), _rx, _ry,
                id="Base",
                fill="white", fill_opacity="0",
                stroke=stroke, stroke_width=width, stroke_opacity=stroke_opacity,
            )
        )
        #print("FluEntry", drawing[0])
        drawing[1].save()
        return drawing[0]


class FluEntryCanvas(DCanvas):
    draw = FluEntryDraw

    def create_round_rectangle(self,
                               x1, y1, x2, y2, r1, r2=None, temppath=None,
                               fill="transparent", fill_opacity=1, stop1="0.93", stop2="0.94",
                               outline="black", outline2="black", outline_opacity=1, outline2_opacity=1,
                               width=1
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill, fill_opacity=fill_opacity, stop1=stop1, stop2=stop2,
            outline=outline, outline2=outline2, outline_opacity=outline_opacity, outline2_opacity=outline2_opacity,
            width=width
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle


from .tooltip import FluToolTipBase


class FluEntry(FluEntryCanvas, DDrawWidget, FluToolTipBase):
    def __init__(self, *args,
                 width=120,
                 height=32,
                 font=None,
                 cursor="xterm",
                 textvariable=None,
                 mode="light",
                 state="normal",
                 **kwargs):
        self._init(mode)

        from tkinter import Entry

        self.entry = Entry(textvariable=textvariable, border=0, cursor=cursor)

        self.entry.bind("<Enter>", self._event_enter, add="+")
        self.entry.bind("<Leave>", self._event_leave, add="+")
        self.entry.bind("<Button-1>", self._event_on_button1, add="+")
        self.entry.bind("<ButtonRelease-1>", self._event_off_button1, add="+")
        self.entry.bind("<FocusIn>", self._event_focus_in, add="+")
        self.entry.bind("<FocusOut>", self._event_focus_out, add="+")

        super().__init__(*args, width=width, height=height, cursor=cursor, **kwargs)

        self.bind("<Button-1>", lambda e: self.entry.focus_set())

        self.dconfigure(
            state=state,
        )

        from .defs import set_default_font
        set_default_font(font, self.attributes)

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

        self.delete("all")

        self.entry.configure(font=self.attributes.font)

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
            self.entry.configure(state="normal")
        else:
            _dict = self.attributes.disabled
            self.entry.configure(state="disabled")

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

        self.entry.configure(background=_back_color, insertbackground=_text_color, foreground=_text_color,
                             disabledbackground=_back_color, disabledforeground=_text_color)

        self.element_border = self.create_round_rectangle(
            0, 0, width, height, _radius, temppath=self.temppath,
            fill=_back_color, fill_opacity=_back_opacity, stop1=_stop1, stop2=_stop2,
            outline=_border_color, outline_opacity=_border_color_opacity, outline2=_border_color2,
            outline2_opacity=_border_color2_opacity,
            width=_border_width
        )

        if _underline_fill:
            self.element_line = self.create_line(
                _radius / 3 + _border_width, self.winfo_height() - _radius / 3,
                self.winfo_width() - _radius / 3 - _border_width * 2, self.winfo_height() - _radius / 3,
                width=_underline_width, fill=_underline_fill
            )

        self.element_text = self.create_window(
            _radius/2+_border_width, _radius/2+_border_width,
            window=self.entry, anchor="nw",
            width=self.winfo_width() - _border_width * 2 - _radius,
            height=self.winfo_height() - _border_width * 2 - _radius
        )

        self.tag_raise(self.element_text)

    def _event_focus_in(self, event=None):
        self.isfocus = True

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
        r = entry(mode, "rest")
        h = entry(mode, "hover")
        p = entry(mode, "pressed")
        d = entry(mode, "disabled")
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
                "underline_width": r["underline_width"]
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
                "underline_width": r["underline_width"]
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
                "underline_width": r["underline_width"]
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
                "underline_width": r["underline_width"]
            }
        )

    def _light(self):
        self._theme("light")

    def _dark(self):
        self._theme("dark")