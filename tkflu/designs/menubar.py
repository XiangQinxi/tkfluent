def menubar(mode):
    mode = mode.lower()
    if mode == "light":
        return {
            "back_color": "#f3f3f3",
        }
    else:
        return {
            "back_color": "#202020",
        }
