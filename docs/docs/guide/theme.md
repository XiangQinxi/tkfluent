# 主题与配色

tkfluent 的主题体现在三个层次：**窗口级深浅模式**、**全局主色调**、
**单个组件的样式**。三者可以独立使用。

## 一、深浅模式

### 单个组件

每个组件在构造时接受 `mode`：

```python
tkflu.FluButton(root, text="浅色", mode="light")
tkflu.FluButton(root, text="深色", mode="dark")
```

### 整个窗口

`FluWindow` 也有 `mode`，但**它不会自动递归**改子组件。
批量切换请用 `FluThemeManager`：

```python
import tkflu

root = tkflu.FluWindow(mode="light")
thememanager = tkflu.FluThemeManager(window=root, mode="light")

tkflu.FluButton(root, text="切换主题", command=thememanager.toggle).pack()

root.mainloop()
```

或者配合开关组件：

```python
toggle = tkflu.FluToggleButton(root, text="深色模式")
toggle.dconfigure(command=lambda: tkflu.toggle_theme(toggle, thememanager))
```

`FluThemeManager.mode()` 会遍历窗口的直接子组件，调用它们的 `theme(mode=...)`
并重绘。嵌套容器里的组件由其自身的 `update_children()` 负责向下传播，
所以**尽量把组件直接挂在窗口或 `FluFrame` 下**。

## 二、全局主色调

强调色（`style="accent"` 的按钮、开关等）取的是一个全局主色调，
提供 6 个预设：

```python
import tkflu

tkflu.blue_primary_color()     # 默认
tkflu.red_primary_color()
tkflu.orange_primary_color()
tkflu.yellow_primary_color()
tkflu.green_primary_color()
tkflu.purple_primary_color()
```

也可以自己指定一对颜色（浅色模式用第一个，深色模式用第二个）：

```python
from tkflu import set_primary_color

set_primary_color(("#005fb8", "#60cdff"))
```

!!! note "改完要重绘"
    主色调是**读取时取值**，已经画好的组件不会自动变色。
    改完之后需要重新 `theme()` 或 `_draw()`，最简单是重启界面：

    ```python
    tkflu.purple_primary_color()
    # 已存在的强调色按钮需要重画才会生效
    button.theme(mode="light", style="accent")
    ```

## 三、单组件样式

`FluButton` 有三种样式：

```python
tkflu.FluButton(root, text="standard")                  # 默认：浅色描边
tkflu.FluButton(root, text="accent", style="accent")    # 强调色填充
tkflu.FluButton(root, text="menu", style="menu")        # 无边框菜单项
```

`FluFrame` 有两种：

```python
tkflu.FluFrame(root, style="standard")     # 普通面板
tkflu.FluFrame(root, style="popupmenu")    # 弹出菜单用的面板
```

## 四、组件的四种状态

每个交互组件的配色由 `(mode, style, state)` 决定，其中 `state` 有四档：

| 状态 | 触发时机 |
| --- | --- |
| `rest` | 常态 |
| `hover` | 鼠标悬停 |
| `pressed` | 按下 |
| `disabled` | `dconfigure(state="disabled")` |

想改某个状态的配色，可以覆盖组件自己的状态字典：

```python
button = tkflu.FluButton(root, text="自定义悬停色")
button.dconfigure(hover={
    "back_color": "#ffe0e0",
    "back_opacity": 1,
    "border_color": "#ff0000",
    "border_color_opacity": 1,
    "border_color2": None,
    "border_color2_opacity": None,
    "border_width": 1,
    "radius": 6,
    "text_color": "#a00000",
})
button._draw()
```

## 五、过渡动画

主题切换的渐变过渡由两个全局参数控制：

```python
from tkflu import set_animation_steps, set_animation_step_time

set_animation_steps(5)        # 过渡帧数
set_animation_step_time(20)   # 每帧间隔（毫秒）
```

两者都设为 `0`（默认值）即关闭过渡。
帧数越多越顺滑，但每帧都会重新绘制一次，低配机器上建议 3–6 帧。

## 六、设计规范在哪

组件"长什么样"集中在 `tkflu.designs` 包里，每个模块返回一份普通的 `dict`：

```python
from tkflu.designs.button import button

button("light", "accent", "hover")
# {'back_color': '#005fb8', 'back_opacity': '0.9', ...}
```

所以**换皮肤不需要改组件代码**，改这些函数的返回值即可。
每个模块的取值说明见 [设计规范 API](../api/tkflu.designs.md)。
