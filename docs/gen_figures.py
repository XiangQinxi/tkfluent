"""生成 tkfluent 文档站用的插图，输出到 ``docs/docs/assets/``。

跟 tkdeft 的 ``docs/gen_figures.py`` 是同一套做法，只是内容换成组件：

* **组件图鉴**：真起一个窗口把组件摆好，用 Win32 ``PrintWindow`` 抓**客户区**，
  再按 ``winfo_rootx/rooty`` 精确裁剪出每个控件，最后拼成带名字的图鉴；
* **按钮状态矩阵**：4 个状态 × 3 种样式 × 2 种主题，用的就是真实组件
  （``enter`` / ``button1`` / ``state`` 直接设成对应状态再 ``_draw()``）；
* **整窗截图**：``python -m tkflu`` 的画廊，浅色 / 深色各一张；
* **流程图**：``diagrams/*.mmd`` 用 mermaid-cli 预渲染（见下面的说明）。

用法（在 ``docs/`` 目录下）::

    python gen_figures.py            # 只列出会生成哪些图
    python gen_figures.py --write    # 实际写入 docs/docs/assets/
    python gen_figures.py --write --only widgets-grid   # 只生成一张

生成完请跑一次 ``python benchmarks/check_docs.py``（在 tkdeft 仓库里），
确认文档站仍然 ``--strict`` 无警告。

!!! note "关于流程图"
    Material 的 mermaid 支持是**运行时从 unpkg CDN 拉脚本**的，而本站启用了
    ``offline`` 插件——离线打开时图会消失。所以流程图统一放 ``diagrams/*.mmd``，
    由本脚本渲染成 PNG，页面只引用图片。
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "docs", "assets")
DIAGRAMS = os.path.join(HERE, "diagrams")

#: 渲染流程图用的浏览器（mermaid-cli 走 Puppeteer，用系统已有的即可）
BROWSERS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)

# ---------------------------------------------------------------- 调色板
BG_LIGHT = "#f3f3f3"
BG_DARK = "#202020"
CARD = "#ffffff"
CARD_DARK = "#2b2b2b"
LINE = "#e0e0e0"
LINE_DARK = "#3a3a3a"
TEXT = "#1b1b1b"
TEXT_DARK = "#f0f0f0"
MUTED = "#616161"
MUTED_DARK = "#a0a0a0"
ACCENT = "#005fb8"

FONTS = (
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhl.ttc",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
)


def _font(size: int):
    """取一个支持中文的字体；找不到就退回 Pillow 内置位图字体。"""
    from PIL import ImageFont

    for path in FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------- 画布工具
def _new(width: int, height: int, color=BG_LIGHT):
    from PIL import Image

    return Image.new("RGB", (width, height), color)


def _draw_text(draw, xy, text, font, fill=TEXT, anchor="la"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def _centered(image, box_w, box_h):
    from PIL import Image

    canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    canvas.alpha_composite(
        image,
        (max(0, (box_w - image.width) // 2), max(0, (box_h - image.height) // 2)),
    )
    return canvas


# ---------------------------------------------------------------- Win32 抓图
# 说明：这段与 tkdeft 的 benchmarks/visual_demo.py 同源。这里保留一份本地实现，
# 是为了让 tkfluent 的文档生成不依赖另一个仓库的脚本目录。
_PW_RENDERFULLCONTENT = 0x00000002


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


def _capture_hwnd(hwnd: int, width: int, height: int, flag: int = _PW_RENDERFULLCONTENT):
    """按**窗口句柄**抓图（Win32 PrintWindow）。

    为什么不按屏幕坐标抓：DPI 缩放、多虚拟桌面、窗口被遮挡时都会抓错对象。
    按句柄抓既不受遮挡影响，也不受坐标映射影响。

    :returns: ``(PIL 图片, PrintWindow 是否成功)``
    """
    from PIL import Image

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    hdc = user32.GetWindowDC(hwnd)
    memdc = gdi32.CreateCompatibleDC(hdc)
    bitmap = gdi32.CreateCompatibleBitmap(hdc, width, height)
    gdi32.SelectObject(memdc, bitmap)
    ok = user32.PrintWindow(hwnd, memdc, flag)

    header = _BITMAPINFOHEADER()
    header.biSize = ctypes.sizeof(header)
    header.biWidth = width
    header.biHeight = -height          # 负数 = 自上而下
    header.biPlanes = 1
    header.biBitCount = 32
    buffer = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(memdc, bitmap, 0, height, buffer, ctypes.byref(header), 0)
    image = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1)

    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(memdc)
    user32.ReleaseDC(hwnd, hdc)
    return image.convert("RGB"), bool(ok)


def _pump(root, times: int = 25) -> None:
    """把待处理事件跑完，确保布局与重绘都落地（否则截到的是半成品）。"""
    for _ in range(times):
        root.update()


def _capture_client(root, margin: int = 0):
    """抓窗口**客户区**（不含系统标题栏/边框）。

    客户区坐标与 ``winfo_rootx/rooty`` 是同一套坐标系，因此可以直接按控件
    的 ``winfo`` 框裁剪。留 ``margin`` 像素余量，避免把抗锯齿边缘切掉。

    :returns: ``(整窗图, [(控件, 裁剪框), ...])``
    """
    width, height = root.winfo_width(), root.winfo_height()
    image, ok = _capture_hwnd(int(root.winfo_id()), width, height)
    if not ok:
        print("  ! PrintWindow 返回 False，截出来的可能是空白")
    return image, (width, height)


def _crop_widget(shot, root, widget, margin: int = 2):
    """按控件的 ``winfo`` 框从整窗图里裁出它（坐标以客户区原点为准）。"""
    x = widget.winfo_rootx() - root.winfo_rootx() - margin
    y = widget.winfo_rooty() - root.winfo_rooty() - margin
    w = widget.winfo_width() + margin * 2
    h = widget.winfo_height() + margin * 2
    x = max(0, min(x, shot.width - 1))
    y = max(0, min(y, shot.height - 1))
    return shot.crop((x, y, min(x + w, shot.width), min(y + h, shot.height)))


# ---------------------------------------------------------------- 组件图鉴
#: (名字, 说明, 构造参数) —— 尺寸都在这里定，摆位与裁剪靠 winfo 实测
WIDGETS = (
    ("FluLabel", "文本标签", {"text": "FluLabel", "height": 22}),
    ("FluBadge", "徽标 / 胶囊", {"text": "FluBadge"}),
    ("FluBadge(accent)", "强调色徽标", {"text": "Accent", "style": "accent"}),
    ("FluButton", "标准按钮", {"text": "FluButton"}),
    ("FluButton(accent)", "强调按钮", {"text": "Accent", "style": "accent"}),
    ("FluToggleButton", "开关按钮", {"text": "FluToggleButton", "width": 170}),
    ("FluEntry", "单行输入框", {"width": 180, "height": 32}),
    ("FluText", "多行文本框", {"width": 180, "height": 56}),
    ("FluSlider", "滑块", {"width": 180, "height": 28}),
    ("FluScrollBar", "滚动条", {"width": 180, "height": 6, "orient": "horizontal"}),
    (
        "FluListBox",
        "列表（可滚动 / 可选）",
        {
            "width": 180,
            "height": 48,
            "item_height": 24,
            "items": [f"第 {i} 行" for i in range(1, 21)],
        },
    ),
    ("FluCheckBox", "复选框", {"text": "FluCheckBox", "checked": True}),
    ("FluCheckBox(三态)", "不确定态", {"text": "三态", "checked": None}),
    ("FluRadioBox", "单选框", {"text": "FluRadioBox", "value": "a"}),
    (
        "FluLiteNav",
        "轻量导航栏",
        {
            "items": [("★", "一"), ("☆", "二")],
            "orient": "horizontal",
            "style": "card",
            "selected": 0,
        },
    ),
    ("FluImage", "图片", {"width": 96, "height": 48}),
    ("FluFrame", "圆角面板", {"width": 180, "height": 48}),
    ("FluButton(disabled)", "禁用态", {"text": "Disabled", "state": "disabled"}),
    ("FluButton(menu)", "菜单样式", {"text": "Menu 样式", "style": "menu"}),
)


def _make_sample_image(path: str) -> str:
    """画一张示意图（避免文档生成依赖外部素材）。"""
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (192, 96), "#005fb8")
    draw = ImageDraw.Draw(image)
    for i in range(0, 192, 8):
        draw.rectangle((i, 0, i + 4, 96), fill="#0a7ad0" if (i // 8) % 2 else "#004c93")
    draw.ellipse((56, 16, 136, 80), fill="#ffd166")
    image.save(path)
    return path


def figure_widgets_grid(mode: str = "light", out_name: str = "widgets-grid.png"):
    """组件图鉴：真起窗口摆好组件 → 抓客户区 → 逐个裁剪 → 拼成带名字的图。"""
    import tkflu

    from PIL import ImageDraw

    dark = mode == "dark"
    bg = BG_DARK if dark else BG_LIGHT
    # 卡片底色刻意与窗口背景一致：组件本身大多是白色的（面板、输入框），
    # 白色卡片会让它们"隐身"，只留一圈边框来分隔格子
    card = bg
    line = LINE_DARK if dark else LINE
    text = TEXT_DARK if dark else TEXT
    muted = MUTED_DARK if dark else MUTED

    sample = _make_sample_image(os.path.join(HERE, "_sample_image.png"))

    columns = 3
    cell_w, cell_h = 236, 104
    pad = 16

    root = tkflu.FluWindow(mode=mode)
    root.title(f"tkfluent 组件图鉴 · {mode}")
    width = pad * 2 + cell_w * columns
    rows = (len(WIDGETS) + columns - 1) // columns
    height = pad * 2 + cell_h * rows
    root.geometry(f"{width}x{height}+90+60")
    root.update()

    placed = []
    for index, (name, _desc, kwargs) in enumerate(WIDGETS):
        col, row = index % columns, index // columns
        kwargs = dict(kwargs)
        if name.startswith("FluImage"):
            kwargs["image"] = sample
        widget = getattr(tkflu, name.split("(")[0])(root, mode=mode, **kwargs)
        widget.place(
            x=pad + col * cell_w + (cell_w - widget.winfo_reqwidth()) // 2,
            y=pad + row * cell_h + 6,
        )
        placed.append((name, _desc, widget))

    _pump(root)
    _pump(root)
    shot = _capture_client(root)[0]

    canvas = _new(width, height, bg)
    draw = ImageDraw.Draw(canvas)
    f_name = _font(13)
    f_desc = _font(11)
    for index, (name, desc, widget) in enumerate(placed):
        col, row = index % columns, index // columns
        x = pad + col * cell_w
        y = pad + row * cell_h
        draw.rounded_rectangle(
            (x, y, x + cell_w - 12, y + cell_h - 12),
            radius=8, fill=card, outline=line, width=1,
        )
        crop = _crop_widget(shot, root, widget, margin=2)
        canvas.paste(crop, (x + (cell_w - 12 - crop.width) // 2, y + 10))
        _draw_text(draw, (x + 12, y + cell_h - 40), name, f_name, text)
        _draw_text(draw, (x + 12, y + cell_h - 24), desc, f_desc, muted)

    root.destroy()
    return canvas


# ---------------------------------------------------------------- 按钮状态矩阵
#: 状态 → 怎么让真实组件进入这个状态
def _apply_state(button, state: str) -> None:
    if state == "disabled":
        button.dconfigure(state="disabled")
    elif state == "hover":
        button.enter = True
    elif state == "pressed":
        button.enter = True
        button.button1 = True
    button._draw()


def figure_button_states():
    """按钮状态矩阵：4 状态 × 3 样式，浅色/深色各一组。"""
    import tkflu

    from PIL import ImageDraw

    styles = ("standard", "accent", "menu")
    states = ("rest", "hover", "pressed", "disabled")
    btn_w, btn_h = 132, 32
    cell_w, cell_h = btn_w + 26, btn_h + 20
    label_w = 76
    block_head = 34
    pad = 22
    gap = 26

    width = pad * 2 + label_w + cell_w * len(styles)
    height = pad * 2 + (block_head + cell_h * len(states) + gap) * 2

    canvas = _new(width, height, BG_LIGHT)
    draw = ImageDraw.Draw(canvas)
    f_title, f_cell, f_label = _font(15), _font(12), _font(13)

    for block, mode in enumerate(("light", "dark")):
        block_top = pad + block * (block_head + cell_h * len(states) + gap)
        block_bg = BG_LIGHT if mode == "light" else BG_DARK
        block_fg = TEXT if mode == "light" else TEXT_DARK
        block_muted = MUTED if mode == "light" else MUTED_DARK

        draw.rectangle(
            (0, block_top - block_head, width, block_top + cell_h * len(states)),
            fill=block_bg,
        )
        _draw_text(
            draw, (pad, block_top - block_head + 6),
            f"mode='{mode}'", f_title, block_fg,
        )
        for col, style in enumerate(styles):
            _draw_text(
                draw,
                (pad + label_w + col * cell_w + cell_w // 2, block_top - block_head + 10),
                f"style='{style}'", f_cell, block_muted, anchor="ma",
            )

        root = tkflu.FluWindow(mode=mode)
        root.geometry(f"{width}x{cell_h * len(states) + 10}+90+60")
        root.update()

        widgets = []
        for row, state in enumerate(states):
            _draw_text(
                draw, (pad + label_w - 12, block_top + row * cell_h + cell_h // 2),
                state, f_label, block_muted, anchor="ra",
            )
            for col, style in enumerate(styles):
                button = tkflu.FluButton(
                    root, text=state, width=btn_w, height=btn_h,
                    mode=mode, style=style,
                )
                button.place(x=col * cell_w + 13, y=row * cell_h + 10)
                widgets.append((row, col, state, button))

        # 先把布局跑出来（place 之后 winfo_width 才是真实值），
        # 再把每个按钮拨到它那一格的状态并重绘——顺序反了就画成 rest 了
        _pump(root)
        for _row, _col, state, button in widgets:
            _apply_state(button, state)
        _pump(root)
        shot = _capture_client(root)[0]
        for row, col, _state, button in widgets:
            crop = _crop_widget(shot, root, button, margin=2)
            canvas.paste(
                crop,
                (
                    pad + label_w + col * cell_w + (cell_w - crop.width) // 2,
                    block_top + row * cell_h + (cell_h - crop.height) // 2,
                ),
            )
        root.destroy()

    _draw_text(
        draw, (pad, height - 16),
        "同一批真实组件：enter / button1 / state 直接设成对应状态后重绘（放大 2 倍保存）",
        _font(11), MUTED,
    )
    return canvas.resize((width * 2, height * 2), 1)   # 1 = NEAREST，保持像素锐利


# ---------------------------------------------------------------- 整窗截图
#: 画廊截图的窗口尺寸。必须与 ``python -m tkflu`` 的默认 ``--geometry``
#: 保持一致，否则组件会被挤在一起（0.4.0 起默认是 760x900，
#: 因为画廊里多了复选框 / 单选框 / 真列表 / 导航栏）。
GALLERY_GEOMETRY = "760x900"


def figure_gallery(mode: str, out_name: str):
    """运行 ``python -m tkflu`` 的画廊并截整窗（含系统标题栏）。"""
    import tkflu
    from tkflu.__main__ import build_gallery

    root = tkflu.FluWindow(mode=mode)
    root.title(f"tkfluent 组件画廊 · {mode}")
    root.geometry(f"{GALLERY_GEOMETRY}+80+40")
    build_gallery(root, mode=mode)
    _pump(root, 30)
    time.sleep(0.4)

    width, height = root.winfo_width(), root.winfo_height()
    # 父句柄（真正的顶层窗口）抓得更完整：含标题栏，看起来就是"真跑起来的程序"
    child = int(root.winfo_id())
    parent = ctypes.windll.user32.GetParent(child)
    image, ok = _capture_hwnd(parent, width, height)
    if not ok or image.getcolors(maxcolors=1 << 22) is None:
        image, _ = _capture_hwnd(child, width, height)

    root.destroy()
    print(f"  {image.width}x{image.height} -> assets/{out_name}")
    return image


def figure_theme_compare(light_name="gallery-light.png", dark_name="gallery-dark.png",
                         out_name="theme-compare.png"):
    """把浅色/深色两张整窗截图并排放，用于"换主题"的对比说明。"""
    from PIL import Image, ImageDraw

    paths = [os.path.join(ASSETS, name) for name in (light_name, dark_name)]
    if not all(os.path.exists(path) for path in paths):
        print(f"  跳过 {out_name}：缺少 {light_name} / {dark_name}（先生成画廊截图）")
        return None

    images = [Image.open(path).convert("RGB") for path in paths]
    target_h = 560
    scaled = [
        image.resize(
            (int(image.width * target_h / image.height), target_h), Image.LANCZOS
        )
        for image in images
    ]
    pad, head, gap = 22, 40, 24
    width = pad * 2 + sum(image.width for image in scaled) + gap
    height = pad * 2 + head + target_h
    canvas = _new(width, height)
    draw = ImageDraw.Draw(canvas)
    f_title = _font(15)

    x = pad
    for label, image in zip(("浅色 mode='light'", "深色 mode='dark'"), scaled):
        _draw_text(draw, (x, pad + 8), label, f_title, TEXT)
        canvas.paste(image, (x, pad + head))
        draw.rectangle(
            (x - 1, pad + head - 1, x + image.width, pad + head + target_h),
            outline=LINE,
        )
        x += image.width + gap

    _draw_text(
        draw, (pad, height - 18),
        "同一套组件：FluThemeManager 切换 mode 后重新 _draw()，绘制层不用改",
        _font(11), MUTED,
    )
    return canvas


# ---------------------------------------------------------------- 流程图
def figure_diagram(source: str, out_name: str, scale: int = 2):
    """把 ``docs/diagrams/<source>.mmd`` 渲染成 ``assets/<out_name>``。

    需要 Node（``npx``）与一个 Chromium 系浏览器；两者都没有时**跳过**，
    仓库里已提交的图片不受影响。
    """
    import shutil

    src = os.path.join(DIAGRAMS, source + ".mmd")
    if not os.path.exists(src):
        print(f"  跳过 {out_name}：找不到 {src}")
        return None
    if shutil.which("npx") is None:
        print(f"  跳过 {out_name}：没有 npx（装了 Node 就能重新生成）")
        return None

    env = dict(os.environ)
    browser = next((path for path in BROWSERS if os.path.exists(path)), None)
    if browser:
        env.setdefault("PUPPETEER_EXECUTABLE_PATH", browser)

    dst = os.path.join(ASSETS, out_name)
    cmd = ["npx", "--yes", "@mermaid-js/mermaid-cli@11",
           "-i", src, "-o", dst, "-b", "white", "-s", str(scale)]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env, shell=True)
    if result.returncode != 0 or not os.path.exists(dst):
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-3:]
        print(f"  跳过 {out_name}：mermaid-cli 失败 {tail}")
        return None
    print(f"  {source}.mmd -> assets/{out_name}")
    return dst


# ---------------------------------------------------------------- 入口
FIGURES = {
    "widgets-light": "widgets-light.png · 组件图鉴（浅色）",
    "widgets-dark": "widgets-dark.png · 组件图鉴（深色）",
    "button-states": "button-states.png · 按钮 4 状态 × 3 样式（浅/深两组）",
    "gallery-light": "gallery-light.png · 画廊整窗截图（浅色）",
    "gallery-dark": "gallery-dark.png · 画廊整窗截图（深色）",
    "theme-compare": "theme-compare.png · 浅色/深色并排对比",
    "architecture": "architecture.png · tkfluent 与 tkdeft 的分层（diagrams/architecture.mmd）",
    "widget-anatomy": "widget-anatomy.png · 组件的内部结构（diagrams/widget-anatomy.mmd）",
    "theme-flow": "theme-flow.png · 一键换肤的调用链（diagrams/theme-flow.mmd）",
    "event-flow": "event-flow.png · 事件 → 状态 → 重绘（diagrams/event-flow.mmd）",
    "svg-pipeline": "svg-pipeline.png · 一张图是怎么画出来的（diagrams/svg-pipeline.mmd）",
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="生成 tkfluent 文档站插图")
    parser.add_argument("--write", action="store_true", help="实际写入文件")
    parser.add_argument("--only", action="append", default=None,
                        help="只生成指定插图（可重复）")
    args = parser.parse_args(argv)

    wanted = args.only or list(FIGURES)
    unknown = [name for name in wanted if name not in FIGURES]
    if unknown:
        parser.error(f"未知的插图 {unknown}；可用：{sorted(FIGURES)}")

    print("将生成：")
    for name in wanted:
        print(f"  - {FIGURES[name]}")
    if not args.write:
        print("\n（加 --write 才会真正写入 docs/docs/assets/）")
        return 0

    if sys.platform != "win32":
        # 截图依赖 Win32 PrintWindow；流程图仍然可以生成
        only_diagrams = [n for n in wanted if n in
                         ("architecture", "widget-anatomy", "theme-flow",
                          "event-flow", "svg-pipeline")]
        print("  注意：非 Windows 平台，截图类插图跳过")
        wanted = only_diagrams

    os.makedirs(ASSETS, exist_ok=True)
    producers = {
        "widgets-light": lambda: _save(figure_widgets_grid("light", "widgets-light.png"), "widgets-light.png"),
        "widgets-dark": lambda: _save(figure_widgets_grid("dark", "widgets-dark.png"), "widgets-dark.png"),
        "button-states": lambda: _save(figure_button_states(), "button-states.png"),
        "gallery-light": lambda: _save(figure_gallery("light", "gallery-light.png"), "gallery-light.png"),
        "gallery-dark": lambda: _save(figure_gallery("dark", "gallery-dark.png"), "gallery-dark.png"),
        "theme-compare": lambda: _save(figure_theme_compare(), "theme-compare.png"),
        "architecture": lambda: figure_diagram("architecture", "architecture.png"),
        "widget-anatomy": lambda: figure_diagram("widget-anatomy", "widget-anatomy.png"),
        "theme-flow": lambda: figure_diagram("theme-flow", "theme-flow.png"),
        "event-flow": lambda: figure_diagram("event-flow", "event-flow.png"),
        "svg-pipeline": lambda: figure_diagram("svg-pipeline", "svg-pipeline.png"),
    }
    for name in wanted:
        producers[name]()

    sample = os.path.join(HERE, "_sample_image.png")
    if os.path.exists(sample):
        os.remove(sample)
    return 0


def _save(image, name: str):
    if image is None:
        print(f"  跳过 {name}：没有内容")
        return None
    path = os.path.join(ASSETS, name)
    image.save(path)
    print(f"  {image.width}x{image.height} -> assets/{name}")
    return path


if __name__ == "__main__":
    raise SystemExit(main())
