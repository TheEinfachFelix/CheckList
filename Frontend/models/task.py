from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Task:
    id: str
    title: str
    description: str
    completed: bool = False
    tags: list[str] = None
    prio: Optional[int] = -1
    due_date: Optional[str] = None