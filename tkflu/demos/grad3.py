from tkflu import *


root = FluWindow()

theme_manager = FluThemeManager(root)

menubar = FluMenuBar(root)
for i in range(5):
    menubar.add_command(label=f"Item{i+1}")
menubar.show()

btn = FluButton(root, text="Button", mode="light", style="standard", command=lambda: theme_manager.toggle())
btn.pack(padx=20, pady=20, fill="both", expand="yes")

root.mainloop()