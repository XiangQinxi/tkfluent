"""统一主题过渡的回归测试。

对应的真实问题（0.4.0 之前的 ``FluThemeManager``）::

    for widget in window.winfo_children():
        widget.theme(mode=mode)   # 每个组件内部各排各的过渡帧
        widget._draw()
        widget.update()           # ← 把事件循环跑了起来

后果是三个互相放大的毛病，这里每一条都有闸门：

1. **阻塞**。``update()`` 会处理全部待办事件。实测 41 个组件的画廊里
   单次 ``mode()`` 要 2.1 秒，期间窗口点不动。
   → :meth:`TestNotBlocking.test_mode_does_not_pump_the_event_loop`
2. **不同步**。每个组件各排各的 ``after``，起点是"轮到它自己"那一刻；
   而前面的 ``update()`` 又会把后面组件的帧提前执行掉，于是"一个一个变色"。
   → :meth:`TestSynchronised.test_every_widget_is_painted_on_the_same_time_axis`
3. **动画被吃掉**。真正跑完的帧全在 ``mode()`` 内部消耗掉了，用户看到的
   不是过渡，而是"卡一会儿然后瞬间变色"。
   → :meth:`TestNotBlocking.test_mode_returns_before_any_frame_is_painted`
"""

from __future__ import annotations

import time

import pytest

import tkflu
from conftest import requires_tk

pytestmark = requires_tk


def pump(root, times=6):
    for _ in range(times):
        root.update()


class _AnimationSettings:
    """临时改动画参数，测完还原（它们是**进程级**的环境变量）。"""

    def __init__(self, steps, step_time, easing=None, budget=None):
        self.steps = steps
        self.step_time = step_time
        self.easing = easing
        self.budget = budget

    def __enter__(self):
        from tkflu.designs.animation import (
            get_animation_step_time,
            get_animation_steps,
            get_theme_easing,
            set_animation_step_time,
            set_animation_steps,
            set_theme_easing,
        )
        from tkflu.theme_transition import get_transition_budget

        self._old = (
            get_animation_steps(),
            get_animation_step_time(),
            get_theme_easing(),
            get_transition_budget(),
        )
        set_animation_steps(self.steps)
        set_animation_step_time(self.step_time)
        if self.easing:
            set_theme_easing(self.easing)
        if self.budget is not None:
            from tkflu.theme_transition import set_transition_budget

            set_transition_budget(self.budget)
        return self

    def __exit__(self, *exc):
        from tkflu.designs.animation import (
            set_animation_step_time,
            set_animation_steps,
            set_theme_easing,
        )
        from tkflu.theme_transition import set_transition_budget

        set_animation_steps(self._old[0])
        set_animation_step_time(self._old[1])
        set_theme_easing(self._old[2])
        set_transition_budget(self._old[3])
        return False


def build_scene(window, mode="light"):
    """一屏"颜色差异明显"的组件（颜色在深浅主题下确实不同的那些）。"""
    widgets = {
        "label": tkflu.FluLabel(window, text="标签", mode=mode),
        "accent": tkflu.FluButton(window, text="强调", mode=mode, style="accent"),
        "standard": tkflu.FluButton(window, text="标准", mode=mode),
        "checkbox": tkflu.FluCheckBox(window, text="复选", mode=mode),
        "listbox": tkflu.FluListBox(
            window, width=180, height=90, items=["一", "二"], mode=mode
        ),
    }
    for widget in widgets.values():
        widget.pack(anchor="w", padx=4, pady=2)
    pump(window, 4)
    return widgets


def _read_path(attributes, path):
    """按叶子路径读回一个值（``("rest", "back_color")`` 这类）。"""
    current = attributes
    for key in path:
        current = current[key]
    return current


def drain(root, timeout=2.0):
    """把待执行的 ``after`` 跑完（真实 mainloop 语义，不要用 update() 忙等）。"""
    done = []
    deadline = time.time() + timeout

    def tick():
        if root.tk.call("after", "info") == "" or time.time() > deadline:
            done.append(True)
            root.quit()
        else:
            root.after(5, tick)

    root.after(5, tick)
    root.mainloop()
    return bool(done)


