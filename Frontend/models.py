from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional, List, Dict, Any

DATE_FMT = "%Y-%m-%d"

PRIO_STR_TO_INT = {"hoch": 2, "mittel": 1, "niedrig": 0}
PRIO_INT_TO_STR = {2: "hoch", 1: "mittel", 0: "niedrig", -1: "(keine)"}


def parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except Exception:
        return None


def format_date(d: Optional[date]) -> Optional[str]:
    if not d:
        return None
    return d.strftime(DATE_FMT)


def human_due(d: Optional[date]) -> str:
    if not d:
        return "Kein Fälligkeitsdatum"
    today = date.today()
    delta = (d - today).days
    if delta == 0:
        return "Heute"
    if delta == 1:
        return "Morgen"
    if delta == -1:
        return "Gestern"
    if delta < 0:
        return f"Überfällig seit {abs(delta)} Tag(en)"
    return d.strftime("%d.%m.%Y")


@dataclass
class SchemaNewTaskItem:
    title: str
    description: str
    completed: bool = False
    tags: List[str] = field(default_factory=list)
    prio: Optional[int] = -1
    due_date: Optional[date] = None

    def to_payload(self) -> Dict[str, Any]:
        data = asdict(self)
        data["due_date"] = format_date(self.due_date)
        return data


@dataclass
class SchemaTaskItem(SchemaNewTaskItem):
    id: str = ""

    @staticmethod
    def from_api(d: Dict[str, Any]) -> "SchemaTaskItem":
        return SchemaTaskItem(
            id=d.get("id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            completed=d.get("completed", False),
            tags=d.get("tags", []) or [],
            prio=d.get("prio", -1),
            due_date=parse_date(d.get("due_date"))
        )

    def to_payload(self) -> Dict[str, Any]:
        base = super().to_payload()
        base["id"] = self.id
        return base


# ---- UI convenience helpers ----

def prio_to_str(prio: Optional[int]) -> str:
    return PRIO_INT_TO_STR.get(prio if prio is not None else -1, "(keine)")


def str_to_prio(s: str) -> int:
    return PRIO_STR_TO_INT.get(s, -1)