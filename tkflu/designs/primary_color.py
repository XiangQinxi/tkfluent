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
