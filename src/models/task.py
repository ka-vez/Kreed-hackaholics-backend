from email.policy import default

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, column
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_type = Column(String, nullable=False)
    parameters = Column(Text)
    status = column(String, default="pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="tasks")



