def window(mode):
    if mode.lower() == "light":
        return {
            "back_color": "#ffffff",
            "text_color": "#000000",
            "closebutton": {
                "back_color": "#cf392d",
                "text_color": "#000000",
                "text_hover_color": "#ffffff"
            }
        }
    else:
        return {
            "back_color": "#202020",
            "text_color": "#ffffff",
            "closebutton": {
                "back_color": "#c42b1c",
                "text_color": "#ffffff",
                "text_hover_color": "#000000"
            }
        }
