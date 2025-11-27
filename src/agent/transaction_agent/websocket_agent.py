# WebSocket-compatible agent graph
# This agent is designed to work with WebSocket communication

from src.agent.transaction_agent.llm import tools
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.routes import (
    route_after_classification,
    should_answer_question
)
from src.agent.transaction_agent.websocket_nodes import (
    classify_and_fill_ws,
    check_for_missing_slots_ws,
    clarify_ws,
    answer_question_ws,
    confirm_ws,
    tool_response_ws
)

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END


def should_call_tools(state: AgentState) -> str:
    """Check if we should execute tools"""
    messages = state.get('messages', [])
    
    # Look for tool_calls in recent messages
    for msg in reversed(messages):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:  # type: ignore
            return "execute"
    
    return "skip"


def should_execute_after_pin(state: AgentState) -> str:
    """Check if PIN was verified to execute tools"""
    pin_verified = state.get('pin_verified', False)
    
    if pin_verified:
        print("PIN verified - executing tools")
        return "execute"
    else:
        print("PIN not verified or transaction cancelled")
        return "end"


# Initialize the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("classify_and_fill", classify_and_fill_ws)
graph.add_node("check_missing_slots", check_for_missing_slots_ws)
graph.add_node("clarify", clarify_ws)
graph.add_node("confirm", confirm_ws)
graph.add_node("answer_question", answer_question_ws)

# Tool execution
tool_node = ToolNode(tools=tools)
graph.add_node("execute_tools", tool_node)
graph.add_node("tool_response", tool_response_ws)

# Edges
graph.add_edge(START, "classify_and_fill")

graph.add_conditional_edges(
    "classify_and_fill",
    lambda state: "question" if state['intent'] == 'general_chat' else "action",
    {
        "question": "answer_question",
        "action": "check_missing_slots"
    }
)

graph.add_conditional_edges(
    "check_missing_slots",
    route_after_classification,
    {
        "clarify": "clarify",
        "confirm": "confirm"  # Go to confirm node which generates tool calls
    }
)

# After confirm, execute tools directly
graph.add_edge("confirm", "execute_tools")

# After clarify, need more input so end (client will send another message)
graph.add_edge("clarify", END)

# After tool execution, show the response
graph.add_edge("execute_tools", "tool_response")
graph.add_edge("tool_response", END)

# After answering question, we're done
graph.add_edge("answer_question", END)

# Compile the graph
websocket_app = graph.compile()
