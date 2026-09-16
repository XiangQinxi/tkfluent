"""渲染引擎选择（tkfluent → :mod:`tkdeft.engines` 的适配层）。

历史上这里用环境变量存一个整数：``0`` = tksvg、``1`` = wand。现在真正的
引擎实现在 :mod:`tkdeft.engines`，本模块只负责：

* 保持 ``set_renderer(int)`` / ``get_renderer()`` 的行为不变（向后兼容）；
* 允许直接传引擎名：``set_renderer("skia")``；
* 在进程内把选择同步给 tkdeft 引擎注册表。

编号与引擎名的对应关系
----------------------
=========== ==================================================
``get_renderer()``  引擎
=========== ==================================================
0            tksvg（默认，保持既有行为）
1            wand
2            skia（进程内栅格，推荐）
3            pillow（进程内栅格，无额外依赖）
4            cairo（进程内栅格）
=========== ==================================================

这张表就是 :data:`tkdeft.engines.RENDERER_INDEX`，tkfluent 不再自己维护一份。

用法
----
::

    from tkflu import set_renderer, get_renderer_name, list_renderers

    set_renderer("skia")        # 或 set_renderer(2)
    get_renderer()              # -> 2
    get_renderer_name()         # -> "skia"
    list_renderers()            # -> [(0, 'tksvg', True), (1, 'wand', True), ...]

组件内部要"按引擎分支"时，只需要判断 ``get_renderer() == 1``（Wand 的历史特例），
其余情况（含新增的栅格引擎）都走默认几何。
"""

from __future__ import annotations

from os import environ

#: tkfluent 需要的 tkdeft 最低版本 —— 绘制引擎层（tkdeft.engines）从 0.2.0 开始提供
MIN_TKDEFT_VERSION = (0, 2, 0)

_MISSING_ENGINES_MESSAGE = """\
tkfluent 需要 tkdeft >= {required}，但当前环境里的 tkdeft 不提供 tkdeft.engines。

当前 tkdeft：
    版本: {version}
    位置: {location}

tkdeft.engines（可插拔绘制引擎层）是 0.2.0 新增的，旧版本没有这个子包。

解决办法（任选其一）：

  1) 升级已安装的版本
       pip install -U tkdeft

  2) 本地开发时，把仓库里的 tkdeft 以"可编辑"方式装进当前环境
       pip install -e <tkdeft 仓库路径>
     例如：
       pip install -e "{local_hint}"

  3) 临时把 tkdeft 仓库加到 PYTHONPATH（不安装）
       set PYTHONPATH=<tkdeft 仓库路径>

原始错误：{error}
""".strip()


def _describe_tkdeft() -> "dict[str, str]":
    """收集当前环境里 tkdeft 的版本与位置，用于生成可操作的报错信息。"""
    import os.path

    info = {"version": "未知", "location": "未知", "local_hint": "<tkdeft 仓库路径>"}
    try:
        import tkdeft

        info["version"] = getattr(tkdeft, "__version__", "未声明 __version__（早于 0.2.0）")
        path = getattr(tkdeft, "__file__", None)
        if path:
            info["location"] = os.path.dirname(path)
    except Exception:
        info["version"] = "无法导入 tkdeft"
    # 猜一个常见的仓库位置，只用于示例命令
    guess = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        "tkdeft",
    )
    if os.path.isdir(guess):
        info["local_hint"] = guess
    return info


def _import_engines():
    """导入 tkdeft.engines，失败时给出可操作的说明。"""
    try:
        from tkdeft.engines import (  # noqa: F401
            RENDERER_INDEX,
            describe_engines,
            engine_index,
            get_engine,
            get_engine_name,
            list_engines,
            set_engine,
        )
    except ImportError as exc:
        info = _describe_tkdeft()
        raise ImportError(
            _MISSING_ENGINES_MESSAGE.format(
                required=".".join(str(p) for p in MIN_TKDEFT_VERSION),
                error=f"{type(exc).__name__}: {exc}",
                **info,
            )
        ) from exc
    return (
        RENDERER_INDEX,
        describe_engines,
        engine_index,
        get_engine,
        get_engine_name,
        list_engines,
        set_engine,
    )


(
    _renderer_index,
    _describe_engines,
    _engine_index,
    _get_engine,
    _get_engine_name,
    _list_engines,
    _set_engine,
) = _import_engines()

