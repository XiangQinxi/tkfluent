# 常见问题与排查

这一页收集的是 **tkfluent 里真实踩过的坑**——大部分来自 Tkinter 本身的语义，
或者"组件默认行为与直觉不一致"，而不是库的 bug（标注了 🐞 的除外，那是真缺陷，
已经在新版本修掉）。

每条都按 **症状 / 原因 / 怎么办** 写，代码片段可以直接抄。

## 先做这三步

```python
import tkflu

print(tkflu.__version__)          # 至少 0.5.0（这一版重写了主题切换）
```

```bash
python -m tkflu --list-engines    # 当前有哪些渲染引擎可用
python -m tkflu --check           # 无界面自检，退出码 0 表示一切正常
```

如果 `--check` 通过、但你的程序有问题，大概率是本页里的某一类"用法/语义"问题；
如果 `--check` 就失败，先升级依赖：

```bash
pip install -U tkdeft tkfluent
```

> 相关页面：[主题与配色](theme.md)、[组件总览](components.md)、
> [运行演示](run-demo.md)、[架构说明](architecture.md)。

---

## 一、主题与配色

### 1. 改了主色调，界面没变

**症状**：调用 `tkflu.purple_primary_color()`（或 `set_primary_color(...)`）之后，
窗口里已经画好的强调色按钮、开关**颜色纹丝不动**。

**原因**：主色调是**读取时取值**——组件的配色字典在构造/换主题时从全局取一次色，
之后就一直用它自己的字典。改全局值不会回头去改已经建好的组件。

**怎么办**：改完之后让受影响的组件**重新取色并重绘**。

```python
import tkflu

root = tkflu.FluWindow()
button = tkflu.FluButton(root, text="强调色", style="accent")
button.pack(padx=16, pady=16)

tkflu.purple_primary_color()                  # 只改了"全局取值"
button.theme(mode="light", style="accent")    # ← 重新取色
button._draw()                                # ← 重绘一次（保险起见）
```

!!! tip "最省事的做法"
    在主色调改动很少的前提下，直接把 `set_primary_color(...)` 放在**创建组件之前**，
    就不用逐个重绘了。详见 [主题与配色](theme.md)。

### 2. 🐞 点"切换主题"报 `AttributeError: 'NoneType' object has no attribute 'lower'`

**症状**：点一键换肤的按钮，控制台抛：

```text
AttributeError: 'NoneType' object has no attribute 'lower'
```

栈顶通常落在某个组件的 `theme()` 上。

**原因**：`FluThemeManager` 一键换肤时**只传 `mode`**，`style` 参数是 `None`。
如果组件的 `theme()` 拿**参数** `style` 去判断分支，就会在 `None` 上取 `.lower()`。
这正是 `FluListBox.theme()` 在 0.3.0 之前的样子（`FluListBox` 是唯一这么写的组件，
所以只有它会崩）。

**怎么办**：升级到 **0.3.0** 即可：

```bash
pip install -U tkfluent
```

自己写组件（或照着模板改）时，判断分支要用**构造时存下来的** `self.style`，
并且兜底：

```python
# ✗ 用参数判断：一键换肤时 style 是 None
def theme(self, mode="light", style=None):
    if style.lower() == "accent":        # AttributeError: 'NoneType' ...
        ...

# ✓ 用 self.style，并给一个兜底值
def theme(self, mode="light", style=None):
    if mode:
        self.mode = mode
    if style:
        self.style = style
    style = getattr(self, "style", None) or "standard"   # ← 关键
    if style.lower() == "accent":
        ...
```

### 3. 组件不跟着窗口换主题

**症状**：`tkflu.FluWindow(mode="dark")` 之后，窗口变了，里面的按钮、标签还是浅色。

**原因**：`FluWindow(mode=...)` **只管窗口自己**，不会递归改子组件；
`FluToplevel` 同理。

**怎么办**：用 `FluThemeManager` 做批量切换。它会走完窗口的**整棵控件树**
（自动去重），把每个持有配色的组件都切到目标模式——组件挂多深都不影响，
嵌套面板、菜单栏里的菜单项、列表 / 导航栏都会被覆盖到。

