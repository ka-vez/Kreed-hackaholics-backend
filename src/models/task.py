# external imports
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User


class Task(SQLModel, table=True):
    __tablename__ = "tasks" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id")
    task_type: str = Field(nullable=False)
    parameters: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    result: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="tasks")



