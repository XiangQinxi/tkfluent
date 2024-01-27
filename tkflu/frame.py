from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas


class FluFrameDraw(DSvgDraw):
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


class FluFrameCanvas(DCanvas):
    draw = FluFrameDraw

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


from tkinter import Frame
from tkdeft.object import DObject


class FluFrame(Frame, DObject):
    def __init__(self,
                 master=None,
                 *args,
                 width=300,
                 height=150,
                 mode="light",
                 **kwargs,
                 ):
        from tempfile import mkstemp
        _, self.temppath = mkstemp(suffix=".svg", prefix="tkdeft.temp.")

        self.canvas = FluFrameCanvas(master, *args, width=width, height=height, **kwargs)

        super().__init__(master=self.canvas)

        self._init(mode)

        self.enter = False
        self.button1 = False

        self._draw(None)

        self.canvas.bind("<Configure>", self._event_configure, add="+")

    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "back_color": None,
                "border_color": None,
                "border_color2": None,
                "border_width": None,
                "radius": None,
            }
        )

        self.theme(mode)

    def theme(self, mode="light"):
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        self.dconfigure(
            back_color="#ffffff",
            border_color="#ebebeb",
            border_color2="#e4e4e4",
            border_width=1,
            radius=6,
        )

    def _dark(self):
        self.dconfigure(
            back_color="#242424",
            border_color="#303030",
            border_color2="#282828",
            border_width=1,
            radius=6,
        )

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

    def _draw(self, event=None):
        self.canvas.delete("all")
        self.canvas.config(background=self.canvas.master.cget("background"))
        self.config(background=self.attributes.back_color)

        _back_color = self.attributes.back_color
        _border_color = self.attributes.border_color
        _border_color2 = self.attributes.border_color2
        _border_width = self.attributes.border_width
        _radius = self.attributes.radius

        self.element1 = self.canvas.create_round_rectangle(
            0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), _radius, temppath=self.temppath,
            fill=_back_color, outline=_border_color, outline2=_border_color2, width=_border_width
        )

        self.element2 = self.canvas.create_window(
            self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
            window=self,
            width=self.canvas.winfo_width() - _border_width * 2 - _radius,
            height=self.canvas.winfo_height() - _border_width * 2 - _radius
        )

    def _event_configure(self, event=None):
        self._draw(event)
