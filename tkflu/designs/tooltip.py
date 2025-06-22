def tooltip(mode):
    if mode.lower() == "light":
        return {
            "back_color": "#e2e2e2",
            "text_color": "#000000",
            "frame_color": "#F9F9F9",
            "frame_border_color": "#ebebeb"
        }
    else:
        return {
            "back_color": "#1a1a1a",
            "text_color": "#ffffff",
            "frame_color": "#2f2f2f",
            "frame_border_color": "#161616"
        }