# ---------------------------------------------------------------------------
# 同步
# ---------------------------------------------------------------------------
class TestSynchronised:
    def test_every_widget_is_painted_on_the_same_time_axis(self, window):
        """所有组件共用**一个**进度 ``t``——这才是"同步换肤"。

        旧实现里每个组件各排各的帧，实测各组件"第一次变色"的时刻能差出
        150ms 以上；这里断言同一个 ``_paint`` 调用把同一个 ``t`` 写给所有人。
        """
        with _AnimationSettings(4, 30):
            build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                assert transition.animated
                assert len(transition.plans) >= 4, "参与过渡的组件太少"

                for t in (0.25, 0.5, 0.75, 1.0):
                    transition._paint(t)
                    moment = {plan.t for plan in transition.plans.values()}
                    assert moment == {t}, f"同一帧里出现了多个进度：{moment}"
            finally:
                transition.cancel()

    def test_all_widgets_end_on_the_target_theme(self, window):
        """过渡收尾不能停在中间色上（旧实现的"最后一帧就是中间态"就栽在这）。"""
        with _AnimationSettings(3, 20):
            widgets = build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            drain(window)

            assert transition._finished
            assert tkflu.active_transition() is None
            for name, widget in widgets.items():
                assert getattr(widget, "_theme_blend", None) is None, name

            # 再切回来，属性必须与"直接静态换肤"一致
            manager.mode("light")
            drain(window)

            from tkflu.designs.label import label as label_design

            assert widgets["label"].attributes.text_color == label_design("light")[
                "text_color"
            ]

    def test_top_level_scalar_colours_are_interpolated(self, window):
        """顶层就是叶子的配色字段（``FluLabel.text_color``）必须参与插值。

        回归：``values_at`` 曾经对"路径长度为 1"的叶子去取 ``path[1:]``，
        得到空元组后回写时 ``IndexError``，异常被兜住 → 这些组件**从不参与过渡**。
        """
        with _AnimationSettings(4, 30):
            label = tkflu.FluLabel(window, text="标签", mode="light")
            label.pack()
            pump(window, 3)

            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                plan = label._theme_blend
                assert plan is not None, "标签没有参与过渡"
                assert ("text_color",) in plan.kinds

                mid = plan.values_at(0.5)["text_color"]
                assert mid not in ("#000000", "#ffffff"), mid
                # 起点 / 终点仍然精确
                assert plan.values_at(0.0)["text_color"] == "#000000"
                assert plan.values_at(1.0)["text_color"] == "#ffffff"
            finally:
                transition.cancel()

    def test_design_driven_widgets_keep_the_blended_colour(self, window):
        """``_draw()`` 里会重算配色的组件也要能保住中间色。

        ``FluCheckBox`` / ``FluListBox`` 的 ``_draw()`` 开头会调
        ``_apply_design()``，按当前 ``(mode, 状态)`` 重新查设计规范——
        没有 :func:`~tkflu.theme_transition.blend_theme_design` 这一层的话，
        刚写进去的中间色会被整个覆盖掉，它们就成了整屏里唯一"瞬间跳变"的。
        """
        with _AnimationSettings(4, 30):
            checkbox = tkflu.FluCheckBox(window, text="复选", mode="light")
            checkbox.pack()
            pump(window, 3)

            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                plan = checkbox._theme_blend
                assert plan is not None and plan.kinds

                path = next(iter(plan.kinds))
                before = plan.before[path]
                after = plan.after[path]

                transition._paint(0.5)
                # _draw() → _apply_design() 之后仍然是中间色
                blended = _read_path(checkbox.attributes, path)
                assert blended not in (before, after), (
                    f"{path} 被 _apply_design 覆盖成了终态：{blended}"
                )

                transition.finish()
                assert _read_path(checkbox.attributes, path) == after
            finally:
                transition.cancel()

    def test_gradient_is_monotone_with_easing(self):
        """缓动曲线单调、端点精确，且确实不是线性（否则"缓动"是假的）。"""
        from tkflu.designs.animation import EASINGS, easing_function

        for name, function in EASINGS.items():
            assert function(0.0) == pytest.approx(0.0, abs=1e-9)
            assert function(1.0) == pytest.approx(1.0, abs=1e-9)

        values = [EASINGS["ease_in_out"](i / 10) for i in range(11)]
        assert values == sorted(values), "缓动曲线不单调"
        assert values[2] < 0.2, "ease_in_out 的前段应当更慢"
        assert easing_function("不存在的名字") is EASINGS["ease_in_out"]


