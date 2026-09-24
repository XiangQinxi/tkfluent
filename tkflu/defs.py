"""便捷函数集合。

包含主题切换辅助函数、主色调预设（红/橙/黄/绿/蓝/紫），
以及菜单项的文本宽度测量。这些名字会经由 ``from tkflu import *`` 直接暴露。"""

#: 常用的正文字号，与 designs.fonts 里的默认值保持一致
_DEFAULT_FONT_SIZE = 9
_DEFAULT_FONT_FAMILY = "Segoe UI"


def is_wide_char(char: str) -> bool:
    """判断是否为"宽字符"（中日韩文字、全角标点、emoji 等）。

    这类字符的显示宽度约为拉丁字母的两倍。用 ``len()`` 估算文本宽度时
    必须把它们按 2 个字符计，否则中文标签会被算得严重偏窄。
    """
    if not char:
        return False
    code = ord(char)
    return (
        0x1100 <= code <= 0x115F  # 谚文字母
        or 0x2E80 <= code <= 0x303E  # 中日韩部首、康熙部首、中日韩符号
        or 0x3041 <= code <= 0x33FF  # 假名、注音、谚文兼容、中日韩兼容
        or 0x3400 <= code <= 0x4DBF  # 中日韩扩展 A
        or 0x4E00 <= code <= 0x9FFF  # 中日韩统一表意文字
        or 0xA000 <= code <= 0xA4CF  # 彝文
        or 0xAC00 <= code <= 0xD7A3  # 谚文音节
        or 0xF900 <= code <= 0xFAFF  # 中日韩兼容表意文字
        or 0xFE30 <= code <= 0xFE6F  # 中日韩兼容形式、小写变体
        or 0xFF00 <= code <= 0xFF60  # 全角形式
        or 0xFFE0 <= code <= 0xFFE6  # 全角符号
        or 0x1F300 <= code <= 0x1F9FF  # emoji
        or 0x20000 <= code <= 0x3FFFD  # 中日韩扩展 B 及以后
    )


def label_cells(label) -> int:
    """把标签折算成"拉丁字符个数"：宽字符算 2 个。"""
    return sum(2 if is_wide_char(ch) else 1 for ch in str(label or ""))


def measure_label_width(master, label, padding: int = 26) -> int:
    """估算一个菜单/按钮标签需要多宽（像素）。

    历史实现用 ``len(label) * 8``：对 ``"FluMenu1"`` 这类拉丁标签大致够用，
    但对中日韩文字会**严重偏窄**——``"文件"`` 只有 2 个字符，算出来 16 像素，
    文字被挤成一团。

    这里优先向 Tk 要真实度量；拿不到字体时退回"宽字符按 2 个计"的估算。

    :param master: 任意控件（用于定位 Tk 解释器与字体）
    :param label: 标签文本
    :param padding: 在文本宽度之外额外预留的左右内边距
    """
    text = str(label or "")
    if not text:
        return max(24, padding)

    width = 0
    try:
        from tkinter.font import Font

        # 注意是 root= 而不是 master=：tkinter.font.Font 的第一个参数叫 root，
        # 写 master= 会被当成"一个叫 master 的字体选项"，直接抛 TclError
        # （以前这里就是这个错，被 except 吞掉之后**永远**走下面的估算分支，
        #  菜单因此比真实需要宽了 1.6~2 倍）。
        font = Font(root=master, family=_DEFAULT_FONT_FAMILY, size=_DEFAULT_FONT_SIZE)
        width = int(font.measure(text))
    except Exception:
        width = 0

    if width <= 0:
        # 拿不到字体度量时的兜底估算
        width = label_cells(text) * _DEFAULT_FONT_SIZE

    return width + padding


def toggle_theme(toggle_button, thememanager):
    if toggle_button.dcget("checked"):
        thememanager.mode("dark")
    else:
        thememanager.mode("light")


def call_command(callback, *args):
    """按回调**实际能接受**的参数个数调用它。

    组件回调的签名历来不统一：``FluButton`` 的 ``command`` 不接受参数，
    而列表 / 导航类组件的回调天然想知道"选中了哪一项"。如果直接
    ``callback(index, item)``，所有只写 ``lambda: ...`` 的老代码都会
    ``TypeError``；反过来直接 ``callback()``，想拿到选中项的人又拿不到。

    这里检查一次签名，取两者都能接受的最大参数个数——既不让老写法崩，
    也不强迫新写法用 ``*args``。

    :param callback: 可调用对象；为 ``None`` 时直接返回 ``None``
    :param args: 候选参数（按位置顺序）
    :returns: 回调的返回值

    ::

        call_command(lambda: print("hi"))              # -> hi（忽略多出来的参数）
        call_command(lambda i: print(i), 3)            # -> 3
        call_command(lambda *a: print(a), 1, 2)        # -> (1, 2)

    .. note::
       签名无法获取时（部分 C 实现的内建可调用对象）退化为"不传参数"。
    """
    if callback is None:
        return None

    import inspect

    try:
        parameters = list(inspect.signature(callback).parameters.values())
    except (TypeError, ValueError):
        return callback()

    if any(p.kind is p.VAR_POSITIONAL for p in parameters):
        return callback(*args)

    positional = sum(
        1
        for p in parameters
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    )
    return callback(*args[:positional])


def set_default_font(font, attributes, master=None):
    """把字体写进 ``attributes.font``，调用方传了就用调用方的。

    :param font: 调用方指定的字体；``None`` 表示用库默认的 Segoe UI
    :param attributes: 组件的属性字典（通常是 ``self.attributes``）
    :param master: 组件自己（**强烈建议传**）。字体对象是**按 Tk 解释器**
        注册的：不传 master 时它会挂到 ``tkinter._default_root`` 上，
        同一进程里第二个 ``FluWindow`` 所属的解释器就不认识这个字体名，
        Tk 会静默退回系统兜底字体（实测"宋体 18"），界面直接走样。

    .. note::
       旧实现只在 ``font is None`` 时才写 ``attributes.font``，
       于是 ``FluLabel(root, font=("Courier New", 24))`` 里的 ``font``
       被**整个丢掉**，``attributes.font`` 保持 ``None``，最终画出来的是
       ``TkDefaultFont``——比库默认字体还不对。
    """
    if font is not None:
        attributes.font = font
        return

    from .designs.fonts import SegoeFont

    attributes.font = SegoeFont(master=master)


def red_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#d20e1e", "#f46762"))


def orange_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#c53201", "#fe7e34"))


def yellow_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#e19d00", "#ffd52a"))


def green_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#0e6d0e", "#45e532"))


def blue_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#005fb8", "#60cdff"))


def purple_primary_color():
    from .designs.primary_color import set_primary_color

    set_primary_color(("#4f4dce", "#b5adeb"))
