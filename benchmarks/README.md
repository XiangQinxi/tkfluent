# benchmarks

主题切换的度量脚本。**数值断言在 `tests/`，这两个脚本负责"到底花了多久 /
是不是同步 / 屏幕上真的变了吗"。**

```bash
python benchmarks/theme_switch_bench.py                    # 精简场景（13 个控件）
python benchmarks/theme_switch_bench.py --gallery           # 完整组件画廊（59 个控件）
python benchmarks/theme_switch_bench.py --gallery -r skia   # 换引擎
python benchmarks/theme_switch_bench.py --json out.json --label before

python benchmarks/theme_transition_shots.py                # 连拍换肤过程（Windows）
```

## `theme_switch_bench.py`

| 指标 | 含义 |
| --- | --- |
| `mode_sync_ms` | `FluThemeManager.mode()` **这一次调用**花了多久。这段时间里事件循环是卡死的，用户点完按钮到界面响应之间的延迟就是它 |
| `sweep_ms` | 从点下按钮到"最后一帧画完"的总时间 |
| `max_gap_ms` | 采样计时器两次触发之间最长的间隔——用户感知到的掉帧 |
| `distinct_colors` | 被采样控件在整趟换肤里出现过几种不同配色。**1 = 根本没过过渡**（一步跳到终态） |
| `sync_spread_ms` | 各采样控件"第一次变色"的时刻之间的最大差值。这是"同步进行"的直接度量：**0 才是真正同步** |

!!! note "`sync_spread_ms` 偶尔不是 0"
    0 表示所有控件在同一帧改变。偶尔会看到几十毫秒的非零值，那**不是**不同步，
    而是某个控件的第一帧混色**四舍五入后和起点色一样**（例如 `#ffffff` 与
    `#fefefe` 都取整成 `#ffffff`），于是它"第一次可见的变化"落到了下一帧。
    真正的同步保证是结构性的：`_paint(t)` 在**一次回调**里把同一个 `t` 写给
    所有控件（`tests/test_theme_transition.py` 断言了这一点）。

采样由事件循环自己驱动（一个 2ms 的 `after` 计时器）+ 真正的 `mainloop`。

!!! warning "别用 `while: root.update()` 忙等来量"
    `update()` 会把所有到点的回调一口气跑完，整段动画会被压缩进**一次**
    `update()` 调用里——采样器一个中间帧都看不到，"过渡帧数"会测成 1，
    而真实界面上它是正常的。这个坑我踩过一次。

## `theme_transition_shots.py`

按窗口句柄连拍（复用 tkdeft `benchmarks/visual_demo.py` 里的 Win32
`PrintWindow`：不受遮挡、不受 DPI 缩放影响），把换肤过程中的几帧存到
`benchmarks/shots/`，并打印面板上一个探针点的颜色。

断言很简单但很关键：**红通道必须逐帧单调变化，而且中间要出现既不是起点
也不是终点的值**——那才叫"过渡"，而不是"瞬间跳变"。

实测输出（`skia`，6 帧 × 60ms）：

```text
红通道序列： [255, 251, 251, 224, 149, 74, 47]
单调变暗： 是 ✓
中间色帧数：3  ✓ 真的在过渡
```

抓图前必须 `update_idletasks()`（PrintWindow 抓的是 DWM **已经合成**的内容），
但**不能**用 `update()`——那会把后面还没到点的动画帧一起执行掉，
脚本自己就把要观察的过渡抹平了。

非 Windows 平台会自动跳过（只支持 Windows 的 `PrintWindow`）。
