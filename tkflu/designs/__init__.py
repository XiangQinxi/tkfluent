"""设计规范（Fluent / WinUI3 的配色与几何）。

这个包把"组件长什么样"从"组件怎么工作"里拆了出来：
每个模块返回一份普通的 ``dict``（颜色、透明度、圆角半径、边框宽度），
组件绘制时查表取值。

因此**换皮肤不需要改组件代码**——改这里的返回值即可。"""

from .animation import (
    DEFAULT_EASING,
    EASINGS,
    FluAnimation,
    easing_function,
    easing_names,
    get_animation_step_time,
    get_animation_steps,
    get_theme_easing,
    set_animation_step_time,
    set_animation_steps,
    set_theme_easing,
    suspended_widget_animation,
    widget_animation_suspended,
)
from .design import FluDesign
from .fonts import *
from .gradient import FluGradient
from .primary_color import FluPrimaryColor, get_primary_color, set_primary_color
# 渲染引擎这几个查询接口一并转出：``set_renderer`` / ``get_renderer`` 早就在包根了，
# 只有"按名字查询"的那几个没跟上——文档里 `tkflu.get_renderer_name()` 这种自然写法
# 会 AttributeError。它们都是 tkdeft.engines 的薄转发，见 renderer.py。
from .renderer import (
    FluRenderer,
    describe_engines,
    engine_index,
    get_engine_name,
    get_renderer,
    get_renderer_name,
    list_engines,
    list_renderers,
    renderer_description,
    set_renderer,
)

