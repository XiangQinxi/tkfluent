class FluDesign(object):
    def __init__(self):
        pass

    def badge(self, *args, **kwargs):
        from .badge import badge
        return badge(*args, **kwargs)

    def button(self, *args, **kwargs):
        from .button import button
        return button(*args, **kwargs)

    def entry(self, *args, **kwargs):
        from .entry import entry
        return entry(*args, **kwargs)

    def frame(self, *args, **kwargs):
        from .frame import frame
        return frame(*args, **kwargs)

    def label(self, *args, **kwargs):
        from .label import label
        return label(*args, **kwargs)

    def menubar(self, *args, **kwargs):
        from .menubar import menubar
        return menubar(*args, **kwargs)

    def scrollbar(self, *args, **kwargs):
        from .scrollbar import scrollbar
        return scrollbar(*args, **kwargs)

    def slider(self, *args, **kwargs):
        from .slider import slider
        return slider(*args, **kwargs)

    def text(self, *args, **kwargs):
        from .text import text
        return text(*args, **kwargs)

    def tooltip(self, *args, **kwargs):
        from .tooltip import tooltip
        return tooltip(*args, **kwargs)

    def window(self, *args, **kwargs):
        from .window import window
        return window(*args, **kwargs)