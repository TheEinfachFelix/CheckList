import customtkinter as ctk


class Badge(ctk.CTkLabel):
    def __init__(self, master, text: str, fg: str, *args, **kwargs):
        super().__init__(master, text=text, corner_radius=8, padx=8, pady=4,
                         fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"],
                         text_color=fg, font=("Inter", 12, "bold"), *args, **kwargs)
        self._accent = fg
        self._add_border()

    def _add_border(self):
        self.configure(border_width=1, border_color=self._accent)

    def set_text(self, t):
        self.configure(text=t)

    def set_color(self, c):
        self._accent = c
        self.configure(text_color=c, border_color=c)


class Chip(ctk.CTkLabel):
    def __init__(self, master, text: str):
        super().__init__(master, text=text, corner_radius=999, padx=8, pady=2,
                         fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"),
                         font=("Inter", 11, "normal"))


class IconButton(ctk.CTkButton):
    def __init__(self, master, icon_text: str, command=None):
        super().__init__(master, text=icon_text, width=36, height=32, corner_radius=8,
                         fg_color=("#EEF2FF", "#111827"), hover_color=("#E0E7FF", "#374151"),
                         text_color=("#1E3A8A", "#E5E7EB"), command=command)

    def set_text(self, t):
        super().configure(text=t)
