"""动画参数。

控制主题切换等过渡动画的帧数与帧间隔。

.. code-block:: python

    from tkflu import set_animation_steps, set_animation_step_time

    set_animation_steps(5)        # 5 帧
    set_animation_step_time(20)   # 每帧 20ms

两者都设为 0 即关闭动画（默认就是关闭）。"""

from os import environ


def set_animation_steps(steps: int):
    environ["tkfluent.animation_steps"] = str(steps)


def get_animation_steps():
    return int(environ["tkfluent.animation_steps"])


def set_animation_step_time(step_time: int):
    environ["tkfluent.animation_step_time"] = str(step_time)


def get_animation_step_time():
    return int(environ["tkfluent.animation_step_time"])


if "tkfluent.animation_steps" not in environ:
    set_animation_steps(0)
if "tkfluent.animation_step_time" not in environ:
    set_animation_step_time(0)


class FluAnimation(object):
    def animation_steps(self, steps: int = None):
        if steps:
            from os import environ

            environ["tkfluent.animation_steps"] = str(steps)
        else:
            from os import environ

            return int(environ["tkfluent.animation_steps"])

    def animation_step_time(self, step_time: int = None):
        if step_time:
            from os import environ

            environ["tkfluent.animation_step_time"] = str(step_time)
        else:
            from os import environ

            return int(environ["tkfluent.animation_step_time"])
