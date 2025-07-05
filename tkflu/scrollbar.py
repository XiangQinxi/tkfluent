from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.drawwidget import DDrawWidget


class FluScrollBarDraw(DSvgDraw):
    def create_track(
            self,
            x1, y1, x2, y2, radius, radiusy=None, temppath=None,
            fill="transparent"
    ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill,
            )
        )
        drawing[1].save()
        return drawing[0]

    def create_thumb(
            self,
            x1, y1, x2, y2, radius, radiusy=None, temppath=None,
            fill="transparent"
    ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill,
            )
        )
        drawing[1].save()
        return drawing[0]


class FluScrollBarCanvas(DCanvas):
    draw = FluScrollBarDraw

    def create_track(
            self,
            x1, y1, x2, y2, r1, r2=None, temppath=None,
            fill="transparent"
    ):
        self._img = self.svgdraw.create_track(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill
        )
        self._tkimg = self.svgdraw.create_tksvg_image(self._img)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    def create_thumb(
            self,
            x1, y1, x2, y2, r1, r2=None, temppath=None,
            fill="transparent"
    ):
        self._img2 = self.svgdraw.create_thumb(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill
        )
        self._tkimg2 = self.svgdraw.create_tksvg_image(self._img2)
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg2)


from .constants import MODE
from typing import Union
from tkinter import Event


class FluScrollBar(FluScrollBarCanvas, DDrawWidget):
    def __init__(self, *args,
                 width=None,
                 height=None,
                 command=None,
                 state="normal",
                 mode="light",
                 orient= "vertical",
                 **kwargs):
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


        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:
            def empty(): pass

            command = empty

        self.dconfigure(
            command=command,
            state=state,
            orient=orient
        )

        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.attributes.command(), add="+")

    def _init(self, mode: MODE = "light"):
        from easydict import EasyDict

        self.enter = False
        self.button1 = False

        self.thumb_height = 100
        self.thumb_y = 10

        self.attributes = EasyDict(
            {
                "command": None,
                "state": "normal",
                "expanded": False,
                "orient": "vertical",

                "rest": {},
                "expand": {},
                "disabled": {}
            }
        )

        self.theme(mode=mode)


    def theme(self, mode: MODE = None):
        if mode:
            self.mode = mode
        from .designs.scrollbar import scrollbar
        m = scrollbar(mode)
        self.attributes.rest = m["rest"]
        self.attributes.expand = m["expand"]
        self.attributes.disabled = m["disabled"]

    def _event_enter(self, event=None):
        self.enter = True
        self.attributes.expanded = True

        self._draw(event)

    def _event_leave(self, event=None):
        self.enter = False
        self.attributes.expanded = False

        self._draw(event)

    def set(self, start=None, end=None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

        orient = self.dcget("orient")
        width = self.winfo_width()
        height = self.winfo_height()

        if orient == "vertical":
            # 计算垂直滑块位置 (轨道高度 = 总高度 - 20px 边距)
            track_height = height - 20
            thumb_y1 = 10 + self.start * track_height
            thumb_y2 = 10 + self.end * track_height

            # 更新滑块坐标
            if hasattr(self, 'element_thumb'):
                self.coords(self.element_thumb,
                            1, thumb_y1,
                            width - 1, thumb_y2)
        else:
            # 计算水平滑块位置 (轨道宽度 = 总宽度 - 20px 边距)
            track_width = width - 20
            thumb_x1 = 10 + self.start * track_width
            thumb_x2 = 10 + self.end * track_width

            # 更新滑块坐标
            if hasattr(self, 'element_thumb'):
                self.coords(self.element_thumb,
                            thumb_x1, 1,
                            thumb_x2, height - 1)

    def _draw(self, event: Union[Event, None] = None, tempcolor: Union[dict, None] = None):
        """

        Parameters:
          绘制按钮
        """
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()
        # 提前定义，反正多次调用浪费资源

        state = self.dcget("state")
        orient = self.dcget("orient")
        expanded = self.dcget("expanded")

        _dict = None

        if not tempcolor:
            if state == "normal":
                if self.attributes.expanded:
                    _dict = self.attributes.expand
                else:
                    _dict = self.attributes.rest
            else:
                _dict = self.attributes.disabled

            _thumb_color = _dict.thumb_color
            if hasattr(_dict, "track_color"):
                _track_color = _dict.track_color
            else:
                _track_color = None
            _radius = _dict.radius
        else:
            _thumb_color = tempcolor.thumb_color
            _track_color = tempcolor.track_color

        self.delete("all")

        if expanded:
            if orient == "vertical":
                self.element_track = self.create_track(
                    0, 0, width, height, _radius, temppath=self.temppath,
                    fill=_track_color,
                )

                self.element_thumb = self.create_thumb(
                    1, 10, width-1, height-10, _radius, temppath=self.temppath2,
                    fill=_thumb_color,
                )
            else:
                self.element_track = self.create_track(
                    0, 0, width, height, _radius, temppath=self.temppath,
                    fill=_track_color,
                )

                self.element_thumb = self.create_thumb(
                    0, 0, width, height, _radius, temppath=self.temppath2,
                    fill=_thumb_color,
                )
        else:
            if orient == "vertical":
                self.element_thumb = self.create_thumb(
                    3, 10, width-1, height-10, _radius, temppath=self.temppath2,
                    fill=_thumb_color,
                )

        self.update()


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