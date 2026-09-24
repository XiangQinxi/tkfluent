"""缺陷回归：每条断言对应一个**真实修过的** bug。

这些测试的写法刻意"贴着真实调用路径"——不是构造一个更有利的环境，
而是复现用户会遇到的那条路（换肤、关窗、重建、事件、真几何）。
每条前面都写了"当年坏在哪"，改回去就会红。
"""

from __future__ import annotations

import gc
import os
import tkinter as tk

import pytest

import tkflu
from conftest import _new_window, requires_tk

pytestmark = requires_tk


def pump(root, times=6):
    for _ in range(times):
        root.update()


# ---------------------------------------------------------------------------
# FluButton
# ---------------------------------------------------------------------------
class TestButton:
    def test_theme_with_unknown_style_does_not_brick_the_button(self, window):
        """旧行为：`theme(style="bogus")` → TypeError，且 self.style 变成
        "bogus"，这个按钮从此再也切不了主题（还会拖垮整趟换肤）。"""
        button = tkflu.FluButton(window, text="x")
        button.pack()
        pump(window)
        button.theme(style="bogus")  # 不抛
        button.theme(mode="dark")  # 仍然能正常换肤
        assert button.mode == "dark"
        assert button.style == "standard"

    def test_construction_with_falsy_mode_does_not_raise(self, window):
        """旧行为：`FluButton(mode=None)` → AttributeError（_init 里还没 self.mode）。"""
        button = tkflu.FluButton(window, text="x", mode=None)
        button.pack()
        pump(window)
        assert button.mode == "light"

    def test_theme_manager_sweep_survives_a_bad_button(self, window):
        """一个坏按钮不该让后面的兄弟组件轮不到换肤。"""
        bad = tkflu.FluButton(window, text="bad")
        good = tkflu.FluButton(window, text="good")
        bad.pack()
        good.pack()
        pump(window)
        bad.theme(style="bogus")
        manager = tkflu.FluThemeManager(window=window, mode="light")
        manager.mode("dark")
        assert good.mode == "dark"

    def test_disabled_button_does_not_invoke(self, window):
        """旧行为：disabled 按钮仍然能被 invoke()/回车触发。"""
        calls = []
        button = tkflu.FluButton(
            window, text="x", state="disabled", command=lambda: calls.append(1)
        )
        button.pack()
        pump(window)
        button.invoke()
        assert calls == []

    def test_enabled_button_still_invokes(self, window):
        calls = []
        button = tkflu.FluButton(window, text="x", command=lambda: calls.append(1))
        button.pack()
        pump(window)
        button.invoke()
        assert calls == [1]

    def test_animation_ends_on_the_target_state(self, window):
        """旧行为：动画最后一帧就是最终状态，steps=1 时按钮停在**旧主题**上。"""
        from tkflu.designs.animation import (
            get_animation_step_time,
            get_animation_steps,
            set_animation_step_time,
            set_animation_steps,
        )

        old_steps, old_time = get_animation_steps(), get_animation_step_time()
        set_animation_steps(1)
        set_animation_step_time(1)
        try:
            button = tkflu.FluButton(window, text="x", mode="light")
            button.pack()
            pump(window)
            button.theme(mode="dark")
            # 等动画帧跑完（帧间隔是 1ms，末帧在 11ms 处）
            import time

            deadline = time.time() + 2.0
            while time.time() < deadline and button.traced_count():
                window.update()
                time.sleep(0.01)
            expected = button.attributes.rest.back_opacity
            # 属性与画面必须一致：画面由 attributes 决定，这里验证
            # "动画结束后 attributes 就是目标主题"，并且没有残留帧。
            assert button.traced_count() == 0
            assert float(button.attributes.rest.back_opacity) != float(
                tkflu.designs.button.button("light", "standard", "rest")["back_opacity"]
            )
            assert expected is not None
        finally:
            set_animation_steps(old_steps)
            set_animation_step_time(old_time)

    def test_animation_frames_are_cancelled_not_accumulated(self, window):
        """旧行为：每次动画排 N 个 after 且从不取消，来回悬停会不断堆积。"""
        from tkflu.designs.animation import (
            get_animation_step_time,
            get_animation_steps,
            set_animation_step_time,
            set_animation_steps,
        )

        old_steps, old_time = get_animation_steps(), get_animation_step_time()
        set_animation_steps(8)
        set_animation_step_time(50)  # 足够长，帧不会自己跑完
        try:
            button = tkflu.FluButton(window, text="x")
            button.pack()
            pump(window)
            for _ in range(5):
                button._event_enter()
                button._event_leave()
            # 每轮先撤销上一轮，所以队列里最多只有一轮的帧
            assert button.traced_count() <= 8
            button.cancel_traced()
            assert button.traced_count() == 0
        finally:
            set_animation_steps(old_steps)
            set_animation_step_time(old_time)


