# WebSocket-compatible agent nodes
# These nodes work with WebSocket communication instead of terminal input()

from src.agent.transaction_agent.llm import llm
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.system_prompts import (
    classify_and_fill_system_content,
    clarify_system_content,
    confirm_system_content,
    answer_question_system_content,
    action_confirmation_system_content
)

from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class ClassifierSchema(BaseModel):
    intent: str
    slots: dict


parser = PydanticOutputParser(pydantic_object=ClassifierSchema)

# System prompt to prepend only at the start
CLASSIFY_AND_FILL_SYSTEM_PROMPT = SystemMessage(content=classify_and_fill_system_content)

# This schema defines what's required for each intent.
REQUIRED_SLOTS_SCHEMA = {
    "buy_airtime": ["phone_number", "network", "amount"],
    "buy_data": ["phone_number", "network", "amount"],
    "buy_electricity": ["meter_number", "amount"],
    "transfer_money": ["receipient_account_number", "receipient_bank_name", "amount"],
    
    # Other intents have no slot requirements
    "check_balance": [],
    "user_confirmed_YES": [],
    "user_confirmed_NO": [],
    "general_chat": []
}


def classify_and_fill_ws(state: AgentState) -> dict:
    """WebSocket version - expects user message already in state"""
    messages = list(state['messages'])
    
    if not messages:
        # No messages yet - this shouldn't happen in WebSocket mode
        return {"messages": [], "intent": "general_chat", "slots": {}}
    
    # Normal classification flow
    user_message = messages[-1]
    
    all_messages = [CLASSIFY_AND_FILL_SYSTEM_PROMPT] + list(state['messages'])
    
    response = llm.invoke(all_messages)
    
    intent_and_slots = dict(parser.parse(response.content))  # type: ignore
    
    # Merge new slots with existing slots (preserve previous values)
    merged_slots = {**state.get('slots', {}), **intent_and_slots['slots']}
    
    # Don't return the classifier response - it's just JSON, not for the user
    return {"intent": intent_and_slots['intent'], "slots": merged_slots}


def check_for_missing_slots_ws(state: AgentState) -> dict:
    """Check for missing slots - same as terminal version"""
    intent = state['intent']
    slots = state['slots']
    
    required_slots = REQUIRED_SLOTS_SCHEMA.get(intent, [])
    
    missing_slots_list = []
    
    for slot_name in required_slots:
        if not slots.get(slot_name):
            missing_slots_list.append(slot_name)
    
    return {"missing_slots": missing_slots_list}


def clarify_ws(state: AgentState) -> dict:
    """WebSocket version - generates clarification question"""
    system_prompt = SystemMessage(content=clarify_system_content(str(state['missing_slots'])))
    user_prompt = HumanMessage(content="Ask me for the missing information.")
    
    response = llm.invoke([system_prompt, user_prompt])
    
    content = str(response.content) if response.content else "Could you please provide the missing information?"
    
    # Return the clarification message
    return {"messages": [AIMessage(content=content)]}


def confirm_ws(state: AgentState) -> dict:
    """WebSocket version - generates tool calls for execution"""
    if state["intent"] == 'buy_electricity':
        transaction_details = str({
            "intent": state["intent"],
            "meter_number": state['slots']['meter_number'],
            "amount": str(state["slots"]["amount"])
        })
    elif state["intent"] == 'transfer_money':
        transaction_details = str({
            "intent": state['intent'],
            "receipient_account_number": state['slots']['receipient_account_number'],
            "receipient_bank_name": state['slots']['receipient_bank_name'],
            "amount": state['slots']['amount']
        })
    else:
        transaction_details = str({
            "intent": state["intent"],
            "phone_number": state['slots']['phone_number'],
            "amount": str(state["slots"]["amount"]),
            "network": state["slots"]["network"]
        })
    
    # Create a message for the LLM to trigger tool call
    action_system_prompt = SystemMessage(
        content=action_confirmation_system_content(
            intent=state['intent'],
            user_input="yes",  # Auto-confirm for now
            slots=state['slots']
        )
    )
    user_confirmation = HumanMessage(content="yes")
    
    # Bind tools and invoke - this generates tool_calls
    # llm is already bound with tools in llm.py
    llm_decision = llm.invoke([action_system_prompt, user_confirmation])
    
    # Don't send the empty message - just store it for tool execution
    # Only update state, the message will be added by the state reducer
    return {"messages": [llm_decision]}


def process_confirmation_ws(state: AgentState) -> dict:
    """Process user's confirmation response - called after user responds"""
    messages = state.get('messages', [])
    
    if not messages or len(messages) < 2:
        return {"messages": []}
    
    # Get the last user message (their confirmation response)
    user_message = messages[-1]
    user_input = user_message.content if hasattr(user_message, 'content') else ""
    
    # Let the LLM decide what to do based on user's confirmation
    action_system_prompt = SystemMessage(
        content=action_confirmation_system_content(
            intent=state['intent'],
            user_input=user_input,
            slots=state['slots']
        )
    )
    
    # Let the LLM decide
    llm_decision = llm.invoke([action_system_prompt, user_message])
    
    return {"messages": [llm_decision], "awaiting_confirmation": False}


def pin_confirmation_ws(state: AgentState) -> dict:
    """WebSocket version - requests PIN input"""
    # Send PIN request message
    return {
        "messages": [AIMessage(content="[PIN_REQUEST]Please enter your 4-digit PIN to proceed")],
        "awaiting_pin": True
    }


def process_pin_ws(state: AgentState) -> dict:
    """Process PIN after user submits it"""
    messages = state.get('messages', [])
    correct_pin = state.get("pin") or "1235"
    
    if not messages:
        return {"pin_verified": False}
    
    # Get the last user message (PIN)
    last_message = messages[-1]
    entered_pin = last_message.content if hasattr(last_message, 'content') else ""
    
    # Validate PIN
    if entered_pin == correct_pin:
        return {
            "pin_verified": True,
            "awaiting_pin": False,
            "messages": [AIMessage(content="PIN verified. Processing transaction...")]
        }
    else:
        return {
            "pin_verified": False,
            "awaiting_pin": False,
            "messages": [AIMessage(content="Invalid PIN. Transaction cancelled.")]
        }


def answer_question_ws(state: AgentState) -> dict:
    """WebSocket version - answers general questions"""
    system_prompt = SystemMessage(content=answer_question_system_content())
    
    # Get all messages for context, but extract last user message
    messages = state.get('messages', [])
    
    # Find the last user message (not the classifier response)
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg
            break
    
    if not last_user_message:
        last_user_message = HumanMessage(content="Hello")
    
    # Invoke with system prompt and user message
    response = llm.invoke([system_prompt, last_user_message])
    
    content = str(response.content) if response.content else "I'm here to help! How can I assist you?"
    
    return {"messages": [AIMessage(content=content)]}


def tool_response_ws(state: AgentState) -> dict:
    """WebSocket version - extracts and returns tool response"""
    messages = state['messages']
    
    # Find the last ToolMessage
    tool_message = None
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'tool':
            tool_message = msg
            break
    
    if tool_message:
        # Return the tool result as an AI message
        return {"messages": [AIMessage(content=tool_message.content)]}
    else:
        return {"messages": [AIMessage(content="Transaction completed successfully!")]}
