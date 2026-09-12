# 组件总览

所有组件都可以从包根直接导入：

```python
import tkflu
# 或者
from tkflu import FluWindow, FluButton, FluFrame
```

## 一览表

| 组件 | 用途 | 关键参数 |
| --- | --- | --- |
| [`FluWindow`](../api/tkflu.window.md) | 主窗口（应用根窗口） | `mode` |
| [`FluToplevel`](../api/tkflu.toplevel.md) | 子窗口 | `mode` |
| [`FluFrame`](../api/tkflu.frame.md) | 圆角面板 / 容器 | `width` `height` `mode` `style` |
| [`FluLabel`](../api/tkflu.label.md) | 文本标签 | `text` `width` `height` `font` |
| [`FluButton`](../api/tkflu.button.md) | 按钮 | `text` `style` `state` `command` |
| [`FluToggleButton`](../api/tkflu.togglebutton.md) | 开关 | `text` `command`（读 `dcget("checked")`） |
| [`FluBadge`](../api/tkflu.badge.md) | 徽标 / 胶囊标签 | `text` `width` `style` |
| [`FluEntry`](../api/tkflu.entry.md) | 单行输入框 | `width` `textvariable` `state` |
| [`FluText`](../api/tkflu.text.md) | 多行文本框 | `width` `height` `state` |
| [`FluSlider`](../api/tkflu.slider.md) | 滑块 | `value` `min` `max` `orient` `tick` `changed` |
| [`FluScrollBar`](../api/tkflu.scrollbar.md) | 滚动条 | `command` `orient` `state` |
| [`FluImage`](../api/tkflu.image.md) | 图片 | `image`（路径或 `PhotoImage`） |
| [`FluMenu`](../api/tkflu.menu.md) | 下拉菜单 | `add_command` / `add_cascade` |
| [`FluMenuBar`](../api/tkflu.menubar.md) | 菜单栏 | `add_command` / `add_cascade` |
| [`FluPopupMenu`](../api/tkflu.popupmenu.md) | 弹出菜单 | — |
| [`FluPopupWindow`](../api/tkflu.popupwindow.md) | 通用弹出窗口 | — |
| [`FluToolTip`](../api/tkflu.tooltip.md) | 悬浮提示 | 通过组件的 `.tooltip()` 挂载 |
| [`FluThemeManager`](../api/tkflu.thememanager.md) | 主题管理 | `mode` / `toggle` |
| [`FluListBox`](../api/tkflu.listbox.md) | 列表 | ⚠️ 占位实现，见下文 |

!!! warning "FluListBox 尚未完成"
    `FluListBox` 目前只是一个"长得像按钮的圆角矩形"，**还没有真正的列表数据与选择能力**。
    保留它是为了固定 API 形状，暂不建议用于生产。

## 最小示例

```python
import tkflu

root = tkflu.FluWindow(mode="light")
root.geometry("360x260")

frame = tkflu.FluFrame(root, width=320, height=220)
frame.pack(fill="both", expand=True, padx=15, pady=15)

tkflu.FluLabel(frame, text="你好，tkfluent").pack(anchor="w", padx=10, pady=(10, 4))

tkflu.FluButton(frame, text="点我", command=lambda: print("clicked")).pack(
    fill="x", padx=10, pady=4
)

entry = tkflu.FluEntry(frame, width=280)
entry.pack(fill="x", padx=10, pady=4)

root.mainloop()
```

## 按钮的三种样式

```python
import tkflu

root = tkflu.FluWindow()

tkflu.FluButton(root, text="standard").pack(padx=10, pady=4)
tkflu.FluButton(root, text="accent", style="accent").pack(padx=10, pady=4)
tkflu.FluButton(root, text="menu", style="menu").pack(padx=10, pady=4)
tkflu.FluButton(root, text="disabled", state="disabled").pack(padx=10, pady=4)

root.mainloop()
```

## 开关与状态读取

`FluToggleButton` 的选中状态存在组件的 `attributes` 里，用 `dcget` 读取：

```python
toggle = tkflu.FluToggleButton(root, text="启用")

def on_toggle():
    print("当前状态：", toggle.dcget("checked"))

toggle.dconfigure(command=on_toggle)
```

同样的 `dcget` / `dconfigure` 也适用于其他组件（它们是
`tkdeft.object.DObject` 提供的统一配置接口）：

```python
button.dconfigure(text="新的文字", state="disabled")
print(button.dcget("state"))     # 'disabled'
```

## 挂提示

任何继承 `FluToolTipBase` 的组件都能挂一个 Fluent 风格的提示：

```python
label = tkflu.FluLabel(root, text="把鼠标放上来")
label.tooltip(text="我是提示")
```

## 容器怎么用

`FluFrame` 内部是"画布 + 子 Frame"的结构，但它把 `pack` / `grid` / `place`
都代理给了内部画布，所以你可以像用普通容器一样用它：

```python
frame = tkflu.FluFrame(root, width=300, height=200)
frame.pack(padx=10, pady=10)

tkflu.FluButton(frame, text="在面板里").pack(padx=8, pady=8)
```

## 想直接看效果

```bash
python -m tkflu
```

会打开一个把所有组件摆在一起的画廊，详见 [运行演示](run-demo.md)。
