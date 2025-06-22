from tkflu import FluWindow, FluButton, FluToolTip


root =  FluWindow(mode="dark")
root.wincustom(way=0)

btn = FluButton(root, text="Hover me", style="accent")
btn.pack(padx=5, pady=5,  ipadx=2, ipady=2)

root.mainloop()