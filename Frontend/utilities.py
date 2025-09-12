import json
from datetime import datetime, date
from pathlib import Path
import uuid

DATA_FILE = Path("tasks.json")
DATE_FMT = "%Y-%m-%d"


def today_str() -> str:
    """Returns today's date as a string in the specified format."""
    return date.today().strftime(DATE_FMT)


def parse_date(s: str | None) -> date | None:
    """Parses a date string to a date object. Returns None if invalid."""
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        return None


def human_due(d: date | None) -> str:
    """Returns a human-readable due date string."""
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
    """Returns CTk-friendly hex colors for badges based on priority."""
    mapping = {
        "hoch": "#D92D20",   # red
        "mittel": "#F79009",  # orange
        "niedrig": "#12B76A",  # green
    }
    # Default color if priority is unknown
    return mapping.get(priority, "#6B7280")


def status_color(is_done: bool, overdue: bool) -> str:
    """Returns a color for the task status."""
    if is_done:
        return "#12B76A"  # green
    if overdue:
        return "#D92D20"  # red
    return "#2563EB"      # blue


def ensure_data_file() -> None:
    """Ensures that the data file exists; creates it if not."""
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(
            {"tasks": []}, indent=2), encoding="utf-8")


def load_tasks() -> list:
    """Loads tasks from the data file."""
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data.get("tasks", [])
    except json.JSONDecodeError:
        return []


def save_tasks(tasks: list) -> None:
    """Saves tasks to the data file."""
    DATA_FILE.write_text(json.dumps(
        {"tasks": tasks}, indent=2, ensure_ascii=False), encoding="utf-8")


def new_task_template() -> dict:
    """Generates a new task template."""
    return {
        "id": str(uuid.uuid4()),
        "title": "",
        "desc": "",
        "due": None,          # YYYY-MM-DD
        "priority": "mittel",  # niedrig | mittel | hoch
        "tags": [],
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
