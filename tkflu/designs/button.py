from .primary_color import get_primary_color


def button(mode: str, style: str, state: str):
    _r = 6
    mode = mode.lower()
    style = style.lower()
    state = state.lower()
    if mode == "light":
        if style == "standard":
            if state == "rest":
                return {
                    "back_color": "#ffffff",
                    "back_opacity": "0.7",
                    "border_color": "#000000",
                    "border_color_opacity": "0.2",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.3",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "hover":
                return {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.5",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.2",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "pressed":
                return {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.3",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#636363",
                }
            elif state == "disabled":
                return {
                    "back_color": "#ffffff",
                    "back_opacity": "1.000000",
                    "border_color": "#000000",
                    "border_color_opacity": "0.058824",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.160784",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#a2a2a2",
                }
        elif style == "accent":
            if state == "rest":
                return {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#ffffff",
                }
            elif state == "hover":
                return {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#ffffff",
                }
            elif state == "pressed":
                return {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.08",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#fbfbfb",
                }
            elif state == "disabled":
                return {
                    "back_color": "#000000",
                    "back_opacity": "0.22",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "1",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "1",
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#f3f3f3",
                }
        else:
            if state == "rest":
                return {
                    "back_color": "#ffffff",
                    "back_opacity": 0,
                    "border_color": "#000000",
                    "border_color_opacity": "0",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "hover":
                return {
                    "back_color": "#F9F9F9",
                    "back_opacity": 0,
                    "border_color": "#000000",
                    "border_color_opacity": "0",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "pressed":
                return {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.3",
                    "border_color": "#000000",
                    "border_color_opacity": "0",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#636363",
                }
            elif state == "disabled":
                return {
                    "back_color": "#ffffff",
                    "back_opacity": 0,
                    "border_color": "#000000",
                    "border_color_opacity": "0",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#a2a2a2",
                }
    else:
        if style == "standard":
            if state == "rest":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.06",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#FFFFFF",
                }
            elif state == "hover":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.08",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#FFFFFF",
                }
            elif state == "pressed":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.03",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#7D7D7D",
                }
            elif state == "disabled":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.04",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#a2a2a2",
                }
        elif style == "accent":
            if state == "rest":
                return {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "hover":
                return {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#000000",
                }
            elif state == "pressed":
                return {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#101010",
                }
            elif state == "disabled":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.16",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.16",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": _r,
                    "text_color": "#a7a7a7",
                }
        else:
            if state == "rest":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0",
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#FFFFFF",
                }
            elif state == "hover":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.04",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.045",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#FFFFFF",
                }
            elif state == "pressed":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.015",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.035",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#7D7D7D",
                }
            elif state == "disabled":
                return {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 0,
                    "radius": _r,
                    "text_color": "#a2a2a2",
                }
