"""控件通用配色（中性色 / 文本色 / 焦点环）。

数值来源
--------
这一版的数值**直接取自设计稿**（Figma 导出的 ``Basic Input.svg``），
不再是"按 Fluent 印象估的"：

* 复选框方框 / 单选框圆环的未选中描边 = ``rgb(0,0,0)`` + ``stroke-opacity 0.6063``
* 同一个框的填充 = ``rgb(0,0,0)`` + ``fill-opacity 0.0241``
* 选中填充 = ``rgb(0,95,184)``（浅色强调色）
* 禁用选中 = ``rgb(0,0,0)`` + ``0.2169``（来自 ``Lists & Collections.svg``）

为什么要保留"颜色 + 透明度"两个字段，而不是先合成成实色
--------------------------------------------------------
设计稿给的是半透明黑（``#000000`` @ 0.6），它**压在任何背景上都是对的**：
放在白色面板上得到 ``#646464``，放在 ``#2B2B2B`` 的深色面板上得到 ``#161616``。
一旦提前合成成实色，换到深色主题就全错了。所以这里成对返回，
交给绘制引擎自己去合成（圆角矩形、圆环都支持 ``*_opacity``）。

只有 ``create_text`` 没有透明度参数（见 :data:`TEXT`），文字色必须提前合成。
"""

__all__ = [
    "blend",
    "TEXT",
    "NEUTRAL",
    "FOCUS",
    "FOCUS_RING",
    "FOCUS_MARGIN",
    "FOCUS_OUTER_WIDTH",
    "FOCUS_INNER_WIDTH",
    "FOCUS_RADIUS",
    "SURFACE",
    "GLYPH_DISABLED",
    "paint",
]

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

#: 中性控件（复选框方框、单选框圆环）在四种交互状态下的描边 / 填充。
#: 每一项都是 ``(颜色, 不透明度)``，``None`` 表示这一层不画。
#:
#: 下面是**设计稿逐状态量出来的**（``Basic Input.svg`` 的
#: ``Mode=…, State=…, Selected=…`` 变体），不是估的：
#:
#: ========  ==============================  ==============================
#: 状态       浅色                            深色
#: ========  ==============================  ==============================
#: rest      底 #000@0.0241 / 边 #000@0.6063  底 #000@0.1   / 边 #FFF@0.6047
#: hover     底 #000@0.0578 / 边 #000@0.6063  底 #FFF@0.0419/ 边 #FFF@0.6047
#: pressed   底 #000@0.0924 / 边 #000@0.2169  底 #FFF@0.0698/ 边 #FFF@0.1581
#: disabled  底 无           / 边 #000@0.2169  底 无          / 边 #FFF@0.1581
#: ========  ==============================  ==============================
NEUTRAL = {
    "light": {
        "rest": {"border": ("#000000", 0.6063), "fill": ("#000000", 0.0241)},
        "hover": {"border": ("#000000", 0.6063), "fill": ("#000000", 0.0578)},
        "pressed": {"border": ("#000000", 0.2169), "fill": ("#000000", 0.0924)},
        "disabled": {"border": ("#000000", 0.2169), "fill": None},
    },
    "dark": {
        "rest": {"border": ("#ffffff", 0.6047), "fill": ("#000000", 0.1000)},
        "hover": {"border": ("#ffffff", 0.6047), "fill": ("#ffffff", 0.0419)},
        "pressed": {"border": ("#ffffff", 0.1581), "fill": ("#ffffff", 0.0698)},
        "disabled": {"border": ("#ffffff", 0.1581), "fill": None},
    },
}

#: 焦点环。设计稿把它是画在**控件外沿紧贴的 3px 带**上，**两层**：
#: 先铺 3px 的"内色"、再在上面盖 2px 的"外色"，所以看上去是
#: 「外 2px 深 + 内 1px 浅」。浅色主题里外色是 ``#000000 @ 0.8956``（近黑）、
#: 内色是纯白；深色主题反过来。
FOCUS_RING = {
    "light": {"outer": ("#000000", 0.8956), "inner": ("#ffffff", 1.0)},
    "dark": {"outer": ("#ffffff", 1.0), "inner": ("#000000", 0.7000)},
}

#: 焦点带总宽度（设计稿：控件外扩 3px，即总外扩 6）
FOCUS_MARGIN = 3
#: 焦点带里"外色"的宽度（剩下的是内色）
FOCUS_OUTER_WIDTH = 2
#: 焦点带里"内色"的宽度
FOCUS_INNER_WIDTH = 1
#: 复选框焦点矩形的圆角（设计稿：方框圆角 4 + 外扩 3 = 7）
FOCUS_RADIUS = 7

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


def paint(pair, fallback=(None, 0.0)):
    """把 ``(颜色, 不透明度)`` 拆成绘制用的两个字段。

    :param pair: ``(color, opacity)``；``None`` 表示"这一层不画"
    :param fallback: ``pair`` 为空时返回什么
    :returns: ``(color, opacity)``
    """
    if not pair:
        return fallback
    return pair[0], float(pair[1])
