# agent.py

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor
from gmailUtils import tools
from dotenv import load_dotenv
import os
import openai
import re
from prompts import *

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

tools = [*tools]
model = ChatOpenAI(model="gpt-4o")
executor = chat_agent_executor.create_tool_calling_executor(model, tools)


def run_prompt(prompt: str):
    response = executor.invoke({"messages": [HumanMessage(content=prompt)]})
    ai_messages = [msg.content for msg in response["messages"]
                   if isinstance(msg, AIMessage)]
    return ai_messages


def get_and_categorize_email_node(state):
    print("📥 Getting and categorizing email...")
    result = run_prompt(GET_AND_CATEGORIZE_EMAIL_PROMPT)
    match = re.findall(r"\*\*(.*?)\*\*", result[1])
    print(match)
    state["category"] = match
    return state


def create_draft_node(state):
    print("📝 Creating draft...")
    category = state["category"]
    prompt = CREATE_DRAFT_PROMPT.format(category=category)
    result = run_prompt(prompt)
    state["draft"] = result[2]
    return state


def send_email_node(state):
    print("📤 Sending email...")
    result = run_prompt(SEND_THE_EMAIL_PROMPT)
    state["sent"] = result[3]
    return state


def no_send_node(state):
    print("🚫 Not sending email for complaints.")
    state["sent"] = "Email not sent due to complaint category."
    return state


def route_by_category(state):
    return "send_email" if state["category"] != "customer_complaint" else "no_send"
