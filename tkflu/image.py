"""图片组件。

``FluImage`` 在 :class:`~tkflu.frame.FluFrame` 的基础上显示一张图片，
因此同时具备圆角背景、边框与主题切换能力。

.. code-block:: python

    import tkflu
    from tkflu.image import FluImage

    root = tkflu.FluWindow()
    FluImage(root, image="logo.png").pack(padx=16, pady=16)
    root.mainloop()

``image`` 参数既可以传图片文件路径，也可以传一个已经建好的 ``PhotoImage``
（用 ``PIL.ImageTk`` 生成的那种也可以）。
"""

from __future__ import annotations

from tkinter import PhotoImage
from typing import Optional, Union

from .frame import FluFrame

__all__ = ["FluImage"]


class FluImage(FluFrame):
    """带圆角背景、可显示图片的 Fluent 容器。

    继承 :class:`~tkflu.frame.FluFrame`，因此圆角背景、主题切换、
    ``pack`` / ``grid`` / ``place`` 的代理方法与普通 FluFrame 一致。

    :param image: 图片文件路径，或已有的 ``PhotoImage``
    :param width: 默认宽度（未指定图片时使用）
    :param height: 默认高度（未指定图片时使用）
    """

    def __init__(
        self,
        master=None,
        *args,
        image: Optional[Union[str, PhotoImage]] = None,
        width: int = 200,
        height: int = 150,
        mode: str = "light",
        style: str = "standard",
        **kwargs,
    ):
        super().__init__(
            master, *args, width=width, height=height, mode=mode, style=style, **kwargs
        )

        #: 必须由 Python 侧持有引用，否则 PhotoImage 被回收后图片会消失
        self._image_ref = None
        self.element_image = None

        if image is not None:
            self.image(image)

    # ------------------------------------------------------------------
    def image(self, image: Optional[Union[str, PhotoImage]] = None):
        """设置或读取图片。

        传 ``None`` 表示读取当前图片；传路径或 ``PhotoImage`` 表示替换。
        """
        if image is None:
            return self._image_ref

        if isinstance(image, str):
            # master=self 很关键：不传时图片会挂到默认根窗口的解释器上，
            # 多 Tk 解释器场景下画布会报 "not a photo image"
            photo = PhotoImage(file=image, master=self)
        else:
            photo = image

        self._image_ref = photo

        size = (photo.width(), photo.height())
        if self.element_image is not None:
            self.canvas.delete(self.element_image)
        self.element_image = self.canvas.create_image(
            size[0] / 2, size[1] / 2, anchor="center", image=photo
        )
        # canvas 的图片引用同样需要 Python 侧保活
        self.canvas._keep_photo(self.element_image, photo)

        self.config(width=size[0], height=size[1])
        self.canvas.config(width=size[0], height=size[1])
        self._draw()
        return photo
