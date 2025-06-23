from tkflu import *

root = FluWindow()
root.title("tkfluent designer")
root.geometry("500x300")

theme_manager = FluThemeManager(root)

menubar = FluMenuBar(root)

menu1 = FluMenu()
menu1.geometry("90x90")
menu1.add_command(label="Light", command=lambda: theme_manager.mode("light"))
menu1.add_command(label="Dark", command=lambda: theme_manager.mode("dark"))

menubar.add_command(label="File", style="standard", width=40, command=lambda: print("File -> Clicked"))
menubar.add_cascade(label="Theme Mode", style="standard", width=100, menu=menu1)

menubar.show()


root.mainloop()