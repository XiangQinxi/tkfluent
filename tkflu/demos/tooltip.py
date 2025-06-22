from tkflu import *


root = FluWindow()

thememanager = FluThemeManager(root, mode="dark")

button = FluButton(root, text="Click me", command=lambda: print("Clicked"), style="standard")
button.pack()

tooltip = FluToolTip(button, text="This is a tooltip")

root.mainloop()