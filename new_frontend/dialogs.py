import customtkinter as ctk

class AddTaskDialog(ctk.CTkToplevel):
    def __init__(self, master, on_submit=None):
        super().__init__(master)
        self.title("Neue Aufgabe")
        self.geometry("400x250")
        self.on_submit = on_submit

        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        self.focus()

        ctk.CTkLabel(self, text="Titel").pack(anchor="w", padx=20, pady=(20, 4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Titel…")
        self.title_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(self, text="Beschreibung").pack(anchor="w", padx=20, pady=(16, 4))
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="Beschreibung…")
        self.desc_entry.pack(fill="x", padx=20)

        btn_row = ctk.CTkFrame(self)
        btn_row.pack(fill="x", side="bottom", padx=20, pady=20)
        ctk.CTkButton(btn_row, text="Abbrechen", command=self.destroy).pack(side="right")
        ctk.CTkButton(btn_row, text="Speichern", command=self._submit).pack(side="right", padx=(0, 8))

    def _submit(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not title:
            ctk.CTkLabel(self, text="Bitte einen Titel eingeben.", text_color="red").pack()
            return
        if self.on_submit:
            self.on_submit({"title": title, "description": desc})
        self.destroy()