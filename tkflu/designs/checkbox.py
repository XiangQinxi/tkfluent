"""复选框的设计规范。

:func:`checkbox` 按 ``(mode, state, checked)`` 返回一份配色字典，
共 2 主题 × 4 状态 × 3 勾选态。

勾选态有三种取值，与 Windows 的 Fluent 复选框一致：

====================== ==========================================
``checked``            外观
====================== ==========================================
``False``              空的方框
``True``               强调色填充 + 勾号
``None``               强调色填充 + 横杠（不确定态，indeterminate）
====================== ==========================================

几何与配色的来源
----------------
``tests`` 之外的一切数值都取自 Figma 设计稿（``Basic Input.svg``）：
方框 20×20、圆角 4、描边 1px；未选中描边 ``#000000 @ 0.6063``、
填充 ``#000000 @ 0.0241``；选中填充 ``rgb(0,95,184)``。
描边与填充成对返回 ``(颜色, 不透明度)``，由绘制引擎按背景合成，
见 :mod:`tkflu.designs.control`。
"""

from .control import FOCUS_RING, GLYPH_DISABLED, NEUTRAL, TEXT, paint
from .primary_color import get_primary_color

__all__ = ["checkbox", "GLYPH_NONE", "GLYPH_CHECK", "GLYPH_DASH", "CHECK_GLYPH"]

#: 不画任何图形
GLYPH_NONE = "none"
#: 画一个勾号
GLYPH_CHECK = "check"
#: 画一截横杠（不确定态）
GLYPH_DASH = "dash"

#: 勾号用的字形：Segoe Fluent Icons 的 ``CheckMark``。
#: WinUI 的 CheckBox 模板就是 ``<FontIcon Glyph="&#xE73E;" FontSize="12"/>``。
#: 实测设计稿里的勾号墨迹是 10×7，用这个字号画出来是 12×8——每边大 1px，
#: 比手画折线（又粗又大）或换字号（11 号会缩到 8×7 且整体右移 3px）都更接近。
CHECK_GLYPH = "\ue73e"

#: 方框的圆角半径（设计稿：18×18 的填充矩形 rx=3，加 1px 内缩 → 外框 r=4）
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
        # 未选中：只有描边 + 一层极淡的底（设计稿里有这层底：fill-opacity 0.0241）
        back_color, back_opacity = paint(neutral["fill"])
        border_color, border_opacity = paint(neutral["border"])
        glyph_color = None
    else:
        # 已勾选 / 不确定：强调色填充，描边与填充同色（设计稿里就是这样，
        # 视觉上等于没有独立描边）
        if state == "disabled":
            # 禁用态不跟随强调色，避免"看起来还能点"。
            # 数值来自 Lists & Collections.svg 里的禁用勾选框：
            # 浅色 = #000000 @ 0.2169、深色 = #FFFFFF @ 0.1581
            fill = (
                ("#000000", 0.2169) if mode == "light" else ("#ffffff", 0.1581)
            )
            back_color, back_opacity = paint(fill)
            border_color, border_opacity = paint(fill)
            glyph_color = GLYPH_DISABLED[mode]
        else:
            back_color = accent
            back_opacity = {"rest": 1.0, "hover": 0.9, "pressed": 0.8}[state]
            border_color, border_opacity = accent, 1.0
            glyph_color = TEXT[mode]["on_accent"]

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
        "focus_color": FOCUS_RING[mode]["outer"][0],
        "focus_opacity": (
            0.0 if state == "disabled" else FOCUS_RING[mode]["outer"][1]
        ),
        "focus_inner_color": FOCUS_RING[mode]["inner"][0],
        "focus_inner_opacity": (
            0.0 if state == "disabled" else FOCUS_RING[mode]["inner"][1]
        ),
    }
