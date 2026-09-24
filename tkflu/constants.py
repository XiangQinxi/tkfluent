"""公共常量与类型别名。

集中定义主题模式、组件状态、按钮/面板样式等字面量，
既做类型提示也避免各处硬编码字符串。"""

from typing import Literal

NO = FALSE = OFF = 0
YES = TRUE = ON = 1

# Modes
LIGHT = "light"
DARK = "dark"
MODE = Literal["light", "dark"]

# States
NORMAL = "normal"
DISABLED = "disabled"
STATE = Literal["normal", "disabled"]

# 组件样式
# ``STANDARD`` 是按钮与面板**共用**的取值，定义一次即可
# （旧文件里写了两遍，读起来像是两个不同的常量）。
STANDARD = "standard"
ACCENT = "accent"
MENU = "menu"
POPUPMENU = "popupmenu"
BUTTONSTYLE = Literal["standard", "accent", "menu"]
FRAMESTYLE = Literal["standard", "popupmenu"]
