"""滚动条组件。

``FluScrollBar`` 画出 Fluent 风格的滚动条（轨道 + 滑块），并通过
``command`` 回调与被滚动的控件联动。

与 Tk 原生滚动条的接线方式完全一致：

.. code-block:: python

    import tkinter as tk
    import tkflu

    root = tkflu.FluWindow()
    text = tk.Text(root, wrap="none")
    bar = tkflu.FluScrollBar(root, orient="vertical")
    text.configure(yscrollcommand=bar.set)          # 控件 → 滚动条
    bar.dconfigure(command=text.yview)              # 滚动条 → 控件
    text.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")

``bar.set(first, last)`` 接收两个 ``0``–``1`` 的比例（Tk 会以**字符串**形式传进来，
这里会自己转成浮点）；拖动滑块或点击轨道时，组件按 Tk 约定调用
``command("moveto", 比例)`` / ``command("scroll", 行数, "units")``。

.. note::
   历史实现里 ``set()`` 是坏的：它把比例当数字直接相加（Tk 传的是字符串，
   立刻 ``TypeError``），再用 ``coords(item, x1, y1, x2, y2)`` 去改一个
   **图片**图元——图片只接受 0 个或 2 个坐标，于是抛
   ``TclError: wrong # coordinates``。同时横向滚动条在未展开时不画任何东西
   （整个控件是空的），而滑块长度也从来不看内容比例。
"""

from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget


class FluScrollBarDraw(DSvgDraw):
    """滚动条的 SVG 绘制后端（槽与滑块都是无描边的圆角矩形）。"""

    def create_track(
        self, x1, y1, x2, y2, radius, radiusy=None, temppath=None, fill="transparent"
    ):
        """滚动条的"槽"：一个不描边的圆角矩形。

        :returns: 生成好的 SVG 文件路径
        """
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1),
                (x2 - x1, y2 - y1),
                _rx,
                _ry,
                fill=fill,
            )
        )
        drawing[1].save()
        return drawing[0]

    def create_thumb(
        self, x1, y1, x2, y2, radius, radiusy=None, temppath=None, fill="transparent"
    ):
        """滚动条的滑块：同样是一个不描边的圆角矩形。

        :returns: 生成好的 SVG 文件路径
        """
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1),
                (x2 - x1, y2 - y1),
                _rx,
                _ry,
                fill=fill,
            )
        )
        drawing[1].save()
        return drawing[0]


class FluScrollBarCanvas(DCanvas):
    draw = FluScrollBarDraw

    def create_track(
        self, x1, y1, x2, y2, r1, r2=None, temppath=None, fill="transparent"
    ) -> int:
        """画滚动条的槽。

        :returns: 画布上的 item id

        两条路径：

        * 栅格引擎（skia / pillow / cairo）→ :meth:`tkdeft.windows.canvas.DCanvas.create_roundrect_raster`，
          进程内直接出位图并缓存；
        * 其余引擎 → :class:`FluScrollBarDraw` 的 SVG 实现，再由
          :meth:`tkdeft.windows.canvas.DCanvas.draw_svg_item` 变成画布图片。
        """
        item = self.create_roundrect_raster(
            x1, y1, x2, y2, r1, r2, fill=fill, outline=None, width=0
        )
        if item is not None:
            return item

        path = self.svgdraw.create_track(
            x1, y1, x2, y2, r1, r2, temppath=temppath, fill=fill
        )
        return self.draw_svg_item(path, None, x1, y1)

    def create_thumb(
        self, x1, y1, x2, y2, r1, r2=None, temppath=None, fill="transparent"
    ) -> int:
        """画滚动条的滑块（路径与 :meth:`create_track` 相同）。"""
        item = self.create_roundrect_raster(
            x1, y1, x2, y2, r1, r2, fill=fill, outline=None, width=0
        )
        if item is not None:
            return item

        path = self.svgdraw.create_thumb(
            x1, y1, x2, y2, r1, r2, temppath=temppath, fill=fill
        )
        return self.draw_svg_item(path, None, x1, y1)


from tkinter import Event
from typing import Union

from .constants import MODE


