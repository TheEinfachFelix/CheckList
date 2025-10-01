import customtkinter as ctk
from models.task import Task

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task: Task = None, on_save=None):
        super().__init__(master)
        self.task = task
        self.on_save = on_save
        self.title("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.geometry("400x400")

        self.entry_title = ctk.CTkEntry(self, placeholder_text="Titel")
        self.entry_title.pack(pady=10, fill="x", padx=20)

        self.entry_desc = ctk.CTkTextbox(self, height=100)
        self.entry_desc.pack(pady=10, fill="both", padx=20, expand=True)

        self.entry_prio = ctk.CTkEntry(self, placeholder_text="Prio (Zahl)")
        self.entry_prio.pack(pady=10, fill="x", padx=20)

        btn_save = ctk.CTkButton(self, text="Speichern", command=self.save)
        btn_save.pack(pady=20)

        if task:
            self.entry_title.insert(0, task.title)
            self.entry_desc.insert("1.0", task.description)
            self.entry_prio.insert(0, str(task.prio))

    def save(self):
        data = {
            "id": self.task.id if self.task else None,
            "title": self.entry_title.get(),
            "description": self.entry_desc.get("1.0", "end").strip(),
            "prio": int(self.entry_prio.get() or -1),
            "completed": self.task.completed if self.task else False,
            "tags": self.task.tags if self.task else [],
            "due_date": self.task.due_date if self.task else None
        }
        if self.on_save:
            self.on_save(data)
        self.destroy()