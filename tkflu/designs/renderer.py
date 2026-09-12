from os import environ


def set_renderer(way: int):
    environ["tkfluent.renderer"] = str(way)


def get_renderer():
    return int(environ["tkfluent.renderer"])


if "tkfluent.renderer" not in environ:
    set_renderer(0)


class FluRenderer(object):
    def renderer(self, way: int = None):
        if way:
            environ["tkfluent.renderer"] = str(way)
        else:
            return int(environ["tkfluent.renderer"])
