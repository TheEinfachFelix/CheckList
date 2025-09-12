import uuid
from datetime import datetime


def new_task_template():
    return {
        "id": str(uuid.uuid4()),
        "title": "",
        "desc": "",
        "due": None,
        "priority": "mittel",
        "tags": [],
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
