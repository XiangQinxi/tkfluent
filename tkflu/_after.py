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

为什么销毁时不能"全解释器一起取消"
----------------------------------
``after info`` 是**按 Tcl 解释器**返回的，而一个解释器上可以同时住着好几个
顶层窗口（``FluWindow`` + 若干 ``FluToplevel``）。"全取消"看似安全，实际会
把别的窗口的回调一起干掉，而且那些命令名还留在**别的**控件的
``_tclCommands`` 里没人清理——下次它们销毁时会重复删除已经删掉的命令，
抛 ``TclError: can't delete Tcl command``，异常冒到 ``root.destroy()``，
窗口关不掉、``tkinter._default_root`` 残留。

所以这里改成**按归属取消**：``Misc._register`` 已经把命令名记在发起控件的
``_tclCommands`` 上，于是"这个名字归谁"是能精确回答的。只取消本子树持有的
那些，其余一概不碰。

一个容易踩的坑
--------------
不能直接对 root 调 ``after_cancel()``。``Misc.after_cancel`` 内部会调用
``self.deletecommand(script)``，而 ``self`` 是 **root**：Tcl 命令被删掉了，
但记录它的却是**发起控件的** ``_tclCommands``（root 的列表里根本没有它，
``remove`` 静默失败）。等那个控件自己被销毁时，``Misc.destroy`` 会拿这个
已经删掉的命令再删一次，抛出 ``TclError: can't delete Tcl command``。

因此这里：
1. 先列出本子树**实际持有**的命令名；
2. 从 ``after info`` 里取出每个回调对应的脚本名，只处理归属本子树的；
3. 在 Tcl 层面取消调度并删除这些命令；
4. 最后遍历本子树，把这些名字从各控件的 ``_tclCommands`` 里摘掉，
   避免它们被重复删除。
"""

from __future__ import annotations

from typing import List, Set

__all__ = ["cancel_all_after", "pending_after_count", "TracedAfter"]


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


def _owned_commands(root_widget) -> Set[str]:
    """控件子树里所有控件"自己登记的" ``after`` 命令名。

    ``Misc._register`` 会把生成的 Tcl 命令名记进**发起控件**的
    ``_tclCommands``。因此"这个名字归谁"是可以精确回答的，
    不需要也不应该去动别的窗口的回调。
    """
    names: Set[str] = set()
    stack = [root_widget]
    seen = set()
    while stack:
        current = stack.pop()
        key = id(current)
        if key in seen:
            continue
        seen.add(key)
        try:
            names.update(getattr(current, "_tclCommands", None) or ())
        except Exception:
            pass
        try:
            stack.extend(current.children.values())
        except Exception:
            pass
    return names


def pending_after_count(widget) -> int:
    """还有多少个待执行的 ``after`` 回调（便于诊断与测试）。"""
    return len(_after_ids(widget))


def cancel_all_after(widget) -> int:
    """取消**该控件及其子树**排队的 ``after`` 回调，返回取消的数量。

    应当在 ``destroy()`` 之前调用。清理过程中的任何异常都被吞掉——
    关闭窗口这件事不应该因为清理失败而失败。

    .. warning::
       ``after info`` 是**按 Tcl 解释器**返回的，一个解释器上可能同时住着
       好几个顶层窗口。旧实现把这份列表**整个**取消掉，后果是：

       * 另一个窗口排的回调被无辜取消（比如 ``root.after(500, ...)``
         再也不执行）；
       * 但那些命令名仍然记在**别的**控件的 ``_tclCommands`` 里，
         ``_forget_commands`` 只走被销毁控件自己的子树，摘不到它们；
       * 于是下次别的控件销毁时会再删一次已经删掉的命令 →
         ``TclError: can't delete Tcl command``，异常一路冒到
         ``root.destroy()``，窗口没关掉、``_default_root`` 残留，
         之后 ``FluMenu()`` / ``FluToplevel()`` 全部报
         "application has been destroyed"。

       现在改成"只取消本子树真正持有的那些"，其余一律不碰。
    """
    owned = _owned_commands(widget)
    if not owned:
        return 0

    tk = widget.tk
    cancelled = 0
    doomed: Set[str] = set()

    for after_id in _after_ids(widget):
        name = _script_name(widget, after_id)
        if not name or name not in owned:
            continue  # 不属于这棵子树 —— 是别的窗口的回调，别动它
        try:
            tk.call("after", "cancel", after_id)
            cancelled += 1
            doomed.add(name)
        except Exception:
            pass

    # 删除已经不会再执行的 Tcl 命令，并从本子树的记录里摘掉，
    # 免得控件销毁时重复删除而抛 "can't delete Tcl command"。
    for name in doomed:
        try:
            tk.deletecommand(name)
        except Exception:
            pass
    if doomed:
        _forget_commands(widget, doomed)

    return cancelled


class TracedAfter:
    """把本控件排队的 ``after`` 记下来，便于"重排前撤销旧的、销毁时清理"。

    :func:`cancel_all_after` 解决的是**关窗**时的残留回调；这个混入解决的是
    控件**活着**的时候动画回调堆积的问题：

    * 主题过渡动画会一次性排 ``steps`` 个 ``after``。用户来回切主题时，
      旧的那一批不会被取消，会和新的交错执行，把画面带回**中间状态**；
    * 控件销毁后，那批回调还排在解释器上（虽然 Tk 会静默吞掉，
      但 ``after info`` 会一直长下去）。

    用法::

        class MyWidget(TracedAfter, tkinter.Canvas):
            def animate(self):
                self.cancel_traced()               # 先撤销上一轮
                for i in range(steps):
                    self.after_traced(i * 20, self.frame)

    :meth:`cancel_traced` 只取消**本控件自己**登记的回调，不会影响别的控件，
    因此不需要像 :func:`cancel_all_after` 那样绕开 ``after_cancel`` 的坑。
    """

    def _traced_ids(self) -> List[str]:
        """本控件当前登记在案的 ``after`` id 列表（惰性创建）。"""
        ids = self.__dict__.get("_traced_after_ids")
        if ids is None:
            ids = []
            self.__dict__["_traced_after_ids"] = ids
        return ids

    def after_traced(self, delay: int, callback):
        """排一个 ``after``，并登记它的 id。

        :param delay: 毫秒
        :param callback: 回调
        :returns: ``after`` 的 id
        """
        ids = self._traced_ids()

        def run():
            try:
                ids.remove(handle)
            except ValueError:
                pass
            callback()

        handle = self.after(delay, run)
        ids.append(handle)
        return handle

    def cancel_traced(self) -> int:
        """取消本控件所有尚未执行的 ``after``，返回取消的数量。"""
        ids = self._traced_ids()
        cancelled = 0
        for handle in list(ids):
            try:
                self.after_cancel(handle)
                cancelled += 1
            except Exception:
                pass
        ids.clear()
        return cancelled

    def traced_count(self) -> int:
        """还有多少个本控件排队中的 ``after``（诊断与测试用）。"""
        return len(self._traced_ids())
