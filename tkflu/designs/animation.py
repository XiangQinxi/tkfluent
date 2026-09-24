"""动画参数与缓动函数。

控制主题切换等过渡动画的帧数、帧间隔与**缓动曲线**。

.. code-block:: python

    from tkflu import set_animation_steps, set_animation_step_time

    set_animation_steps(5)              # 5 帧
    set_animation_step_time(20)         # 每帧 20ms
    set_theme_easing("ease_in_out")     # 缓动曲线（默认）

两者都设为 0 即关闭动画（默认就是关闭）。

单控件动画的"暂停开关"
----------------------
:func:`~tkflu.theme_transition.run_theme_transition` 会把整棵控件树的颜色插值
放到**同一条时间轴**上统一驱动。那一刻它必须先"静默地"把每个组件的目标配色写进
``attributes``（否则算不出插值起点），此时各个组件**自己**的 ``_theme()`` 动画
必须让路，否则同一次换肤会排出两套互相打架的帧。

:func:`suspended_widget_animation` 就是那个让路开关：它在上下文里把
:func:`get_animation_steps` / :func:`get_animation_step_time` 都读成 0，
于是所有组件的 ``_theme()`` 自然退化成"直接写目标值"，一行组件代码都不用改。
"""

from __future__ import annotations

from contextlib import contextmanager
from os import environ
from typing import Callable, Dict, Optional

__all__ = [
    "set_animation_steps",
    "get_animation_steps",
    "set_animation_step_time",
    "get_animation_step_time",
    "set_theme_easing",
    "get_theme_easing",
    "easing_function",
    "easing_names",
    "suspended_widget_animation",
    "widget_animation_suspended",
    "FluAnimation",
]


# ---------------------------------------------------------------------------
# 缓动曲线
# ---------------------------------------------------------------------------
def linear(t: float) -> float:
    """匀速。老实现用的就是它。"""
    return t


def ease_in(t: float) -> float:
    """慢起快落。"""
    return t * t * t


def ease_out(t: float) -> float:
    """快起慢落。"""
    return 1.0 - pow(1.0 - t, 3)


def ease_in_out(t: float) -> float:
    """两头慢、中间快（cubic）。换肤的默认曲线。"""
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - pow(-2.0 * t + 2.0, 3) / 2.0


def ease_out_back(t: float) -> float:
    """末端轻微过冲的弹回曲线，想"更活泼"时可以换它。"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1.0 + c3 * pow(t - 1.0, 3) + c1 * pow(t - 1.0, 2)


#: 名字 → 缓动函数
EASINGS: Dict[str, Callable[[float], float]] = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "ease_out_back": ease_out_back,
}

#: 主题过渡的默认曲线
DEFAULT_EASING = "ease_in_out"


def easing_names():
    """所有可用的缓动名字（排序后）。"""
    return sorted(EASINGS)


def easing_function(name: Optional[str]):
    """按名字取缓动函数；名字不认识时**退回默认曲线**而不是抛异常。

    理由和 :meth:`tkflu.button.FluButton.theme` 里那个"未知 style 退回默认值"
    的约定一致：一次换肤不该因为一个拼错的曲线名整趟崩掉。

    :param name: 曲线名，或一个可调用对象（原样返回）
    """
    if callable(name):
        return name
    if not name:
        return EASINGS[DEFAULT_EASING]
    return EASINGS.get(str(name).lower(), EASINGS[DEFAULT_EASING])


def set_theme_easing(name: str) -> None:
    """设置主题过渡的缓动曲线，取值见 :data:`EASINGS`。"""
    environ["tkfluent.theme_easing"] = str(name)


def get_theme_easing() -> str:
    """当前主题过渡的缓动曲线名。"""
    return environ.get("tkfluent.theme_easing", DEFAULT_EASING)


# ---------------------------------------------------------------------------
# 帧数 / 帧间隔
# ---------------------------------------------------------------------------
#: 单控件动画的暂停深度（>0 表示"让路给统一过渡"）
_suspension_depth = 0


@contextmanager
def suspended_widget_animation():
    """在这个上下文里，各组件自己的 ``_theme()`` 动画全部让路。

    :func:`~tkflu.theme_transition.run_theme_transition` 用它来"静默地"把
    目标配色写进各组件，从而拿到干净的插值起点。

    .. note::
       用计数而不是布尔量：统一过渡本身也可能被嵌套调用（窗口 → 面板 → 菜单栏），
       布尔量会在内层退出时把外层的暂停提前解除。
    """
    global _suspension_depth
    _suspension_depth += 1
    try:
        yield
    finally:
        _suspension_depth -= 1


def widget_animation_suspended() -> bool:
    """当前是否处于"让路"状态。"""
    return _suspension_depth > 0


def set_animation_steps(steps: int):
    environ["tkfluent.animation_steps"] = str(int(steps))


def get_animation_steps():
    if _suspension_depth:
        return 0
    return int(environ["tkfluent.animation_steps"])


def set_animation_step_time(step_time: int):
    environ["tkfluent.animation_step_time"] = str(int(step_time))


def get_animation_step_time():
    if _suspension_depth:
        return 0
    return int(environ["tkfluent.animation_step_time"])


if "tkfluent.animation_steps" not in environ:
    set_animation_steps(0)
if "tkfluent.animation_step_time" not in environ:
    set_animation_step_time(0)
if "tkfluent.theme_easing" not in environ:
    set_theme_easing(DEFAULT_EASING)


class FluAnimation(object):
    def animation_steps(self, steps: int = None):
        if steps:
            set_animation_steps(steps)
        else:
            return get_animation_steps()

    def animation_step_time(self, step_time: int = None):
        if step_time:
            set_animation_step_time(step_time)
        else:
            return get_animation_step_time()
