"""Form für Erstellen / Bearbeiten von Tasks."""
import customtkinter as ctk
from tkinter import messagebox
from models import SchemaNewTaskItem, SchemaTaskItem
from datetime import datetime
from typing import Optional

class TaskForm(ctk.CTkToplevel):
    def __init__(self, master, api, task: Optional[SchemaTaskItem] = None, on_done=None):
        super().__init__(master)
        self.api = api
        self.task = task
        self.on_done = on_done
        self.title("Edit Task" if task else "New Task")
        self.geometry("520x420")

        # Fields
        self.title_var = ctk.StringVar(value=task.title if task else "")
        self.completed_var = ctk.BooleanVar(value=task.completed if task else False)
        self.tags_var = ctk.StringVar(value=", ".join(task.tags) if (task and task.tags) else "")
        self.prio_var = ctk.StringVar(value=str(task.prio) if task else "")
        self.due_var = ctk.StringVar(value=task.due_date if (task and task.due_date) else "")

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(form, text="Title").grid(row=0, column=0, sticky="w")
        self.title_entry = ctk.CTkEntry(form, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Description").grid(row=1, column=0, sticky="nw")
        self.desc_entry = ctk.CTkTextbox(form, height=100)
        self.desc_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        if self.task:
            self.desc_entry.insert("0.0", self.task.description)

        ctk.CTkLabel(form, text="Completed").grid(row=2, column=0, sticky="w")
        ctk.CTkSwitch(form, variable=self.completed_var, text="").grid(row=2, column=1, sticky="w", padx=8)

        ctk.CTkLabel(form, text="Tags (comma separated)").grid(row=3, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.tags_var).grid(row=3, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(form, text="Priority").grid(row=4, column=0, sticky="w")
        self.prio_entry = ctk.CTkEntry(form, textvariable=self.prio_var)
        self.prio_entry.grid(row=4, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(form, text="Due date (YYYY-MM-DD)").grid(row=5, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.due_var).grid(row=5, column=1, sticky="w", padx=8, pady=4)

        btn_frame = ctk.CTkFrame(form)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(12,0))

        save_text = "Update" if task else "Create"
        ctk.CTkButton(btn_frame, text=save_text, command=self.save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=6)

        form.grid_columnconfigure(1, weight=1)

    def parse_due(self, s: str):
        s = s.strip()
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            raise

    def save(self):
        title = self.title_var.get().strip()
        description = self.desc_entry.get("0.0", "end").strip()
        completed = self.completed_var.get()
        tags = [t.strip() for t in self.tags_var.get().split(",") if t.strip()]

        prio_text = self.prio_var.get().strip()
        prio = int(prio_text) if prio_text.isdigit() else -1

        try:
            due = self.parse_due(self.due_var.get())
        except Exception:
            messagebox.showerror("Invalid date", "Please use YYYY-MM-DD for the due date or leave empty.")
            return

        if not title:
            messagebox.showerror("Validation", "Title is required")
            return

        if self.task:
            payload = SchemaTaskItem(
                id=self.task.id,
                title=title,
                description=description,
                completed=completed,
                tags=tags,
                prio=prio,
                due_date=due,
            )
            try:
                self.api.update_task(payload)
                messagebox.showinfo("Success", "Task updated")
                if self.on_done:
                    self.on_done(True)
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update task:\n{e}")
        else:
            payload = SchemaNewTaskItem(
                title=title,
                description=description,
                completed=completed,
                tags=tags,
                prio=prio,
                due_date=due,
            )
            try:
                self.api.create_task(payload)
                messagebox.showinfo("Success", "Task created")
                if self.on_done:
                    self.on_done(True)
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create task:\n{e}")