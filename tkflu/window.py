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

        # 设置窗口图标
        from .icons import light
        from tkinter import PhotoImage
        self.iconphoto(False, PhotoImage(file=light()))

        # 绑定事件处理函数
        self.bind("<Configure>", self._event_configure, add="+")  # 窗口大小/位置改变事件
        self.bind("<Escape>", self._event_key_esc, add="+")       # ESC键按下事件
        self.protocol("WM_DELETE_WINDOW", self._event_delete_window)  # 窗口关闭事件

