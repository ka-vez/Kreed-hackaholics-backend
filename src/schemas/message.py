from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    sender: str
    message_text: str
    tokens: int

class MessageCreate(MessageBase):
    chat_session_id: int

class MessageOut(MessageBase):
    id: int
    chat_session_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
