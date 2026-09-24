"""轻量导航栏的设计规范。

导航栏本身**不画背景**（``back_color = None``）——它一般贴在窗口或面板的
顶部/左侧，背景交给父容器；需要一块独立色块时用 ``style="card"``。

对照 Windows 的 ``NavigationView``：

* 选中项的指示条是强调色的小圆头条；
* 选中项底只有一层很淡的强调色，文字变成强调色；
* 悬停项是一层很淡的中性色。

这里给的是**整套**调色板（而不是"某个状态下的一个条目"），
对应的实现方式与其它组件一致：控件把它灌进 ``attributes``，
绘制每个条目时按条目自己的状态取值。
"""

from .control import GLYPH_DISABLED, TEXT, blend
from .primary_color import get_primary_color

__all__ = ["litenav", "STYLES"]

#: 支持的样式
STYLES = ("standard", "card")

#: 选中项底色的强调色浓度
_SELECT_TINT = {"light": 0.10, "dark": 0.16}

#: 悬停项底色的中性色浓度
_HOVER_TINT = 0.037

#: 按下项底色的中性色浓度
_PRESSED_TINT = 0.06


def litenav(mode: str = "light", style: str = "standard") -> dict:
    """取导航栏的整套配色。

    :param mode: ``"light"`` / ``"dark"``
    :param style: ``"standard"``（透明底）或 ``"card"``（带圆角卡片底）
    :returns: 配色字典，键与 ``FluLiteNav.attributes`` 一一对应

    :raises ValueError: ``mode`` / ``style`` 无法识别
    """
    mode = str(mode).lower()
    style = str(style).lower()
    if mode not in ("light", "dark"):
        raise ValueError(f"未知的主题模式 {mode!r}；应为 'light' 或 'dark'")
    if style not in STYLES:
        raise ValueError(f"未知的样式 {style!r}；应为 {list(STYLES)} 之一")

    accent = get_primary_color()[0 if mode == "light" else 1]
    surface = "#ffffff" if mode == "light" else "#2b2b2b"
    overlay = "#000000" if mode == "light" else "#ffffff"

    if style == "card":
        back_color = surface
        # 卡片样式下用一点黑描边压住边缘（深浅主题都是黑，只是透明度不同）
        border_color = "#000000"
        border_opacity = 0.0578 if mode == "light" else 0.10
    else:
        back_color = None
        border_color = None
        border_opacity = 0.0

    return {
        "back_color": back_color,
        "back_opacity": 1.0 if back_color else 0.0,
        "border_color": border_color,
        "border_color_opacity": border_opacity,
        "border_width": 1 if style == "card" else 0,
        "radius": 7,
        # 条目
        "item_text_color": TEXT[mode]["primary"],
        "item_disabled_text": TEXT[mode]["disabled"],
        "item_selected_text": accent,
        "item_hover_back": blend(overlay, _HOVER_TINT, surface),
        "item_pressed_back": blend(overlay, _PRESSED_TINT, surface),
        "item_selected_back": blend(accent, _SELECT_TINT[mode], surface),
        "indicator_color": accent,
        "indicator_idle": blend(accent, 0.35, surface),
        # 禁用态的图标/占位色
        "glyph_disabled": GLYPH_DISABLED[mode],
    }
