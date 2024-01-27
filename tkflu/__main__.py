from tkflu import *
from tkinter import *
from tkinter.font import *

mode = "dark"

root = FluWindow(mode=mode)
root.wincustom(way=1)
root.wm_geometry("180x360")

frame = FluFrame(mode=mode)

badge1 = FluBadge(frame, text="FluBadge", width=60, mode=mode)
badge1.pack(padx=5, pady=5)

badge2 = FluBadge(frame, text="FluBadge (Accent)", width=120, mode=mode, style="accent")
badge2.pack(padx=5, pady=5)

button1 = FluButton(
    frame, text="FluButton", command=lambda: print("FluButton -> Clicked"), mode=mode
)
button1.pack(fill="x", padx=5, pady=5)

button2 = FluButton(
    frame, text="FluButton (Accent)", command=lambda: print("FluButton -> Clicked"), style="accent", mode=mode
)
button2.pack(fill="x", padx=5, pady=5)

togglebutton1 = FluToggleButton(
    frame, text="FluToggleButton", command=lambda: print("FluToggleButton -> Toggled"), mode=mode
)
togglebutton1.pack(fill="x", padx=5, pady=5)

entry1 = FluEntry(frame, mode=mode)
entry1.pack(fill="x", padx=5, pady=5)

text1 = FluText(frame, mode=mode)
text1.pack(fill="x", padx=5, pady=5)

frame.pack(fill="both", expand="yes", side="right", padx=5, pady=5)
root.mainloop()
