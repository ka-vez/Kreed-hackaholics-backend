# internal imports 
from src.agent.transaction_agent.llm import llm
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.system_prompts import (
    classify_and_fill_system_content, 
    clarify_system_content, 
    confirm_system_content,
    answer_question_system_content,
    action_confirmation_system_content
    )

# external imports
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import getpass


class ClassifierSchema(BaseModel):
    intent: str
    slots: dict

parser = PydanticOutputParser(pydantic_object=ClassifierSchema)



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

print("🤖 Hi, i'm Alat AI, what would you like to do?")
# System prompt to prepend only at the start
CLASSIFY_AND_FILL_SYSTEM_PROMPT = SystemMessage(content=classify_and_fill_system_content)

def classify_and_fill(state: AgentState) -> dict:
    """Call the LLM classifier and return the AIMessage as a partial state update.

    Do NOT mutate `state` in-place. Returning `{"messages": [response]}` will
    cause the `add_messages` reducer to append the AIMessage to the conversation.
    """
    messages = list(state['messages'])
    if not messages:
        user_input = input("👤 USER: ")
        user_message = HumanMessage(content=user_input)

    else:
        user_input = input("👤 USER: ")
        user_message = HumanMessage(content=user_input)
    
    all_messages = [CLASSIFY_AND_FILL_SYSTEM_PROMPT] + list(state['messages']) + [user_message]

    response = llm.invoke(all_messages)
    # print(response.content)

    intent_and_slots = dict(parser.parse(response.content))   # type: ignore
    # print(intent_and_slots)

    # Merge new slots with existing slots (preserve previous values)
    merged_slots = {**state.get('slots', {}), **intent_and_slots['slots']}
    # print("merged_slots ", merged_slots)

    # Return BOTH the user message and AI response so they're both in the history
    return {"messages": [user_message, response], "intent": intent_and_slots['intent'], "slots": merged_slots} 

def check_for_missing_slots(state: AgentState) -> dict:
    """
    Checks the current slots against the required schema for the current intent
    and populates the 'missing_slots' list.
    """
    # print("---UPDATING MISSING SLOTS---")
    
    # Get the data from the state
    intent = state['intent']
    slots = state['slots']
    
    # Get the list of required slots for this intent.
    # .get(intent, []) defaults to an empty list if the intent isn't in our schema
    required_slots = REQUIRED_SLOTS_SCHEMA.get(intent, [])
    
    missing_slots_list = []
    
    # Loop through the list of required slots
    for slot_name in required_slots:
        # Check if the slot is NOT in the state's 'slots' dict
        # or if it's there but is None or an empty string
        if not slots.get(slot_name):
            missing_slots_list.append(slot_name)
            
    # print(f"Missing slots found: {missing_slots_list}")
    
    # Return a dictionary to update the state
    print(missing_slots_list)
    return {"missing_slots": missing_slots_list}

def clarify(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=clarify_system_content(str(state['missing_slots'])))
    
    # Add a simple user message to trigger the response
    user_prompt = HumanMessage(content="Ask me for the missing information.")

    # Send both system and user message
    response = llm.invoke([system_prompt, user_prompt])
    
    # Fallback if response is empty
    content = str(response.content) if response.content else ""
    if not content.strip():
        fallback_message = "Could you please provide the missing information?"
        print(f"\n🤖 {fallback_message}")
    else:
        print(f"\n🤖 {content.strip()}")

    return state

