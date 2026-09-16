# 文档怎么维护

面向**改这个文档站的人**（不是给读者看的）。站点用 mkdocs + Material + mkdocstrings 构建。

## 目录结构

```
docs/
├── mkdocs.yml            站点配置（nav / 插件 / 扩展 / 锚点校验）
├── requirements.txt      文档工具链版本
├── gen_api_pages.py      生成 api/*.md（每个模块一个页面）
├── gen_figures.py        生成 docs/assets/*.png（插图）
├── diagrams/*.mmd        流程图源码（mermaid），由 gen_figures.py 渲染
└── docs/
    ├── index.md          主页
    ├── getstarted/       安装 / 上手 / 第一个应用
    ├── guide/            组件总览 / 架构 / 主题 / 运行演示 / 常见问题
    ├── tutorial/         主题切换 / 渲染引擎 / 提示气泡
    ├── api/              由 gen_api_pages.py + 源码 docstring 生成
    ├── assets/           插图（提交进仓库）
    ├── blog/index.md     更新日志入口（Material blog 插件）
    ├── blog/posts/       一个版本一篇：YYYY-MM-DD.md
    └── stylesheets/extra.css
```

## 改内容

| 想改什么 | 改哪里 |
| --- | --- |
| 说明文字、示例代码 | 对应的 `.md`（`docs/docs/**`） |
| 某个 API 的说明 | **改源码的文档字符串**，再重新生成 API 页 |
| 导航顺序、新增页面 | `mkdocs.yml` 的 `nav` |
| 插图样式、配色 | `docs/docs/stylesheets/extra.css` |

## 两个生成脚本

```bash
cd docs

python gen_api_pages.py            # 预览
python gen_api_pages.py --write    # 重建 api/*.md

python gen_figures.py              # 预览插图
python gen_figures.py --write      # 重建全部插图
python gen_figures.py --write --only widgets-light   # 只做一张
```

### 插图（`gen_figures.py`）

| 插图 | 怎么来的 |
| --- | --- |
| `widgets-light.png` / `widgets-dark.png` | 真起一个窗口把组件摆好，用 Win32 `PrintWindow` 抓**客户区**，再按 `winfo_rootx/rooty` 精确裁剪每一格 |
| `button-states.png` | 4 状态 × 3 样式 × 2 主题的真实按钮：`enter` / `button1` / `state` 设成对应状态后 `_draw()` |
| `gallery-light.png` / `gallery-dark.png` | 跑 `python -m tkflu` 的画廊并截整窗（含系统标题栏） |
| `theme-compare.png` | 上面两张并排 |
| `architecture.png` / `widget-anatomy.png` / `theme-flow.png` / `event-flow.png` / `svg-pipeline.png` | `diagrams/*.mmd` 经 mermaid-cli 渲染 |

!!! warning "流程图为什么是预渲染的图片"
    Material 的 mermaid 支持是**运行时从 unpkg CDN 拉脚本**的，而本站启用了
    `offline` 插件（离线可读）。直接写 ` ```mermaid ` 的话，离线打开只剩一段代码。
    所以流程图以 `diagrams/*.mmd` 为源、渲染成 PNG 提交进仓库。
    改图流程：改 `.mmd` → `python gen_figures.py --write` → 提交图片。

    渲染需要 Node（`npx`）与一个 Chromium 系浏览器（脚本会自动找 Edge / Chrome）。
    截图部分依赖 Windows 的 `PrintWindow`，非 Windows 平台会自动跳过截图、只渲染流程图。

### 页面里引用插图

```markdown
<figure markdown>
  ![说明](../assets/xxx.png)
  <figcaption>图注：写清楚这张图要说明什么</figcaption>
</figure>
```

`md_in_html` 扩展已经在 `mkdocs.yml` 里打开了，否则上面的写法会显示成字面文本。

## 本地预览与构建

```bash
cd docs
mkdocs serve -f mkdocs.yml            # 本地预览
mkdocs build --strict --site-dir /tmp/tkfluent-docs   # 严格构建（写到临时目录）
```

!!! danger "不要直接 `mkdocs build`"
    `docs/site` 是**已提交**的构建产物，直接 build 会覆盖它。一定带 `--site-dir`。

## 提交前的检查

```bash
cd ../..                       # 到 tkdeft 仓库根（两个站的检查都在那里）
python benchmarks/check_docs.py          # 两个文档站都构建一遍（--strict）
python benchmarks/check_docs.py tkfluent # 只构建 tkfluent
```

`--strict` 会把 WARNING 当 ERROR，能挡下 nav 缺失、正文死链、图片路径写错、
docstring 解析失败。锚点（`#xxx`）也已在 `mkdocs.yml` 里调成 `warn`——
**中文标题的锚点会被 slugify 成 `#_1` 这类**，要链接某个小节时请显式写 id：

```markdown
## 主题与配色 { #theme }
```

## 更新日志怎么写

在 `docs/docs/blog/posts/` 新增 `YYYY-MM-DD.md`，front matter 至少要有：

```yaml
---
draft: false
date: 2026-09-13
categories:
  - 0.3.0
---
```

首页与 README **不放**更新日志明细，只指向这里。
