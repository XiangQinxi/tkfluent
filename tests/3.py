from tkinter import Tk, Frame
from tkflu.button import FluButton

root = Tk()

frame1 = Frame(background="#ffffff")
frame2 = Frame(background="#202020")

frame1.pack(fill="both", expand="yes", side="left")
frame2.pack(fill="both", expand="yes", side="right")

btn1 = FluButton(frame1, text="Light", mode="light")
btn2 = FluButton(frame1, text="Light.Accent", mode="light", style="accent")
btn3 = FluButton(frame1, text="Light.Menu", mode="light", style="menu")
btn4 = FluButton(frame2, text="Dark", mode="dark")
btn5 = FluButton(frame2, text="Dark.Aceent", mode="dark", style="accent")
btn6 = FluButton(frame2, text="Dark.Menu", mode="dark", style="menu")

btn1.pack(fill="x", side="top", padx=5, pady=5)
btn2.pack(fill="x", side="top", padx=5, pady=5)
btn3.pack(fill="x", side="top", padx=5, pady=5)
btn4.pack(fill="x", side="top", padx=5, pady=5)
btn5.pack(fill="x", side="top", padx=5, pady=5)
btn6.pack(fill="x", side="top", padx=5, pady=5)

root.mainloop()