```python
import tkflu

root = tkflu.FluWindow(mode="light")
thememanager = tkflu.FluThemeManager(window=root, mode="light")

tkflu.FluButton(root, text="切换主题", command=thememanager.toggle).pack(pady=8)

root.mainloop()
```

配合开关组件也行：

```python
toggle = tkflu.FluToggleButton(root, text="深色模式")
toggle.dconfigure(command=lambda: tkflu.toggle_theme(toggle, thememanager))
```

!!! tip "自己写的容器不用做任何事"
    只要组件是用 `master=` 正常挂进去的，换肤就会走到它。
    不需要实现 `update_children()` 之类的向下传播
    （这个约定在 0.5.0 之前存在，现在已由统一过渡接管）。

### 4. 过渡动画没效果，或者很卡

**症状**：切换主题时颜色是"啪"地跳变，没有渐变；或者反过来——动画开着，
低配机器上明显卡顿。

**原因**：过渡动画由两个全局参数控制，**库默认都是 `0`（等于关闭）**：

```python
from tkflu import set_animation_steps, set_animation_step_time

set_animation_steps(5)        # 过渡帧数
set_animation_step_time(20)   # 每帧间隔（毫秒）
```

**怎么办**：想要动画就显式打开。

```python
from tkflu import set_animation_steps, set_animation_step_time

set_animation_steps(5)
set_animation_step_time(20)

# 录屏 / 做基准测试时彻底关掉
set_animation_steps(0)
set_animation_step_time(0)
```

!!! note "命令行画廊的默认值不一样"
    `python -m tkflu`（组件画廊）为了让效果明显，**默认给的是 5 帧 / 20ms**；
    命令行也提供 `--animation-steps` / `--animation-step-time` / `--no-animation`。
    库本身的默认值仍是 0。详见 [运行演示](run-demo.md)。

!!! warning "帧数不等于会画几帧"
    每一帧都要重绘**整棵树**，所以实际画几帧取决于渲染引擎有多快：

    | 引擎 | 一次全树重绘（约 20 个组件） |
    | --- | --- |
    | `tksvg`（默认） | 100 ~ 200 ms |
    | `pillow` | 50 ~ 100 ms |
    | `skia` | 10 ~ 30 ms |

    库会先量一次开销，再把帧数降到**预算**（默认 600ms）以内——
    所以在 `tksvg` 上即使设了 5 帧，实际也可能只画出 2 帧。
    这是刻意的：宁可少几帧，也要每一帧都完整、同步，更不能把窗口冻住。

    **想要丝滑就换引擎**（比加帧数有效得多）：

    ```python
    import tkflu

    tkflu.set_renderer("skia")     # 或 "pillow"
    ```

    想看这次到底画了几帧：

    ```python
    transition = thememanager.mode("dark")
    transition.describe()
    # {'mode': 'dark', 'widgets': 59, 'requested_steps': 5, 'steps': 3,
    #  'frames_painted': 2, 'paint_cost_ms': 316.83, 'failures': []}
    ```

### 4'. 换肤"一个一个变色" / 点完按钮卡住

**症状**：点"切换主题"之后，组件从左到右挨个变色；或者界面先卡住一两秒，
然后"啪"地一下变成新主题，中间什么都看不到。

**原因**：0.4.0 及更早的实现是这么写的：

```python
for widget in window.winfo_children():
    widget.theme(mode=mode)   # 每个组件内部各排各的过渡帧
    widget._draw()
    widget.update()           # ← 这一句把事件循环跑了起来
```

`update()` 会处理**全部**待办事件（包括用户输入、重绘、定时器），于是：

1. **阻塞**——组件越多这一趟越久。实测 59 个组件的画廊里单次
   `mode()` 要 **2.3 ~ 3.3 秒**，这期间窗口完全点不动；
2. **不同步**——每个组件各排各的 `after`，起点是"轮到它自己"那一刻；
   而前面组件的 `update()` 又会把后面组件的帧提前执行掉，于是"一个一个变色"；
3. **动画被吃掉**——真正跑完的帧全在那次 `mode()` 里消耗掉了，
   用户看到的不是过渡，而是"卡两秒然后瞬间变色"。

