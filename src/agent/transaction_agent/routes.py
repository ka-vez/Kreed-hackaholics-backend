# local imports 
from src.agent.transaction_agent.state import AgentState


def route_after_classification(state: AgentState) -> str:
    """
    Reads the 'intent' and 'missing_slots' to decide the next step.
    This is the main logic for your conditional edges.
    """
    # print("---ROUTING---")
    intent = state['intent']
    missing_slots = state['missing_slots']

    # 1. Handle confirmation intents (Yes/No)
    if intent == "user_confirmed_YES":
        print("Routing to: execute_tool")
        return "execute_tool"  # Go run the API call
        
    if intent == "user_confirmed_NO":
        print("Routing to: generate_response_cancelled")
        return "generate_response_cancelled" # Go to a node that says "OK, cancelled."

    # 2. Handle transactional intents (buy_*)
    if intent in ["buy_airtime", "buy_data", "buy_electricity", "transfer_money"]:
        if len(missing_slots) > 0:
            # print("Routing to: clarify")
            return "clarify"  # Go to the 'clarify' (ask question) node
        else:
            # print("Routing to: confirm")
            return "confirm"  # All info is present, go to 'confirm' node

    # 3. Handle all other intents
    print("Routing to: generate_response_chat")
    return "generate_response_chat" # Just a general chat, go to main response node

def should_use_tools(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    if not last_message.tool_calls: # type: ignore
        return "end"
    else: 
        return "continue"
