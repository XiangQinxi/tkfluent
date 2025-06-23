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
