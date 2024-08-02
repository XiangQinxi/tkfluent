from tkinter import Toplevel
from tkdeft.object import DObject
from .bwm import BWm


class FluToplevel(Toplevel, BWm, DObject):

    """Fluent设计的子窗口"""

    def __init__(self, *args, mode="light", **kwargs):

        """
        初始化类

        :param args: 参照tkinter.TK.__init__
        :param className: 参照tkinter.TK.__init__
        :param mode: Fluent主题模式 分为 “light” “dark”
        :param kwargs: 参照tkinter.TK.__init__
        """

        self._init(mode)

        self.custom = False

        Toplevel.__init__(self, *args, **kwargs)

        self.bind("<Configure>", self._event_configure)

    def _exit(self):
        self.destroy()
