"""

Fluent设计的tkinter组件库（模板）

-------------
作者：XiangQinxi

贡献者：totowang-hhh
-------------
"""

from .badge import FluBadge
from .button import FluButton
from .bwm import BWm
from .constants import *
from .defs import *
from .designs import *
from .entry import FluEntry
from .frame import FluFrame
from .icons import *
from .image import FluImage
from .label import FluLabel
from .listbox import FluListBox
from .menu import FluMenu
from .menubar import FluMenuBar
from .popupmenu import FluPopupMenu, FluPopupMenuWindow
from .popupwindow import FluPopupWindow
from .scrollbar import FluScrollBar
from .slider import FluSlider
from .text import FluText
from .thememanager import FluThemeManager
from .togglebutton import FluToggleButton
from .tooltip import FluToolTip, FluToolTip2, FluToolTipBase
from .toplevel import FluToplevel
from .window import FluWindow

# 说明：FluListBox 与 FluImage 此前没有出现在包根，
# 导致 tkflu.FluListBox 不可用（只有 tkflu.listbox.FluListBox）。
# 这里补上，让所有公开组件都能从包根导入。

FluChip = FluBadge
FluPushButton = FluButton
FluTextInput = FluEntry
FluTextBox = FluText
FluPanel = FluFrame
FluMainWindow = FluWindow
FluSubWindow = FluToplevel

# 
