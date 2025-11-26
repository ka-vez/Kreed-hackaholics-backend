# internal imports

# external imports
from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.chat_session import ChatSession
    from src.models.task import Task


class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(unique=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
