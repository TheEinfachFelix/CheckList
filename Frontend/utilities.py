from __future__ import annotations
import requests
from typing import List, Optional
from models import SchemaTaskItem, SchemaNewTaskItem

# Passe die Base-URL an, falls dein FastAPI anders läuft
API_BASE = "http://127.0.0.1:8000"
TIMEOUT = 10


def list_tasks() -> List[SchemaTaskItem]:
    r = requests.get(f"{API_BASE}/TaskItems/", timeout=TIMEOUT)
    r.raise_for_status()
    return [SchemaTaskItem.from_api(x) for x in r.json()]


def get_task(task_id: str) -> Optional[SchemaTaskItem]:
    r = requests.get(f"{API_BASE}/TaskItem/{task_id}", timeout=TIMEOUT)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    d = r.json()
    return SchemaTaskItem.from_api(d) if d else None


def create_task(new_item: SchemaNewTaskItem) -> SchemaTaskItem:
    payload = new_item.to_payload()
    r = requests.post(f"{API_BASE}/TaskItem/", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return SchemaTaskItem.from_api(r.json())


def update_task(item: SchemaTaskItem) -> Optional[SchemaTaskItem]:
    payload = item.to_payload()
    r = requests.put(f"{API_BASE}/TaskItem/", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    d = r.json()
    return SchemaTaskItem.from_api(d) if d else None


def delete_task(task_id: str) -> bool:
    r = requests.delete(f"{API_BASE}/TaskItem/{task_id}", timeout=TIMEOUT)
    r.raise_for_status()
    return bool(r.json())