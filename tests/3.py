from tkinter import *
from tkflu import *

root = FluWindow(mode="dark")
root.geometry("300x100")

label = Label(text="E830", font=SegoeFluentIcons())
label.pack(fill="both", expand="yes")

root.mainloop()