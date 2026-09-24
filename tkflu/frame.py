"""面板/容器组件。

``FluFrame`` 是一个带圆角背景与边框的容器。它内部由"画布 + 子 Frame"组成：

* 画布负责画圆角矩形背景；
* 子 Frame 承载你的内容。

因此 ``FluFrame`` 把 ``pack`` / ``grid`` / ``place`` 都代理给了它内部的画布，
你可以像用普通容器一样使用它。"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw

from .designs.frame import frame


class FluFrameDraw(DSvgDraw):
    def create_roundrect(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        radiusy=None,
        temppath=None,
        fill="transparent",  # fill_opacity=1,
        outline="black",
        outline_opacity=1,
        width=1,
    ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        filter1 = drawing[1].defs.add(
            drawing[1].filter(
                id="filter",
                start=(0, 0),
                size=(x2 - x1, y2 - y1),
                filterUnits="userSpaceOnUse",
                color_interpolation_filters="sRGB",
            )
        )

        filter1.feFlood(flood_opacity="0", result="BackgroundImageFix")
        filter1.feColorMatrix(
            "SourceAlpha",
            type="matrix",
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0",
            result="hardAlpha",
        )
        filter1.feOffset(dx="0", dy="2")
        filter1.feGaussianBlur(stdDeviation="1.33333")
        filter1.feComposite(in2="hardAlpha", operator="out", k2="-1", k3="1")
        filter1.feColorMatrix(
            type="matrix", values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.039 0"
        )
        filter1.feBlend(
            mode="normal", in2="BackgroundImageFix", result="effect_dropShadow_1"
        )
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
        # 几何内缩半个线宽，四边描边才完整。旧写法把矩形铺满 0..w / 0..h，
        # 描边中心线正好压在画布边界上，四条边都只剩一半厚度。
        from tkdeft.svg import add_roundrect

        add_roundrect(
            drawing[1],
            x1,
            y1,
            x2,
            y2,
            _rx,
            _ry,
            fill=fill,  # fill_opacity=fill_opacity,
            outline=outline,
            outline_opacity=outline_opacity,
            width=width,
        )
        drawing[1].save()
        return drawing[0]

class FluFrameCanvas(DCanvas):
    """面板的画布。

    ``create_round_rectangle`` / ``create_roundrect`` 直接继承
    :class:`tkdeft.windows.canvas.DCanvas`——它内部会调用
    :meth:`~tkdeft.windows.canvas.DCanvas.draw_roundrect`，
    当前引擎是栅格引擎时走进程内位图快速路径，否则回退到
    :meth:`~tkdeft.windows.canvas.DCanvas.draw_roundrect_svg`
    （图元来自 :class:`FluFrameDraw`）。
    """

    draw = FluFrameDraw
    frame = None

    #: 这张画布**不持有主题状态**——配色属于它内嵌的 :class:`FluFrame`。
    #: ``FluThemeManager`` 会走整棵控件树，那个 ``FluFrame`` 自己就会被收到；
    #: 若再让画布转发一次，同一套配色会被算两遍（旧实现就是这样，还附带
    #: 每个子控件一次 ``update()``）。
    _theme_proxy = True

    def theme(self, mode="light"):
        """把面板（连同它的子控件）切到 ``mode``。

        旧实现是"自己写 + 遍历子控件 + 每个子控件 ``update()``"，那是
        "一个一个变色"的根源。现在整棵子树交给统一过渡：一条时间轴，
        所有组件同步插值（见 :mod:`tkflu.theme_transition`）。
        """
        from .theme_transition import applying_themes, run_theme_transition

        if applying_themes():
            # 有人（FluThemeManager）正在统一驱动：只改自己的配色，
            # 子控件由驱动方负责，别在这里另起一条时间轴。
            self.frame.theme(mode)
            return
        run_theme_transition(self, mode)


from tkinter import Frame

from tkdeft.object import DObject

from ._after import TracedAfter
from .designs.gradient import FluGradient


class FluFrame(Frame, DObject, FluGradient, TracedAfter):
    def __init__(
        self,
        master=None,
        *args,
        width=300,
        height=150,
        mode="light",
        style="standard",
        **kwargs,
    ):
        self.canvas = FluFrameCanvas(
            master, *args, width=width, height=height, **kwargs
        )
        self.canvas.frame = self

        # 旧实现在这里 mkstemp() 了一个 .svg 临时文件，既泄漏 fd 又从不清理。
        # 现在直接复用画布绘制对象自带的 scratch 文件（控件销毁时统一回收）。
        self.temppath = self.canvas.svgdraw.scratch_path(".svg")

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
                # "back_opacity": None,
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

    def _theme(
        self, mode, style, animation_steps: int = None, animation_step_time: int = None
    ):
        n = frame(mode, style)

        if animation_steps is None:
            from .designs.animation import get_animation_steps

            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time

            animation_step_time = get_animation_step_time()
        # 只在"确实有一个旧颜色可以过渡"时才做动画。
        #
        # 旧实现写的是 hasattr(self.attributes, "back_color") and
        # hasattr(n, "back_color")——`n` 是普通的 dict，`hasattr(dict, ...)`
        # 永远是 False，于是这段过渡动画**从来没有跑过**（静默的死代码）。
        # 顺带一提：首次构造时 self.attributes.back_color 还是 None，
        # 直接拿去插值会抛 AttributeError，所以这里也要挡住。
        previous = self.attributes.back_color
        if (
            previous
            and n.get("back_color")
            and (animation_steps or animation_step_time)
        ):
            steps = max(1, int(animation_steps))
            back_colors = self.generate_hex2hex(previous, n["back_color"], steps=steps)
            for i in range(steps):

                def update(ii=i):  # 使用默认参数立即捕获i的值
                    self._draw(tempcolor=back_colors[ii])

                self.after_traced(i * animation_step_time, update)
            self.after_traced(
                steps * animation_step_time + 10, lambda: self._draw()
            )
        self.dconfigure(
            back_color=n["back_color"],
            border_color=n["border_color"],
            border_color_opacity=n["border_color_opacity"],
            border_width=n["border_width"],
            radius=n["radius"],
        )
        self._draw()
        self.update_idletasks()
        self.canvas.update_idletasks()

    def _light(self):
        self._theme("light", "standard")

    def _light_popupmenu(self):
        self._theme("light", "popupmenu")

    def _dark(self):
        self._theme("dark", "standard")

    def _dark_popupmenu(self):
        self._theme("dark", "popupmenu")

    # ------------------------------------------------------------------
    # 几何管理代理
    # ------------------------------------------------------------------
    # FluFrame 自己挂在内部画布上，真正参与父容器布局的是那张画布。
    # 所以下面这些方法都要转给画布——早先有几处转错了：pack_propagate
    # 把 flag 丢了（变成了"读取"而不是"设置"）、grid_location 丢参数、
    # grid_anchor 传了个 Ellipsis 对象、place_info 返回的是 grid_info。
    def _parent_background(self):
        """父容器的背景色（拿不到时给一个安全的兜底）。

        ``FluFrame`` 会把画布背景同步成父容器的背景，这样圆角外面
        不会露出突兀的一块灰。但 **ttk 控件没有 ``-background`` 选项**：
        ``ttk.Frame`` / ``ttk.Notebook`` / ``ttk.LabelFrame`` 里放一个
        ``FluFrame`` 时，旧写法 ``self.canvas.master.cget("background")``
        会直接抛 ``TclError: unknown option "-background"``，控件根本建不出来。
        """
        parent = self.canvas.master
        for option in ("background", "bg"):
            try:
                return parent.cget(option)
            except Exception:
                continue
        # ttk：向当前主题要它自己的底色
        try:
            from tkinter import ttk

            style = ttk.Style(parent)
            return style.lookup(parent.winfo_class(), "background") or "#ffffff"
        except Exception:
            return "#ffffff"

    def pack_info(self):
        return self.canvas.pack_info()

    def pack_forget(self):
        return self.canvas.pack_forget()

    def pack_slaves(self):
        return self.canvas.pack_slaves()

    def pack_propagate(self, flag=None):
        return self.canvas.pack_propagate(flag)

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

    def grid_anchor(self, anchor=None):
        if anchor is None:
            return self.canvas.grid_anchor()
        return self.canvas.grid_anchor(anchor)

    def grid_slaves(self, row=None, column=None):
        kwargs = {}
        if row is not None:
            kwargs["row"] = row
        if column is not None:
            kwargs["column"] = column
        return self.canvas.grid_slaves(**kwargs)

    def grid_propagate(self, flag=None):
        return self.canvas.grid_propagate(flag)

    def grid_location(self, x, y):
        return self.canvas.grid_location(x, y)

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
        return self.canvas.place_info()

    def place_forget(self):
        return self.canvas.place_forget()

    def place_slaves(self):
        return self.canvas.place_slaves()

    def place_configure(self, **kwargs):
        return self.canvas.place_configure(**kwargs)

    place = place_configure

    def destroy(self):
        """销毁面板，**连同它的画布**。

        这是一个容易被忽略的泄漏：``FluFrame`` 自己挂在内部画布上，
        而那张画布是**父容器的直接子控件**（``self.canvas.master`` 才是
        真正的父容器）。Tk 只会自动销毁"子控件"，所以 ``FluFrame.destroy()``
        过去只干掉了内嵌的 Frame，画布和画在它上面的圆角背景**留在原地**——
        每建一次再销毁一次就多留一块面板。
        """
        canvas = getattr(self, "canvas", None)
        try:
            self.cancel_traced()
            super().destroy()
        finally:
            if canvas is not None:
                try:
                    canvas.destroy()
                except Exception:
                    pass

    def _draw(self, event=None, tempcolor: dict = None):

        self.canvas.delete("all")
        self.canvas.config(background=self._parent_background())
        if not tempcolor:
            _back_color = self.attributes.back_color
        else:
            _back_color = tempcolor
        # _back_opacity = self.attributes.back_opacity
        _border_color = self.attributes.border_color
        _border_color_opacity = self.attributes.border_color_opacity
        _border_width = self.attributes.border_width
        _radius = self.attributes.radius

        self.element1 = self.canvas.create_round_rectangle(
            0,
            0,
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            _radius,
            temppath=self.temppath,
            fill=_back_color,  # fill_opacity=_back_opacity,
            outline=_border_color,
            outline_opacity=_border_color_opacity,
            width=_border_width,
        )

        self.config(background=_back_color)

        self.element2 = self.canvas.create_window(
            self.canvas.winfo_width() / 2,
            self.canvas.winfo_height() / 2,
            window=self,
            width=self.canvas.winfo_width() - _border_width * 2 - _radius,
            height=self.canvas.winfo_height() - _border_width * 2 - _radius,
        )

        # 只做 idle 级刷新（布局 + 重绘），刻意不使用 update()：
        # update() 会处理**全部**待处理事件，其中包括 <Configure>，
        # 于是可能在 _draw 内部再次触发 _draw，形成重入。
        # 另外这里也刻意不再挂 after(100, ...) 延迟回调——它对最终外观没有
        # 额外贡献（背景色已在上面同步设置，且任何尺寸变化都会经 <Configure>
        # 重新走一遍 _draw），却会带来两个真实问题：
        #   1. 连续 resize 时回调不断堆积，每个都强制刷新一次布局 → 卡顿；
        #   2. 窗口关闭后残留回调仍会触发，控制台刷
        #      "invalid command name ...<lambda>"。
        self.update_idletasks()

    def _event_configure(self, event=None):
        self._draw(event)
