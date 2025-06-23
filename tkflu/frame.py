from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas

from .designs.frame import frame


class FluFrameDraw(DSvgDraw):
    def create_roundrect(self,
                         x1, y1, x2, y2, radius, radiusy=None, temppath=None,
                         fill="transparent",  #fill_opacity=1,
                         outline="black", outline_opacity=1, width=1
                         ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        filter1 = drawing[1].defs.add(
            drawing[1].filter(id="filter", start=(0, 0), size=(x2 - x1, y2 - y1), filterUnits="userSpaceOnUse",
                              color_interpolation_filters="sRGB")
        )

        filter1.feFlood(flood_opacity="0", result="BackgroundImageFix")
        filter1.feColorMatrix("SourceAlpha", type="matrix", values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0",
                              result="hardAlpha")
        filter1.feOffset(dx="0", dy="2")
        filter1.feGaussianBlur(stdDeviation="1.33333")
        filter1.feComposite(in2="hardAlpha", operator="out", k2="-1", k3="1")
        filter1.feColorMatrix(type="matrix", values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.039 0")
        filter1.feBlend(mode="normal", in2="BackgroundImageFix", result="effect_dropShadow_1")
        filter1.feBlend(mode="normal", in2="effect_dropShadow_1", result="shape")

        """if outline2:
            border = drawing[1].linearGradient(start=(x1, y1), end=(x1, y2), id="DButton.Border")
            border.add_stop_color("0%", outline)
            border.add_stop_color("100%", outline2)
            drawing[1].defs.add(border)
            _border = f"url(#{border.get_id()})"
        else:
            _border = outline"""

        """
        <rect id="Surface / Card Surface" rx="-0.500000" width="159.000000" height="79.000000" transform="translate(3.500000 1.500000)" fill="#FFFFFF" fill-opacity="0"/>
        """
        """drawing[1].add(
            drawing[1].rect(
                rx="-0.500000",
                size=(x2 - x1 - 7, y2 - y1 - 7),
                transform="translate(3.500000 1.500000)",
                fill="#FFFFFF",
                fill_opacity="0"
            )
        )
        drawing[1].add(
            drawing[1].rect(
                (4, 2), (x2 - x1 - 8, y2 - y1 - 8), _rx, _ry,
                fill="#FFFFFF",
                fill_opacity="0.700000",
            )
        )
        group = drawing[1].g(filter="url(#filter)", style="mix-blend-mode:multiply")
        group.add(
            drawing[1].rect(
                (4, 2), (x2 - x1 - 8, y2 - y1 - 8), _rx, _ry,
                fill="#FFFFFF",
                fill_opacity="1",
            )
        )"""
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill,  #fill_opacity=fill_opacity,
                stroke_width=width,
                stroke=outline, stroke_opacity=outline_opacity
            )
        )
        drawing[1].save()
        return drawing[0]


