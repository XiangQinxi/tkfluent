from .popupwindow import FluPopupWindow


class FluToolTip(FluPopupWindow):
    def __init__(self, widget, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.widget = widget
