"""列表的设计规范。

:func:`listbox` 返回列表控件在某个状态下的整套配色：控件底色与描边、
条目的悬停/选中高亮、选中指示条，以及自绘滚动条的滑块。

列表的描边沿用历史上的一点点"上浅下深"竖直渐变
（``border_color`` → ``border_color2``），与
:meth:`tkflu.listbox.FluListBoxCanvas.create_round_rectangle` 里传的
``gradient_stop1/2`` 对应。

高亮色的算法
------------
标准样式下是"把强调色按很低的比例压到控件底色上"，得到一行淡蓝；
强调样式下控件本身就是强调色，再压强调色等于没压，所以改成往
``on_accent``（浅色强调 → 白、深色强调 → 黑）方向混合。
"""

from .control import NEUTRAL, TEXT, blend
from .primary_color import get_primary_color

__all__ = ["listbox"]

#: 圆角半径（与历史占位实现一致）
RADIUS = 6

#: 标准样式下选中项里强调色的浓度（越低越像 Windows 的浅色高亮）
_SELECT_TINT = {"light": 0.16, "dark": 0.22}

#: 标准样式下悬停行的中性色浓度
_HOVER_TINT = 0.037


def listbox(mode: str = "light", style: str = "standard", state: str = "rest") -> dict:
    """取列表控件在某个状态下的配色。

    :param mode: ``"light"`` / ``"dark"``
    :param style: ``"standard"`` / ``"accent"``
    :param state: ``"rest"`` / ``"hover"`` / ``"pressed"`` / ``"disabled"``
    :returns: 配色字典，键与 ``FluListBox.attributes`` 一一对应

    :raises ValueError: ``mode`` / ``style`` / ``state`` 无法识别
    """
    mode = str(mode).lower()
    style = str(style).lower()
    state = str(state).lower()
    if mode not in ("light", "dark"):
        raise ValueError(f"未知的主题模式 {mode!r}；应为 'light' 或 'dark'")
    if style not in ("standard", "accent"):
        raise ValueError(f"未知的样式 {style!r}；应为 'standard' 或 'accent'")
    if state not in NEUTRAL[mode]:
        raise ValueError(f"未知的状态 {state!r}；应为 {sorted(NEUTRAL[mode])} 之一")

    accent = get_primary_color()[0 if mode == "light" else 1]
    surface = "#ffffff" if mode == "light" else "#2b2b2b"
    disabled = state == "disabled"

    if style == "accent":
        back_color = border_color = border_color2 = accent
        item_overlay = TEXT[mode]["on_accent"]
        selected_back = blend(item_overlay, 0.22, back_color)
        hover_back = blend(item_overlay, 0.12, back_color)
        indicator_color = item_overlay
    else:
        back_color = surface
        border_color = "#f0f0f0" if mode == "light" else "#3a3a3a"
        border_color2 = "#d6d6d6" if mode == "light" else "#262626"
        selected_back = blend(accent, _SELECT_TINT[mode], back_color)
        hover_back = blend(
            "#000000" if mode == "light" else "#ffffff", _HOVER_TINT, back_color
        )
        indicator_color = accent

    text_color = TEXT[mode]["primary"]
    if style == "accent":
        text_color = TEXT[mode]["on_accent"]
    if disabled:
        text_color = TEXT[mode]["disabled"]
        hover_back = selected_back if style == "accent" else blend(
            "#000000" if mode == "light" else "#ffffff", 0.02, back_color
        )

    return {
        "back_color": back_color,
        "border_color": border_color,
        "border_color2": border_color2,
        "border_width": 1,
        "radius": RADIUS,
        "text_color": text_color,
        # 条目
        "item_text_color": text_color,
        "item_hover_back": hover_back,
        "item_selected_back": selected_back,
        "item_selected_text": text_color,
        "indicator_color": indicator_color,
        # 自绘滚动条
        "scroll_thumb_color": "#8d8d8d" if mode == "light" else "#9f9f9f",
        "scroll_thumb_opacity": 0.9 if not disabled else 0.4,
    }
