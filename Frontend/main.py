"""Startpunkt der customTkinter-Anwendung."""
import customtkinter as ctk
from ui.task_list import TaskListFrame
from api_client import ApiClient

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

API = ApiClient()  # konfiguriere BASE_URL in api_client.py falls nötig

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task-Manager")
        self.geometry("900x600")
        self.minsize(700, 450)

        self.task_list_frame = TaskListFrame(self, api_client=API)
        self.task_list_frame.pack(fill="both", expand=True, padx=12, pady=12)

if __name__ == "__main__":
    app = App()
    app.mainloop()