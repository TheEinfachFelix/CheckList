import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import uuid

APP_NAME = "Checklist Pro"
DATA_FILE = Path("tasks.json")
DATE_FMT = "%Y-%m-%d"

# -------------- Utility helpers --------------

def today_str():
    return date.today().strftime(DATE_FMT)

def parse_date(s: str | None):
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except Exception:
        return None


def human_due(d: date | None) -> str:
    if not d:
        return "Kein Fälligkeitsdatum"
    delta = (d - date.today()).days
    if delta == 0:
        return "Heute"
    if delta == 1:
        return "Morgen"
    if delta == -1:
        return "Gestern"
    if delta < 0:
        return f"Überfällig seit {abs(delta)} Tag(en)"
    return d.strftime("%d.%m.%Y")


def priority_color(priority: str) -> str:
    # Return CTk-friendly hex colors for badges
    mapping = {
        "hoch": "#D92D20",   # red
        "mittel": "#F79009", # orange
        "niedrig": "#12B76A",# green
    }
    return mapping.get(priority, "#6B7280")


def status_color(is_done: bool, overdue: bool) -> str:
    if is_done:
        return "#12B76A"  # green
    if overdue:
        return "#D92D20"  # red
    return "#2563EB"      # blue


def ensure_data_file():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"tasks": []}, indent=2), encoding="utf-8")


def load_tasks():
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data.get("tasks", [])
    except Exception:
        return []


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps({"tasks": tasks}, indent=2, ensure_ascii=False), encoding="utf-8")


