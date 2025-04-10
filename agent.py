import openai
from dotenv import load_dotenv
import os
from gmailUtils import tools
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.prebuilt import chat_agent_executor
from prompts import *
from langchain.prompts import PromptTemplate


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


tools = [*tools]


model = ChatOpenAI(model="gpt-4o")

agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)


# def get_latest_inbox_messages(agent_executor):
#     try:
#         response = agent_executor.invoke({"messages": [HumanMessage(
#             content="This is an email box of AI company NewRobot. Get latest unread incoming message from my inbox")]})
#         return response
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None 
    
def get_and_categorize_email(agent_executor):
     categorize_prompt = PromptTemplate(template=GET_AND_CATEGORIZE_EMAIL_PROMPT).format()
     response = agent_executor.invoke({
         "messages": [HumanMessage(
             content=categorize_prompt)]
     })
     return response
 
def create_draft(agent_executor):
     create_draft_prompt = PromptTemplate(template=CREATE_DRAFT_PROMPT).format()
     response = agent_executor.invoke({
         "messages": [HumanMessage(
             content=create_draft_prompt)]
     })
     return response
 
def send_email(agent_executor):
    response = agent_executor.invoke({
        "messages": [SystemMessage(
            content="Send the latest draft email")]
    })
    return response


# Example usage:
category = get_and_categorize_email(agent_executor)
#create_draft_message = create_draft(agent_executor)
#send_message = send_email(agent_executor)

print(category["messages"])