# ---------------------------------------------------------------------------
# 不阻塞
# ---------------------------------------------------------------------------
class TestNotBlocking:
    def test_theme_sweep_does_not_pump_the_event_loop(self, window):
        """换肤期间**不能**顺手把事件循环跑一遍。

        旧实现每个组件一次 ``update()``，而 ``update()`` 会处理全部待办事件——
        排队中的 ``after(0)`` 回调当场就被执行掉了。这里放一个探针回调：
        它在整趟换肤返回前**不该**被执行。

        .. note::
           这里特意用 ``FluFrame`` 作为换肤的根，而不是窗口：
           ``FluWindow`` / ``FluToplevel`` 会调 ``pywinstyles.apply_style()``，
           而那个第三方函数内部自己带了一句 ``window.update()``
           （见 :meth:`tkflu.bwm.BWm._apply_titlebar_style`）。
        """
        from tkflu.theme_transition import run_theme_transition

        fired = []
        with _AnimationSettings(4, 50):
            panel = tkflu.FluFrame(window, width=320, height=220, mode="light")
            panel.pack()
            for widget in (
                tkflu.FluLabel(panel, text="标签", mode="light"),
                tkflu.FluButton(panel, text="强调", style="accent", mode="light"),
                tkflu.FluCheckBox(panel, text="复选", mode="light"),
                tkflu.FluListBox(
                    panel, width=180, height=90, items=["一", "二"], mode="light"
                ),
            ):
                widget.pack(anchor="w", padx=4, pady=2)
            pump(window, 4)

            window.after(0, lambda: fired.append("ran"))
            transition = run_theme_transition(panel, "dark")
            try:
                assert fired == [], "换肤里跑了事件循环（update() 的老毛病）"
            finally:
                transition.cancel()

    def test_window_style_is_only_reapplied_when_the_mode_changes(self, window):
        """同一模式下重复换肤不该再调 ``pywinstyles``。

        ``pywinstyles.detect()`` 内部会 ``window.update()``——一个不在我们
        控制里的"跑一遍事件循环"。模式没变就没必要再请它回来。
        """
        pywinstyles = pytest.importorskip("pywinstyles")
        calls = []
        original = pywinstyles.apply_style
        pywinstyles.apply_style = lambda win, style: calls.append(style)
        try:
            window.theme_myself("light")  # 当前已经是 light
            assert calls == []
            window.theme_myself("dark")
            assert calls == ["dark"]
            window.theme_myself("dark")
            assert calls == ["dark"], "同一模式被重复应用了"
        finally:
            pywinstyles.apply_style = original

    def test_mode_returns_before_any_frame_is_painted(self, window):
        """``mode()`` 返回时一帧都还没画——重活交给事件循环，调用方立刻拿到控制权。"""
        with _AnimationSettings(5, 40):
            build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                assert transition.frames_painted == 0
                assert not transition._finished
            finally:
                transition.cancel()

    def test_frames_are_trimmed_to_fit_the_budget(self, window):
        """一次全树重绘要多久，就按它裁剪帧数——而不是把窗口冻住去硬画。

        ``tksvg`` 下一屏十几个组件重绘一次要上百毫秒。旧实现把这些时间全塞在
        ``mode()`` 里；现在它降的是**帧数**，总时长还有预算兜着。
        """
        with _AnimationSettings(12, 5, budget=60):
            build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                # 跑一拍让 _start 量出重绘开销并裁剪帧数
                deadline = time.time() + 5.0
                while transition.paint_cost_ms == 0 and time.time() < deadline:
                    window.update()
                    if transition._finished:
                        break

                assert transition.requested_steps == 12
                assert transition.paint_cost_ms > 0, "没有量到重绘开销"
                max_steps = int(
                    60 // max(transition.paint_cost_ms, transition.step_time)
                )
                assert transition.steps <= max(1, max_steps)
                assert transition.steps < 12, "预算远小于单帧开销时不该硬撑 12 帧"
            finally:
                transition.cancel()


