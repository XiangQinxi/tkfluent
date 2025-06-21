from typing import Literal

NO = FALSE = OFF = 0
YES = TRUE = ON = 1

# Modes
LIGHT = 'light'
DARK = 'dark'
MODE = Literal["light", "dark"]

# States
NORMAL = 'normal'
DISABLED = 'disabled'
STATE = Literal["normal", "disabled"]

# FluButton Styles
STANDARD = 'standard'
ACCENT = 'accent'
MENU = 'menu'
BUTTONSTYLE = Literal["standard", "accent", "menu"]
