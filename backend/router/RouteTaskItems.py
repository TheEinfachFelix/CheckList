from fastapi import APIRouter, FastAPI
from schema.SchemaTaskItem import SchemaTaskItem

router = APIRouter()

@router.get("/TaskItems/", tags=["TaskItems"])
async def read_TaskItems() -> list[SchemaTaskItem]:
    return [SchemaTaskItem(id=1, title="Task 1", description="Description 1", completed=False),
            SchemaTaskItem(id=2, title="Task 2", description="Description 2", completed=True)]

@router.get("/TaskItem/{item_id}", tags=["TaskItems"])
async def read_TaskItem(item_id: int) -> SchemaTaskItem:
    return SchemaTaskItem(id=item_id, title=f"Task {item_id}", description=f"Description {item_id}", completed=False)

@router.post("/TaskItem/", tags=["TaskItems"])
async def create_TaskItem(item: SchemaTaskItem) -> SchemaTaskItem:
    return item

@router.put("/TaskItem/{item_id}", tags=["TaskItems"])
async def update_TaskItem(item_id: int, item: SchemaTaskItem) -> SchemaTaskItem:
    return item

@router.delete("/TaskItem/{item_id}", tags=["TaskItems"])
async def delete_TaskItem(item_id: int) -> None:
    return None