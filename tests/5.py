from tkflu import FluWindow, FluButton, FluToggleButton, FluThemeManager, toggle_theme, ACCENT

root = FluWindow()

theme_manager = FluThemeManager(root)
toggle_button = FluToggleButton(
    text="Toggle Theme", command=lambda: toggle_theme(toggle_button, theme_manager)
)
toggle_button.pack(padx=3, pady=3, )

button = FluButton(root, text="Accent Button", style=ACCENT)
button.pack(padx=3, pady=3, )

root.mainloop()