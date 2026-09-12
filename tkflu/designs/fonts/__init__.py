"""字体加载。

内嵌 Segoe UI 与 Segoe Fluent Icons 字体文件，
优先用 ``tkextrafont`` 加载以保证跨平台一致；失败时回退到系统字体。"""

from os.path import abspath, dirname, join

path = abspath(dirname(__file__))

segoefont = join(path, "segoeui.ttf")
segoefluenticons = join(path, "segoe_fluent_icons.ttf")


def SegoeFont(size=9, weight="normal"):
    from _tkinter import TclError

    try:
        from tkextrafont import Font

        font = Font(file=segoefont, size=size, family="Segoe UI")
    except TclError:
        try:
            from tkinter.font import Font

            font = Font(size=size, family="Segoe UI", weight=weight)
        except TclError:
            from tkinter.font import nametofont

            font = nametofont("TkDefaultFont").configure(size=size, weight=weight)
    return font


def SegoeFluentIcons(size=9, weight="normal", *args, **kwargs):
    from _tkinter import TclError

    try:
        from tkextrafont import Font

        font = Font(
            file=segoefluenticons,
            size=size,
            family="Segoe Fluent Icons",
            *args,
            **kwargs
        )
    except TclError:
        try:
            from tkinter.font import Font

            font = Font(size=size, family="Segoe Fluent Icons", *args, **kwargs)
        except TclError:
            from tkinter.font import nametofont

            font = nametofont("TkDefaultFont").configure(size=size, weight=weight)
    return font
