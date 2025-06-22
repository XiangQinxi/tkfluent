# tkfluent

`tkinter`现代化组件库。设计来于`Fluent` `WinUI3` 设计

![](https://learn.microsoft.com/zh-cn/windows/apps/images/logo-winui.png)

## 依赖图
```bash
PS .\tkfluent> poetry show --tree                                                                                                                                                                                        
easydict 1.13 Access dict values as attributes (works recursively).
pillow 10.4.0 Python Imaging Library (Fork)
svgwrite 1.4.3 A Python library to create SVG drawings.
tkdeft 0.0.9 使用tkinter+tksvg开发的现代化界面库
├── easydict >=1.13,<2.0
├── pillow >=10.2.0,<11.0.0
├── svgwrite >=1.4.3,<2.0.0
├── tkextrafont >=0.6.3,<0.7.0
│   └── scikit-build *
│       ├── distro *
│       ├── packaging *
│       ├── setuptools >=42.0.0
│       ├── tomli *
│       └── wheel >=0.32.0
└── tksvg >=0.7.4,<0.8.0
    └── scikit-build *
        ├── distro *
        ├── packaging *
        ├── setuptools >=42.0.0
        ├── tomli *
        └── wheel >=0.32.0
tkextrafont 0.6.3 Fonts loader for Tkinter
└── scikit-build *
    ├── distro *
    ├── packaging *
    ├── setuptools >=42.0.0
    ├── tomli *
    └── wheel >=0.32.0
tksvg 0.7.4 SVG support for PhotoImage in Tk 8.6
└── scikit-build *
    ├── distro *
    ├── packaging *
    ├── setuptools >=42.0.0
    ├── tomli *
    └── wheel >=0.32.0
```