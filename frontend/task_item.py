import customtkinter as ctk
import tkinter as tk  # Importing tk for BooleanVar and Menu
from datetime import date
from widgets import Badge, Chip, IconButton
from utilities import parse_date, human_due, priority_color, status_color, today_str


class TaskItem(ctk.CTkFrame):
    def __init__(self, master, task, on_toggle, on_edit, on_delete, *args, **kwargs):
        super().__init__(master, *args, fg_color=("#FFFFFF",
                                                  "#1F2937"), corner_radius=12, **kwargs)
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
        self.var = tk.BooleanVar(value=task.get(
            "completed", False))  # Using tk.BooleanVar
        self.chk = ctk.CTkCheckBox(self, text="", variable=self.var, command=self.toggle,
                                   width=24, height=24)
        self.chk.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="n")

        # Middle: title + meta
        title_text = task.get("title") or "(Ohne Titel)"
        self.title_lbl = ctk.CTkLabel(
            self, text=title_text, font=("Inter", 14, "bold"))
        self.title_lbl.grid(row=0, column=1, sticky="w", pady=(12, 0))

        meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        meta_frame.grid(row=1, column=1, sticky="w", pady=(2, 12))

        # due badge
        due_str = human_due(d)
        due_fg = status_color(task.get("completed"), overdue)
        self.due_badge = Badge(meta_frame, text=due_str, fg=due_fg)
        self.due_badge.pack(side="left", padx=(0, 6))

        # priority badge
        pr = task.get("priority", "mittel")
        self.pr_badge = Badge(
            meta_frame, text=pr.capitalize(), fg=priority_color(pr))
        self.pr_badge.pack(side="left", padx=(0, 6))

        # tag chips
        for t in task.get("tags", []):
            Chip(meta_frame, text=f"#{t}").pack(side="left", padx=(0, 6))

        # Right: actions
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=12, pady=12, sticky="e")

        self.star_btn = IconButton(
            actions, "★" if pr == "hoch" else "☆", command=self.toggle_star)
        self.star_btn.pack(side="left", padx=4)

        self.edit_btn = IconButton(
            actions, "✎", command=lambda: self.on_edit(self.task))
        self.edit_btn.pack(side="left", padx=4)

        self.del_btn = IconButton(
            actions, "🗑", command=lambda: self.on_delete(self.task))
        self.del_btn.pack(side="left", padx=4)

        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Als erledigt markieren" if not self.var.get(
        ) else "Als offen markieren", command=self.toggle)
        self.menu.add_command(label="Bearbeiten…",
                              command=lambda: self.on_edit(self.task))
        self.menu.add_separator()
        self.menu.add_command(label="Heute fällig", command=self.set_due_today)
        self.menu.add_cascade(label="Priorität", menu=self._priority_submenu())
        self.menu.add_separator()
        self.menu.add_command(
            label="Löschen", command=lambda: self.on_delete(self.task))

        self.bind("<Button-3>", self._open_menu)
        for w in (self.title_lbl, meta_frame, actions):
            w.bind("<Button-3>", self._open_menu)

        self._apply_completed_style()

    def _priority_submenu(self):
        m = tk.Menu(self.menu, tearoff=0)
        for p in ("hoch", "mittel", "niedrig"):
            m.add_command(label=p.capitalize(),
                          command=lambda pr=p: self._set_priority(pr))
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
        self.due_badge.set_color(status_color(
            self.task.get("completed"), False))
        self.event_generate("<<TaskChanged>>")

    def toggle_star(self):
        self._set_priority("hoch" if self.task.get(
            "priority") != "hoch" else "mittel")

    def toggle(self):
        self.task["completed"] = bool(self.var.get())
        self._apply_completed_style()
        self.event_generate("<<TaskChanged>>")

    def _apply_completed_style(self):
        if self.task.get("completed"):
            self.title_lbl.configure(text_color=("#9CA3AF", "#9CA3AF"))
        else:
            self.title_lbl.configure(text_color=("#111827", "#F9FAFB"))

    def set_text(self, t):
        super().configure(text=t)
