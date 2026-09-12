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

    def _schedule_render(self):
        """安排渲染任务"""
        if not self._is_rendering:
            self._is_rendering = True
            root = tk._default_root or list(self._dirty_widgets)[0].winfo_toplevel()
            root.after(self._render_delay, self._render_all)

    def _render_all(self):
        """执行所有待处理的渲染任务"""
        # 处理动画
        self._process_animations()

        # 处理脏组件
        if self._dirty_widgets:
            # 按Z轴顺序排序组件
            sorted_widgets = sorted(self._dirty_widgets, key=lambda w: w.winfo_zorder())
            for widget in sorted_widgets:
                if hasattr(widget, "_draw_centralized"):
                    widget._draw_centralized()
                elif hasattr(widget, "_draw"):
                    widget._draw()
                widget.update_idletasks()
            self._dirty_widgets.clear()

        self._is_rendering = False
        # 如果还有动画或脏组件，继续渲染
        if self._animation_queue or self._dirty_widgets:
            self._schedule_render()

    def _process_animations(self):
        """处理动画队列"""
        completed_animations = []

        for idx, anim in enumerate(self._animation_queue):
            widget = anim["widget"]
            steps = anim["steps"]
            current_step = anim["current_step"]
            step_time = anim["step_time"]

            if current_step < len(steps):
                # 应用当前帧动画
                if hasattr(widget, "_apply_animation_step"):
                    widget._apply_animation_step(steps[current_step])
                anim["current_step"] += 1
            else:
                completed_animations.append(idx)

        # 移除完成的动画
        for idx in reversed(completed_animations):
            del self._animation_queue[idx]


# 创建全局渲染管理器实例
render_manager = RenderManager()


# 替换默认的update_idletasks方法
def optimized_update_idletasks(self):
    if hasattr(self, "master") and self.master is not None:
        render_manager.mark_dirty(self)
    else:
        # 回退到原始实现
        original_update_idletasks(self)


# 保存原始方法
original_update_idletasks = tk.Widget.update_idletasks

# 替换Tkinter的update_idletasks
if environ.get("tkfluent.optimized_rendering", "0") == "1":
    tk.Widget.update_idletasks = optimized_update_idletasks
