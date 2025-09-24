"""Frame, das die Liste der Tasks anzeigt und CRUD-Aktionen anbietet."""
import customtkinter as ctk
from tkinter import messagebox
from .task_form import TaskForm
from models import SchemaTaskItem, SchemaNewTaskItem
from datetime import date
from typing import List

class TaskListFrame(ctk.CTkFrame):
    def __init__(self, master, api_client, **kwargs):
        super().__init__(master, **kwargs)
        self.api = api_client
        self.tasks: List[SchemaTaskItem] = []

        # Oberer Toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=6, pady=6)

        self.refresh_btn = ctk.CTkButton(toolbar, text="Refresh", command=self.refresh)
        self.refresh_btn.pack(side="left", padx=6)

        self.add_btn = ctk.CTkButton(toolbar, text="New Task", command=self.new_task)
        self.add_btn.pack(side="left", padx=6)

        self.edit_btn = ctk.CTkButton(toolbar, text="Edit", command=self.edit_task)
        self.edit_btn.pack(side="left", padx=6)

        self.delete_btn = ctk.CTkButton(toolbar, text="Delete", command=self.delete_task)
        self.delete_btn.pack(side="left", padx=6)

        # Task list area
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))

        self.task_listbox = ctk.CTkTextbox(list_frame, width=400, wrap="word")
        self.task_listbox.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.task_listbox.configure(state="disabled")

        # simple selection via index input because CTk doesn't have a listbox styled heavily; keep simple
        right_frame = ctk.CTkFrame(list_frame, width=200)
        right_frame.pack(side="left", fill="y")

        self.selected_id_var = ctk.StringVar()
        ctk.CTkLabel(right_frame, text="Selected ID:").pack(pady=(8,0))
        self.selected_entry = ctk.CTkEntry(right_frame, textvariable=self.selected_id_var)
        self.selected_entry.pack(pady=(0,8), padx=6, fill="x")

        # Details
        ctk.CTkLabel(right_frame, text="Filters / Quick Actions:").pack(pady=(8,4))
        self.show_completed_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(right_frame, text="Show completed", variable=self.show_completed_var, command=self.render_tasks).pack()

        # initial load
        self.refresh()

    def refresh(self):
        try:
            self.tasks = self.api.list_tasks()
            self.render_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks:\n{e}")

    def render_tasks(self):
        self.task_listbox.configure(state="normal")
        self.task_listbox.delete("1.0", "end")
        for t in self.tasks:
            if not self.show_completed_var.get() and t.completed:
                continue
            due = t.due_date if t.due_date else "-"
            tags = ", ".join(t.tags or [])
            self.task_listbox.insert("end",
                                     f"ID: {t.id}\nTitle: {t.title}\nDesc: {t.description}\nCompleted: {t.completed}\nPrio: {t.prio}\nDue: {due}\nTags: {tags}\n---\n")
        self.task_listbox.configure(state="disabled")

    def new_task(self):
        TaskForm(self, api=self.api, on_done=self.on_form_done)

    def edit_task(self):
        item_id = self.selected_id_var.get().strip()
        if not item_id:
            messagebox.showinfo("Info", "Please enter the ID of the task you want to edit in 'Selected ID'.")
            return
        try:
            task = self.api.get_task(item_id)
            if task is None:
                messagebox.showerror("Not found", "Task not found")
                return
            TaskForm(self, api=self.api, task=task, on_done=self.on_form_done)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch task:\n{e}")

    def delete_task(self):
        item_id = self.selected_id_var.get().strip()
        if not item_id:
            messagebox.showinfo("Info", "Please enter the ID of the task you want to delete in 'Selected ID'.")
            return
        if not messagebox.askyesno("Confirm", "Delete task with ID: %s?" % item_id):
            return
        try:
            ok = self.api.delete_task(item_id)
            if ok:
                messagebox.showinfo("Deleted", "Task deleted")
                self.refresh()
            else:
                messagebox.showerror("Error", "Task could not be deleted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete task:\n{e}")

    def on_form_done(self, success: bool):
        if success:
            self.refresh()