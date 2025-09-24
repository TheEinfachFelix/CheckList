from typing import Optional, List
import requests
from datetime import date, datetime
from models import SchemaTaskItem, SchemaNewTaskItem

# Passe die BASE_URL falls nötig an
BASE_URL = "http://localhost:8000"

class ApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _to_iso(self, d: Optional[date]) -> Optional[str]:
        if d is None:
            return None
        if isinstance(d, str):
            return d
        return d.isoformat()

    def list_tasks(self) -> List[SchemaTaskItem]:
        resp = requests.get(f"{self.base_url}/TaskItems/")
        resp.raise_for_status()
        data = resp.json()
        # Pydantic model conversion happens clientseitig optional
        return [SchemaTaskItem(**t) for t in data]

    def get_task(self, item_id: str) -> Optional[SchemaTaskItem]:
        resp = requests.get(f"{self.base_url}/TaskItem/{item_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return SchemaTaskItem(**resp.json())

    def create_task(self, item: SchemaNewTaskItem) -> SchemaTaskItem:
        payload = item.model_dump()
        # due_date sollte als ISO-String gesendet werden (FastAPI erwartet String)
        if payload.get("due_date"):
            if isinstance(payload["due_date"], date):
                payload["due_date"] = payload["due_date"].isoformat()
        resp = requests.post(f"{self.base_url}/TaskItem/", json=payload)
        resp.raise_for_status()
        return SchemaTaskItem(**resp.json())

    def update_task(self, item: SchemaTaskItem) -> Optional[SchemaTaskItem]:
        payload = item.model_dump()
        # due_date -> ISO
        if payload.get("due_date"):
            if isinstance(payload["due_date"], date):
                payload["due_date"] = payload["due_date"].isoformat()
        resp = requests.put(f"{self.base_url}/TaskItem/", json=payload)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return SchemaTaskItem(**resp.json())

    def delete_task(self, item_id: str) -> bool:
        resp = requests.delete(f"{self.base_url}/TaskItem/{item_id}")
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return resp.json() is True or resp.status_code == 200