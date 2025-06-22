from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget

from .designs.slider import slider


class FluSliderDraw(DSvgDraw):
    def create_slider(
            self,
            x1, y1, x2, y2,
            x3,  # 滑块的x坐标
            r1,  # 滑块外圆半径
            r2,  # 滑块内圆半径
            temppath=None,
            fill="transparent", fill_opacity=1,  # 滑块外圆的背景颜色、透明度
            radius=3,  # 滑块进度条圆角大小
            outline="transparent", outline_opacity=1,  # 滑块伪阴影的渐变色中的第一个渐变颜色、透明度
            outline2="transparent", outline2_opacity=1,  # 滑块伪阴影的渐变色中的第二个渐变颜色、透明度
            inner_fill="transparent", inner_fill_opacity=1,  # 滑块内圆的背景颜色、透明度
            track_fill="transparent", track_height=4, track_opacity=1,  # 滑块进度条的选中部分矩形的背景颜色、高度、透明度
            rail_fill="transparent", rail_opacity=1  #
    ):
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath, fill_opacity=0)

        border = drawing[1].linearGradient(start=(r1, 1), end=(r1, r1 * 2 - 1), id="DButton.Border",
                                           gradientUnits="userSpaceOnUse")
        border.add_stop_color(0.500208, outline, outline_opacity)
        border.add_stop_color(0.954545, outline2, outline2_opacity)
        drawing[1].defs.add(border)
        stroke = f"url(#{border.get_id()})"
        #print("x1:", x1, "\n", "y1:", y1, "\n", "x2:", x2, "\n", "y2:", y2, "\n", "r1:", r1, "\n", sep="")

        x = x1 + r1 - 4
        xx = x2 - r1 + 4

        #print("track_x1:", x, "\n", "track_x2:", xx, sep="")

        #print("")

        drawing[1].add(
            drawing[1].rect(
                (x, (y2 - y1) / 2 - track_height / 2),
                # 矩形x位置：画布最左的x坐标 + 滑块外半径 - 滑块内半径
                # 矩形y位置：画布高度(画布最上的y坐标 - 画布最上的y坐标)一半 - 进度条的高度的一半
                (xx - x, track_height),
                # 矩形宽度：画布最右的x坐标 - 滑块外半径 + 滑块内半径 | 矩形高度：进度条的高度
                rx=radius,
                fill=rail_fill, fill_opacity=rail_opacity
            )
        )  # 滑块进度未选中区域 (占全部)

        drawing[1].add(
            drawing[1].rect(
                (x, (y2 - y1) / 2 - track_height / 2),
                # 矩形x位置：画布最左的x坐标 + 滑块外半径 - 滑块内半径
                # 矩形y位置：画布高度(画布最上的y坐标 - 画布最上的y坐标)一半 - 进度条的高度的一半
                (x3 - x, track_height),
                # 矩形宽度：(滑块的x坐标 - 矩形x位置) | 矩形高度：进度条的高度
                rx=radius,
                fill=track_fill, fill_opacity=track_opacity, fill_rule="evenodd"
            )
        )  # 滑块进度左边的选中区域 (只左部分)

        x = x3
        y = (y2 - y1) / 2

        drawing[1].add(
            drawing[1].circle(
                (x, y), r1,
                fill=stroke, fill_opacity=1, fill_rule="evenodd"
            )
        )  # 圆形滑块的伪阴影边框
        drawing[1].add(
            drawing[1].circle(
                (x, y), r1 - 1,
                fill=fill, fill_opacity=fill_opacity, fill_rule="nonzero"
            )
        )  # 圆形滑块的外填充
        drawing[1].add(
            drawing[1].circle(
                (x, y), r2,
                fill=inner_fill, fill_opacity=inner_fill_opacity, fill_rule="nonzero"
            )
        )  # 圆形滑块的内填充
        drawing[1].save()
        return drawing[0]


class FluSliderCanvas(DCanvas):
    draw = FluSliderDraw

    def create_slider(self,
                      x1, y1, x2, y2, x3, r1, r2, temppath=None,
                      fill="transparent", fill_opacity=1, radius=3,
                      outline="transparent", outline_opacity=1,
                      outline2="transparent", outline2_opacity=1,
                      inner_fill="transparent", inner_fill_opacity=1,
                      track_fill="transparent", track_height=4, track_opacity=1,
                      rail_fill="transparent", rail_opacity=1
                      ):
        self._img = self.svgdraw.create_slider(
            x1, y1, x2, y2, x3, r1, r2, temppath=temppath,
            fill=fill, fill_opacity=fill_opacity, radius=radius,
            outline=outline, outline_opacity=outline_opacity,
            outline2=outline2, outline2_opacity=outline2_opacity,
            inner_fill=inner_fill, inner_fill_opacity=inner_fill_opacity,
            track_fill=track_fill, track_height=track_height, track_opacity=track_opacity,
            rail_fill=rail_fill, rail_opacity=rail_opacity
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)


