"""字体加载。

内嵌 Segoe UI 与 Segoe Fluent Icons 字体文件，
优先用 ``tkextrafont`` 加载以保证跨平台一致；失败时回退到系统字体。"""

from os.path import abspath, dirname, join

path = abspath(dirname(__file__))

segoefont = join(path, "segoeui.ttf")
segoefluenticons = join(path, "segoe_fluent_icons.ttf")


def SegoeFont(size=9, weight="normal", master=None):
    """加载一份 Segoe UI 字体对象。

    :param size: 字号
    :param weight: 字重（``"normal"`` / ``"bold"``）
    :param master: 目标 Tk 控件；**多解释器场景必须传**。

    .. warning::
       不传 ``master`` 时，``tkextrafont`` / ``tkinter.font`` 都会把字体注册到
       ``tkinter._default_root`` 所属的那个解释器上。同一个进程里开了第二个
       ``FluWindow`` 时，第二个解释器并不认识这个名字，Tk 会**静默退回**
       系统兜底字体（实测变成"宋体 18"），文字又大又难看。
       组件层统一通过 :func:`tkflu.defs.set_default_font` 传入自己的 ``master``。
    """
    from _tkinter import TclError

    try:
        from tkextrafont import Font

        font = Font(file=segoefont, size=size, family="Segoe UI", root=master)
    except TclError:
        try:
            from tkinter.font import Font

            font = Font(root=master, size=size, family="Segoe UI", weight=weight)
        except TclError:
            from tkinter.font import nametofont

            font = nametofont("TkDefaultFont")
            font.configure(size=size, weight=weight)
    return font


def SegoeFluentIcons(size=9, weight="normal", *args, **kwargs):
    """加载一份 Segoe Fluent Icons 字体对象。

    :param kwargs: 可含 ``master``（多解释器场景必须传，理由同 :func:`SegoeFont`）
    """
    from _tkinter import TclError

    master = kwargs.pop("master", None)

    try:
        from tkextrafont import Font

        font = Font(
            root=master,
            file=segoefluenticons,
            size=size,
            family="Segoe Fluent Icons",
            *args,
            **kwargs
        )
    except TclError:
        try:
            from tkinter.font import Font

            font = Font(
                root=master,
                size=size,
                family="Segoe Fluent Icons",
                *args,
                **kwargs
            )
        except TclError:
            from tkinter.font import nametofont

            font = nametofont("TkDefaultFont")
            font.configure(size=size, weight=weight)
    return font
