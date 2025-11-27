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
    return "generate_chat" # Just a general chat, go to main response node

def should_answer_question(state: AgentState):
    intent = state['intent']
    
    if intent == 'general_chat':
        print("answering question")
        return "question"
    
    else:
        print("performing action")
        return "action"

def should_continue_transactions_and_use_tools(state: AgentState):
    """Check if any recent message contains tool calls from the LLM and PIN is verified"""
    messages = state.get('messages', [])
    pin_verified = state.get('pin_verified', False)
    
    if not messages:
        return "end"
    
    # Look for tool_calls in recent messages (not just the last one)
    # because pin_confirmation adds messages after the confirm node's tool_calls
    has_tool_calls = False
    for msg in reversed(messages):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:  # type: ignore
            has_tool_calls = True
            print(f"Found tool_calls: {msg.tool_calls}")  # type: ignore
            break
    
    if has_tool_calls and pin_verified:
        print("Tool calls found and PIN verified - executing tools")
        return "continue"
    elif not has_tool_calls:
        print("No tool calls found, ending")
        return "end"
    else:
        print("PIN verification failed, ending")
        return "end"
    