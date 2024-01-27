# tkdeft

[![Netlify Status](https://api.netlify.com/api/v1/badges/c7626ce2-9556-4e4f-b28e-36dc0b513398/deploy-status)](https://app.netlify.com/sites/tkdeft/deploys)

意为`灵巧`，灵活轻巧好用

继`tkadw`之后的`tkinter`的现代化界面库

> 开发中

---

## 原理
先使用`svgwrite`进行矢量作图（默认会将其存储到临时文件夹中），再用`tksvg`打开图片，将图片利用`Canvas`或`Label`显示出来

> 这其中还是有些坑的，比如图片不显示等


## 计划
未来我打算先制作出`SunValley`设计的库然后就去做别的项目

设计来源： https://pixso.cn/community/file/ItC5JH1TOwj15EeOPcY7LQ?from_share

### 为什么不像tkadw一样做跟易用的主题？
因为`svg`能实现很多漂亮的组件，而我套的模板可能不对其它设计其太大的作用

所以我将这个设计库放在这里当做模板，供其它设计者参考使用。


## 更新日志
### 2024-01-22
发布`0.0.1`版本，模板组件包括`DButton`

### 2023-01-23
发布`0.0.2`版本，补充模板组件`DEntry`、`DFrame`、`DText`, `DBadge`

### 2023-01-25
发布`0.0.3` `0.0.4`版本，粗心了，两次补充依赖
发布`0.0.5`版本，模板组件主题由`theme(mode=..., style=...)`设置，不再使用如`DDarkButton`这样的，添加`DWindow.wincustom`自定义窗口（仅限Windows）
发布`0.0.6`版本，模板组件`DBadge`补充样式`style=accent`，并对自定义窗口进行稍微调整