from tkinter import *
from tkflu import *
from tkflu.designs.scrollbar import scrollbar

root = FluWindow()

frane = FluFrame(root)
frane.pack(fill="both", expand="yes", padx=10, pady=10)

scrollbar = FluScrollBar(frane, orient=VERTICAL)
scrollbar.pack(fill="y", side="right")

canvas = Canvas(frane, yscrollcommand=scrollbar.set)
canvas.pack(fill="both", expand="yes", padx=5, pady=5)

for i in range(20):
    canvas.create_window(0, i * 30, anchor="nw", window=FluButton(text=f"Button {i}"))

root.mainloop()