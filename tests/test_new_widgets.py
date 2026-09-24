"""新组件（复选框 / 单选框 / 列表 / 导航栏）的行为回归。"""

from __future__ import annotations

import pytest

import tkflu
from tkflu.checkbox import FluCheckBox
from tkflu.litenav import FluLiteNav
from tkflu.listbox import FluListBox
from tkflu.radiobox import FluRadioBox

from conftest import requires_tk

pytestmark = requires_tk


def pump(root, times=6):
    for _ in range(times):
        root.update()


# ---------------------------------------------------------------------------
# FluCheckBox
# ---------------------------------------------------------------------------
class TestCheckBox:
    def test_defaults_and_toggle(self, window):
        box = FluCheckBox(window, text="启用")
        box.pack()
        pump(window)
        assert box.dcget("checked") is False
        box.invoke()
        assert box.dcget("checked") is True
        box.invoke()
        assert box.dcget("checked") is False

    def test_three_state_cycles(self, window):
        box = FluCheckBox(window, text="三态", three_state=True)
        box.pack()
        pump(window)
        seen = [box.dcget("checked")]
        for _ in range(3):
            box.invoke()
            seen.append(box.dcget("checked"))
        assert seen == [False, True, None, False], seen

    def test_two_state_never_goes_indeterminate(self, window):
        box = FluCheckBox(window, text="两态")
        box.pack()
        pump(window)
        for _ in range(5):
            box.invoke()
            assert box.dcget("checked") in (True, False)

    def test_command_fires_once_per_invoke(self, window):
        calls = []
        box = FluCheckBox(window, text="x", command=lambda: calls.append(box.checked))
        box.pack()
        pump(window)
        box.invoke()
        box.invoke()
        assert calls == [True, False]

    def test_disabled_ignores_invoke(self, window):
        calls = []
        box = FluCheckBox(
            window, text="x", state="disabled", command=lambda: calls.append(1)
        )
        box.pack()
        pump(window)
        box.invoke()
        assert calls == []
        assert box.dcget("checked") is False

    def test_graceful_roundtrip(self, window):
        box = FluCheckBox(window, text="x", checked=True)
        box.pack()
        pump(window)
        for mode in ("dark", "light"):
            box.theme(mode=mode)
            pump(window, 2)
        assert box.dcget("checked") is True

    def test_auto_width_grows_with_text(self, window):
        short = FluCheckBox(window, text="短")
        long = FluCheckBox(window, text="一段明显更长的标签文字")
        short.pack()
        long.pack()
        pump(window)
        assert long.winfo_reqwidth() > short.winfo_reqwidth()

    def test_auto_width_is_remembered_as_automatic(self, window):
        box = FluCheckBox(window, text="带宽度自适应的复选框")
        box.pack()
        pump(window)
        # 没传 width → 保持"自适应"模式，文字变长时会跟着变宽
        assert box._fixed_width is None
        before = box.winfo_reqwidth()
        box.dconfigure(text="一段明显更长的复选框标签文字内容")
        box._draw()
        pump(window)
        assert box.winfo_reqwidth() >= before

    def test_checked_property_and_set_checked(self, window):
        box = FluCheckBox(window, text="x")
        box.pack()
        pump(window)
        box.checked = True
        assert box.dcget("checked") is True
        box.set_checked(None)
        assert box.checked is None


# ---------------------------------------------------------------------------
# FluRadioBox
# ---------------------------------------------------------------------------
class TestRadioBox:
    def test_shared_variable_is_exclusive(self, window):
        import tkinter as tk

        var = tk.StringVar(master=window, value="a")
        radios = [
            FluRadioBox(window, text=key, variable=var, value=key)
            for key in ("a", "b", "c")
        ]
        for radio in radios:
            radio.pack()
        pump(window)
        assert [r.checked for r in radios] == [True, False, False]

        radios[2].invoke()
        pump(window)
        assert [r.checked for r in radios] == [False, False, True]
        assert var.get() == "c"

    def test_group_name_shares_a_variable(self, window):
        radios = [
            FluRadioBox(window, text=key, group="plan", value=key)
            for key in ("x", "y")
        ]
        for radio in radios:
            radio.pack()
        pump(window)
        radios[0].invoke()
        pump(window)
        radios[1].invoke()
        pump(window)
        assert [r.checked for r in radios] == [False, True]

    def test_group_registry_is_released_on_destroy(self, window):
        from tkflu.radiobox import _GROUP_VARS

        before = len(_GROUP_VARS)
        root2 = tkflu.FluWindow()
        root2.withdraw()
        radio = FluRadioBox(root2, text="a", group="solo", value="a")
        radio.pack()
        pump(root2)
        assert len(_GROUP_VARS) == before + 1
        root2.destroy()
        assert len(_GROUP_VARS) == before

    def test_invoke_on_checked_is_a_noop(self, window):
        calls = []
        radio = FluRadioBox(window, text="a", value="a", command=lambda: calls.append(1))
        radio.pack()
        pump(window)
        radio.invoke()
        radio.invoke()
        assert len(calls) == 1

    def test_only_the_newly_selected_radio_notifies(self, window):
        import tkinter as tk

        var = tk.StringVar(master=window, value="a")
        calls = []
        for key in ("a", "b"):
            FluRadioBox(
                window,
                text=key,
                variable=var,
                value=key,
                command=lambda k=key: calls.append(k),
            ).pack()
        pump(window)
        calls.clear()
        var.set("b")
        pump(window)
        assert calls == ["b"], calls

    def test_variable_and_group_are_mutually_exclusive(self, window):
        import tkinter as tk

        with pytest.raises(ValueError):
            FluRadioBox(
                window, text="x", variable=tk.StringVar(master=window), group="g"
            )


