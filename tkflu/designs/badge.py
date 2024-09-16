from .primary_color import get_primary_color


def badge(mode, style):
    mode = mode.lower()
    style = style.lower()
    if mode == "light":
        if style == "standard":
            return {
                "back_color": "#000000",
                "back_opacity": 0.057800,
                "border_color": "#000000",
                "border_color_opacity": 0.057800,
                "border_width": 1,
                "text_color": "#191919",
            }
        else:
            return {
                "back_color": get_primary_color()[0],
                "back_opacity": 1,
                "border_color": get_primary_color()[0],
                "border_color_opacity": 1,
                "border_width": 1,
                "text_color": "#FFFFFF",
            }
    else:
        if style == "standard":
            return {
                "back_color": "#FFFFFF",
                "back_opacity": 0.041900,
                "border_color": "#000000",
                "border_color_opacity": 0.041900,
                "border_width": 1,
                "text_color": "#FFFFFF",
            }
        else:
            return {
                "back_color": get_primary_color()[1],
                "back_opacity": 1,
                "border_color": get_primary_color()[1],
                "border_color_opacity": 1,
                "border_width": 1,
                "text_color": "#000000",
            }
