from .primary_color import get_primary_color


def slider(mode: str, state: str):
    mode = mode.lower()
    state = state.lower()

    if mode == "light":
        if state == "rest":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,
                    "inner_radius": 6,

                    "back_color": "#FFFFFF",
                    "back_opacity": 1,

                    "border_color": "#000000",
                    "border_color_opacity": 0.058824,

                    "border_color2": "#000000",
                    "border_color2_opacity": 0.160784,

                    "inner_back_color": get_primary_color()[0],
                    "inner_back_opacity": 1,
                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[0],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#000000",
                    "back_opacity": 0.445800
                }
            }
        elif state == "hover":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,
                    "inner_radius": 8,

                    "back_color": "#FFFFFF",
                    "back_opacity": 1,

                    "border_color": "#000000",
                    "border_color_opacity": 0.058824,

                    "border_color2": "#000000",
                    "border_color2_opacity": 0.160784,

                    "inner_back_color": get_primary_color()[0],
                    "inner_back_opacity": 1,
                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[0],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#000000",
                    "back_opacity": 0.445800
                }
            }
        elif state == "pressed":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,
                    "inner_radius": 5,

                    "back_color": "#FFFFFF",
                    "back_opacity": 1,

                    "border_color": "#000000",
                    "border_color_opacity": 0.058824,

                    "border_color2": "#000000",
                    "border_color2_opacity": 0.160784,

                    "inner_back_color": get_primary_color()[0],
                    "inner_back_opacity": 0.8,
                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[0],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#000000",
                    "back_opacity": 0.445800
                }
            }
        elif state == "disabled":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,
                    "inner_radius": 6,

                    "back_color": "#FFFFFF",
                    "back_opacity": 1,

                    "border_color": "#000000",
                    "border_color_opacity": 0.058824,

                    "border_color2": "#000000",
                    "border_color2_opacity": 0.160784,

                    "inner_back_color": "#000000",
                    "inner_back_opacity": 0.317300,
                },
                "track": {
                    "width": 4,

                    "back_color": "#000000",
                    "back_opacity": 0.216900
                },
                "rail": {
                    "back_color": "#000000",
                    "back_opacity": 0.317300
                }
            }
    else:
        if state == "rest":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,

                    "inner_radius": 6,
                    "inner_back_color": get_primary_color()[1],
                    "inner_back_opacity": 1,

                    "back_color": "#454545",
                    "back_opacity": 1,

                    "border_color": "#FFFFFF",
                    "border_color_opacity": 0.094118,

                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": 0.070588,

                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[1],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#FFFFFF",
                    "back_opacity": 0.544200
                }
            }
        elif state == "hover":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,

                    "inner_radius": 8,
                    "inner_back_color": get_primary_color()[1],
                    "inner_back_opacity": 1,

                    "back_color": "#454545",
                    "back_opacity": 1,

                    "border_color": "#FFFFFF",
                    "border_color_opacity": 0.094118,

                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": 0.070588,

                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[1],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#FFFFFF",
                    "back_opacity": 0.544200
                }
            }
        elif state == "pressed":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,

                    "inner_radius": 5,
                    "inner_back_color": get_primary_color()[1],
                    "inner_back_opacity": 0.8,

                    "back_color": "#454545",
                    "back_opacity": 1,

                    "border_color": "#FFFFFF",
                    "border_color_opacity": 0.094118,

                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": 0.070588,

                },
                "track": {
                    "width": 4,

                    "back_color": get_primary_color()[1],
                    "back_opacity": 1
                },
                "rail": {
                    "back_color": "#FFFFFF",
                    "back_opacity": 0.544200
                }
            }
        elif state == "disabled":
            return {
                "radius": 2,
                "thumb": {
                    "radius": 12,

                    "inner_radius": 6,
                    "inner_back_color": "#FFFFFF",
                    "inner_back_opacity": 0.158100,

                    "back_color": "#454545",
                    "back_opacity": 1,

                    "border_color": "#FFFFFF",
                    "border_color_opacity": 0.094118,

                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": 0.070588,

                },
                "track": {
                    "width": 4,

                    "back_color": "#FFFFFF",
                    "back_opacity": 0.158100
                },
                "rail": {
                    "back_color": "#FFFFFF",
                    "back_opacity": 0.544200
                }
            }
