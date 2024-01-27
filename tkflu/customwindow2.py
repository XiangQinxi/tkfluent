from tkinter import Event, Widget, Tk, Frame


class WindowDragArea(object):
    x, y = 0, 0

    def __init__(self, window):
        self.window = window

    def _click(self, event: Event):
        self.x, self.y = event.x, event.y

    def _window_move(self, event: Event):
        new_x = (event.x - self.x) + self.window.winfo_x()
        new_y = (event.y - self.y) + self.window.winfo_y()
        if new_y <= 0:
            new_y = 0
        self.window.geometry(f"+{new_x}+{new_y}")

    def bind(self, widget: Widget):
        widget.bind("<Button-1>", self._click)
        widget.bind("<B1-Motion>", lambda event: self._window_move(event))

    def tag_bind(self, widget: Widget, tag):
        widget.tag_bind(tag, "<Button-1>", self._click)
        widget.tag_bind(tag, "<B1-Motion>", lambda event: self._window_move(event))


class WidgetDragArea(object):
    x, y = 0, 0

    def __init__(self, widget=None):
        self.widget = widget

    def _click(self, event: Event):
        self.x, self.y = event.x, event.y

    def _widget_move(self, event: Event):
        new_x = (event.x - self.x) + self.widget.winfo_x()
        new_y = (event.y - self.y) + self.widget.winfo_y()
        if new_y <= 0:
            new_y = 0
        self.widget.place(x=new_x, y=new_y)

    def bind(self):
        self.widget.bind("<Button-1>", self._click)
        self.widget.bind("<B1-Motion>", lambda event: self._widget_move(event))

    def tag_bind(self, tag):
        self.widget.tag_bind(tag, "<Button-1>", self._click)
        self.widget.tag_bind(tag, "<B1-Motion>", lambda event: self._widget_move(event))


def bind_window_drag(window, widget):
    _ = WindowDragArea(window)
    _.bind(widget)
    return _


def tag_bind_window_drag(window, widget, tag):
    _ = WindowDragArea(window)
    _.tag_bind(widget, tag)
    return _


def bind_widget_drag(widget):
    _ = WidgetDragArea(widget)
    _.bind()
    return _


def tag_bind_widget_drag(widget, tag):
    _ = WidgetDragArea(widget)
    _.tag_bind(tag)
    return _


