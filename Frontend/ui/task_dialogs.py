import customtkinter as ctk
from models.task import Task
from tkcalendar import DateEntry

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task: Task = None, on_save=None):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.task = task
        self.on_save = on_save
        self.title("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.geometry("400x450")

        self.entry_title = ctk.CTkEntry(self, placeholder_text="Titel", font=("Arial", 16))
        self.entry_title.pack(pady=10, fill="x", padx=20)

        self.entry_desc = ctk.CTkTextbox(self, height=100, font=("Arial", 14))
        self.entry_desc.pack(pady=10, fill="both", padx=20, expand=True)

        self.prio_var = ctk.StringVar(value="niedrig")
        self.prio_menu = ctk.CTkOptionMenu(self, variable=self.prio_var, values=["niedrig", "mittel", "hoch"], font=("Arial", 14))
        self.prio_menu.pack(pady=10, fill="x", padx=20)

        self.date_label = ctk.CTkLabel(self, text="Fälligkeitsdatum", font=("Arial", 14))
        self.date_label.pack(pady=(10,0), padx=20, anchor="w")

        # Date field and calendar button
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(pady=5, fill="x", padx=20)
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(date_frame, textvariable=self.date_var, font=("Arial", 14), width=220, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(side="left", fill="x", expand=True)
        self.calendar_btn = ctk.CTkButton(date_frame, text="📅", width=40, command=self.open_calendar)
        self.calendar_btn.pack(side="left", padx=(5,0))

        btn_save = ctk.CTkButton(self, text="Speichern", font=("Arial", 16), command=self.save)
        btn_save.pack(pady=20)

        if task:
            self.entry_title.insert(0, task.title)
            self.entry_desc.insert("1.0", task.description)
            self.prio_var.set(task.prio if task.prio else "niedrig")
            if task.due_date:
                self.date_var.set(task.due_date)

    def open_calendar(self):
        # Pop-up calendar window
        top = ctk.CTkToplevel(self)
        top.title("Datum wählen")
        top.geometry("250x250")
        top.transient(self)
        top.grab_set()
        cal = DateEntry(top, date_pattern="yyyy-mm-dd", locale="de_DE", font=("Arial", 14))
        cal.pack(pady=40, padx=20)
        def set_date():
            self.date_var.set(cal.get_date().strftime("%Y-%m-%d"))
            top.destroy()
        btn = ctk.CTkButton(top, text="Auswählen", command=set_date)
        btn.pack(pady=10)
        top.focus_force()

    def save(self):
        prio = self.prio_var.get()
        due_date = self.date_var.get()
        data = {
            "id": self.task.id if self.task else None,
            "title": self.entry_title.get(),
            "description": self.entry_desc.get("1.0", "end").strip(),
            "prio": prio,
            "completed": self.task.completed if self.task else False,
            "tags": self.task.tags if self.task else [],
            "due_date": due_date
        }
        if self.on_save:
            self.on_save(data)
        self.destroy()