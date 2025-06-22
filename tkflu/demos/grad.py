import matplotlib.pyplot as plt
import numpy as np


def color_gradient(color1, color2, steps=10, output_format='both'):
    """
    生成颜色渐变序列
    :param color1: 起始颜色 (RGB元组或HEX字符串)
    :param color2: 结束颜色 (RGB元组或HEX字符串)
    :param steps: 渐变步数
    :param output_format: 输出格式 ('rgb', 'hex' 或 'both')
    :return: 渐变颜色列表
    """

    # 输入格式处理
    def parse_color(color):
        if isinstance(color, str):  # HEX格式
            color = color.lstrip('#')
            return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        return color  # 已经是RGB格式

    rgb1 = np.array(parse_color(color1))
    rgb2 = np.array(parse_color(color2))

    # 生成渐变
    gradient = []
    for t in np.linspace(0, 1, steps):
        rgb = rgb1 + (rgb2 - rgb1) * t
        rgb = np.round(rgb).astype(int)
        rgb_clipped = np.clip(rgb, 0, 255)  # 确保在0-255范围内
        gradient.append(rgb_clipped)

    # 格式转换
    result = []
    for color in gradient:
        r, g, b = color
        if output_format == 'rgb':
            result.append(tuple(color))
        elif output_format == 'hex':
            result.append(f"#{r:02x}{g:02x}{b:02x}")
        else:  # both
            result.append({
                'rgb': tuple(color),
                'hex': f"#{r:02x}{g:02x}{b:02x}"
            })

    return result


# 示例使用
if __name__ == "__main__":
    # 输入颜色 (支持RGB或HEX)
    start_color = "#FF0000"  # 红色
    end_color = (0, 0, 255)  # 蓝色

    # 生成渐变 (20个步骤)
    gradient = color_gradient(start_color, end_color, steps=20, output_format='both')

    # 打印输出
    print("颜色渐变序列:")
    for i, color in enumerate(gradient):
        print(f"{i + 1:2d}: RGB{color['rgb']} -> {color['hex']}")

    # 可视化展示
    plt.figure(figsize=(10, 2))
    for i, color in enumerate(gradient):
        plt.fill_between([i, i + 1], 0, 1, color=np.array(color['rgb']) / 255)
    plt.title("Color Gradient Visualization")
    plt.axis('off')
    plt.show()
