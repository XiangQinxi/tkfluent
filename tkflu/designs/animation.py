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
    set_animation_steps(10)
if "tkfluent.animation_step_time" not in environ:
    set_animation_step_time(10)


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
