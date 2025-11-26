from typing import Annotated, List, Dict, Any, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # The conversation history. 'add_messages' is a special
    # function that appends new messages to this list.
    messages: Annotated[list, add_messages]
    
    # What does the user want? (e.g., "buy_airtime", "buy_data", "general_chat")
    intent: str
    
    # A dictionary to store collected information
    # e.g., {"phone_number": "080...", "amount": 500, "service": "mtn"}
    slots: Dict[str, Any]
    
    # What information is STILL missing to fulfill the intent?
    # e.g., ["amount", "phone_number"]
    missing_slots: List[str]
    
    # The final message from a tool (e.g., "Success!" or "Error: Failed")
    tool_response: str