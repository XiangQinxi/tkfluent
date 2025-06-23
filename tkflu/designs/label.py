def label(mode: str):
    mode = mode.lower()
    if mode == "light":
        return {
            "text_color": "#000000",
        }
    else:
        return {
            "text_color": "#ffffff",
        }
