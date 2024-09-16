def frame(mode, style):
    mode = mode.lower()
    style = style.lower()
    if mode == "light":
        if style == "standard":
            return {
                "back_color": "#FFFFFF",
                "border_color": "#000000",
                "border_color_opacity": 0.057800,
                "border_width": 2,
                "radius": 7,
            }
        else:
            return {
                "back_color": "#FFFFFF",
                "border_color": "#000000",
                "border_color_opacity": 0.057800,
                "border_width": 2,
                "radius": 7,
            }
    else:
        if style == "standard":
            return {
                "back_color": "#282828",
                "border_color": "#000000",
                "border_color_opacity": 0.100000,
                "border_width": 2,
                "radius": 7,
            }
        else:
            return {
                "back_color": "#282828",
                "border_color": "#000000",
                "border_color_opacity": 0.100000,
                "border_width": 2,
                "radius": 7,
            }