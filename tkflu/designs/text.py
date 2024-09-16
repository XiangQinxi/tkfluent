from .primary_color import get_primary_color


def text(mode, state):
    _r = 6
    mode = mode.lower()
    state = state.lower()
    if mode == "light":
        if state == "rest":
            return {
                "back_color": "#FEFEFE",
                "back_opacity": 1,

                "stop1": 0.999878,
                "border_color": "#000000",
                "border_color_opacity": 0.058824,

                "stop2": 1.000000,
                "border_color2": "#000000",
                "border_color2_opacity": 0.447059,

                "border_width": 1,
                "radius": _r,
                "text_color": "#646464",
                "underline_fill": "#8a8a8a",
                "underline_width": 1,
            }
        elif state == "hover":
            return {
                "back_color": "#FAFAFA",
                "back_opacity": 1,

                "stop1": 0.999878,
                "border_color": "#000000",
                "border_color_opacity": "0.058824",

                "stop2": 1.000000,
                "border_color2": "#000000",
                "border_color2_opacity": "0.447059",

                "border_width": 1,
                "radius": _r,
                "text_color": "#626262",
                "underline_fill": "#8a8a8a",
                "underline_width": 1,
            }
        elif state == "pressed":
            return {
                "back_color": "#FFFFFF",
                "back_opacity": 0.700000,

                "stop1": 0.941406,
                "border_color": "#000000",
                "border_color_opacity": 0.058824,

                "stop2": 1,
                "border_color2": get_primary_color()[0],
                "border_color2_opacity": 1,

                "border_width": 1,
                "radius": _r,
                "text_color": "#646464",
                "underline_fill": get_primary_color()[0],
                "underline_width": 1.5,
            }
        elif state == "disabled":
            return {
                "back_color": "#FAFAFA",
                "back_opacity": 1,

                "stop1": None,
                "border_color": "#000000",
                "border_color_opacity": 0.057800,

                "stop2": None,
                "border_color2": None,
                "border_color2_opacity": None,

                "border_width": 1,
                "radius": _r,
                "text_color": "#646464",
                "underline_fill": None,
                "underline_width": 1.5,
            }

    else:
        if state == "rest":
            return {
                "back_color": "#292929",
                "back_opacity": 1,

                "stop1": 0.999767,
                "border_color": "#FFFFFF",
                "border_color_opacity": 0.078431,

                "stop2": 1.000000,
                "border_color2": "#FFFFFF",
                "border_color2_opacity": 0.545098,

                "border_width": 1,
                "radius": _r,
                "text_color": "#d1d1d1",
                "underline_fill": "#989898",
                "underline_width": 1,
            }
        elif state == "hover":
            return {
                "back_color": "#2f2f2f",
                "back_opacity": 1,

                "stop1": 0.999767,
                "border_color": "#FFFFFF",
                "border_color_opacity": "0.078431",

                "stop2": 1,
                "border_color2": "#FFFFFF",
                "border_color2_opacity": "0.545098",

                "border_width": 1,
                "radius": _r,
                "text_color": "#d2d2d2",

                "underline_fill": "#989898",
                "underline_width": 1,
            }
        elif state == "pressed":
            return {
                "back_color": "#1d1d1d",
                "back_opacity": 1,

                "stop1": 0.941406,
                "border_color": "#FFFFFF",
                "border_color_opacity": 0,

                "stop2": 1,
                "border_color2": get_primary_color()[1],
                "border_color2_opacity": 1,

                "border_width": 1,
                "radius": _r,
                "text_color": "#cecece",

                "underline_fill": get_primary_color()[1],
                "underline_width": 1.5,
            }
        elif state == "disabled":
            return {
                "back_color": "#262626",
                "back_opacity": 0,

                "stop1": None,
                "border_color": "#FFFFFF",
                "border_color_opacity": 0.069800,

                "stop2": None,
                "border_color2": None,
                "border_color2_opacity": None,

                "border_width": 1,
                "radius": _r,
                "text_color": "#757575",
                "underline_fill": None,
                "underline_width": 1,
            }
