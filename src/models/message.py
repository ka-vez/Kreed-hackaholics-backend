from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id= Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda : datetime.now(UTC))
    tokens = Column(Integer, nullable=False)

    chat_session = relationship("ChatSession", back_populates="messages")
