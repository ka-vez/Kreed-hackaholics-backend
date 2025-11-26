# external imports
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.message import Message


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: Optional[datetime] = Field(default=None)
    title: Optional[str] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="chat_sessions")
    messages: List["Message"] = Relationship(back_populates="chat_session", sa_relationship_kwargs={"cascade": "all, delete"})