class FluFrameCanvas(DCanvas):
    draw = FluFrameDraw
    frame = None

    def theme(self, mode="light"):
        self.theme_myself(mode=mode)

        for widget in self.frame.winfo_children():
            if hasattr(widget, "theme"):
                widget.theme(mode=mode)
                if hasattr(widget, "_draw"):
                    widget._draw()
                widget.update()

    def theme_myself(self, mode="light"):
        self.frame.theme(mode)
        if hasattr(self.frame, "_draw"):
            self.frame._draw()
        self.frame.update()
        self.update()

    def create_round_rectangle(self,
                               x1, y1, x2, y2, r1, r2=None, temppath=None,
                               fill="transparent",  #fill_opacity=1,
                               outline="black", outline_opacity=1, width=1
                               ):
        self._img = self.svgdraw.create_roundrect(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill,  #fill_opacity=fill_opacity,
            outline=outline, outline_opacity=outline_opacity, width=width
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle


from tkinter import Frame
from tkdeft.object import DObject
from .designs.gradient import FluGradient


class FluFrame(Frame, DObject, FluGradient):
    def __init__(self,
                 master=None,
                 *args,
                 width=300,
                 height=150,
                 mode="light",
                 style="standard",
                 **kwargs,
                 ):
        from tempfile import mkstemp
        _, self.temppath = mkstemp(suffix=".svg", prefix="tkdeft.temp.")

        self.canvas = FluFrameCanvas(master, *args, width=width, height=height, **kwargs)
        self.canvas.frame = self

        super().__init__(master=self.canvas)

        self._init(mode, style)

        self.enter = False
        self.button1 = False

        self._draw(None)

        self.canvas.bind("<Configure>", self._event_configure, add="+")

    def _init(self, mode, style):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "back_color": None,
                #"back_opacity": None,
                "border_color": None,
                "border_color_opacity": None,
                "border_width": None,
                "radius": None,
            }
        )

        self.theme(mode=mode, style=style)

    def theme(self, mode=None, style=None):
        if mode:
            self.mode = mode
        if style:
            self.style = style
        if self.mode.lower() == "dark":
            if self.style.lower() == "popupmenu":
                self._dark_popupmenu()
            else:
                self._dark()
        else:
            if self.style.lower() == "popupmenu":
                self._light_popupmenu()
            else:
                self._light()

    def _theme(self, mode, style, animate_steps: int = 10):
        n = frame(mode, style)
        if hasattr(self.attributes, "back_color") and hasattr(n, "back_color"):
            back_colors = self.generate_hex2hex(self.attributes.back_color, n["back_color"], steps=10)
            for i in range(10):
                def update(ii=i):  # 使用默认参数立即捕获i的值
                    self._draw(tempcolor=back_colors[ii])

                self.after(i * 10, update)  # 直接传递函数，不需要lambda
        self.after(animate_steps * 10 + 10, lambda: self._draw())
        self.dconfigure(
            back_color=n["back_color"],
            border_color=n["border_color"],
            border_color_opacity=n["border_color_opacity"],
            border_width=n["border_width"],
            radius=n["radius"],
        )
        self._draw()
        self.update()
        self.canvas.update()

    def _light(self):
        self._theme("light", "standard")

    def _light_popupmenu(self):
        self._theme("light", "popupmenu")

    def _dark(self):
        self._theme("dark", "standard")
    def _dark_popupmenu(self):
        self._theme("dark", "popupmenu")

    def pack_info(self):
        return self.canvas.pack_info()

    def pack_forget(self):
        return self.canvas.pack_forget()

    def pack_slaves(self):
        return self.canvas.pack_slaves()

    def pack_propagate(self, flag):
        return self.canvas.pack_propagate()

    def pack_configure(self, **kwargs):
        return self.canvas.pack_configure(**kwargs)

    pack = pack_configure

    def grid_info(self):
        return self.canvas.grid_info()

    def grid_forget(self):
        return self.canvas.grid_forget()

    def grid_size(self):
        return self.canvas.grid_size()

    def grid_remove(self):
        return self.canvas.grid_remove()

    def grid_anchor(self, anchor=...):
        return self.canvas.grid_anchor(anchor)

    def grid_slaves(self, row=..., column=...):
        return self.canvas.grid_slaves(row=row, column=column)

    def grid_propagate(self, flag):
        return self.canvas.grid_propagate(flag)

    def grid_location(self, x, y):
        return self.canvas.grid_location()

    def grid_bbox(self, **kwargs):
        return self.canvas.grid_bbox(**kwargs)

    def grid_configure(self, **kwargs):
        return self.canvas.grid_configure(**kwargs)

    grid = grid_configure

    def grid_rowconfigure(self, **kwargs):
        return self.canvas.grid_rowconfigure(**kwargs)

    def grid_columnconfigure(self, **kwargs):
        return self.canvas.grid_columnconfigure(**kwargs)

    def place_info(self):
        return self.canvas.grid_info()

    def place_forget(self):
        return self.canvas.place_forget()

    def place_slaves(self):
        return self.canvas.place_slaves()

    def place_configure(self, **kwargs):
        return self.canvas.place_configure(**kwargs)

    place = place_configure

    def _draw(self, event=None, tempcolor: dict = None):

        self.canvas.delete("all")
        self.canvas.config(background=self.canvas.master.cget("background"))
        if not tempcolor:
            _back_color = self.attributes.back_color
        else:
            _back_color = tempcolor
        #_back_opacity = self.attributes.back_opacity
        _border_color = self.attributes.border_color
        _border_color_opacity = self.attributes.border_color_opacity
        _border_width = self.attributes.border_width
        _radius = self.attributes.radius

        self.element1 = self.canvas.create_round_rectangle(
            0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), _radius, temppath=self.temppath,
            fill=_back_color,  #fill_opacity=_back_opacity,
            outline=_border_color, outline_opacity=_border_color_opacity, width=_border_width
        )

        self.config(background=_back_color)

        self.element2 = self.canvas.create_window(
            self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
            window=self,
            width=self.canvas.winfo_width() - _border_width * 2 - _radius,
            height=self.canvas.winfo_height() - _border_width * 2 - _radius
        )

        self.update_idletasks()

        self.after(100, lambda: self.update_idletasks())
        self.after(100, lambda: self.config(background=_back_color))

    def _event_configure(self, event=None):
        self._draw(event)
