from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SchemaTaskItem(BaseModel):
    id: str = Field(..., description="The ID of the task")
    title: str = Field(..., description="The title of the task")
    description: str = Field(..., description="The description of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags associated with the task", optional=True)
    prio: Optional[str] = Field(default="niedrig", description="Priority of the task", optional=True)
    due_date: Optional[str] = Field(description="Due date of the task", optional=True)