class FluSlider(FluSliderCanvas, DDrawWidget):
    def __init__(self, *args,
                 text="",
                 width=70,
                 height=28,
                 font=None,
                 mode="light",
                 state="normal",
                 value=20,
                 max=100,
                 min=0,
                 **kwargs
                 ):

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

        self._init(mode)

        self.dconfigure(
            state=state,
            value=value,
            max=max, min=min,
        )

        super().__init__(*args, width=width, height=height, **kwargs)

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")

        self.bind("<Motion>", self._event_button1_motion)

        from .defs import set_default_font
        set_default_font(font, self.attributes)

    def _init(self, mode):
        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "command": None,
                "state": None,

                "value": 20,
                "max": 100,
                "min": 0,

                "rest": {},
                "hover": {},
                "pressed": {},
                "disabled": {},
            }
        )

        self.theme(mode)

    def _draw(self, event=None):

        """
        重新绘制组件

        :param event:
        """

        super()._draw(event)

        #print("width:", self.winfo_width(), "\n", "height:", self.winfo_height(), sep="")

        #print("")

        self.delete("all")

        state = self.dcget("state")

        _dict = None

        if state == "normal":
            if event:
                if self.enter:
                    if self.button1:
                        _dict = self.attributes.pressed
                    else:
                        _dict = self.attributes.hover
                else:
                    _dict = self.attributes.rest
            else:
                _dict = self.attributes.rest
        else:
            _dict = self.attributes.disabled

        _radius = _dict.radius

        _track_height = _dict.track.width
        _track_back_color = _dict.track.back_color
        _track_back_opacity = _dict.track.back_opacity

        _rail_back_color = _dict.rail.back_color
        _rail_back_opacity = _dict.rail.back_opacity

        _thumb_radius = _dict.thumb.radius
        _thumb_inner_radius = _dict.thumb.inner_radius

        _thumb_back_color = _dict.thumb.back_color
        _thumb_back_opacity = _dict.thumb.back_opacity

        _thumb_border_color = _dict.thumb.border_color
        _thumb_border_color_opacity = _dict.thumb.border_color_opacity

        _thumb_border_color2 = _dict.thumb.border_color2
        _thumb_border_color2_opacity = _dict.thumb.border_color2_opacity

        _thumb_inner_back_color = _dict.thumb.inner_back_color
        _thumb_inner_back_opacity = _dict.thumb.inner_back_opacity

        thumb_xp = self.attributes.value / (self.attributes.max - self.attributes.min)  # 滑块对应数值的比例
        thumb_x = (self.winfo_width() - (_thumb_radius + 4) * 2) * thumb_xp  # 滑块对应数值的x左边

        self.attributes["^r"] = _thumb_radius  # 滑块进度条x坐标
        self.attributes["^x"] = _thumb_radius - 4  # 滑块进度条
        self.attributes["^xx"] = self.winfo_width() - _thumb_radius + 4

        self.element_thumb = self.create_slider(
            0, 0, self.winfo_width(), self.winfo_height(), thumb_x, _thumb_radius, _thumb_inner_radius,
            temppath=self.temppath,
            fill=_thumb_back_color, fill_opacity=_thumb_back_opacity, radius=_radius,
            outline=_thumb_border_color, outline_opacity=_thumb_border_color_opacity,
            outline2=_thumb_border_color2, outline2_opacity=_thumb_border_color2_opacity,
            inner_fill=_thumb_inner_back_color, inner_fill_opacity=_thumb_inner_back_opacity,
            track_height=_track_height, track_fill=_track_back_color, track_opacity=_track_back_opacity,
            rail_fill=_rail_back_color, rail_opacity=_rail_back_opacity
        )

    def pos(self, event):
        if self.enter:
            if self.button1:
                valuep = (event.x - self.attributes["^x"]) / (self.attributes["^xx"] - self.attributes["^x"]) # 数值的比例：(鼠标点击的x坐标 - 滑块进度条的x坐标) ÷ 滑块进度条的宽度
                value = (event.x - self.attributes["max"] - self.attributes["min"])  # 数值的比例 × 数值范围(最大数值 - 最小数值)
                value = ((event.x + self.attributes["^r"]) / (self.winfo_width())) * self.attributes.max
                self.dconfigure(
                    value=value
                )
                #print("value:", value, sep="")
                #print("")

    def _event_button1_motion(self, event):
        self.pos(event)

    def _event_on_button1(self, event=None):
        super()._event_on_button1(event=event)
        self.pos(event)

    def theme(self, mode=None):
        if mode:
            self.mode = mode
        if self.mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _theme(self, mode):
        r = slider(mode, "rest")
        h = slider(mode, "hover")
        p = slider(mode, "pressed")
        d = slider(mode, "disabled")
        self.dconfigure(
            rest={
                "radius": r["radius"],
                "thumb": {
                    "radius": r["thumb"]["radius"],
                    "inner_radius": r["thumb"]["inner_radius"],

                    "back_color": r["thumb"]["back_color"],
                    "back_opacity": r["thumb"]["back_opacity"],

                    "border_color": r["thumb"]["border_color"],
                    "border_color_opacity": r["thumb"]["border_color_opacity"],
                    "border_color2": r["thumb"]["border_color2"],
                    "border_color2_opacity": r["thumb"]["border_color2_opacity"],

                    "inner_back_color": r["thumb"]["inner_back_color"],
                    "inner_back_opacity": r["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": r["track"]["back_color"],
                    "back_opacity": r["track"]["back_opacity"],
                    "width": r["track"]["width"]
                },
                "rail": {
                    "back_color": r["rail"]["back_color"],
                    "back_opacity": r["rail"]["back_opacity"],
                }
            },
            hover={
                "radius": h["radius"],
                "thumb": {
                    "radius": h["thumb"]["radius"],
                    "inner_radius": h["thumb"]["inner_radius"],

                    "back_color": h["thumb"]["back_color"],
                    "back_opacity": h["thumb"]["back_opacity"],

                    "border_color": h["thumb"]["border_color"],
                    "border_color_opacity": h["thumb"]["border_color_opacity"],
                    "border_color2": h["thumb"]["border_color2"],
                    "border_color2_opacity": h["thumb"]["border_color2_opacity"],

                    "inner_back_color": h["thumb"]["inner_back_color"],
                    "inner_back_opacity": h["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": h["track"]["back_color"],
                    "back_opacity": h["track"]["back_opacity"],
                    "width": h["track"]["width"]
                },
                "rail": {
                    "back_color": h["rail"]["back_color"],
                    "back_opacity": h["rail"]["back_opacity"],
                }
            },
            pressed={
                "radius": p["radius"],
                "thumb": {
                    "radius": p["thumb"]["radius"],
                    "inner_radius": p["thumb"]["inner_radius"],

                    "back_color": p["thumb"]["back_color"],
                    "back_opacity": p["thumb"]["back_opacity"],

                    "border_color": p["thumb"]["border_color"],
                    "border_color_opacity": p["thumb"]["border_color_opacity"],
                    "border_color2": p["thumb"]["border_color2"],
                    "border_color2_opacity": p["thumb"]["border_color2_opacity"],

                    "inner_back_color": p["thumb"]["inner_back_color"],
                    "inner_back_opacity": p["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": p["track"]["back_color"],
                    "back_opacity": p["track"]["back_opacity"],
                    "width": p["track"]["width"]
                },
                "rail": {
                    "back_color": p["rail"]["back_color"],
                    "back_opacity": p["rail"]["back_opacity"],
                }
            },
            disabled={
                "radius": d["radius"],
                "thumb": {
                    "radius": d["thumb"]["radius"],
                    "inner_radius": d["thumb"]["inner_radius"],

                    "back_color": d["thumb"]["back_color"],
                    "back_opacity": d["thumb"]["back_opacity"],

                    "border_color": d["thumb"]["border_color"],
                    "border_color_opacity": d["thumb"]["border_color_opacity"],
                    "border_color2": d["thumb"]["border_color2"],
                    "border_color2_opacity": d["thumb"]["border_color2_opacity"],

                    "inner_back_color": d["thumb"]["inner_back_color"],
                    "inner_back_opacity": d["thumb"]["inner_back_opacity"],
                },
                "track": {
                    "back_color": d["track"]["back_color"],
                    "back_opacity": d["track"]["back_opacity"],
                    "width": d["track"]["width"]
                },
                "rail": {
                    "back_color": d["rail"]["back_color"],
                    "back_opacity": d["rail"]["back_opacity"],
                }
            }
        )

    def _light(self):
        self._theme("light")

    def _dark(self):
        self._theme("dark")
