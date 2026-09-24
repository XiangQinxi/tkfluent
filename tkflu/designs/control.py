"""控件通用配色（中性色 / 文本色 / 焦点环）。

Windows 的 Fluent 设计规范里，这些颜色大多写成 **带 alpha 的黑色或白色**
（例如 ``TextFillColorPrimary = #E4000000``）。tkinter 的 ``create_text``
只认**实色** ``fill``，没有透明度参数，所以：

* 走画布图元（圆角矩形、圆形）的部分，把颜色 + 透明度一起交给引擎，
  由引擎自己合成——这是 :mod:`tkflu.designs.checkbox` 等模块返回
  ``*_opacity`` 字段的用途；
* 走 ``create_text`` 的文字，必须先在这里按背景色**合成成实色**。

本模块就是干第二件事的：:func:`blend` 把半透明前景压到不透明背景上，
得到该主题下"看起来一样"的实色十六进制值。

.. note::
   :func:`blend` 只支持 ``#rrggbb`` 形式的十六进制输入，且背景必须不透明。
   这是刻意的：设计规范里的背景要么是面板色要么是窗口色，都是实色。
"""

__all__ = ["blend", "TEXT", "NEUTRAL", "FOCUS", "SURFACE", "GLYPH_DISABLED"]

#: 文字合成时假定的背景色（与 :mod:`tkflu.designs.frame` 的面板底色一致）
SURFACE = {"light": "#ffffff", "dark": "#2b2b2b"}

#: 正文 / 次要 / 禁用文字（**实色**，可直接喂给 ``create_text``）
TEXT = {
    "light": {
        "primary": "#1b1b1b",
        "secondary": "#616161",
        "disabled": "#a2a2a2",
        "on_accent": "#ffffff",
    },
    "dark": {
        "primary": "#ffffff",
        "secondary": "#d2d2d2",
        "disabled": "#787878",
        "on_accent": "#000000",
    },
}

#: 中性控件（复选框的方框、单选框的圆环）在四种交互状态下的描边/填充。
#: 数值来源：Fluent 的 ``ControlStrokeColorDefault`` / ``ControlFillColor*``。
NEUTRAL = {
    "light": {
        "rest": {"border": "#8d8d8d", "fill": None},
        "hover": {"border": "#626262", "fill": "#f9f9f9"},
        "pressed": {"border": "#8d8d8d", "fill": "#f0f0f0"},
        "disabled": {"border": "#c8c8c8", "fill": None},
    },
    "dark": {
        "rest": {"border": "#9f9f9f", "fill": None},
        "hover": {"border": "#d2d2d2", "fill": "#323232"},
        "pressed": {"border": "#9f9f9f", "fill": "#383838"},
        "disabled": {"border": "#4d4d4d", "fill": None},
    },
}

#: 勾选类控件在**禁用**状态下的图形色（勾号 / 圆点）。
#: 不能直接沿用 ``on_accent``：禁用态下底色不再是强调色，对比度会掉到看不清。
GLYPH_DISABLED = {"light": "#ffffff", "dark": "#787878"}

#: 焦点环（键盘 Tab 到控件时画在方框/圆环外侧的一圈）
FOCUS = {"light": "#000000", "dark": "#ffffff"}


def _to_rgb(color):
    """把 ``#rgb`` / ``#rrggbb`` 解析成 ``(r, g, b)``。

    :raises ValueError: 不是可识别的十六进制颜色
    """
    text = str(color).strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"无法解析颜色 {color!r}，只支持 #rgb / #rrggbb")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def blend(foreground, alpha, background):
    """把半透明的 ``foreground`` 合成到不透明的 ``background`` 上。

    :param foreground: 前景色（``#rgb`` / ``#rrggbb``）
    :param alpha: 前景的不透明度，``0``–``1``
    :param background: 背景色，必须不透明
    :returns: 合成后的实色 ``#rrggbb``

    ::

        >>> blend("#000000", 0.894, "#ffffff")
        '#1b1b1b'
    """
    fg = _to_rgb(foreground)
    bg = _to_rgb(background)
    ratio = max(0.0, min(1.0, float(alpha)))
    mixed = tuple(int(round(f * ratio + b * (1.0 - ratio))) for f, b in zip(fg, bg))
    return "#{:02x}{:02x}{:02x}".format(*mixed)