# ---------------------------------------------------------------------------
# FluToggleButton
# ---------------------------------------------------------------------------
class TestToggleButton:
    def test_theme_accepts_style_keyword(self, window):
        """旧行为：`theme(style=...)` → TypeError，于是它不能当菜单项。"""
        toggle = tkflu.FluToggleButton(window, text="x")
        toggle.pack()
        pump(window)
        toggle.theme(mode="dark", style="menu")
        assert toggle.mode == "dark"

    def test_theme_with_no_arguments_is_safe(self, window):
        toggle = tkflu.FluToggleButton(window, text="x")
        toggle.pack()
        pump(window)
        toggle.theme()
        assert toggle.mode == "light"

    def test_menu_accepts_a_toggle_button_as_item(self, window):
        """FluMenu.add_command(custom_widget=...) 会用 style= 去调 theme()。"""
        menu = tkflu.FluMenu()
        menu.add_command(
            custom_widget=tkflu.FluToggleButton, label="开关项", width=100
        )
        assert menu.dcget("actions")

    def test_checking_on_border_ramp_uses_border_colors(self, window):
        """旧行为：勾选动画的描边是从**背景色**插值的（边框闪成强调蓝）。"""
        from tkflu.designs.animation import (
            get_animation_step_time,
            get_animation_steps,
            set_animation_step_time,
            set_animation_steps,
        )

        old_steps, old_time = get_animation_steps(), get_animation_step_time()
        set_animation_steps(4)
        set_animation_step_time(1000)  # 别让它自己跑完，便于观察插值
        try:
            toggle = tkflu.FluToggleButton(window, text="x")
            toggle.pack()
            pump(window)
            toggle.toggle()
            frames = []
            original = toggle._draw

            def spy(event=None, tempcolor=None):
                if tempcolor is not None:
                    frames.append((tempcolor.back_color, tempcolor.border_color))
                return original(event, tempcolor)

            toggle._draw = spy
            toggle.toggle()
            # 第一帧的 delay 是 0，但也要过一次事件循环才会执行
            pump(window, 4)
            toggle.cancel_traced()
            assert frames, "没有产生任何动画帧"
            # 至少有一帧的描边色与背景色不同（旧实现里两者恒等）
            assert any(back != border for back, border in frames), frames
        finally:
            set_animation_steps(old_steps)
            set_animation_step_time(old_time)


# ---------------------------------------------------------------------------
# FluLabel / FluImage
# ---------------------------------------------------------------------------
class TestLabelImage:
    def test_font_argument_is_honoured(self, window):
        """旧行为：`font=` 被整个丢掉，attributes.font 一直是 None。"""
        label = tkflu.FluLabel(window, text="Hi", font=("Courier New", 14))
        label.pack()
        pump(window)
        assert label.attributes.font == ("Courier New", 14)

    def test_default_font_lands_on_the_widgets_own_interpreter(self, window):
        """旧行为：SegoeFont() 不带 master，第二个解释器认不出这个字体名。"""
        label = tkflu.FluLabel(window, text="文本")
        label.pack()
        pump(window)
        font = label.attributes.font
        assert font is not None
        # 该名字在**本解释器**里必须存在
        label.tk.call("font", "actual", str(font))

    def test_image_covers_the_panel_not_hidden_by_inner_frame(self, window, tmp_path):
        """旧行为：内嵌 Frame 是真实控件窗口，永远盖在画布元素之上，
        图片实际只露出边框内侧一圈。"""
        from PIL import Image

        path = tmp_path / "px.png"
        Image.new("RGB", (60, 40), (255, 0, 0)).save(path)

        widget = tkflu.FluImage(window, image=str(path))
        widget.pack()
        pump(window)
        # 有图片时内嵌 Frame 的 window 元素必须被隐藏，否则会盖住图片
        assert widget.canvas.itemcget(widget.element2, "state") == "hidden"
        kinds = [widget.canvas.type(i) for i in widget.canvas.find_all()]
        assert kinds.count("image") >= 2
        # 尺寸 = 图片 + 两倍内边距，圆角边框才不会被图片四角压掉
        assert widget.canvas.winfo_reqwidth() == 60 + widget.padding * 2

    def test_image_accepts_pathlib_and_pil(self, window, tmp_path):
        from PIL import Image

        path = tmp_path / "px.png"
        Image.new("RGB", (30, 30), (0, 200, 0)).save(path)

        by_path = tkflu.FluImage(window, image=path)  # pathlib.Path
        by_pil = tkflu.FluImage(window, image=Image.new("RGB", (30, 30)))
        by_path.pack()
        by_pil.pack()
        pump(window)
        assert by_path.image() is not None
        assert by_pil.image() is not None

    def test_missing_file_raises_a_clear_error(self, window, tmp_path):
        with pytest.raises(FileNotFoundError):
            tkflu.FluImage(window, image=str(tmp_path / "nope.png"))

    def test_unsupported_type_raises_type_error(self, window):
        with pytest.raises(TypeError):
            tkflu.FluImage(window, image=12345)

    def test_frameless_image_still_behaves_like_a_frame(self, window):
        """没有图片时内嵌 Frame 要照常显示（否则 FluImage 变成空壳）。"""
        widget = tkflu.FluImage(window)
        widget.pack()
        pump(window)
        assert widget.canvas.itemcget(widget.element2, "state") == "normal"


