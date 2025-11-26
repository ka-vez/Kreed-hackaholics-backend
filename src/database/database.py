# internal imports
from src.models.chat_session import ChatSession
from src.models.message import Message
from src.models.task import Task
from src.models.user import User



# external imports
import os
from sqlmodel import create_engine, Session, SQLModel
from fastapi import Depends
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine("sqlite:///bank.db", echo=True)

def get_db():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)