import customtkinter as ctk
from tkinter import messagebox, BooleanVar  # Importing BooleanVar explicitly
from utilities import new_task_template, parse_date, today_str

APP_NAME = "Checklist Pro"


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task=None, on_submit=None):
        super().__init__(master)
        self.title("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.geometry("520x520")
        self.resizable(False, False)
        self.grab_set()
        self.focus()

        self.on_submit = on_submit
        self.task = task or new_task_template()

        ctk.CTkLabel(self, text="Titel", font=("Inter", 12, "bold")).pack(
            anchor="w", padx=20, pady=(20, 4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Kurzer Titel…")
        self.title_entry.pack(fill="x", padx=20)
        self.title_entry.insert(0, self.task.get("title", ""))

        ctk.CTkLabel(self, text="Beschreibung", font=("Inter", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 4))
        self.desc_txt = ctk.CTkTextbox(self, height=140)
        self.desc_txt.pack(fill="both", expand=False, padx=20)
        if self.task.get("desc"):
            self.desc_txt.insert("1.0", self.task.get("desc"))

        # Row: due + priority
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(16, 0))

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(left, text="Fällig am (YYYY-MM-DD)").pack(anchor="w")
        self.due_entry = ctk.CTkEntry(left, placeholder_text=today_str())
        self.due_entry.pack(fill="x", pady=(4, 0))
        if self.task.get("due"):
            self.due_entry.insert(0, self.task["due"])

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", expand=True, fill="x", padx=(16, 0))
        ctk.CTkLabel(right, text="Priorität").pack(anchor="w")
        self.prio = ctk.CTkOptionMenu(
            right, values=["hoch", "mittel", "niedrig"])
        self.prio.set(self.task.get("priority", "mittel"))
        self.prio.pack(fill="x", pady=(4, 0))

        # Tags
        ctk.CTkLabel(self, text="Tags (Komma-getrennt)", font=("Inter", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 4))
        self.tags_entry = ctk.CTkEntry(
            self, placeholder_text="z.B. Schule, Arbeit, Haushalt")
        self.tags_entry.pack(fill="x", padx=20)
        if self.task.get("tags"):
            self.tags_entry.insert(0, ", ".join(self.task["tags"]))

        # Completed
        self.done_var = BooleanVar(value=self.task.get(
            "completed", False))  # Using the imported BooleanVar
        self.done_chk = ctk.CTkCheckBox(
            self, text="Erledigt", variable=self.done_var)
        self.done_chk.pack(anchor="w", padx=20, pady=(12, 0))

        # Buttons
        btnrow = ctk.CTkFrame(self, fg_color="transparent")
        btnrow.pack(fill="x", side="bottom", padx=20, pady=20)
        ctk.CTkButton(btnrow, text="Abbrechen", fg_color=("#F3F4F6", "#374151"), text_color=(
            "#111827", "#E5E7EB"), command=self.destroy).pack(side="right")
        ctk.CTkButton(btnrow, text="Speichern", command=self._submit).pack(
            side="right", padx=(0, 8))

    def _submit(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning(APP_NAME, "Bitte einen Titel eingeben.")
            return
        due_text = self.due_entry.get().strip()
        if due_text:
            d = parse_date(due_text)
            if not d:
                messagebox.showwarning(
                    APP_NAME, "Ungültiges Datum. Bitte als YYYY-MM-DD eingeben.")
                return
        tags = [t.strip()
                for t in self.tags_entry.get().split(",") if t.strip()]

        self.task.update({
            "title": title,
            "desc": self.desc_txt.get("1.0", "end").strip(),
            "due": due_text or None,
            "priority": self.prio.get(),
            "tags": tags,
            "completed": bool(self.done_var.get()),
        })
        if self.on_submit:
            self.on_submit(self.task)
        self.destroy()
