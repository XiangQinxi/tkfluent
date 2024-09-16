from tkflu import *

root = FluWindow()

manager = FluThemeManager()

style = ACCENT
mode = DARK

button1 = FluButton(text="FluButton", style=MENU, state=NORMAL)
button1.pack(fill="both", expand="yes", padx=5, pady=5)

button2 = FluButton(text="FluButton", style=MENU, state=DISABLED)
button2.pack(fill="both", expand="yes", padx=5, pady=5)

frame = FluFrame()

button3 = FluButton(frame, text="FluButton", style=style, state=NORMAL)
button3.pack(fill="both", expand="yes", padx=5, pady=5)

button4 = FluButton(frame, text="FluButton", style=style, state=DISABLED)
button4.pack(fill="both", expand="yes", padx=5, pady=5)

frame.pack(fill="both", expand="yes", padx=5, pady=5)

manager.mode(mode)

root.mainloop()