import tkinter as tk
from tkinter import ttk
import numpy as np


class GradientLabelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter渐变标签演示")
        self.root.geometry("400x200")

        # 渐变控制变量
        self.is_animating = False
        self.current_step = 0
        self.gradient_steps = 20  # 渐变步数

        # 创建UI组件
        self.create_widgets()

        # 预生成渐变序列 (从蓝色到红色)
        self.gradient = self.generate_gradient_hex(
            "#ffffff",
            "#005fb8",
            self.gradient_steps
        )

    def create_widgets(self):
        """创建界面组件"""
        # 渐变显示标签
        self.label = tk.Label(
            self.root,
            text="渐变背景标签",
            font=('Arial', 20),
            relief='raised',
            borderwidth=2
        )
        self.label.pack(pady=20, ipadx=50, ipady=30, fill='x', padx=20)

        # 控制按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        # 开始按钮
        self.start_button = ttk.Button(
            button_frame,
            text="开始渐变",
            command=self.toggle_animation
        )
        self.start_button.pack(side='left', padx=5)

        # 重置按钮
        ttk.Button(
            button_frame,
            text="重置",
            command=self.reset_animation
        ).pack(side='left', padx=5)

    def generate_gradient(self, start_color, end_color, steps):
        """生成颜色渐变序列"""
        gradient = []
        for t in np.linspace(0, 1, steps):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            gradient.append(f"#{r:02x}{g:02x}{b:02x}")
        return gradient

    def generate_gradient_hex(self, start_hex, end_hex, steps):
        """
        专为HEX颜色设计的渐变生成器
        :param start_hex: 起始颜色 HEX格式 (如 "#FF0000")
        :param end_hex: 结束颜色 HEX格式 (如 "#0000FF")
        :param steps: 渐变步数
        :return: HEX格式的颜色列表
        """

        # 去除#号并转换为RGB元组
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

        # RGB转HEX
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

        rgb_start = hex_to_rgb(start_hex)
        rgb_end = hex_to_rgb(end_hex)

        gradient = []
        for t in np.linspace(0, 1, steps):
            # 计算每个通道的中间值
            r = int(rgb_start[0] + (rgb_end[0] - rgb_start[0]) * t)
            g = int(rgb_start[1] + (rgb_end[1] - rgb_start[1]) * t)
            b = int(rgb_start[2] + (rgb_end[2] - rgb_start[2]) * t)

            # 确保值在0-255范围内并转换为HEX
            gradient.append(rgb_to_hex((
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b))
            )))

        return gradient

    def toggle_animation(self):
        """切换动画状态"""
        self.is_animating = not self.is_animating
        self.start_button.config(
            text="停止渐变" if self.is_animating else "开始渐变"
        )
        if self.is_animating:
            self.animate_gradient()

    def animate_gradient(self):
        """执行渐变动画"""
        if not self.is_animating:
            return

        # 更新标签背景色
        color = self.gradient[self.current_step]
        self.label.config(background=color)

        # 更新步进
        self.current_step = (self.current_step + 1) % len(self.gradient)

        # 50ms后继续下一帧 (约20FPS)
        self.root.after(50, self.animate_gradient)

    def reset_animation(self):
        """重置动画状态"""
        self.is_animating = False
        self.current_step = 0
        self.start_button.config(text="开始渐变")
        self.label.config(background='SystemButtonFace')  # 恢复默认背景色


if __name__ == "__main__":
    root = tk.Tk()
    app = GradientLabelApp(root)
    root.mainloop()
