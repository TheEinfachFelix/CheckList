from fastapi import APIRouter, FastAPI
from schema.SchemaTaskItem import SchemaTaskItem
from schema.SchemaNewTaskItem import SchemaNewTaskItem

router = APIRouter()

from fastapi import APIRouter
from schema.SchemaTaskItem import SchemaTaskItem
from schema.SchemaNewTaskItem import SchemaNewTaskItem
from db.mongo import task_collection
from bson import ObjectId

router = APIRouter()

def task_helper(task) -> SchemaTaskItem:
    return SchemaTaskItem(
        id=str(task["_id"]),
        title=task.get("title", ""),
        description=task.get("description", ""),
        completed=task.get("completed", False),
        tags=task.get("tags", []),
        prio=task.get("prio", "niedrig"),
        due_date=task.get("due_date", None),
    )

@router.get("/TaskItems/", tags=["TaskItems"])
async def read_TaskItems() -> list[SchemaTaskItem]:
    tasks = []
    async for task in task_collection.find():
        tasks.append(task_helper(task))
    return tasks

@router.get("/TaskItem/{item_id}", tags=["TaskItems"])
async def read_TaskItem(item_id: str) -> SchemaTaskItem | None:
    task = await task_collection.find_one({"_id": ObjectId(item_id)})
    if task:
        return task_helper(task)
    return None

@router.post("/TaskItem/", tags=["TaskItems"])
async def create_TaskItem(item: SchemaNewTaskItem) -> SchemaTaskItem:
    new_task = item.model_dump()
    result = await task_collection.insert_one(new_task)
    created_task = await task_collection.find_one({"_id": result.inserted_id})
    return task_helper(created_task)

@router.put("/TaskItem/", tags=["TaskItems"])
async def update_TaskItem(item: SchemaTaskItem) -> SchemaTaskItem | None:
    update_data = item.model_dump()
    updated = await task_collection.update_one(
        {"_id": ObjectId(item.id)},
        {"$set": update_data}
    )
    if updated.modified_count == 1:
        task = await task_collection.find_one({"_id": ObjectId(item.id)})
        return task_helper(task)
    return None


@router.delete("/TaskItem/{item_id}", tags=["TaskItems"])
async def delete_TaskItem(item_id: str) -> bool:
    result = await task_collection.delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count == 1