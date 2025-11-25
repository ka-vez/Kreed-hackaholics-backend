from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), default=lambda : datetime.now(UTC))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    title = Column(String, nullable=True)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="chat_sessions", cascade="all, delete")
