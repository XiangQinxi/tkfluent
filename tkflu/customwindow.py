from tkinter import Tk

from ctypes import POINTER, Structure, c_int
from ctypes.wintypes import HWND, RECT, UINT

WM_NCCALCSIZE = 0x0083
WS_EX_APPWINDOW = 0x00040000
WS_VISIBLE = 0x10000000
WS_THICKFRAME = 0x00040000
WS_CAPTION = 0x00C00000
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020

SWP_NOSIZE = 0x0001
SWP_NOREDRAW = 0x0008
SWP_FRAMECHANGED = 0x0020

SW_MAXIMIZE = 3
SW_NORMAL = 1

GWL_EXSTYLE = -20
GWL_STYLE = -16
GWL_WNDPROC = -4


class PWINDOWPOS(Structure):
    _fields_ = [
        ("hWnd", HWND),
        ("hwndInsertAfter", HWND),
        ("x", c_int),
        ("y", c_int),
        ("cx", c_int),
        ("cy", c_int),
        ("flags", UINT),
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [("rgrc", RECT * 3), ("lppos", POINTER(PWINDOWPOS))]


from ctypes import WINFUNCTYPE, c_char_p, c_uint64, windll


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
        self.window.update()

    def bind(self, widget: Widget):
        widget.bind("<Button-1>", self._click)
        widget.bind("<B1-Motion>", lambda event: self._window_move(event))

    def tag_bind(self, widget: Widget, tag):
        widget.tag_bind(tag, "<Button-1>", self._click)
        widget.tag_bind(tag, "<B1-Motion>", lambda event: self._window_move(event))


class CustomWindow(object):
    def __init__(self, window: Tk = None, wait=100):

        if window is not None:
            self.window: Tk = window
        else:
            from tkinter import _default_root
            self.window: Tk = _default_root

        self.window.after(wait, self.setup)

    def bind_drag(self, widget):
        WindowDragArea(self.window).bind(widget)

    def setup(self):
        def handle(hwnd: any, msg: any, wp: any, lp: any) -> any:
            if msg == WM_NCCALCSIZE and wp:
                sz = NCCALCSIZE_PARAMS.from_address(lp)
                sz.rgrc[0].top -= 6

            return windll.user32.CallWindowProcW(*map(c_uint64, (globals()[old], hwnd, msg, wp, lp)))

        self.hwnd = windll.user32.GetParent(self.window.winfo_id())

        windll.user32.SetWindowLongA(self.hwnd, GWL_EXSTYLE, WS_EX_APPWINDOW)
        windll.user32.SetWindowLongA(self.hwnd, GWL_STYLE, WS_VISIBLE | WS_THICKFRAME)

        old, new = "old", "new"
        prototype = WINFUNCTYPE(c_uint64, c_uint64, c_uint64, c_uint64, c_uint64)
        globals()[old] = None
        globals()[new] = prototype(handle)
        globals()[old] = windll.user32.GetWindowLongPtrA(self.hwnd, GWL_WNDPROC)
        windll.user32.SetWindowLongPtrA(self.hwnd, GWL_WNDPROC, globals()[new])

        self.window.wm_iconify()
        self.window.wm_deiconify()
        self.window.focus_force()
        self.window.update()


from tkinter import Tk


class CustomTk(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customwindow = CustomWindow(self, *args, **kwargs)


if __name__ == '__main__':
    from tkinter import Tk, Frame
    root = Tk()
    root.title("Test")

    frame = Frame(root, width=100, height=25, background="grey")
    frame.pack(fill="x", side="top")

    customwindow = CustomWindow(root, wait=100)
    customwindow.bind_drag(frame)

    root.mainloop()