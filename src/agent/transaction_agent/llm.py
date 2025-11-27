# internal imports
from src.agent.transaction_agent.tools import (
    extra_data, 
    transfer_money, 
    buy_airtime, 
    buy_data, 
    buy_electricity
)

# external imports
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

tools = [extra_data, transfer_money, buy_airtime, buy_data, buy_electricity]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    max_tokens=500,
    max_retries=2
    ).bind_tools(tools) # type: ignore