def scrollbar(mode):
    """滚动栏设计配置"""
    if mode.lower() == "dark":
        return {
            "rest": {
                "thumb_color": "#9a9a9a",
                "radius": 2,
            },
            "expand": {
                "track_color": "#2b2b2b",
                "thumb_color": "#9f9f9f",
                "radius": 4,
            },
            "disabled": {
                "thumb_color": "#515151",
                "radius": 2,
            }
        }
    else:  # light mode
        return {
            "rest": {
                "thumb_color": "#868686",
                "radius": 2,
            },
            "expand": {
                "track_color": "#f8f8f8",
                "thumb_color": "#898989",
                "radius": 4,
            },
            "disabled": {
                "thumb_color": "#9f9f9f",
                "radius": 2,
            }
        }
