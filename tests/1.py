from tkflu import *
from tkinter import *
from tkinter.font import *


root = FluWindow()
#root.wincustom(way=0)
root.wm_geometry("220x400")

popupmenu = FluPopupMenu()
popupmenu.window.geometry("100x40")

thememanager = FluThemeManager()

menubar = FluMenuBar(root)
menubar.add_command(
    label="FluMenu1", width=80, command=lambda: print("FluMenu -> Clicked")
)
menubar.pack(fill="x",)

frame = FluFrame(root)

badge1 = FluBadge(frame, text="FluBadge", width=60)
badge1.pack(padx=5, pady=5)

badge2 = FluBadge(frame, text="FluBadge (Accent)", width=120, style="accent")
badge2.pack(padx=5, pady=5)

button1 = FluButton(
    frame, text="FluButton", command=lambda: print("FluButton -> Clicked")
)
button1.pack(fill="x", padx=5, pady=5)

button2 = FluButton(
    frame, text="FluButton (Accent)", command=lambda: print("FluButton (Accent) -> Clicked"), style="accent"
)
button2.pack(fill="x", padx=5, pady=5)

def toggle1():
    print(f"FluToggleButton -> Toggled -> Checked: {togglebutton1.dcget('checked')}")
    if togglebutton1.dcget('checked'):
        thememanager.mode("dark")
    else:
        thememanager.mode("light")

togglebutton1 = FluToggleButton(
    frame, text="FluToggleButton", command=toggle1
)
togglebutton1.pack(fill="x", padx=5, pady=5)

entry1 = FluEntry(frame)
entry1.pack(fill="x", padx=5, pady=5)

text1 = FluText(frame)
text1.pack(fill="x", padx=5, pady=5)

frame.pack(fill="both", expand="yes", side="right", padx=5, pady=5)

root.mainloop()