**现在**（0.5.0 起）：`FluThemeManager.mode()` 把整棵树交给一条统一时间轴
（详见 [主题与配色 · 过渡动画](theme.md#transition-animation)）。同样的 59 个组件：

| | 0.4.0 | 0.5.0 |
| --- | --- | --- |
| `mode()` 阻塞（`skia`） | 2787 ms | **12 ms** |
| `mode()` 阻塞（`tksvg`） | 3282 ms | **30 ms** |
| 各组件"第一次变色"的时刻差 | 150 ms 以上 | **0 ms**（同一帧） |
| 过渡中间色 | 0 帧（瞬间跳变） | 2 ~ 4 帧 |

**要不要改自己的代码**：不需要。`thememanager.mode()` / `toggle()` /
`tkflu.toggle_theme()` 的用法一个都没变。

!!! note "`mode()` 不再在返回前画完"
    它只把目标配色静默写进各组件的 `attributes`，重绘交给事件循环。
    所以**紧接着 `mode()` 读 `attributes` 已经是新主题的值，但画面还没变**；
    要等约 `steps × step_time` 才会全部落定。测试里同步等结果的话：

    ```python
    transition = thememanager.mode("dark")
    while not transition.finished:
        root.update()
    ```

---

## 二、布局与尺寸

### 5. `FluLabel` 的文字被左右裁掉

**症状**：标签里的文字两端被切掉，或者改完文字后显示的还是旧的。

**原因**：`FluLabel` 是一块**固定尺寸的画布**，文本居中绘制；文本比画布宽就会被裁。
而 `width` 不传时的"自适应"是**只增不减**的（避免文字变短时抖动），
所以动态改文字后需要重新量一次宽度。

**怎么办**：不传 `width` 让它自适应；需要固定宽度时才显式传。改完文字后调一次 `_draw()`。

```python
import tkflu

root = tkflu.FluWindow()

# 自适应：文字多长，标签就多宽（不会裁）
label = tkflu.FluLabel(root, text="FluLabel（悬停看提示）")
label.pack(padx=10, pady=6)

# 显式宽度：行为与旧版一致，超出仍然会被裁
tkflu.FluLabel(root, text="固定 120px", width=120).pack(padx=10, pady=6)

# 动态改文字：改完必须重绘一次，让它重新量宽
label.dconfigure(text="一段更长的中文标题")
label._draw()
```

更多组件用法见 [组件总览](components.md)。

### 6. 中文菜单项挤成一团 / 菜单弹窗被截断

**症状**：菜单栏里 `"文件"` `"编辑"` 挤在一起；或者下拉菜单弹出来时，
右边文字被切掉。

**原因**：用字符个数估宽度对中文是**严重偏窄**的——CJK 是宽字符，
`"文件"` 按 `len(text) * 8` 只算出 **16px**。

```python
# ✗ 不要这样估宽度
width = len("文件") * 8          # 16px，实际需要 ~32px
```

**怎么办**：交给真实字体度量。tkfluent 内部就是这么做的
（`tkflu/defs.py` 的 `measure_label_width`，优先向 Tk 要字体度量，
CJK 兜底按宽字符 ×2）。

```python
from tkflu.defs import measure_label_width

width = measure_label_width(self, "文件")      # 真实像素宽度
```

!!! tip "用现成的菜单组件就不会遇到"
    `FluMenuBar` / `FluMenu` 已经用实测宽度排版，下拉菜单也会按最长项
    调 `preferred_size()`。只有你自己拼菜单宽度时才需要关心这件事。

---

## 三、组件能力边界

### 7. 条目删除为什么叫 `delete_item` 而不是 `delete`？

**症状**：想清空列表，写 `box.delete(0)` 或 `box.delete("all")`，
结果要么删的是**画布元素**，要么直接 `RecursionError`（0.4.0 之前的实现里）。

**原因**：`FluListBox` 自己就是一个 `tkinter.Canvas`，而 `Canvas.delete`
是"删除画布元素"的意思——重绘的第一步就是 `self.delete("all")`。
两者一旦同名，重绘就会递归调用自己。

**怎么办**：

```python
box.delete_item(0)      # 删第 0 条
box.delete_item("all")  # 全部删掉（等价于 box.clear()）
box.clear()             # 推荐写法
```

同样的道理，`FluListBox` 的 `insert()` 也和 `Canvas.insert` 同名——
在本控件上请把它当作"插入条目"来用。

### 7'. `FluListBox` 0.4.0 之后变了什么？

**症状**：升级到 0.4.0 后，`FluListBox(parent, text="标题", width=120)`
看起来还是老样子，但一旦传了 `items=` 就变成一个 160px 高的列表。

**原因**：0.3.0 之前它是**占位实现**——一个"长得像按钮的圆角矩形"，
没有条目、不能选、不能滚。0.4.0 补成了真列表。

**怎么办**：

* 只传 `text=`（老写法）：列表为空，`text` 作为**空状态提示**居中显示，
  高度保持历史的 32px。老代码看起来一模一样。
* 传 `items=`（新写法）：高度默认 160px，按 `selectmode` 支持
  单选 / 多选 / `Ctrl`+`Shift` 扩展选择。
* 老代码里如果依赖"点一下就触发 `command`"，注意现在的语义是：
  **单击 = 选中，双击 / `Enter` = 激活（触发 `command`）**。
  想监听"选中变化"请用 `on_select`。

```python
box = tkflu.FluListBox(
    root, items=[f"第 {i} 行" for i in range(1, 21)],
    command=lambda index, item: print("激活", index, item),
    on_select=lambda indices, items: print("选中", indices),
)
```

!!! tip "回调签名是"宽容"的"

    `command` / `on_select` 会尽量以 `(index, item)` / `(indices, items)` 调用，
    但你只写 `lambda: ...` 也照样能用——参数个数是按签名裁的。
    （见 `tkflu.defs.call_command`。）

---

## 四、资源与生命周期

### 8. 内嵌的原生 `Entry` / `Text` 挂错窗口、销毁后不回收

**症状**：`FluEntry` / `FluText` 里的输入框跑到**别的窗口**上去了；
或者开多个 `FluToplevel` 时控件嵌不进去；控件销毁后输入框还留着。

**原因**：创建原生控件时不传 `master`，Tkinter 会把它挂到**默认根窗口**
（`tkinter._default_root`），而不是你正在构造的那个控件。
这是 tkdeft 侧的缺陷，**0.3.0 已修**（`FluEntry` / `FluText` 现在显式传 `master=self`）。

**怎么办**：升级依赖；自己写组件时务必显式传 `master`。

```bash
pip install -U tkdeft tkfluent
```

```python
from tkinter import Entry

# 自定义组件里创建原生控件：master=self
self.entry = Entry(self)          # ✓ 挂到自身，随自身一起销毁
# self.entry = Entry()            # ✗ 挂到默认根窗口
```

!!! tip "图片也有同样的问题"
    `PhotoImage` 同样绑定在具体的 Tk 解释器上。`FluImage` 传路径时会用
    `master=self` 创建图片，你手写 `create_image` 时也要照做。

!!! note "想操作内嵌的原生控件，直接拿它的属性"
    `FluEntry` / `FluText` **没有**把原生控件的方法全部代理出来，需要哪就用它的属性：

    ```python
    entry = tkflu.FluEntry(root, width=240)
    entry.entry.insert(0, "初始文本")        # 原生 tkinter.Entry 在 .entry 上
    print(entry.entry.get())

    text = tkflu.FluText(root, width=240, height=100)
    text.text.insert("1.0", "第一行")         # 原生 tkinter.Text 在 .text 上
    print(text.text.get("1.0", "end").strip())
    ```

    这些内嵌控件是在 `super().__init__()` **之后**才创建并嵌入画布的
    （那时 `self` 才是一个可用的画布，能当作 `master`）。父类构造期间的首次
    `_draw()` 会因为它们还是 `None` 而跳过，构造完成后再访问即可。

### 9. 关窗时刷 `invalid command name ...` / `can't delete Tcl command`

**症状**：关闭窗口后控制台刷一堆：

```text
invalid command name "140234567890123<lambda>"
    while executing
"140234567890123<lambda>"
    ("after" script)
```

严重时 `root.destroy()` **根本没销毁窗口**，`tkinter._default_root` 残留，
之后再建窗口就撞 `bad window path name`。

**原因**：`after` 回调注册在 **Tcl 解释器**上，而命令名记在**发起控件**的
`_tclCommands` 里；控件销毁**不会**自动取消已排队的回调。
更坑的是——**不能直接对 root 调 `after_cancel()`**：`root.after_cancel(id)`
会删掉那条 Tcl 命令，但记录它的却是发起控件（root 的列表里没有它，
`remove` 静默失败）；等那个控件自己被销毁时，`Misc.destroy` 会拿着这条
已经删掉的命令再删一次 → `TclError: can't delete Tcl command` → 异常一路冒到
`root.destroy()`。

**怎么办**：**谁注册，谁取消**。tkfluent 自己在 `FluWindow` / `FluToplevel`
销毁前统一回收（`tkflu/_after.py`）：

```python
from tkflu._after import cancel_all_after, pending_after_count

print(pending_after_count(root))   # 还有多少待执行回调（便于诊断）
cancel_all_after(root)             # 取消该解释器上所有待执行回调
```

你自己写组件时用 `after`，就在自己的 `<Destroy>` 里取消它：

```python
class MyWidget(tkflu.FluButton):          # 示例：继承任意 Flu 组件
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._after_id = None
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._after_id = self.after(20, self._tick)

    def _tick(self):
        self._after_id = None
        if self.winfo_exists():
            self._draw()

    def _on_destroy(self, event=None):
        # 子控件的 <Destroy> 会冒泡到父控件，必须判断是不是自己
        if event is not None and event.widget is not self:
            return
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)    # self 就是注册者，正确
            except Exception:
                pass
            self._after_id = None
```

!!! danger "两个容易忽略的点"
    1. `event.widget is not self` 这个判断必须写——否则父控件会替子控件
       取消回调，把还在用的回调也干掉；
    2. 别图省事写成 `root.after_cancel(...)`，它"看起来能跑"，
       代价要到控件销毁时才结算，症状出现在**关窗**那一刻，很难联想到元凶。

---

## 五、显示与自定义绘制

### 10. 图片不显示 / 过一会儿变成空白

**症状**：`FluImage` 里图片是空的，或者显示一会儿之后变成一块空白；
同一画布上多张图片时，只有最后一张能活下来。

**原因**：Tkinter 的画布元素**不会**替 Python 侧持有 `PhotoImage` 引用。
图片对象一旦被垃圾回收，对应的画布元素就变成空白——这是 Tkinter 的经典陷阱。
自己用 `PIL.ImageTk.PhotoImage` 建图片、只塞进局部变量时最容易踩。

**怎么办**：交给组件、或者自己保住引用。

```python
import tkflu

root = tkflu.FluWindow()

# ✓ 最省心：直接传路径，FluImage 自己建图并在内部保活
tkflu.FluImage(root, image="logo.png").pack(padx=16, pady=16)

# ✓ 传 PhotoImage 时，引用要挂在"还活着的对象"上
from PIL import Image, ImageTk

photo = ImageTk.PhotoImage(Image.open("logo.png"), master=root)
image_widget = tkflu.FluImage(root, image=photo)
image_widget.pack(padx=16, pady=16)

image_widget.source_photo = photo   # 关键：别让它只是一个会消失的局部变量

root.mainloop()
```

!!! note "组件内部怎么保活的"
    `FluImage` 把图片存在 `self._image_ref`，并把画布 item 交给
    `canvas._keep_photo(item, photo)` 按 id 记账。所以你传**路径**时完全不用管；
    传 `PhotoImage` 时，组件保活的是**它自己那份引用**——
    前提是这个对象本身还活着（别让 `photo` 只存在于一个临时函数里）。

### 11. `FluFrame` 上叠加自己的画布元素，一重绘就被擦掉

**症状**：往 `FluFrame`（或 `FluImage`）的画布上 `create_text` / `create_image`，
当时能看到，组件下一次重绘就消失了。

**原因**：`FluFrame._draw()` 的开头会 `self.canvas.delete("all")`——
**画布上的所有元素**（包括你后来加的那些）都会被清掉。

**怎么办**：想叠加东西，就**覆盖 `_draw`**：先让基类画背景，再画自己的元素。

```python
import tkflu


class MyOverlay(tkflu.FluFrame):
    def _draw(self, event=None, tempcolor=None):
        super()._draw(event, tempcolor)        # 基类会 delete("all") 并画圆角背景
        # 自己的元素画在基类之后，这样每次重绘都会重新加上
        self.canvas.create_text(
            12, 12, anchor="nw", text="叠加的文字", fill="#1b1b1b"
        )


root = tkflu.FluWindow()
MyOverlay(root, width=240, height=120).pack(padx=16, pady=16)
root.mainloop()
```

`FluImage` 就是仓库里的标准例子：它覆盖 `_draw`，在父类画完背景后调自己的
`_draw_image()`。**不要在 `FluFrame` 上直接 `create_image` 叠加内容。**

---

## 六、渲染引擎

### 12. 引擎相关报错：装不上 / 切不了 / 不知道有没有生效

**症状**：`tkflu.set_renderer("skia")` 抛 `ValueError`，提示缺少依赖；
或者不确定自己到底跑在哪个引擎上。

**原因**：引擎不可用时 tkfluent **故意报错**，而不是静默退回慢路径——
否则你会以为性能已经改善，实际还在走磁盘。所以缺依赖就是一个显式的 `ValueError`。

**怎么办**：

```bash
# 1) 装上可选引擎（skia 最快，pillow 零额外依赖、永远可用）
pip install "tkfluent[skia]"
pip install "tkfluent[cairo]"

# 2) 看当前环境里哪些引擎可用
python -m tkflu --list-engines

# 3) 无界面自检（指定引擎）
python -m tkflu --check -r skia
```

```python
import tkflu

tkflu.set_renderer("skia")        # 或 tkflu.set_renderer(2)

# 想确认"现在到底跑在哪个引擎上"，用 renderer 适配层里的查询函数
from tkflu.designs.renderer import get_renderer_name, list_renderers

print(get_renderer_name())        # -> "skia"
print(list_renderers())           # [(0, 'tksvg', True), (1, 'wand', True), (2, 'skia', True), ...]
```

自动化挑选最快的可用引擎：

```bash
python -m tkflu -r auto
```

!!! tip "报错信息里会写清楚缺什么"
    例如 `ValueError: 绘制引擎 'skia' 不可用，缺少依赖：('skia', 'numpy', 'PIL')`。
    绝大多数情况是把包装进了**另一个** Python 解释器，用
    `python -c "import sys; print(sys.executable)"` 确认一下再
    `python -m pip install "tkfluent[skia]"`。

    引擎与编号的完整说明见 [运行演示](run-demo.md)。

---

## 七、无桌面 / CI 环境

### 13. 在没有显示器的机器上跑（CI、容器、远程）

**症状**：CI 里跑界面相关代码直接失败；或者写布局断言时怎么量都是 `1`。

**原因**：两件事——

1. 起真窗口需要可用的显示/桌面会话；
2. 窗口**未映射**时 Tk 不做几何计算，`winfo_width()` / `winfo_height()`
   一律返回 `1`（`withdraw()` 状态下尤其明显）。

**怎么办**：无界面环境用自检入口，它**不需要显示器**：

```bash
python -m tkflu --check                 # 退出码 0 = 通过
python -m tkflu --check -r skia         # 指定引擎
```

`--check` 会真实建出每个组件，并对它们依次跑重绘、浅色/深色主题、
鼠标进入/离开、按下/抬起、尺寸变化等钩子，最后打印缓存统计。

写自己的布局检查时，套用同一条原则：**没有可用的桌面会话就跳过，而不是失败**。

```python
import tkinter

root = tkinter.Tk()
root.geometry("640x480")
root.update()                    # ← 让 Tk 完成一次布局，之后量才有意义
widget.pack()
root.update()
print(widget.winfo_width())      # 现在是真实宽度；未 update() 时是 1

# 无桌面时：
# - 要么跳过这组断言；
# - 要么用 --check 这类不依赖映射的钩子做验证。
```

!!! note "逐引擎跑一遍最稳"
    ```bash
    for e in tksvg wand skia pillow cairo; do
        python -m tkflu --check -r "$e" || echo "引擎 $e 失败"
    done
    ```

---

## 八、平台相关

### 14. 自定义标题栏（`bwm` / `customwindow`）

**症状**：想用 Fluent 风格的无边框窗口，但行为怪怪的——拖动、最大化、
关闭有时不生效；用 `way=0` 开两个窗口甚至可能直接把进程干掉。

**原因**：这条路径是**实验性**的，只在 Windows 上验证过：

* `way=1`（`bwm`）会在创建时挂两个短暂的 `after(30/60)` 做
  "隐藏再显示"的手势（为了抢任务栏归属）。它们会随窗口销毁被回收，
  但这条路径本身没在非 Windows 上验证过。
* `way=0`（`customwindow`）把窗口过程（WNDPROC）回调存进**进程级全局**，
  开第二个窗口时第一个回调可能已被 GC —— 实测会以
  `0xC0000005`（访问冲突）直接崩掉进程。

**怎么办**：**不建议在正式产品里用**。要试就显式指定，并且接受它的局限：

```bash
python -m tkflu --custom-titlebar 1        # 实验特性，仅 Windows
```

自己实现时至少把临时回调记下来、在 `<Destroy>` 里取消
（做法见本页第 9 条）；平台判断也要做好，别让非 Windows 用户走到这条路径上。
`way=0` 在多窗口场景下请直接避开。

---

## 九、0.4.0 修掉的真缺陷（升级前必看）

这一节列的都是在 0.4.0 里**已经修好**的东西。如果你的代码里有对应的绕行写法，
升级之后可以删掉了。

| 症状 | 原因 | 现在 |
| --- | --- | --- |
| 点"切换可用状态"没反应（要鼠标划过才刷新） | 画廊改完 `state` 后没有重绘（`dconfigure` 只写属性） | 改完立刻 `_draw()` |
| `FluButton(..., style=...)` 写错一个字母，按钮从此再也切不了主题，还会带崩整趟换肤 | `theme()` 查表后无条件调用结果 | 非法取值退回默认值，不写入实例 |
| `disabled` 的按钮**回车**或 `invoke()` 照样触发 `command` | `invoke()` 漏了 `state` 判断 | 与鼠标点击一致地拦住 |
| `FluImage` 只显示成一个空盒子（图片被内嵌 Frame 盖住） | 嵌入的控件窗口永远画在画布元素之上 | 有图片时把内嵌窗口隐藏，图片按内边距居中 |
| 同一个进程里开第二个 `FluWindow`，文字变成很大的宋体 | 字体对象建在了第一个解释器上 | 字体按控件自己的解释器创建 |
| `FluLabel(..., font=...)` 传了字体却没生效 | 传入的字体被整个丢掉 | 传入即生效 |
| `FluSlider(orient="vertical")` 构造即崩 | 非横向时轨道/把手没创建，随后 `tag_bind` 抛错 | 纵向方向已实现 |
| `FluSlider(min=50, max=50)` 抛 `ZeroDivisionError` | 一段死代码里的除法先执行 | 区间退化为一个点时也能用 |
| 滑块 `value` 超出 `[min, max]`，进度条画到控件外面 | 只夹了把手、没夹进度 | 取值统一夹紧 |
| 拖动滑块时把手**没有**按下态 | 配色分支写成 `if event:`，而拖动最后那次调用不带事件 | 只看状态位 |
| `FluScrollBar.set(0.0, 0.5)` 报 `TclError` / `TypeError` | Tk 传进来的是**字符串**；且用 `coords` 改图片元素只接受 2 个坐标 | 自己转浮点，几何在 `_draw` 里算 |
| 横向滚动条静止时**什么都不显示** | 未展开分支只画竖直方向 | 两个方向都画 |
| 鼠标划过**禁用**的滚动条就报 svgwrite 的 `TypeError` | 禁用配色表里没有 `track_color`，None 当了 SVG 的 fill | 回退到滑块色 |
| 菜单弹窗挂在默认根窗口上，属主关了它还留着 | 弹出窗口没接 `master`；`FluMenu(tl)` 还被 `height` 位置参数吃掉 | 属主关系正确，父菜单一并收起 |
| 只设了动画帧间隔（帧数为 0）时，菜单打不开 / 提示气泡报 `ZeroDivisionError` | 淡入条件写成 `or`，除法却用帧数 | 条件与除法一致 |
| 反复开关窗口内存一直涨（50 次约 +96 MB） | 图标 `PhotoImage` 按 `id(tk)` 缓存，钉住整个解释器 | 去掉进程级缓存 |
| `FluFrame.destroy()` 之后面板还留在屏幕上 | 画布是父容器的直接子控件，销毁没带上它 | `destroy()` 连同画布一起销毁 |
| `FluFrame` 放进 `ttk.Frame` / `ttk.Notebook` 直接报 `unknown option "-background"` | 拿父容器的 `cget("background")`，ttk 没这个选项 | ttk 下向主题要底色 |
| 销毁一个子窗口后，**主窗口**排的 `after` 再也不执行，接着关主窗口报 `can't delete Tcl command` | `after` 清理是"整个解释器"级的，会误伤别的窗口 | 只回收本子树真正持有的回调 |
| Tab 聚焦到 `FluEntry`，按压没有按下态 | `<Button-1>` 绑定漏了 `add="+"`，覆盖掉了基类处理 | 加上 `add="+"` |

---

## 十、0.5.0 改了什么（主题切换重写）

0.5.0 只做了一件事：**把主题切换重写**。完整来龙去脉见
[更新日志](../blog/posts/2026-09-24_2.md)，这里只列"你需要知道的行为变化"。

| 事项 | 0.4.0 | 0.5.0 |
| --- | --- | --- |
| `mode()` 的阻塞时长（59 个控件的画廊，`skia`） | 2.8 ~ 4.0 s | **≈ 30 ms** |
| 同上（`tksvg`，默认引擎） | ≈ 3.3 s | **≈ 25 ms** |
| 各组件"第一次变色"的时刻差 | 150 ms 以上 | **0 ms**（同一帧） |
| 过渡中间色 | 1 种（瞬间跳变） | 3 ~ 6 种 |
| 换肤覆盖范围 | 窗口的直接子组件 + 各容器自己向下传播 | **整棵控件树** |
| `FluWindow.theme(mode)` | 只管窗口自己 | 连带窗口里的全部组件 |
| `mode()` 返回时画面 | 已经是新主题 | 还是旧主题（过渡随后开始） |

**升级要不要改代码**：不用。`FluThemeManager.mode()` / `toggle()` /
`tkflu.toggle_theme()` 的用法一个都没变。

**唯一要留意的**：如果你在测试里紧跟着 `mode()` 就去断言"画面/属性是最终态"，
现在要等过渡跑完。同步等的话：

```python
transition = thememanager.mode("dark")
while not transition.finished:
    root.update()
assert button.attributes.rest.back_color == "#202020"
```

只想立刻落定、不要动画，就按次关掉：

```python
thememanager.mode("dark", animation_steps=0)
```

### 附：老实现坏在哪（想理解细节可以看）

```python
for widget in window.winfo_children():
    widget.theme(mode=mode)   # 每个组件内部各排各的过渡帧
    widget._draw()
    widget.update()           # ← 这一句把事件循环跑了起来
```

`update()` 处理**全部**待办事件（含用户输入），于是：组件越多这一趟越久；
每个组件的帧起点是"轮到它自己"那一刻（而前面组件的 `update()` 又会把后面
组件已经到点的帧就地执行掉），所以"一个一个变色"；真正跑完的帧又都在那次
`mode()` 里消耗掉了，所以动画根本看不到——用户看到的是"卡两秒然后瞬间变色"。

---

## 还找不到原因？

1. 先确认版本：`python -c "import tkflu, tkdeft; print(tkflu.__version__, tkdeft.__version__)"`
   应为 `0.5.0 0.3.0`；
2. 跑一遍全引擎自检（见第 13 条）；
3. 用 [运行演示](run-demo.md) 里的画廊复现看看——排除是不是自己代码里的用法问题；
4. 还是不行，就带着**最小复现代码 + 报错栈 + `--list-engines` 输出**去提 issue。

入门相关的两页也可以对照看：[轻松上手](../getstarted/easytouse.md)、
[第一个应用](../getstarted/the_1st_app.md)；包根导出了哪些名字见
[tkflu API](../api/tkflu.md)。
