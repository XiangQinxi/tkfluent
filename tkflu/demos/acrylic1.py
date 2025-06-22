from tkflu import *
from pywinstyles import *


root = FluWindow()

thememanager = FluThemeManager()
thememanager.mode("dark")

root.dconfigure(back_color="#000000")

btn1 = FluButton(root, text="Normal", command=lambda: apply_style(root, "normal"))
btn1.pack(padx=5, pady=5)

btn2 = FluButton(root, text="Acrylic", command=lambda: apply_style(root, "acrylic"))
btn2.pack(padx=5, pady=5)

root.mainloop()