# ---------------------------------------------------------------------------
# FluListBox
# ---------------------------------------------------------------------------
class TestListBox:
    def test_data_operations(self, window):
        box = FluListBox(window, items=["a", "b", "c"])
        box.pack()
        pump(window)
        assert len(box) == 3
        assert box.get(1) == "b"
        assert box.index("c") == 2
        assert box.index("zzz") is None

        box.insert(1, "new")
        assert box.items() == ["a", "new", "b", "c"]
        box.append("tail")
        assert box.items()[-1] == "tail"
        box.delete_item(0)
        assert box.items() == ["new", "b", "c", "tail"]
        box.remove(0)
        assert box.items() == ["b", "c", "tail"]
        box.clear()
        assert len(box) == 0

    def test_insert_keeps_selection_on_the_same_item(self, window):
        box = FluListBox(window, items=["a", "b", "c"])
        box.pack()
        pump(window)
        box.select(1)
        box.insert(0, "new")
        assert box.get(box.selection()[0]) == "b"

    def test_delete_adjusts_selection(self, window):
        box = FluListBox(window, items=["a", "b", "c", "d"])
        box.pack()
        pump(window)
        box.select(3)
        box.delete_item(0)
        assert box.get(box.selection()[0]) == "d"

    def test_get_raises_on_bad_index(self, window):
        box = FluListBox(window, items=["a"])
        box.pack()
        pump(window)
        with pytest.raises(IndexError):
            box.get(5)

    @pytest.mark.parametrize("mode", ["single", "multiple", "extended"])
    def test_select_modes(self, window, mode):
        box = FluListBox(window, items=[str(i) for i in range(6)], selectmode=mode)
        box.pack()
        pump(window)
        box.select(1)
        box.select(3)
        if mode == "single":
            assert box.selection() == (3,)
        else:
            assert box.selection() == (1, 3)

    def test_invalid_selectmode_raises(self, window):
        with pytest.raises(ValueError):
            FluListBox(window, selectmode="bogus")

    def test_command_is_arity_tolerant(self, window):
        """回调按 Tk 的惯例拿 ``(index, item)``，但只写很少参数的老代码也不能崩。

        参数是**按位置**给的，所以单参数回调拿到的是 ``index``。
        """
        zero = []
        one = []
        two = []
        box = FluListBox(window, items=["only"], command=lambda: zero.append(1))
        box.pack()
        pump(window)
        box.activate(0)
        assert zero == [1]

        box.dconfigure(command=lambda index: one.append(index))
        box.activate(0)
        assert one == [0]

        box.dconfigure(command=lambda index, item: two.append((index, item)))
        box.activate(0)
        assert two == [(0, "only")]

        starred = []
        box.dconfigure(command=lambda *args: starred.append(args))
        box.activate(0)
        assert starred == [(0, "only")]

    def test_on_select_fires_only_when_selection_changes(self, window):
        seen = []
        box = FluListBox(
            window, items=["a", "b"], on_select=lambda idx, items: seen.append(idx)
        )
        box.pack()
        pump(window)
        box.select(0)
        box.select(0)
        assert seen == [(0,)]

    def test_rolling_and_clamping(self, window):
        box = FluListBox(window, width=200, height=160, items=list(range(40)))
        box.pack()
        pump(window)
        assert box.yview()[0] == 0.0
        box.scroll(5)
        assert box._offset == 5
        box.scroll(-100)
        assert box._offset == 0
        box.scroll(10_000)
        assert box._offset == box._max_offset()
        box.yview_moveto(0)
        assert box._offset == 0

    def test_see_scrolls_into_view(self, window):
        box = FluListBox(window, width=200, height=160, items=list(range(40)))
        box.pack()
        pump(window)
        box.see(30)
        assert box._offset <= 30 <= box._offset + box._visible_rows()
        box.see(0)
        assert box._offset == 0

    def test_wheel_scrolls(self, window):
        box = FluListBox(window, width=200, height=160, items=list(range(40)))
        box.pack()
        pump(window)

        class Event:
            num = None

        # 滚轮向下（Windows 上是 -120）→ 列表往下滚
        down = Event()
        down.delta = -120
        box._event_wheel(down)
        assert box._offset > 0
        # 再往下滚一点，避免贴着 0 边界
        box._event_wheel(down)
        offset = box._offset
        # 滚轮向上（+120）→ 往回滚
        up = Event()
        up.delta = 120
        box._event_wheel(up)
        assert box._offset < offset

        # X11 用 Button-4 / Button-5，没有 delta
        x11_up = Event()
        x11_up.num = 4
        before = box._offset
        box._event_wheel(x11_up)
        assert box._offset < before
        x11_down = Event()
        x11_down.num = 5
        before = box._offset
        box._event_wheel(x11_down)
        assert box._offset > before

    def test_keyboard_moves_selection(self, window):
        box = FluListBox(window, items=[str(i) for i in range(20)])
        box.pack()
        pump(window)
        box._move_selection(1)
        assert box.selection() == (0,)
        box._move_selection(2)
        assert box.selection() == (2,)
        box._move_selection_to(19)
        assert box.selection() == (19,)

    def test_click_selects_the_row_under_the_cursor(self, window):
        box = FluListBox(window, width=200, height=160, items=list(range(20)))
        box.pack()
        pump(window)

        class Event:
            state = 0
            x = 40

        event = Event()
        # 行高跟着组件的常量走，别再写死 32（设计稿对齐后是 40）
        event.y = 1 + box.ITEM_HEIGHT * 2 + 5
        assert box._row_at(event.y) == 2
        box._event_on_button1(event)
        assert box.selection() == (2,)

    def test_click_outside_any_row_is_ignored(self, window):
        box = FluListBox(window, width=200, height=160, items=list(range(20)))
        box.pack()
        pump(window)
        assert box._row_at(-5) is None
        assert box._row_at(2) == 0
        assert box._row_at(10_000) is None

    def test_disabled_click_does_nothing(self, window):
        box = FluListBox(window, items=["a"], state="disabled")
        box.pack()
        pump(window)

        class Event:
            state = 0
            x = 10
            y = 5

        box._event_on_button1(Event())
        assert box.selection() == ()

    def test_empty_state_shows_the_placeholder(self, window):
        box = FluListBox(window, text="这里空空如也", width=200)
        box.pack()
        pump(window)
        kinds = [box.type(i) for i in box.find_all()]
        assert "text" in kinds

        box.insert("end", "有内容了")
        pump(window)
        texts = [box.itemcget(i, "text") for i in box.find_all() if box.type(i) == "text"]
        assert "有内容了" in texts
        assert "这里空空如也" not in texts

    def test_legacy_text_only_keeps_the_short_height(self, window):
        legacy = FluListBox(window, text="FluListBox", width=120)
        legacy.pack()
        pump(window)
        # 老写法（只给 text）保持历史的高度 32
        assert legacy.winfo_reqheight() == 32
        assert len(legacy) == 0

    def test_new_list_defaults_to_a_readable_height(self, window):
        box = FluListBox(window, items=["a"])
        box.pack()
        pump(window)
        assert box.winfo_reqheight() == 160

    def test_theme_switch_is_safe_without_style(self, window):
        box = FluListBox(window, items=["a", "b"])
        box.pack()
        pump(window)
        box.theme(mode="dark")
        box.theme(mode="light")
        box.theme()
        assert box.mode == "light"

    def test_delete_is_not_shadowed(self, window):
        """``delete`` 必须还是画布语义，否则重绘会递归调用自己。"""
        box = FluListBox(window, items=["a"])
        box.pack()
        pump(window)
        box.delete("all")  # 画布语义：清空画布元素
        assert box.find_all() == ()
        box._draw()
        assert box.find_all()  # 重绘后又有内容，且没有 RecursionError

    def test_scrollbar_geometry_only_when_needed(self, window):
        few = FluListBox(window, width=200, height=160, items=["a"])
        few.pack()
        pump(window)
        assert few._scrollbar_geometry() is None

        many = FluListBox(window, width=200, height=160, items=list(range(50)))
        many.pack()
        pump(window)
        assert many._scrollbar_geometry() is not None


