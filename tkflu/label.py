"""文本标签组件。

``FluLabel`` 支持通过 ``tooltip()`` 挂一个 Fluent 风格的悬浮提示。

宽度自适应
----------
历史实现的 ``width`` 默认是 120px 的**固定画布**，文本以 ``anchor="center"``
居中绘制。文字一旦比 120px 宽，左右两侧就都被裁掉——例如
``FluLabel(root, text="FluLabel（悬停看提示）")`` 会被显示成
``uLabel（悬停看提示）``。

现在：**调用方不传 ``width`` 时**，标签会按文本自动撑开（只增不减，
避免文字变化时抖动）。显式传了 ``width`` 则完全以显式值为准，行为与旧版一致。
"""

from tkdeft.windows.drawwidget import DDrawWidget

from .designs.gradient import FluGradient
from .tooltip import FluToolTipBase

#: 文本两侧的呼吸空间（像素）
_TEXT_PADDING = 12
#: 没有文本时沿用的旧默认宽度
_EMPTY_WIDTH = 120


def _resolve_master(args, kwargs):
    """从构造参数里找出 Tk 主控件，用于测量字体。"""
    if "master" in kwargs:
        return kwargs["master"]
    if args:
        return args[0]
    import tkinter

    return tkinter._default_root


class FluLabel(DDrawWidget, FluToolTipBase, FluGradient):
    def __init__(
        self, *args, text="", width=None, height=32, font=None, mode="light", **kwargs
    ):
        self._init(mode)

        #: 调用方显式指定的宽度；None 表示"按文本自适应"
        self._fixed_width = width

        super().__init__(*args, width=self._initial_width(args, kwargs, text, width),
                         height=height, **kwargs)

        self.dconfigure(
            text=text,
        )

        from .defs import set_default_font

        set_default_font(font, self.attributes)

    # ------------------------------------------------------------------
    def _initial_width(self, args, kwargs, text, width):
        """创建画布前先算出一个合理的初始宽度。"""
        if width is not None:
            return width
        if not text:
            return _EMPTY_WIDTH
        from .defs import measure_label_width

        return max(24, measure_label_width(_resolve_master(args, kwargs), text,
                                           padding=_TEXT_PADDING))

    def _init(self, mode):

        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "text_color": "#1b1b1b",
            }
        )

        self.theme(mode=mode)

    def _fit_to_text(self):
        """文本比画布宽时把画布加宽（只增不减，避免反复触发重排）。

        只在调用方**没有**显式指定宽度时生效。
        """
        if self._fixed_width is not None:
            return
        if not getattr(self, "element_text", None):
            return

        try:
            bbox = self.bbox(self.element_text)
        except Exception:
            return
        if not bbox:
            return  # 尚未映射，量不到

        needed = int(bbox[2] - bbox[0]) + _TEXT_PADDING
        current = self.winfo_reqwidth()
        if needed > current:
            self.config(width=needed)

    def _draw(self, event=None, tempcolor=None):
        super()._draw(event)

        if tempcolor:
            _text_color = tempcolor
        else:
            _text_color = self.attributes.text_color

        if not hasattr(self, "element_text"):
            self.element_text = self.create_text(
                self.winfo_width() / 2,
                self.winfo_height() / 2,
                anchor="center",
                fill=_text_color,
                text=self.attributes.text,
                font=self.attributes.font,
            )
        else:
            self.coords(
                self.element_text, self.winfo_width() / 2, self.winfo_height() / 2
            )
            self.itemconfigure(
                self.element_text,
                fill=_text_color,
                text=self.attributes.text,
                font=self.attributes.font,
            )

        self._fit_to_text()

    def theme(
        self, mode="light", animation_steps: int = None, animation_step_time: int = None
    ):
        from .designs.label import label

        self.mode = mode
        m = label(mode)

        if animation_steps is None:
            from .designs.animation import get_animation_steps

            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time

            animation_step_time = get_animation_step_time()

        if not animation_steps == 0 or not animation_step_time == 0:
            if hasattr(self, "tk"):
                if self.attributes.text_color != m["text_color"]:
                    text_colors = self.generate_hex2hex(
                        self.attributes.text_color,
                        m["text_color"],
                        steps=animation_steps,
                    )
                    for i in range(animation_steps):

                        def update(ii=i):  # 使用默认参数立即捕获i的值
                            self._draw(tempcolor=text_colors[ii])

                        self.after(
                            i * animation_step_time, update
                        )  # 直接传递函数，不需要lambda
        self.dconfigure(text_color=m["text_color"])
        if hasattr(self, "tk"):
            self._draw()
