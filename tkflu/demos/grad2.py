from tkflu import *

set_animation_steps(20)
set_animation_step_time(50)

root = FluWindow()

theme_manager = FluThemeManager(root)

frame = FluFrame(root, mode="light", style="standard")

btn = FluButton(frame, text="Button", mode="light", style="standard", command=lambda: theme_manager.toggle())
btn.pack(padx=20, pady=20, fill="both", expand="yes")

frame.pack(padx=20, pady=20, fill="both", expand="yes")

root.mainloop()