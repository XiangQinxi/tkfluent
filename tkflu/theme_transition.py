"""主题过渡：把整棵控件树的换肤放到**同一条时间轴**上。

为什么需要它
------------
"一键换肤"的朴素实现是这样写的（见 0.4.0 之前的 :mod:`tkflu.thememanager`）::

    for widget in window.winfo_children():
        widget.theme(mode=mode)      # 每个组件内部各自排一串 after 做自己的过渡
        widget._draw()
        widget.update()              # ← 这一句把事件循环跑了起来

问题有三个，且互相放大：

1. **阻塞**。``update()`` 会处理**全部**待办事件（含用户输入、重绘、定时器）。
   组件越多，这一趟循环就越长；实测 41 个组件的画廊里
   ``FluThemeManager.mode()`` 单次调用要 **2.1 秒**，这期间窗口完全点不动。
2. **不同步**。每个组件的过渡各排各的 ``after``，起点是"轮到它自己"的那一刻。
   而上面那个 ``update()`` 又会把已经到点、属于**前面**组件的帧就地执行掉，
   于是画面变成"一个一个地变色"。
3. **动画被吃掉**。真正跑完的帧全在那次 ``mode()`` 调用里消耗掉了，
   用户看到的不是过渡，而是"卡两秒然后瞬间变色"。

这里换一种组织方式：

* **先静默地算目标**。在 :func:`~tkflu.designs.animation.suspended_widget_animation`
  保护下依次调用各组件**原有**的 ``theme()``，于是配色被写进 ``attributes``，
  但组件自己的过渡动画全部让路。这一趟不碰事件循环，也不重绘。
* **再统一插值**。对每个组件做一次 ``attributes`` 快照，与目标值逐叶子比对，
  挑出**能插值的叶子**（``#rrggbb`` 颜色、``*_opacity`` 数值）。
* **一条时间轴画所有组件**。整棵树共用 ``steps`` 帧、一张 ``after`` 链，
  每帧把所有组件的中间色一次性写进去再统一重绘 —— 这才是"同步"。
* **时间轴自己会丢帧**。帧索引由**真实流逝的时间**算出来，而不是"排了几帧"。
  某一帧画得太慢时，下一帧直接跳到该到的位置，因此总时长始终是
  ``steps × step_time``，不会因为组件多而拖尾。

对组件的要求只有一条：配色状态放在 ``self.attributes`` 里（这本就是 tkfluent 的
一贯做法）。基于"设计规范字典"重算配色的组件（``FluCheckBox`` / ``FluRadioBox`` /
``FluListBox`` / ``FluLiteNav``）需要在它们的 ``_apply_design()`` 里调一次
:func:`blend_theme_design`，否则 ``_draw()`` 里的重算会把中间色覆盖掉。

用法::

    from tkflu.theme_transition import run_theme_transition

    run_theme_transition(root, "dark")          # 整棵树一起过渡
    run_theme_transition(root, "dark", steps=0) # 只要结果，不要动画
"""

from __future__ import annotations

import re
from os import environ
from time import perf_counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "ThemeTransition",
    "WidgetThemePlan",
    "run_theme_transition",
    "active_transition",
    "applying_themes",
    "blend_theme_design",
    "collect_themed_widgets",
    "interpolatable",
    "set_transition_budget",
    "get_transition_budget",
    "DEFAULT_TRANSITION_BUDGET_MS",
]

