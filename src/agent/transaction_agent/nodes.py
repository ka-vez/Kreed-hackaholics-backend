# internal imports 
from src.agent.transaction_agent.llm import llm
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.system_prompts import (
    classify_and_fill_system_content, 
    clarify_system_content, 
    confirm_system_content
    )

# external imports
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage


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


# System prompt to prepend only at the start
CLASSIFY_AND_FILL_SYSTEM_PROMPT = SystemMessage(content=classify_and_fill_system_content)

def classify_and_fill(state: AgentState) -> dict:
    """Call the LLM classifier and return the AIMessage as a partial state update.

    Do NOT mutate `state` in-place. Returning `{"messages": [response]}` will
    cause the `add_messages` reducer to append the AIMessage to the conversation.
    """
    messages = list(state['messages'])
    if not messages:
        print("🤖 Hi, i'm Alat AI, what would you like to do?")
        user_input = input("👤 USER: ")
        user_message = HumanMessage(content=user_input)

    else:
        user_input = input("👤 USER: ")
        user_message = HumanMessage(content=user_input)
    
    all_messages = [CLASSIFY_AND_FILL_SYSTEM_PROMPT] + list(state['messages']) + [user_message]

    response = llm.invoke(all_messages)
    # print(response.content)

    intent_and_slots = dict(parser.parse(response.content))   # type: ignore
    print(intent_and_slots)

    # Merge new slots with existing slots (preserve previous values)
    merged_slots = {**state.get('slots', {}), **intent_and_slots['slots']}
    print("merged_slots ", merged_slots)

    # Return the AIMessage so the graph appends it to the messages list.
    return {"messages": [response], "intent": intent_and_slots['intent'], "slots": merged_slots} 

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

def confirm(state: AgentState) -> AgentState:
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
    
    return state
    return state