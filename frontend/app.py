import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date
from utilities import load_tasks, save_tasks, parse_date
from dialogs import TaskDialog
from task_item import TaskItem
from filters import ButtonGroup
from widgets import Badge, Chip, IconButton
import requests

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

        # DATA
        self.tasks = load_tasks()
        self.filtered = []
        self.active_filter = "Alle"
        self.tag_filter = None
        self.search_query = ""
        self.sort_mode = tk.StringVar(value="Fälligkeit")

        # GRID
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        self._build_sidebar()
        self._build_list()
        self._build_statusbar()

        # Event bindings
        self.bind("<<TaskChanged>>", lambda e: self._on_task_changed())
        self.bind_all("<Control-n>", lambda e: self.open_new_task())
        self.bind_all("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind_all("<Delete>", lambda e: self._delete_selected())
        self.bind_all("<Control-s>", lambda e: self._save())

        self.refresh()

    # ----- UI Sections -----

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=64)
        bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text=APP_NAME, font=("Inter", 20, "bold")).grid(
            row=0, column=0, padx=16, pady=12)

        self.search_entry = ctk.CTkEntry(
            bar, placeholder_text="Suchen (Titel, Beschreibung, #Tag)…")
        self.search_entry.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        self.sort_menu = ctk.CTkOptionMenu(
            bar,
            values=["Fälligkeit", "Priorität", "Erstellt", "Titel"],
            variable=self.sort_mode,
            command=lambda _v: self.refresh()
        )
        self.sort_menu.grid(row=0, column=2, padx=(8, 0))

        ctk.CTkButton(bar, text="+ Neue Aufgabe (Ctrl+N)",
                      command=self.open_new_task).grid(row=0, column=3, padx=8)

        self.theme_switch = ctk.CTkSwitch(
            bar, text="Dark Mode", command=self._toggle_theme)
        self.theme_switch.grid(row=0, column=4, padx=16)

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, corner_radius=0, width=260)
        side.grid(row=1, column=0, rowspan=2, sticky="nsew")
        side.grid_rowconfigure(4, weight=1)

        # Filter buttons
        ctk.CTkLabel(side, text="Filter", font=("Inter", 14, "bold")).pack(
            anchor="w", padx=16, pady=(16, 6))

        self.filter_group = ButtonGroup(side, [
            ("Alle", self._set_filter),
            ("Heute", self._set_filter),
            ("Überfällig", self._set_filter),
            ("Offen", self._set_filter),
            ("Erledigt", self._set_filter),
            ("Hoch priorisiert", self._set_filter),
        ])
        self.filter_group.pack(fill="x", padx=12)

        # Tags
        ctk.CTkLabel(side, text="Tags", font=("Inter", 14, "bold")
                     ).pack(anchor="w", padx=16, pady=(16, 6))
        self.tags_frame = ctk.CTkScrollableFrame(side, height=220)
        self.tags_frame.pack(fill="both", expand=False, padx=12)

        tag_add = ctk.CTkFrame(side, fg_color="transparent")
        tag_add.pack(fill="x", padx=12, pady=(8, 12))
        self.new_tag_entry = ctk.CTkEntry(
            tag_add, placeholder_text="Neuen Tag filtern… #")
        self.new_tag_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tag_add, text="Hinzufügen", command=self._add_tag_filter).pack(
            side="left", padx=(8, 0))

        # Bulk actions
        ctk.CTkLabel(side, text="Sammelaktionen", font=(
            "Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(8, 6))
        bulk = ctk.CTkFrame(side)
        bulk.pack(fill="x", padx=12)
        ctk.CTkButton(bulk, text="Alle erledigt markieren",
                      command=self._complete_all).pack(fill="x", pady=6)
        ctk.CTkButton(bulk, text="Alle Filter löschen", fg_color=("#F3F4F6", "#374151"),
                      text_color=("#111827", "#E5E7EB"), command=self._clear_filters).pack(fill="x", pady=6)

    def _build_list(self):
        container = ctk.CTkFrame(self)
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Info bar
        self.info_lbl = ctk.CTkLabel(container, text="", font=("Inter", 12))
        self.info_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(container)
        self.list_frame.grid(
            row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=48)
        bar.grid(row=2, column=1, sticky="nsew")
        bar.grid_columnconfigure(1, weight=1)

        self.progress = ctk.CTkProgressBar(bar, height=10)
        self.progress.grid(row=0, column=0, padx=12, pady=8, sticky="ew")

        self.status_lbl = ctk.CTkLabel(bar, text="Bereit", font=("Inter", 12))
        self.status_lbl.grid(row=0, column=1, padx=12)

    # ----- Actions -----

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
        for t in self.tasks:
            if t in self.filtered:
                t["completed"] = True
        self._on_task_changed()

    def _delete_selected(self):
        pass

    def _save(self):
        save_tasks(self.tasks)
        self.status_lbl.configure(text="Gespeichert")
        self.after(1200, lambda: self.status_lbl.configure(text="Bereit"))

    def open_new_task(self):
        TaskDialog(self, task=None, on_submit=self._add_task)

    def _add_task(self, t):
        requests.post("http://127.0.0.1:8000/TaskItem", json=t, timeout=10)
        self.tasks.insert(0, t)
        self._on_task_changed()

    def _edit_task(self, t):
        def _apply(updated):
            print(updated)
            requests.put("http://127.0.0.1:8000/TaskItem", json=updated, timeout=10)
            self._on_task_changed()
        TaskDialog(self, task=dict(t), on_submit=_apply)

    def _delete_task(self, t):
        if messagebox.askyesno(APP_NAME, f"Aufgabe ‘{t.get('title') or 'Ohne Titel'}’ löschen?"):
            self.tasks = [x for x in self.tasks if x["id"] != t["id"]]
            self._on_task_changed()

    def _on_task_changed(self):
        self.refresh()
        save_tasks(self.tasks)

    # ----- Filtering & sorting -----

    def _apply_filters(self):
        tasks = list(self.tasks)
        # Text search (title, desc, tag #)
        if self.search_query:
            q = self.search_query

            def match(t):
                if q in (t.get("title", "").lower()):
                    return True
                if q in (t.get("desc", "").lower()):
                    return True
                if q.startswith("#"):
                    return q[1:] in [x.lower() for x in t.get("tags", [])]
                if any(q in x.lower() for x in t.get("tags", [])):
                    return True
                return False
            tasks = [t for t in tasks if match(t)]

        # Primary filter
        label = self.active_filter
        today = date.today()
        if label == "Heute":
            tasks = [t for t in tasks if parse_date(
                t.get("due")) == today and not t.get("completed")]
        elif label == "Überfällig":
            tasks = [t for t in tasks if (d := parse_date(
                t.get("due"))) and d < today and not t.get("completed")]
        elif label == "Offen":
            tasks = [t for t in tasks if not t.get("completed")]
        elif label == "Erledigt":
            tasks = [t for t in tasks if t.get("completed")]
        elif label == "Hoch priorisiert":
            tasks = [t for t in tasks if t.get(
                "priority") == "hoch" and not t.get("completed")]

        # Tag filter
        if self.tag_filter:
            tasks = [t for t in tasks if self.tag_filter.lower() in [x.lower()
                                                                     for x in t.get("tags", [])]]

        # Sorting
        mode = self.sort_mode.get()
        if mode == "Fälligkeit":
            def key(t):
                d = parse_date(t.get("due"))
                return (1, date.max) if d is None else (0, d)
            tasks.sort(key=key)
        elif mode == "Priorität":
            order = {"hoch": 0, "mittel": 1, "niedrig": 2}
            tasks.sort(key=lambda t: (
                order.get(t.get("priority", "mittel"), 1), t.get("title", "")))
        elif mode == "Erstellt":
            tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        elif mode == "Titel":
            tasks.sort(key=lambda t: t.get("title", ""))

        self.filtered = tasks

    def _rebuild_tags_panel(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()
        tag_counts = {}
        for t in self.tasks:
            for tag in t.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        if not tag_counts:
            ctk.CTkLabel(self.tags_frame, text="Keine Tags vorhanden.").pack(
                anchor="w", padx=6, pady=6)
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
            ctk.CTkLabel(
                self.list_frame, text="Keine Aufgaben für die aktuelle Ansicht.").pack(pady=20)
        else:
            for t in self.filtered:
                item = TaskItem(self.list_frame, t, on_toggle=self._on_toggle,
                                on_edit=self._edit_task, on_delete=self._delete_task)
                item.pack(fill="x", padx=6, pady=6)

        total = len(self.tasks)
        done = len([t for t in self.tasks if t.get("completed")])
        open_cnt = total - done
        overdue_cnt = len([t for t in self.tasks if (d := parse_date(
            t.get("due"))) and d < date.today() and not t.get("completed")])
        self.info_lbl.configure(
            text=f"{len(self.filtered)} angezeigt • {open_cnt} offen • {done} erledigt • {overdue_cnt} überfällig")

        self.progress.set(0 if total == 0 else done / total)
        self.status_lbl.configure(
            text=f"Sortierung: {self.sort_mode.get()} • Filter: {self.active_filter}{' • #' + self.tag_filter if self.tag_filter else ''}")

    def _on_toggle(self, task):
        self._on_task_changed()
