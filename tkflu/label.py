from tkdeft.windows.drawwidget import DDrawWidget
from .tooltip import FluToolTipBase


class FluLabel(DDrawWidget, FluToolTipBase):
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

    def _draw(self, event=None):
        super()._draw(event)

        self.delete("all")

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=self.attributes.text_color, text=self.attributes.text, font=self.attributes.font
        )

    def theme(self, mode="light"):
        self.mode = mode
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        self.dconfigure(
            text_color="#000000"
        )

    def _dark(self):
        self.dconfigure(
            text_color="#ffffff"
        )