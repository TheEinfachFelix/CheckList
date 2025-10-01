import customtkinter as ctk
from services import api_client
from models.task import Task

class TaskTable(ctk.CTkFrame):
    def __init__(self, master, on_edit, **kwargs):
        super().__init__(master, **kwargs)
        self.on_edit = on_edit
        self.headers = ["Titel", "Beschreibung", "Fällig", "Priorität", "Status", "Aktionen"]
        self.rows = []
        self.draw_headers()

    def draw_headers(self):
        for col, header in enumerate(self.headers):
            label = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            label.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

    def load_tasks(self):
        for row in self.rows:
            for widget in row:
                widget.destroy()
        self.rows.clear()

        tasks = api_client.get_tasks()
        for i, task in enumerate(tasks, start=1):
            self.add_task_row(i, task)

    def add_task_row(self, row, task: Task):
        title = ctk.CTkLabel(self, text=task.title)
        desc = ctk.CTkLabel(self, text=task.description[:40] + "..." if len(task.description) > 40 else task.description)
        due = ctk.CTkLabel(self, text=task.due_date or "-")
        prio = ctk.CTkLabel(self, text=str(task.prio))
        status = ctk.CTkLabel(self, text="✔️" if task.completed else "❌")

        btn_edit = ctk.CTkButton(self, text="✏️", width=50, command=lambda: self.on_edit(task))
        btn_delete = ctk.CTkButton(self, text="🗑️", width=50, command=lambda: self.delete_task(task))
        btn_done = ctk.CTkButton(self, text="✅", width=50, command=lambda: self.toggle_task(task))

        widgets = [title, desc, due, prio, status, btn_edit, btn_delete, btn_done]

        for col, w in enumerate(widgets):
            w.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        self.rows.append(widgets)

    def delete_task(self, task: Task):
        api_client.delete_task(task.id)
        self.load_tasks()

    def toggle_task(self, task: Task):
        api_client.toggle_task(task)
        self.load_tasks()