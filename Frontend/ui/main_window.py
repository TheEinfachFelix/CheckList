import customtkinter as ctk
from ui.task_table import TaskTable
from ui.task_dialogs import TaskDialog
from services import api_client

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("900x600")

        self.task_table = TaskTable(self, on_edit=self.open_edit_dialog)
        self.task_table.pack(fill="both", expand=True, padx=20, pady=20)

        btn_add = ctk.CTkButton(self, text="Neue Aufgabe ➕", command=self.open_create_dialog)
        btn_add.pack(pady=10)

        self.task_table.load_tasks()

    def open_create_dialog(self):
        TaskDialog(self, on_save=self.create_task)

    def create_task(self, data):
        api_client.create_task(data)
        self.task_table.load_tasks()

    def open_edit_dialog(self, task):
        TaskDialog(self, task=task, on_save=self.update_task)

    def update_task(self, data):
        api_client.update_task(data)
        self.task_table.load_tasks()