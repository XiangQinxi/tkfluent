"""单选框的设计规范。

:func:`radiobox` 按 ``(mode, state, checked)`` 返回一份配色字典——形状与
复选框不同（圆环 + 圆点，而不是方框 + 勾号），几何却是同一套：
外径 20、描边 1px、圆角取半径的一半（也就是正圆）。

数值来源
--------
取自 Figma 设计稿 ``Basic Input (1).svg``：

============ ==========================================================
元素          设计稿里的写法
============ ==========================================================
外圈          20×20 占位
圆环          19×19 ``rx=9.5``，``stroke-width=1``
圆内          18×18 ``rx=9``（这一层就是"圆环内部的填充"）
圆点          8×8 ``rx=4``，居中（圆心与圆环同心）
============ ==========================================================

未选中：圆环 ``#000000 @ 0.6063`` + 内部填充 ``#000000 @ 0.0241``。
选中：圆环换成强调色。

.. warning::
   设计稿里"选中"这一态的圆内填充被画成了**强调色**，圆点却是**白色**——
   两个叠起来是一枚"蓝色甜甜圈"。而 Windows 11 的 RadioButton 是
   **细圆环 + 中间一个小圆点**（圆内不填充）。
   这里按 **Windows 的形态**实现（圆内不填充、圆点用强调色），
   但圆点的直径照抄设计稿的 **8px**（旧实现是 10px，偏大）。
   如果确实要设计稿那个"甜甜圈"，把 :data:`ARC_FILL_WHEN_CHECKED` 改成
   ``True`` 即可。
"""

from .control import FOCUS_RING, NEUTRAL, TEXT, paint
from .primary_color import get_primary_color

__all__ = ["radiobox", "RING_WIDTH", "DOT_RATIO", "DOT_SIZE", "DOT_SIZE_HOVER", "dot_size_for"]

#: 圆环线宽（设计稿：``stroke-width=1``）
RING_WIDTH = 1

#: 圆点直径：**四种状态各不相同**（设计稿 ``Bullet`` 的实测值）。
#: rest 8 / hover 10 / pressed 6 / disabled 8 —— 这组节奏在两个主题下一致，
#: 说明"悬停变大、按下变小"是有意为之的，不是笔误。
DOT_SIZES = {"rest": 8, "hover": 10, "pressed": 6, "disabled": 8}

#: 默认圆点直径（等价于 rest）
DOT_SIZE = DOT_SIZES["rest"]
#: 悬停时的圆点直径
DOT_SIZE_HOVER = DOT_SIZES["hover"]
#: 圆点直径与外径的比例（按默认尺寸算）
DOT_RATIO = DOT_SIZE / 20.0

#: 选中时把"圆内"也填成强调色。
#:
#: .. important::
#:   设计稿里选中态的画法是「18×18 圆内填**强调色** + 8×8 的圆点填
#:   **反差色**」，叠起来是一枚"实心圆 + 中间一个小孔"。
#:   判定这是设计意图（而不是笔误）的依据有两条：圆点直径在四个状态下是
#:   **8 / 10 / 6 / 8**，节奏连贯；圆点用的颜色正好是
#:   ``TextOnAccentFillColorPrimary``（浅色主题白、深色主题黑），
#:   也就是"压在强调色上的图形色"。这套逻辑是自洽的。
#:
#:   注意：**Windows 自己的 RadioButton 不是这样**——它是「1px 圆环 +
#:   中心圆点，圆内不填充」。想要 Windows 原版形态，把这里和
#:   :data:`DOT_COLOR_ON_ACCENT` 一起改成 ``False``。
ARC_FILL_WHEN_CHECKED = True

#: 圆点用"压在强调色上的图形色"（浅色=白、深色=黑）。
#: ``False`` 时圆点用强调色本身（＝ Windows 原版形态）。
DOT_COLOR_ON_ACCENT = True


def dot_size_for(state: str) -> int:
    """某个状态下圆点的直径。"""
    return DOT_SIZES.get(str(state).lower(), DOT_SIZE)


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
        raise ValueError(f"未知的状态 {state!r}；应为 {sorted(NEUTRAL[mode])} 之一")

    accent = get_primary_color()[0 if mode == "light" else 1]
    neutral = NEUTRAL[mode][state]
    text = TEXT[mode]["disabled"] if state == "disabled" else TEXT[mode]["primary"]

    if state == "disabled":
        # 禁用：圆环与圆点都退回中性色（不再跟随强调色）。
        # 设计稿里禁用的选中态是"一个 20×20 的实心圆 + 白/黑圆点"，没有独立圆环。
        border_color, border_opacity = paint(neutral["border"])
        if checked:
            back_color, back_opacity = border_color, border_opacity
            dot_color = TEXT[mode]["on_accent"]
        else:
            back_color, back_opacity = paint(neutral["fill"])
            dot_color = None
    elif checked:
        border_color, border_opacity = accent, 1.0
        dot_color = TEXT[mode]["on_accent"] if DOT_COLOR_ON_ACCENT else accent
        if ARC_FILL_WHEN_CHECKED:
            back_color, back_opacity = accent, 1.0
        else:
            back_color, back_opacity = None, 0.0
    else:
        border_color, border_opacity = paint(neutral["border"])
        back_color, back_opacity = paint(neutral["fill"])
        dot_color = None

    return {
        "back_color": back_color,
        "back_opacity": back_opacity,
        "border_color": border_color,
        "border_color_opacity": border_opacity,
        "border_width": RING_WIDTH,
        "text_color": text,
        "dot_color": dot_color,
        "dot_size": dot_size_for(state),
        "dot_ratio": DOT_RATIO,
        "focus_color": FOCUS_RING[mode]["outer"][0],
        "focus_opacity": (
            0.0 if state == "disabled" else FOCUS_RING[mode]["outer"][1]
        ),
        "focus_inner_color": FOCUS_RING[mode]["inner"][0],
        "focus_inner_opacity": (
            0.0 if state == "disabled" else FOCUS_RING[mode]["inner"][1]
        ),
    }
