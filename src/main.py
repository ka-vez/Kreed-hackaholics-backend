# internal imports
from src.api.v1 import chat
from src.database.database import create_db_and_tables

#external imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(title="BelAI")

# CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"Hello": "BelAI", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
