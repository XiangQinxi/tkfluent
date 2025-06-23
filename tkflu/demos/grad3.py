from tkflu import *

set_animation_steps(20)
set_animation_step_time(20)

root = FluWindow()

theme_manager = FluThemeManager(root)

button = FluButton(root, text="Button", mode="light", style="standard", command=lambda: theme_manager.toggle())
button.pack(padx=20, pady=20, fill="both", expand="yes")

label = FluLabel(root, text="Label", mode="light")
label.pack(padx=20, pady=20, fill="both", expand="yes")

root.mainloop()