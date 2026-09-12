# 安装

库名叫做`tkfluent`，但导入时要使用`tkflu`这缩减名称

!!! info "用PIP下载"
    ``` bash
    pip install tkfluent
    ```
    中国国内镜像源
    ```bash
    pip install tkfluent -i https://pypi.tuna.tsinghua.edu.cn/simple
    ``` 

!!! info "从Github下载"
    
    从[Releases](https://github.com/XiangQinxi/tkfluent/releases/)下载`tkfluent-x.x.x-py3-none-any.whl`
    
    !!! tip ""
        注意替换本地下载的文件名
    ``` bash
    pip install tkfluent-x.x.x-py3-none-any.whl 
    ```

!!! info "克隆项目并编译安装"
    由于本项目是使用`poetry`打包的，所以需要安装`poetry`进行编译
    ```bash
    pip install poetry -U
    ```

    中国国内镜像源
    ```bash
    pip install poetry -U -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```
    克隆项目至本地
    ```bash
    git clone https://github.com/XiangQinxi/tkfluent.git
    ```
    编译并安装
    ```bash
    cd tkfluent
    poetry install
    poetry build
    pip install dist/tkfluent-x.x.x-py3-none-any.whl
    ```

## 版本要求：tkfluent 0.2.0 需要 tkdeft >= 0.2.0

`tkfluent` 的绘制后端由 [`tkdeft`](https://pypi.org/project/tkdeft) 提供。
从 **0.2.0** 开始，`tkdeft` 增加了可插拔的**绘制引擎层**（`tkdeft.engines`），
`skia` / `pillow` / `cairo` 这几个进程内栅格引擎都在里面。

如果环境里还是旧版 `tkdeft`，导入 `tkflu` 时会看到：

```text
ModuleNotFoundError: No module named 'tkdeft.engines'
```

!!! tip "怎么修"
    正常 `pip install tkfluent` 会自动带上正确的 `tkdeft`。
    只有在**本地开发**（两个仓库都在本机）时才容易踩到，因为 IDE 会把项目根
    加进 `sys.path`，于是 `import tkflu` 用的是本地新代码，而 `tkdeft`
    仍解析到 site-packages 里的旧版本。

    最稳的做法是把两个仓库都装成"可编辑"模式：

    ```bash
    pip install -e ../tkdeft      # 先装被依赖的
    pip install -e .              # 再装 tkfluent
    ```

    装完可以用一句话确认环境是否正确：

    ```bash
    python -c "import tkdeft; print(tkdeft.__version__, tkdeft.__file__)"
    # 期望输出 0.2.0 以及你本地 tkdeft 仓库的路径
    ```

    也可以临时用环境变量指定，不安装：

    ```bash
    set PYTHONPATH=C:\path\to\tkdeft        # Windows
    export PYTHONPATH=/path/to/tkdeft       # macOS / Linux
    ```

!!! note "关于 Pillow 版本"
    `tkdeft` / `tkfluent` 对 Pillow **不设上界**（`>=10.2`），
    Pillow 10 / 11 / 12 均已实测可用。这样安装时不会把你环境里已经装好的
    新版 Pillow 降级。

