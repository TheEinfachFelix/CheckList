"""Frame, das die Liste der Tasks anzeigt und CRUD-Aktionen anbietet."""
import customtkinter as ctk
from tkinter import messagebox
from .task_form import TaskForm
from models import SchemaTaskItem
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

        # nutze Treeview-artige Tabelle
        self.task_listbox = ctk.CTkTextbox(list_frame, wrap="none")
        self.task_listbox.pack(fill="both", expand=True, padx=6, pady=6)
        self.task_listbox.configure(state="disabled")

        # Auswahlfeld für Task-ID
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=6, pady=6)

        self.selected_id_var = ctk.StringVar()
        ctk.CTkLabel(bottom_frame, text="Selected ID:").pack(side="left", padx=(0,6))
        self.selected_entry = ctk.CTkEntry(bottom_frame, textvariable=self.selected_id_var, width=300)
        self.selected_entry.pack(side="left", padx=(0,6))

        self.show_completed_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(bottom_frame, text="Show completed", variable=self.show_completed_var, command=self.render_tasks).pack(side="left", padx=6)

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

        header = f"{'ID':<24} | {'Title':<20} | {'Prio':<4} | {'Due':<12} | {'Completed':<9} | Tags\n"
        self.task_listbox.insert("end", header)
        self.task_listbox.insert("end", "-"*90 + "\n")

        for t in self.tasks:
            if not self.show_completed_var.get() and t.completed:
                continue
            due = t.due_date if t.due_date else "-"
            tags = ", ".join(t.tags or [])
            row = f"{t.id:<24} | {t.title:<20} | {t.prio:<4} | {due:<12} | {str(t.completed):<9} | {tags}\n"
            self.task_listbox.insert("end", row)

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