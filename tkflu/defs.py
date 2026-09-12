"""便捷函数集合。

包含主题切换辅助函数与主色调预设（红/橙/黄/绿/蓝/紫）。
这些名字会经由 ``from tkflu import *`` 直接暴露。"""

def toggle_theme(toggle_button, thememanager):
    if toggle_button.dcget("checked"):
        thememanager.mode("dark")
    else:
        thememanager.mode("light")


def set_default_font(font, attributes):
    if font is None:
        from .designs.fonts import SegoeFont

        attributes.font = SegoeFont()


def red_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#d20e1e", "#f46762"))


def orange_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#c53201", "#fe7e34"))


def yellow_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#e19d00", "#ffd52a"))


def green_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#0e6d0e", "#45e532"))


def blue_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#005fb8", "#60cdff"))


def purple_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#4f4dce", "#b5adeb"))
