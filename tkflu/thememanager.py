"""主题管理器。

``FluThemeManager`` 是"一键换肤"的入口：把窗口（整棵控件树）统一切到
浅色 / 深色。真正的过渡由 :mod:`tkflu.theme_transition` 驱动——
**所有组件共用一条时间轴**，因此颜色是一起变的，而不是一个一个排队变。

.. code-block:: python

    thememanager = FluThemeManager(window=root, mode="light")

    thememanager.mode("dark")   # 切到深色
    thememanager.toggle()       # 在浅色/深色之间切换

0.4.0 之前这里是这样写的::

    for widget in window.winfo_children():
        widget.theme(mode=mode)
        widget._draw()
        widget.update()      # ← 每个组件都跑一遍事件循环

``update()`` 会把**全部**待办事件（含用户输入）处理掉，于是组件越多、
这一趟就越久，而且每个组件自己排的过渡帧会被前面组件的 ``update()``
就地执行掉——用户看到的是"卡住一段时间，然后一个一个地变色"。
实测 41 个组件的画廊里单次 ``mode()`` 要 **2.1 秒**。

现在这里只做一件事：把请求交给统一过渡。
"""

from typing import Optional, Union

from .theme_transition import active_transition, run_theme_transition

__all__ = ["FluThemeManager"]


class FluThemeManager(object):
    """把某个窗口（或任意子树）的一键换肤入口。

    :param window: 目标窗口；省略时用 ``tkinter._default_root``
    :param mode: 初始模式（``"light"`` / ``"dark"``）。**不会**在构造时换肤，
        只是记下来供 :meth:`toggle` 判断方向——与 0.4.0 之前的行为一致
    :param delay: 历史参数，已不再使用（保留是为了不改调用方的签名）
    """

    def __init__(
        self, window=None, mode: str = "light", delay: Union[int, None] = 100
    ):
        if window:
            self._window = window
        else:
            from tkinter import _default_root

            self._window = _default_root
        self._mode = mode

    @property
    def window(self):
        """当前目标窗口。"""
        return self._window

    @property
    def mode_(self) -> str:
        """当前记录的模式（``FluThemeManager.mode`` 是方法，所以另起名字）。"""
        return self._mode

    def mode(
        self,
        mode: str,
        delay: Union[int, None] = None,
        animation_steps: Optional[int] = None,
        animation_step_time: Optional[int] = None,
        easing=None,
    ):
        """把整棵树切到 ``mode``。

        :param mode: ``"light"`` / ``"dark"``
        :param delay: 历史参数，已不再使用
        :param animation_steps: 覆盖全局帧数（``0`` = 不要动画）
        :param animation_step_time: 覆盖全局帧间隔（毫秒）
        :param easing: 覆盖缓动曲线（名字或可调用对象）
        :returns: 这一次过渡对象（可用于取消 / 查失败列表）

        .. note::
           同一个窗口上只会有一个过渡在跑。用户在动画途中再点一次，
           新过渡会**就地接管**旧的（以当前中间色为起点），
           因此不会叠出越跑越慢的帧队列。
        """
        target = self._resolve(mode)
        self._mode = target
        return run_theme_transition(
            self._window,
            target,
            steps=animation_steps,
            step_time=animation_step_time,
            easing=easing,
        )

    def toggle(
        self,
        delay: Union[int, None] = None,
        animation_steps: Optional[int] = None,
        animation_step_time: Optional[int] = None,
        easing=None,
    ):
        """在 ``light`` / ``dark`` 之间切换。"""
        mode = "dark" if self._mode == "light" else "light"
        return self.mode(
            mode,
            delay,
            animation_steps=animation_steps,
            animation_step_time=animation_step_time,
            easing=easing,
        )

    def refresh(self, mode: Optional[str] = None):
        """不换模式，只把当前配色重新下发一遍（面板动态加载控件后很有用）。"""
        return self.mode(mode or self._mode)

    # ------------------------------------------------------------------
    @staticmethod
    def _resolve(mode) -> str:
        """容错：``None`` / 拼错的值退回 ``light``，而不是让整趟换肤崩掉。

        组件层的 ``theme()`` 早就是这么做的（见 ``FluButton.theme`` 的说明），
        这里保持一致——换肤入口更不该因为一个手滑的参数把界面卡在半路。
        """
        if mode is None:
            return "light"
        text = str(mode).lower()
        return text if text in ("light", "dark") else "light"

    @staticmethod
    def running():
        """当前正在跑的过渡（没有则 ``None``）。"""
        return active_transition()
