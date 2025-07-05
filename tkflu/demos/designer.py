from tkflu import *

set_animation_steps(10)
set_animation_step_time(10)

root = FluWindow()
root.title("tkfluent designer")
root.geometry("500x300")

theme_manager = FluThemeManager(root)

menubar = FluMenuBar(root)

menu1 = FluMenu()
menu1.geometry("90x90")
menu1.add_command(label="Light", command=lambda: theme_manager.mode("light"))
menu1.add_command(label="Dark", command=lambda: theme_manager.mode("dark"))

def func1():
    messagebox = FluToplevel()
    messagebox.geometry("300x200")

    label = FluLabel(messagebox, text="This is a example for tkfluent!", width=160, height=32)
    label.pack(anchor="center")

menubar.add_command(label="File", style="standard", width=40, command=lambda: print("File -> Clicked"))
menubar.add_cascade(label="Theme Mode", style="standard", width=85, menu=menu1)
menubar.add_command(label="About", style="standard", width=45, command=lambda: func1())

menubar.show()


root.mainloop()