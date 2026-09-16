# 渲染引擎与性能

`tkfluent` 的绘制后端是可切换的，底层由
[`tkdeft.engines`](https://pypi.org/project/tkdeft) 提供。

## 可选的渲染器

| 编号 | 引擎 | 类型 | 额外依赖 |
| --- | --- | --- | --- |
| `0` | `tksvg` | SVG，**默认，行为与旧版完全一致** | 无 |
| `1` | `wand` | SVG → PNG | `Wand` |
| `2` | `skia` | 进程内栅格，速度与画质最好 | `pip install tkfluent[skia]` |
| `3` | `pillow` | 进程内栅格，**永远可用** | 无 |
| `4` | `cairo` | 进程内栅格 | `pip install tkfluent[cairo]` |

## 切换

```python
from tkflu.designs.renderer import set_renderer, list_renderers

print(list_renderers())
# [(0, 'tksvg', True), (1, 'wand', True), (2, 'skia', True), (3, 'pillow', True), (4, 'cairo', True)]

set_renderer(2)        # 按编号（旧写法，0/1 语义不变）
set_renderer("skia")   # 也接受引擎名
```

也可以面向对象地使用：

```python
from tkflu import FluRenderer

r = FluRenderer()
r.renderer(2)          # 设置
r.renderer()           # 读取当前编号
```

!!! warning "引擎不可用时会报错"
    `set_renderer(2)` 在没装 `skia-python` 时会抛 `ValueError`。
    这是有意为之——静默退回就会让你以为性能已经改善，实际还在走慢路径。

## 查询引擎信息

`tkflu.designs.renderer` 是 [`tkdeft.engines`](https://pypi.org/project/tkdeft)
的适配层，除了切换引擎，还把 tkdeft 的查询接口原样转了出来：

```python
from tkflu.designs.renderer import (
    describe_engines, engine_index, get_engine_name,
    list_engines, list_renderers, renderer_description,
)

list_renderers()
# [(0, 'tksvg', True), (1, 'wand', True), (2, 'skia', True), (3, 'pillow', True), (4, 'cairo', True)]

get_engine_name()                  # -> "skia"
engine_index("skia")               # -> 2
renderer_description("skia")       # -> "skia-python 进程内栅格化（无磁盘 I/O，抗锯齿质量高）"

for row in describe_engines():     # 编号 / 类型 / 依赖 / 是否可用 / 是否当前
    print(row)
```

这些名字同时也从**包根**转出了一份，所以 `tkflu.get_renderer_name()`、
`tkflu.list_renderers()` 一样能用（`set_renderer` / `get_renderer` 本来就在包根）。

命令行里也能看到同一份信息：

```bash
python -m tkflu --list-engines
```

## 组件是怎么落到引擎上的

组件本身**不关心**当前是哪个引擎。`FluButtonCanvas` 之类的画布类把绘制
交给 `tkdeft` 的统一入口
[`DCanvas.draw_roundrect()`](https://pypi.org/project/tkdeft)：

```python
# tkflu/button.py（节选）——组件层只留一行
self.element_border = self.create_round_rectangle(
    0, 0, width, height, _radius,
    temppath=self.temppath, temppath2=self.temppath3,
    fill=_back_color, outline=_border_color, width=_border_width,
)
```

`create_round_rectangle` / `create_track` / `create_thumb` 最终都调用
`tkdeft.windows.canvas.DCanvas.draw_*`：当前引擎是栅格引擎时走**进程内位图
快速路径**（不生成 SVG、不落盘，相同规格还会命中缓存），否则自动回退到
SVG 实现（`draw_roundrect_svg` 等钩子）。

所以：

* 想把某个组件强制渲染成 SVG（做对照），把它的画布 `raster_enabled` 置 `False` 即可；
* 想给某类图元换一套 SVG 实现，覆盖 `draw_roundrect_svg` / `draw_track_svg` /
  `draw_thumb_svg` 即可，不需要再写"先试快速路径、失败再回退"的样板代码。

## 为什么默认还是 tksvg？

栅格引擎（skia / pillow / cairo）与 tksvg 在抗锯齿细节上存在亚像素级差异。
为了让已有项目升级后界面**一个像素都不变**，默认仍然是 `tksvg`。
想要性能就显式切到 `2` 或 `3`。

引擎层已经做过保真度比对：在 24 个按钮状态（浅色/深色 × 标准/强调/菜单 ×
常态/悬停/按下/禁用）下，各栅格引擎与 `tksvg` 的平均像素差都 ≤ 5.7/255，
绝大多数状态低于 2。

## 实测提升

| 场景 | `0` tksvg（默认） | `2` skia | 提升 |
| --- | --- | --- | --- |
| 按钮重绘 | 5.95 ms | 0.15 ms | **39×** |
| 按钮 hover 往返 | 13.65 ms | 0.26 ms | **52×** |
| 20 个按钮批量重绘 | 139.9 ms | 2.93 ms | **48×** |
| 圆角矩形（参数相同，命中缓存） | 10.80 ms | 0.02 ms | **480×** |
| 圆角矩形（尺寸各不相同） | 13.81 ms | 1.26 ms | **11×** |

即使不切换渲染器，`0.2.0` 对 `tkdeft` 基础设施的修复（临时文件与 fd 泄漏、
图片被 GC 导致画面空白、无效的重复重绘）本身也能带来约 **2–3×** 的改善。

## 缓存与内存

渲染结果按"引擎 + 图元类型 + 绘制规格"缓存，**同尺寸同配色的一组控件共用同一张
`PhotoImage`**。缓存不做 LRU 淘汰，而是按像素预算（默认 8M 像素）控制上限——
因为 `PhotoImage` 一旦被回收，引用它的画布元素会变成空白。

```python
from tkdeft.engines import cache_stats, set_cache_budget

print(cache_stats())
# {'entries': 62, 'pixels': 169244, 'budget': 8000000,
#  'hits': 178, 'misses': 99, 'hit_rate': 0.642, 'overflow': 0}

set_cache_budget(16_000_000)   # 界面很复杂时可以调大
```

## 基准与回归

`tkdeft` 仓库里的 `benchmarks/` 提供了一键回归：

```bash
python benchmarks/run_all.py
```

包含：引擎自检（通道序 / alpha / 四边描边）、与 tksvg 的保真度比对、
设计稿画廊、全组件冒烟、性能基准。