# ---------------------------------------------------------------------------
# 接管 / 取消
# ---------------------------------------------------------------------------
class TestHandover:
    def test_a_second_switch_takes_over_the_first(self, window):
        """动画途中再切一次：旧的**就地**让位，不叠加帧队列。

        旧实现每切一次就多排一串 ``after``，来回点几下之后帧会互相打架，
        画面停在中间色上。
        """
        with _AnimationSettings(8, 50):
            build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")

            first = manager.mode("dark")
            assert not first._finished
            second = manager.mode("light")
            try:
                assert first._finished, "旧过渡没有被接管"
                assert first._handle is None

                drain(window)
                assert second._finished
                assert tkflu.active_transition() is None
            finally:
                second.cancel()

    def test_only_one_transition_is_active(self, window):
        with _AnimationSettings(6, 40):
            build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                assert tkflu.active_transition() is transition
                assert tkflu.FluThemeManager.running() is transition
            finally:
                transition.cancel()
            assert tkflu.active_transition() is None

    def test_cancel_restores_the_target_colours(self, window):
        with _AnimationSettings(6, 100):
            widgets = build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark")
            try:
                transition._paint(0.5)
                transition.cancel(restore=True)
            finally:
                pass
            for name, widget in widgets.items():
                assert getattr(widget, "_theme_blend", None) is None, name
            from tkflu.designs.label import label as label_design

            assert widgets["label"].attributes.text_color == label_design("dark")[
                "text_color"
            ]

    def test_animation_can_be_turned_off_per_call(self, window):
        """``animation_steps=0`` 时只落结果，不排任何帧。"""
        with _AnimationSettings(6, 40):
            widgets = build_scene(window)
            manager = tkflu.FluThemeManager(window=window, mode="light")
            transition = manager.mode("dark", animation_steps=0)
            assert transition._finished
            assert transition.frames_painted == 0
            from tkflu.designs.label import label as label_design

            assert widgets["label"].attributes.text_color == label_design("dark")[
                "text_color"
            ]


# ---------------------------------------------------------------------------
# 入口容错 / 覆盖
# ---------------------------------------------------------------------------
class TestManagerEntry:
    def test_unknown_mode_falls_back_to_light(self, window):
        """一个手滑的参数不该让整趟换肤崩掉。"""
        build_scene(window)
        manager = tkflu.FluThemeManager(window=window, mode="dark")
        manager.mode("bogus", animation_steps=0)
        assert manager.mode_ == "light"
        manager.mode(None, animation_steps=0)
        assert manager.mode_ == "light"

    def test_toggle_flips_between_the_two_modes(self, window):
        build_scene(window)
        manager = tkflu.FluThemeManager(window=window, mode="light")
        manager.toggle(animation_steps=0)
        assert manager.mode_ == "dark"
        manager.toggle(animation_steps=0)
        assert manager.mode_ == "light"

    def test_a_broken_widget_does_not_stop_the_sweep(self, window):
        """一个组件换肤时抛异常，兄弟组件照样要换上，且**被记录下来**。

        旧实现是 `except AttributeError: continue` 式的静默跳过，连钩子内部
        抛的异常也一起吞了。这里断言异常被记进 ``failures``，好让它可见。
        """
        good = tkflu.FluLabel(window, text="好的", mode="light")
        good.pack()
        bad = tkflu.FluLabel(window, text="坏的", mode="light")
        bad.pack()
        pump(window, 3)

        def explode(*_args, **_kwargs):
            raise RuntimeError("这个组件坏掉了")

        bad.theme = explode

        manager = tkflu.FluThemeManager(window=window, mode="light")
        transition = manager.mode("dark", animation_steps=0)
        assert any(widget is bad for widget, _error in transition.failures)
        assert not any(widget is good for widget, _error in transition.failures)

        from tkflu.designs.label import label as label_design

        assert good.attributes.text_color == label_design("dark")["text_color"]
        assert any("坏掉了" in repr(error) for _widget, error in transition.failures)

    def test_animation_helpers_are_exported(self):
        for name in (
            "ThemeTransition",
            "run_theme_transition",
            "blend_theme_design",
            "collect_themed_widgets",
            "active_transition",
            "interpolatable",
            "set_transition_budget",
            "get_transition_budget",
            "easing_function",
            "easing_names",
            "get_theme_easing",
            "set_theme_easing",
            "suspended_widget_animation",
            "widget_animation_suspended",
        ):
            assert hasattr(tkflu, name), name

    def test_interpolatable_accepts_colours_and_opacities_only(self):
        from tkflu.theme_transition import interpolatable

        assert interpolatable(("back_color",), "#ffffff", "#000000")
        assert interpolatable(("rest", "back_opacity"), 0.0, 1.0)
        # 线宽 / 圆角**不**插值：让边框"长出来"比瞬间变过去更怪
        assert not interpolatable(("border_width",), 1, 3)
        assert not interpolatable(("radius",), 4, 8)
        # 一边是 None（首次构造）也没得插
        assert not interpolatable(("back_color",), None, "#000000")
