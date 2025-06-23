from tkdeft.windows.drawwidget import DDrawWidget
from .tooltip import FluToolTipBase
from .designs.gradient import FluGradient


class FluLabel(DDrawWidget, FluToolTipBase, FluGradient):
    def __init__(self, *args,
                 text="",
                 width=120,
                 height=32,
                 font=None,
                 mode="light",
                 **kwargs):
        self._init(mode)

        super().__init__(*args, width=width, height=height, **kwargs)

        self.dconfigure(
            text=text,
        )

        from .defs import set_default_font
        set_default_font(font, self.attributes)

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

    def _draw(self, event=None, tempcolor=None):
        super()._draw(event)

        self.delete("all")

        if tempcolor:
            _text_color = tempcolor
        else:
            _text_color = self.attributes.text_color

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

    def theme(self, mode="light", animation_steps: int = None, animation_step_time: int = None):
        from .designs.label import label
        self.mode = mode
        m = label(mode)

        if animation_steps is None:
            from .designs.animation import get_animation_steps
            animation_steps = get_animation_steps()
        if animation_step_time is None:
            from .designs.animation import get_animation_step_time
            animation_step_time = get_animation_step_time()

        if hasattr(self, "tk"):
            if self.attributes.text_color != m["text_color"]:
                text_colors = self.generate_hex2hex(self.attributes.text_color, m["text_color"], steps=animation_steps)
                for i in range(animation_steps):
                    def update(ii=i):  # 使用默认参数立即捕获i的值
                        self._draw(tempcolor=text_colors[ii])

                    self.after(i * animation_step_time, update)  # 直接传递函数，不需要lambda
        self.dconfigure(
            text_color=m["text_color"]
        )
