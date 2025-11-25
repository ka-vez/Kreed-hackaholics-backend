import os
from src.api.v1.ai_logic import app
from fastapi import APIRouter
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/eng")
async def english_chat(query):
    """
    Chat with the model in English.
    """

    # sets the messages
    prompt = {"messages": [HumanMessage(query)], "intent":"", "slots": {}, "missing_slots": [], "tool_response": ""}

    response = app.invoke(prompt) # type: ignore
    return response
    

