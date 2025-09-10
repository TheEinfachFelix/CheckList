from pydantic import BaseModel, Field

class SchemaTaskItem(BaseModel):
    id: int = Field(..., description="The ID of the task")
    title: str = Field(..., description="The title of the task")
    description: str = Field(..., description="The description of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
