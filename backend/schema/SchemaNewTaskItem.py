from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SchemaNewTaskItem(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: str = Field(..., description="The description of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags associated with the task", optional=True)
    prio: Optional[int] = Field(default=-1, description="Priority of the task", optional=True)
    due_date: Optional[date] = Field(description="Due date of the task", optional=True)