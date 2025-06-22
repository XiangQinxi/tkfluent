from tkflu import *


root = FluWindow()

theme_manager = FluThemeManager(root)

menubar = FluMenuBar(root)
menubar.add_command(label="Item1", width=80, command=lambda: print("FluMenu1 -> Clicked"))
menubar.show()

button = FluToggleButton(
    text="Toggle Theme", command=lambda: toggle_theme(button, theme_manager)
)
button.pack(padx=3, pady=3, )

button2 = FluToggleButton(
    text="Toggle Button"
)
button2.pack(padx=3, pady=3, )

root.mainloop()