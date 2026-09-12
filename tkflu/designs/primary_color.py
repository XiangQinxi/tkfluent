"""主色调（强调色）配置。

强调色按钮、开关等组件都从这里取色，用 ``set_primary_color`` 全局替换。

.. code-block:: python

    from tkflu import purple_primary_color

    purple_primary_color()      # 换成紫色"""

from os import environ


def set_primary_color(color: tuple = None):
    from json import dumps

    environ["tkfluent.primary_color"] = dumps(color)


def get_primary_color():
    from json import loads

    return loads(environ["tkfluent.primary_color"])


if "tkfluent.primary_color" not in environ:
    set_primary_color(("#005fb8", "#60cdff"))


class FluPrimaryColor(object):
    def primary_color(self, color: tuple = None):
        if color:
            from json import dumps
            from os import environ

            environ["tkfluent.primary_color"] = dumps(color)
        else:
            from json import loads
            from os import environ

            return loads(environ["tkfluent.primary_color"])