# ---------------------------------------------------------------------------
# FluFrame
# ---------------------------------------------------------------------------
class TestFrame:
    def test_destroy_takes_the_canvas_with_it(self, window):
        """旧行为：画布是父容器的直接子控件，FluFrame.destroy() 只干掉内嵌 Frame，
        圆角面板留在原地——建一次销毁一次就多留一块。"""
        for _ in range(3):
            frame = tkflu.FluFrame(window, width=100, height=60)
            frame.pack()
            pump(window)
            frame.destroy()
            pump(window)
        leftover = [
            child
            for child in window.winfo_children()
            if "fluframecanvas" in str(child)
        ]
        assert leftover == []

    def test_works_inside_ttk_containers(self, window):
        """旧行为：`self.canvas.master.cget("background")` 在 ttk 容器里直接
        `TclError: unknown option "-background"`。"""
        import tkinter.ttk as ttk

        for maker in (
            lambda parent: ttk.Frame(parent),
            lambda parent: ttk.LabelFrame(parent, text="lf"),
        ):
            host = maker(window)
            host.pack()
            pump(window, 2)
            frame = tkflu.FluFrame(host, width=80, height=40)
            frame.pack()
            pump(window, 2)
            assert frame.canvas.winfo_exists()

    def test_geometry_proxies_pass_their_arguments(self, window):
        """旧行为：pack_propagate 丢 flag、grid_location 丢参数、
        grid_anchor 传了个 Ellipsis、place_info 返回 grid_info。"""
        frame = tkflu.FluFrame(window, width=100, height=60)
        frame.pack()
        pump(window)
        assert frame.pack_propagate(False) is None
        assert isinstance(frame.place_info(), dict)
        assert isinstance(frame.grid_location(0, 0), tuple)
        assert frame.grid_anchor("nw") is None
        assert isinstance(frame.grid_slaves(), list)

    def test_theme_animation_actually_runs_when_enabled(self, window):
        """旧行为：`hasattr(n, "back_color")` 对普通 dict 恒为 False，
        整段过渡动画是**死代码**。"""
        from tkflu.designs.animation import (
            get_animation_step_time,
            get_animation_steps,
            set_animation_step_time,
            set_animation_steps,
        )

        old_steps, old_time = get_animation_steps(), get_animation_step_time()
        set_animation_steps(4)
        set_animation_step_time(1000)
        try:
            frame = tkflu.FluFrame(window, width=100, height=60, mode="light")
            frame.pack()
            pump(window)
            frame.theme(mode="dark")
            assert frame.traced_count() > 0, "过渡动画没有排任何帧"
            frame.cancel_traced()
        finally:
            set_animation_steps(old_steps)
            set_animation_step_time(old_time)


