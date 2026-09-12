"""tkfluent 组件画廊与命令行入口。

本模块既是 ``python -m tkflu`` 的入口，也可以当普通模块导入使用。

命令行
------
.. code-block:: text

    python -m tkflu                       # 启动组件画廊（默认浅色、库默认渲染引擎）
    python -m tkflu -r skia               # 指定渲染引擎（名字或编号皆可）
    python -m tkflu -r auto               # 自动挑选当前可用的最快引擎
    python -m tkflu --list-engines        # 只列出可用引擎后退出
    python -m tkflu --mode dark           # 深色主题启动
    python -m tkflu --primary purple      # 换主色调
    python -m tkflu --no-animation        # 关掉过渡动画
    python -m tkflu --check               # 无界面自检（建一遍全部组件后退出，CI 可用）

作为模块
--------
.. code-block:: python

    from tkflu.__main__ import main

    raise SystemExit(main(["--renderer", "pillow", "--check"]))

.. note::
   画廊左侧展示"内容型"组件，右侧展示"交互型"组件；底部状态栏实时显示
   当前渲染引擎与图片缓存命中率。点击任何组件都会在控制台打印一行事件日志
   （窗口底部也会显示最近一条），方便确认事件是否按预期触发。
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Callable, Dict, List, Optional, Sequence

__all__ = ["main", "build_parser", "build_gallery", "resolve_renderer"]


def _bootstrap_direct_run() -> None:
    """支持用 ``python path/to/tkflu/__main__.py`` 直接运行本文件。

    直接以脚本方式运行时，``sys.path[0]`` 是**包目录本身**
    （``.../tkfluent/tkflu``），而不是它的上级目录。于是 ``import tkflu``
    会跳到别处去找——可能解析到 site-packages 里已安装的旧版本，
    也可能直接找不到，两种情况都很让人困惑。

    这里在真正导入之前，把包目录的**上级**放进 ``sys.path``，
    让 ``import tkflu`` 稳定地命中本仓库的包。

    经 ``python -m tkflu`` 或作为库导入时，``__package__`` 有值，本函数不做任何事。
    """
    if __package__:
        return
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent not in sys.path:
        sys.path.insert(0, parent)


_bootstrap_direct_run()

#: ``--primary`` 可选的主色调预设 -> defs 里的设置函数名
PRIMARY_PRESETS = {
    "blue": "blue_primary_color",
    "red": "red_primary_color",
    "orange": "orange_primary_color",
    "yellow": "yellow_primary_color",
    "green": "green_primary_color",
    "purple": "purple_primary_color",
}

#: ``-r auto`` 时的偏好顺序：进程内栅格引擎优先（最快），其次才是 SVG 引擎
AUTO_ENGINE_ORDER = ("skia", "cairo", "pillow", "tksvg", "wand")


# ---------------------------------------------------------------------------
# 命令行
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器（单独暴露出来便于测试与复用）。"""
    parser = argparse.ArgumentParser(
        prog="python -m tkflu",
        description="tkfluent 组件画廊：把所有 Fluent 组件摆在一个窗口里",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python -m tkflu                   启动画廊\n"
            "  python -m tkflu -r skia           用 skia 引擎渲染\n"
            "  python -m tkflu --list-engines    查看可用引擎\n"
            "  python -m tkflu --check           无界面自检\n"
        ),
    )
    parser.add_argument(
        "-r",
        "--renderer",
        default=None,
        metavar="ENGINE",
        help=(
            "渲染引擎：名字（tksvg/wand/skia/pillow/cairo）或编号（0-4），"
            "也可以写 auto 自动挑选最快的可用引擎。不指定则沿用库的默认引擎"
        ),
    )
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="列出所有引擎及其可用性后退出",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=("light", "dark"),
        default="light",
        help="启动时的主题模式（默认 light）",
    )
    parser.add_argument(
        "--primary",
        choices=tuple(PRIMARY_PRESETS),
        default=None,
        help="主色调预设（强调色按钮/开关会立刻反映出来）",
    )
    parser.add_argument(
        "--geometry",
        default="640x600",
        metavar="WxH",
        help="窗口尺寸，例如 720x640（默认 640x600）",
    )
    parser.add_argument(
        "--animation-steps",
        type=int,
        default=5,
        metavar="N",
        help="过渡动画的帧数（默认 5；0 表示关闭）",
    )
    parser.add_argument(
        "--animation-step-time",
        type=int,
        default=20,
        metavar="MS",
        help="每帧间隔毫秒数（默认 20）",
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="等价于 --animation-steps 0 --animation-step-time 0",
    )
    parser.add_argument(
        "--cache-budget",
        type=int,
        default=None,
        metavar="PIXELS",
        help="图片缓存的像素预算（默认沿用 tkdeft 的 8,000,000）",
    )
    parser.add_argument(
        "--custom-titlebar",
        type=int,
        choices=(0, 1),
        default=None,
        metavar="WAY",
        help="启用自定义标题栏（实验特性，仅 Windows 有效）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="无界面自检：建出全部组件并跑一遍事件后退出（成功返回 0）",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="退出前打印图片缓存的命中统计",
    )
    return parser


