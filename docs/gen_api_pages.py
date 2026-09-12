"""重新生成 tkfluent 的 mkdocstrings API 页面。

每个页面就是三行：

.. code-block:: markdown

    # tkflu.<模块>

    ::: tkflu.<模块>

新增了公开模块之后，把它加进下面的 GROUPS 再跑一次即可。

用法（在 ``docs/`` 目录下）::

    python gen_api_pages.py            # 预览将要生成/更新哪些页面
    python gen_api_pages.py --write    # 实际写入
    python gen_api_pages.py --nav      # 只打印可直接粘进 mkdocs.yml 的 nav 片段
"""

from __future__ import annotations

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

# docs/gen_api_pages.py -> docs/docs/api/
DOCS = pathlib.Path(__file__).resolve().parent / "docs"

HEADER = "# {title}\n\n::: {target}\n"

#: 分组 -> [(模块路径, 显示标题)]
GROUPS = {
    "组件 Widgets": [
        ("badge", "FluBadge 徽标"),
        ("button", "FluButton 按钮"),
        ("togglebutton", "FluToggleButton 开关"),
        ("entry", "FluEntry 单行输入"),
        ("text", "FluText 多行文本"),
        ("label", "FluLabel 标签"),
        ("frame", "FluFrame 面板"),
        ("image", "FluImage 图片"),
        ("listbox", "FluListBox 列表"),
        ("scrollbar", "FluScrollBar 滚动条"),
        ("slider", "FluSlider 滑块"),
        ("menu", "FluMenu 菜单"),
        ("menubar", "FluMenuBar 菜单栏"),
        ("popupmenu", "FluPopupMenu 弹出菜单"),
        ("popupwindow", "FluPopupWindow 弹出窗口"),
        ("tooltip", "FluToolTip 提示气泡"),
    ],
    "窗口 Windows": [
        ("window", "FluWindow 主窗口"),
        ("toplevel", "FluToplevel 子窗口"),
        ("bwm", "BWm 窗口外观"),
        ("customwindow", "CustomWindow（实验）"),
        ("customwindow2", "WindowDragArea 拖拽区域"),
    ],
    "基础设施 Core": [
        ("constants", "constants 常量"),
        ("defs", "defs 便捷函数"),
        ("thememanager", "FluThemeManager 主题管理"),
        ("icons", "icons 窗口图标"),
        ("render_manager", "render_manager 重绘调度"),
        ("designs.renderer", "renderer 渲染引擎"),
    ],
    "设计规范 Designs": [
        ("designs", "designs 总览"),
        ("designs.button", "按钮配色"),
        ("designs.badge", "徽标配色"),
        ("designs.entry", "输入框配色"),
        ("designs.text", "文本框配色"),
        ("designs.frame", "面板配色"),
        ("designs.label", "标签配色"),
        ("designs.menubar", "菜单栏配色"),
        ("designs.scrollbar", "滚动条配色"),
        ("designs.slider", "滑块配色"),
        ("designs.tooltip", "提示配色"),
        ("designs.window", "窗口配色"),
        ("designs.gradient", "渐变工具"),
        ("designs.primary_color", "主色调"),
        ("designs.animation", "动画参数"),
        ("designs.design", "FluDesign 入口"),
        ("designs.fonts", "字体加载"),
    ],
}


def print_nav() -> None:
    print("  - API 文档:")
    print("      - api/index.md")
    print("      - api/tkflu.md")
    for group, modules in GROUPS.items():
        print(f"      - {group}:")
        for module, _ in modules:
            print(f"          - api/tkflu.{module}.md")


def main() -> int:
    write = "--write" in sys.argv

    if "--nav" in sys.argv:
        print_nav()
        return 0

    api_dir = DOCS / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for group, modules in GROUPS.items():
        print(f"--- {group} ---")
        for module, title in modules:
            filename = f"tkflu.{module}.md"
            path = api_dir / filename
            content = HEADER.format(
                title=f"tkflu.{module} · {title}", target=f"tkflu.{module}"
            )
            action = "更新" if path.exists() else "新建"
            print(f"  {action} api/{filename:36s} {title}")
            if write:
                path.write_text(content, encoding="utf-8")
            written += 1

    print(f"\n{'已写入' if write else '待写入'} {written} 个页面"
          + ("" if write else "（加 --write 实际写入）"))
    print("nav 片段：python gen_api_pages.py --nav")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
