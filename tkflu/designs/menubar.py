def menubar(mode):
    mode = mode.lower()
    if mode == "light":
        return {
            "back_color": "#f3f3f3",
            "border_color": "#e5e5e5",
        }
    else:
        return {
            "back_color": "#202020",
            "border_color": "#1d1d1d",
        }