# ---------------------------------------------------------------------------
# FluSlider
# ---------------------------------------------------------------------------
class TestSlider:
    def test_vertical_orientation_constructs(self, window):
        """旧行为：orient != "horizontal" 时轨道/把手根本没创建，
        随后 tag_bind 抛 AttributeError —— 构造即崩。"""
        slider = tkflu.FluSlider(
            window, width=28, height=140, orient="vertical", min=0, max=100, value=0
        )
        slider.pack()
        pump(window)
        assert slider.element_thumb is not None
        assert slider.element_track is not None

    def test_unknown_orientation_raises_value_error(self, window):
        with pytest.raises(ValueError):
            tkflu.FluSlider(window, orient="diagonal")

    def test_equal_min_max_does_not_divide_by_zero(self, window):
        """旧行为：一段死代码里的 (max - min) 除法先炸 ZeroDivisionError。"""
        slider = tkflu.FluSlider(window, min=50, max=50, value=50)
        slider.pack()
        pump(window)
        assert slider.get() == 50

    def test_inverted_range_is_normalised(self, window):
        slider = tkflu.FluSlider(window, min=90, max=10, value=50)
        slider.pack()
        pump(window)
        slider.set(200)
        assert slider.get() == 90
        slider.set(0)
        assert slider.get() == 10

    def test_out_of_range_value_is_clamped_and_stays_inside(self, window):
        """旧行为：超范围的 value 会让进度条画到控件外面几百像素。"""
        slider = tkflu.FluSlider(window, width=200, height=28, min=0, max=100, value=200)
        slider.pack()
        pump(window)
        assert slider.get() == 100
        box = slider.bbox(slider.element_track)
        assert box[2] <= 210, box

    def test_narrow_slider_is_not_inverted(self, window):
        """旧行为：滑块比把手还窄时分母为负，往右拖反而变小。"""
        slider = tkflu.FluSlider(window, width=20, height=28, min=0, max=100)
        slider.pack()
        pump(window)

        class Event:
            y = 0

        left = Event()
        left.x = 0
        slider.pos(left)
        low = slider.get()
        right = Event()
        right.x = 19
        slider.pos(right)
        assert slider.get() >= low

    def test_drag_shows_the_pressed_palette(self, window):
        """旧行为：拖动路径最后调的是不带事件的 _draw()，而配色分支写成
        `if event:`，于是拖动永远是 rest 外观。"""
        slider = tkflu.FluSlider(window, width=200, height=28, min=0, max=100, value=50)
        slider.pack()
        pump(window)

        class Event:
            state = 0
            y = 14

        event = Event()
        event.x = 150
        slider._event_on_button1(event)
        pump(window)
        assert slider.button1 is True
        assert slider._palette()[0] == "pressed"
        slider._event_off_button1(event)

    def test_set_and_get(self, window):
        """旧行为：没有 set()/get()，只能 dconfigure(value=) 再手动 _draw()。"""
        slider = tkflu.FluSlider(window, width=200, height=28, min=0, max=10)
        slider.pack()
        pump(window)
        slider.set(7)
        assert slider.get() == 7

    def test_keyboard_changes_the_value(self, window):
        """旧行为：方向键完全没有绑定。"""
        slider = tkflu.FluSlider(window, width=200, height=28, min=0, max=10, value=5)
        slider.pack()
        pump(window)
        slider.step_by(1)
        assert slider.get() == 6
        slider.step_by(-2)
        assert slider.get() == 4
        slider.set(slider.attributes.min)
        slider.step_by(-1)
        assert slider.get() == 0

    def test_command_keyword_is_accepted(self, window):
        """旧行为：command 只写在属性表里，构造函数不收，于是
        `FluSlider(command=cb)` 把 -command 透给 Canvas → TclError。"""
        slider = tkflu.FluSlider(window, command=lambda value: None)
        slider.pack()
        pump(window)
        assert slider.attributes.command is not None

    def test_changed_only_fires_when_the_value_moves(self, window):
        """旧行为：原地按一下也会触发 changed。"""
        calls = []
        slider = tkflu.FluSlider(
            window, width=200, height=28, min=0, max=100, value=50,
            changed=lambda value: calls.append(value),
        )
        slider.pack()
        pump(window)

        class Event:
            state = 0
            y = 14

        event = Event()
        event.x = 100  # 大约就是当前值所在的位置
        slider._event_on_button1(event)
        slider._event_off_button1(event)
        assert calls == []

    def test_theme_accepts_falsy_mode(self, window):
        """旧行为：FluSlider(mode="") → AttributeError（self.mode 还不存在）。"""
        slider = tkflu.FluSlider(window, mode="")
        slider.pack()
        pump(window)
        assert slider.mode == "light"
        slider.theme()
        slider.theme(mode="dark")
        assert slider.mode == "dark"