# ---------------------------------------------------------------------------
# FluLiteNav
# ---------------------------------------------------------------------------
class TestLiteNav:
    def test_items_are_normalised(self, window):
        nav = FluLiteNav(
            window,
            items=[
                "只有标签",
                ("★", "图标+标签"),
                {"label": "字典", "key": "k", "enabled": False},
            ],
        )
        nav.pack()
        pump(window)
        assert len(nav) == 3
        assert nav.get_item(0)["label"] == "只有标签"
        assert nav.get_item(1)["icon"] == "★"
        assert nav.get_item(2)["key"] == "k"
        assert nav.get_item(2)["enabled"] is False

    def test_bad_item_shape_raises(self, window):
        with pytest.raises(TypeError):
            FluLiteNav(window, items=[(1, 2, 3)])

    def test_bad_orient_and_style_raise(self, window):
        with pytest.raises(ValueError):
            FluLiteNav(window, orient="diagonal")
        with pytest.raises(ValueError):
            FluLiteNav(window, style="flat")

    def test_selection_by_index_and_key(self, window):
        nav = FluLiteNav(
            window,
            items=[{"label": "A", "key": "a"}, {"label": "B", "key": "b"}],
            selected="b",
        )
        nav.pack()
        pump(window)
        assert nav.selected() == 1
        assert nav.selected_key() == "b"

        assert nav.select("a") is True
        assert nav.selected() == 0
        assert nav.select("a") is False  # 重复选中
        assert nav.select("missing") is False

    def test_disabled_item_cannot_be_selected(self, window):
        nav = FluLiteNav(
            window,
            items=[{"label": "A", "key": "a"}, {"label": "B", "key": "b", "enabled": False}],
        )
        nav.pack()
        pump(window)
        assert nav.select("b") is False
        assert nav.selected() == -1

    def test_keyboard_skips_disabled_items(self, window):
        nav = FluLiteNav(
            window,
            items=[
                {"label": "A", "key": "a"},
                {"label": "B", "key": "b", "enabled": False},
                {"label": "C", "key": "c"},
            ],
        )
        nav.pack()
        pump(window)
        nav.select("a")
        nav._move(1)
        assert nav.selected_key() == "c"
        nav._move(-1)
        assert nav.selected_key() == "a"

    def test_command_receives_index_and_item(self, window):
        seen = []
        nav = FluLiteNav(
            window,
            items=["A", "B"],
            command=lambda index, item: seen.append((index, item["label"])),
        )
        nav.pack()
        pump(window)
        assert nav.select(1) is True
        assert seen == [(1, "B")]
        # 再选一次同一个：不重复触发
        assert nav.select(1) is False
        assert seen == [(1, "B")]

    def test_item_level_command_wins(self, window):
        seen = []
        nav = FluLiteNav(
            window,
            items=[{"label": "A", "command": lambda index, item: seen.append("item")}],
            command=lambda index, item: seen.append("widget"),
        )
        nav.pack()
        pump(window)
        nav.select(0)
        assert seen == ["item"]

    def test_add_configure_remove_clear(self, window):
        nav = FluLiteNav(window, items=["A"])
        nav.pack()
        pump(window)
        position = nav.add_item("B", icon="★", key="b")
        assert position == 1 and len(nav) == 2
        nav.add_item("C", key="c", index=0)
        assert nav.get_item(0)["label"] == "C"
        nav.configure_item("b", label="B2")
        assert nav.get_item("b") and nav.get_item(2)["label"] == "B2"
        nav.remove_item("c")
        assert len(nav) == 2
        nav.clear()
        assert len(nav) == 0 and nav.selected() == -1

    def test_bad_item_index_raises(self, window):
        nav = FluLiteNav(window, items=["A"])
        nav.pack()
        pump(window)
        with pytest.raises(IndexError):
            nav.get_item(9)

    def test_remove_item_leaves_callable_widget(self, window):
        nav = FluLiteNav(window, items=["A", "B", "C"])
        nav.pack()
        pump(window)
        nav.destroy()  # 不该抛异常

    def test_hit_test_uses_item_geometry(self, window):
        nav = FluLiteNav(window, items=["A", "B"], orient="horizontal")
        nav.pack()
        pump(window)
        assert nav._hit_index(2, 10) == 0
        assert nav._hit_index(-5, 10) is None
        assert nav._hit_index(2, 1000) is None

    def test_theme_and_mode_roundtrip(self, window):
        nav = FluLiteNav(window, items=["A"], style="card", mode="light")
        nav.pack()
        pump(window)
        nav.theme(mode="dark")
        assert nav.mode == "dark"
        nav.theme(mode="light", style="standard")
        assert nav.style == "standard"
        pump(window, 2)
        nav._draw()
        assert nav.find_all()