def new_task_template():
    return {
        "id": str(uuid.uuid4()),
        "title": "",
        "desc": "",
        "due": None,          # YYYY-MM-DD
        "priority": "mittel",# niedrig | mittel | hoch
        "tags": [],
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

# -------------- Task Item Widget --------------

class TaskItem(ctk.CTkFrame):
    def __init__(self, master, task, on_toggle, on_edit, on_delete, *args, **kwargs):
        super().__init__(master, *args, fg_color=("#FFFFFF", "#1F2937"), corner_radius=12, **kwargs)
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.columnconfigure(1, weight=1)

        overdue = False
        d = parse_date(task.get("due"))
        if d and d < date.today() and not task.get("completed"):
            overdue = True

        # Left: checkbox
        self.var = tk.BooleanVar(value=task.get("completed", False))
        self.chk = ctk.CTkCheckBox(self, text="", variable=self.var, command=self.toggle,
                                   width=24, height=24)
        self.chk.grid(row=0, column=0, padx=(12,8), pady=12, sticky="n")

        # Middle: title + meta
        title_text = task.get("title") or "(Ohne Titel)"
        self.title_lbl = ctk.CTkLabel(self, text=title_text, font=("Inter", 14, "bold"))
        self.title_lbl.grid(row=0, column=1, sticky="w", pady=(12,0))

        meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        meta_frame.grid(row=1, column=1, sticky="w", pady=(2,12))

        # due badge
        due_str = human_due(d)
        due_fg = status_color(task.get("completed"), overdue)
        self.due_badge = Badge(meta_frame, text=due_str, fg=due_fg)
        self.due_badge.pack(side="left", padx=(0,6))

        # priority badge
        pr = task.get("priority", "mittel")
        self.pr_badge = Badge(meta_frame, text=pr.capitalize(), fg=priority_color(pr))
        self.pr_badge.pack(side="left", padx=(0,6))

        # tag chips
        for t in task.get("tags", []):
            Chip(meta_frame, text=f"#{t}").pack(side="left", padx=(0,6))

        # Right: actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=12, pady=12, sticky="e")

        self.star_btn = IconButton(actions, "★" if pr == "hoch" else "☆", command=self.toggle_star)
        self.star_btn.pack(side="left", padx=4)

        self.edit_btn = IconButton(actions, "✎", command=lambda: self.on_edit(self.task))
        self.edit_btn.pack(side="left", padx=4)

        self.del_btn = IconButton(actions, "🗑", command=lambda: self.on_delete(self.task))
        self.del_btn.pack(side="left", padx=4)

        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Als erledigt markieren" if not self.var.get() else "Als offen markieren", command=self.toggle)
        self.menu.add_command(label="Bearbeiten…", command=lambda: self.on_edit(self.task))
        self.menu.add_separator()
        self.menu.add_command(label="Heute fällig", command=self.set_due_today)
        self.menu.add_cascade(label="Priorität", menu=self._priority_submenu())
        self.menu.add_separator()
        self.menu.add_command(label="Löschen", command=lambda: self.on_delete(self.task))

        self.bind("<Button-3>", self._open_menu)
        for w in (self.title_lbl, meta_frame, actions):
            w.bind("<Button-3>", self._open_menu)

        self._apply_completed_style()

    def _priority_submenu(self):
        m = tk.Menu(self.menu, tearoff=0)
        for p in ("hoch", "mittel", "niedrig"):
            m.add_command(label=p.capitalize(), command=lambda pr=p: self._set_priority(pr))
        return m

    def _open_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _set_priority(self, pr):
        self.task["priority"] = pr
        self.pr_badge.set_color(priority_color(pr))
        self.pr_badge.set_text(pr.capitalize())
        self.star_btn.set_text("★" if pr == "hoch" else "☆")
        self.event_generate("<<TaskChanged>>")

    def set_due_today(self):
        self.task["due"] = today_str()
        self.due_badge.set_text("Heute")
        self.due_badge.set_color(status_color(self.task.get("completed"), False))
        self.event_generate("<<TaskChanged>>")

    def toggle_star(self):
        self._set_priority("hoch" if self.task.get("priority") != "hoch" else "mittel")

    def toggle(self):
        self.task["completed"] = bool(self.var.get())
        self._apply_completed_style()
        self.event_generate("<<TaskChanged>>")

    def _apply_completed_style(self):
        if self.task.get("completed"):
            self.title_lbl.configure(text_color=("#9CA3AF", "#9CA3AF"))
        else:
            self.title_lbl.configure(text_color=("#111827", "#F9FAFB"))


class Badge(ctk.CTkLabel):
    def __init__(self, master, text: str, fg: str, *args, **kwargs):
        super().__init__(master, text=text, corner_radius=8, padx=8, pady=4,
                         fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"],
                         text_color=fg, font=("Inter", 12, "bold"), *args, **kwargs)
        self._accent = fg
        self._add_border()

    def _add_border(self):
        self.configure(border_width=1, border_color=self._accent)

    def set_text(self, t):
        self.configure(text=t)

    def set_color(self, c):
        self._accent = c
        self.configure(text_color=c, border_color=c)


class Chip(ctk.CTkLabel):
    def __init__(self, master, text: str):
        super().__init__(master, text=text, corner_radius=999, padx=8, pady=2,
                         fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"),
                         font=("Inter", 11, "normal"))


class IconButton(ctk.CTkButton):
    def __init__(self, master, icon_text: str, command=None):
        super().__init__(master, text=icon_text, width=36, height=32, corner_radius=8,
                         fg_color=("#EEF2FF", "#111827"), hover_color=("#E0E7FF", "#374151"),
                         text_color=("#1E3A8A", "#E5E7EB"), command=command)

    def set_text(self, t):
        super().configure(text=t)

# -------------- Dialogs --------------

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task=None, on_submit=None):
        super().__init__(master)
        self.title("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.geometry("520x520")
        self.resizable(False, False)
        self.grab_set()
        self.focus()

        self.on_submit = on_submit
        self.task = task or new_task_template()

        ctk.CTkLabel(self, text="Titel", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(20,4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Kurzer Titel…")
        self.title_entry.pack(fill="x", padx=20)
        self.title_entry.insert(0, self.task.get("title", ""))

        ctk.CTkLabel(self, text="Beschreibung", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(16,4))
        self.desc_txt = ctk.CTkTextbox(self, height=140)
        self.desc_txt.pack(fill="both", expand=False, padx=20)
        if self.task.get("desc"):
            self.desc_txt.insert("1.0", self.task.get("desc"))

        # Row: due + priority
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(16,0))

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(left, text="Fällig am (YYYY-MM-DD)").pack(anchor="w")
        self.due_entry = ctk.CTkEntry(left, placeholder_text=today_str())
        self.due_entry.pack(fill="x", pady=(4,0))
        if self.task.get("due"):
            self.due_entry.insert(0, self.task["due"]) 

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", expand=True, fill="x", padx=(16,0))
        ctk.CTkLabel(right, text="Priorität").pack(anchor="w")
        self.prio = ctk.CTkOptionMenu(right, values=["hoch", "mittel", "niedrig"]) 
        self.prio.set(self.task.get("priority", "mittel"))
        self.prio.pack(fill="x", pady=(4,0))

        # Tags
        ctk.CTkLabel(self, text="Tags (Komma-getrennt)", font=("Inter", 12, "bold")).pack(anchor="w", padx=20, pady=(16,4))
        self.tags_entry = ctk.CTkEntry(self, placeholder_text="z.B. Schule, Arbeit, Haushalt")
        self.tags_entry.pack(fill="x", padx=20)
        if self.task.get("tags"):
            self.tags_entry.insert(0, ", ".join(self.task["tags"]))

        # Completed
        self.done_var = tk.BooleanVar(value=self.task.get("completed", False))
        self.done_chk = ctk.CTkCheckBox(self, text="Erledigt", variable=self.done_var)
        self.done_chk.pack(anchor="w", padx=20, pady=(12,0))

        # Buttons
        btnrow = ctk.CTkFrame(self, fg_color="transparent")
        btnrow.pack(fill="x", side="bottom", padx=20, pady=20)
        ctk.CTkButton(btnrow, text="Abbrechen", fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"), command=self.destroy).pack(side="right")
        ctk.CTkButton(btnrow, text="Speichern", command=self._submit).pack(side="right", padx=(0,8))

    def _submit(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning(APP_NAME, "Bitte einen Titel eingeben.")
            return
        due_text = self.due_entry.get().strip()
        if due_text:
            d = parse_date(due_text)
            if not d:
                messagebox.showwarning(APP_NAME, "Ungültiges Datum. Bitte als YYYY-MM-DD eingeben.")
                return
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]

        self.task.update({
            "title": title,
            "desc": self.desc_txt.get("1.0", "end").strip(),
            "due": due_text or None,
            "priority": self.prio.get(),
            "tags": tags,
            "completed": bool(self.done_var.get()),
        })
        if self.on_submit:
            self.on_submit(self.task)
        self.destroy()

# -------------- Main App --------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1100x700")
        self.minsize(980, 600)

        # THEME
        ctk.set_appearance_mode("system")  # light/dark follows OS; user can toggle
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

        # Filter buttons
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

        # Tags
        ctk.CTkLabel(side, text="Tags", font=("Inter", 14, "bold")).pack(anchor="w", padx=16, pady=(16,6))
        self.tags_frame = ctk.CTkScrollableFrame(side, height=220)
        self.tags_frame.pack(fill="both", expand=False, padx=12)

        tag_add = ctk.CTkFrame(side, fg_color="transparent")
        tag_add.pack(fill="x", padx=12, pady=(8,12))
        self.new_tag_entry = ctk.CTkEntry(tag_add, placeholder_text="Neuen Tag filtern… #")
        self.new_tag_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tag_add, text="Hinzufügen", command=self._add_tag_filter).pack(side="left", padx=(8,0))

        # Bulk actions
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

        # Info bar
        self.info_lbl = ctk.CTkLabel(container, text="", font=("Inter", 12))
        self.info_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10,4))

        # Scrollable list
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
            # only tasks passing current filter
            if t in self.filtered:
                t["completed"] = True
        self._on_task_changed()

    def _delete_selected(self):
        # Not tracking selection; this action is only reachable via Delete shortcut if a menu is open typically.
        pass

    def _save(self):
        save_tasks(self.tasks)
        self.status_lbl.configure(text="Gespeichert")
        self.after(1200, lambda: self.status_lbl.configure(text="Bereit"))

    def open_new_task(self):
        TaskDialog(self, task=None, on_submit=self._add_task)

    def _add_task(self, t):
        self.tasks.insert(0, t)
        self._on_task_changed()

    def _edit_task(self, t):
        def _apply(updated):
            for i, x in enumerate(self.tasks):
                if x["id"] == updated["id"]:
                    self.tasks[i] = updated
                    break
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
                # allow searching with #tag
                if q.startswith("#"):
                    return q[1:] in [x.lower() for x in t.get("tags", [])]
                # otherwise search tags too
                if any(q in x.lower() for x in t.get("tags", [])):
                    return True
                return False
            tasks = [t for t in tasks if match(t)]

        # Primary filter
        label = self.active_filter
        today = date.today()
        if label == "Heute":
            tasks = [t for t in tasks if parse_date(t.get("due")) == today and not t.get("completed")]
        elif label == "Überfällig":
            tasks = [t for t in tasks if (d:=parse_date(t.get("due"))) and d < today and not t.get("completed")]
        elif label == "Offen":
            tasks = [t for t in tasks if not t.get("completed")]
        elif label == "Erledigt":
            tasks = [t for t in tasks if t.get("completed")]
        elif label == "Hoch priorisiert":
            tasks = [t for t in tasks if t.get("priority") == "hoch" and not t.get("completed")]

        # Tag filter
        if self.tag_filter:
            tasks = [t for t in tasks if self.tag_filter.lower() in [x.lower() for x in t.get("tags", [])]]

        # Sorting
        mode = self.sort_mode.get()
        if mode == "Fälligkeit":
            def key(t):
                d = parse_date(t.get("due"))
                # Put None due at the end
                return (1, date.max) if d is None else (0, d)
            tasks.sort(key=key)
        elif mode == "Priorität":
            order = {"hoch": 0, "mittel": 1, "niedrig": 2}
            tasks.sort(key=lambda t: (order.get(t.get("priority", "mittel"), 1), t.get("title", "")))
        elif mode == "Erstellt":
            tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        elif mode == "Titel":
            tasks.sort(key=lambda t: t.get("title", ""))

        self.filtered = tasks

    def _rebuild_tags_panel(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()
        # Collect tags
        tag_counts = {}
        for t in self.tasks:
            for tag in t.get("tags", []):
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

        # Clear list
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.filtered:
            ctk.CTkLabel(self.list_frame, text="Keine Aufgaben für die aktuelle Ansicht.").pack(pady=20)
        else:
            for t in self.filtered:
                item = TaskItem(self.list_frame, t, on_toggle=self._on_toggle, on_edit=self._edit_task, on_delete=self._delete_task)
                item.pack(fill="x", padx=6, pady=6)

        # Update info
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.get("completed")])
        open_cnt = total - done
        overdue_cnt = len([t for t in self.tasks if (d:=parse_date(t.get("due"))) and d < date.today() and not t.get("completed")])
        self.info_lbl.configure(text=f"{len(self.filtered)} angezeigt • {open_cnt} offen • {done} erledigt • {overdue_cnt} überfällig")

        self.progress.set(0 if total == 0 else done / total)
        self.status_lbl.configure(text=f"Sortierung: {self.sort_mode.get()} • Filter: {self.active_filter}{' • #' + self.tag_filter if self.tag_filter else ''}")

    def _on_toggle(self, task):
        # TaskItem emits <<TaskChanged>> already, so just save
        self._on_task_changed()


class ButtonGroup(ctk.CTkFrame):
    def __init__(self, master, items):
        super().__init__(master, fg_color="transparent")
        self.buttons = []
        for label, cb in items:
            b = ctk.CTkButton(self, text=label, height=36, command=lambda l=label: cb(l),
                              fg_color=("#F3F4F6", "#374151"), text_color=("#111827", "#E5E7EB"),
                              hover_color=("#E5E7EB", "#4B5563"))
            b.pack(fill="x", pady=4)
            self.buttons.append(b)


if __name__ == "__main__":
    app = App()
    app.mainloop()