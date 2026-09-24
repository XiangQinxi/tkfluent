"""单选框的设计规范。

:func:`radiobox` 按 ``(mode, state, checked)`` 返回一份配色字典——形状与
复选框不同（圆环 + 圆点，而不是方框 + 勾号），配色令牌却是同一套
``ControlStrongStrokeColor*`` / ``AccentFillColor*``，所以
:data:`tkflu.designs.control.NEUTRAL` 被两个模块共用。
"""

from .control import FOCUS, NEUTRAL, TEXT
from .primary_color import get_primary_color

__all__ = ["radiobox", "RING_WIDTH", "DOT_RATIO"]

#: 圆环线宽
RING_WIDTH = 1

#: 圆点直径与圆环外径的比例（WinUI 的内圆大约是外径的一半）
DOT_RATIO = 0.5


def radiobox(mode: str = "light", state: str = "rest", checked: bool = False) -> dict:
    """取单选框在某个状态下的配色。

    :param mode: ``"light"`` / ``"dark"``
    :param state: ``"rest"`` / ``"hover"`` / ``"pressed"`` / ``"disabled"``
    :param checked: 是否被选中
    :returns: 配色字典，键与 ``FluRadioBox.attributes`` 一一对应

    :raises ValueError: ``mode`` 或 ``state`` 无法识别
    """
    mode = str(mode).lower()
    state = str(state).lower()
    if mode not in ("light", "dark"):
        raise ValueError(f"未知的主题模式 {mode!r}；应为 'light' 或 'dark'")
    if state not in NEUTRAL[mode]:
        raise ValueError(
            f"未知的状态 {state!r}；应为 {sorted(NEUTRAL[mode])} 之一"
        )

    accent = get_primary_color()[0 if mode == "light" else 1]
    neutral = NEUTRAL[mode][state]
    text = TEXT[mode]["disabled"] if state == "disabled" else TEXT[mode]["primary"]

    if state == "disabled":
        # 禁用态：圆环与圆点都用中性灰，不再跟随强调色
        ring_color = neutral["border"]
        dot_color = neutral["border"] if checked else None
        back_color, back_opacity = neutral["fill"], 1.0 if neutral["fill"] else 0.0
    elif checked:
        # 选中：圆环与圆点都是强调色，内部不填充
        ring_color = accent
        dot_color = accent
        back_color, back_opacity = neutral["fill"], 0.0
    else:
        ring_color = neutral["border"]
        dot_color = None
        back_color, back_opacity = neutral["fill"], 1.0 if neutral["fill"] else 0.0

    return {
        "back_color": back_color,
        "back_opacity": back_opacity,
        "border_color": ring_color,
        "border_color_opacity": 1.0,
        "border_width": RING_WIDTH,
        "text_color": text,
        "dot_color": dot_color,
        "dot_ratio": DOT_RATIO,
        "focus_color": FOCUS[mode],
        "focus_opacity": 0.0 if state == "disabled" else 0.35,
    }
