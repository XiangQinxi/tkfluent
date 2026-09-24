"""列表的设计规范。

数值来源：Figma 设计稿 ``Lists & Collections.svg`` 里的
``List View / List View Item`` 组件（该文件的图层名是可读的，
所以下面每条都能对应到具体元素）。

==================== ==========================================================
项                    设计稿
==================== ==========================================================
条目高度              40（单行）/ 56（两行）/ 72（三行）
条目宽度              容器宽 − 2（左右各留 1px）
条目圆角              4；高亮底圆角 3
高亮底内缩            左右 **5**、上下 **3**
选中指示条            3 宽、圆角 1.5、距条目左边缘 **4**、垂直居中、长 **16**
文字左缩进            **16**
容器圆角              **8**
==================== ==========================================================

.. important::
   **选中行的底色和悬停行是同一个中性色**（浅色 ``#000000 @ 0.0373``），
   *不是* 强调色的淡色。强调色只用在左侧那条指示条上。
   旧实现把选中行做成了"强调色 16% 的淡蓝"，那是错的。
"""

from .control import NEUTRAL, TEXT, blend
from .primary_color import get_primary_color

__all__ = ["listbox", "RADIUS", "ITEM_RADIUS"]

#: 容器圆角（设计稿 rx=8）
RADIUS = 8

#: 条目高亮的圆角（设计稿 rx=3）
ITEM_RADIUS = 3

#: 行底色的中性色浓度：(浅色主题, 深色主题)
_ROW_TINT = {
    "rest": 0.0,
    "hover": (0.0373, 0.0605),
    "pressed": (0.0241, 0.0419),
}

#: 文字浓度（浅色/深色各一套），合成到面板底色上
_TEXT_ALPHA = {
    "rest": {"light": 0.8956, "dark": 0.8956},
    "pressed": {"light": 0.6063, "dark": 0.7860},
    "disabled": {"light": 0.3614, "dark": 0.3628},
}


def _overlay_color(mode: str) -> str:
    """行底色是用"叠一层"实现的：浅色叠黑、深色叠白。"""
    return "#000000" if mode == "light" else "#ffffff"


def listbox(mode: str = "light", style: str = "standard", state: str = "rest") -> dict:
    """取列表控件在某个状态下的配色。

    :param mode: ``"light"`` / ``"dark"``
    :param style: ``"standard"``（白面板）/ ``"accent"``（强调色底）
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
    overlay = _overlay_color(mode)

    if style == "accent":
        back_color = border_color = border_color2 = accent
        item_text = TEXT[mode]["on_accent"]
    else:
        back_color = surface
        # 设计稿里容器**只给了圆角，没画描边和底色**；这里保留历史上
        # "上浅下深"的那道 1px 渐变边（它是这个库的既有外观）。
        border_color = "#f0f0f0" if mode == "light" else "#3a3a3a"
        border_color2 = "#d6d6d6" if mode == "light" else "#262626"
        item_text = TEXT[mode]["primary"]

    if disabled:
        item_text = TEXT[mode]["disabled"]

    def row_fill(key):
        """行底色：把中性色叠到控件底色上，得到可直接绘制的实色。"""
        tint = _ROW_TINT[key]
        if not tint:
            return None
        ratio = tint if isinstance(tint, float) else tint[0 if mode == "light" else 1]
        base = back_color if style == "standard" else accent
        return blend(overlay, ratio, base)

    hover_back = row_fill("hover")
    pressed_back = row_fill("pressed")
    selected_back = row_fill("hover")  # 设计稿：选中与悬停同色，强调色只给指示条

    return {
        "back_color": back_color,
        "border_color": border_color,
        "border_color2": border_color2,
        "border_width": 1,
        "radius": RADIUS,
        "text_color": item_text,
        # 条目
        "item_text_color": item_text,
        "item_hover_back": hover_back,
        "item_pressed_back": pressed_back,
        "item_selected_back": selected_back,
        "item_selected_text": item_text,
        "indicator_color": accent,
        "indicator_disabled": blend(
            "#000000" if mode == "light" else "#ffffff",
            0.2169 if mode == "light" else 0.1581,
            surface,
        ),
        # 自绘滚动条（数值来自 Scrolling.svg：细态 2px / 展开态 6px / 轨道 12px）
        "scroll_thumb_color": "#8a8a8a" if mode == "light" else "#989898",
        "scroll_thumb_opacity": 1.0 if not disabled else 0.5,
    }
