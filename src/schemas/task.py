from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    task_type: str
    parameters: Optional[str] = None

class TaskCreate(TaskBase):
    user_id: int

class TaskOut(TaskBase):
    id: int
    user_id: int
    status: str
    result: Optional[str] = None
    created_at: datetime

    class config:
        orm_mode = True
