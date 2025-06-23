class FluGradient:
    def hex_to_rgb(self, h: str):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def generate_rgb2hex(self, start_color, end_color, steps):
        """生成颜色渐变序列"""
        import numpy as np
        gradient = []
        for t in np.linspace(0, 1, steps):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            gradient.append(f"#{r:02x}{g:02x}{b:02x}")
        return gradient

    def generate_hex2hex(self, start_hex, end_hex, steps):
        """
        专为HEX颜色设计的渐变生成器
        :param start_hex: 起始颜色 HEX格式 (如 "#FF0000")
        :param end_hex: 结束颜色 HEX格式 (如 "#0000FF")
        :param steps: 渐变步数
        :return: HEX格式的颜色列表
        """

        # 去除#号并转换为RGB元组

        # RGB转HEX

        rgb_start = self.hex_to_rgb(start_hex)
        rgb_end = self.hex_to_rgb(end_hex)
        import numpy as np
        gradient = []
        if steps is None:
            return None
        for t in np.linspace(0, 1, steps):
            # 计算每个通道的中间值
            r = int(rgb_start[0] + (rgb_end[0] - rgb_start[0]) * t)
            g = int(rgb_start[1] + (rgb_end[1] - rgb_start[1]) * t)
            b = int(rgb_start[2] + (rgb_end[2] - rgb_start[2]) * t)

            # 确保值在0-255范围内并转换为HEX
            gradient.append(
                self.rgb_to_hex(
                    (
                        max(0, min(255, r)),
                        max(0, min(255, g)),
                        max(0, min(255, b))
                    )
                )
            )

        return gradient
