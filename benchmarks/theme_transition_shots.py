"""目视验证：换肤途中连拍几帧，确认屏幕上真的看得到中间色。

数值断言（``tests/`` 里的那些）只能证明 ``attributes`` 在变；这个脚本证明
**屏幕**在变——它按窗口句柄抓图（复用 tkdeft ``benchmarks/visual_demo.py``
里的 Win32 ``PrintWindow``：不受遮挡、不受 DPI 缩放影响），把换肤过程中的
几帧存下来并打印画面平均亮度。深色主题更暗，所以一次成功的过渡应当看到
亮度**单调下降**（深色 → 浅色则单调上升），而不是"两帧之间直接跳到底"。

用法::

    python benchmarks/theme_transition_shots.py
    python benchmarks/theme_transition_shots.py --steps 6 --step-time 60
"""

from __future__ import annotations

import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

#: tkdeft 的截图工具所在（仓库同级目录）
_TKDEFT = os.path.join(os.path.dirname(_ROOT), "tkdeft")


def _load_capture():
    """拿到 Win32 ``capture_window``；非 Windows / 找不到 tkdeft 时返回 ``None``。"""
    if sys.platform != "win32":
        return None
    if _TKDEFT not in sys.path and os.path.isdir(os.path.join(_TKDEFT, "benchmarks")):
        sys.path.insert(0, _TKDEFT)
    try:
        from benchmarks.visual_demo import capture_window
    except Exception:
        return None
    return capture_window


def _brightness(image, box=None):
    from PIL import ImageStat

    region = image.crop(box) if box else image
    return round(ImageStat.Stat(region.convert("L")).mean[0], 1)


def build_scene(root, mode="light"):
    """摆一屏颜色差异明显的组件（面板 + 标准按钮 + 强调按钮 + 标签）。"""
    import tkflu

    panel = tkflu.FluFrame(root, width=440, height=260, mode=mode)
    panel.pack(padx=14, pady=14)
    widgets = [panel]
    for text, style in (("标准", "standard"), ("强调", "accent")):
        button = tkflu.FluButton(panel, text=text, width=240, mode=mode, style=style)
        button.pack(pady=6)
        widgets.append(button)
    label = tkflu.FluLabel(panel, text="标签", mode=mode)
    label.pack(pady=6)
    widgets.append(label)
    return panel, widgets


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="换肤过程连拍验证")
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--step-time", type=int, default=60)
    parser.add_argument("--renderer", default="skia")
    parser.add_argument("--out", default=os.path.join(_ROOT, "benchmarks", "shots"))
    args = parser.parse_args(argv)

    capture_window = _load_capture()
    if capture_window is None:
        print("跳过：需要 Windows + tkdeft 的 benchmarks/visual_demo.py")
        return 0

    import tkflu

    tkflu.set_renderer(args.renderer)
    tkflu.set_animation_steps(args.steps)
    tkflu.set_animation_step_time(args.step_time)

    root = tkflu.FluWindow(mode="light")
    root.geometry("520x360+60+60")
    root.deiconify()
    for _ in range(20):
        root.update()

    panel, widgets = build_scene(root, mode="light")
    for _ in range(20):
        root.update()

    os.makedirs(args.out, exist_ok=True)
    from ctypes import windll

    child = int(root.winfo_id())
    parent = windll.user32.GetParent(child)
    width, height = root.winfo_width(), root.winfo_height()
    # 面板内部的一个点：最能代表"这一帧面板是什么颜色"
    probe = (min(200, width - 20), min(150, height - 20))
    box = (30, 30, min(470, width - 10), min(300, height - 10))

    captured = []

    def shoot(index, label):
        # 必须先 update_idletasks()：PrintWindow 抓的是 DWM **已经合成**的内容，
        # "改完 canvas item → 真正上屏"要等一次空闲重绘。这里**只跑 idle**
        # （不要用 update()）——update() 会把后面还没到点的动画帧一起执行掉，
        # 那样脚本自己就把要观察的过渡给抹平了。
        root.update_idletasks()
        # 顶层父句柄 + flag=0：客户区最完整（flag=2 在部分系统上会返回空白）
        image, ok = capture_window(parent, width, height, 0)
        path = os.path.join(args.out, f"transition-{index}-{label}.png")
        image.save(path)
        value = _brightness(image, box)
        pixel = image.getpixel(probe)
        captured.append((label, value, pixel))
        print(
            f"  [{index}] {label:>5}  面板点={pixel}  均值亮度={value:<6}"
            f"  {'OK' if ok else 'FAIL'}  {os.path.basename(path)}"
        )

    shots = [0] + [int(args.step_time * (i + 1)) for i in range(args.steps)]
    switch_at = 150

    def schedule():
        for index, delay in enumerate(shots):
            label = "start" if index == 0 else f"f{index}"
            root.after(switch_at + delay, lambda i=index, t=label: shoot(i, t))
        root.after(switch_at + shots[-1] + 150, root.quit)

    manager = tkflu.FluThemeManager(window=root, mode="light")
    root.after(switch_at, lambda: manager.mode("dark"))
    root.after(60, schedule)
    root.mainloop()

    print("\n各帧面板颜色：")
    for label, _value, pixel in captured:
        print(f"  {label:>5}  {pixel}")

    # 只看面板**内部**那个探针点的红通道：它必须逐帧单调下降（浅 → 深），
    # 而且中间应当出现**既不是起点也不是终点**的值（那才是"过渡"）。
    reds = [pixel[0] for _label, _value, pixel in captured]
    drops = [a - b for a, b in zip(reds, reds[1:])]
    monotone = all(step >= -2 for step in drops)
    middles = [r for r in reds if reds[0] - 12 > r > reds[-1] + 12]
    print("\n红通道序列：", reds)
    print("逐帧差值：", drops)
    print("单调变暗：", "是 ✓" if monotone else "否 ✗")
    print(f"中间色帧数：{len(middles)}  {'✓ 真的在过渡' if middles else '✗ 是瞬间跳变'}")

    try:
        root.destroy()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