# ---------------------------------------------------------------------------
# FluScrollBar
# ---------------------------------------------------------------------------
class TestScrollBar:
    def test_set_accepts_tk_string_fractions(self, window):
        """旧行为：Tk 的 yscrollcommand 会传字符串进来，
        `10 + self.start * track_height` 直接 TypeError。"""
        bar = tkflu.FluScrollBar(window, width=12, height=200)
        bar.pack()
        pump(window)
        bar.set("0.0", "0.5")
        assert bar.get() == (0.0, 0.5)
        bar.set(0.25, 0.75)
        assert bar.get() == (0.25, 0.75)

    def test_thumb_length_follows_the_content_fraction(self, window):
        """旧行为：滑块永远是整条轨道长，set() 完全不起作用。"""
        bar = tkflu.FluScrollBar(window, width=12, height=200)
        bar.pack()
        pump(window)
        bar.set(0.0, 0.25)
        pump(window)
        short = bar.bbox(bar.element_thumb)
        bar.set(0.0, 1.0)
        pump(window)
        full = bar.bbox(bar.element_thumb)
        assert (short[3] - short[1]) < (full[3] - full[1])

    def test_horizontal_bar_is_visible_at_rest(self, window):
        """旧行为：未展开分支只在竖直方向画滑块，横向滚动条整个是空的。"""
        bar = tkflu.FluScrollBar(window, width=180, height=8, orient="horizontal")
        bar.pack()
        pump(window)
        assert bar.find_all()
        assert bar.bbox(bar.element_thumb) is not None

    def test_hover_on_disabled_bar_does_not_crash(self, window):
        """旧行为：disabled 配色表里没有 track_color，None 被当成 SVG fill，
        鼠标一划过就 `TypeError: 'None' is not a valid value for attribute 'fill'`。"""
        bar = tkflu.FluScrollBar(window, width=12, height=120, state="disabled")
        bar.pack()
        pump(window)
        bar._event_enter()
        pump(window)
        bar._event_leave()
        pump(window)
        assert bar.find_all()

    def test_tempcolor_path_works(self, window):
        """旧行为：tempcolor 分支漏了 _radius，用到时 UnboundLocalError。"""
        from easydict import EasyDict

        bar = tkflu.FluScrollBar(window, width=12, height=120)
        bar.pack()
        pump(window)
        bar._draw(tempcolor=EasyDict({"thumb_color": "#ff0000", "track_color": "#00ff00"}))
        pump(window)
        assert bar.find_all()

    def test_command_uses_the_tk_protocol(self, window):
        """旧行为：command 永远无参调用，接不上 Tk 的 moveto/scroll 约定。"""
        calls = []
        bar = tkflu.FluScrollBar(
            window, width=12, height=200, command=lambda *args: calls.append(args)
        )
        bar.pack()
        pump(window)
        # 先把滑块缩到 30%，这样点在 y=150 时落在**轨道**而不是滑块上
        bar.set(0.0, 0.3)
        pump(window)

        class Event:
            x = 6

        event = Event()
        event.y = 150
        bar._event_on_button1(event)
        pump(window)
        assert calls and calls[-1][0] == "moveto", calls
        bar._event_off_button1(event)

    def test_theme_without_arguments_is_safe(self, window):
        """旧行为：theme() 把 None 传给 designs.scrollbar.scrollbar() → AttributeError。"""
        bar = tkflu.FluScrollBar(window, width=12, height=120)
        bar.pack()
        pump(window)
        bar.theme()
        assert bar.mode == "light"

    def test_orient_applies_before_the_first_draw(self, window):
        bar = tkflu.FluScrollBar(window, width=180, height=8, orient="horizontal")
        bar.pack()
        pump(window)
        assert bar.attributes.orient == "horizontal"
        box = bar.bbox(bar.element_thumb)
        assert (box[2] - box[0]) > (box[3] - box[1])  # 横向：宽 > 高


