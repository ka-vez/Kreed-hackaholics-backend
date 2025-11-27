# internal imports 
from src.agent.transaction_agent.llm import tools
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.routes import (
    route_after_classification, 
    should_answer_question, 
    should_continue_transactions_and_use_tools
)
from src.agent.transaction_agent.nodes import (
    classify_and_fill,
    check_for_missing_slots,
    clarify,
    confirm,
    answer_question,
    tool_response,
    pin_confirmation
)

# external imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END


# initializing the graph state
graph = StateGraph(AgentState)

# nodes
graph.add_node("classify_and_fill_node", classify_and_fill)
graph.add_node("check_for_missing_slots_node", check_for_missing_slots)
graph.add_node("clarify_agent", clarify)
graph.add_node("confirm_agent", confirm)
graph.add_node("answer_question", answer_question)
graph.add_node("tool_response", tool_response)
graph.add_node("confirm_pin", pin_confirmation)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

# edges
graph.add_edge(START, "classify_and_fill_node")
graph.add_conditional_edges(
    "classify_and_fill_node",
    should_answer_question,
    {
        "question": "answer_question",
        "action": "check_for_missing_slots_node"
    }
)
graph.add_conditional_edges(
    "check_for_missing_slots_node",
    route_after_classification,
    {
        "clarify": "clarify_agent",
        "confirm": "confirm_agent"
    }
)
graph.add_edge("clarify_agent", "classify_and_fill_node")
graph.add_edge("confirm_agent", "confirm_pin")

graph.add_conditional_edges(
    "confirm_pin",
    should_continue_transactions_and_use_tools,
    {
        "continue": "tools",
        "end": END
    }
)
graph.add_edge("tools" , "tool_response")
graph.add_edge("tool_response", END)

app = graph.compile()

if __name__ == "__main__":
    while True:
        state = {"messages":[], "intent": "", "slots": {}, "missing_slots": [], "tool_response": "", "use_tool": False, "pin_verified": False}
        result = app.invoke(state) # type: ignore
        # print("\n", result)


