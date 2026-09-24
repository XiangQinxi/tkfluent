"""图片组件。

``FluImage`` 在 :class:`~tkflu.frame.FluFrame` 的基础上显示一张图片，
因此同时具备圆角背景、边框与主题切换能力。

.. code-block:: python

    import tkflu
    from tkflu.image import FluImage

    root = tkflu.FluWindow()
    FluImage(root, image="logo.png").pack(padx=16, pady=16)
    root.mainloop()

``image`` 参数可以传：

* 图片文件路径（``str`` 或 :class:`os.PathLike`，例如 ``pathlib.Path``）；
* 一个已经建好的 ``PhotoImage``（含 ``PIL.ImageTk.PhotoImage``）；
* 一个 ``PIL.Image.Image`` 对象（会自动经 ``ImageTk`` 转成 ``PhotoImage``）。

为什么图片必须画在**最上面**
----------------------------
``FluFrame`` 的内部结构是"画布 + 内嵌 Frame"，那个内嵌 Frame 是通过
``create_window`` 挂到画布上的**真实控件窗口**。Tk 里**嵌入的控件窗口永远
画在画布元素之上**，与创建顺序无关——所以早期实现"先让父类画背景、再
``create_image`` 叠图片"的做法根本没有生效：整张图被内嵌 Frame 盖住，
只剩边框内侧一圈露出来，看起来仍然是个空盒子。

这里的做法是：有图片时把内嵌 Frame 那个 window 元素 ``state="hidden"``，
图片按一小圈内边距居中画在画布上，圆角边框因此完整可见。
"""

from __future__ import annotations

import os
from tkinter import PhotoImage
from typing import Optional, Union

from .frame import FluFrame

__all__ = ["FluImage"]

#: 图片与面板边缘之间的内边距（像素）
IMAGE_PADDING = 4


class FluImage(FluFrame):
    """带圆角背景、可显示图片的 Fluent 容器。

    继承 :class:`~tkflu.frame.FluFrame`，因此圆角背景、主题切换、
    ``pack`` / ``grid`` / ``place`` 的代理方法与普通 FluFrame 一致。

    :param image: 图片路径 / ``PhotoImage`` / ``PIL.Image.Image``
    :param width: 未指定图片时的宽度
    :param height: 未指定图片时的高度
    :param padding: 图片与面板边缘之间的内边距
    """

    def __init__(
        self,
        master=None,
        *args,
        image: Optional[Union[str, os.PathLike, PhotoImage]] = None,
        width: int = 200,
        height: int = 150,
        mode: str = "light",
        style: str = "standard",
        padding: int = IMAGE_PADDING,
        **kwargs,
    ):
        # 必须在 super().__init__() 之前初始化：FluFrame 的构造函数里就会
        # 调用 self._draw()，而我们的 _draw 覆盖版会去读 _image_ref。
        #: 必须由 Python 侧持有引用，否则 PhotoImage 被回收后图片会消失
        self._image_ref = None
        self.element_image = None
        #: 图片与边缘之间的内边距
        self.padding = max(0, int(padding))

        super().__init__(
            master, *args, width=width, height=height, mode=mode, style=style, **kwargs
        )

        if image is not None:
            self.image(image)

    # ------------------------------------------------------------------
    def image(self, image=None):
        """设置或读取图片。

        :param image: 传 ``None`` 表示读取当前图片；否则为路径 /
            ``PhotoImage`` / ``PIL.Image.Image``
        :returns: 当前生效的 ``PhotoImage``
        :raises TypeError: 传入了不支持的类型
        :raises OSError: 文件不存在或不是可识别的图片

        .. note::
           传入图片后控件尺寸会被调整成「图片尺寸 + 两倍内边距」，
           这样圆角边框不会被图片的四角压掉。
        """
        if image is None:
            return self._image_ref

        photo = self._coerce_photo(image)
        self._image_ref = photo

        size = (photo.width(), photo.height())
        total = (size[0] + self.padding * 2, size[1] + self.padding * 2)
        self.config(width=total[0], height=total[1])
        self.canvas.config(width=total[0], height=total[1])

        # 立刻生效：窗口已存在时 canvas.config 会触发 <Configure> → _draw；
        # 还没映射时这里也要主动画一次，否则要等到窗口出现才有内容。
        self._draw()
        return photo

    def _coerce_photo(self, image):
        """把各种"图片"输入统一成 ``PhotoImage``。

        :raises TypeError: 类型不支持
        :raises OSError: 路径打不开
        """
        # 1) 路径（str 与 pathlib.Path 都算）
        if isinstance(image, (str, os.PathLike)):
            path = os.fspath(image)
            if not os.path.exists(path):
                raise FileNotFoundError(f"找不到图片文件：{path}")
            # master=self 很关键：不传时图片会挂到默认根窗口的解释器上，
            # 多 Tk 解释器场景下画布会报 "not a photo image"
            return PhotoImage(file=path, master=self)

        # 2) 已经是 PhotoImage 时直接使用。
        #    注意：PIL.ImageTk.PhotoImage **不是** tkinter.PhotoImage 的子类，
        #    所以还要按模块名认一次（它同样有 width()/height()，可直接交给画布）。
        if isinstance(image, PhotoImage):
            return image
        if (type(image).__module__ or "").startswith("PIL.ImageTk") and hasattr(
            image, "width"
        ):
            return image

        # 3) Pillow 的 Image：转成 PhotoImage 再交给画布
        if (type(image).__module__ or "").split(".")[0] == "PIL" and hasattr(
            image, "mode"
        ):
            try:
                from PIL import ImageTk
            except Exception as exc:  # pragma: no cover - Pillow 是硬依赖
                raise TypeError("需要 Pillow 才能显示 PIL.Image 对象") from exc
            return ImageTk.PhotoImage(image, master=self)

        raise TypeError(
            "image 只支持 文件路径 / os.PathLike / PhotoImage / PIL.Image，"
            f"收到 {type(image).__name__}"
        )

    def _draw(self, event=None, tempcolor=None):
        """先画圆角背景（父类），再把图片叠上去。

        覆盖父类是必需的：父类开头会 ``canvas.delete("all")``，
        如果图片元素是在别处创建的，任何一次重绘都会把它连带删掉——
        这正是"FluImage 看起来是个空盒子"的原因。
        """
        super()._draw(event, tempcolor)
        self._draw_image()

    def _draw_image(self):
        """把图片画在面板中央（重绘时会被重新调用）。

        同时把父类那个内嵌 Frame 的 window 元素隐藏掉——嵌入的控件窗口
        永远盖在画布元素之上，不隐藏就没法把图片露出来。没有图片时
        照常显示内嵌 Frame，此时 FluImage 的行为与普通 FluFrame 一致。
        """
        photo = getattr(self, "_image_ref", None)
        self._set_inner_window_visible(photo is None)
        if photo is None:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            # 布局尚未完成，退回到"图片尺寸 + 内边距"，避免画到 (0, 0)
            width = photo.width() + self.padding * 2
            height = photo.height() + self.padding * 2

        self.element_image = self.canvas.create_image(
            width / 2, height / 2, anchor="center", image=photo
        )
        # canvas 的图片引用同样需要 Python 侧保活，否则被回收后画面会空白
        self.canvas._keep_photo(self.element_image, photo)

    def _set_inner_window_visible(self, visible: bool):
        """显示/隐藏父类挂在画布上的内嵌 Frame 窗口。"""
        item = getattr(self, "element2", None)
        if item is None:
            return
        try:
            self.canvas.itemconfigure(item, state="normal" if visible else "hidden")
        except Exception:
            pass