class FluScrollBar(FluScrollBarCanvas, DDrawWidget):
    #: 轨道与控件边缘的距离
    PADDING = 2
    #: 未展开（鼠标不在上面）时滑块的厚度。设计稿实测 2px。
    THIN = 2
    #: 滑块的最小长度，避免内容极长时滑块细成一条线
    MIN_THUMB = 16

    def __init__(
        self,
        *args,
        width=None,
        height=None,
        command=None,
        state="normal",
        mode="light",
        orient="vertical",
        **kwargs
    ):
        """构造滚动条。

        :param width: 宽度；``None`` 时按方向取默认值（竖直 6、水平 120）
        :param height: 高度；``None`` 时按方向取默认值（竖直 120、水平 6）
        :param command: 滚动回调，按 Tk 约定以
            ``("moveto", 比例)`` 或 ``("scroll", 行数, "units")`` 调用
        :param state: ``"normal"`` / ``"disabled"``
        :param mode: ``"light"`` / ``"dark"``
        :param orient: ``"vertical"`` / ``"horizontal"``
        """
        self._init(mode)
        if orient == "horizontal":
            if width is None:
                width = 120
            if height is None:
                height = 6
        else:
            if width is None:
                width = 6
            if height is None:
                height = 120

        # 这些状态必须在 super().__init__() 之前就位：基类构造时会立刻
        # 调用一次 _draw()，而 _draw 要用到它们。
        #: 内容可视区的起点比例（0–1）
        self.start = 0.0
        #: 内容可视区的终点比例（0–1）
        self.end = 1.0
        #: 拖拽滑块时记录起点
        self._drag = None

        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:

            def empty(*args, **kwargs):
                pass

            command = empty

        # orient 要在**第一次绘制之前**就写进属性，否则第一帧会按
        # 默认的 vertical 画一遍，留下一个尺寸不对的滑块。
        self.dconfigure(command=command, state=state, orient=orient)

        self.bind("<B1-Motion>", self._event_drag, add="+")
        self.configure(takefocus=1)

        self._draw()

    def _init(self, mode: MODE = "light"):
        from easydict import EasyDict

        self.enter = False
        self.button1 = False
        self.mode = mode or "light"

        self.attributes = EasyDict(
            {
                "command": None,
                "state": "normal",
                "expanded": False,
                "orient": "vertical",
                "rest": {},
                "expand": {},
                "disabled": {},
            }
        )

        self.theme(mode=mode)

    def theme(self, mode: MODE = None):
        """切换主题。

        :param mode: ``"light"`` / ``"dark"``；省略或传空表示沿用当前值

        .. note::
           旧实现把**参数** ``mode`` 直接交给 ``designs.scrollbar.scrollbar()``，
           而那个函数没有默认值——于是不带参数调用 ``theme()``（换肤时会走到）
           直接 ``AttributeError: 'NoneType' object has no attribute 'lower'``。
        """
        resolved = mode or getattr(self, "mode", None) or "light"
        self.mode = resolved
        from .designs.scrollbar import scrollbar

        m = scrollbar(resolved)
        self.attributes.rest = m["rest"]
        self.attributes.expand = m["expand"]
        self.attributes.disabled = m["disabled"]

    # ------------------------------------------------------------------
    # 内容比例（Tk 的 set(first, last) 协议）
    # ------------------------------------------------------------------
    def set(self, first, last):
        """设置滑块位置与长度（Tk 的 ``yscrollcommand`` / ``xscrollcommand`` 协议）。

        :param first: 可视区起点比例
        :param last: 可视区终点比例

        Tk 传进来的是**字符串**（例如 ``"0.0"`` / ``"0.45"``），这里统一转成
        浮点并夹到 ``0``–``1``；真正的几何在 :meth:`_draw` 里算，
        所以不需要（也不能）直接去改图片图元的坐标。
        """

        def to_float(value, fallback):
            try:
                return float(value)
            except (TypeError, ValueError):
                return fallback

        self.start = max(0.0, min(1.0, to_float(first, self.start)))
        self.end = max(0.0, min(1.0, to_float(last, self.end)))
        if self.end < self.start:
            self.start, self.end = self.end, self.start
        self._draw()

    def get(self):
        """当前可视区的 ``(first, last)`` 比例。"""
        return self.start, self.end

    # ------------------------------------------------------------------
    # 事件
    # ------------------------------------------------------------------
    def _event_enter(self, event=None):
        self.enter = True
        # 禁用状态不展开：展开会改配色与厚度，看起来像"还能拖"
        self.attributes.expanded = self.attributes.state == "normal"
        self._draw(event)

    def _event_leave(self, event=None):
        self.enter = False
        self.attributes.expanded = False
        self._drag = None
        self._draw(event)

    def _event_on_button1(self, event=None):
        """按下：落在滑块上就开始拖；落在轨道上则按页滚动。"""
        if self.attributes.state != "normal":
            return
        if event is not None:
            self.focus_set()
            thumb = self._thumb_box()
            if self._point_in(thumb, event):
                self._drag = {
                    "origin": event.y if self._is_vertical() else event.x,
                    "start": self.start,
                    "length": self.end - self.start,
                }
            else:
                self._scroll_to_event(event)
        super()._event_on_button1(event)

    def _event_off_button1(self, event=None):
        self._drag = None
        super()._event_off_button1(event)

    def _event_drag(self, event=None):
        """拖动滑块：按 Tk 约定发 ``moveto``。"""
        if self._drag is None or event is None:
            return
        box = self._track_box()
        span = (box[3] - box[1]) if self._is_vertical() else (box[2] - box[0])
        if span <= 0:
            return
        position = event.y if self._is_vertical() else event.x
        delta = (position - self._drag["origin"]) / span
        target = max(0.0, min(1.0 - self._drag["length"], self._drag["start"] + delta))
        self.start = target
        self.end = target + self._drag["length"]
        self._draw()
        self._emit("moveto", target)

    def _scroll_to_event(self, event):
        """点在轨道上：把滑块中心挪到点击处。"""
        box = self._track_box()
        span = (box[3] - box[1]) if self._is_vertical() else (box[2] - box[0])
        if span <= 0:
            return
        position = event.y if self._is_vertical() else event.x
        fraction = (position - (box[1] if self._is_vertical() else box[0])) / span
        length = self.end - self.start
        target = max(0.0, min(1.0 - length, fraction - length / 2.0))
        self.start = target
        self.end = target + length
        self._draw()
        self._emit("moveto", target)

    def _emit(self, *args):
        """按 Tk 约定调用 ``command``（同时容忍零参数的老写法）。"""
        from .defs import call_command

        call_command(self.attributes.command, *args)

    # ------------------------------------------------------------------
    # 几何
    # ------------------------------------------------------------------
    def _is_vertical(self):
        return str(self.attributes.orient).lower() != "horizontal"

    def _track_box(self):
        """轨道的 ``(x1, y1, x2, y2)``。"""
        pad = self.PADDING
        return (pad, pad, max(pad + 1, self.winfo_width() - pad),
                max(pad + 1, self.winfo_height() - pad))

    def _thumb_box(self):
        """滑块的 ``(x1, y1, x2, y2)``。"""
        box = self._track_box()
        vertical = self._is_vertical()
        span = (box[3] - box[1]) if vertical else (box[2] - box[0])
        thumb_length = max(self.MIN_THUMB, (self.end - self.start) * span)
        thumb_length = min(thumb_length, span)

        if vertical:
            y1 = box[1] + self.start * span
            y2 = min(box[3], y1 + thumb_length)
        else:
            x1 = box[0] + self.start * span
            x2 = min(box[2], x1 + thumb_length)

        if self.attributes.expanded:
            return (box[0], y1, box[2], y2) if vertical else (x1, box[1], x2, box[3])

        # 未展开：只画一条细滑块，居中
        if vertical:
            center = (box[0] + box[2]) / 2.0
            return (center - self.THIN / 2.0, y1, center + self.THIN / 2.0, y2)
        center = (box[1] + box[3]) / 2.0
        return (x1, center - self.THIN / 2.0, x2, center + self.THIN / 2.0)

    @staticmethod
    def _point_in(box, event):
        return box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------
    def _draw(
        self, event: Union[Event, None] = None, tempcolor: Union[dict, None] = None
    ):
        """重绘滚动条。"""
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return

        state = self.dcget("state")
        expanded = bool(self.dcget("expanded")) and state == "normal"

        if not tempcolor:
            if state == "normal":
                _dict = self.attributes.expand if expanded else self.attributes.rest
            else:
                _dict = self.attributes.disabled

            _thumb_color = _dict.thumb_color
            # 禁用态的配色表里没有 track_color。旧实现直接用 None 去当
            # SVG 的 fill，svgwrite 会抛
            # "TypeError: 'None' is not a valid value for attribute 'fill'"——
            # 也就是"鼠标划过禁用的滚动条就报错"。
            _track_color = getattr(_dict, "track_color", None) or _dict.thumb_color
            _radius = _dict.radius
        else:
            _thumb_color = tempcolor.thumb_color
            _track_color = getattr(tempcolor, "track_color", None) or _thumb_color
            # tempcolor 分支过去漏了 _radius，下面用到时直接
            # UnboundLocalError。
            _radius = getattr(tempcolor, "radius", 2)

        self.delete("all")

        if expanded:
            self.element_track = self.create_track(
                0,
                0,
                width,
                height,
                _radius,
                temppath=self.temppath,
                fill=_track_color,
            )

        thumb = self._thumb_box()
        # 两种方向、展开与否都要画滑块——旧实现只在"竖直且未展开"时画，
        # 于是横向滚动条静止时整个控件是空的。
        self.element_thumb = self.create_thumb(
            thumb[0],
            thumb[1],
            thumb[2],
            thumb[3],
            _radius,
            temppath=self.temppath2,
            fill=_thumb_color,
        )

        self.update_idletasks()


