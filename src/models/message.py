# external imports 
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.chat_session import ChatSession


class Message(SQLModel, table=True):
    __tablename__ = "messages" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    chat_session_id: int = Field(foreign_key="chat_sessions.id")
    sender: str = Field(nullable=False)
    message_text: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tokens: int = Field(nullable=False)
    
    chat_session: Optional["ChatSession"] = Relationship(back_populates="messages")
