# internal imports 
from src.agent.transaction_agent.state import AgentState
from src.agent.transaction_agent.routes import route_after_classification
from src.agent.transaction_agent.nodes import (
    classify_and_fill,
    check_for_missing_slots,
    clarify,
    confirm
)

# external imports
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END


# initializing the graph state
graph = StateGraph(AgentState)

# nodes
graph.add_node("classify_and_fill_agent", classify_and_fill)
graph.add_node("check_for_missing_slots_node", check_for_missing_slots)
graph.add_node("clarify_agent", clarify)
graph.add_node("confirm_agent", confirm)

# tool_node = ToolNode(tools=tools)
# graph.add_node("tools", tool_node)

# edges
graph.add_edge(START, "classify_and_fill_agent")
graph.add_edge("classify_and_fill_agent", "check_for_missing_slots_node")
graph.add_conditional_edges(
    "check_for_missing_slots_node",
    route_after_classification,
    {
        "clarify": "clarify_agent",
        "confirm": "confirm_agent"
    }
)
graph.add_edge("clarify_agent", "classify_and_fill_agent")
graph.add_edge("confirm_agent", END)

# graph.add_edge("tools", "classify_and_fill_agent")

app = graph.compile()

if __name__ == "__main__":
    while True:
        state = {"messages":[], "intent": "", "slots": {}, "missing_slots": [], "tool_response": ""}
        result = app.invoke(state) # type: ignore
        # print("\n", result)


