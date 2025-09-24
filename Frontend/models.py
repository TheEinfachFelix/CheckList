from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class SchemaNewTaskItem(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: str = Field(..., description="The description of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the task")
    prio: Optional[int] = Field(default=-1, description="Priority of the task")
    due_date: Optional[date] = Field(None, description="Due date of the task")

class SchemaTaskItem(SchemaNewTaskItem):
    id: str = Field(..., description="The ID of the task")