"""``after`` 回调的统一回收。

问题
----
``tkinter`` 的 ``after()`` 把回调注册在 **Tcl 解释器** 上（命令名由
``Misc._register`` 生成并记在 **发起控件** 的 ``_tclCommands`` 列表里），
而不是记在控件树上。控件 ``destroy()`` 时 Tkinter 会删掉控件自己的命令，
但**不会**取消已排队的 ``after`` 回调。于是窗口关闭后，这些回调一触发就报：

.. code-block:: text

    invalid command name "140234567890123<lambda>"
        while executing
    "140234567890123<lambda>"
        ("after" script)

tkfluent 里有多处动画会挂 ``after``（``FluButton`` / ``FluFrame`` /
``FluMenuBar`` / ``BWm`` / ``FluLabel`` / ``FluToggleButton`` /
``FluPopupWindow``），它们都没有取消机制。

为什么可以在销毁时"全部取消"
----------------------------
``after info`` 是**按 Tcl 解释器**返回的。销毁一个顶层窗口时，这个解释器上的
所有待执行回调本来就会随解释器失效——没有任何回调应当比它的解释器活得更久。
所以销毁前把它们全部取消是安全且彻底的。

一个容易踩的坑
--------------
不能直接对 root 调 ``after_cancel()``。``Misc.after_cancel`` 内部会调用
``self.deletecommand(script)``，而 ``self`` 是 **root**：Tcl 命令被删掉了，
但记录它的却是**发起控件的** ``_tclCommands``（root 的列表里根本没有它，
``remove`` 静默失败）。等那个控件自己被销毁时，``Misc.destroy`` 会拿这个
已经删掉的命令再删一次，抛出 ``TclError: can't delete Tcl command``——
这个异常会一路冒到 ``root.destroy()``，导致窗口根本没被销毁、
``tkinter._default_root`` 残留，后续再建窗口就撞上 ``bad window path name``。

因此这里：
1. 先从 ``after info`` 里取出每个回调对应的 **脚本名**（即 Tcl 命令名）；
2. 在 Tcl 层面取消调度，并删除这些命令；
3. 最后遍历整棵控件树，把这些名字从各控件的 ``_tclCommands`` 里摘掉，
   避免它们被重复删除。
"""

from __future__ import annotations

from typing import List, Set

__all__ = ["cancel_all_after", "pending_after_count"]


def _after_ids(widget) -> List[str]:
    """该控件所属解释器上所有待执行 ``after`` 的 id。"""
    try:
        return list(widget.tk.splitlist(widget.tk.call("after", "info")))
    except Exception:
        return []


def _script_name(widget, after_id: str):
    """取某个 ``after`` 对应的 Tcl 命令名（不是所有 id 都对应 Python 回调）。"""
    try:
        info = widget.tk.splitlist(widget.tk.call("after", "info", after_id))
    except Exception:
        return None
    return info[0] if info else None


def _forget_commands(root_widget, names: Set[str]) -> int:
    """从整棵控件树的 ``_tclCommands`` 里摘掉指定命令名，返回摘掉的数量。"""
    removed = 0
    stack = [root_widget]
    seen = set()
    while stack:
        current = stack.pop()
        key = id(current)
        if key in seen:
            continue
        seen.add(key)

        commands = getattr(current, "_tclCommands", None)
        if commands:
            kept = [name for name in commands if name not in names]
            removed += len(commands) - len(kept)
            current._tclCommands = kept

        try:
            stack.extend(current.children.values())
        except Exception:
            pass
    return removed


def pending_after_count(widget) -> int:
    """还有多少个待执行的 ``after`` 回调（便于诊断与测试）。"""
    return len(_after_ids(widget))


def cancel_all_after(widget) -> int:
    """取消该控件所属 Tcl 解释器上所有待执行回调，返回取消的数量。

    应当在 ``destroy()`` 之前调用。清理过程中的任何异常都被吞掉——
    关闭窗口这件事不应该因为清理失败而失败。
    """
    ids = _after_ids(widget)
    if not ids:
        return 0

    names = {name for name in (_script_name(widget, i) for i in ids) if name}

    cancelled = 0
    tk = widget.tk
    for after_id in ids:
        try:
            tk.call("after", "cancel", after_id)
            cancelled += 1
        except Exception:
            pass

    # 删除已经不会再执行的 Tcl 命令，并从所有控件的记录里摘掉，
    # 免得控件销毁时重复删除而抛 "can't delete Tcl command"。
    for name in names:
        try:
            tk.deletecommand(name)
        except Exception:
            pass
    if names:
        _forget_commands(widget, names)

    return cancelled
