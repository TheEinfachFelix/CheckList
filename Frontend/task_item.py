from __future__ import annotations
import tkinter as tk
import customtkinter as ctk
from datetime import date
from models import SchemaTaskItem, human_due, prio_to_str
from widgets import Badge, Chip, IconButton


def priority_color(priority_str: str) -> str:
    mapping = {
        "hoch": "#D92D20",
        "mittel": "#F79009",
        "niedrig": "#12B76A",
        "(keine)": "#6B7280",
    }
    return mapping.get(priority_str, "#6B7280")


def status_color(is_done: bool, overdue: bool) -> str:
    if is_done:
        return "#12B76A"
    if overdue:
        return "#D92D20"
    return "#2563EB"


class TaskItem(ctk.CTkFrame):
    def __init__(self, master, task: SchemaTaskItem, on_toggle, on_edit, on_delete, *args, **kwargs):
        super().__init__(master, *args, fg_color=("#FFFFFF", "#1F2937"), corner_radius=12, **kwargs)
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.columnconfigure(1, weight=1)

        d = task.due_date
        overdue = bool(d and d < date.today() and not task.completed)

        # Left: checkbox
        self.var = tk.BooleanVar(value=task.completed)
        self.chk = ctk.CTkCheckBox(self, text="", variable=self.var, command=self.toggle,
                                   width=24, height=24)
        self.chk.grid(row=0, column=0, padx=(12,8), pady=12, sticky="n")

        # Middle: title + meta
        title_text = task.title or "(Ohne Titel)"
        self.title_lbl = ctk.CTkLabel(self, text=title_text, font=("Inter", 14, "bold"))
        self.title_lbl.grid(row=0, column=1, sticky="w", pady=(12,0))

        meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        meta_frame.grid(row=1, column=1, sticky="w", pady=(2,12))

        due_str = human_due(d)
        due_fg = status_color(task.completed, overdue)
        self.due_badge = Badge(meta_frame, text=due_str, fg=due_fg)
        self.due_badge.pack(side="left", padx=(0,6))

        pr_str = prio_to_str(task.prio)
        self.pr_badge = Badge(meta_frame, text=pr_str.capitalize(), fg=priority_color(pr_str))
        self.pr_badge.pack(side="left", padx=(0,6))

        for t in task.tags:
            Chip(meta_frame, text=f"#{t}").pack(side="left", padx=(0,6))

        # Right: actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=12, pady=12, sticky="e")

        self.star_btn = IconButton(actions, "★" if task.prio == 2 else "☆", command=self.toggle_star)
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
        self.menu.add_separator()
        self.menu.add_command(label="Löschen", command=lambda: self.on_delete(self.task))

        self.bind("<Button-3>", self._open_menu)
        for w in (self.title_lbl, meta_frame, actions):
            w.bind("<Button-3>", self._open_menu)

        self._apply_completed_style()

    def _open_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def set_due_today(self):
        from datetime import date
        self.task.due_date = date.today()
        self.due_badge.set_text("Heute")
        self.event_generate("<<TaskChanged>>")

    def toggle_star(self):
        self.task.prio = 2 if (self.task.prio or -1) != 2 else 1
        self.star_btn.set_text("★" if self.task.prio == 2 else "☆")
        self.event_generate("<<TaskChanged>>")

    def toggle(self):
        self.task.completed = bool(self.var.get())
        self._apply_completed_style()
        self.event_generate("<<TaskChanged>>")

    def _apply_completed_style(self):
        if self.task.completed:
            self.title_lbl.configure(text_color=("#9CA3AF", "#9CA3AF"))
        else:
            self.title_lbl.configure(text_color=("#111827", "#F9FAFB"))