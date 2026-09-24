"""复选框的设计规范。

:func:`checkbox` 按 ``(mode, state, checked)`` 返回一份配色字典，
共 2 主题 × 4 状态 × 3 勾选态。

勾选态有三种取值，与 Windows 的 Fluent 复选框一致：

=================== ==========================================
``checked``         外观
=================== ==========================================
``False``           空的方框
``True``            强调色填充 + 勾号
``None``            强调色填充 + 横杠（不确定态，indeterminate）
=================== ==========================================

配色数值来自 Fluent 的 ``CheckBoxCheckBackground*`` 系列令牌，
其中的半透明黑/白已按面板底色（见 :data:`tkflu.designs.control.SURFACE`）
合成为实色——``create_text`` 不吃透明度，文字必须是实色。
"""

from .control import FOCUS, GLYPH_DISABLED, NEUTRAL, TEXT
from .primary_color import get_primary_color

__all__ = ["checkbox", "GLYPH_NONE", "GLYPH_CHECK", "GLYPH_DASH"]

#: 不画任何图形
GLYPH_NONE = "none"
#: 画一个勾号
GLYPH_CHECK = "check"
#: 画一截横杠（不确定态）
GLYPH_DASH = "dash"

#: 方框的圆角半径（WinUI 里 20px 的方框用 4）
RADIUS = 4

#: 勾选后仍然保留的描边宽度。保持为 1 是为了让方框几何在"勾选/未勾选"之间
#: **完全一致**——描边宽度会参与几何内缩，一旦变化，方框大小就会跳一下。
BORDER_WIDTH = 1


def _glyph_for(checked):
    """把 ``checked`` 的三种取值翻译成要画的图形。"""
    if checked is None:
        return GLYPH_DASH
    return GLYPH_CHECK if checked else GLYPH_NONE


def checkbox(mode: str = "light", state: str = "rest", checked=False) -> dict:
    """取复选框在某个状态下的配色。

    :param mode: ``"light"`` / ``"dark"``
    :param state: ``"rest"`` / ``"hover"`` / ``"pressed"`` / ``"disabled"``
    :param checked: ``True`` / ``False`` / ``None``（``None`` = 不确定态）
    :returns: 配色字典，键与 ``FluCheckBox.attributes`` 一一对应

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
    glyph = _glyph_for(checked)

    if glyph == GLYPH_NONE:
        # 未勾选：只有描边（禁用态更淡）
        back_color, back_opacity = None, 0.0
        border_color = neutral["border"]
        border_opacity = 1.0
        glyph_color = None
    else:
        # 已勾选 / 不确定：强调色填充，描边不可见
        if state == "disabled":
            # 禁用态不跟随强调色，避免"看起来还能点"
            back_color, back_opacity = NEUTRAL[mode]["disabled"]["border"], 1.0
            glyph_color = GLYPH_DISABLED[mode]
        else:
            back_color = accent
            back_opacity = {"rest": 1.0, "hover": 0.9, "pressed": 0.8}[state]
            glyph_color = TEXT[mode]["on_accent"]
        border_color, border_opacity = accent, 0.0

    focus_opacity = 0.0 if state == "disabled" else 0.35

    return {
        "back_color": back_color,
        "back_opacity": back_opacity,
        "border_color": border_color,
        "border_color_opacity": border_opacity,
        "border_width": BORDER_WIDTH,
        "radius": RADIUS,
        "text_color": text,
        "glyph_color": glyph_color,
        "glyph": glyph,
        "focus_color": FOCUS[mode],
        "focus_opacity": focus_opacity,
    }
