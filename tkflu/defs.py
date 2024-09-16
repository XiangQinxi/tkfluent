def toggle_theme(toggle_button, thememanager):
    if toggle_button.dcget('checked'):
        thememanager.mode("dark")
    else:
        thememanager.mode("light")


def set_default_font(font, attributes):
    if font is None:
        from .designs.fonts import SegoeFont
        attributes.font = SegoeFont()


def orange_primary_color():
    from .designs.primary_color import set_primary_color
    set_primary_color(("#c53201", "#fe7e34"))
