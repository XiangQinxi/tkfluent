"""渲染引擎选择（tkfluent → tkdeft.engines 的适配层）。

历史上这里用环境变量存一个整数：``0`` = tksvg、``1`` = wand。现在真正的
引擎实现在 :mod:`tkdeft.engines`，本模块只负责：

* 保持 ``set_renderer(int)`` / ``get_renderer()`` 的行为不变（向后兼容）；
* 允许直接传引擎名：``set_renderer("skia")``；
* 在进程内把选择同步给 tkdeft 引擎注册表。

=========== ==================================================
``get_renderer()``  引擎
=========== ==================================================
0            tksvg（默认，保持既有行为）
1            wand
2            skia（进程内栅格，推荐）
3            pillow（进程内栅格，无额外依赖）
4            cairo（进程内栅格）
=========== ==================================================
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
        get_engine,
        get_engine_name,
        list_engines,
        set_engine,
    )


(
    RENDERER_INDEX,
    get_engine,
    get_engine_name,
    list_engines,
    set_engine,
) = _import_engines()

__all__ = [
    "set_renderer",
    "get_renderer",
    "get_renderer_name",
    "list_renderers",
    "get_engine",
    "set_engine",
    "list_engines",
    "RENDERER_INDEX",
    "MIN_TKDEFT_VERSION",
    "FluRenderer",
]

_ENV_KEY = "tkfluent.renderer"

_INDEX_OF = {name: index for index, name in RENDERER_INDEX.items()}


def _to_engine_ref(way):
    """把 ``set_renderer`` 的参数解析成 tkdeft 引擎标识。"""
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

    ``way`` 可以是整数编号（0-4）或引擎名（``"skia"`` / ``"pillow"`` /
    ``"cairo"`` / ``"tksvg"`` / ``"wand"``）。引擎不可用时抛 ``ValueError``，
    避免"以为开了 skia 其实还在走慢路径"。
    """
    engine = set_engine(_to_engine_ref(way))
    environ[_ENV_KEY] = str(_INDEX_OF.get(engine.name, 0))


def get_renderer() -> int:
    """当前渲染器编号（保持历史 API）。"""
    return int(environ.get(_ENV_KEY, "0"))


def get_renderer_name() -> str:
    """当前引擎名，比编号更直观。"""
    return get_engine_name()


def list_renderers():
    """列出 ``(编号, 引擎名, 是否可用)``。"""
    return [
        (index, name, list_engines().get(name, False))
        for index, name in sorted(RENDERER_INDEX.items())
    ]


class FluRenderer(object):
    """面向对象风格的渲染器开关（保留旧 API）。"""

    def renderer(self, way=None):
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
