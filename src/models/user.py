from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


    chat_sessions = relationship("ChatSession", back_populates="user")
    # tasks = relationship("Task", back_populates="user")
    #
