from tkflu import *

set_renderer(1)
set_animation_steps(10)
set_animation_step_time(10)

root = FluWindow()
root.title("tkfluent designer")
root.geometry("600x300")

theme_manager = FluThemeManager(root)

menubar = FluMenuBar(root)

menu1 = FluMenu()
menu1.geometry("90x90")
menu1.add_command(label="Light", command=lambda: theme_manager.mode("light"))
menu1.add_command(label="Dark", command=lambda: theme_manager.mode("dark"))


def func1():
    messagebox = FluToplevel()
    messagebox.geometry("300x200")

    label = FluLabel(
        messagebox, text="This is a example for tkfluent!", width=160, height=32
    )
    label.pack(anchor="center")


style = "menu"

menubar.add_command(
    label="File", style=style, width=40, command=lambda: print("File -> Clicked")
)
menubar.add_cascade(label="Theme Mode", style=style, width=85, menu=menu1)
menubar.add_command(label="About", style=style, width=45, command=lambda: func1())

menubar.show()

widgets = FluFrame(root, width=100)

widgets.title = FluLabel(widgets, text="Widgets", width=100)
widgets.title.pack(fill="x", side="top")

widgets.pack(fill="y", side="left", padx=10, pady=10)

windows = FluFrame(root, width=300)
windows.pack(fill="y", side="left", expand="yes", anchor="center", padx=10, pady=10)

configs = FluFrame(root, width=200)
configs.pack(fill="y", side="right", padx=10, pady=10)

root.mainloop()
