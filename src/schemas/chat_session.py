from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    user_id: int

class ChatSessionOut(ChatSessionBase):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None


    class Config:
        orm_mode = True