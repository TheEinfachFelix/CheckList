import customtkinter as ctk
from ui.task_table import TaskTable
from ui.task_dialogs import TaskDialog
from services import api_client

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("900x600")

        # Filter frame
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=(20,0))

        # Priority filter
        prio_label = ctk.CTkLabel(filter_frame, text="Priorität:", font=("Arial", 14))
        prio_label.pack(side="left", padx=(10,5))
        self.prio_var = ctk.StringVar(value="alle")
        self.prio_filter = ctk.CTkOptionMenu(filter_frame, variable=self.prio_var,
                                           values=["alle", "niedrig", "mittel", "hoch"],
                                           command=self.apply_filters)
        self.prio_filter.pack(side="left", padx=5)

        # Search filter
        search_label = ctk.CTkLabel(filter_frame, text="Suche:", font=("Arial", 14))
        search_label.pack(side="left", padx=(20,5))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *args: self.apply_filters())
        search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var, 
                                  width=200, placeholder_text="In Titel oder Beschreibung suchen...")
        search_entry.pack(side="left", padx=5)

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
        
    def apply_filters(self, *args):
        priority = self.prio_var.get()
        search_text = self.search_var.get().lower()
        self.task_table.apply_filters(
            priority=None if priority == "alle" else priority,
            search_text=search_text if search_text else None
        )