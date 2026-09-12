"""集中式重绘调度。

.. warning::
   这个模块目前 **默认不启用**（只有设置了环境变量
   ``tkfluent.optimized_rendering=1`` 才会接管 ``update_idletasks``）。
   原因是它会把控件重绘延迟到下一个 ``after(16ms)``，与 tkfluent 各控件
   "事件里立即 ``_draw()``" 的既有语义不同，直接打开会改变交互时序。

本次修复的两个真实缺陷
----------------------
1. ``sorted(self._dirty_widgets, key=lambda w: w.winfo_zorder())``
   —— ``tkinter`` **没有** ``winfo_zorder`` 这个方法。只要有一条脏控件，
   这个排序就会抛 ``AttributeError``，异常从 ``after`` 回调里冒出来，
   用户看到的是控制台刷屏 + 界面停止重绘。现在改为按"先父后子"的稳定顺序。
2. ``_schedule_render`` 里 ``tk._default_root or list(self._dirty_widgets)[0]``
   —— 当两者都不可用时（动画队列刚入队但 ``_default_root`` 为 ``None``）
   会 ``IndexError``。现在做了兜底。
"""

import tkinter as tk
from os import environ
from typing import Dict, List, Set


class RenderManager:
    _instance = None
    _dirty_widgets: Set[tk.Widget] = set()
    _animation_queue: List[Dict] = []
    _render_delay = 16  # ~60 FPS
    _is_rendering = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def mark_dirty(self, widget: tk.Widget):
        """标记组件需要重绘"""
        if widget not in self._dirty_widgets:
            self._dirty_widgets.add(widget)
            self._schedule_render()

    def queue_animation(
        self, widget: tk.Widget, animation_steps: List[Dict], step_time: int
    ):
        """添加动画到队列"""
        self._animation_queue.append(
            {
                "widget": widget,
                "steps": animation_steps,
                "current_step": 0,
                "step_time": step_time,
            }
        )
        self._schedule_render()

    @staticmethod
    def _root_for(widgets):
        """挑一个可用的 Tk 控件来挂 ``after`` 回调。"""
        if tk._default_root is not None:
            return tk._default_root
        for widget in widgets:
            try:
                return widget.winfo_toplevel()
            except Exception:
                continue
        return None

    def _schedule_render(self):
        """安排渲染任务"""
        if self._is_rendering:
            return
        root = self._root_for(self._dirty_widgets)
        if root is None:
            # 还没有任何可用的 Tk 解释器：等下一次 mark_dirty 再排程，
            # 而不是在这里抛异常。
            return
        self._is_rendering = True
        root.after(self._render_delay, self._render_all)

    @staticmethod
    def _paint_order(widget):
        """按控件在窗口树里的深度排序（父控件先画，子控件后画）。

        ``tkinter`` 并未提供 ``winfo_zorder``；用 ``winfo_parent`` 的层级深度
        近似 Z 序，既稳定又不会抛异常。
        """
        depth = 0
        try:
            parent = widget.winfo_parent()
            seen = set()
            while parent and parent not in seen:
                seen.add(parent)
                depth += 1
                parent = widget.nametowidget(parent).winfo_parent()
        except Exception:
            return (0, "")
        return (depth, str(widget))

    def _render_all(self):
        """执行所有待处理的渲染任务"""
        try:
            # 处理动画
            self._process_animations()

            # 处理脏组件
            if self._dirty_widgets:
                # 先取快照再遍历：_draw 过程里可能又有控件把自己标记为脏，
                # 那些留到下一轮，而不是在本轮里越滚越多。
                sorted_widgets = sorted(self._dirty_widgets, key=self._paint_order)
                for widget in sorted_widgets:
                    # 重绘过程中可能被销毁，需容错
                    try:
                        if hasattr(widget, "_draw_centralized"):
                            widget._draw_centralized()
                        elif hasattr(widget, "_draw"):
                            widget._draw()
                    except tk.TclError:
                        continue
                # 清空本轮的脏标记；这会同时抹掉遍历期间新加的标记，
                # 避免 FluButton._draw 结尾的 mark_dirty 造成 60FPS 空转。
                self._dirty_widgets.clear()
        finally:
            self._is_rendering = False

        if self._animation_queue or self._dirty_widgets:
            self._schedule_render()

    def _process_animations(self):
        """处理动画队列"""
        completed_animations = []

        for idx, anim in enumerate(self._animation_queue):
            widget = anim["widget"]
            steps = anim["steps"]
            current_step = anim["current_step"]

            if current_step < len(steps):
                # 应用当前帧动画
                applier = getattr(widget, "_apply_animation_step", None)
                if applier is not None:
                    try:
                        applier(steps[current_step])
                    except tk.TclError:
                        pass
                anim["current_step"] += 1
            else:
                completed_animations.append(idx)

        # 移除完成的动画
        for idx in reversed(completed_animations):
            del self._animation_queue[idx]


# 创建全局渲染管理器实例
render_manager = RenderManager()


# 保存原始方法
original_update_idletasks = tk.Widget.update_idletasks


def optimized_update_idletasks(self):
    """把 ``update_idletasks`` 变成"标记脏 + 延迟合批重绘"。"""
    if getattr(self, "master", None) is not None:
        render_manager.mark_dirty(self)
    else:
        # 回退到原始实现
        original_update_idletasks(self)


# 替换Tkinter的update_idletasks
if environ.get("tkfluent.optimized_rendering", "0") == "1":
    tk.Widget.update_idletasks = optimized_update_idletasks
