# 运行演示（组件画廊）

tkfluent 自带一个把**所有组件摆在同一个窗口里**的画廊，用来快速看效果、
对比渲染引擎、或者验证环境是否装好。

## 启动

```bash
python -m tkflu
```

安装后也可以直接用命令：

```bash
tkfluent-demo
```

## 命令行参数

```text
python -m tkflu [-h] [-r ENGINE] [--list-engines] [-m {light,dark}]
                [--primary {blue,red,orange,yellow,green,purple}]
                [--geometry WxH] [--animation-steps N]
                [--animation-step-time MS] [--no-animation]
                [--cache-budget PIXELS] [--custom-titlebar WAY]
                [--check] [--stats]
```

| 参数 | 说明 |
| --- | --- |
| `-r, --renderer` | 渲染引擎：名字、编号（0-4）或 `auto`；不指定则沿用库默认 |
| `--list-engines` | 列出所有引擎及其可用性后退出 |
| `-m, --mode` | 启动主题：`light`（默认）或 `dark` |
| `--primary` | 主色调预设，会影响强调色按钮与开关 |
| `--geometry` | 窗口尺寸，例如 `720x640` |
| `--animation-steps` | 过渡动画帧数（默认 5，`0` 关闭） |
| `--animation-step-time` | 每帧间隔毫秒数（默认 20） |
| `--no-animation` | 等价于把上面两个都设为 0 |
| `--cache-budget` | 图片缓存的像素预算 |
| `--custom-titlebar` | 启用自定义标题栏（实验特性，仅 Windows） |
| `--check` | 无界面自检，成功返回 0 |
| `--stats` | 退出时打印缓存命中统计 |

## 常用组合

```bash
# 看看有哪些引擎可用
python -m tkflu --list-engines

# 用最快的可用引擎（进程内栅格化）
python -m tkflu -r auto

# 指定引擎、深色主题、紫色主色调
python -m tkflu -r skia --mode dark --primary purple

# 关掉动画（低配机器或录屏时更稳）
python -m tkflu --no-animation

# 换主色调看看强调色组件的变化
python -m tkflu --primary orange
```

## 无界面自检 `--check`

`--check` 会真实地建出画廊里的每一个组件，然后对每个组件依次调用
重绘、浅色/深色主题、鼠标进入/离开、按下/抬起、尺寸变化等钩子，
最后打印缓存统计并退出。

```bash
python -m tkflu --check              # 用默认引擎
python -m tkflu --check -r skia      # 指定引擎
echo $?                              # 0 表示一切正常
```

它适合放进 CI：能在**不需要显示器**的前提下抓出"构造函数签名不匹配、
某个引擎下绘制报错"这类问题。逐引擎跑一遍就能覆盖所有后端：

```bash
for e in tksvg wand skia pillow cairo; do
    python -m tkflu --check -r "$e" || echo "引擎 $e 失败"
done
```

## 画廊里都有什么

窗口分成两块：

* **左栏**是"内容展示型"组件：标签（带提示）、徽标（标准/强调）、
  输入框、多行文本框、列表、图片；
* **右栏**是"交互型"组件：四种按钮、开关、滑块、滚动条；
* **顶部**是菜单栏（含二级、三级级联）；
* **底部**是状态栏，显示当前渲染引擎与图片缓存命中率，并提供
  "切换主题""批量切换可用状态""刷新状态"三个按钮。

点任何组件都会在控制台打印一行事件日志，窗口底部也会显示最近一条，
用来确认事件是否按预期触发。

## 作为模块调用

`main()` 可以直接导入，参数与命令行一致：

```python
from tkflu.__main__ import main

raise SystemExit(main(["--renderer", "pillow", "--check"]))
```

## 其他示例脚本

包内还带了几个更聚焦的示例，直接运行即可：

```bash
python -m tkflu.demos.demo1        # 基础组件
python -m tkflu.demos.grad         # 渐变效果
python -m tkflu.demos.grad3        # 带过渡动画的渐变
python -m tkflu.demos.designer     # 设计器风格
python -m tkflu.demos.scroll       # 滚动
python -m tkflu.demos.tooltip      # 提示气泡
```
