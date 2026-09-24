"""pytest 公共夹具。

Tk 需要真实的窗口系统；没有桌面会话时**跳过**而不是失败——
与 ``tkdeft/benchmarks/check_layout.py`` 的处理保持一致
（在无头环境下断言布局是没有意义的，不是代码坏了）。
"""

from __future__ import annotations

import os
import sys

import pytest

# 允许直接 `pytest tests/` 而不用先 pip install -e .
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _tk_available() -> bool:
    """能否创建一个 Tk 根窗口。"""
    try:
        import tkinter

        root = tkinter.Tk()
    except Exception:
        return False
    root.destroy()
    return True


TK_AVAILABLE = _tk_available()

#: 无头环境下列上的标记
requires_tk = pytest.mark.skipif(
    not TK_AVAILABLE, reason="需要可用的 Tk（桌面会话）"
)

#: 五个渲染引擎；缺依赖的会被自动跳过
ENGINES = ("tksvg", "wand", "skia", "pillow", "cairo")


def _new_window():
    """建一个 ``FluWindow``；解释器一时起不来时重试几次。

    本机偶发（大约 5% 的概率）Tk 会抛
    ``TclError: Can't find a usable tk.tcl ... couldn't read file .../ttk/scale.tcl``
    ——这是**环境**问题（`C:\\Python\\Py313\\tcl\\tk8.6\\ttk` 里的文件一时读不到），
    不是库的缺陷。测试不该被它整片判红，所以重试 + 退让。
    """
    import time

    import tkflu

    last = None
    for attempt in range(3):
        try:
            return tkflu.FluWindow(mode="light")
        except Exception as exc:  # pragma: no cover - 环境相关
            last = exc
            time.sleep(0.2 * (attempt + 1))
    pytest.skip(f"Tk 解释器无法创建（环境问题）：{last}")


@pytest.fixture(scope="session")
def shared_root():
    """整个会话共用的**唯一**一个 Tcl 解释器（一个 ``FluWindow``）。

    为什么只留一个：每个 ``FluWindow`` 都建一个独立的 Tcl 解释器，
    而 Tk 解释器在 Windows 上会占掉一批文件句柄 / 映射资源。逐个测试各建一个
    （100+ 个）之后，再建新解释器时 Tk 会开始报

    .. code-block:: text

        TclError: Can't find a usable tk.tcl in the following directories:
        ... couldn't read file ".../tk8.6/ttk/scale.tcl": no such file or directory

    ——文件其实好好地躺在那儿，是资源被耗干了。这与库本身无关，
    但会让整套测试变成随机红。
    """
    root = _new_window()
    root.geometry("200x150+20+20")
    root.deiconify()
    for _ in range(10):
        root.update()
    yield root
    try:
        root.destroy()
    except Exception:
        pass
    import tkinter

    tkinter._default_root = None


@pytest.fixture
def window(shared_root):
    """每个测试一个**新鲜的 ``FluToplevel``**（共用上面那个解释器）。

    * 用 Toplevel 而不是根窗口：不新增解释器，也就不会把环境耗干；
    * 每个测试一个新窗口：控件不会在同一个窗口里越堆越多——堆到装不下时
      控件的 ``winfo_width()`` 会变成 1，所有跟几何有关的断言都会失效。

    刻意 ``deiconify`` 而不是 ``withdraw``：``withdraw`` 状态下子控件的
    ``winfo_width()`` 一律是 **1**。窗口映射不出来（无桌面会话）时跳过。
    """
    import tkflu

    child = tkflu.FluToplevel(master=shared_root, mode="light")
    child.geometry("460x560+40+40")
    child.deiconify()
    child.lift()
    for _ in range(20):
        shared_root.update()
    if not child.winfo_ismapped():
        child.destroy()
        pytest.skip("窗口未能映射（无桌面会话），无法测量真实几何")

    try:
        yield child
    finally:
        try:
            child.destroy()
        except Exception:
            pass


@pytest.fixture
def isolated_window():
    """一个**独占**的窗口（每个测试建、测试完销毁）。

    只有确实需要"干净解释器"的测试才用它——每用一次就多一个 Tk 解释器，
    别在普通测试里随便用。
    """
    root = _new_window()
    root.withdraw()
    try:
        yield root
    finally:
        try:
            root.destroy()
        except Exception:
            pass


@pytest.fixture
def engine(request):
    """按参数切换渲染引擎，测完恢复默认。"""
    import tkflu
    from tkdeft.engines import list_engines

    name = request.param
    if not list_engines().get(name):
        pytest.skip(f"引擎 {name} 在当前环境不可用（缺依赖）")
    previous = tkflu.get_engine_name()
    tkflu.set_renderer(name)
    try:
        yield name
    finally:
        tkflu.set_renderer(previous)