#: ``#rgb`` / ``#rrggbb`` / ``#rrggbbaa``
_HEX_RE = re.compile(r"^#(?P<body>[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


# ---------------------------------------------------------------------------
# 小工具：安全快照 / 路径读写
# ---------------------------------------------------------------------------
def _is_mapping(value) -> bool:
    """``dict`` / ``EasyDict`` 都算。不认其它 Mapping——避免误碰 Tk 对象。"""
    return isinstance(value, dict)


def _copy_like(value):
    """按**原类型**深拷贝嵌套字典。

    必须保类型：``attributes.rest`` 是 ``EasyDict``，组件里到处写
    ``attributes.rest.back_color``。换成普通 ``dict`` 就会 AttributeError。

    只递归 dict / list / tuple，其它对象（字体、回调、子控件引用）一律原样返回，
    绝不去复制一个 Tk 控件。
    """
    if _is_mapping(value):
        copied = {key: _copy_like(item) for key, item in value.items()}
        try:
            return type(value)(copied)
        except Exception:
            return copied
    if isinstance(value, list):
        return [_copy_like(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_like(item) for item in value)
    return value


def _leaves(value, prefix: Tuple = ()):
    """把嵌套结构摊平成 ``(路径, 叶子值)``。

    只有"不是容器"的值才算叶子；空容器本身算叶子（它的值是 ``{}``，
    插值阶段会被 :func:`_classify` 直接排除）。
    """
    if _is_mapping(value):
        if not value:
            yield prefix, value
            return
        for key, item in value.items():
            yield from _leaves(item, prefix + (key,))
        return
    if isinstance(value, (list, tuple)):
        if not value:
            yield prefix, value
            return
        for index, item in enumerate(value):
            yield from _leaves(item, prefix + (index,))
        return
    yield prefix, value


def _has_path(mapping, path: Sequence) -> bool:
    current = mapping
    for key in path:
        if not _is_mapping(current) and not isinstance(current, (list, tuple)):
            return False
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return False
    return True


def _set_path(mapping, path: Sequence, value) -> None:
    current = mapping
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


# ---------------------------------------------------------------------------
# 颜色 / 数值插值
# ---------------------------------------------------------------------------
def _parse_color(value):
    """``#rgb`` / ``#rrggbb`` / ``#rrggbbaa`` → ``(r, g, b, a 或 None, 原始位数)``。"""
    if not isinstance(value, str):
        return None
    match = _HEX_RE.match(value.strip())
    if not match:
        return None
    body = match.group("body")
    if len(body) == 3:
        body = "".join(ch * 2 for ch in body)
    rgb = tuple(int(body[i : i + 2], 16) for i in (0, 2, 4))
    alpha = int(body[6:8], 16) if len(body) == 8 else None
    return rgb + (alpha, len(body) // 2)


def _to_number(value):
    """数值型叶子 → float；不是数值返回 ``None``。

    ``*_opacity`` 在历史代码里有时是 ``float``、有时是 ``str``（按钮的过渡帧
    就写过 ``str(...)``），这里两种都认。
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _is_opacity_key(path: Sequence) -> bool:
    return isinstance(path[-1], str) and path[-1].endswith("_opacity")


def _classify(path: Sequence, before, after) -> Optional[str]:
    """这个叶子能不能插值？能的话返回 ``"color"`` / ``"number"``。"""
    if before == after:
        return None
    if path and _is_opacity_key(path):
        if _to_number(before) is not None and _to_number(after) is not None:
            return "number"
    start, end = _parse_color(before), _parse_color(after)
    if start and end and (start[3] is None) == (end[3] is None):
        return "color"
    return None


def _lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def _blend_color(before: str, after: str, t: float) -> str:
    start, end = _parse_color(before), _parse_color(after)
    digits = max(start[4], end[4])
    channels = [_lerp(start[i], end[i], t) for i in range(3)]
    if start[3] is not None or end[3] is not None:
        channels.append(_lerp(start[3] or 255, end[3] or 255, t))
    rounded = [max(0, min(255, int(round(channel)))) for channel in channels]
    width = 2 if digits != 1 else 1
    return "#" + "".join(f"{channel:0{width}x}" for channel in rounded)


def _blend_number(before, after, t: float):
    value = _lerp(_to_number(before), _to_number(after), t)
    if isinstance(before, str) or isinstance(after, str):
        # 保持"原来是字符串就还回字符串"
        return f"{value:.4f}".rstrip("0").rstrip(".") or "0"
    return value


def interpolatable(path: Sequence, before, after) -> bool:
    """公开的小判定：``path`` 上的这两个值之间能不能做过渡插值。

    ::

        interpolatable(("back_color",), "#ffffff", "#000000")   # True
        interpolatable(("border_width",), 1, 3)                  # False
    """
    return _classify(path, before, after) is not None


# ---------------------------------------------------------------------------
# 单个组件的插值计划
# ---------------------------------------------------------------------------
class WidgetThemePlan:
    """一个组件在这次换肤里的"起点 → 终点"。

    只保存**能插值的叶子**（颜色 / 不透明度）。其它字段（线宽、圆角、
    字体、回调）在静默应用阶段就已经落成目标值了，过渡期间不该动它们——
    把它们也插值会让边框"长出来"、圆角"变形"。
    """

    __slots__ = (
        "widget",
        "before",
        "after",
        "after_tree",
        "kinds",
        "tops",
        "_paths",
        "_templates",
        "_t",
    )

    def __init__(self, widget, before: Dict, after: Dict, after_tree: Dict):
        """
        :param before: 换肤前的**叶子表**（路径 → 值）
        :param after: 换肤后的叶子表
        :param after_tree: 换肤后的**嵌套结构**（保留 EasyDict 等原类型），
            用来生成每帧要写回去的子树、以及收尾时恢复目标值

        .. note::
           **顶层就是叶子的情况非常常见**（``FluLabel`` 只有
           ``attributes.text_color``、``FluBadge`` 只有 ``back_color``），
           所以 :meth:`values_at` 必须单独处理"路径长度为 1"的叶子——
           否则 ``path[1:]`` 是空元组，回写时会 ``IndexError``。
        """
        self.widget = widget
        self.before = before
        self.after = after
        self.after_tree = after_tree
        self.kinds: Dict[Tuple, str] = {}
        self._t = 0.0
        self._templates: Dict[Any, Any] = {}
        self._paths: Dict[Any, List[Tuple]] = {}

        for path, old in before.items():
            if path not in after:
                continue
            kind = _classify(path, old, after[path])
            if kind is not None:
                self.kinds[path] = kind

        self.tops = []
        if self.kinds:
            seen = set()
            for path in self.kinds:
                top = path[0]
                if top not in seen:
                    seen.add(top)
                    self.tops.append(top)
                self._paths.setdefault(top, []).append(path)
            for top in self.tops:
                self._templates[top] = _copy_like(after_tree[top])

    def __bool__(self) -> bool:
        return bool(self.kinds)

    def __len__(self) -> int:
        return len(self.kinds)

    @property
    def t(self) -> float:
        """最近一帧的进度（0→1），供 :func:`blend_theme_design` 读取。"""
        return self._t

    def value_at(self, path: Tuple, t: float):
        kind = self.kinds[path]
        if kind == "color":
            return _blend_color(self.before[path], self.after[path], t)
        return _blend_number(self.before[path], self.after[path], t)

    def values_at(self, t: float) -> Dict:
        """这一帧要写进 ``attributes`` 的顶层键 →（含中间色的）子树。"""
        self._t = t
        out: Dict = {}
        for top in self.tops:
            paths = self._paths[top]
            template = self._templates[top]
            if not _is_mapping(template) and not isinstance(
                template, (list, tuple)
            ):
                # 顶层本身就是叶子：直接换掉整个值
                out[top] = self.value_at(paths[0], t)
                continue
            for path in paths:
                _set_path(template, path[1:], self.value_at(path, t))
            out[top] = template
        return out

    def blend_into(self, target, t: float):
        """把 ``target``（本轮目标配色字典）里的可插值叶子换成中间色。"""
        self._t = t
        if not self.kinds:
            return target
        blended = _copy_like(target)
        for path in self.kinds:
            if not _has_path(target, path):
                continue
            try:
                _set_path(blended, path, self.value_at(path, t))
            except (KeyError, IndexError, TypeError):
                continue
        return blended

    def restore(self) -> None:
        """把 ``attributes`` 恢复成本轮的目标值（过渡收尾 / 中断时用）。

        从 ``after_tree`` 现取一份新的副本，而不是用 ``_templates``——
        后者在每一帧里都被就地改写成中间色了。
        """
        self.widget.dconfigure(
            {top: _copy_like(self.after_tree[top]) for top in self.tops}
        )


def _plan_for(widget) -> Optional[WidgetThemePlan]:
    return getattr(widget, "_theme_blend", None)


#: ``widget.__dict__`` 里没有 ``_draw`` 时的占位（区别于"值是 None"）
_MISSING = object()


def _noop_draw(*_args, **_kwargs):
    """静默应用阶段的"空重绘"。"""


def _suspend_draw(widget):
    """临时把 ``widget._draw`` 换成空操作，返回恢复用的令牌。

    为什么需要它：静默应用阶段要调各组件的 ``theme()`` 把目标配色写进
    ``attributes``，而 ``FluFrame`` / ``FluLabel`` / ``FluLiteNav`` /
    ``FluMenuBar`` 的 ``theme()`` 里顺手会 ``_draw()`` 一下。那会把**目标色**
    提前画到屏幕上：过渡还没开始，用户就先看见终态闪一下；而且这几笔重绘在
    ``tksvg`` 下就是白花的几百毫秒（反正过渡的第一帧会重画一遍）。

    之所以敢这么干：``_draw()`` 是"把当前 ``attributes`` 画出来"，纯读取；
    过渡的第一帧会立刻重新画一遍，所以不存在"少画了就一直错"的状态。
    用**实例属性**遮蔽类方法，退出时按原样恢复（包括调用方本来就有的覆盖）。
    """
    token = widget.__dict__.get("_draw", _MISSING)
    widget._draw = _noop_draw
    return token


def _resume_draw(widget, token) -> None:
    """把 :func:`_suspend_draw` 遮蔽掉的 ``_draw`` 还回去。"""
    if token is _MISSING:
        try:
            del widget.__dict__["_draw"]
        except KeyError:  # pragma: no cover
            pass
        return
    widget.__dict__["_draw"] = token


def blend_theme_design(widget, design):
    """给"每次 ``_draw()`` 都重算配色"的组件用的钩子。

    ``FluCheckBox`` / ``FluRadioBox`` / ``FluListBox`` / ``FluLiteNav`` 的
    ``_draw()`` 开头会调 ``_apply_design()``：它按当前
    ``(mode, 状态)`` 重新查一遍设计规范，于是刚写进去的中间色会被**覆盖掉**。
    在 ``_apply_design()`` 里套一层这个函数，中间色就能保住。

    没有正在进行的过渡（或这个组件不参与过渡）时原样返回。

    :param widget: 组件自己
    :param design: ``_apply_design()`` 刚算出来的目标配色
    """
    plan = _plan_for(widget)
    if plan is None:
        return design
    return plan.blend_into(design, plan.t)


# ---------------------------------------------------------------------------
# 控件树收集
# ---------------------------------------------------------------------------
def collect_themed_widgets(root) -> List:
    """广度优先收集 ``root`` 子树里所有"持有主题状态"的控件。

    * 父控件排在子控件前面（重绘顺序稳定，容器先画底、子控件后画面）；
    * 按对象身份去重（同一个控件只会被换肤一次）；
    * 跳过带 ``_theme_proxy = True`` 的**容器画布**：``FluFrameCanvas`` 的
      ``theme()`` 只是转发给它内嵌的 ``FluFrame``，主题状态并不属于画布。
      整棵树既然会被走一遍，那个 ``FluFrame`` 自己就会被收集到，
      再让画布转发一次就等于把整套配色算两遍。
    """
    from collections import deque

    found: List = []
    seen = set()
    queue = deque([root])
    while queue:
        widget = queue.popleft()
        if id(widget) in seen:
            continue
        seen.add(id(widget))

        if not getattr(widget, "_theme_proxy", False):
            if hasattr(widget, "theme") and hasattr(widget, "attributes"):
                found.append(widget)

        try:
            queue.extend(list(widget.children.values()))
        except Exception:
            continue
    return found


# ---------------------------------------------------------------------------
# 过渡本体
# ---------------------------------------------------------------------------
#: 正在进行的过渡（同一时刻只允许一个）
_active: Optional["ThemeTransition"] = None

#: "静默应用配色"阶段的深度；>0 时不允许再起一次过渡
_applying_depth = 0

#: 一次主题过渡允许占用的总时长上限（毫秒）。
#:
#: 主题过渡的每一帧都要**重画整棵树**，所以"能画几帧"完全取决于渲染引擎。
#: 默认的 ``tksvg`` 引擎下，一屏 20 来个组件重绘一次大约要 100~200ms；
#: 若硬按 ``steps=5 × step_time=20ms`` 的时间表去排，时间轴上大部分帧都会
#: 被直接跳过，用户看到的其实是"闪一下"。这里改成：先量一次真实重绘耗时，
#: 再把帧数**降**到能塞进这个预算的数量——宁可少几帧，也要每一帧都完整同步。
DEFAULT_TRANSITION_BUDGET_MS = 600.0


def set_transition_budget(milliseconds) -> None:
    """设置主题过渡的总时长上限（毫秒）；``0`` 表示不限制。"""
    environ["tkfluent.theme_transition_budget"] = str(float(milliseconds))


def get_transition_budget() -> float:
    """当前的主题过渡总时长上限（毫秒）。"""
    try:
        return float(
            environ.get(
                "tkfluent.theme_transition_budget", DEFAULT_TRANSITION_BUDGET_MS
            )
        )
    except (TypeError, ValueError):
        return DEFAULT_TRANSITION_BUDGET_MS


def active_transition() -> Optional["ThemeTransition"]:
    """当前正在跑的过渡；没有则为 ``None``。"""
    return _active


def applying_themes() -> bool:
    """是否正处在"统一过渡的静默应用"阶段。

    组件里那些**会递归**的 ``theme()``（``FluFrameCanvas`` / ``FluMenuBar`` /
    ``FluToplevel``）靠它判断"这一趟是不是别人在指挥"：是的话就只改自己的配色，
    子控件交给驱动方，免得同一棵子树被换两遍肤。
    """
    return _applying_depth > 0


class ThemeTransition:
    """一次"整棵树同步换肤"。

    :param root: 子树的根控件（通常是窗口）
    :param mode: ``"light"`` / ``"dark"``
    :param steps: 帧数；``None`` 表示读全局配置
    :param step_time: 每帧毫秒；``None`` 表示读全局配置
    :param easing: 缓动曲线名或可调用对象；``None`` 表示读全局配置
    """

    def __init__(
        self,
        root,
        mode: str,
        steps: Optional[int] = None,
        step_time: Optional[int] = None,
        easing=None,
    ):
        from .designs.animation import (
            easing_function,
            get_animation_step_time,
            get_animation_steps,
            get_theme_easing,
        )

        self.root = root
        self.mode = mode
        self.steps = int(get_animation_steps() if steps is None else steps)
        self.step_time = int(
            get_animation_step_time() if step_time is None else step_time
        )
        self.easing = easing_function(
            get_theme_easing() if easing is None else easing
        )

        #: 参与的组件 → 插值计划
        self.plans: Dict[int, WidgetThemePlan] = {}
        #: 没有可插值叶子、但必须重绘一次的组件
        self.redraw_only: List = []
        #: 换肤时抛异常的组件（(控件, 异常)），照旧不影响其它组件
        self.failures: List[Tuple[Any, BaseException]] = []

        #: 本次过渡真正跑了几帧（自适应之后的值，见 :meth:`_start`）
        self.frames_painted = 0
        #: 一次全树重绘的实测耗时（毫秒），0 表示还没量到
        self.paint_cost_ms = 0.0

        self._handle = None
        self._frame_index = -1
        self._started_at = 0.0
        self._finished = False
        self._deadline_ms = 0.0
        self._requested_steps = self.steps

    # -- 生命周期 ---------------------------------------------------------
    @property
    def animated(self) -> bool:
        """这次换肤到底要不要动画。"""
        return self.steps > 0 and self.step_time > 0

    def run(self) -> "ThemeTransition":
        """执行一次换肤：先静默落目标值，再（可选地）拉起统一过渡。

        .. note::
           **这里一帧都不画**。静默应用阶段所有组件的 ``_draw()`` 都被屏蔽了
           （见 :func:`_suspend_draw`），所以屏幕仍然停在**换肤前**的样子——
           那正好就是过渡的第 0 帧。真正第一笔重绘发生在下一拍的 ``_start`` 里，
           调用方因此能立刻拿回控制权。在默认的 ``tksvg`` 引擎上，一次全树重绘
           要几百毫秒，同步做掉就等于"点了按钮卡半秒"。
        """
        widgets = collect_themed_widgets(self.root)
        self._apply_targets(widgets)

        if not self.animated or not self.plans:
            self.finish()
            return self

        self._schedule(1, self._start)
        return self

    def _start(self) -> None:
        """第一拍：估一次全树重绘的开销，据此决定这次到底跑几帧。"""
        self._handle = None
        if not self._alive():
            self.finish(paint=False)
            return

        self.paint_cost_ms = self._probe_paint_cost()

        budget = get_transition_budget()
        # 渲染得越慢，能塞进预算的帧就越少。不是"少画几帧"，而是
        # **把总帧数降下来**——这样每一帧都是完整、同步的一帧，
        # 而不是画了一半就被时间追上。
        affordable = (
            self.steps
            if budget <= 0
            else int(budget // max(self.paint_cost_ms, self.step_time, 1))
        )
        affordable = max(0, affordable)
        if affordable < 2:
            # 连两帧都塞不进预算：动画只会变成"停顿一下再跳"，不如直接落定
            # （而且这时候一帧都还没画过，落定只需一次重绘）。
            self.steps = 0
            self.finish()
            return

        self.steps = min(self.steps, affordable)
        self._deadline_ms = self.steps * max(
            self.paint_cost_ms, self.step_time
        ) + max(500, self.paint_cost_ms * 3)

        self._started_at = perf_counter()
        self._frame_index = 0
        self._schedule(self.step_time)

    def _probe_paint_cost(self) -> float:
        """抽几个组件画一下，据此**估算**一次全树重绘要多久。

        为什么不干脆整棵树画一遍来量：那正是我们想省掉的那一次重绘。
        抽样画是安全的——屏幕本来就还停在旧配色上（静默应用阶段没画过），
        被抽到的组件画成起点色之后，和没被抽到的完全一致。
        """
        plans = list(self.plans.values())
        if not plans:
            return 0.0
        sample_size = min(3, len(plans))
        stride = max(1, len(plans) // sample_size)
        sample = plans[::stride][:sample_size]

        started = perf_counter()
        for plan in sample:
            try:
                plan.widget.dconfigure(plan.values_at(0.0))
                plan.widget._draw()
            except Exception:
                continue
        elapsed = (perf_counter() - started) * 1000.0
        return elapsed / len(sample) * len(plans)

    def _apply_targets(self, widgets) -> None:
        """静默地把目标配色写进每个组件，并算出插值计划。"""
        global _applying_depth
        from .designs.animation import suspended_widget_animation

        _applying_depth += 1
        try:
            with suspended_widget_animation():
                for widget in widgets:
                    self._apply_one(widget)
        finally:
            _applying_depth -= 1

    def _apply_one(self, widget) -> None:
        # 上一次过渡可能还挂着计划，先摘掉（否则 _draw() 会拿旧进度插值）
        self._detach(widget)
        try:
            before_tree = _copy_like(widget.attributes)
        except Exception as exc:  # pragma: no cover - 只可能来自异常的 attributes
            self.failures.append((widget, exc))
            return

        # 让 theme() 只改配色、不画。有些组件的 theme() 里顺手 _draw() 了一下
        # （FluFrame / FluLabel / FluLiteNav / FluMenuBar），那会把**目标色**
        # 提前画到屏幕上——过渡还没开始，用户就先看见终态闪一下。
        token = _suspend_draw(widget)
        try:
            widget.theme(mode=self.mode)
        except Exception as exc:
            self.failures.append((widget, exc))
            return
        finally:
            _resume_draw(widget, token)

        try:
            after_tree = _copy_like(widget.attributes)
        except Exception as exc:  # pragma: no cover
            self.failures.append((widget, exc))
            return

        before = dict(_leaves(before_tree))
        after = dict(_leaves(after_tree))
        plan = WidgetThemePlan(widget, before, after, after_tree)
        if plan:
            widget._theme_blend = plan
            self.plans[id(widget)] = plan
        else:
            # 没有可插值的叶子——留着让它在每一帧里跟着重绘，
            # 免得它成了整屏唯一"瞬间跳变"的组件。
            self.redraw_only.append(widget)

    # -- 帧循环 -----------------------------------------------------------
    def _schedule(self, delay: int, callback=None) -> None:
        try:
            self._handle = self.root.after(
                max(1, int(delay)), callback or self._tick
            )
        except Exception:
            self._handle = None
            self.finish()

    def _alive(self) -> bool:
        if self._finished:
            return False
        try:
            return bool(self.root.winfo_exists())
        except Exception:
            return False

    def _tick(self) -> None:
        """画下一帧。

        节奏是**顺序推进**的：上一帧实际画了多久，这一帧就少等多久
        （``step_time - 上一帧耗时``）。因此渲染慢的时候动画会自然变慢，
        而不是"按时间跳过大部分帧、只剩头尾两下"。
        帧数已经在 :meth:`_start` 里按**抽样估算**的开销裁过；这里再拿**实测**
        开销复核一次——抽样难免估偏，实测一帧之后立刻把剩余帧数收到位，
        所以最多只多花一帧的代价。
        """
        self._handle = None
        if not self._alive():
            self.finish(paint=False)
            return

        elapsed_ms = (perf_counter() - self._started_at) * 1000.0
        if elapsed_ms > self._deadline_ms:
            self.finish()
            return

        index = self._frame_index + 1
        if index >= self.steps:
            self.finish()
            return

        self._frame_index = index
        cost = self._paint(self.easing(index / self.steps))
        self.frames_painted += 1
        self.paint_cost_ms = max(self.paint_cost_ms, cost)
        self._trim_to_budget(index, cost, elapsed_ms)
        self._schedule(int(self.step_time - cost))

    def _trim_to_budget(self, index: int, cost: float, elapsed_ms: float) -> None:
        """按实测开销收紧剩余帧数（预算已经花掉的部分不再补）。"""
        budget = get_transition_budget()
        if budget <= 0:
            return
        remaining = budget - elapsed_ms
        affordable = int(remaining // max(cost, self.step_time, 1))
        if index + affordable < self.steps:
            self.steps = max(index + 1, index + affordable)
        self._deadline_ms = max(
            budget, self.steps * max(cost, self.step_time)
        ) + max(500.0, cost * 3)

    def _paint(self, t: float) -> float:
        """把所有组件画到**同一个**进度 ``t`` 上，返回耗时（毫秒）。

        一次回调画完整棵树是刻意的：这样任意时刻屏幕上所有控件都处于
        同一个 ``t``，不会出现"这一半已经变了、那一半还没变"的撕裂。
        """
        started = perf_counter()
        # 先把进度写进所有计划，再统一重绘：这样"重算配色"的组件
        # （见 blend_theme_design）在 _draw() 里读到的也是同一帧的 t。
        payloads = []
        for plan in list(self.plans.values()):
            try:
                payloads.append((plan, plan.values_at(t)))
            except Exception:
                payloads.append((plan, None))

        for plan, values in payloads:
            widget = plan.widget
            try:
                if values:
                    widget.dconfigure(values)
                widget._draw()
            except Exception:
                continue

        for widget in self.redraw_only:
            try:
                widget._draw()
            except Exception:
                continue
        return (perf_counter() - started) * 1000.0

    # -- 收尾 -------------------------------------------------------------
    def _detach(self, widget) -> None:
        if getattr(widget, "_theme_blend", None) is not None:
            try:
                del widget._theme_blend
            except AttributeError:  # pragma: no cover
                widget._theme_blend = None

    def finish(self, paint: bool = True) -> None:
        """落到目标配色并收尾（可重复调用）。

        .. note::
           收尾**只重绘一次**：先把各组件的确切目标值写回 ``attributes``
           （插值出来的最后一帧可能还差一点点浮点），再统一画一遍。
           旧写法是先 ``_paint(1.0)`` 再来一轮 ``restore() + _draw()``，
           等于白画一整棵树——在 ``tksvg`` 下就是白等几百毫秒。
        """
        global _active
        if self._finished:
            return
        self._finished = True

        self._stop_timer()

        for plan in self.plans.values():
            self._detach(plan.widget)
            if not paint:
                continue
            try:
                plan.restore()
            except Exception:
                continue

        if paint:
            self._redraw()

        if _active is self:
            _active = None

    def _redraw(self) -> None:
        """按目标配色把参与的组件统一重绘一遍（不做插值）。"""
        for plan in list(self.plans.values()):
            try:
                plan.widget._draw()
            except Exception:
                continue
        for widget in self.redraw_only:
            try:
                widget._draw()
            except Exception:
                continue

    # -- 诊断 -------------------------------------------------------------
    @property
    def finished(self) -> bool:
        """过渡是否已经收尾（帧跑完 / 被取消 / 直接落定都算）。"""
        return self._finished

    @property
    def requested_steps(self) -> int:
        """调用方**要求**的帧数（可能因为渲染太慢被 :meth:`_start` 调低）。"""
        return self._requested_steps

    def describe(self) -> Dict[str, Any]:
        """一句话说明这次过渡实际发生了什么（日志 / 基准脚本用）。"""
        return {
            "mode": self.mode,
            "widgets": len(self.plans) + len(self.redraw_only),
            "animated": len(self.plans),
            "requested_steps": self._requested_steps,
            "steps": self.steps,
            "step_time": self.step_time,
            "frames_painted": self.frames_painted,
            "paint_cost_ms": round(self.paint_cost_ms, 2),
            "failures": [
                f"{type(widget).__name__}: {error!r}"
                for widget, error in self.failures
            ],
        }

    def _stop_timer(self) -> None:
        if self._handle is None:
            return
        try:
            self.root.after_cancel(self._handle)
        except Exception:
            pass
        self._handle = None

    def cancel(self, restore: bool = True) -> None:
        """中断这次过渡。

        :param restore: ``True``（默认）把控件落回本次的**目标**配色；
            ``False`` 保留当前中间色——紧接着要起一次新过渡时用这个，
            新过渡会以当前中间色为起点，画面是连续的。
        """
        global _active
        if self._finished:
            return
        self._finished = True
        self._stop_timer()

        for plan in self.plans.values():
            self._detach(plan.widget)
            if not restore:
                continue
            try:
                plan.restore()
                plan.widget._draw()
            except Exception:
                continue

        if _active is self:
            _active = None


def run_theme_transition(
    root,
    mode: str,
    steps: Optional[int] = None,
    step_time: Optional[int] = None,
    easing=None,
) -> ThemeTransition:
    """把 ``root`` 子树整体换到 ``mode``，所有控件共用一条时间轴。

    :param root: 子树根控件
    :param mode: ``"light"`` / ``"dark"``
    :param steps: 帧数；``None`` 读全局配置（:func:`tkflu.set_animation_steps`）
    :param step_time: 每帧毫秒；``None`` 读全局配置
    :param easing: 缓动曲线名；``None`` 读全局配置（默认 ``ease_in_out``）
    :returns: 这次过渡（动画关闭时返回的是已经收尾的实例）

    .. note::
       同一时刻只保留一个过渡：新的会把旧的**就地**接管（保留中间色作为新起点），
       所以用户连点"切换主题"不会叠加出越跑越慢的帧队列。
       处于静默应用阶段的嵌套调用会被忽略——那种调用来自组件自己的 ``theme()``。
    """
    global _active
    if _applying_depth:
        # 来自组件内部 theme() 的嵌套调用（如 FluMenuBar.theme → 子控件）。
        # 它自己已经只改配色了，不该在这里再起一条时间轴。
        return _active if _active is not None else ThemeTransition(root, mode)

    previous = _active
    if previous is not None:
        # 旧过渡的窗口可能已经被销毁了（控件销毁时会取消它排的 after，
        # 但模块级的 _active 还指着它）。那种情况下它已经没有画面要收拾，
        # 直接丢掉引用，别拖着一串死控件。
        if previous._alive():
            previous.cancel(restore=False)
        else:
            previous._finished = True

    transition = ThemeTransition(
        root, mode, steps=steps, step_time=step_time, easing=easing
    )
    _active = transition
    transition.run()
    return transition
