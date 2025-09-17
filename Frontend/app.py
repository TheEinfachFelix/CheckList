from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date
from models import SchemaTaskItem, SchemaNewTaskItem, parse_date, prio_to_str
from utilities import list_tasks, create_task, update_task, delete_task
from task_item import TaskItem
from filters import ButtonGroup

APP_NAME = "Checklist Pro"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(980, 600)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.tasks: list[SchemaTaskItem] = []
        self.filtered: list[SchemaTaskItem] = []
        self.active_filter = "Alle"
        self.tag_filter: str | None = None
        self.search_query = ""
        self.sort_mode = tk.StringVar(value="Fälligkeit")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        self._build_sidebar()
        self._build_list()
        self._build_statusbar()

        self.bind("<<TaskChanged>>", lambda e: self._on_task_changed())
        self.bind_all("<Control-n>", lambda e: self.open_new_task())
        self.bind_all("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Control-s>", lambda e: self._save())

        self.refresh_from_backend()

    # UI Sections
    def _build_topbar(self):
        from dialogs import TaskDialog
        self.TaskDialog = TaskDialog  # save class ref

        bar = ctk.CTkFrame(self, height=64)
        bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text=APP_NAME, font=("Inter", 20, "bold")).grid(row=0, column=0, padx=16, pady=12)

        self.search_entry = ctk.CTkEntry(bar, placeholder_text="Suchen (Titel, Beschreibung, #Tag)…")
        self.search_entry.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        self.sort_menu = ctk.CTkOptionMenu(bar, values=["Fälligkeit", "Priorität", "Erstellt", "Titel"],
                                           variable=self.sort_mode, command=lambda _v: self.refresh())
        self.sort_menu.grid(row=0, column=2, padx=(8,0))

        ctk.CTkButton(bar, text="+ Neue Aufgabe (Ctrl+N)", command=self.open_new_task).grid(row=0, column=3, padx=8)

        self.theme_switch = ctk.CTkSwitch(bar, text="Dark Mode", command=self._toggle_theme)
        self.theme_switch.grid(row=0, column=4, padx=16)

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, corner_radius=0, width=260)
        side.grid(row=1, column=0, rowspan=2, sticky="nsew")
        side.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(side, text="Filter", font=("Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(16,6))
        self.filter_group = ButtonGroup(side, [
            ("Alle", self._set_filter),
            ("Heute", self._set_filter),
            ("Überfällig", self._set_filter),
            ("Offen", self._set_filter),
            ("Erledigt", self._set_filter),
            ("Hoch priorisiert", self._set_filter),
        ])
        self.filter_group.pack(fill="x", padx=12)

        ctk.CTkLabel(side, text="Tags", font=("Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(16,6))
        self.tags_frame = ctk.CTkScrollableFrame(side, height=220)
        self.tags_frame.pack(fill="both", expand=False, padx=12)

        tag_add = ctk.CTkFrame(side, fg_color="transparent")
        tag_add.pack(fill="x", padx=12, pady=(8,12))
        self.new_tag_entry = ctk.CTkEntry(tag_add, placeholder_text="Neuen Tag filtern… #")
        self.new_tag_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tag_add, text="Hinzufügen", command=self._add_tag_filter).pack(side="left", padx=(8,0))

        ctk.CTkLabel(side, text="Sammelaktionen", font=("Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(8,6))
        bulk = ctk.CTkFrame(side)
        bulk.pack(fill="x", padx=12)
        ctk.CTkButton(bulk, text="Alle erledigt markieren", command=self._complete_all).pack(fill="x", pady=6)
        ctk.CTkButton(bulk, text="Alle Filter löschen", fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"), command=self._clear_filters).pack(fill="x", pady=6)

    def _build_list(self):
        container = ctk.CTkFrame(self)
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.info_lbl = ctk.CTkLabel(container, text="", font=("Inter", 12))
        self.info_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10,4))

        self.list_frame = ctk.CTkScrollableFrame(container)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=48)
        bar.grid(row=2, column=1, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        self.progress = ctk.CTkProgressBar(bar, height=10)
        self.progress.grid(row=0, column=0, padx=12, pady=8, sticky="ew")

        self.status_lbl = ctk.CTkLabel(bar, text="Bereit", font=("Inter", 12))
        self.status_lbl.grid(row=0, column=1, padx=12)

    # Actions
    def _toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    def _on_search(self):
        self.search_query = self.search_entry.get().strip().lower()
        self.refresh()

    def _set_filter(self, label):
        self.active_filter = label
        self.refresh()

    def _add_tag_filter(self):
        t = self.new_tag_entry.get().strip().lstrip("#")
        if not t:
            return
        self.tag_filter = t
        self.new_tag_entry.delete(0, "end")
        self.refresh()

    def _clear_filters(self):
        self.active_filter = "Alle"
        self.tag_filter = None
        self.search_query = ""
        self.search_entry.delete(0, "end")
        self.refresh()

    def _complete_all(self):
        from .utilities import update_task
        for t in self.tasks:
            if t in self.filtered:
                if not t.completed:
                    t.completed = True
                    update_task(t)
        self.refresh_from_backend()

    def _save(self):
        # UI feedback only – Daten werden beim Ändern sofort ans Backend geschickt
        self.status_lbl.configure(text="Gespeichert")
        self.after(1200, lambda: self.status_lbl.configure(text="Bereit"))

    def open_new_task(self):
        self.TaskDialog(self, task=None, on_submit=self._create_task)

    def _create_task(self, new_item: SchemaNewTaskItem):
        create_task(new_item)
        self.refresh_from_backend()

    def _edit_task(self, t: SchemaTaskItem):
        self.TaskDialog(self, task=t, on_submit=self._apply_update)

    def _apply_update(self, updated: SchemaTaskItem | SchemaNewTaskItem):
        if isinstance(updated, SchemaTaskItem):
            update_task(updated)
        else:
            create_task(updated)
        self.refresh_from_backend()

    def _delete_task(self, t: SchemaTaskItem):
        from tkinter import messagebox
        if messagebox.askyesno(APP_NAME, f"Aufgabe ‘{t.title or 'Ohne Titel'}’ löschen?"):
            delete_task(t.id)
            self.refresh_from_backend()

    def _on_task_changed(self):
        # Wird von TaskItem bei Toggle/Star/DueToday ausgelöst → ans Backend schreiben
        # Finde referenziertes Task-Objekt über ID
        from .utilities import update_task
        # In dieser App werden TaskItem-Instanzen mit self.task referenziert, wir updaten direkt
        # Danach frisch laden, damit Backend-Quelle die Wahrheit bleibt
        widget = self.focus_get()
        # Unabhängig vom Focus einfach alles speichern, was in filtered steckt
        for t in self.filtered:
            update_task(t)
        self.refresh_from_backend()

    # Filtering & sorting
    def _apply_filters(self):
        tasks = list(self.tasks)
        q = self.search_query
        if q:
            def match(t: SchemaTaskItem):
                if q in (t.title or "").lower():
                    return True
                if q in (t.description or "").lower():
                    return True
                if q.startswith("#"):
                    return q[1:] in [x.lower() for x in t.tags]
                if any(q in x.lower() for x in t.tags):
                    return True
                return False
            tasks = [t for t in tasks if match(t)]

        label = self.active_filter
        today = date.today()
        if label == "Heute":
            tasks = [t for t in tasks if t.due_date == today and not t.completed]
        elif label == "Überfällig":
            tasks = [t for t in tasks if t.due_date and t.due_date < today and not t.completed]
        elif label == "Offen":
            tasks = [t for t in tasks if not t.completed]
        elif label == "Erledigt":
            tasks = [t for t in tasks if t.completed]
        elif label == "Hoch priorisiert":
            tasks = [t for t in tasks if (t.prio or -1) == 2 and not t.completed]

        if self.tag_filter:
            tasks = [t for t in tasks if self.tag_filter.lower() in [x.lower() for x in t.tags]]

        mode = self.sort_mode.get()
        if mode == "Fälligkeit":
            def key(t: SchemaTaskItem):
                return (1, date.max) if t.due_date is None else (0, t.due_date)
            tasks.sort(key=key)
        elif mode == "Priorität":
            order = {2: 0, 1: 1, 0: 2, -1: 3}
            tasks.sort(key=lambda t: (order.get(t.prio if t.prio is not None else -1, 3), t.title or ""))
        elif mode == "Erstellt":
            # Backend liefert kein created_at: Wir belassen Reihenfolge
            pass
        elif mode == "Titel":
            tasks.sort(key=lambda t: t.title or "")

        self.filtered = tasks

    def _rebuild_tags_panel(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()
        tag_counts = {}
        for t in self.tasks:
            for tag in t.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        if not tag_counts:
            ctk.CTkLabel(self.tags_frame, text="Keine Tags vorhanden.").pack(anchor="w", padx=6, pady=6)
            return
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[0].lower()):
            btn = ctk.CTkButton(self.tags_frame, text=f"#{tag}  ({count})", height=34,
                                fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"),
                                hover_color=("#E5E7EB", "#4B5563"),
                                command=lambda t=tag: self._set_tag_filter(t))
            btn.pack(fill="x", pady=4, padx=6)

    def _set_tag_filter(self, t):
        self.tag_filter = t
        self.refresh()

    def refresh(self):
        self._apply_filters()
        self._rebuild_tags_panel()

        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.filtered:
            ctk.CTkLabel(self.list_frame, text="Keine Aufgaben für die aktuelle Ansicht.").pack(pady=20)
        else:
            for t in self.filtered:
                item = TaskItem(self.list_frame, t, on_toggle=self._on_task_changed, on_edit=self._edit_task, on_delete=self._delete_task)
                item.pack(fill="x", padx=6, pady=6)

        total = len(self.tasks)
        done = len([t for t in self.tasks if t.completed])
        open_cnt = total - done
        overdue_cnt = len([t for t in self.tasks if t.due_date and t.due_date < date.today() and not t.completed])
        self.info_lbl.configure(text=f"{len(self.filtered)} angezeigt • {open_cnt} offen • {done} erledigt • {overdue_cnt} überfällig")
        self.progress.set(0 if total == 0 else done / total)
        self.status_lbl.configure(text=f"Sortierung: {self.sort_mode.get()} • Filter: {self.active_filter}{' • #' + self.tag_filter if self.tag_filter else ''}")

    def refresh_from_backend(self):
        try:
            self.tasks = list_tasks()
            self.status_lbl.configure(text="Daten aktualisiert")
        except Exception as e:
            self.status_lbl.configure(text=f"Fehler: {e}")
        self.refresh()