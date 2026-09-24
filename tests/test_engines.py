"""逐引擎冒烟：五个渲染引擎下都要能把这些组件建出来、画出来、换肤。

这是"组件层"的引擎矩阵，与 tkdeft 的 ``benchmarks/smoke_widgets.py`` 互补：
那边覆盖的是绘制图元，这边覆盖的是 tkfluent 的组件（含本轮新增的
复选框 / 单选框 / 列表 / 导航栏）。
"""

from __future__ import annotations

import pytest

import tkflu
from conftest import ENGINES, _new_window, requires_tk

pytestmark = requires_tk


def pump(root, times=6):
    for _ in range(times):
        root.update()


@pytest.fixture(params=ENGINES)
def active_engine(request):
    """切到某个引擎；缺依赖时自动跳过。"""
    from tkdeft.engines import list_engines

    if not list_engines().get(request.param):
        pytest.skip(f"引擎 {request.param} 不可用（缺依赖）")
    previous = tkflu.get_engine_name()
    tkflu.set_renderer(request.param)
    try:
        yield request.param
    finally:
        tkflu.set_renderer(previous)


def build_all(root, mode="light"):
    """把全部公开组件摆出来，返回 ``{名字: 组件}``。"""
    widgets = {}
    widgets["label"] = tkflu.FluLabel(root, text="标签", mode=mode)
    widgets["badge"] = tkflu.FluBadge(root, text="徽标", mode=mode)
    widgets["button"] = tkflu.FluButton(root, text="按钮", mode=mode)
    widgets["button_accent"] = tkflu.FluButton(
        root, text="强调", mode=mode, style="accent"
    )
    widgets["toggle"] = tkflu.FluToggleButton(root, text="开关", mode=mode)
    widgets["entry"] = tkflu.FluEntry(root, width=150, mode=mode)
    widgets["text"] = tkflu.FluText(root, width=150, height=60, mode=mode)
    widgets["slider"] = tkflu.FluSlider(root, width=150, mode=mode)
    widgets["slider_v"] = tkflu.FluSlider(
        root, width=28, height=120, orient="vertical", mode=mode
    )
    widgets["scrollbar"] = tkflu.FluScrollBar(
        root, width=150, height=8, orient="horizontal", mode=mode
    )
    widgets["checkbox"] = tkflu.FluCheckBox(root, text="复选框", mode=mode)
    widgets["checkbox_three"] = tkflu.FluCheckBox(
        root, text="三态", checked=None, three_state=True, mode=mode
    )
    widgets["radio"] = tkflu.FluRadioBox(
        root, text="单选", value="a", group="engine-smoke", mode=mode
    )
    widgets["listbox"] = tkflu.FluListBox(
        root, width=200, height=120, items=[f"行 {i}" for i in range(20)], mode=mode
    )
    widgets["nav"] = tkflu.FluLiteNav(
        root,
        items=[("★", "一"), ("☆", "二")],
        orient="horizontal",
        style="card",
        mode=mode,
    )
    widgets["frame"] = tkflu.FluFrame(root, width=120, height=60, mode=mode)

    for widget in widgets.values():
        widget.pack(anchor="w", padx=4, pady=1)
    return widgets


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_every_widget_builds_and_draws(active_engine, mode):
    root = _new_window()
    try:
        root.geometry("560x900+40+20")
        root.deiconify()
        widgets = build_all(root, mode=mode)
        pump(root, 12)

        for name, widget in widgets.items():
            assert widget.winfo_exists(), name
            assert widget.winfo_ismapped() or name in ("text",), name

        # 换肤走一遍真实路径（含窗口与嵌套面板的递归）
        manager = tkflu.FluThemeManager(window=root, mode=mode)
        for target in ("dark", "light"):
            manager.mode(target)
            pump(root, 3)
    finally:
        root.destroy()


def test_gallery_self_check_passes_on_every_engine(active_engine):
    """``python -m tkflu --check`` 的等价路径（程序内调用）。

    ``main()`` 会按 CLI 参数**全局**改动画设置，测完要还原，
    否则后面的测试会莫名其妙地跑在"开动画"的状态下。
    """
    from tkflu.__main__ import main
    from tkflu.designs.animation import (
        get_animation_step_time,
        get_animation_steps,
        set_animation_step_time,
        set_animation_steps,
    )

    steps, step_time = get_animation_steps(), get_animation_step_time()
    try:
        assert main(["--check"]) == 0
    finally:
        set_animation_steps(steps)
        set_animation_step_time(step_time)


def test_gallery_builds_like_the_cli(active_engine):
    """画廊里必须出现本轮新增的组件。"""
    from tkflu.__main__ import build_gallery

    root = _new_window()
    try:
        root.geometry("760x900+40+20")
        root.deiconify()
        widgets = build_gallery(root, mode="light", log=lambda text: None)
        pump(root, 12)
        for key in (
            "checkbox",
            "checkbox_three",
            "radio_a",
            "radio_b",
            "radio_c",
            "listbox",
            "nav",
        ):
            assert key in widgets, f"画廊里缺少 {key}"
        assert len(widgets["listbox"]) == 30
        assert len(widgets["nav"]) == 3
    finally:
        root.destroy()
