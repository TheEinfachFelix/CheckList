import customtkinter as ctk
from dialogs import AddTaskDialog

APP_NAME = "Checklist Pro"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(980, 600)

        # THEME
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # GRID
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        self._build_sidebar()
        self._build_list()
        self._build_statusbar()

        self.tasks = []


#####   Build UI   #####
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=64)
        bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text=APP_NAME, font=("Inter", 20, "bold")).grid(
            row=0, column=0, padx=16, pady=12)

        self.search_entry = ctk.CTkEntry(
            bar, placeholder_text="Suchen (Titel, Beschreibung, #Tag)…")
        self.search_entry.grid(row=0, column=1, padx=8, pady=12, sticky="ew")

        self.sort_menu = ctk.CTkOptionMenu(
            bar,
            values=["Fälligkeit", "Priorität", "Erstellt", "Titel"]
        )
        self.sort_menu.grid(row=0, column=2, padx=(8, 0))

        ctk.CTkButton(bar, text="+ Neue Aufgabe", command=self.create_new_task).grid(row=0, column=3, padx=8)

        self.theme_switch = ctk.CTkSwitch(
            bar, text="Dark Mode")
        self.theme_switch.grid(row=0, column=4, padx=16)

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, corner_radius=0, width=260)
        side.grid(row=1, column=0, rowspan=2, sticky="nsew")
        side.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(side, text="Filter", font=("Inter", 14, "bold")).pack(
            anchor="w", padx=16, pady=(16, 6))

        # Placeholder for filter buttons
        for label in ["Alle", "Heute", "Überfällig", "Offen", "Erledigt", "Hoch priorisiert"]:
            ctk.CTkButton(side, text=label).pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(side, text="Tags", font=("Inter", 14, "bold")
                     ).pack(anchor="w", padx=16, pady=(16, 6))
        self.tags_frame = ctk.CTkScrollableFrame(side, height=220)
        self.tags_frame.pack(fill="both", expand=False, padx=12)

        tag_add = ctk.CTkFrame(side, fg_color="transparent")
        tag_add.pack(fill="x", padx=12, pady=(8, 12))
        self.new_tag_entry = ctk.CTkEntry(
            tag_add, placeholder_text="Neuen Tag filtern… #")
        self.new_tag_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tag_add, text="Hinzufügen").pack(
            side="left", padx=(8, 0))

        ctk.CTkLabel(side, text="Sammelaktionen", font=(
            "Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(8, 6))
        bulk = ctk.CTkFrame(side)
        bulk.pack(fill="x", padx=12)
        ctk.CTkButton(bulk, text="Alle erledigt markieren").pack(fill="x", pady=6)
        ctk.CTkButton(bulk, text="Alle Filter löschen").pack(fill="x", pady=6)

    def _build_list(self):
        container = ctk.CTkFrame(self)
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.info_lbl = ctk.CTkLabel(container, text="", font=("Inter", 12))
        self.info_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.list_frame = ctk.CTkScrollableFrame(container)
        self.list_frame.grid(
            row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # Placeholder for tasks
        ctk.CTkLabel(self.list_frame, text="Hier erscheinen Aufgaben…").pack(pady=20)

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=48)
        bar.grid(row=2, column=1, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        self.progress = ctk.CTkProgressBar(bar, height=10)
        self.progress.grid(row=0, column=0, padx=12, pady=8, sticky="ew")

        self.status_lbl = ctk.CTkLabel(bar, text="Bereit", font=("Inter", 12))
        self.status_lbl.grid(row=0, column=1, padx=12)


#####   Task Management   #####
    def create_new_task(self):
        AddTaskDialog(self, on_submit=self.add_task)

    def add_task(self, task):
        self.tasks.append(task)
        self.refresh_tasks()
    
    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.refresh_tasks()
    
    def refresh_tasks(self):
        # Clear current list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        # Add all tasks
        for task in self.tasks:
            ctk.CTkLabel(self.list_frame, text=str(task)).pack(pady=2)



if __name__ == "__main__":
    app = App()
    app.mainloop()