"""
def add_scrollbar(self,pos:tuple,widget,height:int=200,direction='y',bg='#f0f0f0',color='#999999',oncolor='#89898b'):#绘制滚动条
    #滚动条宽度7px，未激活宽度3px；建议与widget相隔5xp
    def enter(event):#鼠标进入
        self.itemconfig(sc,outline=oncolor,width=7)
    def leave(event):#鼠标离开
        self.itemconfig(sc,outline=color,width=3)
    def widget_move(sp,ep):#控件控制滚动条滚动
        if mode=='y' and use_widget:
            startp=start+canmove*float(sp)
            endp=start+canmove*float(ep)
            self.coords(sc,(pos[0]+5,startp+5,pos[0]+5,endp-5))
        elif mode=='x' and use_widget:
            startp=start+canmove*float(sp)
            endp=start+canmove*float(ep)
            self.coords(sc,(startp+5,pos[1]+5,endp+5,pos[1]+5))
    def mousedown(event):
        nonlocal use_widget#当该值为真，才允许响应widget_move函数
        use_widget=False
        if mode=='y':
            scroll.start=self.canvasy(event.y)#定义起始纵坐标
        elif mode=='x':
            scroll.start=self.canvasx(event.x)#横坐标
    def mouseup(event):
        nonlocal use_widget
        use_widget=True
    def drag(event):
        bbox=self.bbox(sc)
        if mode=='y':#纵向
            move=self.canvasy(event.y)-scroll.start#将窗口坐标转化为画布坐标
            #防止被拖出范围
            if bbox[1]+move<start-1 or bbox[3]+move>end+1:
                return
            self.move(sc,0,move)
        elif mode=='x':#横向
            move=self.canvasx(event.x)-scroll.start
            if bbox[0]+move<start-1 or bbox[2]+move>end+1:
                return
            self.move(sc,move,0)
        #重新定义画布中的起始拖动位置
        scroll.start+=move
        sc_move()
    def topmove(event):#top
        bbox=self.bbox(sc)
        if mode=='y':
            move=-(bbox[3]-bbox[1])/2
            if bbox[1]+move<start:
                move=-(bbox[1]-start)
            self.move(sc,0,move)
        elif mode=='x':
            move=-(bbox[2]-bbox[0])/2
            if bbox[0]+move<start:
                move=-(bbox[0]-start)
            self.move(sc,move,0)
        sc_move()
    def bottommove(event):#bottom
        bbox=self.bbox(sc)
        if mode=='y':
            move=(bbox[3]-bbox[1])/2
            if bbox[3]+move>end:
                move=(end-bbox[3])
            self.move(sc,0,move)
        elif mode=='x':
            move=(bbox[2]-bbox[0])/2
            if bbox[2]+move>end:
                move=(end-bbox[2])
            self.move(sc,0,move)
        sc_move()
    def backmove(event):#back
        bbox=self.bbox(sc)
        if mode=='y':
            posy=self.canvasy(event.y)
            move=posy-bbox[1]
            if move>0 and move+bbox[3]>end:
                move=end-bbox[3]
            if move<0 and move+bbox[1]<start:
                move=start-bbox[1]
            self.move(sc,0,move)
        elif mode=='x':
            posx=self.canvasx(event.x)
            move=posx-bbox[0]
            if move>0 and move+bbox[2]>end:
                move=end-bbox[2]
            if move<0 and move+bbox[0]<start:
                move=start-bbox[0]
            self.move(sc,move,0)
        sc_move()
    def sc_move():#滚动条控制控件滚动
        bbox=self.bbox(sc)
        if mode=='y':
            startp=(bbox[1]-start)/canmove
            widget.yview('moveto',startp)
        elif mode=='x':
            startp=(bbox[0]-start)/canmove
            widget.xview('moveto',startp*1.2)
    if direction.upper()=='X':
        mode='x'
    elif direction.upper()=='Y':
        mode='y'
    else:
        return None
    #上标、下标 ▲▼
    if mode=='y':
        #back=self.create_rectangle((pos[0],pos[1],pos[0]+10,pos[1]+height),fill=bg,width=0)
        back=self.create_polygon((pos[0]+5,pos[1]+5,pos[0]+5,pos[1]+height-5,pos[0]+5,pos[1]+5),
        width=12,outline=bg)
        uid='scrollbar'+str(back)
        self.itemconfig(back,tags=uid)
        top=self.create_text(pos,text='▲',font='微软雅黑 8',anchor='nw',fill=oncolor,tags=uid)
        bottom=self.create_text((pos[0],pos[1]+height),text='▼',font='微软雅黑 8',anchor='sw',fill=oncolor,tags=uid)
        #sc=self.create_rectangle((pos[0],pos[1]+15,pos[0]+10,pos[1]+height-15),fill=color,width=0,tags=uid)
        sc=self.create_polygon((pos[0]+5,pos[1]+20,pos[0]+5,pos[1]+height-20,pos[0]+5,pos[1]+20,),
        width=3,outline=color,tags=uid)
        #起始和终止位置
        start=pos[1]+15
        end=pos[1]+height-15
        canmove=end-start
        #绑定组件
        widget.config(yscrollcommand=widget_move)
    elif mode=='x':
        back=self.create_polygon((pos[0]+5,pos[1]+5,pos[0]+height-5,pos[1]+5,pos[0],pos[1]+5),
        width=12,outline=bg)
        uid='scrollbar'+str(back)
        self.itemconfig(back,tags=uid)
        top=self.create_text((pos[0]+2,pos[1]+11),text='▲',angle=90,font='微软雅黑 8',anchor='w',fill=oncolor,tags=uid)
        bottom=self.create_text((pos[0]+height,pos[1]),text='▼',angle=90,font='微软雅黑 8',anchor='se',fill=oncolor,tags=uid)
        sc=self.create_polygon((pos[0]+20,pos[1]+5,pos[0]+height-20,pos[1]+5,pos[0]+20,pos[1]+5),
        width=3,outline=color,tags=uid)
        start=pos[0]+8
        end=pos[0]+height-13
        canmove=(end-start)*0.95
        widget.config(xscrollcommand=widget_move)
    scroll=TinUINum()
    use_widget=True#是否允许控件控制滚动条
    self.tag_bind(sc,'<Button-1>',mousedown)
    self.tag_bind(sc,'<ButtonRelease-1>',mouseup)
    self.tag_bind(sc,'<B1-Motion>',drag)
    #绑定样式
    self.tag_bind(sc,'<Enter>',enter)
    self.tag_bind(sc,'<Leave>',leave)
    #绑定点击滚动
    self.tag_bind(top,'<Button-1>',topmove)
    self.tag_bind(bottom,'<Button-1>',bottommove)
    self.tag_bind(back,'<Button-1>',backmove)
    return top,bottom,back,sc,uid

"""
