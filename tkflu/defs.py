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

        font = Font(master=master, family=_DEFAULT_FONT_FAMILY, size=_DEFAULT_FONT_SIZE)
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


def set_default_font(font, attributes):
    if font is None:
        from .designs.fonts import SegoeFont

        attributes.font = SegoeFont()


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
