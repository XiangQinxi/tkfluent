"""设计规范（Fluent / WinUI3 的配色与几何）。

这个包把"组件长什么样"从"组件怎么工作"里拆了出来：
每个模块返回一份普通的 ``dict``（颜色、透明度、圆角半径、边框宽度），
组件绘制时查表取值。

因此**换皮肤不需要改组件代码**——改这里的返回值即可。"""

from .animation import (
    FluAnimation,
    get_animation_step_time,
    get_animation_steps,
    set_animation_step_time,
    set_animation_steps,
)
from .design import FluDesign
from .fonts import *
from .gradient import FluGradient
from .primary_color import FluPrimaryColor, get_primary_color, set_primary_color
from .renderer import FluRenderer, get_renderer, set_renderer
