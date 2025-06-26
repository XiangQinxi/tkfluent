from tkinter import Tk, Frame
from tkflu import *

root = FluWindow(mode="dark")
root.geometry("300x100")

slider = FluSlider(value=50, mode="dark")
slider.dconfigure(max=-100, min=100, value=0)
slider.pack(fill="x", padx=10, pady=10)

button = FluButton(text="Check Value", mode="dark", command=lambda: print(slider.dcget("value")))
button.pack(fill="x", padx=10, pady=10)

root.mainloop()