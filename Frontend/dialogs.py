from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date
from models import SchemaTaskItem, SchemaNewTaskItem, format_date, parse_date, str_to_prio, prio_to_str


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task: SchemaTaskItem | None, on_submit):
        super().__init__(master)
        self.title("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.geometry("520x520")
        self.resizable(False, False)
        self.grab_set()
        self.focus()

        self.on_submit = on_submit
        self.task = task

        ctk.CTkLabel(self, text="Titel", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(20,4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Kurzer Titel…")
        self.title_entry.pack(fill="x", padx=20)
        self.title_entry.insert(0, task.title if task else "")

        ctk.CTkLabel(self, text="Beschreibung", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(16,4))
        self.desc_txt = ctk.CTkTextbox(self, height=140)
        self.desc_txt.pack(fill="both", expand=False, padx=20)
        if task and task.description:
            self.desc_txt.insert("1.0", task.description)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(16,0))

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(left, text="Fällig am (YYYY-MM-DD)").pack(anchor="w")
        self.due_entry = ctk.CTkEntry(left, placeholder_text=date.today().strftime("%Y-%m-%d"))
        self.due_entry.pack(fill="x", pady=(4,0))
        if task and task.due_date:
            self.due_entry.insert(0, format_date(task.due_date))

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", expand=True, fill="x", padx=(16,0))
        ctk.CTkLabel(right, text="Priorität").pack(anchor="w")
        self.prio_menu = ctk.CTkOptionMenu(right, values=["hoch", "mittel", "niedrig", "(keine)"])
        self.prio_menu.set(prio_to_str(task.prio) if task else "(keine)")
        self.prio_menu.pack(fill="x", pady=(4,0))

        ctk.CTkLabel(self, text="Tags (Komma-getrennt)", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(16,4))
        self.tags_entry = ctk.CTkEntry(self, placeholder_text="z.B. Schule, Arbeit, Haushalt")
        self.tags_entry.pack(fill="x", padx=20)
        if task and task.tags:
            self.tags_entry.insert(0, ", ".join(task.tags))

        self.done_var = tk.BooleanVar(value=(task.completed if task else False))
        self.done_chk = ctk.CTkCheckBox(self, text="Erledigt", variable=self.done_var)
        self.done_chk.pack(anchor="w", padx=20, pady=(12,0))

        btnrow = ctk.CTkFrame(self, fg_color="transparent")
        btnrow.pack(fill="x", side="bottom", padx=20, pady=20)
        ctk.CTkButton(btnrow, text="Abbrechen", fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"), command=self.destroy).pack(side="right")
        ctk.CTkButton(btnrow, text="Speichern", command=self._submit).pack(side="right", padx=(0,8))

    def _submit(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Checklist Pro", "Bitte einen Titel eingeben.")
            return
        due_text = self.due_entry.get().strip()
        if due_text:
            d = parse_date(due_text)
            if not d:
                messagebox.showwarning("Checklist Pro", "Ungültiges Datum. Bitte als YYYY-MM-DD eingeben.")
                return
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        prio = str_to_prio(self.prio_menu.get())

        if self.task:  # update existing
            self.task.title = title
            self.task.description = self.desc_txt.get("1.0", "end").strip()
            self.task.due_date = parse_date(due_text) if due_text else None
            self.task.prio = prio
            self.task.tags = tags
            self.task.completed = bool(self.done_var.get())
            self.on_submit(self.task)
        else:  # create new
            new_item = SchemaNewTaskItem(
                title=title,
                description=self.desc_txt.get("1.0", "end").strip(),
                due_date=parse_date(due_text) if due_text else None,
                prio=prio,
                tags=tags,
                completed=bool(self.done_var.get()),
            )
            self.on_submit(new_item)
        self.destroy()