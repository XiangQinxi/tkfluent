def scrollbar(mode, state=None):
    """滚动栏设计配置"""
    if mode.lower() == "dark":
        return {
            "rest": {
                "track_color": "#202020",
                "track_opacity": 0.5,
                "thumb_color": "#606060",
                "thumb_opacity": 0.8
            },
            "hover": {
                "track_color": "#202020",
                "track_opacity": 0.7,
                "thumb_color": "#808080",
                "thumb_opacity": 1.0
            },
            "pressed": {
                "track_color": "#202020",
                "track_opacity": 0.9,
                "thumb_color": "#A0A0A0",
                "thumb_opacity": 1.0
            },
            "disabled": {
                "track_color": "#202020",
                "track_opacity": 0.3,
                "thumb_color": "#404040",
                "thumb_opacity": 0.5
            }
        }
    else:  # light mode
        return {
            "rest": {
                "track_color": "#F0F0F0",
                "track_opacity": 0.5,
                "thumb_color": "#C0C0C0",
                "thumb_opacity": 0.8
            },
            "hover": {
                "track_color": "#F0F0F0",
                "track_opacity": 0.7,
                "thumb_color": "#A0A0A0",
                "thumb_opacity": 1.0
            },
            "pressed": {
                "track_color": "#F0F0F0",
                "track_opacity": 0.9,
                "thumb_color": "#808080",
                "thumb_opacity": 1.0
            },
            "disabled": {
                "track_color": "#F0F0F0",
                "track_opacity": 0.3,
                "thumb_color": "#E0E0E0",
                "thumb_opacity": 0.5
            }
        }
