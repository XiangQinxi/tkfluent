def window(mode):
    if mode.lower() == "light":
        return {
            "back_color": "#f9f9f9",
            "text_color": "#000000",
            "closebutton": {
                "back_color": "#cf392d",
                "text_color": "#000000",
                "text_hover_color": "#ffffff"
            }
        }
    else:
        return {
            "back_color": "#282828",
            "text_color": "#ffffff",
            "closebutton": {
                "back_color": "#c42b1c",
                "text_color": "#ffffff",
                "text_hover_color": "#000000"
            }
        }