def resolve_renderer(value: Optional[str]):
    """把 ``--renderer`` 的取值解析成**规范的引擎名**。

    * ``None`` / ``"default"`` / ``""`` → ``None``，表示"不要动库的默认值"
    * ``"auto"`` → 当前可用的最快引擎（见 :data:`AUTO_ENGINE_ORDER`）
    * 数字编号（``"2"``）→ 对应引擎名（``"skia"``）
    * 引擎名原样返回（大小写不敏感）

    :raises ValueError: 编号越界，或引擎名无法识别
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in ("default", ""):
        return None

    from tkdeft.engines import RENDERER_INDEX, list_engines

    if text == "auto":
        available = list_engines()
        for name in AUTO_ENGINE_ORDER:
            if available.get(name):
                return name
        return None

    if text.isdigit():
        index = int(text)
        name = RENDERER_INDEX.get(index)
        if name is None:
            raise ValueError(
                f"未知的渲染器编号 {index}；可用编号：{sorted(RENDERER_INDEX)}"
            )
        return name

    if text not in list_engines():
        raise ValueError(
            f"未知的渲染引擎 {value!r}；可用：{sorted(list_engines())}"
        )
    return text


# ---------------------------------------------------------------------------
# 画廊
# ---------------------------------------------------------------------------
class _EventLog:
    """把组件事件同时写到控制台与窗口底部状态栏。"""

    def __init__(self) -> None:
        self.label = None
        self.count = 0

    def attach(self, label) -> None:
        self.label = label

    def __call__(self, text: str) -> None:
        self.count += 1
        _safe_print(f"[{self.count:02d}] {text}")
        if self.label is not None:
            try:
                self.label.dconfigure(text=f"最近事件：{text}")
                self.label._draw()
            except Exception:
                pass


def _safe_print(text: str, stream=None) -> None:
    """打印一行文本，容忍控制台编码不含某些字符。

    Windows 控制台常是 GBK/CP437 码页，直接 ``print`` 含中文的字符串
    在某些码页下会抛 ``UnicodeEncodeError``。这里退化为"替换不可编码字符"
    而不是让演示程序崩掉。
    """
    stream = stream or sys.stdout
    try:
        print(text, file=stream)
    except UnicodeEncodeError:
        encoding = getattr(stream, "encoding", None) or "utf-8"
        print(text.encode(encoding, "replace").decode(encoding, "replace"), file=stream)


def _make_sample_image(master, width: int = 96, height: int = 48):
    """生成一张示意图片，避免演示依赖外部素材文件。"""
    try:
        from PIL import Image, ImageDraw, ImageTk
    except Exception:  # pragma: no cover - Pillow 是硬依赖
        return None

    image = Image.new("RGB", (width, height), (0, 95, 184))
    draw = ImageDraw.Draw(image)
    for x in range(width):  # 横向渐变，直观看出图片确实被渲染了
        t = x / max(1, width - 1)
        draw.line(
            [(x, 0), (x, height)],
            fill=(int(0 + 120 * t), int(95 + 120 * t), int(184 + 60 * t)),
        )
    draw.rectangle([0, 0, width - 1, height - 1], outline=(255, 255, 255))
    return ImageTk.PhotoImage(image, master=master)


def build_gallery(root, mode: str = "light", log: Optional[Callable] = None) -> Dict:
    """在 ``root`` 里搭出完整的组件画廊。

    Returns:
        关键字为组件名、值为组件实例的字典；另外含 ``"__log__"`` 与
        ``"__status__"`` 两个非组件条目，方便调用方做自检。
    """
    import tkinter as tk

    import tkflu
    from tkflu.image import FluImage
    from tkflu.listbox import FluListBox

    emit = log if log is not None else (lambda text: print(text))
    widgets: Dict = {}

    def track(name, widget):
        widgets[name] = widget
        return widget

    # ---- 菜单栏 ----------------------------------------------------------
    menubar = track("menubar", tkflu.FluMenuBar(root, mode=mode))
    menubar.add_command(label="文件", command=lambda: emit("菜单 → 文件"))
    menubar.add_command(label="编辑", command=lambda: emit("菜单 → 编辑"))

    view_menu = tkflu.FluMenu()
    view_menu.add_command(label="浅色主题", command=lambda: emit("菜单 → 浅色主题"))
    view_menu.add_command(label="深色主题", command=lambda: emit("菜单 → 深色主题"))
    menubar.add_cascade(label="视图", menu=view_menu)

    more_menu = tkflu.FluMenu()
    more_menu.add_command(label="子项 A", command=lambda: emit("菜单 → 子项 A"))
    more_menu.add_command(label="子项 B", command=lambda: emit("菜单 → 子项 B"))

    nested_menu = tkflu.FluMenu()
    nested_menu.add_command(label="嵌套项 1", command=lambda: emit("菜单 → 嵌套项 1"))
    nested_menu.add_command(label="嵌套项 2", command=lambda: emit("菜单 → 嵌套项 2"))
    more_menu.add_cascade(label="更深一层", menu=nested_menu)

    menubar.add_cascade(label="更多", menu=more_menu)
    menubar.pack(fill="x", side="top")

    # ---- 主体：左右两栏 ---------------------------------------------------
    main = track("frame", tkflu.FluFrame(root, width=600, height=470, mode=mode))
    main.pack(fill="both", expand=True, side="top", padx=12, pady=(10, 0))

    left = tkflu.FluFrame(main, width=270, height=430, mode=mode)
    left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

    right = tkflu.FluFrame(main, width=270, height=430, mode=mode)
    right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

    def section(parent, text):
        label = tkflu.FluLabel(parent, text=text, mode=mode)
        label.pack(anchor="w", padx=6, pady=(8, 2))
        return label

    # ---- 左栏：内容展示类 -------------------------------------------------
    section(left, "标签 / 徽标")
    label = track(
        "label",
        tkflu.FluLabel(left, text="FluLabel（悬停看提示）", mode=mode),
    )
    label.tooltip(text="这是 FluToolTip")
    label.pack(anchor="w", padx=6, pady=2)

    badge = track("badge", tkflu.FluBadge(left, text="FluBadge", width=90, mode=mode))
    badge.pack(anchor="w", padx=6, pady=2)

    badge_accent = track(
        "badge_accent",
        tkflu.FluBadge(left, text="Accent", width=90, mode=mode, style="accent"),
    )
    badge_accent.pack(anchor="w", padx=6, pady=2)

    section(left, "输入")
    entry = track("entry", tkflu.FluEntry(left, width=230, mode=mode))
    entry.pack(fill="x", padx=6, pady=2)

    text = track("text", tkflu.FluText(left, width=230, height=56, mode=mode))
    text.pack(fill="x", padx=6, pady=2)

    section(left, "列表 / 图片")
    listbox = track("listbox", FluListBox(left, text="FluListBox", width=120, mode=mode))
    listbox.pack(anchor="w", padx=6, pady=2)

    sample = _make_sample_image(root)
    if sample is not None:
        try:
            image_widget = track("image", FluImage(left, image=sample, mode=mode))
            image_widget.pack(anchor="w", padx=6, pady=6)
        except Exception as exc:  # 图片组件失败不该拖垮整个画廊
            emit(f"FluImage 初始化失败：{type(exc).__name__}: {exc}")

    # ---- 右栏：交互类 -----------------------------------------------------
    section(right, "按钮")
    button = track(
        "button",
        tkflu.FluButton(
            right, text="FluButton", width=220, mode=mode,
            command=lambda: emit("FluButton → Clicked"),
        ),
    )
    button.pack(fill="x", padx=6, pady=2)

    button_accent = track(
        "button_accent",
        tkflu.FluButton(
            right, text="Accent", width=220, mode=mode, style="accent",
            command=lambda: emit("FluButton(Accent) → Clicked"),
        ),
    )
    button_accent.pack(fill="x", padx=6, pady=2)

    button_menu = track(
        "button_menu",
        tkflu.FluButton(
            right, text="Menu 样式", width=220, mode=mode, style="menu",
            command=lambda: emit("FluButton(Menu) → Clicked"),
        ),
    )
    button_menu.pack(fill="x", padx=6, pady=2)

    button_disabled = track(
        "button_disabled",
        tkflu.FluButton(
            right, text="Disabled", width=220, mode=mode, state="disabled"
        ),
    )
    button_disabled.pack(fill="x", padx=6, pady=2)

    section(right, "开关 / 滑块")
    toggle = track(
        "toggle",
        tkflu.FluToggleButton(
            right, text="FluToggleButton", width=220, mode=mode,
            command=lambda: emit(
                f"FluToggleButton → checked={toggle.dcget('checked')}"
            ),
        ),
    )
    toggle.pack(fill="x", padx=6, pady=2)

    slider = track(
        "slider",
        tkflu.FluSlider(
            right, width=220, height=28, value=5, min=0, max=10, mode=mode,
            changed=lambda: emit(f"FluSlider → value={slider.dcget('value')}"),
        ),
    )
    slider.pack(fill="x", padx=6, pady=4)

    scrollbar = track("scrollbar", tkflu.FluScrollBar(right, mode=mode))
    scrollbar.pack(anchor="w", padx=6, pady=2)

    # ---- 底部：事件日志 + 状态栏 ------------------------------------------
    bottom = tkflu.FluFrame(root, width=600, height=96, mode=mode)
    bottom.pack(fill="x", side="bottom", padx=12, pady=(6, 10))

    log_label = track(
        "log_label",
        tkflu.FluLabel(bottom, text="最近事件：—", mode=mode),
    )
    log_label.pack(anchor="w", padx=10, pady=(8, 2))

    status = track(
        "status",
        tkflu.FluLabel(bottom, text="", mode=mode),
    )
    status.pack(anchor="w", padx=10, pady=(0, 8))

    # ---- 主题切换（需要 thememanager）-------------------------------------
    thememanager = tkflu.FluThemeManager(window=root, mode=mode)
    widgets["__theme_manager__"] = thememanager

    theme_toggle = track(
        "theme_toggle",
        tkflu.FluToggleButton(
            bottom, text="切换主题", width=110, mode=mode,
            command=lambda: tkflu.toggle_theme(theme_toggle, thememanager),
        ),
    )
    theme_toggle.pack(side="left", padx=10, pady=(0, 8))

    def toggle_state():
        target_state = (
            tkflu.DISABLED if button.dcget("state") == tkflu.NORMAL else tkflu.NORMAL
        )
        for widget in (button, button_accent, entry, text, toggle, slider):
            widget.dconfigure(state=target_state)
        emit(f"批量切换状态 → {target_state}")

    state_toggle = track(
        "state_toggle",
        tkflu.FluToggleButton(
            bottom, text="切换可用状态", width=130, mode=mode, command=toggle_state
        ),
    )
    state_toggle.pack(side="left", padx=10, pady=(0, 8))

    def refresh_status():
        from tkdeft.engines import cache_stats, get_engine_name

        stats = cache_stats()
        text_value = (
            f"引擎：{get_engine_name()}　"
            f"缓存：{stats['entries']} 张 / 命中率 {stats['hit_rate'] * 100:.1f}%"
        )
        status.dconfigure(text=text_value)
        status._draw()
        emit(text_value)

    status_button = track(
        "status_button",
        tkflu.FluButton(
            bottom, text="刷新状态", width=100, mode=mode, command=refresh_status
        ),
    )
    status_button.pack(side="left", padx=10, pady=(0, 8))
    refresh_status()

    widgets["__log__"] = emit
    widgets["__status__"] = status
    widgets["__root__"] = root
    return widgets


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def _list_engines() -> int:
    """打印引擎清单（顺序与 ``renderer`` 编号一致）。"""
    from tkdeft.engines import RENDERER_INDEX, get_engine_name, list_engines

    available = list_engines()
    current = get_engine_name()
    _safe_print("可用渲染引擎：")
    for index in sorted(RENDERER_INDEX):
        name = RENDERER_INDEX[index]
        if name not in available:
            continue
        mark = "  ← 当前" if name == current else ""
        state = "可用" if available[name] else "缺少依赖"
        _safe_print(f"  {index}  {name:8s} {state}{mark}")
    _safe_print("\n用 -r/--renderer 指定，例如：python -m tkflu -r skia")
    return 0


def _apply_options(args) -> Optional[int]:
    """应用与界面无关的选项。返回非 ``None`` 表示应当立即以该码退出。"""
    import tkflu

    if args.cache_budget is not None:
        from tkdeft.engines import set_cache_budget

        set_cache_budget(args.cache_budget)

    steps = 0 if args.no_animation else max(0, args.animation_steps)
    step_time = 0 if args.no_animation else max(0, args.animation_step_time)
    tkflu.set_animation_steps(steps)
    tkflu.set_animation_step_time(step_time)

    if args.primary:
        getattr(tkflu, PRIMARY_PRESETS[args.primary])()

    try:
        renderer = resolve_renderer(args.renderer)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    if renderer is not None:
        # 引擎名可能合法但依赖缺失（例如没装 skia-python）
        try:
            tkflu.set_renderer(renderer)
        except ValueError as exc:
            _safe_print(f"错误：{exc}", stream=sys.stderr)
            _safe_print("\n可用引擎：", stream=sys.stderr)
            _list_engines_quiet()
            return 2
    return None


def _list_engines_quiet() -> None:
    from tkdeft.engines import list_engines

    for name, ok in list_engines().items():
        _safe_print(f"  {'✓' if ok else '✗'} {name}", stream=sys.stderr)


#: 自检时对每个组件尝试调用的钩子（没有该属性的组件会自动跳过）
_CHECK_STEPS = (
    ("重绘", lambda w: w._draw()),
    ("浅色主题", lambda w: w.theme(mode="light")),
    ("深色主题", lambda w: w.theme(mode="dark")),
    ("鼠标进入", lambda w: w._event_enter()),
    ("鼠标离开", lambda w: w._event_leave()),
    ("按下", lambda w: w._event_on_button1()),
    ("抬起", lambda w: w._event_off_button1()),
    ("尺寸变化", lambda w: w._event_configure()),
)


def _run_check(root, log: _EventLog, widgets: Dict) -> int:
    """无界面自检：把全部组件的事件钩子跑一遍，确认没有异常。

    这是给 CI 用的——它能在无人值守环境下抓出"构造签名不匹配、
    某个引擎下绘制报错"这类问题，而不需要真的看界面。
    """
    import tkinter as tk

    from tkdeft.engines import cache_stats, get_engine_name

    failures: List[str] = []

    try:
        for _ in range(30):
            root.update()
    except Exception as exc:
        failures.append(f"事件循环：{type(exc).__name__}: {exc}")

    components = {
        name: widget
        for name, widget in widgets.items()
        if not name.startswith("__") and widget is not root
    }
    checked = 0
    for name, widget in components.items():
        for step_name, step in _CHECK_STEPS:
            try:
                step(widget)
            except AttributeError:
                continue  # 该组件没有这个钩子，属正常
            except tk.TclError as exc:
                failures.append(f"{name} @ {step_name}：TclError: {exc}")
            except Exception as exc:
                failures.append(f"{name} @ {step_name}：{type(exc).__name__}: {exc}")
        checked += 1
    log(f"自检：跑完 {checked} 个组件的 {len(_CHECK_STEPS)} 类钩子")

    try:
        stats = cache_stats()
        print(
            f"自检完成：引擎 {get_engine_name()}，"
            f"缓存 {stats['entries']} 张，命中率 {stats['hit_rate'] * 100:.1f}%，"
            f"溢出 {stats['overflow']} 次"
        )
    except Exception as exc:
        failures.append(f"缓存统计：{type(exc).__name__}: {exc}")

    # 菜单栏的级联会创建弹出用的 Toplevel。
    # 注意：这里必须"各自独立地"容错——早先的写法把销毁循环和 root.destroy()
    # 放在同一个 try 里，循环一抛异常就会跳过 root.destroy()，于是
    # tkinter._default_root 残留、后续再建窗口就会撞上
    # "bad window path name"。
    for child in list(root.winfo_children()):
        if isinstance(child, tk.Toplevel):
            try:
                child.destroy()
            except Exception as exc:
                failures.append(
                    f"销毁弹出窗口：{type(exc).__name__}: {exc}"
                )
    try:
        root.destroy()
    except Exception as exc:
        failures.append(f"销毁主窗口：{type(exc).__name__}: {exc}")

    if failures:
        for line in failures:
            _safe_print(f"自检失败：{line}", stream=sys.stderr)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行入口。返回进程退出码。

    :param argv: 参数列表；``None`` 表示取 ``sys.argv[1:]``
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_engines:
        return _list_engines()

    rc = _apply_options(args)
    if rc is not None:
        return rc

    import tkflu

    root = tkflu.FluWindow(mode=args.mode)
    root.title(f"tkfluent 组件画廊 · {args.mode}")
    try:
        root.geometry(args.geometry)
    except Exception:
        print(f"警告：--geometry {args.geometry!r} 无效，改用默认尺寸", file=sys.stderr)
        root.geometry("640x600")

    if args.custom_titlebar is not None:
        try:
            root.wincustom(way=args.custom_titlebar)
        except Exception as exc:
            print(
                f"警告：自定义标题栏不可用（{type(exc).__name__}: {exc}）",
                file=sys.stderr,
            )

    if args.check:
        # 自检不该弹出窗口，但仍要真实建出组件才能暴露签名/绘制问题
        root.withdraw()

    log = _EventLog()
    widgets = build_gallery(root, mode=args.mode, log=log)
    log.attach(widgets.get("log_label"))

    if args.check:
        return _run_check(root, log, widgets)

    root.mainloop()

    if args.stats:
        from tkdeft.engines import cache_stats, get_engine_name

        stats = cache_stats()
        print(
            f"\n引擎 {get_engine_name()}：缓存 {stats['entries']} 张（{stats['pixels']} 像素），"
            f"命中 {stats['hits']} / 未命中 {stats['misses']}，"
            f"命中率 {stats['hit_rate'] * 100:.1f}%，溢出 {stats['overflow']} 次"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