def confirm(state: AgentState) -> dict:
    """Get user confirmation and let the LLM decide whether to call the tool"""
    if state["intent"] == 'buy_electricity':
        transaction_details = str(
        {"intent": state["intent"], 
         "meter_number": state['slots']['meter_number'], 
         "amount": str(state["slots"]["amount"])})
        
    elif state["intent"] == 'transfer_money':
        transaction_details = str(
            {"intent": state['intent'],
             "receipient_account_number": state['slots']['receipient_account_number'],
             "receipient_bank_name": state['slots']['receipient_bank_name'],
             "amount": state['slots']['amount']}
        )

    else:
        transaction_details = str(
            {"intent": state["intent"], 
             "phone_number": state['slots']['phone_number'], 
             "amount": str(state["slots"]["amount"]), 
             "network": state["slots"]["network"]})
    
    system_prompt = SystemMessage(content=confirm_system_content(transaction_details))
    user_prompt = HumanMessage(content="Generate the confirmation message based on the transaction details.")
    
    response = llm.invoke([system_prompt, user_prompt])
    
    # Fallback if response is empty
    content = str(response.content) if response.content else ""
    if not content.strip():
        fallback_message = f"Please confirm: {transaction_details}"
        print(f"\n🤖 {fallback_message}")
    else:
        print(f"\n🤖 {content.strip()}")
    
    # Get user confirmation
    user_input = input("👤 USER: ").strip()
    user_confirmation = HumanMessage(content=user_input)

    # Let the LLM decide what to do based on user's confirmation
    action_system_prompt = SystemMessage(
        content=action_confirmation_system_content(
            intent=state['intent'],
            user_input=user_input,
            slots=state['slots']
        )
    )
    
    # Let the LLM decide
    llm_decision = llm.invoke([action_system_prompt, user_confirmation])
    
    return {"messages": [user_confirmation, llm_decision]}

def answer_question(state: AgentState) -> AgentState:
    """Answer general questions using the conversation context"""
    
    system_prompt = SystemMessage(content=answer_question_system_content())
    
    # Get the last user message
    last_message = state['messages'][-2] if state['messages'] else HumanMessage(content="Hello")
    
    response = llm.invoke([system_prompt, last_message])
    
    # Fallback if response is empty
    content = str(response.content) if response.content else ""
    if not content.strip():
        fallback_message = "I'm here to help! How can I assist you with your banking needs today?"
        print(f"\n🤖 {fallback_message}")
    else:
        print(f"\n🤖 {content.strip()}")

    return state

def pin_confirmation(state: AgentState) -> dict:
    """Prompt for the user's PIN (hidden), verify with the stored PIN, and return updates.

    Does not store the raw PIN in the conversation history — only a masked entry is recorded.
    Returns a dict that can update state, e.g. {"messages": [...], "pin_verified": True/False}
    """

    MAX_TRIES = 3
    # Prefer a PIN from state if available, otherwise fall back to a default (for testing).
    correct_pin = state.get("pin") or "1235"

    # Get existing messages to preserve tool_calls from confirm node
    messages_out = []
    attempts = 0

    while attempts < MAX_TRIES:
        try:
            entered = getpass.getpass("👤 ENTER PIN: ").strip()
        except Exception:
            # Fall back to visible input if getpass isn't supported
            entered = input("👤 ENTER PIN: ").strip()

        # Record a masked user message (do NOT store the actual PIN)
        user_msg = HumanMessage(content="[PIN entered]")

        if entered == correct_pin:
            # Don't add any messages to preserve the tool_calls in the last AIMessage
            print("\n🤖 PIN verified. Proceeding with transaction.")
            # Return empty messages list to not interfere with tool execution
            return {"pin_verified": True}

        # Wrong PIN
        attempts += 1
        remaining = max(0, MAX_TRIES - attempts)
        messages_out.append(user_msg)
        if remaining > 0:
            ai_retry = AIMessage(content=f"Invalid PIN. {remaining} attempt(s) remaining.")
            messages_out.append(ai_retry)
            print(f"\n🤖 Invalid PIN. {remaining} attempt(s) remaining.")
        else:
            ai_fail = AIMessage(content="Maximum attempts reached. Transaction cancelled.")
            messages_out.append(ai_fail)
            print("\n🤖 Maximum attempts reached. Transaction cancelled.")
            return {"messages": messages_out, "pin_verified": False}

    # Shouldn't reach here, but return a safe default
    return {"messages": messages_out, "pin_verified": False}
        
def tool_response(state: AgentState) -> AgentState:
    """Extract and display the tool's response to the user"""
    
    messages = state['messages']
    

    # Find the last ToolMessage in the conversation
    tool_message = None
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'tool':
            tool_message = msg
            break
    
    if tool_message:
        # Display the tool's result
        print(f"\n🤖 {tool_message.content}")
    else:
        print("\n🤖 Transaction completed successfully!")
    
    return state