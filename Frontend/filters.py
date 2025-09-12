import customtkinter as ctk


class ButtonGroup(ctk.CTkFrame):
    def __init__(self, master, items):
        super().__init__(master, fg_color="transparent")
        self.buttons = []
        for label, cb in items:
            b = ctk.CTkButton(self, text=label, height=36,
                              command=lambda label=label: cb(label),
                              fg_color=("#F3F4F6", "#374151"),
                              text_color=("#111827", "#E5E7EB"),
                              hover_color=("#E5E7EB", "#4B5563"))
            b.pack(fill="x", pady=4)
            self.buttons.append(b)
