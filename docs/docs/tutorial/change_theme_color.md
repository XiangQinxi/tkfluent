# 修改主题色

## 主题色
### 红色
![红色主题色Dark](red_light.png)
![红色主题色Dark](red_dark.png)
### 蓝色
![蓝色主题色Dark](blue_light.png)
![蓝色主题色Dark](blue_dark.png)

## 修改主题色
修改主题色可以使用以下方法

导入方法
```python
from tkflu.designs.primary_color import set_primary_color
```
设置主题色
```python
set_primary_color((color1, color2))
```
其中`color1`为浅色主题时的主题色，`color2`为深色主题时的主题色

> 可参见[修改主题模式（深浅模式）](change_theme_mode.md)

### 最佳实践建议
1. **保持视觉一致性**：
   - 浅色和深色模式的主题色应保持相同色系
   - 深色模式颜色通常应比浅色模式更亮（在暗背景上更显眼）

2. **性能考虑**：
   - 避免频繁调用此方法
   - 如需测试多个颜色，建议使用窗口预览模式

3. **用户体验建议**：
   - 提供有限的精选配色方案供用户选择
   - 将用户选择的主题色保存到配置文件