#: 编号 → 引擎名（就是 ``tkdeft.engines.RENDERER_INDEX``）
RENDERER_INDEX = _renderer_index
#: 引擎的结构化信息列表（转自 ``tkdeft.engines.describe_engines``）
describe_engines = _describe_engines
#: 取引擎编号（转自 ``tkdeft.engines.engine_index``）
engine_index = _engine_index
#: 取引擎实例（转自 ``tkdeft.engines.get_engine``）
get_engine = _get_engine
#: 取当前引擎名（转自 ``tkdeft.engines.get_engine_name``）
get_engine_name = _get_engine_name
#: 列出 ``{引擎名: 是否可用}``（转自 ``tkdeft.engines.list_engines``）
list_engines = _list_engines
#: 切换引擎（转自 ``tkdeft.engines.set_engine``）
set_engine = _set_engine

__all__ = [
    "set_renderer",
    "get_renderer",
    "get_renderer_name",
    "list_renderers",
    "renderer_description",
    "get_engine",
    "set_engine",
    "list_engines",
    "describe_engines",
    "engine_index",
    "RENDERER_INDEX",
    "MIN_TKDEFT_VERSION",
    "FluRenderer",
]

#: 环境变量名：保存当前渲染器编号，兼容"先 set_renderer 再 import 组件"的用法
_ENV_KEY = "tkfluent.renderer"

#: 引擎名 → 编号
_INDEX_OF = {name: index for index, name in RENDERER_INDEX.items()}


def _to_engine_ref(way):
    """把 ``set_renderer`` 的参数解析成 tkdeft 引擎标识。

    :param way: 整数编号（0–4）或引擎名（``"skia"`` …）
    :returns: 引擎名（原样传给 :func:`tkdeft.engines.set_engine`）
    :raises ValueError: 编号不在 :data:`RENDERER_INDEX` 里
    """
    if isinstance(way, bool) or not isinstance(way, int):
        return way
    if way in RENDERER_INDEX:
        return RENDERER_INDEX[way]
    raise ValueError(
        f"未知的渲染器编号 {way!r}；可用：{RENDERER_INDEX}，或直接传引擎名 "
        f"{sorted(list_engines())}"
    )


def set_renderer(way) -> None:
    """切换渲染引擎。

    :param way: 整数编号（0–4）或引擎名（``"skia"`` / ``"pillow"`` /
        ``"cairo"`` / ``"tksvg"`` / ``"wand"``）

    引擎不可用时抛 ``ValueError``，避免"以为开了 skia 其实还在走慢路径"。
    选择会同步给 tkdeft 的引擎注册表，并记在环境变量里以便子进程继承。
    """
    engine = set_engine(_to_engine_ref(way))
    environ[_ENV_KEY] = str(_INDEX_OF.get(engine.name, 0))


def get_renderer() -> int:
    """当前渲染器编号（保持历史 API）。

    :returns: ``0``–``4``；组件里判"是不是 Wand"用 ``get_renderer() == 1``
    """
    return int(environ.get(_ENV_KEY, "0"))


def get_renderer_name() -> str:
    """当前引擎名，比编号更直观。"""
    return get_engine_name()


def list_renderers():
    """列出 ``(编号, 引擎名, 是否可用)``。

    ::

        >>> list_renderers()
        [(0, 'tksvg', True), (1, 'wand', True), (2, 'skia', True), ...]
    """
    available = list_engines()
    return [
        (index, name, available.get(name, False))
        for index, name in sorted(RENDERER_INDEX.items())
    ]


def renderer_description(name) -> str:
    """取某个引擎的一句话说明（用于 ``--list-engines`` 之类的输出）。

    :param name: 引擎名；未知名字时返回空字符串
    """
    for row in describe_engines():
        if row["name"] == str(name).lower():
            return row.get("description", "")
    return ""


class FluRenderer(object):
    """面向对象风格的渲染器开关（保留旧 API）。

    ::

        renderer = FluRenderer()
        renderer.renderer("skia")      # 设置
        renderer.renderer()            # 读取，-> 2
    """

    def renderer(self, way=None):
        """读写当前渲染器。

        :param way: ``None`` 表示只读；否则等价于 :func:`set_renderer`
        :returns: 读取时返回编号，设置时返回 ``None``
        """
        if way is None:
            return get_renderer()
        set_renderer(way)
        return None


# 模块导入时把环境变量里的选择同步给引擎注册表，兼容"先 set_renderer 再 import"的用法
if _ENV_KEY in environ:
    try:
        set_engine(RENDERER_INDEX[int(environ[_ENV_KEY])])
    except (ValueError, KeyError, TypeError):
        pass
else:
    set_renderer(0)
