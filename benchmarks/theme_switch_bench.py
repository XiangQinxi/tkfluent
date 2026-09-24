"""主题切换基准：量"一次一键换肤"到底花了多少时间、是不是同步、阻塞在哪。

为什么需要这个脚本
------------------
"主题切换卡顿 / 一个一个变色"是主观描述，量不出来的话就只能靠感觉改。
这里把它拆成几个可测量的数：

``mode_sync_ms``
    ``FluThemeManager.mode()`` **这一次调用自己**花了多久。这段时间里 Tk
    的事件循环是**卡死**的（旧实现每个组件都调 ``update()``），用户
    点完按钮到界面响应之间的延迟就是它。
``sweep_ms``
    从点下按钮到"最后一帧画完"的总时间。理想值 ≈ ``steps × step_time``；
    明显超出就说明动画在拖尾。
``max_stall_ms``
    单次回调里最长的"不返回到事件循环"的时间——用户感知到的掉帧。
``distinct_colors``
    被采样控件在整趟换肤里出现过几种不同的中间色。**1 意味着根本没过过渡**
    （一步跳到终态），≈ ``steps + 1`` 才是真的在渐变。
``sync_spread_ms``
    各采样控件"第一次变色"的时刻之间的最大差值。这是"同步进行"的直接度量：
    旧实现里每个组件各排各的 ``after``，这个数会是几十到几百毫秒；
    统一时间轴下应当接近 0。

用法::

    python benchmarks/theme_switch_bench.py                  # 默认 5 帧 × 20ms
    python benchmarks/theme_switch_bench.py --widgets 30
    python benchmarks/theme_switch_bench.py --json out.json --label after
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def build_scene(root, extra_widgets: int = 0, mode: str = "light"):
    """摆一屏有代表性的组件，返回 ``(主题管理器, 采样点, 面板)``。

    "采样点"是可以直接读配色属性的组件——基准靠比对它们的
    ``attributes`` 来数中间色、算同步偏差。
    """
    import tkflu

    widgets = []
    sampled = []

    frame = tkflu.FluFrame(root, width=520, height=380, mode=mode)
    frame.pack(padx=8, pady=8)

    for text, style in (("标准", "standard"), ("强调", "accent"), ("菜单", "menu")):
        button = tkflu.FluButton(frame, text=text, width=200, mode=mode, style=style)
        button.pack(pady=2)
        widgets.append(button)
        sampled.append(("FluButton:" + text, button))

    badge = tkflu.FluBadge(frame, text="Badge", width=90, mode=mode)
    badge.pack(pady=2)
    widgets.append(badge)
    sampled.append(("FluBadge", badge))

    checkbox = tkflu.FluCheckBox(frame, text="复选", mode=mode)
    checkbox.pack(pady=2)
    widgets.append(checkbox)
    sampled.append(("FluCheckBox", checkbox))

    label = tkflu.FluLabel(frame, text="标签", mode=mode)
    label.pack(pady=2)
    widgets.append(label)
    sampled.append(("FluLabel", label))

    entry = tkflu.FluEntry(frame, width=200, mode=mode)
    entry.pack(pady=2)
    widgets.append(entry)

    text_box = tkflu.FluText(frame, width=200, height=48, mode=mode)
    text_box.pack(pady=2)
    widgets.append(text_box)

    slider = tkflu.FluSlider(frame, width=200, mode=mode)
    slider.pack(pady=2)
    widgets.append(slider)

    bar = tkflu.FluScrollBar(frame, width=200, height=6, mode=mode)
    bar.pack(pady=2)
    widgets.append(bar)

    toggle = tkflu.FluToggleButton(frame, text="开关", width=200, mode=mode)
    toggle.pack(pady=2)
    widgets.append(toggle)

    for index in range(extra_widgets):
        extra = tkflu.FluButton(frame, text=f"额外 {index}", width=200, mode=mode)
        extra.pack(pady=1)
        widgets.append(extra)

    manager = tkflu.FluThemeManager(window=root, mode=mode)
    return manager, sampled, frame


def _is_hex(value) -> bool:
    return isinstance(value, str) and value.startswith("#") and len(value) in (4, 7, 9)


def _signature(widget):
    """控件的"配色指纹"：它所有颜色叶子的当前取值。

    用指纹而不是单个字段来数中间色，是因为**很多字段在两个主题下本来就一样**
    （标准按钮的 ``rest.back_color`` 深浅色都是白的），拿它当指标会得出
    "没有动画"的错误结论。指纹涵盖了每个叶子，只要有一处变了就算一帧。
    """
    from tkflu.theme_transition import _leaves

    try:
        items = [
            (path, value)
            for path, value in _leaves(widget.attributes)
            if _is_hex(value)
        ]
    except Exception:
        return None
    return tuple(sorted((str(path), value) for path, value in items))


def _measure_once(root, manager, target, sampled, timeout_ms: int):
    """切一次主题并量到底。**跑真正的 mainloop**。

    不能用 ``while: root.update()`` 忙等：``update()`` 会把所有到点的回调
    一口气跑完，整段动画会被压进一次调用里，采样器一个中间帧都看不到
    （测出来的"过渡帧数"会假得离谱）。mainloop 才会在每帧之间回到空闲、
    让重绘真正发生。
    """
    started = time.perf_counter()
    transition = manager.mode(target)
    sync_ms = (time.perf_counter() - started) * 1000.0

    seen = {name: [_signature(widget)] for name, widget in sampled}
    first_change = {}
    gaps = []
    state = {"running": True, "last_tick": started, "quiet_since": started}

    def sample():
        now = time.perf_counter()
        gaps.append((now - state["last_tick"]) * 1000.0)
        state["last_tick"] = now
        elapsed_ms = (now - started) * 1000.0
        changed = False
        for name, widget in sampled:
            value = _signature(widget)
            if value != seen[name][-1]:
                seen[name].append(value)
                first_change.setdefault(name, elapsed_ms)
                changed = True
        if changed:
            state["quiet_since"] = now
        if state["running"]:
            root.after(2, sample)

    def watch():
        now = time.perf_counter()
        if (now - started) * 1000.0 > timeout_ms:
            state["running"] = False
            root.quit()
            return
        finished = getattr(transition, "_finished", None)
        if finished is None:
            # 不认识过渡对象（旧版本）：退化成"颜色安静下来就算完"
            finished = (now - state["quiet_since"]) > 0.08 and (
                now - started
            ) > 0.05
        if finished:
            state["running"] = False
            root.quit()
            return
        root.after(5, watch)

    root.after(2, sample)
    root.after(5, watch)
    root.mainloop()
    sweep_ms = (time.perf_counter() - started) * 1000.0

    counts = [len(values) for values in seen.values()]
    spread = None
    if len(first_change) >= 2:
        moments = sorted(first_change.values())
        spread = moments[-1] - moments[0]

    return {
        "sync_ms": sync_ms,
        "sweep_ms": sweep_ms,
        "max_gap_ms": max(gaps) if gaps else 0.0,
        "distinct_colors": statistics.mean(counts),
        "sync_spread_ms": spread,
        "detail": transition,
    }


def measure(root, manager, sampled, cycles: int = 6, timeout_ms: int = 4000):
    """反复来回切主题，汇总各项指标。"""
    sync_times = []
    sweep_times = []
    gaps = []
    color_counts = []
    spreads = []
    details = []

    for cycle in range(cycles):
        target = "dark" if cycle % 2 == 0 else "light"
        result = _measure_once(root, manager, target, sampled, timeout_ms)
        sync_times.append(result["sync_ms"])
        sweep_times.append(result["sweep_ms"])
        gaps.append(result["max_gap_ms"])
        color_counts.append(result["distinct_colors"])
        if result["sync_spread_ms"] is not None:
            spreads.append(result["sync_spread_ms"])
        detail = result["detail"]
        if hasattr(detail, "describe"):
            details.append(detail.describe())

    return {
        "mode_sync_ms": round(statistics.mean(sync_times), 2),
        "mode_sync_max_ms": round(max(sync_times), 2),
        "sweep_ms": round(statistics.mean(sweep_times), 2),
        "max_gap_ms": round(max(gaps), 2),
        "distinct_colors": round(statistics.mean(color_counts), 2),
        "sync_spread_ms": round(statistics.mean(spreads), 2) if spreads else None,
        "last_detail": details[-1] if details else None,
    }


def build_gallery_scene(root, mode="light"):
    """用**真正的组件画廊**做场景（``python -m tkflu`` 里那一屏）。

    这是最有代表性的一档：59 个控件参与换肤，包含嵌套面板、菜单栏、
    列表 / 导航栏这类"重"组件。基准默认跑的是精简场景（快），
    ``--gallery`` 打开这个。
    """
    from tkflu.__main__ import build_gallery

    widgets = build_gallery(root, mode=mode, log=lambda text: None)
    sampled = [
        (name, widget)
        for name, widget in widgets.items()
        if not name.startswith("__") and hasattr(widget, "attributes")
    ][:6]
    try:
        # 0.5.0 起才有；拿不到也没关系，只是少打印一行规模信息
        from tkflu.theme_transition import collect_themed_widgets

        print(f"[gallery] 参与换肤的控件数：{len(collect_themed_widgets(root))}")
    except ImportError:
        pass
    return widgets["__theme_manager__"], sampled, widgets.get("frame")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="主题切换耗时基准")
    parser.add_argument("--widgets", type=int, default=0, help="额外按钮个数")
    parser.add_argument(
        "--gallery",
        action="store_true",
        help="用完整组件画廊当场景（59 个控件，最贴近真实使用）",
    )
    parser.add_argument("--steps", type=int, default=5, help="动画帧数")
    parser.add_argument("--step-time", type=int, default=20, help="每帧毫秒")
    parser.add_argument("--cycles", type=int, default=6, help="来回切换轮数")
    parser.add_argument("--renderer", default=None, help="渲染引擎（默认库默认值）")
    parser.add_argument("--json", default=None, help="把结果写到这个 JSON 文件")
    parser.add_argument("--label", default="", help="给这次结果起个名字")
    args = parser.parse_args(argv)

    import tkflu

    if args.renderer:
        tkflu.set_renderer(args.renderer)
    tkflu.set_animation_steps(args.steps)
    tkflu.set_animation_step_time(args.step_time)

    root = tkflu.FluWindow(mode="light")
    root.geometry("620x1000+30+30" if not args.gallery else "760x980+30+30")
    root.deiconify()
    for _ in range(15):
        root.update()

    if args.gallery:
        manager, sampled, frame = build_gallery_scene(root)
    else:
        manager, sampled, frame = build_scene(root, args.widgets)
    for _ in range(15):
        root.update()

    result = measure(root, manager, sampled, cycles=args.cycles)
    result.update(
        {
            "label": args.label or "current",
            "scene": "gallery" if args.gallery else "compact",
            "extra_widgets": args.widgets,
            "steps": args.steps,
            "step_time": args.step_time,
            "renderer": tkflu.get_engine_name(),
            "expected_sweep_ms": args.steps * args.step_time,
        }
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)

    try:
        root.destroy()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