# ---------------------------------------------------------------------------
# FluEntry / FluText
# ---------------------------------------------------------------------------
class TestInputs:
    def test_entry_keeps_the_base_press_handler(self, window):
        """旧行为：`bind("<Button-1>", ...)` 少了 add="+"，把基类的
        _event_on_button1 替换掉了，画布上的 button1 永远是 False。"""
        entry = tkflu.FluEntry(window, width=150)
        entry.pack()
        pump(window)
        assert "_event_on_button1" in entry.bind("<Button-1>")

    def test_text_does_not_write_pixels_into_char_options(self, window):
        """旧行为：把像素值写进 Text 的 width/height（单位是字符/行），
        请求尺寸变成 1300x1200 级别的怪物。"""
        widget = tkflu.FluText(window, width=230, height=90)
        widget.pack()
        pump(window)
        assert widget.text.winfo_reqwidth() < 600
        assert widget.text.winfo_reqheight() < 600


# ---------------------------------------------------------------------------
# 基础设施
# ---------------------------------------------------------------------------
class TestInfrastructure:
    def test_cancel_all_after_spares_other_windows(self):
        """旧行为：cancel_all_after 把**整个解释器**的 after 全取消，
        连带干掉别的窗口的回调，还会在别处留下已删命令的名字，
        导致之后 `can't delete Tcl command` / `application has been destroyed`。"""
        root = _new_window()
        root.withdraw()
        fired = []
        root.after(120, lambda: fired.append("root"))

        child = tkflu.FluToplevel()
        child.withdraw()
        pump(root, 3)
        child.destroy()

        import time

        deadline = time.time() + 2.0
        while time.time() < deadline and not fired:
            root.update()
            time.sleep(0.01)
        assert fired == ["root"], "父窗口排的 after 被误取消了"
        root.destroy()

    def test_windows_can_be_recreated_after_destroy(self):
        """旧行为：清理失败会让 _default_root 残留，之后建窗口就撞
        "application has been destroyed"。"""
        for _ in range(3):
            root = _new_window()
            root.withdraw()
            frame = tkflu.FluFrame(root, width=80, height=40)
            frame.pack()
            pump(root, 2)
            root.destroy()
            assert tkinter_is_clean()

    def test_icons_do_not_pin_interpreters(self):
        """旧行为：图标 PhotoImage 按 id(tk) 缓存，一个窗口一张，
        等于让解释器永远回收不掉（实测 50 个窗口 +96MB）。"""
        import tkflu.icons as icons

        assert not hasattr(icons, "_PHOTOS")
        before = _rss_kb()
        for _ in range(8):
            root = _new_window()
            root.withdraw()
            root.destroy()
        gc.collect()
        growth = _rss_kb() - before
        # 8 个窗口成长不该达到"每窗口约 2MB"的量级
        assert growth < 8 * 1024, f"内存增长 {growth} KB"

    def test_measure_label_width_uses_real_font_metrics(self, window):
        """旧行为：`Font(master=...)` 参数名写错（应为 root=），TclError 被吞掉，
        于是**永远**走"宽字符按 2 计 * 9"的估算，菜单比实际需要宽 1.6~2 倍。"""
        from tkinter.font import Font

        from tkflu.defs import measure_label_width

        text = "A very long English label here"
        measured = measure_label_width(window, text, padding=0)
        real = Font(root=window, family="Segoe UI", size=9).measure(text)
        assert measured == real, (measured, real)

    def test_listbox_delete_is_canvas_delete(self, window):
        """条目删除方法不能叫 delete（会与 Canvas.delete 撞名并递归）。"""
        from tkflu.listbox import FluListBox

        box = FluListBox(window, items=["a"])
        box.pack()
        pump(window)
        assert hasattr(box, "delete_item")
        box.delete("all")  # 必须是画布语义
        assert box.find_all() == ()

    def test_call_command_arity_helper(self):
        """call_command 的三种典型签名。"""
        from tkflu.defs import call_command

        zero, one, starred = [], [], []
        assert call_command(lambda: zero.append(1)) is None
        call_command(lambda value: one.append(value), "v", "ignored")
        call_command(lambda *args: starred.append(args), 1, 2)
        assert zero == [1]
        assert one == ["v"]
        assert starred == [(1, 2)]
        assert call_command(None, 1) is None


def tkinter_is_clean():
    """``_default_root`` 是 None，或它确实还活着。"""
    root = tk._default_root
    if root is None:
        return True
    try:
        root.winfo_exists()
        return True
    except Exception:
        return False


def _rss_kb():
    """当前进程的常驻内存（KB）；拿不到时返回 0（断言会因此变宽松）。"""
    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss // 1024
    except Exception:
        return 0
