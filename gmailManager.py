import openai
from dotenv import load_dotenv
import os
from gmailUtils import tools  # Assuming this contains your Gmail tools
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langgraph.prebuilt import chat_agent_executor

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load your Gmail tools
gmail_tools = [*tools]

# Initialize the LLM
model = ChatOpenAI(model="gpt-4o")

# Define the agent state
agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

class AgentState(TypedDict):
    messages: List[HumanMessage]
    latest_email: str  # To store the content of the latest email
    reply_content: str  # To store the generated reply
    thread_id: str | None  # To store the ID of the created thread

# Define the functions for the graph nodes


def get_latest_email():
    """Fetches the latest email content."""
    tool_results = agent_executor.invoke(
        # Assuming the first tool fetches latest email
        {"tools": [
            gmail_tools[4]], "tool_choice": gmail_tools[4].name}
    )
    # Assuming the tool returns the email content in a specific format
    # You'll need to adapt this based on your tool's output
    latest_email_content = tool_results["actions"][4].tool_call.arguments.get(
        "content", "No email content found.")
    return {"latest_email": latest_email_content}


def analyze_and_reply(state: AgentState):
    """Analyzes the latest email and generates a polite reply."""
    prompt = f"""Analyze the following email and generate a polite reply:
    ---
    {state['latest_email']}
    ---
    Reply:"""
    response = model.invoke([HumanMessage(content=prompt)])
    return {"reply_content": response.content, "messages": state["messages"] + [response]}


def create_and_send_thread(state: AgentState):
    """Creates a new thread with the generated reply and sends it."""
    tool_results = agent_executor.invoke(
        {"messages": state["messages"], "tools": [gmail_tools[1]], "tool_choice": gmail_tools[1].name,  # Assuming the second tool creates and sends thread
         # Basic subject
         "tool_input": {"body": state["reply_content"], "subject": f"Re: {state.get('latest_email', '')[:50]}..."}}
    )
    # Assuming the tool returns the thread ID
    thread_id = tool_results["actions"][0].tool_call.arguments.get("thread_id")
    return {"thread_id": thread_id}


def should_send(state: AgentState):
    # ... your logic ...
    result = "send"  # Or whatever your logic determines
    print(f"should_send returning: {result}")
    return result


# Define the LangGraph workflow
workflow = StateGraph(AgentState)

workflow.add_node("get_email", get_latest_email)
workflow.add_node("analyze_reply", analyze_and_reply)
workflow.add_node("send_email", create_and_send_thread)
workflow.add_node("should_send", should_send)

# Set up the edges
workflow.set_entry_point("get_email")
workflow.add_edge("get_email", "analyze_reply")
workflow.add_edge("analyze_reply", "should_send")
workflow.add_conditional_edges(
    "should_send",
    {"send": "send_email"},
    END
)

# Compile the graph
agent = workflow.compile()

# Run the agent
result = agent.invoke({"messages": [HumanMessage(
    content="Process the latest email and reply politely.")]})

print(result)
