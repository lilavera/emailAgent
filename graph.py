# graph.py

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from agent2 import (
    get_and_categorize_email_node,
    create_draft_node,
    send_email_node,
    no_send_node,
    route_by_category
)

# Define initial state
initial_state = {}

# Build the graph
workflow = StateGraph(dict)

workflow.add_node("get_and_categorize", RunnableLambda(get_and_categorize_email_node))
workflow.add_node("create_draft", RunnableLambda(create_draft_node))
workflow.add_node("send_email", RunnableLambda(send_email_node))
workflow.add_node("no_send", RunnableLambda(no_send_node))

# Edges
workflow.set_entry_point("get_and_categorize")
workflow.add_edge("get_and_categorize", "create_draft")

# Conditional branching after draft creation
workflow.add_conditional_edges("create_draft", route_by_category, {
    "send_email": "send_email",
    "no_send": "no_send"
})

workflow.add_edge("send_email", END)
workflow.add_edge("no_send", END)

# Compile the graph
app = workflow.compile()

# Run it!
if __name__ == "__main__":
    final_state = app.invoke(initial_state)
    print("\n✅ Final State:")
    print(final_state)
