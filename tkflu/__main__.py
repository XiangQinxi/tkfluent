from tkflu import *
from tkinter import *
from tkinter.font import *

from tkflu.listbox import FluListBox

red_primary_color()

root = FluWindow()
#root.wincustom(way=0)
root.geometry("360x600")

popupmenu = FluPopupMenu()

thememanager = FluThemeManager()

menubar = FluMenuBar(root)
menubar.add_command(
    label="FluMenu1", width=80, command=lambda: print("FluMenu1 -> Clicked")
)

menu1 = FluMenu()
menu1.add_command(
    label="FluMenu2-1", width=80, command=lambda: print("FluMenu2-1 -> Clicked")
)
menubar.add_cascade(
    label="FluMenu2", width=80, menu=menu1
)

menu2 = FluMenu(height=93)
menu2.add_command(
    label="FluMenu3-1", width=80, command=lambda: print("FluMenu3-1 -> Clicked")
)

menu3 = FluMenu(height=46, width=10)
menu3.add_command(
    label="FluMenu3-2-1", width=80, command=lambda: print("FluMenu3-2-1 -> Clicked")
)

menu2.add_cascade(
    label="FluMenu3-2", width=80, menu=menu3
)
menubar.add_cascade(
    label="FluMenu3", width=80, menu=menu2
)

menubar.pack(fill="x")

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

togglebutton1 = FluToggleButton(
    frame, text="FluToggleButton", command=lambda: print(f"FluToggleButton -> Toggled -> Checked: {togglebutton1.dcget('checked')}")
)
togglebutton1.pack(fill="x", padx=5, pady=5)

togglebutton2 = FluToggleButton(
    frame, text="Toggle Theme", command=lambda: toggle_theme(togglebutton2, thememanager)
)
togglebutton2.pack(fill="x", padx=5, pady=5)

entry1 = FluEntry(frame)
entry1.pack(fill="x", padx=5, pady=5)

entry2 = FluEntry(frame, height=50)
entry2.pack(fill="x", padx=5, pady=5)

text1 = FluText(frame)
text1.pack(fill="x", padx=5, pady=5)

slider1 = FluSlider(frame, value=0)
slider1.pack(fill="x", padx=5, pady=5)

"""listbox1 = FluListBox(frame)
listbox1.dconfigure()
listbox1.pack(fill="x", padx=5, pady=5)"""

frame.pack(fill="both", expand="yes", side="right", padx=5, pady=5)

root.mainloop()
