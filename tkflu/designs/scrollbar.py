"""滚动条的设计规范。

数值来源：Figma 设计稿 ``Scrolling.svg``（该文件的图层名也是可读的，
``Scroll Bar / Parts / Track``、``Scroll Bar / Parts / Thumb``、
``Mode=…, Orientation=…, Expanded=…``）。经 96 dpi 栅格逐像素复核。

================== ==========================================================
项                  设计稿
================== ==========================================================
控件外框            厚 14px（轨道 12 + 每边 1 内缩）
轨道                厚 12px、圆角 6（整条胶囊）、只在展开态出现
滑块（收起）        厚 **2**px、圆角 1（整条胶囊）
滑块（展开）        厚 **6**px、圆角 3
定位边距            轨道居中于 14px 外框内
================== ==========================================================

配色（合成到各自的面板上之后的实色）：

======== ============ ============
项       浅色（#FAFAFA） 深色（#1C1C1C）
======== ============ ============
滑块       #8A8A8A      #989898
滑块（展开） #8B8B8B      #9F9F9F
轨道       #FCFCFC      #2C2C2C
======== ============ ============

.. note::
   设计稿里**收起态不画轨道**，只有一条细滑块；展开（悬停）时才出现轨道，
   同时滑块变粗。按下 / 禁用两个状态在这份文件里**完全不存在**
   （全文检索不到 pressed / disabled / PointerOver 等字样），
   这里保留历史值，不做推测。
"""


def scrollbar(mode):
    """取滚动条的配色表。

    :param mode: ``"light"`` / ``"dark"``
    :returns: ``{"rest": {...}, "expand": {...}, "disabled": {...}}``
    """
    if str(mode).lower() == "dark":
        return {
            "rest": {
                "thumb_color": "#989898",
                "radius": 1,
                "thickness": 2,
            },
            "expand": {
                "track_color": "#2c2c2c",
                "thumb_color": "#9f9f9f",
                "radius": 3,
                "thickness": 6,
            },
            "disabled": {
                "thumb_color": "#515151",
                "radius": 1,
                "thickness": 2,
            },
        }
    return {
        "rest": {
            "thumb_color": "#8a8a8a",
            "radius": 1,
            "thickness": 2,
        },
        "expand": {
            "track_color": "#fcfcfc",
            "thumb_color": "#8b8b8b",
            "radius": 3,
            "thickness": 6,
        },
        "disabled": {
            "thumb_color": "#9f9f9f",
            "radius": 1,
            "thickness": 2,
        },
    }
