# internal imports
from src.api.v1 import chat
from src.database.database import create_db_and_tables

#external imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(
    title="AlatAI",
    description="""
    AlatAI - Intelligent Banking Assistant API
    
    A sophisticated AI-powered banking assistant that enables users to perform financial transactions 
    through natural language conversations. Built with LangGraph and Google Gemini AI.
    
    **Features:**
    * 💬 Natural language transaction processing
    * 💸 Money transfers between bank accounts
    * 📱 Airtime and data purchases
    * ⚡ Electricity bill payments
    * 🔄 Real-time WebSocket communication
    * 🤖 Intent classification and slot filling
    * 🎯 Context-aware conversation management
    
    **Technology Stack:**
    * FastAPI for high-performance API endpoints
    * LangGraph for agent orchestration
    * Google Gemini 2.0 Flash for natural language understanding
    * WebSocket for real-time bidirectional communication
    * SQLModel for database management
    """,
    version="1.0.0",
    contact={
        "name": "ALAT by Wema",
        "url": "https://www.alat.ng",
    },
    license_info={
        "name": "Proprietary",
    },
)

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
