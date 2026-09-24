"""文档内链自检：相对链接与锚点是否存在。

为什么单独写一个
----------------
``mkdocs build --strict`` 本来就是这道闸门（见 tkdeft 的
``benchmarks/check_docs.py``）。但它在**受限执行环境**里跑不起来：
Material 的 blog 插件用 ``tempfile.mkdtemp()`` 建临时目录（Windows 下是 0700），
有些受限环境不允许往里写，于是构建在 ``on_files`` 阶段就抛
``PermissionError``。这个脚本只读文件、不建临时目录，任何环境都能跑，
用来做一次快速兜底。

它查两件 `--strict` 会管、但肉眼很容易漏的事：

1. ``](相对路径)`` 指向的文件不存在；
2. ``](xxx.md#锚点)`` 里的锚点在目标文件里不存在。

**中文标题的锚点尤其容易错**：``## 过渡动画`` 的锚点不是 ``#过渡动画``，
而是 ``#_5`` 这类。需要被链接的小节必须显式写 id：``## 过渡动画 {: #x }``
（注意 attr_list 语法里的**冒号**，写成 ``{ #x }`` 会被当成普通文字渲染出来）。

用法（在 ``docs/`` 目录下）::

    python check_links.py
"""

from __future__ import annotations

import pathlib
import re
import sys
from urllib.parse import unquote

sys.stdout.reconfigure(encoding="utf-8")

DOCS = pathlib.Path(__file__).resolve().parent / "docs"

_LINK = re.compile(r"\]\(([^)]+)\)")
_FENCE = re.compile(r"```.*?```", re.S)
_EXPLICIT_ID = re.compile(r"\{:\s*#([\w-]+)\s*\}|\{#([\w-]+)\s*\}")
_SKIP_SCHEMES = ("http://", "https://", "#", "mailto:", "tel:")


def anchors_of(path: pathlib.Path) -> set:
    """目标文件里所有可被链接的锚点（显式 id + 各级标题原文）。"""
    text = path.read_text(encoding="utf-8")
    found = set()
    for match in _EXPLICIT_ID.finditer(text):
        found.add(match.group(1) or match.group(2))
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        title = re.sub(r"\{.*?\}", "", line.lstrip("#")).strip()
        if title:
            found.add(title)
            found.add(title.lower().replace(" ", "-"))
    return found


def check() -> list:
    problems = []
    files = sorted(DOCS.rglob("*.md"))
    for path in files:
        if "site" in path.parts:
            continue
        text = _FENCE.sub("", path.read_text(encoding="utf-8"))
        for match in _LINK.finditer(text):
            target = match.group(1).strip()
            if target.startswith(_SKIP_SCHEMES):
                continue
            file_part, _, anchor = target.partition("#")
            if not file_part:
                continue
            # 文件名里带空格时写法是 %20（见 blog/posts/2025.6.26.md 的 gif），
            # 比对磁盘前要先解码，否则会把好链接误报成"文件不存在"。
            resolved = (path.parent / unquote(file_part)).resolve()
            shown = path.relative_to(DOCS.parent)
            if not resolved.exists():
                problems.append(f"{shown} -> {target}  文件不存在")
                continue
            if anchor and resolved.suffix == ".md":
                if anchor not in anchors_of(resolved):
                    problems.append(f"{shown} -> {target}  锚点不存在")
    return files, problems


def check_nav() -> list:
    """``mkdocs.yml`` 的 nav 指向的每个文件都必须存在。

    这是 ``--strict`` 会拦、但改 nav 时特别容易漏的一类：新增一个 API 页
    却忘了加进 nav，页面就建成孤儿（反过来，nav 里留着已删文件就直接报错）。
    """
    config = pathlib.Path(__file__).resolve().parent / "mkdocs.yml"
    text = config.read_text(encoding="utf-8")
    problems = []
    seen = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and stripped.endswith(".md"):
            target = stripped[2:].strip()
            if target in seen:
                continue
            seen.add(target)
            if not (DOCS / target).exists():
                problems.append(f"mkdocs.yml nav -> {target}  文件不存在")
    return problems


def main() -> int:
    files, problems = check()
    problems += check_nav()
    print(f"检查了 {len(files)} 个 markdown 文件，问题 {len(problems)} 个")
    for item in problems:
        print("  ", item)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
