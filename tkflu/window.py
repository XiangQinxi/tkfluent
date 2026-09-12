"""主窗口。

``FluWindow`` 继承自 ``tkinter.Tk``，是应用的根窗口。
它负责应用图标、窗口级主题、以及 ESC / 关闭按钮等默认行为。

.. code-block:: python

    import tkflu

    root = tkflu.FluWindow(mode="light")
    tkflu.FluButton(root, text="你好").pack()
    root.mainloop()"""

from tkinter import Tk, Toplevel

from tkdeft.object import DObject

from .bwm import BWm


class FluWindow(Tk, BWm, DObject):
    """Fluent设计的主窗口"""

    def __init__(self, *args, className="tkdeft", mode="light", **kwargs):
        """
        初始化类实例，继承自tkinter.TK并添加Fluent主题支持

        :param args: 可变位置参数，传递给父类tkinter.TK.__init__的未命名参数
        :param className: 窗口类名，默认"tkdeft"，传递给父类tkinter.TK.__init__
        :param mode: Fluent主题模式，可选值为"light"(明亮)或"dark"(暗黑)，默认"light"
        :param kwargs: 可变关键字参数，传递给父类tkinter.TK.__init__的命名参数
        """

        # 初始化Fluent主题
        self._init(mode)

        # 标记为未使用自定义配置
        self.custom = False

        # 调用父类tkinter.TK的初始化方法
        super().__init__(*args, className=className, **kwargs)

        # 设置窗口图标：直接用内嵌 base64 建图，完全不落盘、不泄漏临时文件。
        # 必须显式传 master=self——不传时 tkinter 会把图片挂到默认根窗口的
        # 解释器上，多 Tk 解释器场景下 iconphoto 会报 "not a photo image"。
        from .icons import icon_photoimage

        self._icon_photo = icon_photoimage("light", master=self)
        self.iconphoto(False, self._icon_photo)

        # 绑定事件处理函数
        self.bind(
            "<Configure>", self._event_configure, add="+"
        )  # 窗口大小/位置改变事件
        self.bind("<Escape>", self._event_key_esc, add="+")  # ESC键按下事件
        self.protocol("WM_DELETE_WINDOW", self._event_delete_window)  # 窗口关闭事件

    def destroy(self):
        """关闭窗口前先回收待执行的 ``after`` 回调。

        ``tkinter`` 的 ``after`` 注册在 Tcl 解释器上，控件销毁时不会被取消，
        残留回调会在窗口关闭后触发并刷 ``invalid command name ...``。
        详见 :mod:`tkflu._after`。
        """
        from ._after import cancel_all_after

        cancel_all_after(self)
        super().destroy()
