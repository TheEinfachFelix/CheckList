import requests
from models.task import Task

API_URL = "http://127.0.0.1:8000"

def get_tasks() -> list[Task]:
    response = requests.get(f"{API_URL}/TaskItems/")
    response.raise_for_status()
    return [Task(**task) for task in response.json()]

def delete_task(task_id: str) -> bool:
    response = requests.delete(f"{API_URL}/TaskItem/{task_id}")
    response.raise_for_status()
    return response.json()

def toggle_task(task: Task) -> Task:
    updated_task = task.__dict__.copy()
    updated_task["completed"] = not task.completed
    response = requests.put(f"{API_URL}/TaskItem/", json=updated_task)
    response.raise_for_status()
    return Task(**response.json())

def update_task(task: Task) -> Task:
    response = requests.put(f"{API_URL}/TaskItem/", json=task)
    response.raise_for_status()
    return Task(**response.json())

def create_task(new_task: dict) -> Task:
    response = requests.post(f"{API_URL}/TaskItem/", json=new_task)
    response.raise_for_status()
    return Task(**response.json())